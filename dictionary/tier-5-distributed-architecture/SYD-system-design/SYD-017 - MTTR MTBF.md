---
id: SYD-017
title: MTTR MTBF
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-015
used_by:
related: SYD-015, SYD-016, SYD-022
tags:
  - reliability
  - intermediate
  - observability
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /syd/mttr-mtbf/
---

# SYD-017 - MTTR MTBF

⚡ TL;DR - Two complementary metrics: MTBF (Mean Time Between Failures) measures how often things break, MTTR (Mean Time To Recovery) measures how fast you fix them. Together they determine system reliability and SLA feasibility.

| #692            | Category: System Design                         | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Monitoring, Incident Management, Operations     |                 |
| **Used by:**    | SRE, Incident Response, Reliability Engineering |                 |
| **Related:**    | Error Budget, Disaster Recovery, Observability  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service keeps failing. Team scrambles. "When will it be fixed?" Unknown. No idea how often it fails or how long repairs take. Customers furious. Leadership asks, "Why is reliability bad?" Team: "We don't know." No metrics to improve.

**THE BREAKING POINT:**
Without quantifying failures and recovery times, reliability improvements are guesswork.

**THE INVENTION MOMENT:**
"What if we measured: How often do systems break (MTBF)? How fast do we fix them (MTTR)? Then reliability = less frequent breaks + faster fixes."

**EVOLUTION:**
MTBF originated in military aviation in the 1940s - the US Army Air Forces tracked aircraft failure rates to predict maintenance intervals. MTTR emerged as its complement: once MTBF was known, reducing MTTR became the other lever for improving availability. Both metrics were adopted by telecommunications in the 1960s-70s, then by IT infrastructure in the 1990s. Modern SRE practice extends the concepts to mean time to detect (MTTD), mean time to acknowledge (MTTA), and mean time to resolve (MTTR) - breaking incident response into measurable phases. The discipline evolved from hardware reliability engineering to software service reliability management.

---

### 📘 Textbook Definition

- **MTBF (Mean Time Between Failures):** Average time that elapses between one failure and the next failure of a component or system. Higher is better (less frequent failures).
- **MTTR (Mean Time To Recovery):** Average time it takes to restore a system to full operational status after a failure. Lower is better (quicker recovery).

Mathematically: **Availability = MTBF / (MTBF + MTTR)**

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MTBF = how often things break. MTTR = how fast we fix. Both matter equally.

**One analogy:**

> A power grid fails once every 2 years on average (MTBF = 2 years). When it fails, restoration takes 4 hours on average (MTTR = 4 hours). Availability = 2 years / (2 years + 4 hours) ≈ 99.977%. A competitor fails once every 1 year (worse MTBF) but fixes in 30 min (better MTTR). Their availability ≈ 99.994%. Both can achieve high availability: one by preventing failures, one by recovering fast.

**One insight:**
You can improve availability by either preventing failures (increase MTBF) or recovering faster (decrease MTTR). Real systems do both.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Failures happen (hardware breaks, software bugs, network partitions)
2. Recovery isn't instant (diagnosis, fix, deployment, verification take time)
3. Availability depends on both failure frequency and recovery speed
4. Different components have different failure characteristics

**DERIVED DESIGN:**
In a system with N independent components, each with MTBF_i and MTTR_i:

- System MTBF ≈ 1 / (sum of component failure rates)
- System MTTR ≈ time to detect + diagnose + fix + deploy + verify

To improve system MTBF: add redundancy, reduce complexity, improve code quality.
To improve system MTTR: better monitoring (faster detection), automated rollbacks, pre-tested fixes.

**THE TRADE-OFFS:**
**Gain:** Quantified reliability. Clear roadmap for improvement (prevent vs. recover faster). Predictable availability.

**Cost:** Calculating accurate MTBF/MTTR requires historical incident data. Early-stage services have limited data. False sense of precision if underlying data is poor.

---

### 🧪 Thought Experiment

**SETUP:**
Two APIs. Both claim "99.9% availability."

**API-A:**

- MTBF: 1,000 hours between failures
- MTTR: 0.9 hours to recover
- Availability = 1,000 / (1,000 + 0.9) = 99.91%

