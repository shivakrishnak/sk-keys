---
id: OBS-038
title: Capacity Planning with Metrics
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-004, OBS-006, OBS-030
used_by: OBS-039, OBS-041, OBS-044
related: OBS-037, OBS-046, OBS-048
tags:
  - observability
  - reliability
  - devops
  - sre
  - advanced
  - production
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /obs/capacity-planning-with-metrics/
---

# OBS-038 - Capacity Planning with Metrics

⚡ TL;DR - Capacity planning with metrics is the discipline
of using historical resource utilization trends to predict
when a system will exhaust capacity - before it does -
and provisioning ahead of the saturation point, not after
the outage that reveals it.

| #038 | Category: Observability & SRE | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Prometheus - Metrics Collection, Grafana - Dashboards, USE Method | |
| **Used by:** | Observability at Scale, Observability Platform Architecture, Platform Observability Engineering | |
| **Related:** | Toil Reduction Strategy, Time-Series Database Design, Formal SLO Theory | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A payment service runs fine for 8 months. No one tracks
CPU or memory trends. One Tuesday, the service starts
throwing OutOfMemoryErrors at peak load. Engineers scramble
to add more pods. Kubernetes takes 3 minutes to schedule
new pods. The service is degraded for 8 minutes.
Investigation afterward shows memory usage has been growing
linearly by 2MB/hour for the past 3 months due to a slow
memory leak - the trend was visible in metrics, but no one
looked. If anyone had looked at the trend 2 weeks ago,
they would have had ample time to investigate and fix
the leak before it caused an incident.

**THE BREAKING POINT:**
Point-in-time monitoring tells you the current state.
It does not tell you whether the current state is
trending toward a cliff. Without trend analysis, capacity
exhaustion is discovered only at the moment of failure -
the worst possible time to respond.

