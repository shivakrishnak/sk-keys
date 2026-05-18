---
id: SYD-015
title: "SLA / SLO / SLI"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-002, SYD-003
used_by: SYD-016, SYD-017
related: SYD-002, SYD-003, SYD-016, SYD-017, SYD-018
tags:
  - architecture
  - reliability
  - operations
  - observability
  - site-reliability-engineering
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/syd/sla-slo-sli/
---

⚡ TL;DR - SLIs measure what you observe, SLOs set
the target you commit to, and SLAs are the contract
with consequences if you miss. The three form a
reliability framework that turns vague "high
availability" goals into measurable engineering targets.

| #015 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Non-Functional Requirements, Availability | |
| **Used by:** | Error Budget, MTTR / MTBF | |
| **Related:** | Non-Functional Requirements, Availability, Error Budget, MTTR / MTBF, RTO / RPO | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineering team tells stakeholders: "Our service
has high availability." What does that mean? Is one
hour of downtime per year acceptable? Per month? Per
day? When an incident occurs and the service is down
for 2 hours, is that a serious failure or business
as usual? Without defined targets, engineering teams
cannot prioritize reliability work, incidents have
no benchmark to evaluate against, and customers have
no basis for holding the service accountable.

**THE BREAKING POINT:**
"High availability" is not a specification. It is
a marketing claim. For reliability to be engineered
rather than hoped for, it must be measured (SLI),
targeted (SLO), and contracted (SLA). Without this
framework, every incident is evaluated subjectively,
and reliability investments compete against features
with no principled way to allocate resources.

**THE INVENTION MOMENT:**
Google's Site Reliability Engineering book (2016)
formalized the SLI/SLO/SLA framework based on
practices that Google had developed internally from
the early 2000s. The framework solved a persistent
problem: how do you make reliability a first-class
engineering concern with objective targets, instead
of an ill-defined aspiration?

---

### 📘 Textbook Definition

**SLI (Service Level Indicator):** A quantitative
measure of a specific aspect of service behavior.
Examples: request success rate (%), latency (ms at
p99), error rate (%), throughput (req/s). SLIs are
measured in real time from metrics or logs.

**SLO (Service Level Objective):** An internal target
for an SLI. "Our success rate SLO is 99.9% over a
30-day rolling window." SLOs are set by engineering
teams and drive reliability engineering decisions.
Missing an SLO triggers an error budget alert.

**SLA (Service Level Agreement):** A contractual
commitment to customers with financial penalties or
credits if SLOs are missed. SLAs are typically
stricter than the internal SLOs they are based on,
providing a safety margin.

The relationship: SLI = what you measure, SLO =
what you target internally, SLA = what you promise
externally with consequences.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SLI measures it, SLO targets it, SLA promises it
externally with consequences.

**One analogy:**
> A restaurant:
> - SLI: average food delivery time = 22 minutes (measured)
> - SLO: internal target = deliver food in < 25 minutes
>   90% of the time
> - SLA: customer-facing promise = "30-minute guarantee
>   or your meal is free"
>
> The SLA has a safety margin vs the SLO, because
> the SLA has financial consequences.

**One insight:**
The SLO is the engineering target. The SLA is the
business commitment. If you set the SLA equal to
the SLO, you have no safety margin. The gap between
SLO and SLA is your operational buffer.

---

### 🔩 First Principles Explanation

**THE MEASUREMENT CHAIN:**

```
┌─────────────────────────────────────────────────┐
│ SLI → SLO → SLA CHAIN                          │
│                                                 │
│ SLI (measured):                                 │
│   success_rate = success_requests /             │
│                  total_requests × 100           │
│                                                 │
│ SLO (internal target):                          │
│   success_rate ≥ 99.9% over 30-day window       │
│                                                 │
│ SLA (external contract):                        │
│   success_rate ≥ 99.5% (with credits if missed) │
│                                                 │
│ Error Budget (from SLO):                        │
│   0.1% of requests may fail in 30 days          │
│   30 days × 0.1% = 43.8 minutes of downtime     │
└─────────────────────────────────────────────────┘
```

**COMMON SLI TYPES:**

