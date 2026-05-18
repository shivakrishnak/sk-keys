---
id: DST-015
title: Availability
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-011, DST-014
used_by: DST-016, DST-028
related: DST-011, DST-014, DST-016, DST-015
tags:
  - distributed
  - reliability
  - foundational
  - sla
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/distributed-systems/availability/
---

⚡ TL;DR - Availability is the fraction of time a system
correctly responds to requests; it is the measurable output
of fault tolerance design, expressed as a percentage (99.9%,
99.99%) that determines allowable downtime per year and
drives infrastructure redundancy decisions.

---

### 📋 Entry Metadata

| #015 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Fault Tolerance, Consistency | |
| **Used by:** | CAP Theorem, Eventual Consistency / BASE | |
| **Related:** | Fault Tolerance, Consistency, CAP Theorem | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A payment service has no availability target. The engineering
team fixes bugs and deploys whenever convenient. Deployments
take the service offline for 20 minutes. Bugs cause service
restarts. The team measures "are requests succeeding?" in
ad-hoc dashboards but has no SLA. Business discovers in
a quarterly review that the payment service was down 72 hours
last quarter. Lost revenue is estimated at $2M. No one on
the team knew this was happening.

**THE MEASUREMENT PROBLEM:**
Without a precise availability definition and measurement,
reliability is invisible. Teams cannot make engineering
trade-offs (redundancy cost vs downtime cost) without knowing
what availability they are currently achieving and what
they are targeting. Availability makes reliability concrete
and quantifiable.

---

### 📘 Textbook Definition

**Availability** is the probability that a system is
operational and correctly serving requests at any given
moment. It is formally defined as:

$$\text{Availability} = \frac{\text{MTTF}}{\text{MTTF} + \text{MTTR}}$$

where **MTTF** (Mean Time To Failure) is the average time
between failures and **MTTR** (Mean Time To Recovery) is
the average time to restore service after a failure.
In practice, availability is expressed as a percentage of
uptime in a given period (typically one year or one month).
The "nines" nomenclature - 99.9% ("three nines"), 99.99%
("four nines"), 99.999% ("five nines") - is standard in
SLAs and SLOs. Availability in distributed systems is
a design property: it is achieved by replication, automatic
failover, and minimizing MTTR through fast failure detection.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Availability measures what fraction of the time your system
is up and serving requests correctly - and quantifies how
much downtime is acceptable per year.

**One analogy:**
> An airline with 99.9% on-time performance sounds impressive
> until you realize that "0.1% late" across 1,000 daily
> flights means 1 late flight per day. Availability nines
> work similarly: the gaps between 9s look small but
> represent large absolute differences in downtime.

**One insight:**
The "nines" table is the essential reference:
```
99%    = 3.65 days downtime per year
99.9%  = 8.7  hours downtime per year
99.99% = 52   minutes downtime per year
99.999%=  5   minutes downtime per year
```
Each additional nine reduces acceptable downtime by 10x.
Moving from 99.9% to 99.99% is a 10x improvement, not a
0.009% improvement. The engineering effort required grows
sharply with each additional nine.

---

### 🔩 First Principles Explanation

**THE MTTF / MTTR EQUATION:**
Availability is driven by two variables:
- **MTTF** (Mean Time To Failure): how long between failures.
  Improved by: better software quality, simpler architecture,
  fewer dependencies.
- **MTTR** (Mean Time To Recovery): how long to recover from
  a failure. Improved by: automatic failover, health checks,
  on-call runbooks, chaos engineering.

```
Example calculation:
  A database fails once per month (MTTF = 730 hours)
  Recovery takes 30 minutes (MTTR = 0.5 hours)

  Availability = 730 / (730 + 0.5) = 99.93%
  Annual downtime = 0.07% × 8760 hours = 6.1 hours

  To achieve 99.99%:
    Need MTTF/(MTTF+MTTR) ≥ 0.9999
    With MTTR=0.5h: need MTTF ≥ 4,999.5h ≈ 208 days
    OR with MTTF=730h: need MTTR ≤ 0.073h ≈ 4.4 minutes

  Interpretation: either fail much less often,
  or recover much faster. Automatic failover in <1 minute
  achieves 4.4 minute MTTR requirement.
```

**THE DEPENDENCY MULTIPLICATION PROBLEM:**