**THE INVENTION MOMENT:**
This is why capacity planning with metrics exists: it
transforms metrics from a reactive diagnostic tool
("what is broken right now?") into a proactive planning
tool ("when will we hit capacity and what do we do before
that?"). The key technique is time-series forecasting -
extrapolating historical trends to predict future values
and the time to exhaustion.

**EVOLUTION:**
Early capacity planning was annual headcount and hardware
procurement based on business projections - engineering
guesses rather than data. The cloud era introduced elastic
capacity but did not eliminate the planning problem -
cost optimization and auto-scaling limits require the same
trend analysis. Modern capacity planning combines
short-term trend forecasting (Prometheus predict_linear),
seasonal decomposition (traffic patterns repeat weekly
and annually), and headroom modeling (maintain N%
utilization below 100% to absorb spike loads).

---

### 📘 Textbook Definition

**Capacity planning with metrics** is the practice of
collecting resource utilization time-series data
(CPU, memory, disk, network, queue depth, connection pool),
applying trend analysis and forecasting to project future
utilization, and provisioning resources or triggering
engineering interventions before utilization reaches
the saturation point that causes user-visible degradation.
Modern capacity planning uses: `predict_linear()` for
short-term linear extrapolation, seasonal decomposition
for periodic traffic patterns, and headroom policies
(maintain utilization below a safe threshold, typically
70-80%) to absorb unplanned spikes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Capacity planning with metrics means looking at where
your resource trends are heading, not just where they
are now, so you add capacity before you run out.

**One analogy:**
> Capacity planning is like a car fuel gauge combined
> with a trip computer. The fuel gauge shows current
> level (point-in-time monitoring). The trip computer
> adds "estimated range: 47 miles, destination: 80
> miles away" - that is the forecast. You don't wait
> until the fuel light comes on (the incident) to notice
> you need to fill up. You plan a stop before you run
> out, based on the trend (consumption rate + distance
> remaining).

**One insight:**
The critical insight is that capacity planning is not
about predicting traffic accurately - it is about
maintaining enough headroom that inaccurate predictions
do not cause incidents. No one can perfectly forecast
traffic. The correct model is: maintain enough headroom
(30% free buffer) that even a 2x unexpected spike in
traffic does not push you to saturation. The headroom
IS the safety margin for forecast error.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every resource has a saturation point where performance
   degrades non-linearly (CPU at 90% produces much worse
   latency than CPU at 70%)
2. Time-series resource data contains trend information
   that point-in-time alerts cannot surface
3. Provisioning takes time (minutes for pod scaling, hours
   for database scaling, days/weeks for hardware procurement)
   - the lead time determines how far in advance you must
   plan
4. Traffic is not uniform - it has daily, weekly, and
   seasonal patterns that must be modeled separately from
   the baseline trend

**DERIVED DESIGN:**
These invariants drive the capacity planning process:
- **Measure**: collect utilization time-series for all resources
- **Trend**: apply linear or non-linear regression to find
  the growth rate
- **Forecast**: project when utilization will reach the
  safety threshold (e.g., 80% of max capacity)
- **Lead time**: compare forecast horizon to provisioning
  lead time - trigger provisioning when time-to-threshold
  is less than lead time
- **Headroom policy**: define safe utilization ceiling
  (80% of max) and maintain utilization below it

**THE TRADE-OFFS:**
**Gain:** Proactive capacity actions before incidents; cost
optimization from right-sizing rather than panic-over-provisioning;
predictable reliability against traffic growth.
**Cost:** Requires reliable metrics collection and retention;
requires engineering investment in forecast models; over-
provisioning has a cost; under-provisioning despite planning
reveals model error.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any finite resource will be exhausted by
sufficient demand; predicting when requires historical data
and a growth model.
**Accidental:** Building custom forecast models in SQL
rather than using Prometheus `predict_linear()`, maintaining
capacity spreadsheets manually rather than automated alerts.

---

### 🧪 Thought Experiment

**SETUP:**
Your Postgres database disk is currently at 60% capacity.
Historical data shows disk grows at 500MB/day. The disk
is 1TB total. Provisioning a larger disk requires 48 hours
of planning, approval, and migration time.

**CALCULATION:**
Current free space: 400GB = 409,600MB
Growth rate: 500MB/day
Time to 80% threshold (safe ceiling):
  Target: 800GB used = 409,600MB - 204,800MB free
  204,800MB / 500MB/day = 409 days at current growth rate
But growth rate is accelerating with new features: 10%
increase per month in data volume.

With exponential growth, the calculation changes. In
3 months at 10% monthly compound growth:
Month 1: 550 MB/day, Month 2: 605 MB/day, Month 3: 666 MB/day
More accurate estimate: disk hits 80% in approximately
300 days, not 409 days.

**WHAT HAPPENS WITHOUT PLANNING:**
No alert. No trend visibility. Engineers notice disk at 95%
during a routine check 11 months from now. Emergency
provisioning required. Database locked for migration over a
weekend. Users impacted.

**WHAT HAPPENS WITH PLANNING:**
Prometheus alert fires at 270 days out (30-day lead time
buffer): "disk projected to hit 80% in 30 days."
Engineers plan and execute disk expansion with full
preparation time. Zero user impact. Database migrated
during scheduled maintenance window.

---

### 🧠 Mental Model / Analogy

> Capacity planning with metrics is like an astronomer
> using orbital mechanics to predict where an asteroid
> will be in 2 years - not where it is now. The asteroid's
> current position is observable; its future trajectory
> is calculated from velocity, direction, and gravitational
> influences. The prediction does not need to be perfect -
> the goal is to detect collision courses early enough
> to take action. A 10% forecast error with 2 years of
> lead time is fine; a 1% error with 2 hours of lead time
> is an incident.

Element mapping:
- "Asteroid's current position" → current utilization (point-in-time)
- "Orbital mechanics calculation" → predict_linear() / regression
- "Collision course" → resource approaching saturation
- "2 years of lead time" → early warning at safe headroom level
- "10% forecast error OK" → headroom absorbs forecast uncertainty

Where this analogy breaks down: asteroids follow Newtonian
mechanics with high predictability; resource utilization
trends are noisier and are affected by unpredictable product
launches, traffic spikes, and data migrations - seasonal
decomposition is required to separate the trend from noise.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Capacity planning means looking at how fast you are using
up a resource (disk, CPU, memory) and calculating when
you will run out. Then you add more capacity before you
actually run out.

**Level 2 - How to use it (junior developer):**
In Prometheus, use `predict_linear(metric[timewindow],
seconds)` to forecast future values. Set an alert that
fires when the predicted value exceeds 90% of capacity
within 30 days. This gives 30 days of warning before
a resource is exhausted - enough time to plan and act.

**Level 3 - How it works (mid-level engineer):**
Capacity planning requires three inputs: current utilization,
growth trend, and safe headroom threshold. Use a sliding
window of 30-90 days for the trend calculation (too short:
noisy; too long: misses growth acceleration). Set the alert
threshold at 70-80% utilization rather than 95%+ (alerts
at 95% give you 5% of capacity remaining to act - not enough
for planned actions). Consider seasonal patterns: database
size grows faster in Q4 for e-commerce; compute grows faster
during marketing campaigns.

**Level 4 - Why it was designed this way (senior/staff):**
The headroom model (maintain 20-30% free capacity) is
designed specifically to absorb forecast error AND handle
burst traffic. If utilization is at 70% and a campaign
doubles traffic, peak utilization hits ~90% - still safe.
If utilization is at 90% and a campaign doubles traffic,
peak hits ~130% of capacity - saturation and incident.
The headroom is the mathematical buffer that makes the
system robust to forecast uncertainty. The alert threshold
is set below the safe ceiling to include lead time for
provisioning actions - the alert should fire early enough
that planned (not emergency) provisioning is possible.

**Level 5 - Mastery (distinguished engineer):**
At large scale, capacity planning requires decomposing
utilization into components: baseline growth (feature
additions, new data), seasonal variation (periodic patterns),
and event-driven spikes (campaign launches, product releases).
Forecasting that ignores seasonality will produce wildly
inaccurate predictions during seasonal peaks. Proper
decomposition uses STL decomposition or Holt-Winters
exponential smoothing. The output is not a single forecast
number but a confidence interval: "with 95% confidence,
disk utilization will reach 80% between 270 and 310 days
from now." The capacity plan then provisions to ensure
headroom even at the lower bound (270 days) accounting
for provisioning lead time. Cost optimization adds the
additional dimension of right-sizing: over-provisioned
resources also cost money, so the goal is not maximum
headroom but optimal headroom given cost and risk tolerance.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS CAPACITY PLANNING ALERT:**

```yaml
# Disk will be full in 4 days - alert now
groups:
  - name: capacity.rules
    rules:
      - alert: DiskFillsIn4Days
        # predict_linear: linear regression over last 6h
        # projects value 4 days forward
        expr: >
          predict_linear(
            node_filesystem_free_bytes{
              mountpoint="/",job="node"
            }[6h],
            4 * 24 * 3600
          ) < 0
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Disk predicted full in 4 days"
          description: >
            {{ $labels.instance }} disk /
            predicted to be full in 4 days
            based on last 6h growth trend.

      # Also alert when already at 80%
      - alert: DiskNearingCapacity
        expr: >
          node_filesystem_free_bytes{mountpoint="/"} /
          node_filesystem_size_bytes{mountpoint="/"} < 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk > 80% full"
```

**TREND ANALYSIS PIPELINE:**

```
┌───────────────────────────────────────────────────┐
│          CAPACITY PLANNING WORKFLOW               │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. Collect time-series (Prometheus)              │
│     CPU, Memory, Disk, Queue depth, Connections  │
│     Retention: 90 days for trend analysis        │
│                                                   │
│  2. Baseline trend (weekly report)                │
│     For each resource:                           │
│       current_utilization: 65%                   │
│       growth_rate: +0.5%/day                     │
│       projected_to_80%: 30 days                  │
│       provisioning_lead_time: 3 days             │
│       status: ALERT (30 days < 90-day threshold) │
│                                                   │
│  3. Seasonal decomposition (quarterly)            │
│     Identify Q4 peak multiplier: 1.4x            │
│     Adjust capacity models for known events      │
│                                                   │
│  4. Provisioning trigger                          │
│     Fire when: days_to_threshold < lead_time*3   │
│     (3x lead time = safety margin for delays)    │
│                                                   │
│  5. Post-provisioning verification               │
│     Confirm utilization dropped below 70%        │
│     Update growth model with new baseline        │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CAPACITY PLANNING LIFECYCLE:**

```
Metrics collected continuously (Prometheus)
   │
   ↓
Weekly automated capacity report generated
   │ predict_linear() for each resource
   │ trend over 30-day window
   │
   ↓
Resources projected >80% utilization in <90 days
   │ Capacity alert fires
   │ Engineering review triggered
   │
   ├── Infrastructure scale-up planned
   │   (database disk, compute nodes)
   │
   ├── Application optimization considered
   │   (is growth due to leak/bloat/inefficiency?)
   │
   └── Cost review
       (is over-provisioned resource identified?)
          │
          ↓
   Provisioning action executed
   (within planned maintenance window)
          │
          ↓
   Utilization confirmed below safe threshold
          │
          ↓
   Growth model updated with new baseline
```

**FAILURE PATH:**

```
Trend alert not configured →
  Resource grows silently to 90%+ →
    Performance degrades at peak load →
      Incident triggered by users →
        Emergency provisioning begins →
          Database locked or service degraded
          during emergency scale action
```

**WHAT CHANGES AT 10X SCALE:**
At 100 services with thousands of resource metrics, manual
review of capacity reports is not feasible. The automation
must categorize resources into: green (>90 days to threshold),
yellow (30-90 days), red (<30 days) and route red/yellow
items to the owning team as tickets. Each ticket should
include: the trend data, the forecast, the recommended
action, and the deadline. Manual review is only required
for red items requiring immediate action.

---

### 💻 Code Example

**Example 1 - BAD: alert on current utilization only**

```yaml
# BAD: alerts only when already near capacity
# By the time this fires, you may have <1 day to act
- alert: HighDiskUsage
  expr: >
    node_filesystem_used_bytes /
    node_filesystem_size_bytes > 0.90
  annotations:
    summary: "Disk is over 90% full"
    # Problem: disk at 90% with 3-day lead time for
    # provisioning = you are already in an incident
```

**Example 2 - GOOD: predictive alert with trend**

```yaml
# GOOD: predict future utilization and alert early
- alert: DiskCapacityWarning
  # predict_linear: linear regression over 24h data
  # projected 30 days forward (30 * 24 * 3600 seconds)
  expr: >
    predict_linear(
      node_filesystem_free_bytes[24h],
      30 * 24 * 3600
    ) < node_filesystem_size_bytes * 0.2
  for: 2h           # must persist for 2h (not spike)
  labels:
    severity: warning
  annotations:
    summary: >
      Disk predicted to exceed 80% within 30 days

# This fires 30 days BEFORE the problem
# Gives planned (not emergency) provisioning window
```

**Example 3 - Automated capacity reporting**

```python
#!/usr/bin/env python3
"""
Weekly capacity planning report from Prometheus.
Reports: resource, current%, trend/day, days_to_80pct
"""
import requests
import json
from datetime import datetime

PROMETHEUS_URL = "http://prometheus:9090"

def query_prometheus(promql: str) -> list:
    resp = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": promql}
    )
    return resp.json()["data"]["result"]