| SLI Category | Measure | Example |
|---|---|---|
| Availability | Uptime fraction | 99.9% of minutes had 0 errors |
| Latency | Request duration | p99 < 300ms |
| Error Rate | Failed requests fraction | < 0.1% return 5xx |
| Throughput | Requests per second | > 500 RPS served |
| Freshness | Data recency | < 1 hour behind real-time |
| Durability | Data not lost | 99.999999% objects retained |

**SETTING THE RIGHT SLO:**
Common mistake: set SLO at "what the system currently
achieves." Wrong. SLO should reflect what users need
to have a good experience, then work backwards to
determine if the system can meet it. If the system
can't, that is a reliability engineering gap to close.

**THE TRADE-OFFS:**

**Gain:** Objective reliability target that guides
engineering investment; error budget framework for
balancing features vs reliability.

**Cost:** Measurement overhead (must instrument all
services); SLO calibration requires careful analysis
to avoid setting targets that are too easy or too hard;
SLA negotiation with legal/business complexity.

---

### 🧪 Thought Experiment

**SCENARIO: Setting SLOs for a payment API**

Questions an SRE team must answer:
1. What should we measure? → SLI selection
2. What is acceptable? → SLO setting
3. What do we promise customers? → SLA setting

**Step 1 - Choose SLIs:**
A payment API has two critical metrics:
- Success rate: % of payment transactions that complete
  without error (core user experience)
- Latency: how long the checkout takes (user patience)

**Step 2 - Set SLOs:**
- Success rate SLO: 99.95% (one in 2,000 payments fails)
- Latency SLO: p99 < 2 seconds (1% of payments can
  take longer)
- Measurement window: 30 days

**Step 3 - Error budget from SLO:**
- Success rate budget: 0.05% of requests can fail
- At 1,000 transactions/hour: 0.05% = 0.5 failures/hour
- Over 30 days: ~360 acceptable failures

**Step 4 - SLA (external):**
- Success rate SLA: 99.9% (stricter than "acceptable"
  for engineering, giving safety margin)
- Penalty: 10% service credit per 0.1% below SLA

**THE INSIGHT:**
Setting SLOs before incidents happen forces explicit
reliability prioritization. A team with a 99.95%
success SLO treats an hour of 10% error rate as
a budget-burning incident requiring immediate response.
Without an SLO, the same incident might be "just
a 10% blip for an hour" with no urgency.

---

### 🧠 Mental Model / Analogy

> Think of it like an airplane's acceptable delay
> metrics. The airline measures on-time departure
> (SLI), targets 88% on-time internally (SLO), and
> promises customers a refund if delays exceed 3 hours
> (SLA). The internal target is tighter than the
> contractual one to give operational buffer. The
> measurement (actual departure times) drives both
> the internal engineering decisions (add gate agents,
> streamline boarding) and the external promise.

- "SLI: actual departure time" → what the monitoring system reports
- "SLO: 88% on-time target" → internal engineering goal
- "SLA: 3-hour delay = refund" → business contract
- "Exceeding SLA: legal/financial consequence" → motivates the SLO

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SLI = the measurement ("our service was up 99.8%").
SLO = the target ("we aim for 99.9% uptime").
SLA = the promise to customers ("we guarantee 99.5%
uptime and will give you a refund if we miss it").

**Level 2 - How to use it (junior developer):**
Ask: what would a user notice if this metric degraded?
If they would notice → it is a candidate SLI.
Define good events: a request is "good" if it returns
2xx in < 500ms. SLI = good_requests / total_requests.
SLO = SLI ≥ 99.9% over 30 days.

**Level 3 - How it works (mid-level engineer):**
SLIs are computed from metrics (Prometheus, Datadog)
or log analysis. Error budgets are derived: budget
= (1 - SLO) × time_window. Budget burn alerts fire
when the error budget depletes faster than expected.
When budget is exhausted: freeze feature releases
until reliability is restored (the error budget policy).

**Level 4 - Why it was designed this way (senior/staff):**
The SLO framework resolves the tension between feature
velocity and reliability. Without error budgets, every
release is a potential reliability risk with no
principled limit. Error budgets create a finite, shared
resource: feature releases spend error budget (every
release has some failure probability); reliability
investment recovers it. When budget is depleted, the
policy decision to freeze features is pre-agreed,
removing it from ad-hoc negotiation.

**Level 5 - Mastery (distinguished engineer):**
The hardest part of SLO practice is SLI selection.
Bad SLIs: measuring something the system can trivially
guarantee but users don't care about (e.g., server
CPU < 90% tells users nothing about their experience);
measuring something technically correct but not
representative (e.g., health check endpoint
availability, not actual user-facing API availability).
Good SLIs: user-focused, aggregating across the full
request path, capturing both availability and latency.
The canonical formulation: SLI = good_events /
total_valid_events, where "good" is defined from
the user's perspective.

