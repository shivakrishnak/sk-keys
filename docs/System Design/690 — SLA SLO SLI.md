---
layout: default
title: "SLA / SLO / SLI"
parent: "System Design"
nav_order: 690
permalink: /system-design/sla-slo-sli/
number: "690"
category: System Design
difficulty: â˜…â˜…â˜†
depends_on: "Observability, Error Budget"
used_by: "Error Budget, MTTR / MTBF"
tags: #intermediate, #reliability, #observability, #architecture, #foundational
---

# 690 â€” SLA / SLO / SLI

`#intermediate` `#reliability` `#observability` `#architecture` `#foundational`

âš¡ TL;DR â€” **SLI** measures reliability (what you observe), **SLO** is your internal target (what you commit to internally), **SLA** is a contractual promise (what you commit to customers with financial consequences for breach).

| #690            | Category: System Design     | Difficulty: â˜…â˜…â˜† |
| :-------------- | :-------------------------- | :-------------- |
| **Depends on:** | Observability, Error Budget |                 |
| **Used by:**    | Error Budget, MTTR / MTBF   |                 |

---

### ðŸ“˜ Textbook Definition

**Service Level Indicator (SLI)** is a quantitative measure of a service's behaviour from the user's perspective â€” a carefully defined metric that captures service performance. Common SLIs: availability (fraction of successful requests), latency (fraction of requests below a threshold), throughput (requests per second), error rate, durability. **Service Level Objective (SLO)** is an internal target value or range for an SLI, expressed as a percentage over a time window: "99.9% of requests should succeed in a rolling 28-day window." SLOs are internal commitments â€” engineering targets used to drive reliability work. **Service Level Agreement (SLA)** is a contractual commitment made to customers that specifies consequences (financial penalties, credits, remediation) if the service fails to meet defined targets. SLAs are typically set looser than SLOs â€” SLO breaches alert engineering before SLA breaches affect customers. Together, these three concepts form the foundation of SRE (Site Reliability Engineering).

---

### ðŸŸ¢ Simple Definition (Easy)

- **SLI**: what you actually measure â€” "99.95% of requests succeeded this month"
- **SLO**: your internal goal â€” "we want 99.9% success rate"
- **SLA**: your customer contract â€” "we promise 99.5%, we'll pay a credit if we miss it"

SLI â‰¥ SLO > SLA (measurements exceed objectives; objectives exceed contracts)

---

### ðŸ”µ Simple Definition (Elaborated)

Think of it as three concentric circles of commitment. The outermost circle is the SLI â€” raw measurement, no judgment. The middle circle is the SLO â€” your internal engineering target (ambitious but achievable). The innermost circle is the SLA â€” the contractual floor you promise customers (conservative, well below your SLO). Engineering tries to maintain SLO. If SLO is breached, it's a reliability incident. If SLA is breached, it's a legal/financial problem. The gap between SLO and SLA is the buffer â€” early warning that prevents SLA breaches.

---

### ðŸ”© First Principles Explanation

**Why this three-layer model exists:**