def capacity_report():
    resources = [
        {
            "name": "disk_root",
            "used": 'node_filesystem_used_bytes'
                    '{mountpoint="/"}',
            "total": 'node_filesystem_size_bytes'
                     '{mountpoint="/"}'
        },
        {
            "name": "memory",
            "used": 'node_memory_MemTotal_bytes - '
                    'node_memory_MemAvailable_bytes',
            "total": 'node_memory_MemTotal_bytes'
        }
    ]

    report = []
    for r in resources:
        # Current utilization
        current_used = float(
            query_prometheus(r["used"])[0]["value"][1]
        )
        total = float(
            query_prometheus(r["total"])[0]["value"][1]
        )
        pct = current_used / total * 100

        # Trend: projected free bytes in 30 days
        projected_free = query_prometheus(
            f"predict_linear(({r['total']}-{r['used']})"
            f"[7d], 30*24*3600)"
        )
        days_to_80pct = None
        if projected_free:
            pf = float(projected_free[0]["value"][1])
            if pf < total * 0.2:
                # already trending past 80% within 30d
                days_to_80pct = "<30 days WARNING"

        report.append({
            "resource": r["name"],
            "current_pct": round(pct, 1),
            "days_to_80pct": days_to_80pct or "OK (>30d)"
        })

    print(f"Capacity Report - {datetime.now().date()}")
    for item in report:
        status = "WARN" if "WARNING" in \
            str(item["days_to_80pct"]) else "OK"
        print(f"[{status}] {item['resource']:20s} "
              f"cur={item['current_pct']:5.1f}% "
              f"forecast={item['days_to_80pct']}")

