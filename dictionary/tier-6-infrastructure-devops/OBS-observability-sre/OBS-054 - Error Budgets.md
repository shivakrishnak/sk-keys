---
id: OBS-054
title: Error Budgets
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-012, OBS-020, OBS-053, OBS-048, OBS-050
used_by: OBS-040
related: OBS-030, OBS-042, OBS-051
tags:
  - observability
  - reliability
  - devops
  - sre
  - intermediate
  - concept
  - slo
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /observability-sre/error-budgets/
---

# OBS-054 - Error Budgets

⚡ TL;DR - The error budget is the time-bound "reliability
credit" derived from the SLO: at 99.9% over 30 days you
have 43.2 minutes to spend on failures. Spending it on
incidents is unavoidable; spending it on deployments is
a deliberate trade-off; running out stops all deployments.
The budget makes reliability a shared engineering and
product decision, not a unilateral SRE veto.

| #054            | Category: Observability & SRE                                                      | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SLO, Error Budget (basic), SLO Deep Dive, Formal SLO Theory, SLO Trade-off Framing |                 |
| **Used by:**    | SRE Book Core Principles                                                           |                 |
| **Related:**    | Alerting Fundamentals, SLO-Based Alerting Strategy, Reliability Mental Model       |                 |

---

### 🔥 The Problem This Solves

**THE RELIABILITY VS. VELOCITY TENSION:**
The product team wants to deploy every day. The SRE team
says "deployments cause incidents." This produces a standoff:
product says "reliability is blocking velocity"; SRE says
"velocity is killing reliability." Both are partially right.
No objective mechanism exists to resolve the conflict.
The result: political battles about deployment frequency,
with reliability work always losing because features have
direct revenue impact and reliability work does not.

**THE INVENTION MOMENT (Google SRE book, 2016):**
The error budget solves the conflict by converting an
abstract argument ("reliability vs. velocity") into a
concrete, shared, objective measurement. Both product and
SRE agree in advance: the error budget defines exactly
how much unreliability is acceptable per month. Spending
the budget on deployments is the team's choice. When the
budget runs out, deployments freeze - not because SRE
says so, but because the shared agreement says so. The
budget transforms a political debate into a data-driven
decision.

**ORGANIZATIONAL ALIGNMENT:**
Before error budgets: "reliability" was a judgment call.
After error budgets: "we have 12 minutes of budget left
this month, this deployment has historically cost 4 minutes
on rollback - do we want to spend 33% of remaining budget
on this release?" is an objective, auditable decision.

---

### 📘 Textbook Definition

An **error budget** is the maximum amount of unreliability
(measured as a time interval, request count, or percentage)
that a service is allowed to experience in a defined window
while still meeting its SLO. It is derived from the SLO
target: `error_budget = (1 - SLO_target) × window`. The
error budget operationalizes reliability as a finite,
spendable resource. It enables teams to make explicit
trade-offs between reliability investment and deployment
velocity, and to measure those trade-offs objectively.
When the error budget is exhausted, the team stops all
risky deployments and prioritizes reliability improvements
until the budget resets or is replenished through improved
performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The error budget is the "failure allowance" derived from
the SLO - 99.9% availability = 43.2 minutes/month to spend
on failures from any cause.

**One analogy:**

> The error budget is like a vacation allowance. Each
> employee has 20 days per year of paid leave (error budget).
> Taking a sick day consumes leave (incident consumes budget).
> Taking planned vacation consumes leave (deployment with
> rollback consumes budget). At the end of the year, unused
> leave may carry over (some organizations reset, some carry
> over). If you take 25 days of leave: policy says you work
> overtime to catch up (budget exhausted: deployment freeze).
> The key innovation: both "sick days" and "vacation" draw
> from the same allowance. You can optimize how you spend it.

---

### 🔩 First Principles Explanation

**THE MATH:**

```
Error budget from SLO:

  SLO = 99.9%  →  allowed_error_rate = 0.1%

  Monthly budget (minutes):
    30 days × 24 hours × 60 minutes × 0.001 = 43.2 minutes

  Budget consumed so far this month:
    (1 - current_30d_SLI) × window_minutes

  Example: current 30d SLI = 99.87%
    consumed = (1 - 0.9987) × 43200 min = 56.2 minutes
    budget remaining = 43.2 - 56.2 = -13 minutes (EXHAUSTED)

  Budget remaining %:
    = max(0, (error_budget_available - consumed) /
              error_budget_available) × 100

  Equivalent Prometheus query:
    (
      (1 - job:svc:ratio_rate30d) -
      (1 - 0.999)
    ) /
    (1 - 0.999) × 100

    → positive: % remaining
    → negative: % over budget
```