**API-B:**

- MTBF: 500 hours between failures (twice as often)
- MTTR: 0.05 hours to recover (12 minutes, fast response)
- Availability = 500 / (500 + 0.05) = 99.99%

**THE INSIGHT:**
API-A prevents failures but recovers slowly. API-B fails more but recovers fast. Both achieve similar availability, but via different strategies. API-A is "prevention-focused." API-B is "recovery-focused."

**Practical implication:** If you have limited resources:

- Limited ops budget → focus on MTTR (automated recovery, good monitoring)
- Limited dev budget → focus on MTBF (code review, testing, redundancy)

---

### 🧠 Mental Model / Analogy

> An automotive factory produces 1,000 cars/day. Occasionally, the assembly line breaks (failure). On average, it breaks once every 2 weeks (MTBF = 14 days = 336 hours). When it breaks, repair takes 2 hours on average (MTTR = 2 hours). During those 2 hours, 0 cars are produced. Factory throughput = 1,000 cars/day × (1 - 2/(24×14)) ≈ 994 cars/day (99.4% uptime). To improve output, the factory can: (1) prevent breakdowns (better maintenance, upgrade equipment) or (2) repair faster (keep spare parts, cross-train technicians). Both approaches increase throughput.

- "Assembly line" → system component
- "Breaks" → failure
- "14 days between breaks" → MTBF
- "2 hours to repair" → MTTR
- "Throughput" → availability
- "Better maintenance" → reduce MTBF
- "Repair faster" → reduce MTTR

**Where analogy breaks down:** Software systems can recover instantly (swap to replica), while physical systems need physical repair time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Servers fail sometimes. MTBF is "on average, how often." MTTR is "on average, how long to fix." High MTBF + low MTTR = reliable system.

**Level 2 - How to use it (junior developer):**
Your service's SLA is 99% uptime. That means ~7.2 hours downtime/month allowed. If MTBF is 100 hours and MTTR is 4 hours, availability = 100/(100+4) = 96%, which is worse than SLA. Decision: improve MTBF (prevent failures) or improve MTTR (recover faster).

**Level 3 - How it works (mid-level engineer):**
Collect incident data over several months. For each incident: log failure time, detection time, diagnosis time, resolution time. MTBF = total uptime / number of failures. MTTR = sum of (end_time - start_time) / number of failures. Availability = MTBF / (MTBF + MTTR). Compare to SLA. If availability < SLA, identify bottlenecks: are failures too frequent (MTBF problem) or recovery too slow (MTTR problem)? Invest accordingly.

**Level 4 - Why it was designed this way (senior/staff):**
MTBF/MTTR emerge from reliability engineering. They quantify two dimensions of reliability: prevention (MTBF) and recovery (MTTR). Different systems need different strategies. High-uptime systems maximize both. Systems in early stages focus on MTTR (recover fast, iterate). Mature systems focus on MTBF (prevent rare failures). MTBF/MTTR also guide team structure: ops focuses on MTTR (incident response), engineering focuses on MTBF (code quality).

---

### ⚙️ How It Works (Mechanism)

MTBF/MTTR calculation and application:

```
INCIDENT LOGGING (Continuous):
  Incident_1:
    - Failure Start: 2024-01-15 14:30
    - Detection: 14:35 (5 min)
    - Resolution: 15:10 (35 min total MTTR)
    - Failure End: 15:10
    - Time Since Previous Failure: 720 hours (MTBF so far)

  Incident_2:
    - Failure Start: 2024-01-29 09:00
    - Detection: 09:02
    - Resolution: 09:47 (47 min total MTTR)
    - Time Since Previous: 336 hours (14 days)

CALCULATION (Monthly):
  Number of Failures: 2
  Uptime: Total_Minutes - (35 + 47) = Total_Minutes - 82

  MTBF = Uptime / Number_of_Failures
         = (Total_Uptime_Minutes) / 2
         = (30 days × 1440 min - 82) / 2
         = (43,200 - 82) / 2
         = 21,559 minutes
         = ~358 hours

  MTTR = Total_Downtime_Minutes / Number_of_Failures
       = 82 / 2
       = 41 minutes

  Availability = MTBF / (MTBF + MTTR)
               = 358 / (358 + 0.68)
               = 99.81%

DECISION POINT:
  SLA = 99.9% (required)
  Current = 99.81% (below target)

  Gap = 0.09 percentage points

  Option A (Improve MTBF):
    Increase MTBF to 500 hours (prevent 1 failure)
    New Availability = 500 / (500 + 0.68) = 99.86%
    Still below SLA. Need more prevention.

  Option B (Improve MTTR):
    Decrease MTTR to 10 minutes (faster recovery, automation)
    New Availability = 358 / (358 + 0.167) = 99.95%
    Above SLA! Cost: automate incident response.

  Option C (Both):
    MTBF = 500 hours + MTTR = 10 minutes
    Availability = 500 / (500 + 0.167) = 99.97%
    Well above SLA.
```