capacity_report()
```

**How to test / verify correctness:**
Backtest the forecast: take a resource that was provisioned
6 months ago and run `predict_linear` against the data
from 6 months ago. Does the forecast from 6 months ago
accurately predict today's utilization? How accurate is
the prediction at 30, 60, and 90 day horizons? This
backtest calibrates your confidence in the forecast model.

---

### ⚖️ Comparison Table

| Approach | Planning Horizon | Accuracy | Automation | Best For |
|---|---|---|---|---|
| **predict_linear() alerts** | Days to weeks | Medium | High | Linear growth resources |
| Holt-Winters forecasting | Weeks to months | High (seasonal) | Medium | Periodic traffic patterns |
| Manual trend review | Ad hoc | Low | None | Small teams, simple infra |
| Cloud auto-scaling | Minutes (reactive) | High (current) | High | Stateless compute bursts |
| Annual capacity planning | 12 months | Low | None | Data center hardware |

**How to choose:**
Use `predict_linear()` alerts for all resource types as a
first-pass early warning. Add Holt-Winters or seasonal
decomposition for resources with strong periodic patterns
(e.g., weekly traffic cycles, monthly batch jobs). Use
cloud auto-scaling as the reactive layer for stateless
compute - but set the auto-scaling limits based on capacity
planning, not ad hoc.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Auto-scaling eliminates capacity planning | Auto-scaling handles stateless compute; databases, queues, disks, and network don't auto-scale - they all require capacity planning |
| Monitor at 90% utilization and act then | At 90% utilization, you often have <1 week to provision; planned provisioning requires 30+ days lead time in most environments |
| Capacity planning is an annual process | Resources grow continuously; capacity planning must be a continuous automated process with weekly alert reviews |
| Linear regression is sufficient for all resources | Resources with periodic patterns (weekly peaks, seasonal growth) require seasonal decomposition - linear regression will underforecast |
| Capacity planning is only for storage | CPU, memory, database connections, message queue depth, and API rate limits all require capacity planning |

---

### 🚨 Failure Modes & Diagnosis

**Forecast Miss Due to Unmodeled Growth Spike**

**Symptom:**
Capacity planning forecast predicted disk exhaustion in 180
days. Disk exhausted in 45 days. Emergency provisioning
required. Incident occurred.

**Root Cause:**
A new feature was launched 3 weeks ago that produces 10x
the log volume of previous features. The forecast was based
on pre-launch growth trend data. The model had no way to
account for the launch because it was not in the historical
data used for projection.

**Diagnostic Questions:**
- Was there a recent deployment that changed data growth rate?
- Is the growth rate consistent with the pre-launch trend
  or has it changed slope?
- Was the launch planned well enough in advance that capacity
  could have been pre-provisioned?

**Fix:**
Implement a "capacity impact assessment" step in the launch
checklist for all features: estimate data/resource impact
before launch. Pre-provision capacity before the launch
rather than relying on post-launch forecast detection.

**Prevention:**
For any launch expected to increase data volume by >20%,
require a capacity pre-provisioning review. Monitor growth
rate trend as a metric alongside absolute utilization -
an alert on "growth rate doubled from baseline" would have
caught this immediately.

---

**Saturation Non-Linearity Not Modeled**

**Symptom:**
PostgreSQL was at 70% CPU utilization. predict_linear()
forecast estimated 30 days to 90% (the alert threshold).
Engineers planned provisioning in 3 weeks. 2 weeks later,
the database is at 95% CPU and query latency is 10x.

**Root Cause:**
CPU saturation in PostgreSQL is non-linear: at 70% CPU,
queries queue normally. At 85% CPU, context switching
overhead begins. At 90%+, the database enters thrashing
mode where throughput actually decreases with more requests
because context switching cost exceeds query execution time.
The linear forecast was accurate about when 90% would be
reached but did not predict the non-linear degradation
starting at 85%.

**Diagnostic Commands:**
```bash
# PostgreSQL: check for query queue buildup
SELECT count(*) FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

