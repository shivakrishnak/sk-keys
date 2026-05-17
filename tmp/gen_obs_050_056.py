"""Generate OBS-050 through OBS-056 stub replacements."""
import os

BASE = r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-6-infrastructure-devops\OBS-observability-sre"

def w(fname, content):
    path = os.path.join(BASE, fname)
    enc = content.encode("utf-8")
    with open(path, "wb") as f:
        f.write(enc)
    print(f"Written: {fname} ({len(enc)} bytes)")

OBS_050 = """\
---
id: OBS-050
title: "SLO Trade-off Framing"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-005, OBS-009, OBS-012, OBS-020, OBS-036, OBS-037, OBS-040, OBS-048
used_by: OBS-051, OBS-053
related: OBS-036, OBS-037, OBS-040, OBS-042, OBS-048, OBS-051, OBS-053, OBS-054
tags:
  - sre
  - slo
  - trade-offs
  - decision-framework
  - advanced
  - production
  - mental-model
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /obs/slo-trade-off-framing/
---

# OBS-050 - SLO Trade-off Framing

\u26a1 TL;DR - SLO trade-off framing is the decision
framework for choosing WHERE to set a reliability
target: too strict (over-engineering, kills velocity),
too loose (user harm, churn), or just right (SLO =
the user experience threshold). Every SLO decision
involves explicit trade-offs between reliability cost,
feature velocity, and user experience, and the SRE
practitioner's job is to make these trade-offs explicit
and data-driven rather than implicit and gut-feel.

| #050 | Category: Observability & SRE | Difficulty: \\u2605\\u2605\\u2605 |
|:---|:---|:---|
| **Depends on:** | SLI/SLO, Error Budget, Incident Response, Post-Mortem, SRE Core Principles, SLO-Based Alerting, Formal SLO Theory | |
| **Used by:** | Reliability Mental Model, SLOs Deep Dive | |
| **Related:** | SLI/SLO, Error Budget, SRE Principles, SLO-Based Alerting, Formal SLO Theory, Reliability Mental Model, SLOs Deep Dive, Error Budgets | |

---

### \\U0001f525 The Problem This Solves

**WORLD WITHOUT IT:**
A product manager asks: "What availability SLO should
we set for the search service?" The SRE team answers:
"99.9%." The PM asks: "Why not 99.99%?" The SRE
team answers: "That's much harder to achieve." No
further justification.

The 99.9% number is arbitrary. It was not chosen
based on user experience data, cost analysis, or
engineering capacity. It was chosen because "99.9%
is the industry standard." The team has no framework
for the decision and cannot defend it. Six months
later the product team wants to increase the SLO
and the SRE team resists without data.

**THE INVENTION:**
SLO trade-off framing provides a structured decision
process for SLO target selection. It asks three
questions: (1) What is the user experience threshold
- at what reliability level do users notice degradation
and change their behavior (abandon, churn, complain)?
(2) What is the engineering cost of each reliability
level - how much does it cost in engineer-hours to
move from 99.9% to 99.99%? (3) What is the velocity
cost - how much feature engineering capacity must
be sacrificed to achieve the target? Answers to
these three questions yield a rational SLO target
and a data-driven framework for SLO revision.

---

### \\U0001f4d8 Textbook Definition

**SLO Trade-off Framing** is the structured analysis
that determines the optimal SLO target by balancing
three competing forces: (1) user experience requirements
(the minimum reliability level that prevents user
harm), (2) engineering cost of reliability (the
marginal cost to improve reliability), and (3)
feature velocity cost (the opportunity cost of
engineering time spent on reliability vs features).

**The Three-Force Model:**

```
    User Experience
    (lower bound for SLO)
           |
           |   < OPTIMAL ZONE >
           |
     SLO ----
           |
           |
    Engineering Cost
    (increases exponentially near 100%)

    Feature Velocity Cost
    (decreases as error budget grows)
```

**Key Concepts:**

**User harm threshold:** The reliability level below
which measurable user harm occurs. Signals: increased
support tickets, decreased conversion, increased
churn. The SLO lower bound must be above this threshold.

**Reliability over-engineering threshold:** The
reliability level above which additional investment
produces no measurable user benefit. Above this
threshold: engineering spend is waste.

**Error budget position:** Where the current error
budget consumption sits relative to budget limits.
Healthy budget (< 50% consumed): SLO may be too
conservative. Budget in deficit: SLO may be too
aggressive for current service maturity.

---

### \\u23f1\\ufe0f Understand It in 30 Seconds

**One line:**
The right SLO is the one where users would notice
degradation if you went below it - not the one that
makes engineers proud.

> The core trade-off:
>
> **Tight SLO (99.99%):**
>   + Users protected from most failures
>   - Massive engineering investment
>   - Feature velocity: very low
>   - Error budget: tiny (52 minutes/year)
>   - Risk: over-engineering for most use cases
>
> **Loose SLO (99.0%):**
>   + Minimum engineering investment
>   + High feature velocity (large error budget)
>   - Users experience frequent failures
>   - Risk: user harm and churn
>
> **Calibrated SLO (based on user research):**
>   + Set at user harm threshold
>   + Engineering investment proportional to need
>   + Feature velocity preserved above threshold
>   + Error budget sized to actual risk tolerance
>   - Requires user research and cost analysis
>
> The framing question: "What is the user harm
> threshold for this service?" Not "What sounds
> like a good SLO?"

---

### \\U0001f529 First Principles Explanation

**THE THREE-FORCE TRADE-OFF:**

```
Force 1: User Experience (Revenue-linked)
  Data source: A/B testing, user research, support tickets

  Example: E-commerce checkout
  - Checkout error rate > 1%: measurable cart abandonment
    (A/B test: 3% increase in abandonment per 1% error rate)
  - Checkout error rate > 5%: severe conversion drop
    (negative reviews, social media complaints)
  - User harm threshold: ~0.5% error rate
  - Implied SLO lower bound: 99.5%

Force 2: Engineering Cost of Reliability
  99.0% to 99.9%: moderate effort
    Add monitoring, basic redundancy, on-call rotation
    Cost: 1 SRE-month/year maintenance
  99.9% to 99.99%: significant effort
    Add circuit breakers, multi-region failover,
    chaos testing, zero-downtime deploys
    Cost: 3 SRE-months/year maintenance
  99.99% to 99.999%: massive effort
    Global active-active, shadow testing, full
    correlated failure analysis
    Cost: 10+ SRE-months/year maintenance

Force 3: Feature Velocity Cost
  SLO = 99.9%, error budget = 0.1% (43.2 min/month)
  If team consumes 80% of budget: 34 min/month used
  Feature releases restricted when budget < 10%:
    ~1 week/month of release freeze risk

  SLO = 99.5%, error budget = 0.5% (216 min/month)
  Much larger budget: far fewer release freezes
  Trade: users experience more failures

OPTIMAL SLO SETTING:
  Set SLO at the user harm threshold.
  DO NOT set tighter than needed.
  DO NOT set looser than user harm threshold.
  Review quarterly with fresh user experience data.
```

**THE SLO DECISION TREE:**

```
1. Is there user research on the harm threshold?
   YES: set SLO at threshold + small margin (e.g., 0.1%)
   NO: use proxy signals (support tickets, churn data)
       or start with industry baseline, revise in 90 days

2. Is the engineering cost to achieve the SLO feasible?
   YES: proceed
   NO: either invest in reliability infrastructure
       or negotiate a looser SLO that is achievable
       (communicating the risk to product/business)

3. Does the error budget support feature velocity?
   YES: current SLO is well-calibrated
   NO (budget too small for planned release cadence):
     Two options:
     a. Loosen the SLO (discuss user harm trade-off)
     b. Reduce release cadence (discuss feature delay cost)

4. Is the error budget consistently unused?
   YES (budget > 90% remaining every month):
     The SLO is probably too loose
     OR the service is over-engineered
     Consider tightening the SLO
     OR use unused budget for proactive chaos testing

5. Review quarterly:
   Is there new user research that changes the harm threshold?
   Has the service matured enough to tighten the SLO?
   Has the engineering cost to maintain the SLO changed?
```

---

### \\U0001f9ea Thought Experiment

**THE FIVE-NINES HOTEL:**

A hotel advertises "99.999% reliable room service"
(5 nines: 5.26 minutes downtime per year). The cost
of achieving this is staggering: 24/7 staff redundancy,
backup kitchens, emergency menu protocols, staff
training to handle any failure scenario within seconds.

A competing hotel offers "99.5% reliable room service"
(1.8 hours downtime per year). Cost: standard staffing.
Price: 30% lower.

Guest research shows: "I ordered room service 3 times
during my 3-night stay. I would notice if it was
late or unavailable once." That's 1/3 = 33% tolerance
for single-order failure. At the order level, 99.5%
availability is far above their tolerance threshold.

The 99.999% hotel is over-investing in reliability
that guests do not perceive. The 99.5% hotel is
offering adequate reliability at better price.

Now change the scenario: the hotel is a hospital with
IV medication delivery. A single failure is life-
threatening. 99.999% is appropriate because the user
harm threshold is effectively 0% tolerance for failure.

The SLO must match the user harm threshold of the
specific service context. No universal "right" SLO.

---

### \\U0001f9e0 Mental Model / Analogy

> SLO trade-off framing is car safety engineering.
>
> A car manufacturer faces three forces: (1) Safety
> standards (minimum acceptable crash protection -
> the user harm threshold), (2) Engineering cost of
> safety features (airbags, crumple zones, ABS: each
> adds cost), (3) Price/performance for the market
> segment (a budget car cannot carry $50K in safety
> systems).
>
> The manufacturer does not try to make the car "as
> safe as possible." That would produce a vehicle
> with military-grade armour at astronomical cost.
> Instead: they calibrate safety to the market's
> requirements and regulations (the user harm threshold)
> and optimise cost within those constraints.
>
> Your SLO is the safety target. The user harm
> threshold is the regulatory minimum. The engineering
> cost is the design constraint. The feature velocity
> cost is the market price competitiveness. The
> calibrated SLO is the car that passes safety
> standards at competitive cost.

---

### \\U0001f4f6 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
SLO trade-off framing is a structured way to decide
how reliable a service needs to be. Instead of picking
a number that "sounds good" (like 99.9%), you ask:
"at what reliability level would users actually notice
and be harmed?" That becomes your target. Not tighter
(waste), not looser (user harm).

**Level 2 - Key questions (junior):**
Three questions: (1) What is the user harm threshold
- below what reliability do users complain or leave?
(2) What does it cost in engineering to achieve each
reliability level? (3) How does the SLO affect feature
release velocity (via error budget size)? Use answers
to these to calibrate the SLO.

**Level 3 - The decision process (mid-level):**
Use user research (A/B tests, support ticket analysis,
churn correlation) to identify the harm threshold.
Use engineering estimates to understand the cost
curve for each 9 of reliability. Use error budget
consumption history to validate that the SLO supports
the team's release cadence. Review quarterly.

**Level 4 - Organisational dynamics (senior):**
SLO targets are negotiated between SRE (engineering
cost), product management (user experience and feature
velocity), and finance (cost of reliability investment).
The SRE role is to make the trade-offs explicit and
provide data. The negotiation should NOT be about
"how reliable can we make this?" but "what is the
minimum reliability that avoids user harm, and can
we afford it?" If the answer is "the minimum reliable
enough SLO costs too much," the service has a
fundamental architecture problem that SLO tuning
cannot solve.

**Level 5 - Portfolio management (staff):**
At a portfolio of 50+ services, each with its own
SLO, the trade-off framing becomes a resource
allocation problem: how do you distribute SRE
engineering capacity across services with different
user harm thresholds and different marginal reliability
costs? Services with high user harm threshold AND
high reliability cost (e.g., checkout at 99.99% vs
search at 99.5%) get disproportionate reliability
investment. Services with low harm threshold AND
low engineering cost get minimum viable SLO. This
is the "reliability portfolio" - allocating limited
SRE resources to the services where reliability
investment has the highest user impact per
engineering-hour.

---

### \\u2699\\ufe0f How It Works (Mechanism)

**USER HARM THRESHOLD ANALYSIS:**

```python
# Correlate error rate with user-visible metrics
# to identify the SLO lower bound

import pandas as pd
import numpy as np
from scipy import stats

def find_harm_threshold(
    error_rates: list[float],
    conversion_rates: list[float],
    support_tickets: list[int],
) -> dict:
    """
    Identify the error rate at which user harm begins.
    Uses correlation and regression analysis.
    """
    df = pd.DataFrame({
        "error_rate": error_rates,
        "conversion": conversion_rates,
        "tickets": support_tickets,
    })

    # Pearson correlation: error rate vs conversion
    r_conv, p_conv = stats.pearsonr(
        df["error_rate"], df["conversion"]
    )
    # Pearson correlation: error rate vs support tickets
    r_tick, p_tick = stats.pearsonr(
        df["error_rate"], df["tickets"]
    )

    # Find the inflection point where conversion
    # rate starts declining (piecewise linear regression)
    # Simplified: find the breakpoint
    threshold_estimates = []

    # Look for the error rate where conversion drops > 1%
    for i, (err, conv) in enumerate(
        zip(df["error_rate"], df["conversion"])
    ):
        if i > 0:
            conv_drop = (
                df["conversion"].iloc[0] - conv
            ) / df["conversion"].iloc[0]
            if conv_drop > 0.01:  # > 1% conversion drop
                threshold_estimates.append(err)
                break

    return {
        "conv_correlation": r_conv,
        "conv_p_value": p_conv,
        "ticket_correlation": r_tick,
        "harm_threshold": (
            min(threshold_estimates) if threshold_estimates
            else None
        ),
        "recommendation": (
            f"SLO lower bound: {1 - min(threshold_estimates):.3%}"
            if threshold_estimates else "Insufficient data"
        ),
    }
```

**ERROR BUDGET VELOCITY ANALYSIS:**

```python
def error_budget_velocity_report(
    slo_target: float,
    window_days: int,
    monthly_deploy_count: int,
    avg_incident_risk_per_deploy: float,
    avg_incident_duration_minutes: float,
) -> dict:
    """
    Estimate error budget consumption from deploy activity
    and assess whether the SLO supports planned velocity.
    """
    # Error budget in minutes
    budget_minutes = (
        (1 - slo_target) * window_days * 24 * 60
    )

    # Expected budget consumption from deploys
    expected_incidents_per_month = (
        monthly_deploy_count * avg_incident_risk_per_deploy
    )
    expected_consumption = (
        expected_incidents_per_month * avg_incident_duration_minutes
    )

    utilisation = expected_consumption / budget_minutes

    return {
        "slo_target": f"{slo_target:.3%}",
        "budget_minutes": budget_minutes,
        "expected_consumption_minutes": expected_consumption,
        "expected_utilisation": f"{utilisation:.1%}",
        "assessment": (
            "HEALTHY: budget supports planned velocity"
            if utilisation < 0.5
            else "WARNING: deploy velocity may exhaust budget"
            if utilisation < 0.9
            else "CRITICAL: planned velocity will exhaust budget"
        ),
        "recommendation": (
            f"Loosen SLO to at least {(1 - expected_consumption / (window_days * 24 * 60 * 0.5)):.3%}"
            if utilisation > 0.9 else None
        ),
    }

# Example: checkout service
report = error_budget_velocity_report(
    slo_target=0.999,         # 99.9% SLO
    window_days=28,
    monthly_deploy_count=50,   # 50 deploys/month
    avg_incident_risk_per_deploy=0.05,  # 5% of deploys cause incident
    avg_incident_duration_minutes=15,   # avg 15 min incident
)
# expected_utilisation: ~82% (WARNING: too tight)
# recommendation: loosen SLO to 99.78% for this velocity
```

---

### \\U0001f504 The Complete Picture - End-to-End Flow

```
[User Experience Research]
  A/B test: what error rate causes measurable user harm?
  Support ticket correlation: at what error rate do tickets spike?
  Churn analysis: at what error rate does retention decline?
  Result: user harm threshold (e.g., 0.5% error rate)
  ↓
[Engineering Cost Analysis]
  What reliability can the current architecture achieve?
  Cost to improve from current to threshold: moderate/high/extreme?
  Long-term maintenance cost of each reliability level?
  ↓
[Error Budget Velocity Analysis]
  At each candidate SLO: what is the error budget size?
  Does the error budget support the planned release cadence?
  What is the expected monthly budget consumption?
  ↓
[SLO Target Selection]
  Set SLO at user harm threshold + small safety margin
  Verify engineering cost is acceptable
  Verify error budget supports planned velocity
  ↓
[Baseline and Monitor]
  Implement SLO measurement
  Track actual budget consumption vs predicted
  ↓
[Quarterly Review]
  Is the SLO still calibrated to user harm threshold?
  Has the cost to maintain the SLO changed?
  Is the error budget healthy or under pressure?
  Should the SLO be tightened (service has matured)
  or loosened (cost too high for marginal user benefit)?
  ↓
[Negotiate Changes]
  SLO changes require explicit trade-off discussion:
  "Tightening SLO from 99.9% to 99.99% costs X
   engineer-months and reduces release velocity by Y.
   User benefit: Z% improvement in conversion.
   Is this worth it?"
```

---

### \\U0001f4bb Code Example

**Example 1 - BAD: Arbitrary SLO selection:**

```yaml
# BAD: SLO set without data or trade-off analysis
slo:
  service: search-api
  availability: 99.99%  # <- Why? "It sounds right"
  # No user research
  # No engineering cost analysis
  # No error budget velocity check
  # Result: engineering over-spends on reliability
  # that users cannot perceive; features delayed
```

**Example 2 - GOOD: Trade-off framed SLO:**

```yaml
# GOOD: SLO backed by explicit trade-off analysis

slo:
  service: search-api
  version: 2024-Q1

  user_harm_analysis:
    harm_threshold: 0.5%
    source: |
      A/B test (2024-01): search error rate > 0.5%
      correlates with 2.1% decrease in click-through rate.
      Below 0.5%: no measurable impact on CTR.
    confidence: high  # n=2.4M sessions

  engineering_cost:
    current_baseline: 99.7%
    cost_to_99_9: "2 sprints: add retry logic + better CDN config"
    cost_to_99_99: |
      "3 months: add multi-region failover, chaos testing,
       zero-downtime deploy pipeline."
    recommendation: 99.9% achievable with acceptable investment

  velocity_analysis:
    monthly_deploys: 30
    error_budget_99_9: 43.2 min/month
    expected_consumption: 22 min/month (51%)
    assessment: healthy - budget supports planned cadence

  decision:
    slo_target: 99.9%
    rationale: |
      Set at 0.1% above user harm threshold (0.5% error rate).
      Engineering cost: moderate (2 sprint investment).
      Error budget: healthy (51% expected consumption).
      Next review: 2024-Q2 - reassess if traffic grows.
```

---

### \\u2696\\ufe0f Comparison Table

| SLO Approach | Cost | User Impact | Velocity | Risk |
|---|---|---|---|---|
| Too tight (99.999%) | Massive | No incremental benefit beyond harm threshold | Very low (tiny error budget) | Engineering waste, burnout |
| Too loose (99.0%) | Minimal | Users experience frequent failures | Very high | User harm, churn, revenue loss |
| Arbitrary (picked a number) | Unknown | Unknown | Unknown | May be wrong in either direction |
| Trade-off framed (harm threshold-calibrated) | Proportional to need | Protected at threshold | Optimised for budget size | Minimal - data-driven |

---

### \\u26a0\\ufe0f Common Misconceptions

| Misconception | Reality |
|---|---|
| "Higher SLO is always better" | Above the user harm threshold, higher SLO means engineering waste with no user benefit. The optimal SLO is exactly at the harm threshold - not above it. |
| "The same SLO applies to all services" | Different services have different user harm thresholds. A checkout service (99.9% or tighter) and a recommendations engine (99.0% acceptable) should have different SLOs reflecting their different user impact. |
| "SLO setting is a one-time decision" | User behavior changes, traffic grows, service architecture evolves, and engineering capacity changes. SLOs must be reviewed quarterly to remain calibrated. |
| "Unused error budget means the SLO is healthy" | Consistently unused budget means the SLO is too loose (service is more reliable than required) OR the team is too conservative in deployments. Intentionally use the budget for chaos experiments and aggressive deployments to validate the system's resilience. |

---

### \\U0001f6a8 Failure Modes & Diagnosis

**SLO set too tight, killing velocity**

**Symptom:**
Team cannot release features because the error budget
is exhausted. The team spends 60% of sprint time on
reliability improvements. User-facing features are
delayed by weeks. Engineers are frustrated.

**Root Cause:**
The SLO was set at 99.99% based on "we want to be
world-class." No user harm analysis was performed.
The actual user harm threshold is 99.5% - users do
not notice the difference between 99.9% and 99.99%.
The team is over-investing in reliability that users
cannot perceive.

**Diagnosis and Fix:**
```
1. Measure actual user harm threshold:
   - Check: at 99.9% availability, are users
     complaining? Are conversion metrics healthy?
   - If no user harm at 99.9%: the SLO is too tight.

2. Compute the velocity cost of the current SLO:
   - Budget: 0.01% * 43,200 min = 4.32 min/month
   - Expected consumption at current deploy cadence:
     30 deploys * 5% incident risk * 5 min avg = 7.5 min
   - Budget exhausted in ~17 days consistently.

3. Propose SLO revision with trade-off framing:
   "Current SLO: 99.99% (budget: 4.32 min/month)
    Proposed SLO: 99.9% (budget: 43.2 min/month)
    User harm threshold: 99.5% (from A/B data)
    Engineering cost saved: 2 SRE-months/quarter
    Feature velocity recovered: ~3 sprints/quarter
    User impact: none measurable (above harm threshold)
    Recommendation: revise SLO to 99.9%"
```

---

### \\U0001f517 Related Keywords

**Prerequisites (understand these first):**
- `SLO-Based Alerting Strategy` - the alerting model
  built on top of the calibrated SLO target
- `Formal SLO Theory` - the statistical foundations
  for understanding when an SLO is verifiable

**Builds On This (learn these next):**
- `Reliability Mental Model` - broader mental frameworks
  for thinking about system reliability
- `Service Level Objectives (SLOs) Deep Dive` - detailed
  exploration of SLO mechanics and case studies

---

### \\U0001f4cc Quick Reference Card

```
\\u250c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510
| THREE      | 1. User harm threshold (lower bound)         |
| FORCES     | 2. Engineering cost (constraint)             |
|            | 3. Feature velocity cost (opportunity cost)  |
\\u251c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u253c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510
| HARM       | Below: users complain, abandon, churn        |
| THRESHOLD  | Above: users don't notice improvement         |
|            | Source: A/B tests, support tickets, churn    |
\\u251c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u253c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510
| OPTIMAL    | Set AT harm threshold + small safety margin   |
| SLO        | NOT tighter: over-engineering, kills velocity |
|            | NOT looser: user harm                         |
\\u251c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u253c\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510
| REVIEW     | Quarterly: new user data? architecture change? |
| CYCLE      | Tighten: service over-performing              |
|            | Loosen: cost too high for marginal benefit    |
\\u2514\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2518
```

---

### \\U0001f48e Transferable Wisdom

**Reusable Engineering Principle:**
Calibrate requirements to observed thresholds, not
aspirational ones. SLO trade-off framing is a specific
instance of a general principle: requirements should
be set at the threshold where they start to matter,
not at the maximum theoretically achievable. API
rate limits: set at the rate where overuse genuinely
degrades service quality (not the maximum the hardware
can theoretically handle). Memory limits: set at the
threshold where memory usage causes actual problems
(not the minimum that technically works). Test
coverage: set at the threshold where additional coverage
prevents real regressions (not 100% because it sounds
good). In each case: over-engineering creates waste
and reduces velocity; under-engineering creates harm.
The calibration question is always: "at what level
does this metric start causing observable problems?"

---

### \\U0001f4a1 The Surprising Truth

The most counterintuitive finding from SLO trade-off
analysis: improving a service from 99.5% to 99.9%
reliability is often EASIER than improving from 99.9%
to 99.95%. The reason: the last few 9s require addressing
rare, non-deterministic failure modes - hardware faults,
network partitions, cascading failures, correlated
failures. These are harder to reproduce, test, and
fix than the common failures that keep a service from
reaching 99.9%. The marginal engineering cost per
additional 9 is not just increasing - it is increasing
super-exponentially. This is why the "what does the
user actually need?" question is so important: if
users do not need 99.99% (and their harm threshold
is 99.5%), then the company is spending exponentially
more engineering time per marginal user benefit as
it climbs from 99.9% to 99.99%.

---

### \\u2705 Mastery Checklist

**You've mastered this when you can:**
1. **[ANALYSE]** Given: a checkout service with A/B
   data showing 2.1% conversion drop at 0.5% error
   rate, current reliability at 99.7%, and 3 sprint
   cost to reach 99.9% vs 6 months to reach 99.99%.
   Justify the optimal SLO target with the three-force
   framework.
2. **[COMPUTE]** Given: 99.9% SLO, 30 deploys/month,
   5% incident rate per deploy, 15 min average incident.
   Calculate expected monthly budget consumption and
   assess whether the SLO supports the planned velocity.
3. **[IDENTIFY]** A team's error budget is consistently
   unused (> 90% remaining every month). What are two
   interpretations of this? What data would you look
   at to distinguish them? What action does each
   interpretation imply?
4. **[PRESENT]** Write a 3-bullet trade-off framing
   for proposing an SLO revision to product management.
   Include: current vs proposed SLO, user impact data,
   and engineering cost trade-off.
5. **[REASON]** Explain why "the same SLO for all
   services" is an anti-pattern. Give two concrete
   examples of services in the same company that
   should have different SLO targets, and explain why.

---

### \\U0001f9e0 Think About This Before We Continue

**Q1.** A payment processing service has a 99.99% SLO
but your user research shows users do not notice
failures below 99.9%. The team is spending 40% of
engineering time on reliability to maintain the 99.99%
target. Is this justified? What argument would you make
to lower the SLO?
*Hint: The standard argument for 99.99% payment services
is legal/regulatory (contractual SLAs with merchants,
card network requirements) - not just user experience.
Check: does the payment provider contract require 99.99%?
Do card network rules mandate a specific uptime? If so:
the SLO is externally mandated, not user-experience-
driven, and the 40% engineering investment is the cost
of compliance. If there are no external requirements:
present the data. "Our user research shows no measurable
harm at 99.9%. The cost of 99.99% is 40% of engineering
capacity. The user benefit above 99.9% is zero. Proposed:
maintain 99.99% as aspirational target but set error
budget policy to allow 99.9% operational target, reclaiming
30% engineering capacity for feature work."*

**Q2.** Your team is evaluating two candidate SLOs
for a new analytics dashboard (non-critical business
intelligence tool): 99.5% or 99.9%. The analytics
dashboard has 200 users (internal), low traffic,
and no revenue impact if it is slow or unavailable
for hours. Which SLO would you choose and why?
*Hint: For an internal BI tool with no revenue impact:
99.5% is appropriate. Arguments: (1) 200 internal users
can tolerate occasional downtime (they have other
tools, work can be deferred). User harm threshold:
probably 99.0% or even 99.5% is fine. (2) 99.9% for
a tool that is not business-critical over-invests
engineering resources. (3) Low traffic means 99.9% is
hard to measure statistically (with 200 req/day:
200 * 30 = 6,000 requests/month - borderline for verifying
99.9%). Better to use 99.5% which is easily verifiable.
(4) The engineering resources saved by not maintaining
99.9% for this tool can be invested in the checkout
service (high user harm threshold) or the payment
service (externally mandated SLO).*

**Q3 (TYPE G):** You are the SRE lead for a company
with 50 microservices of varying criticality. Design
a portfolio SLO framework: (a) classify services into
3-4 tiers by criticality, (b) define default SLO targets
for each tier, (c) define the process for overriding
the default (requiring data justification), and (d)
define the quarterly review process.
*Hint: (a) Tier definitions: Tier 1 (Revenue-critical):
checkout, payment, authentication - direct revenue impact.
Tier 2 (User-experience-critical): search, recommendations,
shopping cart - significant UX impact but not immediate
revenue. Tier 3 (Business-internal): analytics, reporting,
admin tools - internal use, delayed impact. Tier 4
(Background): async jobs, analytics pipelines, notifications -
failure is invisible to users immediately. (b) Default SLOs:
T1: 99.9% (verify with A/B data; may need 99.99% for payment),
T2: 99.5%, T3: 99.0%, T4: 95.0%. (c) Override process:
team submits "SLO Justification Document" with: user harm
threshold data, engineering cost estimate, velocity impact
analysis. SRE lead reviews quarterly; product manager signs
off. (d) Quarterly review: automated SLO health report for
all services. Flag: any service > 3 months without SLO breach
(consider tightening) or > 3 months breached (consider
loosening or reliability investment). Review meeting: 1 hour,
50 services in 90-second summary format per tier.*

---

### \\U0001f3af Interview Deep-Dive

**Q1: "How do you decide what SLO to set for a service?"**
*Why they ask:* Tests whether the candidate has a principled
approach vs cargo-culting "99.9%."
*Strong answer includes:*
- Three-force framing: user harm threshold, engineering
  cost, feature velocity.
- User harm threshold is the starting point: A/B tests,
  support ticket correlation, churn data.
- Set SLO at the threshold + small margin. Not tighter.
- Engineering cost sanity check: can we achieve this SLO
  with reasonable investment?
- Error budget velocity check: does the budget support
  planned release cadence?

**Q2: "A product manager wants to increase the SLO from
99.9% to 99.99%. How do you evaluate this request?"**
*Why they ask:* Tests ability to apply trade-off framing
under stakeholder pressure.
*Strong answer includes:*
- Ask: what is the user harm evidence for this change?
  Is there data showing users are harmed at 99.9%?
- Quantify the cost: moving from 99.9% to 99.99% requires
  what architecture changes? What is the engineering estimate?
  What is the error budget velocity impact (4x smaller budget)?
- Present the trade-off: "Here is what it costs and what
  the user benefit is. Is this investment justified by
  the user benefit data?" If PM cannot provide user harm
  evidence: the SLO change is not justified.

**Q3: "When would you LOWER an SLO?"**
*Why they ask:* Tests understanding that SLOs can be
loosened, not just tightened. Counters the assumption
that reliability always increases.
*Strong answer includes:*
- When the user harm threshold data shows users are not
  harmed at the lower target: the current SLO is over-engineered.
- When consistently unused error budget indicates the service
  is reliably above its target with no effort.
- When the engineering cost to maintain the SLO is too high
  relative to user benefit (the service has changed and
  no longer needs that level of reliability).
- When lowering the SLO would free significant engineering
  capacity for features that produce more user value than
  the marginal reliability improvement.
"""

w("OBS-050 - SLO Trade-off Framing.md", OBS_050)
print("Done OBS-050")
