---
layout: default
title: "Error Budget"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /system-design/error-budget/
id: SYD-016
category: System Design
difficulty: ★★★
depends_on: SLA/SLO/SLI, Service Level, Monitoring
used_by: Production Operations, SRE, Deployment Strategy
related: SLA/SLO/SLI, MTTR/MTBF, Release Cadence
tags:
  - reliability
  - sre
  - operations
  - advanced
  - risk-management
---

# SYD-016 — Error Budget

⚡ TL;DR — A measured amount of "acceptable" service failure per period (month, quarter), derived from the gap between SLA commitment and measured SLI; spending budget on deployments, experiments, and maintenance is data-driven rather than fear-driven.

| #691            | Category: System Design                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | SLA/SLO/SLI, Service Level, Monitoring          |                 |
| **Used by:**    | Production Operations, SRE, Deployment Strategy |                 |
| **Related:**    | SLA/SLO/SLI, MTTR/MTBF, Release Cadence         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
"Can we deploy today?" Risk-averse: "No, too dangerous." Team frustrated, features stuck, users wait. Or reckless: "Yes, ship it." Bugs propagate, SLA breached, customers angry, refunds issued. No principled way to decide when to deploy vs. when to hold back.

**THE BREAKING POINT:**
Reliability vs. velocity always in tension. Without a shared metric, politics and fear dominate deployment decisions—not data.

**THE INVENTION MOMENT:**
"What if we calculated how much failure we're allowed, and used that to decide when to deploy? More budget = deploy more. Low budget = hold off."

---

### 📘 Textbook Definition

**Error Budget:** The quantified amount of service unreliability (downtime, errors, latency violations) that is acceptable within a defined period (typically a month or quarter), calculated as the difference between the SLA commitment and the measured SLI performance. Once error budget is exhausted, all non-critical changes are frozen until budget recovers. Error budget directly funds (implicitly) deployment velocity, experimentation, and maintenance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Error budget = SLA allowance - actual performance. Spend it on risky changes. When empty, stop deploying.

**One analogy:**

> A budget airline oversells flights (SLA: 95% on-time). Actual: 97% on-time. They have a 2% "buffer" (error budget). They spend it on experimental routes (risky), new logistics (might fail). If on-time drops to 94%, budget is gone—no experiments until recovery.

**One insight:**
Error budget aligns business and engineering: meet SLA, and the team can move fast. Ignore SLA, and you have no budget to innovate.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Services will fail (code bugs, infrastructure issues, cascading failures)
2. Customers accept some failure (defined in SLA)
3. SLA typically 99–99.9%; actual SLI is often better (99.5–99.95%)
4. The gap is available to "spend" on risk

**DERIVED DESIGN:**
From SLA/SLO/SLI:

- SLA = 99% (monthly) = 0.01 × 2,592,000 seconds = 25,920 seconds downtime allowed
- SLI (actual) = 99.5% = 12,960 seconds downtime used
- Error Budget = 25,920 - 12,960 = 12,960 seconds remaining (half the month's budget)

This remaining 12,960 seconds is available for: risky deployments, experiments, maintenance windows, or recovery from unexpected incidents. Once spent, freeze changes until SLI recovers and budget replenishes.

**THE TRADE-OFFS:**
**Gain:** Quantified, data-driven deployment decisions. Less blame, more accountability. Clear incentives (stay above SLA, and the team can move faster).

**Cost:** Can become bureaucratic ("budget approval required"). If SLI frequently breaches SLA, deployment velocity drops to near-zero (team overwhelmed with firefighting).

---

### 🧪 Thought Experiment

**SETUP:**
Payment service. SLA = 99.5% monthly. Month = 2,592,000 seconds.

SLA Allowance = 0.005 × 2,592,000 = 12,960 seconds downtime allowed.

**WEEK 1:**
Actual SLI = 99.8% (good). Downtime = 0.002 × 648,000 = 1,296 seconds used.
Budget Remaining = 12,960 - 1,296 = 11,664 seconds.
Decision: "Safe to deploy. Budget comfortable."

**WEEK 2:**
Incident: Database failover failed. Downtime = 1,800 seconds. SLI = 99.7%.
Budget Remaining = 11,664 - 1,800 = 9,864 seconds.
Decision: "Incident happened. Budget still OK. Deploy post-mortem fixes."

**WEEK 3:**
Deploy aggressive feature (5% error rate for 1 hour = 1,800 errors). Rollback in 1 minute, but SLI dips.
Downtime = 180 seconds.
Budget Remaining = 9,864 - 180 = 9,684 seconds.
Decision: "Risky deploy, but budget allows. Safe."

**WEEK 4:**
Trend analysis: "We've spent 3,276 seconds. At this rate, we'll breach SLA in the last week."
Burn Rate = 3,276 / 21 days = 156 seconds/day.
Safe Rate = 12,960 / 30 days = 432 seconds/day.
Decision: "Burn rate is 36% of safe rate. We're conservative. Can deploy more aggressively."

**THE INSIGHT:**
Error budget isn't just "don't deploy." It's a signal: fast rate of budget burn = risky, slow burn = safe. Teams use burn rate to decide deployment cadence and risk tolerance continuously.

---

### 🧠 Mental Model / Analogy

> A software company has a credit card with a $1,000 limit (error budget). Every month, the company starts with $1,000. Risky deploys cost $50 each (risk of incident). Experiments cost $100 (might break things). Safe changes cost $0. If the company spends $800 by week 3, credit limit is nearly exhausted—freeze experiments, only safe changes. If spending only $100/week, plenty of room to experiment. At end of month, unused balance expires (budget replenishes next month). The faster the company spends, the more conservative they must be.

- "Credit card limit" → Error budget
- "Risky deploys" → High-risk changes (new features, optimizations)
- "Experiments" → A/B tests, performance optimizations, infrastructure changes
- "Safe changes" → Bug fixes, rollbacks, documentation
- "Spending rate" → Burn rate (how fast SLI is degrading)

**Where this analogy breaks down:** Error budget isn't purchased monthly—it's a natural consequence of meeting SLA. If a service consistently beats SLA, they have excess budget every month. If they barely meet SLA, budget is tight.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Your service promised 99% uptime (SLA). Actual: 99.2% (better than promised). The extra 0.2% is "error budget"—failure the customer already accepted but didn't happen. You can spend this on experiments or risky changes.

**Level 2 — How to use it (junior developer):**
Check the SLI dashboard. If SLI is 99.2% and SLA is 99%, error budget is positive (0.2%). Safe to deploy. If SLI drops to 98.9%, budget is negative (you breached SLA). Freeze deployments until SLI recovers above 99%.

**Level 3 — How it works (mid-level engineer):**
Calculate error budget = SLA - SLI (monthly or quarterly, depending on window). Track burn rate = (budget_spent / days_elapsed). If burn_rate > (total_budget / period_days), you're on pace to breach SLA—freeze non-critical changes. If burn_rate < safe_rate, deploy aggressively. Implement alerting: if 50% of monthly budget spent by day 10, warn team. If 100% spent by day 25, escalate (breach imminent).

**Level 4 — Why it was designed this way (senior/staff):**
Error budget emerges from SRE (Google). It answers: "How much risk can we take?" Without it, teams are either too conservative (missing velocity goals) or too reckless (breaching SLA). Error budget makes risk quantified and discussable. Burn rate alerts let teams adjust deployment cadence in real-time. This aligns business (SLA compliance) with engineering (feature velocity). High burn rate signals "improve reliability or slow deployments." Low burn rate signals "we have capacity to innovate." Error budget also enables justified experimentation: "We have budget to test this idea," not "We hope this doesn't break."

---

### ⚙️ How It Works (Mechanism)

Error budget calculation and consumption:

```
PERIOD START (Monthly):
  SLA = 99.5% uptime (contractual)
  Month = 2,592,000 seconds

  Error Budget = (SLA × seconds_in_period)
               = 0.995 × 2,592,000 = 2,578,640 seconds "good"
               = (1 - 0.995) × 2,592,000 = 12,960 seconds downtime allowed

  Remaining Budget = 12,960 seconds (100%)

CONTINUOUS MEASUREMENT:
  Every hour, measure SLI (actual uptime)

  If SLI = 99.5%:
    Downtime this hour = 3,600 × 0.005 = 18 seconds
    Remaining Budget -= 18

  If SLI = 99.0% (incident):
    Downtime this hour = 3,600 × 0.01 = 36 seconds
    Remaining Budget -= 36

  If SLI = 100% (good):
    Downtime = 0
    Remaining Budget unchanged

BURN RATE CALCULATION:
  Burn Rate = Seconds_Spent / Days_Elapsed
  Safe Rate = Total_Budget / Days_in_Period

  If Burn Rate > Safe Rate × 1.5:
    "ALERT: Burning faster than safe; restrict deployments"

  If Burn Rate > Safe Rate × 2:
    "CRITICAL: Will breach SLA; freeze non-critical changes"

  If Burn Rate < Safe Rate * 0.5:
    "Budget recovery; can increase deployment frequency"

DEPLOYMENT DECISION:
  Risky Deploy Attempted:
    IF Remaining Budget > estimated_risk:
      ALLOW deploy
    ELSE:
      REJECT deploy (unless critical fix)

  Safe Deploy:
    ALWAYS ALLOW (no budget cost)

BUDGET RECOVERY:
  At end of month, budget resets
  Next month starts fresh
  Unused budget does NOT carry over
  (incentivizes using budget wisely)
```

**In Practice:**
If budget remaining is high (> 50%), team deploys multiple risky features/week. If low (< 20%), team only deploys critical fixes. If empty (< 5%), only emergency patches, all feature work paused.

---

### 🔄 The Complete Picture — End-to-End Flow

```
Service Operates
    ↓
SLI Measured (hourly or real-time)
    ↓
Compare SLI to SLA
    ↓
Calculate: Downtime_This_Period = (SLA - SLI) × seconds
    ↓
Update: Remaining_Budget -= Downtime_This_Period
    ↓
Calculate: Burn_Rate = Budget_Spent / Days_Elapsed
    ↓
Decision Point:
    Burn_Rate vs Safe_Rate comparison
    ├─ Burn Rate < Safe Rate: "Deploy confidently"
    ├─ Burn Rate = Safe Rate: "Deploy conservatively"
    └─ Burn Rate > Safe Rate: "Hold deployments, focus on reliability"

Deployment Request:
    IF Remaining_Budget > 0 AND Burn_Rate acceptable:
        ALLOW deployment
    ELSE:
        BLOCK deployment (unless critical)

At Month-End:
    Budget resets to SLA allowance
    New period begins
```

**What happens at scale:**
At 1M req/s, SLI is granular (per-endpoint, per-region, per-customer). Each endpoint has its own error budget. Deployment strategy becomes: "This endpoint's budget is low, delay this change. That endpoint's budget is high, deploy there."

---

### 💻 Code Example

Implementing error budget tracking and alerts:

**Example 1 — Error Budget Calculation:**

```python
from datetime import datetime, timedelta

class ErrorBudget:
    def __init__(self, sla_percentage=0.995, period_days=30):
        self.sla = sla_percentage
        self.period_days = period_days
        self.seconds_in_period = period_days * 86400
        self.total_budget = (1 - self.sla) * self.seconds_in_period
        self.spent = 0
        self.start_time = datetime.now()

    def record_downtime(self, seconds):
        """Record downtime (spending error budget)"""
        self.spent += seconds
        remaining = self.total_budget - self.spent
        burn_rate = self.spent / self.days_elapsed()
        safe_rate = self.total_budget / self.period_days

        print(f"Downtime: {seconds}s | Spent: {self.spent}s | Remaining: {remaining}s")
        print(f"Burn Rate: {burn_rate:.2f}s/day | Safe Rate: {safe_rate:.2f}s/day")

        return {
            "remaining": remaining,
            "burn_rate": burn_rate,
            "safe_rate": safe_rate,
            "can_deploy": remaining > 0 and burn_rate < safe_rate * 1.5
        }

    def days_elapsed(self):
        return (datetime.now() - self.start_time).days + 1

# Usage
budget = ErrorBudget(sla_percentage=0.995, period_days=30)

# Week 1: Normal operation
budget.record_downtime(1296)  # Good week

# Incident occurs
status = budget.record_downtime(1800)  # 30-min incident

if status["can_deploy"]:
    print("✓ Safe to deploy post-mortem fixes")
else:
    print("✗ Hold deployments until budget recovers")
```

**Example 2 — Prometheus Queries for Burn Rate:**

```promql
# Calculate error budget spent (SLA - SLI)
error_rate = 1 - (rate(requests_success[5m]) / rate(requests_total[5m]))
budget_spent = error_rate * 100

# Burn rate (seconds per day)
burn_rate = increase(budget_spent[24h]) / 1

# Safe rate (total budget / days in period)
safe_rate = (1 - 0.995) * 86400 / 30

# Alert if burn rate exceeds safe rate by 50%
alert: HighErrorBudgetBurnRate
  if: burn_rate > safe_rate * 1.5
  for: 1h
  annotations:
    summary: "Error budget burning fast: {{ $value | humanize }}s/day"
    action: "Consider freezing non-critical deployments"
```

**Example 3 — SLA/SLO/Error Budget YAML:**

```yaml
service: payment-api
sla:
  target: "99.5%"
  period: "30 days"
  budget_seconds: 12960 # (1 - 0.995) * 2,592,000

slo:
  target: "99.9%"
  alert_threshold: "99.8%"

error_budget_policy:
  burn_rate_thresholds:
    - "< 50% of safe rate": deploy_aggressively
    - "50-100% of safe rate": deploy_carefully
    - "> 100% of safe rate": deploy_only_critical_fixes
    - "> 150% of safe rate": freeze_all_deployments

  deployment_holds:
    - trigger: "90% of monthly budget spent"
      action: "Notify on-call, get approval for non-critical deploys"

    - trigger: "100% of monthly budget spent (SLA breached)"
      action: "Freeze all deployments except emergency patches"

  budget_recovery_window: "3 days of 100% SLI needed to unlock"
```

---

### ⚖️ Comparison Table

| Metric              | Error Budget                  | SLA               | SLO               | SLI              |
| ------------------- | ----------------------------- | ----------------- | ----------------- | ---------------- |
| **Definition**      | Available downtime per period | Contract promise  | Internal target   | Measured actual  |
| **Calculated from** | SLA - SLI                     | Customer contract | Business goals    | Monitoring       |
| **Used for**        | Deployment decisions          | Accountability    | Operations target | Trending         |
| **Example**         | 12,960 sec/month              | 99.5%             | 99.9%             | 99.73%           |
| **Granularity**     | Per-period                    | Monthly           | Monthly           | Hourly/Real-time |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| "Error budget = permission to be unreliable"      | No. Error budget is a safety margin—SLA is still the floor. Breaching SLA triggers refunds/penalties.                  |
| "If budget is empty, shut down the service"       | No. Empty budget means "freeze deployments," not shutdown. Service continues operating, but deployment velocity drops. |
| "Error budget can be "saved" for next month"      | No. Budget resets each period. Unused budget is wasted. Incentivizes spending it on useful experiments.                |
| "Error budget is an excuse to skip testing"       | No. Error budget funds deployment risk, not testing laziness. Well-tested changes spend less budget.                   |
| "Every service should have the same error budget" | No. Budget depends on SLA. Payment service (99.95% SLA) has tighter budget than internal tools (99% SLA).              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Budget Exhausted Too Fast (Weeks 1–2)**

**Symptom:**
Month started with 12,960 seconds budget. By week 2 (14 days), only 3,000 seconds remain. Burn rate unsustainable. Will breach SLA by week 3.

**Root Cause:**
Multiple incidents: bad deployment (1-hour outage), infrastructure failure (30-min cascade), then recovery issues. Each incident consumed budget faster than expected.

**Diagnostic Command:**

```bash
# Check burn rate vs. safe rate
burn_rate=$(curl monitoring/api/budget/burn-rate)
safe_rate=$((12960 / 30))  # ~432 sec/day

if [ $(echo "$burn_rate > $safe_rate * 1.5" | bc) -eq 1 ]; then
    echo "ALERT: Burn rate ($burn_rate) exceeds safe rate ($safe_rate)"
fi

# Drill into incident timeline
curl monitoring/api/incidents | grep -E "start|duration" | head -20
```

**Fix:**
Bad approach: "Hope incidents stop happening."
Good approach: (1) Investigate root causes of incidents. (2) Implement circuit breakers to prevent cascades. (3) Improve deployment testing (fewer bad deployments = less budget spent). (4) Add health checks and automatic rollbacks. (5) Educate team on risky changes (deploy during low-traffic windows, not peak).

**Prevention:**
Track incident trends. If burn rate consistently high, it signals infrastructure/code quality issues—address them, don't just freeze deployments.

---

**Failure Mode 2: Team Never Uses Budget (Over-Conservative)**

**Symptom:**
Month ends with 50% of budget unused. Team is afraid to deploy risky features. Experiments backlogged. Velocity stalled. Customers want faster innovation.

**Root Cause:**
Team doesn't trust error budget metric. "What if we're wrong about SLI measurement?" Team defaults to extreme caution: "Only deploy when absolutely certain."

**Diagnostic Command:**

```bash
# Check budget utilization
used_budget=$(curl monitoring/api/budget/spent)
total_budget=12960
utilization=$((used_budget * 100 / total_budget))

echo "Budget utilization: $utilization%"

if [ $utilization -lt 50 ]; then
    echo "WARNING: Budget underutilized; team may be over-conservative"
fi
```

**Fix:**
Bad approach: Force deployments to "use budget."
Good approach: (1) Validate error budget calculation is correct. (2) Build team confidence with successful low-risk deployments first. (3) Communicate: "Error budget exists so you CAN deploy." (4) Run blameless post-mortems—show that incidents are learning opportunities, not career risks. (5) Celebrate successful experiments.

**Prevention:**
Establish a "deployment culture" where error budget is expected to be used. Align incentives: "If you don't experiment, you can't innovate."

---

**Failure Mode 3: SLA Breach Not Understood as Budget Depletion**

**Symptom:**
SLI dropped to 99.2% (SLA was 99.5%). SLA breached. Customers call. Team doesn't realize "we spent all the budget and then exceeded it." Confusion: "How did we breach? We didn't deploy anything unusual."

**Root Cause:**
Monitoring gap: team didn't track error budget or burn rate. Infrastructure issue (not deployment) caused the breach. Team unaware until customers complained.

**Diagnostic Command:**

```bash
# Check SLA breach history
curl monitoring/api/sla-breaches | jq '.[] | {time, sli, sla, cause}' | tail -10

# Check if cause was infrastructure or deployment
curl monitoring/api/events | grep -E "deploy|incident|outage" | grep -B5 "sla-breach"
```

**Fix:**
Bad approach: "Blame the on-call engineer."
Good approach: (1) Implement continuous SLI and error budget dashboards. (2) Set SLO alerts BEFORE SLA breach (99.8% SLI threshold). (3) Establish escalation path: SLI < SLO → investigate. SLI < SLA → incident response. (4) Do post-mortems on infrastructure issues, not just deployments.

**Prevention:**
Monitor both SLI and error budget. If error budget is high but SLI dropped, suspect infrastructure. If error budget is low, suspect deployments or cascading incidents. Real-time alerts prevent surprise breaches.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLA/SLO/SLI` — error budget is derived from these
- `Monitoring` — how SLI (and thus error budget) is measured
- `Service Level` — defining what "acceptable" means

**Builds On This (learn these next):**

- `MTTR/MTBF` — incident recovery time affects error budget burn
- `Deployment Strategy` — error budget informs when to deploy
- `Incident Management` — incident frequency affects budget consumption

**Alternatives / Comparisons:**

- `Release Cadence` — error budget determines sustainable deployment frequency
- `Blast Radius` — limiting blast radius reduces error budget consumption per incident

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Quantified downtime allowed per      │
│              │ period; difference between SLA       │
│              │ commitment and actual SLI            │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Deployment decisions based on fear   │
│ SOLVES       │ instead of data; no principled way   │
│              │ to balance velocity and reliability  │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Budget consumption indicates risk    │
│              │ (high burn = fix reliability);       │
│              │ aligns business (SLA) with          │
│              │ engineering (velocity)              │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Any SLA-critical service; when       │
│              │ deployment velocity matters; when    │
│              │ willing to accept calculated risk    │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ No SLA defined; service not          │
│              │ customer-facing; downtime OK        │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Velocity, principled risk] vs       │
│              │ [operational overhead, team buy-in] │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Meet SLA, spend the buffer on       │
│              │ innovation; run out, pause velocity."│
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Burn Rate → Incident Response →      │
│              │ Deployment Strategies               │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service SLA = 99.9% (monthly). You have 10 features ready to ship, but error budget is nearly exhausted (< 5% remaining). One feature is high-risk (5% chance of 1-hour outage). Another is low-risk (0.1% chance of 10-minute outage). Which do you deploy, and why?

**Q2.** You notice your burn rate is 1.5x the safe rate. Actual incidents (infrastructure failures) caused 60% of the burn, and deployments caused 40%. Should you freeze all deployments, or focus on preventing incidents? What's the tradeoff?