**Trend Analysis Over Time:**

```
Month 1: MTBF = 358h, MTTR = 41min, Availability = 99.81%
Month 2: MTBF = 400h, MTTR = 35min, Availability = 99.87% (improving)
Month 3: MTBF = 450h, MTTR = 25min, Availability = 99.94% (approaching goal)
Month 4: MTBF = 480h, MTTR = 15min, Availability = 99.98% (goal met)
```

**At Scale:**
Track MTBF/MTTR per component (database, API, cache, message queue). Some components might have high MTBF but low MTTR (rare but slow to recover); others low MTBF but high MTTR (frequent but quick recovery). Invest in the weakest component.

---

### 🔄 The Complete Picture - End-to-End Flow

```
System Running Normally
    ↓
Failure Occurs (bug, hardware, network)
    ↓
Detection (monitoring alert, customer complaint)
    ↓ (Detection Time)
Diagnosis (root cause analysis)
    ↓ (Diagnosis Time)
Fix Applied (patch, rollback, manual intervention)
    ↓ (Resolution Time)
System Restored
    ↓
Calculate: MTTR = Detection + Diagnosis + Resolution
    ↓
Time Until Next Failure
    ↓
Calculate: MTBF = Time from last recovery to next failure
    ↓
Aggregate Monthly:
    MTBF = (Total Uptime) / (Number of Failures)
    MTTR = (Total Downtime) / (Number of Failures)
    Availability = MTBF / (MTBF + MTTR)
    ↓
Compare to SLA
    ├─ Above SLA: "On target"
    └─ Below SLA: "Need to improve MTBF or MTTR"
```

---

### 💻 Code Example

Calculating and tracking MTBF/MTTR:

**Example 1 - Incident Data Collection:**

```python
from datetime import datetime, timedelta

class Incident:
    def __init__(self, name, failure_start, detection_time, resolution_time):
        self.name = name
        self.failure_start = datetime.fromisoformat(failure_start)
        self.detected = self.failure_start + timedelta(minutes=detection_time)
        self.resolved = self.detected + timedelta(minutes=resolution_time)
        self.mttr = (self.resolved - self.failure_start).total_seconds() / 60

    def __repr__(self):
        return f"{self.name}: MTTR={self.mttr:.0f}min"

incidents = [
    Incident("DB Connection Pool Exhaustion", "2024-01-15T14:30", 5, 30),
    Incident("Memory Leak in Worker", "2024-01-29T09:00", 2, 45),
    Incident("Cache Timeout Cascade", "2024-02-10T20:15", 8, 20),
]

# Calculate metrics
total_mttr = sum(i.mttr for i in incidents)
avg_mttr = total_mttr / len(incidents)

uptime_hours = (30 * 24) - (total_mttr / 60)
mtbf = (uptime_hours * 60) / len(incidents)  # minutes

availability = mtbf / (mtbf + avg_mttr)

print(f"Incidents: {len(incidents)}")
print(f"Avg MTTR: {avg_mttr:.0f} minutes")
print(f"MTBF: {mtbf:.0f} minutes ({mtbf / 60:.0f} hours)")
print(f"Availability: {availability * 100:.2f}%")
```

**Example 2 - Prometheus Metrics:**

