---
id: OBS-048
title: Formal SLO Theory
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-012, OBS-020, OBS-042, OBS-050, OBS-053
used_by: OBS-053, OBS-054
related: OBS-040, OBS-030, OBS-051
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - concept
  - first-principles
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /obs/formal-slo-theory/
---

# OBS-048 - Formal SLO Theory

⚡ TL;DR - Formal SLO theory treats reliability as a
mathematical object: an SLO is a threshold T on a
distribution of service experience metrics, and an error
budget is the complement of that threshold - a finite
amount of "bad" experience that can be tolerated before
the SLO is violated.

| #048            | Category: Observability & SRE                                                                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SLO, Error Budget, SLO-Based Alerting Strategy, SLO Trade-off Framing, Service Level Objectives Deep Dive |                 |
| **Used by:**    | Service Level Objectives (SLOs) Deep Dive, Error Budgets                                                  |                 |
| **Related:**    | SRE Book Core Principles, Alerting Fundamentals, Reliability Mental Model                                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two engineers debate SLO target calibration: should
the availability SLO be 99.9% or 99.95%? One engineer
says "99.95% because we care about reliability." The
other says "99.9% is more achievable." Neither engineer
can articulate what the difference means concretely:
how much downtime, how many failed requests, what
engineering investment is required to move from one
to the other, and what happens to innovation velocity
if the target is set too high.

**THE BREAKING POINT:**
Without formal SLO theory, SLO target selection is
subjective and politically negotiated rather than derived
from measurement and modeling. The error budget concept
exists but lacks rigorous derivation: engineers know
"error budget = 1 - SLO" but cannot answer "what is the
right error budget for our user base?" or "how does
changing the SLO window from 30 days to 90 days change
the error budget dynamics?"

**THE INVENTION MOMENT:**
Formal SLO theory makes reliability mathematically
tractable. The key formalizations:

1. Reliability as a property of the SLI distribution
2. Error budget as a derived quantity with computable value
3. Burn rate as a continuous-time rate process on the budget
4. Multi-window alerting as an optimal detection strategy
   for budget-exhaustion events
5. Composite SLOs for multi-signal reliability

---

### 📘 Textbook Definition

**Formal SLO theory** is the mathematical framework for
reasoning about service reliability as a measurable
quantity. Given a service-level indicator (SLI) defined
as a ratio of good events to total events, an SLO is a
lower bound on this ratio measured over a time window W:

$$\text{SLO} = \Pr\left[\frac{\text{good\_events}(W)}{\text{total\_events}(W)} \geq T\right] \geq p$$

The **error budget** is the maximum number of bad events
tolerated while maintaining the SLO:

$$\text{budget}(W) = (1 - T) \times \text{total\_events}(W)$$

The **burn rate** is the instantaneous ratio of actual
bad event rate to the maximum sustainable bad event rate:

$$\text{burn\_rate}(t) = \frac{\text{bad\_rate}(t)}{\text{budget\_rate}(W)}$$

where $\text{budget\_rate}(W) = \frac{(1-T)}{|W|}$.
A burn rate > 1 means the budget is being depleted.
A burn rate = 14.4 exhausts the monthly budget in 2 days.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Formal SLO theory gives you the mathematics to compute
exactly how much reliability you have, how fast you are
losing it, and when you will run out.

**One analogy:**

> Formal SLO theory is like the physics of a bank account.
> Without the math, you know "I have money and I spend it."
> With the physics: the account starts at $1,000 (error
> budget). You have an income of $0 (can't earn back budget
> mid-window). Withdrawals happen at a rate r (error rate).
> If r > budget/window, you will be overdrawn before the
> month ends. Burn rate = r / (budget/window) tells you how
> fast you are drawing down. At burn rate 14.4, the account
> is empty in 2 days. The multi-window alert is the overdraft
> protection system - it fires when the burn rate is high
> enough in a short window AND sustained in a longer window.

**One insight:**
The formal framing reveals the non-obvious: the error budget
is not just a number - it is a rate process. An error budget
remaining of 50% has completely different implications
depending on which day of the 30-day window you are on
(day 3 vs day 27). The remaining budget on day 3 should
never be spent down quickly; the remaining budget on day 27
can signal a near-miss even if 50% remains (the window
ends soon, unused budget is "wasted" innovation capacity).

