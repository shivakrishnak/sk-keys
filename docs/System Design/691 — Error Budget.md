---
layout: default
title: "Error Budget"
parent: "System Design"
nav_order: 691
permalink: /system-design/error-budget/
---
# 691 — Error Budget

`#devops` `#sdlc` `#advanced` `#sre` `#reliability`

⚡ TL;DR — The quantified amount of unreliability you are allowed before reliability must take priority over feature shipping.

| #691 | category: System Design
|:---|:---|:---|
| **Depends on:** | SRE, SLO, SLI | |
| **Used by:** | SRE, Release Decisions, CI/CD Gates | |

---

### 📘 Textbook Definition

An Error Budget is the maximum amount of unreliability permitted by a Service Level Objective (SLO) over a given time window. It is calculated as `Error Budget = 100% - SLO target`. The error budget provides a data-driven mechanism to balance the competing goals of shipping velocity and system reliability — when the budget is healthy, teams deploy freely; when it is exhausted, reliability work takes priority.

---

### 🟢 Simple Definition (Easy)

Error budget is **how much failure you're allowed**. If your SLO is 99.9% uptime, your error budget is 0.1% downtime (about 43 minutes per month). Spend it wisely — on incidents, deployments, and experiments. When it's gone, stop deploying until next month.

---

### 🔵 Simple Definition (Elaborated)

The error budget converts an abstract reliability goal (SLO) into a concrete resource that teams manage collaboratively. Dev teams want to spend budget on deployments (every deploy risks breaking something). SRE teams want to keep budget for incidents. When both teams share responsibility for managing the budget, the incentive conflict between "ship fast" and "stay stable" dissolves — they're working from the same data.

---

### 🔩 First Principles Explanation

**The core problem:**
"100% uptime" is impossible and too costly. But "be as reliable as possible" is unmeasurable and leads to perpetual conflict between dev (wants to ship) and ops (wants stability). Neither side has a principled way to say when enough is enough.

**The insight:**
> "Convert reliability into a budget. Budget = quantified permission to be unreliable. When the budget is healthy, ship. When it runs out, fix. Both sides work from the same math."

```
SLO: 99.9% availability over 30 days
  Total time: 30 × 24 × 60 = 43,200 minutes
  Allowed downtime (Error Budget): 43,200 × 0.001 = ~43 minutes

Month scenario:
  - Deploy #1 caused 10 min outage → 33 min remaining
  - Deploy #2 caused 15 min outage → 18 min remaining
  - Incident caused 20 min outage  → -2 min (EXHAUSTED)
  → Freeze all non-emergency deployments
```

---

### ❓ Why Does This Exist (Why Before What)

Without error budgets, reliability goals are either aspirational (ignored) or create permanent conflict between teams. Error budgets make reliability a measurable, shared resource — creating alignment instead of finger-pointing.

---

### 🧠 Mental Model / Analogy

> Error budget is like a fuel tank for a race car. The SLO sets the tank size (how much fuel = unreliability you can afford). Every incident, every risky deployment, and every planned maintenance burns fuel. When the tank is full, race freely. As it empties, become more conservative. When it reaches zero, pit stop: refuel (fix the system) before racing again.

---

### ⚙️ How It Works (Mechanism)

```
Error Budget Calculation:
  Error Budget = (1 - SLO) × Time Window

  Example: SLO = 99.9%, Window = 30 days
  Error Budget = 0.001 × 30 × 24 × 60 min = 43.2 minutes

  Remaining Budget = Error Budget - Actual Downtime

Error Budget Policies (what to do based on budget state):

  Budget > 50%  → Normal operations, full deploy velocity
  Budget 25-50% → Caution: review risky deploys
  Budget 0-25%  → Reduced velocity: only critical releases
  Budget = 0    → Deploy freeze; reliability sprint required
  Budget < 0    → Escalate: VP approval required for any deploy

Burn Rate Alert:
  Current error rate / Allowed error rate = Burn Rate
  Burn Rate > 1  → consuming budget (expected level)
  Burn Rate > 14 → fast burn: will exhaust budget in 2 days (PAGE)
  Burn Rate > 6  → moderate burn: exhausted in 5 days (TICKET)
```

---

### 🔄 How It Connects (Mini-Map)

```
[SLO defined] --> [Error Budget calculated]
                          ↓
              [Incidents + Deploys consume budget]
                          ↓
         [Budget healthy] | [Budget low] | [Budget exhausted]
              ↓                  ↓               ↓
         [Ship freely]   [Cautious deploys] [Deploy freeze]
                                                  ↓
                                       [Reliability sprint]
```

---

### 💻 Code Example