---

### ⚙️ How It Works (Mechanism)

**SLI computation (Prometheus):**

```
┌──────────────────────────────────────────────────────┐
│ SLI COMPUTATION EXAMPLES                             │
│                                                      │
│ Availability SLI:                                    │
│   sum(rate(http_requests_total{code!~"5.."}[5m]))   │
│   /                                                  │
│   sum(rate(http_requests_total[5m]))                 │
│   × 100                                              │
│   = % of requests not returning 5xx                  │
│                                                      │
│ Latency SLI:                                         │
│   histogram_quantile(0.99,                           │
│     rate(http_request_duration_seconds_bucket[5m])) │
│   = p99 latency in seconds                          │
│                                                      │
│ Error budget burn rate:                              │
│   current_error_rate / (1 - SLO_target)             │
│   = how fast you're burning the budget              │
│   > 1.0 = burning faster than sustainable           │
│   > 14.4 = will exhaust 30-day budget in 2h         │
└──────────────────────────────────────────────────────┘
```

**The error budget math:**

```
SLO = 99.9% = 0.999
Error budget = 1 - 0.999 = 0.001 = 0.1%
30 days = 43,200 minutes
Allowed downtime = 43,200 × 0.001 = 43.2 minutes

If the service has 20 minutes of downtime in week 1:
  Budget remaining = 43.2 - 20 = 23.2 minutes
  Alert: budget is 46% consumed in first 25% of window
  Action: review and reduce deployment frequency,
          fix the most impactful reliability issues
```

---

### 💻 Code Example

**Example 1 - Prometheus: SLO recording rules**
```yaml
# GOOD: Define SLI recording rules for dashboard
# and alerting (Prometheus + Alertmanager)
groups:
- name: slo-recording-rules
  interval: 30s
  rules:
  # Availability SLI: good requests / total requests
  - record: job:request_success_rate:ratio_rate5m
    expr: >
      sum(rate(http_requests_total{
        status!~"5..",job="my-api"}[5m]))
      /
      sum(rate(http_requests_total{
        job="my-api"}[5m]))

  # Latency SLI: fraction of requests under 300ms
  - record: job:request_latency_sli:ratio_rate5m
    expr: >
      sum(rate(
        http_request_duration_seconds_bucket{
          le="0.3", job="my-api"}[5m]))
      /
      sum(rate(
        http_request_duration_seconds_count{
          job="my-api"}[5m]))
```

**Example 2 - Alertmanager: Error budget burn alert**
```yaml
# Alert when error budget burning 14.4x too fast
# This means 30-day budget will exhaust in ~50 hours
# Multi-window: fast burn detected quickly
groups:
- name: slo-alerts
  rules:
  - alert: HighErrorBudgetBurnRate
    expr: >
      job:request_success_rate:ratio_rate5m < 0.001
      and
      job:request_success_rate:ratio_rate1h < 0.001
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "SLO burn rate critical"
      description: >
        Error rate is {{ $value | humanizePercentage }}
        over the last hour. At this rate,
        the 30-day error budget will be exhausted
        in {{ 0.001 / $value * 730 | humanizeDuration }}.
```

