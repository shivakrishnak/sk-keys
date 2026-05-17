---
id: SYD-027
title: Capacity Planning
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-014, SYD-026
used_by: ""
related: SYD-014, SYD-025, SYD-026, SYD-028
tags:
  - architecture
  - operations
  - infrastructure
  - planning
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /syd/capacity-planning/
---

# SYD-027 - Capacity Planning

⚡ TL;DR - Capacity planning is the process of
determining the infrastructure resources (compute,
storage, network) needed to meet projected load
with adequate headroom. It bridges back-of-envelope
estimation (what order of magnitude?) and production
operations (how much do we actually provision?). Done
well, it prevents over-provisioning (wasted cost) and
under-provisioning (production failures). It requires
measuring current utilization, forecasting growth,
and provisioning for peak load plus headroom.

| #027 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Auto Scaling, Back-of-Envelope Estimation | |
| **Used by:** | (operational discipline - applies broadly) | |
| **Related:** | Auto Scaling, Thundering Herd, Back-of-Envelope Estimation, Rate Limiting | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A startup grows from 10,000 to 500,000 users in 3
months after a viral moment. The backend is
provisioned for 50,000 users. The system collapses
under the load. The team scrambles to provision more
servers, but the provisioning takes 2-3 weeks.
Business lost during those weeks.

Conversely: a team over-provisions 10x, spending
$500k/month on servers running at 8% utilization.

**THE NEED:**
Both failures (under- and over-provisioning) are
expensive. Capacity planning is the discipline that
minimizes both risks by measuring, forecasting, and
provisioning with principled headroom.

---

### 📘 Textbook Definition

**Capacity planning:** The process of determining
the production capacity needed by an organization
to meet changing demands for its products or services.
In software systems: capacity planning identifies
the compute, memory, storage, network, and operational
resources required to handle projected load (current
and forecasted), with appropriate headroom for
peak traffic and unexpected growth. It involves:
measuring current resource utilization, profiling
resource consumption per unit of work, forecasting
future demand, calculating required resources, and
provisioning with safety margins.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
How much infrastructure do we need now, next quarter,
and next year - and how do we provision it so we
never run out but don't waste money?

**One analogy:**
> A restaurant preparing for the weekend rush:
> "We usually serve 150 covers on Saturday. Last
> month we hit 200 covers once. We prep for 180 covers
> (20% headroom over usual peak). We hire 2 extra
> servers for Saturday nights. If a booking spike
> happens, we call in a third."
>
> The restaurant is doing capacity planning: measure
> typical load, identify historical peak, add headroom,
> provision for that level. Have an escalation plan
> (call the third server) for unexpected spikes.

**One insight:**
Capacity planning is not just about avoiding failure
- it is also about avoiding waste. A system running
at 8% CPU average is either massively over-provisioned
or not generating enough load to justify its cost.
Both extremes need addressing.

---

### 🔩 First Principles Explanation

**THE CAPACITY PLANNING PROCESS:**

```
Step 1: Measure current utilization
  For each resource (CPU, memory, disk I/O, network):
  - Average utilization
  - Peak utilization (P99 over 30 days)
  - Trend (growing? stable? seasonal?)

Step 2: Profile resource consumption per unit of work
  - How much CPU does 1,000 additional QPS consume?
  - How much memory does 1 million cached sessions use?
  - How much disk I/O does 1,000 writes/sec generate?
  This creates a resource cost model:
  resources_needed = baseline + (units × cost_per_unit)

Step 3: Forecast demand
  - Current QPS, storage growth rate
  - Historical growth rate (week/week, month/month)
  - Business projections: planned marketing, launches
  - Seasonal patterns: Black Friday spike, year-end

Step 4: Calculate required resources
  required = forecast_peak × (1 + headroom_factor)
  Typical headroom: 30-50% above expected peak
  Why 30-50%: allows for unexpected growth, prevents
  running at 100% CPU (degradation starts earlier)

Step 5: Provisioning plan
  - Timeline: when to provision
  - Method: manual, auto-scaling, IaC templates
  - Monitoring: alert before hitting capacity limits
  - Review cadence: monthly/quarterly capacity review
```

**THE RESOURCE UTILIZATION SAFE ZONES:**

```
RESOURCE        SAFE ZONE   WARNING     CRITICAL
CPU (average)   <60%        60-80%      >80%
CPU (peak)      <70%        70-90%      >90%
Memory          <80%        80-90%      >90%
Disk I/O        <70%        70-85%      >85%
Network         <70%        70-80%      >80%
Connection pool <80%        80-90%      >90%

NOTE: "Safe" means system performs well and has
headroom for spikes. "Critical" means the system
is at risk of performance degradation or failure
under any additional load.
```

