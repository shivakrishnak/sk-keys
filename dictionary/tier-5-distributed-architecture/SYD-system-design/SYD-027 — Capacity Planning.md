---
layout: default
title: "Capacity Planning"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /system-design/capacity-planning/
id: SYD-027
category: System Design
difficulty: ★★★
depends_on: Back-of-Envelope Estimation, Monitoring, Scalability
used_by: Infrastructure Planning, SRE, DevOps
related: Auto Scaling, Load Balancing, Provisioning
tags:
  - infrastructure
  - planning
  - advanced
  - scaling
  - operations
---

# SYD-027 — Capacity Planning

⚡ TL;DR — Forecasting future resource needs (compute, storage, bandwidth) and provisioning infrastructure proactively to meet demand while optimizing costs and preventing overload.

| #702            | Category: System Design                              | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Back-of-Envelope Estimation, Monitoring, Scalability |                 |
| **Used by:**    | Infrastructure Planning, SRE, DevOps                 |                 |
| **Related:**    | Auto Scaling, Load Balancing, Provisioning           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
System grows without planning. Suddenly: CPU 95%, storage 90%, out of money. Reactive scrambling.

**THE BREAKING POINT:**
Need: Proactive resource planning. Forecast growth, provision ahead of demand, avoid last-minute crises.

**THE INVENTION MOMENT:**
"Forecast growth rate. Track resource usage trends. Provision 6 months ahead. Smooth scaling."

---

### 📘 Textbook Definition

**Capacity Planning:** Systematic process of forecasting future demand for compute, storage, and network resources, and provisioning infrastructure proactively to meet projected needs while optimizing costs and maintaining performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Monitor current usage. Forecast growth. Provision ahead. Avoid running out.

**One analogy:**

> Restaurant: "100 customers/night today. Growing 10%/month. Need 200 seats in 1 year. Build now, not when overbooked."

**One insight:**
Reactive scaling creates crises. Proactive planning prevents them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Demand grows over time (usually exponentially)
2. Provisioning takes time (months to procure hardware)
3. Under-capacity causes outages
4. Over-capacity wastes money
5. Balance: predict, provision, monitor, adjust

**CAPACITY PLANNING PHASES:**

1. **Measure**: Current usage (CPU, memory, storage, bandwidth)
2. **Forecast**: Future demand (growth rate, seasonal patterns)
3. **Plan**: Calculate resources needed
4. **Provision**: Acquire hardware (long lead time)
5. **Monitor**: Track vs. forecast, adjust plan

**THE TRADE-OFFS:**
**Gain:** Avoid outages. Smooth scaling. Cost efficiency.

**Cost:** Provisioning lag (6+ months). Over-provisioning possible. Planning overhead.

---

### 🧪 Thought Experiment

**SETUP:**
SaaS company. 10,000 users today. 20% monthly growth.

**Scenario A: No Capacity Planning (Reactive)**

- Month 1: 10K users, 10 servers
- Month 3: 14.6K users, 10 servers (CPU rising)
- Month 4: 17.6K users, CPU 90% (ALERT!)
- Month 5: 21K users, CPU 100% (OUTAGE!)
- Desperate: order servers, 3-month lead time
- Month 8: Servers arrive (too late, massive churn)

**Scenario B: With Capacity Planning (Proactive)**

- Month 0: Measure 10 servers. Forecast growth.
- Month 0: "In 6 months, need 20 servers (32K users)"
- Month 0: Order 10 servers (3-month lead time)
- Month 3: New servers arrive, 20 total
- Month 6: Actually need 21 servers (on track)
- Smooth scaling, no outages

**Insight:**
Planning lag (3-6 months) means provisioning must happen before demand appears.

---

### 🧠 Mental Model / Analogy

> City infrastructure: "1 million people today. Growing 5%/year. Need roads, water, power for 2 million in 20 years. Plan now. Construction takes 5 years."

- "Population growth" → user/demand growth
- "Roads/water/power" → compute/storage/bandwidth
- "5-year construction" → 3-6 month provisioning lag

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Forecast how much stuff (servers, storage) you'll need in 6-12 months. Order now. Avoid running out.

**Level 2 — How to use it (junior developer):**
Track CPU, memory, disk weekly. Plot trend. If CPU trending to 100% in 3 months, order more servers now (6-month lead time).

**Level 3 — How it works (mid-level engineer):**
Capacity planning process: (1) Monitor current usage (2) Calculate growth rate (3) Forecast in 6, 12 months (4) Calculate headroom needed (40-60%) (5) Provision accordingly (6) Re-forecast monthly.

**Level 4 — Why it was designed this way (senior/staff):**
Capacity planning emerged from painful experience: startups outgrow infrastructure unexpectedly. Metric: "time to capacity exhaustion = current unused capacity / growth rate". Example: 40% unused capacity + 10%/month growth = 4 months to 100%. Must provision before 4 months. Google uses: measure every metric (CPU, memory, storage, network), forecast quarterly, provision at 6-month horizons.