```
If each service has availability A:
System with N services in series: A^N

N=1:  0.999^1  = 99.9%
N=3:  0.999^3  = 99.7%
N=10: 0.999^10 = 99.0%
N=20: 0.999^20 = 98.0%
```

This is why microservices architectures require each service
to have significantly higher individual availability to
maintain system-level availability. A 20-service system
with each service at 99.9% achieves only 98% system
availability - over 175 hours of downtime per year.

**SERIES vs PARALLEL AVAILABILITY:**
```
IN SERIES (all must work):
  Availability = A1 × A2 × A3 × ...
  System is as unreliable as the weakest link

IN PARALLEL (any can work - redundancy):
  Availability = 1 - (1-A1)(1-A2)(1-A3)...
  System is far more reliable than any single component

Example: Two 99% components
  In series:   0.99 × 0.99 = 98.01% availability
  In parallel: 1 - (0.01 × 0.01) = 99.99% availability

This is WHY redundancy (parallel architecture) achieves
dramatically better availability than improving individual
components (series architecture).
```

---

### 🧠 Mental Model / Analogy

> The "nines" are like the number of zeros in a quality
> standard: "one defect per 100 parts" (99%) vs "one
> defect per 10,000 parts" (99.99%). Each additional zero
> represents a 10x improvement in the underlying defect
> rate. The engineering required to go from 1 defect per
> 100 to 1 per 1,000 is very different from 1 per 1,000
> to 1 per 10,000. The marginal cost increases dramatically
> with each additional nine.

**In practice:** Going from 99% to 99.9% may require adding
a standby replica. Going from 99.9% to 99.99% requires
automatic failover in under 5 minutes. Going from 99.99%
to 99.999% requires multi-region active-active architecture
with no manual intervention ever. The engineering investment
jumps by an order of magnitude.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Availability measures how often your service is working.
99.9% means it is working 99.9% of the time and broken
0.1% of the time. Translated: about 8.7 hours broken per
year. The goal is to maximize the working percentage.

**Level 2 - How to use it (junior developer):**
Define SLOs (Service Level Objectives): "This service must
be 99.9% available, measured as the fraction of HTTP requests
in a 30-day window that return a 2xx or 3xx response." Track
this metric on a dashboard. Set up alerts when availability
drops below threshold. Budget the "error budget" (allowed
downtime) across deployments and incidents.

**Level 3 - How it works (mid-level engineer):**
Availability is measured by a synthetic monitor sending
periodic test requests (every 30 seconds) and tracking
success/failure. Separately, real-user traffic success rate
is measured. Availability is the ratio of successful requests
to total requests in the window. An "outage" is a period
where availability drops below the SLO threshold.

**Level 4 - Why it was designed this way (senior/staff):**
The MTTF/MTTR formulation is useful because it separates
two independent engineering concerns: how to prevent
failures (MTTF improvement) vs how to recover from them
(MTTR improvement). At very high availability targets
(99.999%), preventing all failures becomes physically
impossible. The only viable path is reducing MTTR to
seconds through automatic, pre-tested failover procedures.
This is why chaos engineering focuses on MTTR: the system
must know how to recover, not just how to avoid failure.

**Level 5 - Mastery (distinguished engineer):**
Availability SLOs interact with deployment frequency:
every deployment is a potential outage event. A team
deploying 10 times per day at 5 minutes per deployment
consumes 50 minutes of MTTR budget per day - exceeding
the 52-minute annual budget for 99.99% immediately.
This drives zero-downtime deployment techniques (blue-green,
canary, rolling) which are not just operational niceties
but mathematical requirements for high availability
at high deployment frequency. The availability math
forces architectural decisions in a direct, measurable way.

---

### ⚙️ Why It Holds True

**THE FALLACY OF PERFECT COMPONENTS:**
No hardware or software component can achieve 100% uptime.
Google's Bigtable paper reported tablet server availability
of 99.6% per server. Google Cloud reports 99.99% SLA for
their services. The gap between component availability
(99.6%) and service SLA (99.99%) is bridged by redundancy
and automatic recovery. The mathematical reality:
at scale, component failures are not exceptional events -
they are scheduled, normal operating conditions.

**THE ERROR BUDGET CONCEPT:**
Google's SRE book (2016) introduced the error budget: the
allowable unreliability in a service SLO. If the SLO is
99.9%, the error budget is 0.1% = 8.7 hours per year.
This budget can be "spent" on deployments (risk of outage),
experiments, and incidents. When the budget is exhausted,
no new deployments are allowed until the next period.
This makes reliability a shared responsibility between
development (features that consume budget) and operations
(incidents that consume budget) with a clear, quantitative
mechanism.