**THE TRADE-OFFS:**
**Under-provisioning:**
Cost: failures, degraded performance, lost revenue,
on-call incidents, customer churn.
**Over-provisioning:**
Cost: wasted infrastructure spend. At scale, 10%
over-provisioning = significant annual cost.
**Auto-scaling vs pre-provisioning:**
Auto-scaling reduces over-provisioning waste. But
not all resources auto-scale: databases, stateful
services, network bandwidth often require manual
pre-provisioning.

---

### 🧪 Thought Experiment

**SCENARIO: E-commerce capacity planning for Black Friday**

A retailer has:
- Normal peak: 5,000 QPS (October average)
- Last Black Friday peak: 45,000 QPS (9x normal)
- Infrastructure: scaled for 8,000 QPS (60% headroom
  over 5,000 normal peak)
- Auto-scaling: web tier only; DB is fixed 2 primaries

**The problem:**
9x peak means they need 45,000 QPS capacity.
Current DB capacity: 2 primaries × 5,000 writes/sec
= 10,000 writes/sec. At Black Friday peak: needs
45,000 QPS / 10 (read:write ratio) = 4,500 write/sec
+ 40,500 reads/sec. Reads need 40,500 / 10,000 = 4 DB
read replicas. Current count: 1 replica. Not enough.

**Capacity plan for Black Friday:**
- 3 weeks before: add 3 DB read replicas
- 1 week before: load test at 50,000 QPS (10% buffer)
- Day before: verify all replicas synced, auto-scaling
  groups pre-warmed (avoid cold start delay)
- Day-of: operator on-call with runbook for emergency
  scale-out
- Post-event: scale back to normal within 48 hours

**THE INSIGHT:**
Capacity planning for known events (Black Friday)
is straightforward because the spike is predictable.
The harder cases: unknown events (viral social media
post, news coverage), product launches with uncertain
uptake, and gradual growth that compounds month-over-
month. Each requires different forecasting models
and provisioning strategies.

---

### 🧠 Mental Model / Analogy

> Capacity planning is like water reservoir management:
> - The reservoir is your infrastructure capacity
> - Inflow = growth/demand
> - Outflow = serving traffic
> - Water level = current headroom
>
> A reservoir manager:
> 1. Measures current water level (utilization)
> 2. Forecasts rainfall (demand growth)
> 3. Plans when to open additional sources (provision)
> 4. Maintains minimum reserves (safety headroom)
> 5. Does NOT let the reservoir run dry (outage)
> 6. Does NOT build 10x capacity for current rainfall
>    (over-provisioning)
>
> The reservoir manager acts weeks before the
> critical level - not at the last moment.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Figuring out how much computer power, memory, and
storage we need to handle our users, both now and
in the future. Plan ahead so the system does not
fall over and so we do not waste money.

**Level 2 - How to use it (junior developer):**
Set up dashboards: track CPU, memory, disk, and
QPS per service. Check utilization weekly. Alert
if any metric approaches 80%. When it hits 70%,
plan and execute a scaling action (before it is urgent).

**Level 3 - How it works (mid-level engineer):**
The key metric is utilization rate per unit of load.
"Every 1,000 QPS increase consumes 15% more CPU"
creates a linear model. Extrapolate: at 10,000 QPS
(2x current), CPU will be X%. If X% > 80%: provision
now, before that load arrives. Build the model from
load tests and production measurements.

**Level 4 - Why it was designed this way (senior/staff):**
At scale, capacity planning is a financial discipline
as much as a technical one. Cloud infrastructure
costs are the largest line item for many tech companies.
Reserved instances (commit 1-3 years, get 30-60%
discount) vs on-demand vs spot instances create a
portfolio optimization problem. Capacity planning
teams at large companies build financial models: what
mix of reserved/on-demand/spot minimizes cost while
meeting reliability requirements?

**Level 5 - Mastery (distinguished engineer):**
The frontier of capacity planning is predictive
provisioning using machine learning. Instead of
linear extrapolation from historical data, ML models
incorporate seasonality, business event calendars,
and cross-service dependencies to predict capacity
needs. Netflix's engineering blog describes capacity
planning that accounts for new content releases,
award show timing, and even weather events (people
stream more when it rains). At this level, capacity
planning merges with demand forecasting and cost
optimization as a unified discipline.

---

### ⚙️ How It Works (Mechanism)

**Resource profiling - linear model building:**