---

### ⚙️ How It Works (Mechanism)

Capacity planning lifecycle:

```
MEASUREMENT PHASE (Continuous)
──────────────────────────────
Collect metrics daily/hourly:
  - CPU utilization per server/pool
  - Memory utilization
  - Disk I/O
  - Network bandwidth
  - Database queries/sec
  - Storage growth rate

Store time-series data (1+ year history)

FORECASTING PHASE (Monthly)
───────────────────────────
Analyze trends:

  CPU Utilization Time Series:
    Month 1: 20%
    Month 2: 25%
    Month 3: 31%
    Month 4: 39%
    Month 5: 48%
    Growth rate: ~25% per month
    At 100%: ~3 months away

  Storage Time Series:
    Month 1: 100 GB
    Month 2: 150 GB (50% growth)
    Month 3: 225 GB (50% growth)
    Month 4: 338 GB (projected)
    Available: 1 TB
    At limit: ~8 months away

Forecast methods:
  - Linear regression (constant growth)
  - Exponential (percentage growth)
  - Seasonal adjustment (spikes/dips)
  - Compare against growth milestones

PLANNING PHASE (Quarterly)
─────────────────────────
Decision: What to provision?

Current state + projection:
  CPU: 48% today → 150% in 6 months (no headroom!)
  Need 3x more compute

  Memory: 60% today → 90% in 6 months (tight)
  Need 2x more memory

  Storage: 338 GB today → 806 GB in 12 months (50% headroom)
  Need 2x storage

Provisioning plan:
  - Add 3x compute nodes (12-week lead time)
  - Double memory per node (instant, cheaper)
  - Add 2x storage (8-week lead time)
  - Cost: $500K infrastructure investment

PROVISIONING PHASE (Long lead time)
───────────────────────────────────
Lead times vary:
  - Custom hardware: 12-16 weeks
  - Off-the-shelf servers: 4-8 weeks
  - Cloud instances: immediate (but costly)
  - Datacenter space: 8-12 weeks (cooling, power)

Order now for arrival in 12-16 weeks

DEPLOYMENT PHASE (Rolling)
──────────────────────────
When servers arrive:
  - Stage in lab
  - Run acceptance tests
  - Roll out to production (2-4 week rollout)
  - Balance traffic to new capacity

Total timeline: Order → 12 weeks → Test → 4 weeks → Deploy
= ~4 months from order to production

MONITORING & ADJUSTMENT
───────────────────────
Monthly reviews:
  - Forecast vs. actual: hit on target?
  - Adjust forecast based on new data
  - If growth faster than expected: accelerate procurement
  - If slower: defer/reduce orders
```

**Capacity Planning Formula:**

```
Time to Exhaust = Available Capacity / Growth Rate

Example:
  CPU available: 100% - 48% = 52%
  Growth rate: 25%/month
  Time to exhaust: 52% / 25% = 2.08 months
  Action: Provision now (6-month lead time > 2 months!)

  Alternative:
  Headroom target: 40% unused (prevent surprises)
  Current unused: 52%
  Acceptable range: 40-60%
  Action: OK, no need to provision yet
  Review again in 1 month
```

---

### 💻 Code Example

**Example 1 — Capacity Planning Forecast (Python):**

```python
import numpy as np
from datetime import datetime, timedelta

class CapacityPlanner:
    def __init__(self, metric_name, total_capacity):
        self.metric_name = metric_name
        self.total_capacity = total_capacity
        self.history = []  # List of (date, usage) tuples

    def add_measurement(self, date, usage):
        """Record a measurement"""
        self.history.append((date, usage))

    def forecast_linear(self, months_ahead=6):
        """Linear regression forecast"""
        if len(self.history) < 2:
            return None

        # Convert to numbers
        x = np.arange(len(self.history))
        y = np.array([usage for _, usage in self.history])

        # Linear fit: usage = a + b*month
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs[0], coeffs[1]

        # Forecast
        last_month = len(self.history) - 1
        future_month = last_month + months_ahead
        forecasted_usage = intercept + slope * future_month

        return {
            'month_ahead': months_ahead,
            'forecasted_usage': forecasted_usage,
            'growth_rate_per_month': slope,
            'months_to_capacity': (self.total_capacity - forecasted_usage) / slope if slope > 0 else float('inf')
        }

    def get_headroom_recommendation(self, target_headroom_pct=40):
        """Recommend if provisioning needed"""
        if len(self.history) < 1:
            return None

        current_usage = self.history[-1][1]
        current_headroom_pct = (1 - current_usage / self.total_capacity) * 100

        if current_headroom_pct < target_headroom_pct:
            return {
                'action': 'PROVISION NOW',
                'reason': f'Headroom {current_headroom_pct:.1f}% < target {target_headroom_pct}%',
                'urgency': 'HIGH'
            }

        forecast = self.forecast_linear(months_ahead=3)
        if forecast and forecast['months_to_capacity'] < 3:
            return {
                'action': 'PROVISION SOON',
                'reason': f"Capacity exhaustion in {forecast['months_to_capacity']:.1f} months",
                'urgency': 'MEDIUM'
            }

        return {'action': 'NO ACTION', 'urgency': 'LOW'}

# Example: CPU capacity planning
cpu_planner = CapacityPlanner(metric_name='CPU', total_capacity=100)

# Historical usage data
historical_data = [
    (datetime(2024, 1, 1), 20),
    (datetime(2024, 2, 1), 25),
    (datetime(2024, 3, 1), 31),
    (datetime(2024, 4, 1), 39),
    (datetime(2024, 5, 1), 48),
]

for date, usage in historical_data:
    cpu_planner.add_measurement(date, usage)

# Forecast 6 months ahead
forecast = cpu_planner.forecast_linear(months_ahead=6)
print(f"""
CPU CAPACITY FORECAST:
Current usage: 48%
Growth rate: {forecast['growth_rate_per_month']:.1f}% per month
Projected in 6 months: {forecast['forecasted_usage']:.1f}%
Months to capacity: {forecast['months_to_capacity']:.1f}
""")

# Check if provisioning needed
recommendation = cpu_planner.get_headroom_recommendation(target_headroom_pct=40)
print(f"Recommendation: {recommendation['action']} ({recommendation['urgency']})")
```