**BURN RATE RELATIONSHIP:**

```
Burn rate measures how fast the budget is being consumed.

  burn_rate = error_rate / (1 - SLO_target)

  At burn rate 1:  consuming exactly at SLO error rate.
                   Budget lasts exactly the full window.
  At burn rate 14.4: consuming 14.4x the allowed rate.
                     Budget exhausted in 2 hours
                     (30 days × 24h / 14.4 = 50 hours)
  At burn rate 1080: consuming 1080x the allowed rate.
                     Service is completely down.
                     Budget exhausted in 40 minutes.

  Multi-window burn rate alerting uses this to differentiate:
    PAGE: burn rate > 14.4 in 5m AND 1h  (2h budget gone)
    WARN: burn rate > 6 in 30m AND 6h    (5d budget rate)
    (See OBS-042 for complete burn rate alert config)
```

**SPENDING POLICY (the organizational agreement):**

```
Define explicitly before an incident, not during:

STATE 1 - Budget Healthy (> 50% remaining):
  - Normal deployment cadence (e.g., 5 deploys/day)
  - Experimental features allowed to production
  - Load testing against production allowed
  - Chaos engineering experiments in scope

STATE 2 - Budget Caution (20%-50% remaining):
  - Reduce deployment frequency (e.g., max 2/day)
  - Require canary deployment for all changes
  - No experimental features to production
  - Incident reviews for all budget-consuming events

STATE 3 - Budget Warning (< 20% remaining):
  - Deployment freeze for non-critical changes
  - Emergency fixes only with SRE approval
  - All new work paused, engineering redirected
    to reliability improvements
  - Daily budget status in stand-up

STATE 4 - Budget Exhausted (0% remaining):
  - Full deployment freeze
  - Product reviews the feature backlog for reliability debt
  - Engineering works reliability improvement sprint
  - Budget resets at end of window (30 days)
  - Early reset possible with SLO amendment (formal process)
```

---

### 🧪 Thought Experiment

**THE DEPLOYMENT INVESTMENT DECISION:**

It is day 25 of the month. You have 7 minutes of error
budget remaining (16% of 43.2 minutes monthly budget).
You have a critical feature that has been in development
for 3 months. The product team wants to deploy today.

**Historical data for this service:**

- 70% of deployments: no incidents (0 budget consumed)
- 25% of deployments: minor rollback (3-5 minutes consumed)
- 5% of deployments: major incident (15-30 minutes consumed)

**Expected budget consumption:**

```
E[budget_consumed] = 0.70 × 0 + 0.25 × 4 + 0.05 × 20
                   = 0 + 1.0 + 1.0
                   = 2.0 minutes expected value

P(exhaustion from this deploy) =
  P(consuming > 7 minutes) =
  P(major incident) = 5%

Remaining budget after deploy (expected):
  7.0 - 2.0 = 5 minutes (12% of monthly budget)
```

**The decision framework:**

- 5 remaining days in month, 5 minutes of budget left
- Average daily natural consumption: 0.1 × 43.2 / 30 = 0.14 min
- Remaining 5 days natural consumption: 5 × 0.14 = 0.7 min
- Budget after natural consumption: 5 - 0.7 = 4.3 min
- Expected budget after deploy: 5 - 2.0 = 3.0 min

Deploy: expected 3.0 min remaining at month end.
5% chance of SLO breach this month (major incident).

**Alternative:** wait until next month reset (day 30).
Next month starts with full 43.2 minutes. Deploy day 1.
Zero risk of this month's SLO breach.

The error budget turns this from a political debate into
a concrete expected-value calculation.

---

### 🧠 Mental Model / Analogy