```prometheus
# Define custom metrics
mttr_minutes = Gauge('mttr_minutes', 'Mean Time To Recovery', ['service'])
mtbf_hours = Gauge('mtbf_hours', 'Mean Time Between Failures', ['service'])
availability = Gauge('availability_percent', 'System Availability', ['service'])

# After each incident resolution:
incident_duration = (resolved - started).total_seconds() / 60
mttr_minutes.labels(service='payment-api').set(incident_duration)

# Periodically calculate MTBF from uptime and incident count
total_uptime = 30 * 24 * 60  # minutes in 30 days
num_incidents = 3
mtbf = total_uptime / num_incidents
mtbf_hours.labels(service='payment-api').set(mtbf / 60)

# Calculate availability
avg_mttr = sum_of_mttr / num_incidents
calculated_availability = (mtbf / (mtbf + avg_mttr)) * 100
availability.labels(service='payment-api').set(calculated_availability)
```

**Example 3 - SLA/MTBF/MTTR YAML Configuration:**

```yaml
service: payment-api

sla:
  target_availability: "99.9%"
  period: "30 days"

reliability_targets:
  mtbf_hours: 400
  mttr_minutes: 15
  implied_availability: 99.94%

incident_tracking:
  critical_threshold: "MTTR > 30 minutes"
  warning_threshold: "MTTR > 15 minutes"

alerting:
  - name: "High MTTR"
    condition: "MTTR > 20 minutes"
    action: "Investigate incident response delays"

  - name: "Declining MTBF"
    condition: "MTBF trending down"
    action: "Increase testing, code review, monitoring"

improvement_roadmap:
  phase_1: "Improve MTTR to 10 min (automate detection/response)"
  phase_2: "Improve MTBF to 600 hours (reduce failure rate)"
  phase_3: "Achieve 99.99% availability (both metrics optimized)"
```

---

### ⚖️ Comparison Table

| Aspect         | MTBF                                      | MTTR                                  | Availability Impact |
| -------------- | ----------------------------------------- | ------------------------------------- | ------------------- |
| **Meaning**    | Frequency of failures                     | Speed of recovery                     | Combined effect     |
| **Improve by** | Code quality, testing, redundancy         | Automation, monitoring, runbooks      | Both strategies     |
| **Effort**     | High (prevent failures)                   | Medium (optimize recovery)            | Varies              |
| **Example**    | 500 hours between failures                | 10 minutes to fix                     | 99.97%              |
| **SLA Impact** | Critical (frequent failures = low uptime) | Critical (slow recovery = low uptime) | Both matter equally |

**Real-world example:**

- Payment API: MTBF = 1000h, MTTR = 5min → 99.99% (prevention-focused)
- Logging Service: MTBF = 100h, MTTR = 1min → 99.85% (recovery-focused)
- Best-in-class: MTBF = 5000h, MTTR = 2min → 99.999% (both optimized)

---

### ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "High MTBF is all that matters" | No. Both MTBF and MTTR matter equally for availability. A system with MTBF = 1000h and MTTR = 100min can have worse availability than MTBF = 100h and MTTR = 1min. |
| "MTTR can be arbitrarily low"   | No. Detection, diagnosis, and fix all take time. Automated recovery can reduce MTTR to 1-5 min, but near-zero is unrealistic.                                      |
| "MTBF increases forever"        | No. As systems age, hardware wears out, complexity grows. MTBF often plateaus or degrades. Constant improvement needed.                                            |
| "MTBF/MTTR determine SLA alone" | Incomplete. They contribute to availability, but SLA also includes latency, error rates, and other dimensions.                                                     |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Increasing Failure Frequency (MTBF Degrading)**

**Symptom:**
January: 2 incidents. February: 4 incidents. March: 6 incidents. MTBF trending down (from 360 hours to 120 hours). SLA will be breached soon.

**Root Cause:**
More traffic → more load → exposing latent bugs. Or code quality degraded (less rigorous reviews). Or infrastructure aging (hardware failures increasing).

**Diagnostic Command:**