**Example 2 — Multi-Resource Capacity Planner:**

```python
class MultiResourcePlanner:
    def __init__(self):
        self.resources = {
            'cpu': {'capacity': 100, 'current': 48, 'growth_rate': 0.25},
            'memory': {'capacity': 1000, 'current': 600, 'growth_rate': 0.20},
            'storage': {'capacity': 10000, 'current': 3000, 'growth_rate': 0.15},
        }

    def get_provisioning_timeline(self):
        """Calculate when each resource needs provisioning"""
        timeline = {}

        for resource, data in self.resources.items():
            available = data['capacity'] - data['current']
            months_to_exhaust = available / (data['current'] * data['growth_rate'])

            # Lead time for provisioning
            lead_time = 3  # months
            provision_urgency = "NOW" if months_to_exhaust < lead_time else f"in {months_to_exhaust - lead_time:.1f} months"

            timeline[resource] = {
                'current_usage': f"{data['current']:.0f}/{data['capacity']:.0f}",
                'months_to_exhaust': months_to_exhaust,
                'provision': provision_urgency
            }

        return timeline

    def generate_report(self):
        """Generate capacity planning report"""
        timeline = self.get_provisioning_timeline()

        print("=" * 60)
        print("CAPACITY PLANNING REPORT")
        print("=" * 60)

        for resource, info in timeline.items():
            print(f"\n{resource.upper()}")
            print(f"  Current: {info['current_usage']}")
            print(f"  Exhaustion in: {info['months_to_exhaust']:.1f} months")
            print(f"  Action: Provision {info['provision']}")

        print("\n" + "=" * 60)

# Usage
planner = MultiResourcePlanner()
planner.generate_report()
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                  |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| "Cloud auto-scaling makes capacity planning unnecessary" | No. Auto-scaling addresses short-term spikes, not growth. Still need long-term planning. |
| "Measure only peak capacity"                             | Wrong. Measure trend over months. Peak is noise.                                         |
| "Over-provision to be safe"                              | Expensive and wasteful. Provision for target headroom (40-60%).                          |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Growth Faster Than Forecasted**

**Symptom:**
Forecasted 50% growth. Actually 100% growth. Capacity plan suddenly obsolete.

**Prevention:**
Re-forecast monthly. Adjust lead times if growth accelerating.

---

**Failure Mode 2: Long Provisioning Lead Time Not Accounted For**

**Symptom:**
Ordered hardware when CPU at 80%. Arrived after outage (CPU hit 100% 2 weeks earlier).

**Prevention:**
Know lead times. Provision when headroom allows for lead time. Formula: action_point = capacity - (growth_rate \* lead_time).

---

### 🔗 Related Keywords

**Prerequisites:**

- `Back-of-Envelope Estimation`, `Monitoring`

**Builds On This:**

- `Auto Scaling`, `Provisioning`, `SRE`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Forecast future resource needs and    │
│              │ provision proactively                  │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Reactive scaling causes crises; need  │
│ SOLVES       │ proactive planning                     │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Provisioning lag (3-6 months) means   │
│              │ order now for future demand            │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Measure, forecast, provision 6 months│
│              │ early, avoid outages."                 │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your system has 3-month provisioning lead time. CPU at 50%, growing 20%/month. When should you order new capacity?

**Q2.** Over-provisioning wastes money. Under-provisioning causes outages. How do you balance?