> Think of the error budget as a shared "trust account"
> between engineering and customers. The SLO is the promise
> ("we will keep 43.2 minutes or less of downtime this month").
> Every incident is a withdrawal from the trust account.
> Every deployment is a risk of a future withdrawal.
> When the account is nearly empty, the responsible action
> is to stop making withdrawals until it replenishes.
> The key insight: both SRE and product have equal ownership
> of the account balance. SRE doesn't "own" reliability;
> the team collectively decides how to spend the budget.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The error budget is "how much downtime can we afford?"
expressed as a number. If our SLO is 99.9% uptime,
we have 43.2 minutes of downtime allowance per month.
If we use 30 of those minutes on an incident, we have
13.2 left. If we get to 0, we stop deploying new features
until the budget resets.

**Level 2 - How to use it (junior developer):**
Check the error budget before deploying. Your team's
runbook should say "if budget < 20%: get SRE approval
before deploying." Monitor budget consumption rate
daily during incidents. After an incident, calculate
how much budget was consumed. Use that to inform
the next quarterly SLO review.

**Level 3 - How it works (mid-level engineer):**
The error budget is computed from the SLO and current
SLI using Prometheus recording rules. The budget remaining
gauge is a key dashboard panel. Burn rate alerts warn
before budget is exhausted. When budget is at 20%,
trigger a budget alert (Slack/PagerDuty to the team
channel, not a page, but requiring acknowledgment).