```
┌──────────────────────────────────────────────────────┐
│ CAPACITY MODEL BUILDING                             │
│                                                      │
│ Observation (2 weeks of production data):           │
│                                                      │
│ QPS     | CPU (avg) | Mem (GB) | DB Conn            │
│  5,000  |   25%     |  12 GB   |  120               │
│  8,000  |   38%     |  14 GB   |  190               │
│  12,000 |   56%     |  17 GB   |  280               │
│  15,000 |   72%     |  19 GB   |  350               │
│                                                      │
│ Model (linear regression):                          │
│   CPU% = 1.5% + (QPS × 0.00425)                    │
│   Mem = 9 GB + (QPS × 0.00066 GB)                  │
│   DB Conn = 20 + (QPS × 0.022)                     │
│                                                      │
│ Forecast: QPS will reach 25,000 in 3 months         │
│ CPU needed = 1.5 + 25,000 × 0.00425 = 107.75%      │
│ → Need 2x servers, or upgrade instance type         │
│ Mem needed = 9 + 25,000 × 0.00066 = 25.5 GB        │
│ DB Conn needed = 20 + 25,000 × 0.022 = 570          │
│ → Connection pool limit: 400. Need to add            │
│   PgBouncer or connection pooling before then.      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Capacity model query (Prometheus)**
```promql
# Project when CPU will hit 80% at current growth rate
# Use linear_prediction or predict_linear in Prometheus

# Current CPU utilization (30-day average trend)
avg_over_time(
  node_cpu_utilization{job="api-server"}[30d]
)

# Predict when CPU will exceed 0.8 (80%)
# based on 30-day linear trend
# Returns seconds until threshold is crossed
predict_linear(
  node_cpu_utilization{job="api-server"}[30d],
  86400 * 30  # predict 30 days ahead
)
# If result > 0.8: provision more capacity
# within the next 30 days

# Per-instance headroom check:
# Alert if any instance will hit 80% within 14 days
- alert: CapacityHeadroomLow
  expr: >
    predict_linear(
      node_cpu_utilization[14d], 86400 * 14
    ) > 0.8
  labels:
    severity: warning
  annotations:
    summary: >
      Instance {{ $labels.instance }} predicted to
      exceed 80% CPU in 14 days.
      Action: review capacity plan.
```

**Example 2 - Storage capacity trending**
```python
# Track storage growth and project exhaustion date
import datetime
from scipy import stats

def project_storage_exhaustion(
        measurements: list[tuple[datetime.datetime, float]],
        capacity_gb: float,
        warning_threshold: float = 0.85
) -> datetime.datetime:
    """
    Given time-series measurements of storage usage (GB),
    project when storage will hit warning_threshold.
    """
    # Convert to seconds since first measurement
    t0 = measurements[0][0]
    x = [(m[0] - t0).total_seconds() for m in measurements]
    y = [m[1] for m in measurements]

    # Linear regression
    slope, intercept, r_value, _, _ = stats.linregress(x, y)

    # Time until threshold
    target = capacity_gb * warning_threshold
    if slope <= 0:
        return None  # Not growing

    seconds_to_threshold = (target - intercept) / slope
    return t0 + datetime.timedelta(seconds=seconds_to_threshold)

# Example:
# storage growing from 50 TB to 75 TB over 6 months
# Capacity: 100 TB
# Warning at 85 TB: project when that is reached
# → Plan capacity expansion 30+ days before that date
```

**Example 3 - Pre-warming auto-scaling for known events**
```bash
#!/bin/bash
# Pre-warm auto-scaling group before known traffic event
# Run 2 hours before Black Friday midnight start

EVENT="black-friday-2024"
ASG_NAME="api-servers-prod"
NORMAL_MIN=5
NORMAL_MAX=20
EVENT_MIN=30       # Pre-scale to minimum 30 instances
EVENT_MAX=100      # Allow scale to 100

echo "Pre-warming $ASG_NAME for $EVENT"

# Set minimum instances (prevents scale-in during event)
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name $ASG_NAME \
    --min-size $EVENT_MIN \
    --max-size $EVENT_MAX

# Wait for instances to be in service
echo "Waiting for $EVENT_MIN instances to be healthy..."
until [ $(aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names $ASG_NAME \
    --query 'AutoScalingGroups[0].Instances[?HealthStatus==`Healthy`] | length(@)' \
    --output text) -ge $EVENT_MIN ]; do
    sleep 30
done

echo "Pre-warm complete: $EVENT_MIN instances ready"