**Example 3 - SLO reporting in Java application**
```java
// Instrument application to emit SLI-relevant metrics
// Use Micrometer (Spring Boot default metrics library)
@Component
public class SLOInstrumentation {
    private final MeterRegistry registry;

    @Around("@annotation(Tracked)")
    public Object trackRequest(ProceedingJoinPoint pjp)
        throws Throwable {
        Timer.Sample sample = Timer.start(registry);
        boolean success = false;
        try {
            Object result = pjp.proceed();
            success = true;
            return result;
        } catch (Exception e) {
            // Don't count client errors (4xx) against SLO
            // Only server errors (5xx) are SLO-relevant
            if (!(e instanceof ClientException)) {
                registry.counter(
                    "sli.error.count",
                    "service", "my-api"
                ).increment();
            }
            throw e;
        } finally {
            // Record latency (for latency SLO)
            sample.stop(Timer.builder("sli.request.duration")
                .tag("service", "my-api")
                .tag("success", String.valueOf(success))
                .register(registry));
        }
    }
}
```

---

### ⚖️ Comparison Table

| Term | Set By | Audience | Consequences if Missed |
|---|---|---|---|
| **SLI** | Engineering | Engineering | No direct consequence - it is a measurement |
| **SLO** | Engineering | Engineering, Product | Error budget alerts; engineering prioritization |
| **SLA** | Business/Legal | Customers | Financial penalties, service credits |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 100% availability is an achievable SLO | It is not achievable and not desirable. Even if achievable, the cost to get from 99.99% to 100% is exponentially higher than from 99% to 99.9%. Trying for 100% also makes SLO-based prioritization impossible (any failure is a violation). |
| SLA = SLO | Companies often set SLA looser than SLO. "We target 99.9% internally (SLO) and promise 99.5% externally (SLA)." The gap is the safety margin. Setting SLA = SLO means no buffer for operational variance. |
| Error budgets only protect against downtime | Error budgets track any SLO miss: latency degradation, elevated error rate, data staleness. Any metric in the SLI set that degrades contributes to budget burn. |

---

### 🚨 Failure Modes & Diagnosis

**Poorly Calibrated SLO (Too Easy)**

**Symptom:**
The SLO shows "100% compliance" for 12 consecutive
months. The team is proud. But customers are complaining
about slow performance and the team is not responding
urgently because "we're within SLO."

**Root Cause:**
The SLO was set based on current system performance,
not user needs. If users tolerate p99 < 2s but the
system regularly delivers p99 at 1.8s with occasional
spikes to 3s, and the SLO is set at p99 < 3s, the
SLO never fires - but users are unhappy at 1.8s anyway
for other reasons. The SLO is masking, not surfacing,
the problem.

**Diagnostic:**
```bash
# Compare current performance with SLO target
# If current p99 is consistently 50%+ below SLO target,
# the SLO is too loose
# Example: p99 = 1.5s, SLO = 3s → SLO too easy
# Ask: at what latency do users abandon the page?
# Set SLO based on that threshold, not current performance.

# Check user signals: product analytics
# Conversion rate vs latency correlation
# If conversions drop at > 2s, set SLO to p99 < 2s
# not p99 < 3s (which doesn't catch the user-impacting range)
```