```python
# Error budget tracking — Python calculation
def calculate_error_budget(slo_percent: float, window_minutes: int,
                            actual_downtime_minutes: float) -> dict:
    """
    slo_percent: e.g., 99.9 for 99.9% availability SLO
    window_minutes: e.g., 43200 for 30 days
    actual_downtime_minutes: measured downtime in the period
    """
    budget_minutes = window_minutes * (1 - slo_percent / 100)
    remaining_minutes = budget_minutes - actual_downtime_minutes
    remaining_percent = (remaining_minutes / budget_minutes) * 100

    return {
        "slo": f"{slo_percent}%",
        "budget_minutes": round(budget_minutes, 1),
        "used_minutes": actual_downtime_minutes,
        "remaining_minutes": round(remaining_minutes, 1),
        "remaining_percent": round(remaining_percent, 1),
        "policy": "FREEZE" if remaining_percent <= 0 else
                  "CAUTION" if remaining_percent <= 25 else
                  "NORMAL"
    }

# Example
result = calculate_error_budget(
    slo_percent=99.9,
    window_minutes=43200,   # 30 days
    actual_downtime_minutes=35.0
)
# {slo: "99.9%", budget: 43.2 min, used: 35.0 min,
#  remaining: 8.2 min (19%), policy: "CAUTION"}
```

```yaml
# Prometheus alerting rules — multi-window burn rate alerts
# (Google SRE Workbook approach)
groups:
- name: error_budget_alerts
  rules:
  # Fast burn: exhaust budget in < 1 hour → PAGE
  - alert: ErrorBudgetCriticalBurn
    expr: |
      sum(rate(http_requests_total{status=~"5..",job="myservice"}[5m]))
      / sum(rate(http_requests_total{job="myservice"}[5m]))
      > 14 * 0.001   # 14x the hourly budget rate
    for: 2m
    labels: { severity: page }

  # Slow burn: exhaust budget in < 6 days → TICKET
  - alert: ErrorBudgetModerateBurn
    expr: |
      sum(rate(http_requests_total{status=~"5..",job="myservice"}[30m]))
      / sum(rate(http_requests_total{job="myservice"}[30m]))
      > 6 * 0.001
    for: 15m
    labels: { severity: ticket }
```

---

### 🔁 Flow / Lifecycle

```
1. Define SLO → calculate error budget for the month
        ↓
2. Monitor actual SLI continuously
        ↓
3. Track budget consumption (incidents + deployment impact)
        ↓
4. Budget burn rate alerts fire if consumption accelerates
        ↓
5. Budget exhausted → automated deploy gate or manual freeze
        ↓
6. Reliability sprint: reduce toil, fix flaky components
        ↓
7. New time window → budget resets → cycle repeats
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Error budget = allowed failures | Error budget = allowed unreliability (not just failures; also latency) |
| Exhausted budget means we broke our SLA | SLO breach ≠ SLA breach; SLAs have a buffer built in |
| Budget resets erase history | Historical budget trends inform risk decisions for future deploys |
| Only engineering teams track error budgets | Product managers and leadership should own SLO decisions |

---

### 🔥 Pitfalls in Production

**Pitfall 1: SLO Too Strict (Budget Always Exhausted)**
100% error budgets consumed every month → perpetual deploy freeze.
Fix: calibrate SLO to actual user tolerance; start with a lower SLO and tighten over time.

**Pitfall 2: Ignoring Burn Rate**
Budget has 30 min left at day 1 — looks fine, but if current burn rate exhausts it by day 3, it's a crisis.
Fix: always alert on burn rate (how fast are you consuming), not just remaining balance.

**Pitfall 3: Budget as Blame Tool**
Ops blame dev for "burning the budget" with deploys; dev blame ops for "hoarding budget".
Fix: error budget policies are agreed cross-functionally before any incident; it's a shared resource, not a scorecard.

---

### 🔗 Related Keywords

- **SRE** — the practice that invented and uses error budgets
- **SLO (Service Level Objective)** — defines the budget size
- **SLI (Service Level Indicator)** — measures actual reliability
- **Burn Rate** — how fast the error budget is being consumed
- **Toil** — operational work that consumes error budget; SRE aims to eliminate it

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Error Budget = 100% - SLO = quantified        │
│              │ permission to be unreliable                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Making deployment or reliability investment    │
│              │ decisions; aligning dev and ops               │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — every production system should have     │
│              │ an error budget, even if informal             │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Spend your unreliability budget deliberately  │
│              │  — on features, not accidents"                │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ SLO --> SLI --> SLA --> Burn Rate Alerts       │
└───────────────────────────────��─────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** How does the burn rate of an error budget differ from the absolute remaining balance, and why do you need both?  
**Q2.** What happens organizationally when a team's error budget is policy-enforced vs not enforced?  
**Q3.** How would you set an appropriate SLO for a new service with no historical data?