# Schedule post-event scale-down
at -f scale-down.sh 08:00 tomorrow  # After Black Friday peak
```

---

### ⚖️ Comparison Table

| Approach | Best For | Risk | Cost Efficiency |
|---|---|---|---|
| Manual provisioning (fixed) | Predictable, steady-state load | Under-provisioning on spikes | Low (over-provisioned buffer needed) |
| Auto-scaling only | Variable, unpredictable load | Cold start latency during scale-out | High (pay only for what is used) |
| Capacity planning + auto-scaling | Known growth + unpredictable spikes | Requires good monitoring + forecasting | Best (right-sized base + elastic peak) |
| Perpetual over-provisioning | Teams without capacity expertise | High waste | Very low |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Auto-scaling eliminates capacity planning | Auto-scaling handles variable load within a range. It does not eliminate the need to plan the minimum and maximum of that range. Stateful services (DBs) do not auto-scale trivially. Network bandwidth, licenses, and support tiers have fixed capacity that must be planned. |
| 100% utilization is the target | Running at 100% CPU/memory eliminates headroom for spikes. A system at 100% average CPU will fail on any load increase. The target is 60-70% average, leaving 30-40% headroom for spikes. |
| Capacity planning is done once a year | At high-growth companies: monthly. At stable companies: quarterly. At minimum: before any major product launch or seasonal event. The frequency should match the rate of change of the business. |

---

### 🚨 Failure Modes & Diagnosis

**Database Connection Pool Exhaustion**

**Symptom:**
System handles 15,000 QPS fine. An A/B test launches
a new feature (25% rollout). Within 10 minutes,
the database starts throwing "too many connections"
errors. The new feature makes 3 DB queries per request
(the old feature made 1). 25% of 15,000 QPS × 3 = 11,250
additional DB queries/sec, overwhelming the connection pool.

**Root Cause:**
The capacity plan was based on existing features.
The new feature's resource consumption per unit
of work was 3x higher and was not modeled.

**Prevention:**
Load-test new features in staging with production-like
traffic levels before rollout. Include the feature's
DB query count in capacity analysis. Use feature flags
to roll out at 1% and measure resource consumption
change before 25% rollout.

```bash
# Measure DB queries per request before/after feature flag
# Using slow query log + request correlation
# Before feature: avg 1.2 DB queries per API request
# After feature (5% rollout sample):
#   avg 3.8 DB queries per API request
# Capacity impact: 3.8/1.2 = 3.2x DB load
# At 25% rollout: total = 75% × 1.2 + 25% × 3.8
#   = 0.9 + 0.95 = 1.85 (1.54x current DB load)
# At 100% rollout: 3.8/1.2 = 3.2x → beyond DB capacity
# Decision: add read replicas before 100% rollout
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Auto Scaling` - the operational mechanism that
  capacity planning configures
- `Back-of-Envelope Estimation` - the initial rough
  sizing that capacity planning refines

**Builds On This (learn these next):**
- `Rate Limiting (System)` - a complementary technique:
  instead of always provisioning for peak, rate limit
  to protect the system at planned capacity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Plan and provision infrastructure to     │
│               │ meet current + projected load            │
├───────────────┼──────────────────────────────────────────┤
│ PROCESS       │ 1. Measure utilization                   │
│               │ 2. Profile resource cost per QPS         │
│               │ 3. Forecast demand growth                │
│               │ 4. Calculate needed resources (+30-50%)  │
│               │ 5. Provision ahead of need               │
├───────────────┼──────────────────────────────────────────┤
│ SAFE ZONES    │ CPU: <60% avg, <80% peak                 │
│               │ Memory: <80%                             │
│               │ DB connections: <80%                     │
├───────────────┼──────────────────────────────────────────┤
│ HEADROOM      │ 30-50% above expected peak               │
│               │ Never provision to 100% target           │
├───────────────┼──────────────────────────────────────────┤
│ CADENCE       │ Review monthly (high-growth)             │
│               │ Quarterly (stable) + before events       │
├───────────────┼──────────────────────────────────────────┤
│ METRICS       │ CPU, memory, storage, QPS, connections,  │
│               │ p99 latency (leading indicator of stress)│
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Measure, forecast, provision with       │
│               │  30% headroom before you need it."       │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Rate Limiting → Token Bucket             │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Process: measure → profile cost-per-QPS → forecast →
   provision at (peak × 1.3). Never provision to 100%.
2. CPU target: 60-70% average. 30-40% headroom handles
   unexpected spikes without degradation.
3. Capacity planning has a time dimension: provisioning
   takes time. Plan and act before the critical level is
   reached, not after the first degradation alert.

**Interview one-liner:**
"Capacity planning determines how much infrastructure is
needed to handle projected load with headroom. The process:
measure current resource utilization per unit of work (e.g.,
CPU per 1000 QPS), forecast demand growth from historical
trends and business projections, and provision at peak
projected load plus 30-50% safety margin. Target: 60-70%
average CPU to maintain headroom for spikes. Key pitfall:
new features change resource consumption per request - always
load-test new features and model their resource impact before
wide rollout. Auto-scaling helps with the elastic peak, but
stateful services like databases still need manual capacity
planning."