```
THE RELIABILITY MEASUREMENT PROBLEM:
  How do you know if your service is "reliable"?
  "The service is up" â†’ vague, binary, not useful.
  "Users are happy" â†’ unmeasurable, subjective.

  NEED: precise, measurable, actionable definitions.

SERVICE LEVEL INDICATOR (SLI) â€” the measurement:

  Definition: SLI = (good events) / (total events)

  AVAILABILITY SLI:
    SLI = (successful HTTP responses with status 2xx or 3xx)
          / (total HTTP requests)
    Measured over: rolling 28-day window
    Example value: 0.99951 (99.951%)

  LATENCY SLI (threshold-based):
    SLI = (requests completed in < 200ms) / (total requests)
    Example value: 0.9981 (99.81% of requests complete in < 200ms)

    NOTE: Use percentile thresholds (P99, P95), not averages.
    Average latency hides tail latency: 1% of users waiting 10 seconds
    while average is 50ms â€” average says "great", P99 says "broken".

  ERROR RATE SLI:
    SLI = 1 - (5xx errors / total requests)
    = 1 - error_rate

  DURABILITY SLI (for storage systems):
    SLI = (objects retrievable on demand) / (objects stored)

SERVICE LEVEL OBJECTIVE (SLO) â€” the internal target:

  SLO = target threshold for an SLI.
  Example: "SLI_availability >= 99.9% over rolling 28 days"

  SLO MUST BE:
  - Specific: which SLI, what threshold, what time window
  - Measurable: automated monitoring and alerting
  - Achievable: based on architecture capability (not wishful)
  - Time-bounded: rolling window (28 days) vs. calendar period

  SETTING TIGHT vs. LOOSE SLOs:

    TOO TIGHT (99.9999% = 31 seconds downtime/year):
      Nearly impossible to achieve consistently.
      Any incident â†’ SLO breach â†’ engineering distracted by alerts.
      Leads to: alert fatigue, engineering burnout, risk aversion.

    TOO LOOSE (90% = 36 days downtime/year):
      Users are unhappy before SLO breach.
      SLO breach is meaningless signal.

    CORRECT: Set SLO just above where users would notice/complain.
      Survey users: what's the minimum reliability you'd accept?
      Analysis: what does current system actually achieve (SLI history)?
      Set SLO: slightly ambitious vs. current SLI (drives improvement).

ERROR BUDGET: SLO to actionable budget:

  Error Budget = 1 - SLO
  SLO = 99.9% â†’ Error Budget = 0.1% = 43.2 minutes/month allowed downtime

  Error Budget Consumed = 1 - current SLI
  If SLI = 99.85% â†’ consumed 0.15% (exceeded 0.1% budget â†’ SLO breach)

  Error Budget drives decisions:
  - Budget remaining: can deploy new features (accepting risk of failures)
  - Budget exhausted: freeze deployments, focus on reliability only

SERVICE LEVEL AGREEMENT (SLA) â€” the contract:

  SLA is ALWAYS set looser than SLO.
  Example:
    SLO: 99.9% (internal target)
    SLA: 99.5% (customer commitment)
    Buffer: 0.4% (safety margin)

  Why looser?
  - SLO breach: engineering alert â†’ investigation starts before customers notice
  - SLA breach: customers already impacted â†’ legal/financial consequences

  SLA PENALTIES (typical):
    99.5% to 99.0%: 10% service credit
    99.0% to 95.0%: 25% service credit
    Below 95.0%: 50% service credit or right to terminate

  AWS S3 SLA: 99.9% monthly uptime commitment.
  (Note: S3 SLO is much higher â€” designed for 99.999999999% durability)

  PRACTICAL NOTE: Many "SLAs" in informal conversations are actually SLOs.
  When a team says "our SLA is 99.9%", they often mean their internal target.
  True SLAs: signed contracts with customers, specific financial remedies.
```

---

### â“ Why Does This Exist (Why Before What)

WITHOUT SLI/SLO/SLA framework:

- Reliability debates: "Is this acceptable?" â€” subjective, politically charged
- Engineering prioritisation: impossible to justify reliability work vs. features
- Customer trust: no measurable promises â†’ customers cannot evaluate fit for purpose

WITH SLI/SLO/SLA framework:
â†’ Objective measurement: "SLI is 99.85%, SLO is 99.9% â†’ error budget exhausted"
â†’ Decision framework: error budget remaining â†’ ship features; exhausted â†’ reliability sprint
â†’ Customer accountability: contractual commitments with specific consequences

---

### ðŸ§  Mental Model / Analogy

> An airline's on-time performance system. The SLI is the actual measurement: "87.3% of flights this month departed within 15 minutes of schedule." The SLO is the airline's internal target: "we want to hit 90%." The SLA is the contract: "we guarantee 85% on-time performance in our service agreement with corporate clients, or we provide travel credits." The airline tries to beat its SLO (90%) so it never gets close to breaching its SLA (85%).

"Flight on-time percentage" = SLI (the measured metric)
"Internal 90% target" = SLO (engineering/ops target)
"Contractual 85% guarantee" = SLA (customer-facing promise)
"Travel credits on breach" = SLA penalty / service credit

---

### âš™ï¸ How It Works (Mechanism)

**Prometheus + Grafana SLO dashboard:**