# Check context switch rate (non-linearity indicator)
vmstat 1 10 | awk '{print $11, $12}'
# cs (context switches) column
```

**Fix:**
For resources with known non-linear saturation (PostgreSQL,
Redis, JVM GC), set the alert threshold lower than the
linear-degradation assumption: alert at 70% rather than
80%, with a 2x earlier provisioning trigger.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Prometheus - Metrics Collection` - the primary data source
  for resource utilization time-series
- `Grafana - Dashboards and Visualization` - dashboards
  for capacity trend visualization
- `USE Method` - provides the framework for which resources
  to monitor for capacity planning (utilization, saturation)

**Builds On This (learn these next):**
- `Observability at Scale` - at-scale capacity planning
  requires automated reporting and ticket routing
- `Observability Platform Architecture Design` - capacity
  planning for the observability platform itself
- `Platform Observability Engineering` - capacity planning
  integrated into the platform engineering workflow

**Alternatives / Comparisons:**
- `Toil Reduction Strategy` - capacity exhaustion incidents
  are toil; capacity planning eliminates that class of toil
- `Time-Series Database Design` - the storage system for
  the capacity metrics must itself be capacity-planned
- `Formal SLO Theory` - SLO budgets must account for
  capacity-driven reliability degradation periods

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Using metric trends to predict and       │
│              │ prevent resource exhaustion before it    │
│              │ becomes an incident                      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Point-in-time monitoring detects         │
│ SOLVES       │ saturation too late for planned action   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Headroom IS the safety margin for        │
│              │ forecast error; maintain 20-30% free     │
│              │ so forecast inaccuracy does not cause    │
│              │ incidents                                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All finite resources: disk, DB memory,  │
│              │ connection pools, queue depth, API rate  │
│              │ limits - anything that can be exhausted  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Applying linear regression to resources  │
│              │ with known non-linear saturation without │
│              │ adjusting the alert threshold lower      │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Alerting at 90% utilization - gives <1  │
│              │ week for provisioning in most infra      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Earlier provisioning = lower risk but    │
│              │ higher cost; right-size the headroom     │
│              │ based on provisioning lead time + risk   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Monitor the slope, not just the level." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Observability at Scale → Platform       │
│              │ Architecture → Time-Series DB Design     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use `predict_linear()` for early warning alerts - fire
   at 30+ days to threshold, not at 90% current utilization.
   By 90%, you are already in emergency mode.
