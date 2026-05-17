---
id: SYD-016
title: Error Budget
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-015
used_by: ""
related: SYD-015, SYD-017, SYD-018
tags:
  - architecture
  - reliability
  - operations
  - site-reliability-engineering
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /syd/error-budget/
---

# SYD-016 - Error Budget

⚡ TL;DR - An error budget is the maximum acceptable
unreliability for a service, derived directly from
its SLO. It transforms reliability from a subjective
discussion into an objective, shared resource that
engineering and product teams spend together, enabling
principled decisions about feature velocity vs stability.

| #016 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SLA / SLO / SLI | |
| **Used by:** | (none - builds on SYD-015) | |
| **Related:** | SLA / SLO / SLI, MTTR / MTBF, RTO / RPO | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product team and SRE team are in perpetual conflict.
Product wants to ship a major refactor with a history
of causing incidents. SREs want to slow down. There
is no objective basis for either argument - just "we
need to move fast" vs "stability is important." The
conversation is political, not technical. The outcome
depends on who has more organizational power that day.

**THE BREAKING POINT:**
Without a shared, objective reliability target, every
reliability-vs-velocity tradeoff is a negotiation
with no principled resolution. The lack of a shared
framework means reliability is under-invested during
product pressure (features win) and over-invested
during post-incident PTSD (engineering freezes for
weeks after every incident).

**THE INVENTION MOMENT:**
The error budget concept is central to Google's SRE
model, described in the SRE Book (2016). The key
insight: if the business has agreed that 99.9% uptime
is the target, then 0.1% downtime is explicitly
permitted - it is a budget to be spent, not a failure
to be prevented at all costs. Spending it on risk-
taking (deployments) is legitimate. Exhausting it
accidentally (incidents) triggers a policy response.
This converts a political argument into a policy
execution.

---

### 📘 Textbook Definition

An error budget is the quantified allowance for a
service to be unreliable over a defined time window,
derived as `(1 - SLO) × window_duration`. For example,
a 99.9% SLO over 30 days yields a 30-day error budget
of 43.2 minutes of downtime (0.1% × 43,200 minutes).
The error budget is a shared resource between
development (which spends it through risk-taking:
deployments, experiments, infrastructure changes) and
operations (which is responsible for not burning it
through incidents). Budget remaining determines
deployment velocity: budget depleted → freeze
high-risk changes until budget replenishes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The error budget is the amount of time your service
is allowed to be down (or degrade) in a given period,
based on your SLO. Spend it wisely.

**One analogy:**
> A team has a monthly "risk budget" of $1,000.
> Each risky deployment costs ~$200. Incidents cost
> what they actually burned. If you spend $800 on
> three deployments and then have a $300 incident,
> you've exceeded the budget. Policy: stop risky
> deployments until next month's $1,000 refreshes.
> No more "should we deploy" arguments - the budget
> decides.