---

### 🔩 First Principles Explanation

**SLI FORMAL DEFINITION:**

An SLI is a ratio:

$$\text{SLI}(t_1, t_2) = \frac{\#\{good\_events : t_1 \leq t \leq t_2\}}{\#\{total\_events : t_1 \leq t \leq t_2\}}$$

where "good event" is defined by the service team
(e.g., HTTP response with status < 500 and latency < 300ms).

**SLO FORMAL DEFINITION:**

An SLO is a constraint on the SLI:

$$\text{SLO target } T \text{ means: } \text{SLI}(t, t+W) \geq T \text{ for almost all windows}$$

In practice: measured over a rolling or calendar window W,
the SLO is met when SLI ≥ T.

**ERROR BUDGET DERIVATION:**

$$\text{budget}(W) = (1 - T) \times E[\text{total\_events}(W)]$$

For SLO = 99.9%, W = 30 days, 1000 RPS:

- Total events = 1000 × 86400 × 30 = 2.592 billion
- Budget = 0.001 × 2.592B = 2.592 million bad events
- Budget in time = 2.592M / 1000 = 43.2 minutes of 100% errors

**BURN RATE FORMAL DEFINITION:**

Let $b(t)$ = remaining budget at time t. The budget depletes as:

$$\frac{db}{dt} = -r_{\text{bad}}(t) + r_{\text{budget\_rate}}$$

where $r_{\text{budget\_rate}} = \frac{(1-T)}{|W|} \times \lambda$
(budget replenishment rate, where λ = total event rate).

The net depletion rate is:

$$\frac{db}{dt} = \lambda \cdot ((1-T) - p_{\text{bad}}(t))$$

where $p_{\text{bad}}(t)$ is the current bad event probability.
This is negative (budget depleting) when $p_{\text{bad}} > (1-T)$.

**BURN RATE NORMALIZATION:**

$$\text{burn\_rate}(t) = \frac{p_{\text{bad}}(t)}{1 - T}$$

When burn_rate = 1: depleting at exactly the sustainable rate.
When burn_rate = k: budget exhausted in W/k time.

For k = 14.4 and W = 30 days: exhausted in 30/14.4 = 2.08 days.

**COMPOSITE SLO:**

For a service with two SLIs (availability AND latency),
the composite SLO is the intersection:

$$\text{SLO}_{\text{composite}} = \text{SLI}_{\text{avail}} \geq T_A \text{ AND } \text{SLI}_{\text{latency}} \geq T_L$$

Each SLI has its own error budget. The budget is exhausted
by whichever SLI degrades first.

---

### 🧪 Thought Experiment

**THE WINDOW CHOICE PROBLEM:**

You can express the same SLO as:

- 99.9% over 30 days (monthly rolling window)
- 99.9% over 90 days (quarterly rolling window)
- 99.9% over 7 days (weekly rolling window)

**Are these equivalent?**

They are NOT equivalent. The formal difference:

**Error budget absolute size:**

- 30-day: 43.2 minutes of budget
- 90-day: 129.6 minutes of budget (3x larger)
- 7-day: 10.1 minutes of budget (2.3x smaller)

**Burn rate calibration:**

- PAGE_BURN_RATE = 14.4 works for any window because
  14.4x exhausts 5% of budget in 1/14.4 of the window
  (approximately 50 hours for 30 days, 150 hours for 90 days)

**Recovery dynamics:**

- 30-day window: an incident consuming 50% budget (21.6 min
  of 100% errors) takes 30 days to "roll out" of the window
  as new time replaces old time
- 90-day window: same incident takes 90 days to recover from
  - much longer "memory" for bad events
- 7-day window: same incident is "forgotten" in 7 days
  - very short memory, may encourage tactical patching

**PRACTICAL IMPLICATION:**

- 7-day windows make SLO gaming easy (be reliable every
  week except Monday night; each week resets)
- 90-day windows are punishing - a single major incident
  can keep the team below SLO for a full quarter
- 30-day windows balance incident memory against recovery
  opportunity - the industry standard for this reason

---

### 🧠 Mental Model / Analogy

> Formal SLO theory is like the thermodynamics of
> reliability. Just as thermodynamics gives you equations
> for how energy flows through a system, formal SLO theory
> gives you equations for how reliability "flows" through
> a service over time. The error budget is thermal energy -
> it can be expended (bad events) but cannot be recovered
> within the window. The burn rate is the thermal power
> dissipation rate. The multi-window alert is the
> overheat protection system. And just as thermodynamics
> tells you the maximum efficiency of a heat engine
> (Carnot limit), SLO theory tells you the maximum
> change velocity you can sustain while staying within
> the reliability constraint.

Where this analogy breaks down: thermodynamic systems
have conservation laws (energy is conserved); error
budgets do not have a conservation law - unused budget
at end of window is not "rolled over" (in most implementations).
This is a deliberate organizational choice to prevent
budget hoarding.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Formal SLO theory is the math behind reliability targets.
It gives precise definitions for: how good your service
must be (SLO), how much badness you can afford (error
budget), and how fast you are using up that budget
(burn rate). With this math, "how reliable is our service?"
has a measurable answer.

**Level 2 - How to use it (junior developer):**
Compute error budget: budget = (1 - SLO) × window duration.
For 99.9% SLO over 30 days: budget = 0.001 × 43,200 min
= 43.2 minutes. Track burn rate: if error rate is 2%
(20x the 0.1% budget rate), burn rate = 20, budget will
last 30/20 = 1.5 days. Use the burn rate to set alert
thresholds: alert when burn rate > 14.4 (exhausts budget
in 2 days).

**Level 3 - How it works (mid-level engineer):**
The formal SLO model has three components: (1) SLI
measurement (compute the good/total ratio over the window),
(2) error budget tracking (remaining budget = target - consumed
as a running total), (3) burn rate alerting (compute
instantaneous error rate / budget rate and alert when
sustained above threshold). The burn rate formula normalizes
across different SLO targets: a 99% SLO and a 99.9% SLO
with the same burn rate of 14.4 are both consuming budget
at the same relative pace, even though their absolute
error rates are 10x different.

**Level 4 - Why it was designed this way (senior/staff):**
The burn rate normalization is the key insight: it makes
alert thresholds independent of the SLO target. Without
burn rate normalization, a team with a 99.9% SLO would
alert at error rate > 1.44% (14.4 × 0.1%), while a team
with a 99.5% SLO would alert at error rate > 7.2% (14.4 × 0.5%).
Both teams have the same page-worthy event: their budget
will be exhausted in 2 days. The alert threshold in
terms of raw error rate is different, but in terms of
burn rate (the normalized quantity), it is identical at 14.4.
This means the alerting standard can be codified once
(burn rate > 14.4) and applied uniformly across all services
regardless of their specific SLO targets.

**Level 5 - Mastery (distinguished engineer):**
The formal model breaks down at the boundaries:
(1) Very low traffic: statistical fluctuation in error
rate dominates burn rate computation; a single error on
a service with 1 req/min is a 100% error rate for that
minute - burn rate 1000. The response: require minimum
traffic thresholds for SLO measurement, or use Bayesian
smoothing on the error rate estimate.
(2) Correlated failures: the burn rate model assumes
errors are independent events. A major infrastructure
failure produces a correlated burst: all services fail
simultaneously, burning all error budgets simultaneously.
The response: define composite platform SLOs that account
for correlated failure modes.
(3) User heterogeneity: if your 0.1% of errors hit the
same 0.1% of users every time (e.g., international users
with high-latency connections), the error budget model
says "within SLO" but the actual user experience for
that subset is 100% bad. The response: disaggregate SLOs
by user cohort for high-value customer segments.

---

### ⚙️ Why It Holds True

**The Formal Foundation:**

The error budget model is derived from the law of large
numbers: over long windows with many events, the SLI
converges to its expectation. This justifies the window-
based measurement approach - rare events average out,
sustained degradation becomes visible.

The burn rate model is a continuous-time approximation:
rather than computing cumulative budget consumed, compute
the instantaneous rate of consumption and extrapolate.
This approximation is accurate when events are approximately
Poisson-distributed and the time window is long relative
to the scrape interval.

**WHY MULTI-WINDOW ALERTING IS OPTIMAL:**

For a fixed false positive budget (you can tolerate N
false pages per month), what is the optimal alert strategy
to detect budget-threatening events quickly?

Single short window (1 minute): detects fast burns quickly,
but high noise (transient spikes look like fast burns).
Single long window (1 hour): low noise, but slow to detect
fast burns (takes 60 minutes to confirm a fast burn).
Multi-window (check both 5-minute AND 1-hour): fast detection
(5-minute window catches fast burns quickly) with low noise
(1-hour window filters transient spikes). This is the Pareto-
optimal point on the detection speed vs. noise trade-off.

**THE MATHEMATICAL PROOF (simplified):**
A transient spike lasting t_spike minutes at burn rate B:

- 5-minute window shows: B × (t_spike / 5) if t_spike < 5
- 1-hour window shows: B × (t_spike / 60) if t_spike < 60
- Multi-window threshold: BOTH windows > 14.4
- To trigger 5-min: t_spike > 5 × (14.4 / B)
- To trigger 1-hour: t_spike > 60 × (14.4 / B)
- Multi-window fires only when 1-hour also triggered
- For B = 100 (very fast burn): 1-hour fires after 8.7 min
- This means false positives are filtered at the cost of
  8.7-minute detection latency for very fast burns
- The trade-off is explicitly stated and adjustable

---

### 🔄 System Design Implications

**SLO DESIGN PATTERNS:**

```
Pattern 1: Request/Response SLI
  SLI = HTTP responses with status < 500
         and latency_p99 < 500ms
       / total_HTTP_responses

  Good for: APIs, web services
  Challenge: latency_p99 threshold is a percentile, not
  a per-request measurement. Better: use latency as a
  separate SLI with its own error budget.

Pattern 2: Availability × Latency Composite
  SLI_avail = non-error responses / total
  SLI_latency = responses < threshold / total

  Composite SLO: SLI_avail >= 99.9%
                 AND SLI_latency >= 95%

  Each SLI depletes its own error budget.
  On-call is paged when EITHER budget is on fast burn.
  This covers: "service is up but slow" (latency budget burns)
               "service is down" (availability budget burns)

Pattern 3: User-Journey SLI (synthetic canary)
  SLI = synthetic transaction success rate
        measured end-to-end from user perspective

  Advantage: captures failures invisible to per-service SLIs
             (e.g., config change breaks user flow but
             no individual service reports errors)
  Challenge: canary transactions must be realistic but
             harmless; complex to implement for all journeys

Choosing window length:
  - 30 days: industry standard, balanced memory/recovery
  - 7 days: aggressive, fast feedback, easy to game
  - 90 days: conservative, long memory for major incidents
  - Rolling vs calendar: rolling is simpler to compute;
    calendar aligns with business reporting cadence
```

**ERROR BUDGET POLICY DESIGN:**

```
Derived from formal model:
  Budget consumed: 0-25% → no restrictions
  Budget consumed: 25-50% → reliability review triggered
  Budget consumed: 50-75% → feature freeze eligible
  Budget consumed: 75-100% → feature freeze mandatory
  Budget exhausted (>100%) → postmortem required,
    no new features until root cause addressed

WHY THIS SPECIFIC CALIBRATION:
  25% threshold = 10.8 minutes consumed on 43.2 minute budget
  This is 1 typical incident (5-10 minutes of degradation)
  One incident per month is normal operating rate → review
  Two incidents (50%) = elevated rate → corrective action
  Four incidents (100%) = chronic reliability problem → freeze

  The policy is derived from the budget math, not arbitrary.
```

---

### 💻 Code Example

Not applicable as the primary example - Formal SLO Theory
is a conceptual framework. See the mathematical derivations
in the sections above and the implementation in:

- `OBS-042 SLO-Based Alerting Strategy` for Prometheus
  burn rate alert rules
- `OBS-053 Service Level Objectives (SLOs) Deep Dive`
  for SLO lifecycle and measurement implementation
- `OBS-054 Error Budgets` for error budget policy implementation

The formal computation:

```python
# Formal SLO math in Python

def error_budget_minutes(slo_target: float,
                          window_days: int) -> float:
    """
    Compute error budget in minutes.

    Args:
        slo_target: e.g., 0.999 for 99.9%
        window_days: e.g., 30

    Returns:
        Error budget in minutes
    """
    error_rate = 1 - slo_target     # 0.001 for 99.9%
    window_minutes = window_days * 24 * 60
    return error_rate * window_minutes

# Examples
print(error_budget_minutes(0.999, 30))   # 43.2 minutes
print(error_budget_minutes(0.9999, 30))  # 4.32 minutes
print(error_budget_minutes(0.995, 30))   # 216.0 minutes


def burn_rate(current_error_rate: float,
              slo_target: float) -> float:
    """
    Compute current burn rate.

    Args:
        current_error_rate: e.g., 0.02 for 2%
        slo_target: e.g., 0.999 for 99.9% SLO

    Returns:
        Burn rate (1.0 = sustainable rate)
    """
    budget_rate = 1 - slo_target   # 0.001
    return current_error_rate / budget_rate

# Examples
print(burn_rate(0.02, 0.999))   # 20.0
print(burn_rate(0.01, 0.999))   # 10.0
print(burn_rate(0.001, 0.999))  # 1.0 (exactly sustainable)


def time_to_budget_exhaustion_hours(burn_rate_val: float,
                                     window_days: int = 30
                                     ) -> float:
    """
    Given a burn rate, how many hours until budget exhausted?
    """
    window_hours = window_days * 24
    return window_hours / burn_rate_val

# Examples
print(time_to_budget_exhaustion_hours(14.4))  # 50.0 hours
print(time_to_budget_exhaustion_hours(1.0))   # 720.0 hours = 30 days
print(time_to_budget_exhaustion_hours(0.5))   # infinite (not consuming)
```

---

### ⚖️ Comparison Table

| SLO Model                                 | Formalism Level | Practical Adoption             | Use Case                             |
| ----------------------------------------- | --------------- | ------------------------------ | ------------------------------------ |
| **Formal SLO (error budget + burn rate)** | High            | Industry standard (Google SRE) | All production services with on-call |
| Threshold SLA (e.g., "99.9% uptime")      | Low             | Traditional enterprise         | Contractual SLAs with customers      |
| Percentile latency targets (p99 < 300ms)  | Medium          | Common in engineering teams    | Latency-focused services             |
| None (no formal reliability target)       | None            | Common in early-stage          | Very early stage, no on-call         |

**How to choose:**
Use formal SLO with error budget for any service with
a dedicated on-call rotation. The burn rate alerting model
requires the formal SLO definition - you cannot implement
it with informal reliability targets. For contractual SLAs
with customers, use formal SLOs internally and translate
to SLA language for the contract (the SLA is typically
lower than the internal SLO, with the gap being the buffer).

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                           |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SLO = SLA                               | SLO is internal reliability target; SLA is the contractual agreement with customers. SLO is typically stricter. Breaching SLO triggers internal action; breaching SLA triggers customer compensation              |
| Error budget is just "allowed downtime" | Error budget is a rate-based model: it measures bad events per total events, not just downtime. A service that is "up" but returns errors or high latency consumes its error budget just as a "down" service does |
| Higher SLO target = better reliability  | Higher SLO targets constrain innovation (less budget for risky deployments). The correct SLO is calibrated to what users actually notice and value, not to the highest achievable number                          |
| 100% reliability is achievable          | 100% availability SLO means zero tolerance for any failure - including planned maintenance windows. No real production system achieves this. The practical upper bound is 99.999% (5 nines = 5.2 min/year)        |

---

### 🚨 Failure Modes & Diagnosis

**SLO Calibration Too Tight (100% budget consumed every month)**

**Symptom:**
Every month, the team's error budget is exhausted by day 20.
Feature development is in permanent freeze. The team has
anxiety about deploying anything because any deploy risks
consuming the remaining budget. Innovation velocity has
dropped to near zero.

**Root Cause:**
The SLO target was set too high relative to the service's
current reliability capability. A service at 99.8% natural
reliability set to a 99.9% SLO will consume budget in
every incident because its natural error rate (0.2%) is
already 2x the budget rate (0.1%).

**Fix:**

1. Measure the service's baseline reliability over 3 months.
2. Set the initial SLO target at baseline reliability minus
   1-sigma of variation. This ensures budget is not consumed
   on "normal" variation, only on genuine incidents.
3. Tighten the SLO target quarterly as reliability improves
   through engineering investment.

**Root Cause (alternative):**
SLI definition includes non-user-visible errors (e.g.,
retried requests that ultimately succeed are counted as errors).
Fix: use the user-observable outcome (did the user get a
successful response?) not the implementation outcome
(did any individual request fail?).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLO` - the basic SLO concept before formal theory
- `Error Budget` - the budget concept before formal derivation
- `SLO-Based Alerting Strategy` - the alerting application
  of burn rate theory
- `SLO Trade-off Framing` - the practical decisions this
  theory supports
- `Service Level Objectives (SLOs) Deep Dive` - the lifecycle
  this theory formalizes

**Builds On This (learn these next):**

- `Service Level Objectives (SLOs) Deep Dive` - applying
  this theory to the full SLO lifecycle
- `Error Budgets` - the operational use of the budget concept

**Alternatives / Comparisons:**

- `SRE Book Core Principles` - the organizational context
  in which this theory is applied
- `Alerting Fundamentals` - pre-burn-rate alerting that
  this theory supersedes
- `Reliability Mental Model` - the mental model that this
  formal theory makes rigorous

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ SLO            │ SLI ≥ T measured over window W       │
│ DEFINITION     │ T = reliability target (e.g., 0.999) │
├────────────────┼────────────────────────────────────────┤
│ ERROR BUDGET   │ (1 - T) × window_minutes             │
│ FORMULA        │ e.g.: (1-0.999) × 43200 = 43.2 min   │
├────────────────┼────────────────────────────────────────┤
│ BURN RATE      │ current_error_rate / (1 - T)         │
│ FORMULA        │ e.g.: 0.02 / 0.001 = 20              │
├────────────────┼────────────────────────────────────────┤
│ TIME TO        │ window_hours / burn_rate             │
│ EXHAUSTION     │ e.g.: 720 / 20 = 36 hours            │
├────────────────┼────────────────────────────────────────┤
│ PAGE THRESHOLD │ burn_rate > 14.4 in BOTH 5min AND   │
│                │ 1h windows (will exhaust 5% in 1h)  │
├────────────────┼────────────────────────────────────────┤
│ WINDOW CHOICE  │ 30 days: industry standard.          │
│                │ 7d: fast feedback, easy to game.     │
│                │ 90d: long memory for major incidents  │
├────────────────┼────────────────────────────────────────┤
│ ONE-LINER      │ "Burn rate normalizes error rate to  │
│                │ budget consumption rate, making      │
│                │ alert thresholds SLO-independent."   │
├────────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE   │ SLOs Deep Dive → Error Budgets       │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Error budget = (1 - SLO) × window. For 99.9% over 30 days:
   43.2 minutes. This is the finite resource on-call engineers
   are custodians of.
2. Burn rate = error_rate / (1 - SLO). Burn rate of 14.4
   means the budget will be exhausted in 30 days / 14.4 = 2 days.
   This is the page threshold.
3. Window choice matters: 30-day windows are the industry
   standard. 7-day windows produce erratic budget dynamics.
   90-day windows are punishing after major incidents.

**Interview one-liner:**
"Formal SLO theory formalizes reliability as a ratio SLI =
good_events / total_events bounded by target T over window W.
Error budget = (1-T) × window_duration. Burn rate =
current_error_rate / (1-T) - this normalization makes 14.4
the universal PAGE threshold regardless of SLO target:
burn_rate 14.4 exhausts 30-day budget in 2 days for any
SLO value. Multi-window alerting (both 5min AND 1h > 14.4)
is the optimal detection strategy: short window detects
fast burns, long window filters transient spikes."

> Entry stub. Generate full content using Master Prompt v3.0.