```bash
# Check incident trend
curl monitoring/api/incidents/monthly | jq '.[] | {month, count}' | tail -6

# Check if caused by traffic or bugs
curl monitoring/api/errors | jq '.[] | {time, error_type, frequency}' | head -10

# Check infrastructure health
curl monitoring/api/infrastructure | jq '.[] | {component, error_count}'
```

**Fix:**
Bad approach: "We're just unlucky."
Good approach: (1) Increase code review rigor. (2) Add more testing (unit, integration, chaos). (3) Monitor error rates per component-identify the most broken one. (4) Upgrade or replace failing infrastructure. (5) Reduce load (cache, CDN, rate limiting) if traffic is the cause.

**Prevention:**
Establish MTBF SLO (e.g., "never drop below 200 hours"). Alert if trending down. Investigate immediately. Don't wait for SLA breach.

---

**Failure Mode 2: Slow Recovery (MTTR Increasing)**

**Symptom:**
January: avg MTTR = 20 minutes. February: avg MTTR = 30 minutes. March: avg MTTR = 45 minutes. Incidents are happening at normal rate, but recovery is slower.

**Root Cause:**
Runbooks are outdated. Team unfamiliar with new infrastructure. Manual processes not automated. On-call rotation has junior engineers.

**Diagnostic Command:**

```bash
# Check MTTR trend
curl monitoring/api/incidents | jq 'group_by(.month) | .[] | {month, avg_mttr: (map(.mttr) | add / length)}' | tail -6

# Check who's on-call during slow incidents
curl monitoring/api/incidents | jq '.[] | {time, assigned_engineer, mttr}' | sort_by(.mttr) | tail -5

# Check detection time vs. resolution time breakdown
curl monitoring/api/incidents | jq '.[] | {name, detection_time, diagnosis_time, resolution_time}' | head -10
```

**Fix:**
Bad approach: "Hire faster engineers."
Good approach: (1) Automate incident response (alerts, auto-rollback, health checks). (2) Update runbooks with latest infrastructure. (3) Increase on-call training and practice (game-days, chaos engineering). (4) Reduce detection time (better monitoring). (5) Pre-create fix playbooks for common issues.

**Prevention:**
Track MTTR per incident type. If a class of incidents consistently slow to resolve, create automated fix. Review on-call effectiveness quarterly-are specific people slower to respond? Provide training.

---

**Failure Mode 3: Compounding: Frequent + Slow = SLA Disaster**

**Symptom:**
MTBF = 100 hours, MTTR = 30 minutes. Availability = 100 / (100 + 0.5) = 99.50%. SLA = 99.9%. Missing target by 0.4 percentage points. But worse: both metrics trending wrong. MTBF declining, MTTR increasing. Downward spiral.

**Root Cause:**
Service under-invested in reliability. Architecture fragile. No monitoring. Team reactive (fix only when broken). Vicious cycle: failures cause stress → poor decision-making → more failures.

**Diagnostic Command:**

```bash
# Analyze both trends
mtbf_jan=$(curl monitoring/api/incidents | jq --arg month "Jan" '.[] | select(.month == $month)' | jq -s 'length')
mtbf_mar=$(curl monitoring/api/incidents | jq --arg month "Mar" '.[] | select(.month == $month)' | jq -s 'length')

mttr_jan=$(curl monitoring/api/incidents | jq --arg month "Jan" '.[] | select(.month == $month) | .mttr' | jq -s 'add / length')
mttr_mar=$(curl monitoring/api/incidents | jq --arg month "Mar" '.[] | select(.month == $month) | .mttr' | jq -s 'add / length')

echo "MTBF trend: Jan=$mtbf_jan, Mar=$mtbf_mar (negative = bad)"
echo "MTTR trend: Jan=$mttr_jan, Mar=$mttr_mar (positive = bad)"
```

**Fix:**
Bad approach: "Let's just work harder."
Good approach: (1) Declare "reliability sprint"-pause feature work. (2) Address MTBF first (prevent fires before putting them out). (3) Implement monitoring and alerting (reduce MTTR detection time). (4) Automate incident response (reduce MTTR overall). (5) Invest in redundancy and fault-tolerance. (6) Build observability culture.