**Fix:**
Calibrate SLO against user behavior signals (page
abandonment, conversion rate, support tickets). If
users clearly have degraded experience at latency
below the current SLO threshold, tighten the SLO.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Availability` - SLI/SLO/SLA are the measurement
  framework for availability and other reliability targets
- `Non-Functional Requirements` - SLOs formalize NFRs
  into measurable targets

**Builds On This (learn these next):**
- `Error Budget` - derived from SLO; the core mechanism
  for balancing reliability and feature velocity
- `MTTR / MTBF` - complementary reliability metrics
  used alongside SLIs in reliability engineering

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SLI           │ What you MEASURE: success rate,         │
│               │ latency, error rate, throughput         │
├───────────────┼─────────────────────────────────────────┤
│ SLO           │ Internal TARGET: SLI ≥ 99.9% over       │
│               │ 30 days                                 │
├───────────────┼─────────────────────────────────────────┤
│ SLA           │ External CONTRACT: with penalties       │
│               │ if SLOs are missed                      │
├───────────────┼─────────────────────────────────────────┤
│ ERROR BUDGET  │ (1 - SLO) × window = budget for outage  │
│               │ 99.9% SLO → 43.2 min/month budget       │
├───────────────┼─────────────────────────────────────────┤
│ KEY INSIGHT   │ SLO drives engineering. SLA drives      │
│               │ contracts. SLI drives both.             │
├───────────────┼─────────────────────────────────────────┤
│ GOOD SLI      │ User-focused, full request path, measure│
│               │ what users experience                   │
├───────────────┼─────────────────────────────────────────┤
│ BAD SLI       │ Server CPU, health check ping, infra    │
│               │ metrics users don't directly experience │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "SLI measures, SLO targets, SLA         │
│               │  contracts with consequences."          │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Error Budget → MTTR/MTBF → RTO/RPO      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. SLI = measure, SLO = target, SLA = contract.
2. SLO is tighter than SLA - the gap is your safety margin.
3. Good SLIs are user-focused: measure what users
   actually experience (success rate, latency), not
   infrastructure metrics (CPU).

**Interview one-liner:**
"SLI is the measurement (e.g., request success rate),
SLO is the internal target (e.g., success rate ≥
99.9% over 30 days), and SLA is the external contract
with financial consequences if missed. SLOs feed the
error budget - the allowed failure budget for the period.
Good SLIs measure user experience, not infrastructure
health."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
You cannot improve what you do not measure. The SLI/SLO
framework is an application of the general engineering
principle that objectives must be specific, measurable,
and time-bounded. "High availability" fails all three
tests. "99.9% success rate over a 30-day window" passes
all three. The specificity of the target is what
makes it actionable.

**Industry applications:**
- **Google Cloud SLAs:** Published at cloud.google.com/terms/sla.
  GCS provides 99.9% monthly uptime. If monthly uptime
  falls below 99.9%, customers receive 10% service
  credit. Below 99%, 25% credit. The SLA is backed
  by internal SLOs (typically 99.95%) to provide buffer.
- **AWS S3 SLA:** 99.9% monthly uptime. Missing the SLA
  by even 0.01% means service credits. This creates
  strong financial incentives to maintain the internal
  SLO at 99.95%+.

---

### 🎯 Interview Deep-Dive

**Q1: How would you choose SLIs for a real-time
chat application?**
*Why they ask:* Tests whether the candidate knows
how to pick user-relevant metrics.
*Strong answer includes:*
- Message delivery rate: % of messages that are
  delivered to recipients within 1 second (user notices
  if messages are delayed)
- Connection availability: % of users who can
  successfully establish a WebSocket connection
- Latency SLI: fraction of messages delivered in < 500ms
  (users perceive > 500ms as "slow" in real-time chat)
- NOT: server CPU, memory, or pod count - these are
  infrastructure metrics, not user experience metrics

**Q2: Your service's SLO is 99.9% availability.
After an incident, you calculate 45 minutes of
downtime this month. What do you do?**
*Why they ask:* Tests practical SLO/error budget reasoning.
*Strong answer includes:*
- 45 minutes vs 43.2 minute budget: SLO is technically
  missed with ~2 minutes overage
- This is a tight call - was it actually 45 minutes
  of user-impacting downtime, or did the monitoring
  definition over-count?
- Response: post-mortem to understand root cause;
  freeze high-risk changes for the rest of the window;
  determine if SLO was calibrated correctly or needs
  adjustment
- Consider: is the 99.9% SLO actually what users need?
  Or should it be 99.5% (more buffer) or 99.99% (higher bar)?

**Q3: Why would you set an SLA stricter than your SLO,
and what is the appropriate gap?**
*Why they ask:* Tests understanding of the SLO/SLA relationship.
*Strong answer includes:*
- SLA stricter than SLO means: the external promise
  is more lenient than the internal target, providing
  a safety margin
- Wait - this is actually backwards in the question.
  Restate: SLO is stricter than SLA. Internal target
  (SLO) is set higher (99.95%) than external promise
  (SLA: 99.9%). This gives margin.
- Appropriate gap: at least 1-2 nines of headroom.
  If your SLO is 99.95%, your SLA should be 99.9%
  or looser. If you set SLA = SLO = 99.95%, you will
  routinely miss the SLA during incidents that burn
  the error budget but stay within the SLO window.
- The gap provides: time to respond before SLA
  violation; capacity for rare incidents; negotiating
  room with customers.