{%- raw -%}
```yaml
# prometheus rule: SLI calculation and SLO alerting

groups:
  - name: slo_rules
    interval: 60s
    rules:
      # SLI: ratio of successful requests (2xx+3xx vs. total)
      - record: job:sli_availability:ratio_rate5m
        expr: |
          sum(rate(http_requests_total{status=~"2..|3.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))

      # SLI: latency - fraction of requests completing in < 200ms
      - record: job:sli_latency_p200ms:ratio_rate5m
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.2"}[5m]))
          /
          sum(rate(http_request_duration_seconds_count[5m]))

      # Alert: SLO breach imminent (burn rate alert)
      - alert: SLOBurnRateHigh
        expr: |
          job:sli_availability:ratio_rate5m < 0.999
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "SLO breach: availability SLI below 99.9%"
          description: "Current SLI: {{ $value | humanizePercentage }}"

      # Error budget: remaining budget (rolling 28-day window)
      - record: job:error_budget_remaining:ratio
        expr: |
          1 - (1 - avg_over_time(job:sli_availability:ratio_rate5m[28d]))
          / (1 - 0.999)
      # = 1.0: full budget remaining
      # = 0.5: half budget consumed
      # < 0.0: budget exceeded (SLO breached)
```
{%- endraw -%}

---

### ðŸ”„ How It Connects (Mini-Map)

```
Observability
(metrics, traces, logs â€” data collection)
        â”‚
        â–¼ (define what to measure and target)
SLI / SLO / SLA â—„â”€â”€â”€â”€ (you are here)
(measure â†’ target â†’ contract)
        â”‚
        â”œâ”€â”€ Error Budget (SLO â†’ budget â†’ deployment decision gate)
        â”œâ”€â”€ MTTR / MTBF (reliability metrics that feed SLI calculations)
        â””â”€â”€ Alerting (SLO burn rate â†’ PagerDuty â†’ on-call response)
```

---

### ðŸ’» Code Example

**SLO calculation and error budget tracking in Python:**

```python
class SLOTracker:
    def __init__(self, slo_target: float, window_days: int = 28):
        """
        slo_target: float like 0.999 for 99.9%
        window_days: rolling window for SLO calculation
        """
        self.slo_target = slo_target
        self.window_days = window_days

    def calculate_sli(self, good_requests: int, total_requests: int) -> float:
        """SLI = good_requests / total_requests"""
        if total_requests == 0:
            return 1.0  # no traffic = 100% success rate
        return good_requests / total_requests

    def error_budget_minutes(self) -> float:
        """Total error budget in minutes for the window"""
        total_minutes = self.window_days * 24 * 60
        return total_minutes * (1 - self.slo_target)

    def error_budget_consumed(self, current_sli: float) -> dict:
        """How much error budget has been consumed?"""
        budget_total = self.error_budget_minutes()
        window_minutes = self.window_days * 24 * 60
        minutes_failed = (1 - current_sli) * window_minutes
        budget_remaining = budget_total - minutes_failed

        return {
            "slo_target": f"{self.slo_target * 100:.3f}%",
            "current_sli": f"{current_sli * 100:.3f}%",
            "slo_breach": current_sli < self.slo_target,
            "budget_total_minutes": round(budget_total, 1),
            "budget_consumed_minutes": round(minutes_failed, 1),
            "budget_remaining_minutes": round(budget_remaining, 1),
            "budget_remaining_pct": round(budget_remaining / budget_total * 100, 1)
        }

# Usage:
tracker = SLOTracker(slo_target=0.999)  # 99.9% SLO
result = tracker.error_budget_consumed(current_sli=0.9991)
# {
#   "slo_target": "99.900%",
#   "current_sli": "99.910%",
#   "slo_breach": False,
#   "budget_total_minutes": 40.3,
#   "budget_consumed_minutes": 36.3,
#   "budget_remaining_minutes": 4.0,
#   "budget_remaining_pct": 9.9  # 90% of budget consumed â€” warning!
# }
```

---