**Prevention:**
Never ignore MTBF/MTTR trends. If both degrading, escalate immediately. Establish SLOs for each: "MTBF > 200 hours" and "MTTR < 15 minutes." Alert if either violated.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-015 - SLA SLO SLI]] - MTBF/MTTR determine achievable SLA

**Builds On This (learn these next):**
- [[SYD-022 - Disaster Recovery]] - DR planning requires knowing MTTR for major failures

**Alternatives / Comparisons:**
- [[SYD-018 - RTO RPO]] - similar metrics for disaster recovery scenarios
- [[SYD-016 - Error Budget]] - error budget burn rate is related to MTBF frequency

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ MTBF = failure frequency; MTTR =     │
│              │ recovery speed; together determine   │
│              │ availability                         │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Unclear which reliability issues to  │
│ SOLVES       │ fix: prevent failures or recover     │
│              │ faster? No data-driven priority.     │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Availability = MTBF / (MTBF+MTTR);  │
│              │ both matter equally; focus on        │
│              │ weakest link                         │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Production services; tracking        │
│              │ reliability; informing investment    │
│              │ priorities                           │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Early-stage products (limited data); │
│              │ internal tools; prototypes           │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Quantified priorities] vs           │
│              │ [incomplete data, measurement effort]│
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Fix failures less often AND faster."│
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ MTBF → Reliability Eng; MTTR →      │
│              │ Incident Response; Both → SLA       │
└──────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decompose a complex outcome into its contributing factors to identify where to invest. Availability = MTBF / (MTBF + MTTR). You can improve availability by reducing either factor. This decomposition principle applies everywhere: delivery time = queue time + processing time (Little's Law), customer satisfaction = product quality * support quality x price, code review cycle time = time-to-review + time-to-address-feedback. Decompose first, then invest in the factor with highest leverage.

**Where else this pattern appears:**
- **Incident response phases:** Breaking MTTR into MTTD + MTTA + TTR reveals which phase is the bottleneck - often detection takes longer than the actual fix.
- **Deployment pipeline:** Total deploy time = build time + test time + deploy time + validation time - each phase can be optimised independently.
- **Customer support:** Resolution time = queue time + diagnosis time + fix time + verification - decomposing reveals where to invest in automation.

---

### 💡 The Surprising Truth

Reducing MTTR below a certain threshold is more effective than eliminating failures entirely. A system with MTBF = 100 hours and MTTR = 1 minute achieves 99.998% availability. The marginal cost of eliminating the last 0.01% of failures grows exponentially (chaos engineering, full Byzantine fault tolerance), while reducing MTTR from 30 minutes to 3 minutes is often a process and tooling problem - achievable at low cost with better alerting, runbooks, and deployment automation. This is why Google's SRE teams invest more in detection and response tooling than in preventing every failure.

---

### 🧠 Think About This Before We Continue

**Q1.** Your API has SLA = 99% (7.2 hours downtime/month allowed). Current MTBF = 200 hours, MTTR = 30 minutes. Calculate availability. Are you meeting SLA? What needs to improve: MTBF or MTTR?

*Hint:* Think about the formula: Availability = MTBF / (MTBF + MTTR). Calculate current availability and identify whether MTBF improvement or MTTR improvement yields a larger gain per dollar invested.

**Q2.** You have a choice: invest  to reduce MTBF to 300 hours (prevent failures better) OR invest  to reduce MTTR to 10 minutes (recover faster). Which investment yields higher availability gain, and why?

*Hint:* Think about the math: which investment makes a bigger change to the MTBF/(MTBF+MTTR) formula? Explore the diminishing returns of MTBF improvement when MTBF is already high compared to MTTR reduction when MTTR is the dominant term.

**Q3 (Scale):** Your service handles 10,000 req/sec. An incident takes 45 minutes to resolve and occurs once per month. Post-mortem: detection took 15 min, triage took 15 min, fix took 15 min. Which phase should you invest in reducing, and how does it affect your SLA?

*Hint:* Think about which phase is most amenable to technical improvement (monitoring alert speed vs debugging tooling vs deployment speed) versus process improvement (runbooks, escalation paths). Explore which 15-minute phase would have the largest availability impact if halved.