---

### 🗺️ System Design Implications

**AVAILABILITY REQUIREMENTS DRIVE ARCHITECTURE:**

```
┌──────────────────────────────────────────────────────┐
│ Target     │ Architecture Required                   │
├────────────┼────────────────────────────────────────┤
│ 99%        │ Single node, manual recovery OK         │
│ 99.9%      │ Hot standby, auto-failover within 1 min │
│ 99.99%     │ Multi-AZ, failover within 1 minute,     │
│            │ zero-downtime deployments               │
│ 99.999%    │ Multi-region active-active, automated   │
│            │ recovery, no manual intervention ever   │
└──────────────────────────────────────────────────────┘
```

**ELIMINATING SINGLE POINTS OF FAILURE:**
Every component in the dependency chain contributes to
system availability. Identify every SPOF and calculate
its impact on system MTTF. Prioritize eliminating the SPOFs
with the highest failure rates.

---

### 💻 Code Example

**Availability Measurement (Production)**

```python
# Availability SLO tracking using Prometheus + Python
from prometheus_client import Counter, Gauge
import time

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

AVAILABILITY = Gauge(
    'service_availability_ratio',
    'Availability in the last 30 days'
)

def record_request(method: str, endpoint: str, status: int):
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=str(status)
    ).inc()

# PromQL to calculate availability in Grafana:
# 
# sum(rate(http_requests_total{status!~"5.."}[30d]))
# /
# sum(rate(http_requests_total[30d]))
#
# This calculates: (non-5xx requests / total requests)
# over the past 30 days = availability ratio
```

**Calculating Error Budget Consumption**

```python
# Error budget calculator
def calculate_error_budget(
    slo_percent: float,        # e.g., 99.9
    total_requests: int,       # in the period
    error_requests: int        # 5xx responses
) -> dict:
    availability = 1 - (error_requests / total_requests)
    error_rate = error_requests / total_requests
    budget_rate = 1 - (slo_percent / 100)
    budget_consumed = error_rate / budget_rate * 100

    return {
        "availability": f"{availability*100:.4f}%",
        "error_rate": f"{error_rate*100:.4f}%",
        "slo": f"{slo_percent}%",
        "error_budget_consumed": f"{budget_consumed:.1f}%",
        "status": "OK" if budget_consumed < 100 else "EXCEEDED"
    }

# Example:
result = calculate_error_budget(
    slo_percent=99.9,
    total_requests=10_000_000,
    error_requests=5_000
)
# error_rate = 0.05%, budget = 0.1%, consumed = 50% of budget
```

---

### ⚖️ Comparison Table

| Level | Uptime % | Annual Downtime | Requirements |
|---|---|---|---|
| **99%** | 99% | ~3.65 days | Basic monitoring, manual recovery |
| **99.9%** | 99.9% | ~8.7 hours | Hot standby, automated alerts |
| **99.95%** | 99.95% | ~4.4 hours | Multi-AZ deployment |
| **99.99%** | 99.99% | ~52 minutes | Auto-failover <1 min, zero-downtime deploys |
| **99.999%** | 99.999% | ~5 minutes | Multi-region active-active, no manual ops |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "99% availability is pretty good" | 99% = 87.6 hours downtime per year = over 3.5 days. This is unacceptable for any customer-facing production service. |
| "Availability only counts full outages" | Partial availability matters too: if 10% of requests fail, availability is 90% even if the service is "up." An SLO measures request success rate, not just "is the process running." |
| "High availability = high cost" | High availability costs more, but the most impactful improvement (from 99% to 99.9%) is relatively cheap: add a hot standby. The expensive improvements are the final nines. |
| "Cloud providers guarantee my availability" | Cloud providers SLAs (99.9% or 99.99% for most services) cover the infrastructure. Your application availability is your responsibility - you must architect for the cloud provider's allowed downtime. |

---

### 🚨 Failure Modes & Diagnosis

**Measuring Availability Incorrectly**

**Symptom:** Dashboard shows 99.99% availability but users
report frequent errors. Support tickets accumulate. Business
reports revenue impact. The measurement doesn't match
reality.