### âš ï¸ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 100% SLO is the goal                                       | 100% is not achievable and attempting it is counterproductive: it means no deployments (risk of downtime), extreme conservatism, and eventual user disappointment anyway. Honest, achievable SLOs (99.9%, 99.5%) are better than dishonest 100% claims |
| SLA and SLO are the same thing                             | SLO is an internal engineering target with no contractual commitment. SLA is a legal contract with financial consequences. SLA is always set looser than SLO â€” the gap is your safety buffer to prevent SLA breaches                                   |
| Measuring availability as uptime/downtime is the right SLI | Binary uptime/downtime misses partial degradation. A server returning 500 errors 30% of the time is "up" by binary measure but failing users. Request success rate SLI captures this. Modern SRE: measure from the user's perspective                  |
| SLOs should be set as high as possible to show ambition    | SLOs should be calibrated to what users actually need. Over-ambitious SLOs breach constantly â†’ alert fatigue, engineering burnout. Calibrated SLOs breach rarely but meaningfully â†’ each breach is a real signal                                       |

---

### ðŸ”¥ Pitfalls in Production

**Measuring SLI from the wrong vantage point:**

```
PROBLEM: measuring SLI from inside your service (server-side metrics)

  Server-side:
    http_requests_total{status="200"}: 9,990,000
    http_requests_total{status="5xx"}: 10,000
    Calculated SLI: 99.9% â€” looks great!

  Client-side reality (Synthetic monitoring from outside):
    30% of requests: timing out before server responds (TCP connection timeout)
    These timeouts: never reach server â†’ never counted in server-side metrics
    Real user SLI: 70% (30% of requests failing)

  Root cause: load balancer connectivity issue upstream of server metrics.

  SERVER-SIDE METRICS miss:
  - DNS resolution failures
  - Network-level drops before reaching server
  - Load balancer timeouts
  - CDN failures

FIX: Multi-layer SLI measurement

  1. SYNTHETIC MONITORING (Blackbox SLI):
     External probes (Datadog Synthetics, AWS CloudWatch Synthetics)
     running from multiple regions every 60 seconds.
     Measures the actual user-facing URL end-to-end.
     This is the "true" SLI from user perspective.

  2. CLIENT-SIDE RUM (Real User Monitoring):
     JavaScript snippet: window.performance.getEntriesByType("navigation")
     Reports actual page load times per real user session.
     Most representative signal of user experience.

  3. SERVER-SIDE METRICS: secondary signal for root cause analysis
     Good for diagnosing WHERE the problem is (which endpoint, which service)
     NOT for calculating the primary user-facing SLI

  Best practice:
    Primary SLI source = Synthetic monitoring or client RUM
    Debugging tool = server-side metrics + distributed traces
```

---

### ðŸ”— Related Keywords

- `Error Budget` â€” derived from SLO: `error_budget = 1 - SLO`, drives deployment decisions
- `Observability` â€” provides the metrics, traces, and logs that SLIs are calculated from
- `MTTR / MTBF` â€” operational metrics that feed into availability SLI calculations
- `Alerting / On-call` â€” SLO burn rate alerts trigger on-call response
- `Capacity Planning` â€” SLO targets inform required capacity headroom

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ SLI = measure | SLO = internal target     â”‚
â”‚              â”‚ SLA = customer contract (SLO buffer > SLA)â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Defining reliability targets; error budgetâ”‚
â”‚              â”‚ decisions; customer-facing commitments    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Setting SLA = SLO (no buffer â†’ SLA breach â”‚
â”‚              â”‚ on first incident); measuring from inside â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Measure what users feel (SLI), target    â”‚
â”‚              â”‚  what you can achieve (SLO), promise what â”‚
â”‚              â”‚  you can guarantee (SLA)."                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Error Budget â†’ Burn Rate Alerts           â”‚
â”‚              â”‚ â†’ MTTR / MTBF                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** You are setting SLOs for a new payment processing API. The engineering team proposes: availability SLO 99.99%, latency SLO P99 < 100ms. The sales team has already committed to customers: "enterprise-grade, five nines availability." Identify three specific problems with the proposed SLOs and the sales promise. What process would you follow to set correct, calibrated SLOs, and what would you do about the already-made sales promise?

**Q2.** A company's SLO is 99.9% availability over a rolling 28-day window. In the past 28 days, the following incidents occurred: Monday (Day 3): 12-minute outage; Wednesday (Day 10): 8-minute partial degradation (50% of requests failing); Friday (Day 22): 5-minute outage. Calculate: (a) total error budget in minutes for the window, (b) minutes consumed by each incident (note: partial degradation consumes partial budget), (c) remaining budget, and (d) whether the SLO was breached. Show your working.