2. Headroom is not waste - it is the mathematical buffer
   for forecast error and unplanned traffic spikes. 20-30%
   free capacity is a reliability investment.
3. Auto-scaling only helps stateless compute. Databases,
   queues, disks, and network capacity all require
   proactive capacity planning regardless of cloud provider.

**Interview one-liner:**
"Capacity planning with metrics uses historical utilization
trends - `predict_linear()` in Prometheus - to fire alerts
30+ days before a resource hits saturation, giving engineers
time for planned provisioning rather than emergency response.
The key insight is that the alert threshold should be set at
70-80% utilization, not 90%+, because the 20-30% headroom
is the safety margin that absorbs forecast error and spike
traffic. Auto-scaling handles stateless compute but does
not solve capacity planning for databases, queues, or disks."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any finite resource under continuous growth pressure will
be exhausted if not actively managed. The planning horizon
must exceed the provisioning lead time by a safety margin
proportional to forecast uncertainty. This is a universal
principle that applies to supply chain management, software
system resources, financial reserves, and organizational
headcount planning.

**Where else this pattern applies:**
- **DNS TTL and rate limits** - API rate limits (e.g.,
  Kubernetes API server request rate) require the same
  trend analysis; a linearly growing number of controllers
  will eventually exhaust API rate limits
- **Thread pools and connection pools** - pool exhaustion
  is the most common Java/database production incident;
  pool depth metrics with predict_linear() alerts prevent them
- **Cost planning** - cloud cost is a resource with its own
  growth trend; the same forecasting approach predicts
  when monthly cloud spend will breach budget

**Industry applications:**
- **Streaming media** - video encoding queues are capacity-
  planned 90 days ahead to handle major sports or entertainment
  events that drive 10x-50x normal encoding volume
- **E-commerce** - database storage capacity is modeled
  annually with Black Friday as the peak week, with
  seasonal decomposition used to separate baseline growth
  from the annual peak multiplier

---

### 💡 The Surprising Truth

The most expensive cloud bills are not from over-provisioned
resources - they are from under-provisioned resources that
failed and required emergency over-provisioning. When a
database disk fills and you need to provision emergency
capacity, you often have to provision 3-5x what you actually
need because that is the next available tier. A 1TB disk at
95% gets replaced with a 4TB disk in an emergency because
you need headroom immediately and cannot provision precisely.
The planned alternative: incrementally provision from 1TB
to 2TB 90 days before you need it, at exactly the right size.
Proactive capacity planning is not just a reliability
discipline - it is the most effective cloud cost optimization
practice available, and it costs nothing except the time
to set up `predict_linear()` alerts.

> Entry stub. Generate full content using Master Prompt v3.0.