**Root Cause:** Availability is measured by process health
checks ("is the server responding to pings?") rather than
by actual request success rates ("are user requests
succeeding?"). A server can respond to pings while
returning 500 errors to all user requests.

**Fix:** Measure availability as:
```
(successful user requests) / (total user requests)
```
Not: "is the process running."

---

**Cascading SLO Violation from Dependencies**

**Symptom:** Service has 99.9% availability SLO. The service
itself never fails. But its upstream dependencies fail,
causing 99.5% availability. SLO is violated without the
service itself being faulty.

**Root Cause:** Availability SLOs do not account for
dependency availability. If the service depends on a
database with 99.95% availability, and the database is
the only failure mode, system availability is bounded by
the database's SLA.

**Diagnosis:**
```bash
# Trace which dependency caused failures:
# Check error type in request logs
grep '"status":5' access.log |
  grep -o '"error":"[^"]*"' | sort | uniq -c

# If errors are "connection timeout to db-host":
# The database is causing the SLO violation
```

**Fix:** Map all dependency SLAs. Calculate the maximum
system availability given dependencies. Either improve
dependency availability or add fallback behavior for
dependency failures.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Fault Tolerance` - The design property that enables
  high availability
- `Consistency` - The trade-off partner of availability
  in the CAP theorem

**Builds On This (learn these next):**
- `CAP Theorem` - Formalizes the consistency-availability
  trade-off under partitions
- `Eventual Consistency / BASE` - The consistency model
  chosen by AP systems to prioritize availability

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fraction of time system correctly respond│
│              │ to requests (expressed as a percentage)  │
├──────────────┼──────────────────────────────────────────┤
│ KEY FORMULA  │ A = MTTF / (MTTF + MTTR)                 │
├──────────────┼──────────────────────────────────────────┤
│ NINES TABLE  │ 99.9%  = 8.7h/yr  Three nines            │
│              │ 99.99% = 52m/yr   Four nines             │
│              │ 99.999%=  5m/yr   Five nines             │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Series: A = A1 × A2 (weakest link wins)  │
│              │ Parallel: A = 1-(1-A1)(1-A2) (redundancy)│
├──────────────┼──────────────────────────────────────────┤
│ MEASURE AS   │ (successful requests) / (total requests) │
│              │ NOT "is the process running"             │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ "We have never had a major outage"       │
│              │ - availability isn't measured until      │
│              │   a business impact is felt              │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Each nine costs 10x more to achieve;    │
│              │  measure what users actually experience."│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ CAP Theorem → SLO/SLA design →           │
│              │ Error Budget Management                  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The series/parallel availability math is universal. Any
system composed of sequential dependencies has availability
limited by its weakest component. Any system with parallel
(redundant) components has dramatically higher availability.
The pattern "reduce dependencies; add redundancy to critical
dependencies" applies in software, hardware, organizations,
and any complex system.

**The error budget concept** from Google SRE is now a
standard industry practice: convert an availability SLO
(99.9%) into a concrete allowable failure rate (0.1% of
requests), then treat that budget as a shared resource
between development (feature risk) and operations
(infrastructure risk). This creates a measurable, enforceable
reliability standard.

---

### 💡 The Surprising Truth

Amazon discovered in early AWS development that every 100ms
of additional latency reduced revenue by 1%. This drove the
decision to design AWS services for very high availability
(99.99%+). The interesting insight from this: availability
and latency are coupled. A slow response is often worse than
a fast failure - a request that times out after 30 seconds
is "up" by availability measurement but has destroyed more
user value than a 500 error in 100ms. Modern SLOs measure
both availability (success rate) and latency (percentile
distribution), because a system that is "available" but
slow may be more harmful than one that fails fast.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [CALCULATE] Given a service with 3 dependencies each
   at 99.9%, calculate the maximum system availability
   in series, and the minimum individual availability
   needed to achieve 99.9% system availability.
2. [DEFINE] Write an availability SLO for a payment service:
   specify what counts as a success, what counts as failure,
   the measurement window, and the alerting threshold.
3. [ANALYZE] A service has 99.95% availability but the
   SLO is 99.99%. Determine whether improving MTTF or
   MTTR is the more effective lever given the current
   metrics.
4. [DESIGN] A single-node database achieves 99.9%
   availability. Design an architecture that achieves
   99.99% by reducing MTTR without changing the failure
   rate of individual components.
5. [JUSTIFY] Explain to an executive why moving from
   99.99% to 99.999% availability requires multi-region
   active-active architecture and costs 5x more than the
   current setup.