**Level 4 - Why it was designed this way (senior/staff):**
The error budget converts reliability from a veto ("SRE
says no deployments") to a shared resource. Product can
choose to spend budget on velocity (deploy aggressively,
accept higher risk of incidents). Engineering can invest
in reliability to earn budget back. The policy (deployment
freeze at exhaustion) is agreed in advance and enforced
automatically - not by a person. This removes the political
dimension of reliability discussions. The tension becomes
"how should we spend the budget?" rather than "who has
the authority to block deployments?"

**Level 5 - Mastery (distinguished engineer):**
Error budgets at scale require budget portfolio management.
With 200 services, some will exhaust budgets every month
(chronically unreliable) while others never approach
their budget (over-engineered or under-utilized). The
platform analytics layer tracks budget consumption across
all services and identifies: (1) which services have
exhausted budget most frequently (reliability investment
candidates); (2) which services have never used > 20%
of budget (SLO may be too loose - tighten or reallocate
engineering effort); (3) which teams have the best and
worst budget management practices (for knowledge sharing).

---

### ⚙️ Why It Holds True

**WHY THE BUDGET CONVERTS POLITICS TO DATA:**

Without the error budget, the reliability vs. velocity
debate is a values conflict (reliability is important vs.
velocity is important). Both are correct and irresolvable
through argument.

With the error budget, the debate becomes concrete:

- "We have 30% budget remaining. This deploy historically
  costs 5-8% budget. We have 3 deploys queued.
  Expected remaining at month end: ~9%. Above threshold."

The budget acts as a shared oracle. It doesn't resolve
the value conflict; it provides a neutral arbiter that
both sides have agreed to trust. The governance agreement
(what to do at each budget level) must be made before
an incident, not during one. During an incident, the
team is under pressure and governance breaks down.

**WHY BUDGET RESET TIMING MATTERS:**

A 30-day rolling window (continuous) is more operationally
useful than a calendar month reset:

```
Calendar month reset:
  - Teams deploy aggressively on day 1 (full budget)
  - Teams freeze deployments on day 25+ (budget low)
  - Artificial deployment clusters around reset dates
  - "End of month" incidents are disproportionately common

Rolling 30-day window:
  - Consistent budget pressure throughout
  - No artificial deployment timing incentives
  - Incidents from 31+ days ago "fall out" of window
  - Gradual budget recovery after incidents
```

---

### 🔄 System Design Implications

**MULTI-SERVICE ERROR BUDGET DEPENDENCIES:**

```
Service A depends on B (external API).
B's SLO: 99.5% (1,296 min/month budget)
A's SLO: 99.9% (43.2 min/month budget)

When B consumes its budget (1,296 min failures),
A is affected.

Options:
1. Attribute B's failures to B's budget, not A's:
   A's SLI = success rate EXCLUDING B-caused failures
   A's SLO = 99.9% on A's own errors only
   B is accountable for its own budget.

2. Absorb B's failures in A (retry/fallback):
   A's circuit breaker + fallback reduces impact
   Effective: for partial B degradation
   Not effective: for complete B outage

3. Set A's SLO accounting for B:
   A's SLO ≤ B's SLO × A's own reliability
   = 99.5% × 99.95% = 99.45%
   More conservative but reflects actual guarantees

Architecture decision:
  Services in the same error budget "domain" should
  have their SLOs set in a consistent hierarchy:
  platform services (99.99%) > product services (99.9%)
  > background workers (99.5%)
```

---

### 💻 Code Example

**Prometheus alerts for budget status (all three states):**

```yaml
groups:
  - name: error-budget-management
    rules:
      # Budget state 3 - Warning: < 20% remaining
      # Not a page - notifies team channel
      - alert: ErrorBudgetCritical
        expr: >
          (
            (1 - job:checkout:ratio_rate30d)
            -
            (1 - 0.999)
          ) / (1 - 0.999) * 100 < 20
        for: 0m # immediate - budget is depleting
        labels:
          severity: warning
          team: checkout
        annotations:
          summary: >
            Checkout error budget below 20%
          description: >
            {{ $value | humanize }}% of error budget
            remaining for checkout-service.
            Current 30d SLI:
            {{ with query "job:checkout:ratio_rate30d" }}
              {{ . | first | value | humanizePercentage }}
            {{ end }}.
            Deployment freeze at 0%. Review runbook:
            https://runbooks.company.com/slo/checkout

      # Budget state 4 - Exhausted: 0% remaining
      # Page the on-call
      - alert: ErrorBudgetExhausted
        expr: >
          (
            (1 - job:checkout:ratio_rate30d)
            -
            (1 - 0.999)
          ) / (1 - 0.999) * 100 < 0
        for: 5m
        labels:
          severity: critical
          team: checkout
        annotations:
          summary: >
            Checkout error budget EXHAUSTED - deploy freeze
          description: >
            SLO breached. 30d SLI below 99.9%.
            Budget {{ $value | humanize }}% (negative =
            breached). DEPLOY FREEZE in effect.
            No new deployments without SRE approval.
            All hands on reliability improvements.

      # Budget recovery notification
      # When budget recovers to > 50% (after incident)
      - alert: ErrorBudgetRecovered
        expr: >
          (
            (1 - job:checkout:ratio_rate30d)
            -
            (1 - 0.999)
          ) / (1 - 0.999) * 100 > 50
          AND
          (
            (1 - job:checkout:ratio_rate30d[1h] offset 1h)
            -
            (1 - 0.999)
          ) / (1 - 0.999) * 100 < 50
        for: 0m
        labels:
          severity: info
          team: checkout
        annotations:
          summary: >
            Checkout error budget recovered above 50%
          description: >
            Budget now at {{ $value | humanize }}%.
            Normal deployment velocity can resume.
```

---

### ⚖️ Comparison Table

| Approach                  | Velocity-Reliability Balance | Objectivity              | Shared Ownership      |
| ------------------------- | ---------------------------- | ------------------------ | --------------------- |
| **Error budget policy**   | Explicit, data-driven        | High (computed from SLI) | Product + Engineering |
| SRE veto power            | Ad-hoc, subjective           | Low                      | SRE only              |
| No reliability governance | Velocity always wins         | N/A                      | None                  |
| Change advisory board     | Process-heavy, slow          | Medium                   | Operations focus      |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                  |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Error budget freeze = SRE blocking product | The freeze is an automatic consequence of a pre-agreed policy. SRE doesn't "block" anyone; the shared governance agreement blocks deployments when the budget is exhausted                               |
| Unused budget is wasted                    | Unused budget means you over-engineered (or under-utilized). It's a signal to loosen the SLO or invest reliability effort elsewhere. Not a problem, but worth understanding                              |
| Budget exhaustion = outage                 | Budget exhaustion means the SLO target was missed for the window. Individual users may have experienced failures, but "exhausted" ≠ "down". It means accumulated failures exceeded the allowed threshold |
| The budget only tracks incidents           | Budget is consumed by all causes: incidents, risky deployments, planned maintenance, dependency failures. Any event that causes the SLI to drop below the target consumes budget                         |

---

### 🚨 Failure Modes & Diagnosis

**Budget Exhausted Every Month (Chronic Exhaustion)**

**Symptom:**
The checkout service exhausts its 99.9% error budget
every month for 6 consecutive months. Engineering runs
reliability sprints. Budget refills at the monthly reset.
Exhausted again by day 20 the following month. No net
improvement.

**Root Cause Analysis:**
Two possibilities:

1. SLO target is calibrated above natural reliability baseline
   (the service cannot achieve 99.9% naturally).
2. Specific recurring failure modes consume the majority
   of budget (the same incidents happen repeatedly).

**Diagnosis:**

```promql
# Check natural reliability (baseline without incidents)
# Use percentile of 7-day windows over 90 days
# If the 50th percentile is below SLO target:
# the service cannot achieve the target naturally

# Identify top budget consumers by incident
# Look at the error_budget_consumed_minutes metric
# tagged with incident_id
sum by (incident_type) (
  increase(
    checkout_error_budget_consumed_minutes_total[90d]
  )
)
# Top result is likely a recurring failure type
```

**Fix Option A (if SLO is miscalibrated):**
Loosen SLO to match natural reliability baseline.
Run quarterly SLO review early with the data.

**Fix Option B (if recurring incidents):**
Create a reliability project for the top budget consumer.
For example: if database connection pool exhaustion
causes 60% of budget consumption, the project is
"implement connection pool monitoring and auto-scaling."
Require this to be fixed before feature work resumes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLO` - the target the budget is derived from
- `Error Budget` (OBS-020) - the basic concept
- `SLO Deep Dive` - the SLI definition and measurement
  that feeds into error budget calculation
- `Formal SLO Theory` - the math behind burn rates
- `SLO Trade-off Framing` - the decision framework

**Builds On This (learn these next):**

- `SRE Book Core Principles` - the organizational model
  that error budgets are part of

**Alternatives / Comparisons:**

- `Alerting Fundamentals` - pre-SLO alerting without budget framing
- `SLO-Based Alerting Strategy` - burn rate alerting that
  acts before budget is exhausted
- `Reliability Mental Model` - error budget as the
  "accountability force" in the four-force model

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ FORMULA       │ budget = (1 - SLO) × window           │
│               │ 99.9%, 30d = 43.2 min               │
│               │ 99.99%, 30d = 4.32 min              │
├───────────────┼────────────────────────────────────────┤
│ BUDGET STATES │ > 50%: normal deploy cadence          │
│               │ 20-50%: canary required, monitor      │
│               │ < 20%: critical changes only          │
│               │ 0%: deploy freeze, reliability sprint │
├───────────────┼────────────────────────────────────────┤
│ BURN RATE     │ error_rate / (1 - SLO)               │
│               │ Rate 1 = budget lasts full window     │
│               │ Rate 14.4 = exhausted in 50h          │
├───────────────┼────────────────────────────────────────┤
│ KEY INSIGHT   │ Budget converts "reliability vs.      │
│               │ velocity" from a political debate     │
│               │ to an objective trade-off decision    │
├───────────────┼────────────────────────────────────────┤
│ EXHAUSTION    │ Auto-freeze deployments (not SRE veto)│
│               │ Work reliability sprint until budget  │
│               │ replenishes via 30d rolling window    │
├───────────────┼────────────────────────────────────────┤
│ GOVERNANCE    │ Define states and policies BEFORE     │
│               │ an incident, not during one           │
├───────────────┼────────────────────────────────────────┤
│ ONE-LINER     │ "43.2 minutes to spend as you choose. │
│               │ Spend wisely."                       │
├───────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE  │ SRE Book Core Principles              │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Error budget = (1 - SLO_target) × window. 99.9% =
   43.2 minutes/month. This is the allowance for ALL
   causes: incidents, deployments, maintenance.
2. Define the four spending policy states (healthy,
   caution, warning, exhausted) and their consequences
   BEFORE an incident. Governance under pressure fails.
3. Chronic exhaustion signals either miscalibrated SLO
   (target above natural baseline) or recurring incidents
   that need engineering investment. The budget makes the
   problem visible; the quarterly review drives the fix.

**Interview one-liner:**
"Error budget = (1 - SLO_target) × window: 99.9% availability
gives 43.2 minutes/month of allowed failures from any cause.
It converts the reliability-vs-velocity debate from political
to data-driven: define governance states (> 50% budget: normal
deploy; 20-50%: canary required; < 20%: critical only; 0%:
deploy freeze) in advance, then enforce automatically. Key
failure mode: chronic budget exhaustion signals either SLO
miscalibrated above natural reliability, or recurring
incidents needing reliability investment. The budget makes
the problem visible and objective."