**One insight:**
The error budget removes subjectivity from the
reliability-vs-velocity tradeoff. The budget is
a policy, not a preference. When it is depleted,
the policy (not the SRE team's opinion) says
"stop risky changes."

---

### 🔩 First Principles Explanation

**ERROR BUDGET MATH:**

```
SLO = 99.9%
Error rate budget = 1 - 0.999 = 0.001 = 0.1%

Time window = 30 days = 43,200 minutes
Allowed downtime = 43,200 × 0.001 = 43.2 minutes

At 1,000 requests/minute:
Total requests in 30 days = 43,200,000
Allowed failed requests = 43,200
  = 0.1% of all requests
```

**HOW THE BUDGET IS SPENT:**

```
┌─────────────────────────────────────────────────┐
│ BUDGET CONSUMPTION SOURCES                      │
│                                                 │
│ Planned risk (deployment):                      │
│   Deploy v1.2.3 → 0.3% error rate for 5 min   │
│   = 0.3% × 5 min = 0.015 min effective downtime│
│   = 0.035% of 43.2-min budget                  │
│                                                 │
│ Unplanned incident (bug):                       │
│   DB index missing → 80% error rate for 15 min │
│   = 80% × 15 min = 12 minutes of effective     │
│   downtime = 27.8% of 43.2-min budget           │
│                                                 │
│ After 1 incident: 27.8% budget consumed        │
│ If 3 more same incidents: budget exhausted      │
│ Policy: pause high-risk deployments             │
└─────────────────────────────────────────────────┘
```

**THE ERROR BUDGET POLICY:**
The policy is the critical piece - without it, the
error budget is just a number. A typical policy:

1. Error budget > 50%: normal velocity; deployments
   proceed; experiments welcome.
2. Error budget 10-50%: reduced velocity; deploy
   only carefully reviewed changes; focus on reliability.
3. Error budget < 10%: freeze risky deployments;
   all engineering focuses on reliability improvement
   until next window.
4. Error budget exhausted: all new feature releases
   blocked until window resets. Incident post-mortem
   required before resuming.

**THE TRADE-OFFS:**
**Gain:** Objective framework for reliability-vs-velocity
decisions; removes politics from the tradeoff; creates
financial incentive to invest in reliability (budget
spent on incidents = budget not available for deployments).
**Cost:** Requires organizational adoption of the
policy - without buy-in, the budget is ignored.
Requires accurate SLI measurement - bad measurement
produces a meaningless budget. Setting the wrong SLO
produces the wrong budget.

---

### 🧪 Thought Experiment

**SCENARIO: Two teams, same SLO, different philosophies**

**Team A - "Move fast" philosophy:**
Deploys 3 times/week. Each deployment spends 5% of
the monthly budget (error rate spikes briefly on each).
Two incidents this month (10% budget each).
Budget consumed: 3 × 4 weeks × 5% + 2 × 10% = 80%.
20% budget remaining. Can still deploy, but carefully.

**Team B - "Never break prod" philosophy:**
Deploys once/month. Extremely careful. Almost never
has incidents. Budget consumed: 1 deployment × 5%
+ 0 incidents = 5% consumed.
95% budget remaining.

**Error budget perspective:**
Team B is WASTING their error budget. They paid for
99.9% SLO, which means 0.1% failure is acceptable.
By not using that 0.1%, they are being over-cautious
at the cost of feature velocity. The 95% remaining
budget represents risk they could have taken on
useful deployments.

**THE INSIGHT:**
An SLO creates an implicit contract: users accept
up to X% unreliability. Not using the error budget
means being more reliable than the SLO requires -
which is not free. The cost is slower feature delivery
as the team is excessively cautious. Error budgets
encode the principle: "it is OK to be imperfect
within the agreed boundary."

---

### 🧠 Mental Model / Analogy

> Error budget is like a bank balance with a fixed
> monthly allowance. Income = 0 (the budget is not
> earned, it is reset each month). Expenses = incidents
> and deployments. The budget determines how much
> risk-taking is allowed. If the balance goes to zero,
> you stop spending until it resets.
>
> Unlike a real bank: you cannot save excess budget
> month-to-month (it resets). You cannot overdraft
> without triggering the policy (except in emergencies).
> The reset is your safety valve: every 30 days,
> the balance goes back to the full amount.

- "Balance" → remaining error budget
- "Expenses" → incidents and risky deployments
- "Income" → monthly reset (not cumulative)
- "Overdraft prevention" → freeze deployments policy
- "Monthly reset" → rolling window expiry

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Your service is allowed to have problems for a
certain amount of time each month, based on your
reliability target. That amount is your "error budget."
When you run out, you stop making changes until the
next month.

**Level 2 - How to use it (junior developer):**
Calculate: if SLO is 99.9%, the monthly budget is
43.2 minutes. Track monthly downtime in a dashboard.
When it approaches 43 minutes, alert the team to
freeze risky changes.

**Level 3 - How it works (mid-level engineer):**
Error budgets are tracked as burn rate (how fast
the budget is depleting). Normal burn rate = 1.0
(spending the budget evenly over the window). Burn
rate > 14.4 means the budget will be exhausted in
~50 hours. Multi-window burn rate alerts (5-minute
and 1-hour windows) detect both fast and slow burns.

**Level 4 - Why it was designed this way (senior/staff):**
The burn rate alerting (rather than cumulative budget
tracking) is critical for actionability. A simple
threshold alert ("budget < 10%") is too late: if the
budget was 50% and depleted to 5% in 2 hours, you
have only hours to respond. Burn rate alerts fire
within minutes of a rapid burn, giving time to respond
before the budget is exhausted.

**Level 5 - Mastery (distinguished engineer):**
Error budget policy enforcement is the hardest part.
The policy only works if leadership is committed to
it. Common failure modes: product leadership overrides
the freeze ("this release is critical"). SRE team
uses the exhausted budget as an excuse not to deploy
something safe. Budget is treated as a threshold to
hit exactly each month ("we always want to hit exactly
43 minutes of downtime"). The mature version: the
budget is a ceiling, not a target. Having budget
remaining is good. The policy applies when budget
is exhausted, not as a planning target for how much
downtime to have.

---

### ⚙️ How It Works (Mechanism)

**Burn rate calculation:**

```
Normal burn rate = 1.0
  (budget depletes evenly: 43.2 min over 30 days)

Burn rate = current_error_rate / error_budget_rate
where error_budget_rate = (1 - SLO) = 0.001 (for 99.9%)

If current error rate = 0.01 (1%):
  Burn rate = 0.01 / 0.001 = 10
  Budget exhausted in: 30 days / 10 = 3 days

If current error rate = 0.0001 (0.01%):
  Burn rate = 0.0001 / 0.001 = 0.1
  Budget never exhausted (spending less than SLO allows)
```

**Multi-window alert thresholds (Google SRE recommendation):**

```
┌──────────────────────────────────────────────────────┐
│ BURN RATE ALERT TIERS                                │
│                                                      │
│ Tier 1 (Page - critical):                           │
│   5-min window burn rate > 14.4                      │
│   AND 1-hour window burn rate > 14.4                 │
│   → Budget exhausted in ~2 hours. Page on-call.      │
│                                                      │
│ Tier 2 (Ticket - urgent):                            │
│   30-min window burn rate > 6                        │
│   AND 6-hour window burn rate > 6                    │
│   → Budget exhausted in ~5 days. Fix within 24h.    │
│                                                      │
│ Tier 3 (Slow burn warning):                          │
│   24-hour window burn rate > 3                       │
│   → Budget at risk of exhaustion. Review in sprint. │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Prometheus: Burn rate alert rules**
```yaml
# Multi-window burn rate alerting for 99.9% SLO
groups:
- name: error-budget-alerts
  rules:
  # Tier 1: Fast burn (exhausts budget in < 2 hours)
  # Burn rate > 14.4 means: budget gone in 2 hours
  - alert: ErrorBudgetCritical
    expr: >
      (
        job:request_success_rate:ratio_rate5m < 0.001
        * 14.4
      ) and (
        job:request_success_rate:ratio_rate1h < 0.001
        * 14.4
      )
    for: 2m
    labels:
      severity: critical
      slo_window: 30d
    annotations:
      description: >
        SLO burn rate is critical.
        30-day budget will exhaust in ~2 hours.
        Current 5m error rate: {{ $value | humanize }}

  # Tier 2: Moderate burn (5-day exhaustion)
  - alert: ErrorBudgetHigh
    expr: >
      (
        job:request_success_rate:ratio_rate30m < 0.001
        * 6
      ) and (
        job:request_success_rate:ratio_rate6h < 0.001
        * 6
      )
    for: 15m
    labels:
      severity: warning
    annotations:
      description: >
        SLO burn rate elevated.
        30-day budget will exhaust in ~5 days.
```

**Example 2 - Error budget dashboard calculation**
```python
# Calculate remaining error budget for a service
# Called from monitoring/alerting dashboard backend

from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ErrorBudget:
    slo: float          # e.g. 0.999 for 99.9%
    window_days: int    # e.g. 30

    @property
    def total_budget_minutes(self):
        total_minutes = self.window_days * 24 * 60
        return total_minutes * (1 - self.slo)

    def remaining(self, downtime_minutes: float):
        """Returns remaining budget fraction (0.0-1.0)"""
        remaining_minutes = (
            self.total_budget_minutes - downtime_minutes
        )
        return max(0.0, remaining_minutes
                   / self.total_budget_minutes)

    def status(self, downtime_minutes: float):
        remaining = self.remaining(downtime_minutes)
        if remaining > 0.5:
            return "HEALTHY"
        elif remaining > 0.1:
            return "REDUCED"
        elif remaining > 0:
            return "CRITICAL"
        else:
            return "EXHAUSTED"

# Example usage:
budget = ErrorBudget(slo=0.999, window_days=30)
print(f"Total budget: {budget.total_budget_minutes:.1f} min")
# Total budget: 43.2 min

# After an incident with 20 min downtime:
remaining = budget.remaining(20)
print(f"Remaining: {remaining:.1%}")
# Remaining: 53.7%
print(f"Status: {budget.status(20)}")
# Status: REDUCED
```

---

### ⚖️ Comparison Table

| Budget State | Remaining | Policy | Example Action |
|---|---|---|---|
| Healthy | > 50% | Normal velocity | Deploy freely, run experiments |
| Reduced | 10-50% | Careful | Review deployments, prioritize reliability |
| Critical | 1-10% | Constrained | Only critical fixes; reliability work first |
| Exhausted | 0% | Frozen | No new feature deploys; post-mortem required |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Error budget exhaustion means the service is broken | It means the service used more of its allowed unreliability than planned. The service may be working fine; the budget tracks cumulative unreliability, not current state. |
| The goal is to never exhaust the error budget | The goal is to spend the budget wisely. A service that never comes close to budget exhaustion may be over-engineered or too conservative with deployments. The budget should be *available* to be spent on risk-taking. |
| Error budgets only track downtime | They track any SLO violation: latency breaches, elevated error rates, data staleness. If latency p99 exceeds the SLO threshold, it burns the error budget even if the service is technically available. |

---

### 🚨 Failure Modes & Diagnosis

**Budget Death Spiral**

**Symptom:**
A team's error budget is exhausted in week 1 of the
month from an incident. Feature deployments are frozen.
SRE team focuses on reliability improvements. But the
reliability improvements require code changes, which
require deployments, which are frozen. No progress.

**Root Cause:**
The error budget policy is too binary: "budget exhausted
= no deployments." This prevents the reliability
improvements that would restore the budget.

**Fix:**
Differentiate deployment types in the policy:
- High-risk deployments (new features, large refactors):
  frozen when budget exhausted.
- Low-risk deployments (reliability improvements,
  bug fixes with limited blast radius): allowed even
  with exhausted budget.
The policy should target risky changes, not all changes.

**Prevention:**
When writing the error budget policy, categorize
deployments by risk level and apply the freeze
selectively. Not all deployments are equally risky.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SLA / SLO / SLI` - error budget is derived from
  the SLO; cannot be understood without SLO context

**Builds On This (learn these next):**
- `MTTR / MTBF` - complementary reliability metrics;
  MTTR is one of the key drivers of error budget burn

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ (1 - SLO) × window = allowed unreliability│
│              │ 99.9% SLO = 43.2 min/month budget         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Removes subjectivity from reliability-vs- │
│ SOLVES       │ velocity tradeoff                         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Budget exhaustion triggers POLICY (stop   │
│              │ risky changes), not just an alert         │
├──────────────┼───────────────────────────────────────────┤
│ BURN RATE    │ current_error_rate / (1 - SLO)            │
│              │ > 14.4 = page now; > 6 = fix in 24h      │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Treating budget as a target (aim for      │
│              │ exactly 43 min downtime/month) instead    │
│              │ of a ceiling                              │
├──────────────┼───────────────────────────────────────────┤
│ GOOD POLICY  │ Budget > 50%: deploy. Budget < 10%: only  │
│              │ reliability fixes. Budget exhausted:      │
│              │ freeze risky changes.                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Error budget: your allowed imperfection  │
│              │  for the month. Spend it on deployments. │
│              │  Don't burn it on incidents."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ MTTR / MTBF → RTO / RPO                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Budget = (1 - SLO) × time window = allowed unreliability.
2. Spending it on deployments is OK; burning it on
   incidents is the problem.
3. The policy (freeze risky changes when exhausted)
   is what makes the framework useful.

**Interview one-liner:**
"An error budget is (1 - SLO) × time window - the
allowed unreliability. For a 99.9% SLO over 30 days,
that is 43.2 minutes. The budget tracks both planned
spending (deployments with some risk) and unplanned
burning (incidents). When exhausted, the error budget
policy triggers a freeze on high-risk changes, turning
a political negotiation into a policy decision."
