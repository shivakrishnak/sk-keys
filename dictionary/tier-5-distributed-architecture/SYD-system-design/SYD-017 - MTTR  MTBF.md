---
id: SYD-017
title: "MTTR / MTBF"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-015
used_by: ""
related: SYD-015, SYD-016, SYD-018, SYD-003
tags:
  - architecture
  - reliability
  - operations
  - site-reliability-engineering
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /syd/mttr-mtbf/
---

# SYD-017 - MTTR / MTBF

⚡ TL;DR - MTBF measures how often failures happen;
MTTR measures how fast you recover. Both drive
availability: Availability = MTBF / (MTBF + MTTR).
In modern distributed systems, improving MTTR (faster
recovery) often yields better availability than
improving MTBF (reducing failure frequency).

| #017 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SLA / SLO / SLI | |
| **Used by:** | (none - reliability metrics) | |
| **Related:** | SLA / SLO / SLI, Error Budget, RTO / RPO, Availability | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team says: "Our service has 99.9% uptime." But they
cannot answer: how many incidents happened last month?
How long did each last? Was the uptime number driven
by many short incidents or few long ones? Two services
can have identical availability numbers but very
different operational profiles - one fails rarely and
recovers slowly; one fails frequently and recovers
instantly. Without MTBF and MTTR, these look identical.
But they demand completely different investment
strategies to improve.

**THE BREAKING POINT:**
A single availability percentage hides the failure
pattern. A system with 99.9% availability could have:
- Pattern A: 1 incident per year, 8.7 hours long
- Pattern B: 100 incidents per year, 5.2 minutes each

These have identical availability but different root
causes, different user impact, and different solutions.
MTBF and MTTR decompose availability into its two
independent dimensions.

---

### 📘 Textbook Definition

**MTBF (Mean Time Between Failures):** The average
time between the end of one failure and the start of
the next. A measure of how reliable the system is -
how often it fails. Higher MTBF = more reliable.
MTBF = total_operational_time / number_of_failures.

**MTTR (Mean Time To Recover / Repair):** The average
time from when a failure is detected to when the
service is restored to normal operation. A measure
of how fast the team can respond and recover. Lower
MTTR = faster recovery.
MTTR = total_downtime / number_of_failures.

**Availability relationship:**
`Availability = MTBF / (MTBF + MTTR)`

At MTBF=8760h (1 year) and MTTR=8.76h:
`Availability = 8760 / (8760 + 8.76) = 99.9%`

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MTBF measures how often failures happen; MTTR measures
how quickly you fix them. Both determine availability.

**One analogy:**
> A car:
> - MTBF: how often the car breaks down
>   (once every 50,000 miles = high MTBF = reliable)
> - MTTR: how long it takes to fix it
>   (3 hours at the garage = MTTR = 3 hours)
>
> You can have a very reliable car (high MTBF) that
> takes forever to fix (high MTTR), or an unreliable
> car (low MTBF) that is fixed instantly (low MTTR).
> Your availability depends on both.

**One insight:**
In cloud-native systems, it is often easier and more
impactful to reduce MTTR (improve alerting, runbooks,
auto-recovery) than to reduce MTBF (prevent failures).
Failures in distributed systems are inevitable; fast
recovery is achievable by design.

---

### 🔩 First Principles Explanation

**THE AVAILABILITY EQUATION:**

```
Availability = MTBF / (MTBF + MTTR)

MTBF = 100 hours, MTTR = 1 hour:
  Availability = 100 / 101 = 99.01%

MTBF = 100 hours, MTTR = 0.1 hours (6 min):
  Availability = 100 / 100.1 = 99.9%

MTBF = 1000 hours, MTTR = 1 hour:
  Availability = 1000 / 1001 = 99.9%

Same availability, very different operational profiles.
Option 1: fail every 100 hours, recover in 6 minutes.
Option 2: fail every 1000 hours, recover in 1 hour.
```

**WHICH TO OPTIMIZE:**
Improving MTBF by 10x takes 10x longer to see the
same availability improvement that 10x MTTR reduction
gives - because MTBF improvements require deeper
reliability work (eliminating failure causes) while
MTTR improvements are often achievable through process
and tooling (better runbooks, automated recovery,
faster alerts).

**Practical guide:**

```
If MTTR >> MTBF: system fails often and recovers slowly
  → Fix MTTR first (runbooks, auto-recovery)
  → Then fix MTBF (root cause elimination)

If MTBF >> MTTR: system is reliable but slow to recover
  → Acceptable if MTBF is very high
  → If MTBF is still too low: invest in prevention

Rule of thumb: MTTR of < 5 minutes means availability
is primarily driven by MTBF, not recovery speed.
```

**RELATED METRICS:**
- **MTTA (Mean Time To Acknowledge):** Time from failure
  to an engineer acknowledging the alert. High MTTA =
  alerting problems or pager fatigue. First step in
  reducing MTTR.
- **MTTD (Mean Time To Detect):** Time from failure
  to detection by monitoring. High MTTD = monitoring
  gaps. Hidden failures burn error budget silently.
- **MTTF (Mean Time To Failure):** Similar to MTBF
  but counts from the start of operation, not the
  end of the last failure. MTBF = MTTF for repairable
  systems with uniform failure rates.

**THE TRADE-OFFS:**
**MTBF improvement:** Deeper engineering investment
(redundancy, better testing, code quality); takes
longer to see results; pays off for systems with
catastrophic failures.
**MTTR improvement:** Process and tooling investment
(runbooks, auto-recovery, better observability);
faster to implement; pays off for systems with
frequent small failures.

---

### 🧪 Thought Experiment

**SCENARIO: Same availability, different investment paths**

Both services have 99.9% availability (43.2 min/month
downtime). Your team has a $200k engineering budget
to improve reliability.

**Service A profile:**
MTBF = 30 days (fails once a month)
MTTR = 43 minutes (takes a long time to diagnose)

**Service B profile:**
MTBF = 2 days (fails 15 times a month)
MTTR = ~3 minutes (fast automated recovery)

**Investment options:**
- Option X: Improve alerting + runbooks → MTTR from
  43 min to 10 min (service A)
  New availability = 30 days / (30 days + 10 min)
  = 99.977%

- Option Y: Add circuit breaker + retry → MTBF from
  2 days to 10 days (service B)
  New availability = 10 days / (10 days + 3 min)
  = 99.98%

Both options give similar improvement. For Service A,
the bottleneck was MTTR (slow diagnosis). For Service B,
the bottleneck was MTBF (frequent failures). Same
availability number; completely different optimal
investments.

**THE INSIGHT:**
Know your system's MTBF and MTTR before deciding
where to invest. If MTTR is high, invest in
observability and runbooks first. If MTBF is low,
invest in failure prevention (redundancy, better
testing, chaos engineering to find hidden failure modes).

---

### 🧠 Mental Model / Analogy

> MTBF and MTTR are like the two independent dimensions
> of a restaurant's service quality:
> - MTBF is like "how often orders are incorrect"
>   (lower frequency = better)
> - MTTR is like "how fast the restaurant fixes the
>   wrong order" (shorter time = better)
>
> A restaurant can have many order mistakes that
> are fixed in 30 seconds (low MTBF, low MTTR).
> Or rare mistakes that take 10 minutes to fix
> (high MTBF, high MTTR). Customer experience
> depends on both: frequency × duration = total
> dissatisfaction time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
MTBF: how often the system breaks. MTTR: how fast
we fix it when it does. Both determine how available
the service is.

**Level 2 - How to use it (junior developer):**
Track incidents in an incident management tool
(PagerDuty, Opsgenie, Jira). After each incident,
record: start time, end time, time acknowledged.
At month end: MTBF = total uptime / # incidents;
MTTR = total downtime / # incidents.

**Level 3 - How it works (mid-level engineer):**
Both metrics are means - they can be misleading.
A P0 incident lasting 4 hours and 10 P1s lasting
10 minutes each produce different MTTR distributions.
Track percentiles (p50, p90, p99 MTTR) to understand
the tail of recovery time. High p99 MTTR indicates
hard-to-diagnose failure modes.

**Level 4 - Why it was designed this way (senior/staff):**
MTTR decomposition: MTTD (detection) + MTTA
(acknowledgement) + investigation time + fix time
+ verification time. Each component has different
optimal interventions. Better monitoring reduces MTTD.
Better on-call process reduces MTTA. Better runbooks
reduce investigation time. Better deployment tooling
reduces fix time (rollback in 2 min, not 20 min).
Knowing which component dominates guides investment.

**Level 5 - Mastery (distinguished engineer):**
MTBF in distributed systems is often misleading because
"failure" is ambiguous. Is a partial failure (one of
5 servers down, load balancer routing around it,
users unaffected) an "incident"? Is a performance
degradation (p99 latency 2x, but success rate 99.9%)
an "incident"? How you define a failure determines
your MTBF. In production, SLO-based incident
definition is cleaner: an "incident" is any time
period when the SLO was breached. This makes MTBF
and MTTR directly tied to user experience, not
infrastructure events.

---

### ⚙️ How It Works (Mechanism)

**MTTR decomposition - where time is lost:**

```
┌──────────────────────────────────────────────────────┐
│ MTTR = MTTD + MTTA + Time-to-Diagnose + Time-to-Fix │
│        + Time-to-Verify                              │
│                                                      │
│ Incident timeline:                                   │
│                                                      │
│ 14:00 ─ Failure occurs (DB query timeout)           │
│         MTTD starts                                  │
│ 14:07 ─ Alert fires (7 min = MTTD)                 │
│         MTTA starts                                  │
│ 14:15 ─ On-call acknowledges (8 min = MTTA)        │
│         Diagnosis starts                             │
│ 14:35 ─ Root cause found: index dropped (20 min)   │
│         Fix starts                                   │
│ 14:40 ─ Index recreated. Monitoring green. (5 min) │
│         Verify                                       │
│ 14:45 ─ Verified. All-clear. (5 min)               │
│                                                      │
│ MTTR for this incident = 45 minutes                 │
│ Breakdown: MTTD=7, MTTA=8, Diagnose=20, Fix=5,     │
│            Verify=5                                  │
│                                                      │
│ Biggest opportunity: Diagnosis (20 min)             │
│ Invest in: better dashboards, runbooks,             │
│            pre-built queries for common failures    │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Incident tracking to calculate MTBF/MTTR**
```python
# Calculate MTBF and MTTR from incident history
from datetime import datetime, timedelta
from statistics import mean, median

incidents = [
    {"start": datetime(2024, 1, 1, 14, 0),
     "end":   datetime(2024, 1, 1, 14, 45)},
    {"start": datetime(2024, 1, 8, 9, 30),
     "end":   datetime(2024, 1, 8, 9, 38)},
    {"start": datetime(2024, 1, 21, 22, 0),
     "end":   datetime(2024, 1, 22, 0, 30)},
]

# Calculate downtime per incident
downtimes = [
    (i["end"] - i["start"]).total_seconds() / 60
    for i in incidents
]

# MTTR = mean downtime per incident (in minutes)
mttr = mean(downtimes)
print(f"MTTR (mean): {mttr:.1f} minutes")
print(f"MTTR (median): {median(downtimes):.1f} minutes")

# MTBF = mean time between end of one incident
# and start of next
between_failures = [
    (incidents[i+1]["start"] - incidents[i]["end"]
     ).total_seconds() / 3600
    for i in range(len(incidents) - 1)
]
mtbf = mean(between_failures)
print(f"MTBF: {mtbf:.1f} hours")

# Calculate availability
mttr_hours = mttr / 60
availability = mtbf / (mtbf + mttr_hours) * 100
print(f"Availability: {availability:.4f}%")
```

**Example 2 - Automated recovery to reduce MTTR**
```java
// GOOD: Circuit breaker + automatic fallback
// Reduces MTTR from "wait for on-call" to seconds
@Component
public class UserService {
    private final CircuitBreaker circuitBreaker;
    private final UserRepository db;
    private final Cache<String, User> localCache;

    public User getUser(String userId) {
        return circuitBreaker.executeSupplier(() -> {
            // Try primary DB
            User user = db.findById(userId);
            localCache.put(userId, user);
            return user;
        }, fallback -> {
            // Circuit open: serve from cache
            // MTTR for DB failure: instant (no human)
            User cached = localCache.getIfPresent(userId);
            if (cached != null) {
                return cached;
            }
            throw new ServiceUnavailableException(
                "User service degraded: " + fallback);
        });
    }
}
// MTTD: immediate (circuit breaker detects instantly)
// MTTA: 0 (automatic fallback)
// MTTR: seconds (circuit opens, fallback activates)
// No human required for transient failures
```

**Example 3 - Runbook automation for common failures**
```bash
# Runbook: common cause is OOM kill → rolling restart
# Automated runbook reduces investigation time

#!/bin/bash
# Auto-runbook: detect and fix OOM restarts
SERVICE="my-api"
THRESHOLD_RESTARTS=3

# Detect: pods restarting frequently (k8s OOM)
RESTARTS=$(kubectl get pods -l app=$SERVICE \
  -o jsonpath='{.items[*].status.containerStatuses[*]
  .restartCount}' | tr ' ' '\n' | sort -n | tail -1)

if [ "$RESTARTS" -gt "$THRESHOLD_RESTARTS" ]; then
    echo "OOM pattern detected: $RESTARTS restarts"

    # Diagnosis: check last OOM kill event
    kubectl describe pod -l app=$SERVICE \
        | grep -A2 "OOMKilled"

    # Fix: increase memory limit temporarily
    kubectl set resources deployment/$SERVICE \
        --limits=memory=2Gi

    # Alert team: auto-mitigated but requires review
    curl -X POST $SLACK_WEBHOOK \
        -d '{"text":"Auto-fix: OOM on '$SERVICE'.
              Memory limit increased to 2Gi.
              Review heap usage in Grafana."}'
fi
```

---

### ⚖️ Comparison Table

| Metric | What It Measures | High Value = | Low Value = | How to Improve |
|---|---|---|---|---|
| **MTBF** | How often failures occur | Reliable (rare failures) | Unreliable (frequent) | Redundancy, testing, chaos engineering |
| **MTTR** | How fast you recover | Slow recovery | Fast recovery | Runbooks, auto-recovery, better monitoring |
| **MTTD** | How fast failures are detected | Slow detection (monitoring gap) | Fast detection | Better alerting, synthetic monitoring |
| **MTTA** | How fast on-call acknowledges | Slow response (pager fatigue) | Fast response | On-call rotation, alert quality |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MTBF improvement is always the right investment | Reducing MTTR from 60 min to 5 min often yields the same availability improvement as increasing MTBF by 10x. Evaluate both levers. |
| MTTR only measures technical recovery time | MTTR includes time to detect (MTTD) and time to acknowledge (MTTA), which are organizational metrics, not just technical ones. High MTTA often indicates on-call burnout or alert noise problems. |
| Zero MTBF is achievable | In complex distributed systems, failures are inevitable. "No failures" is not a goal; "fast recovery from inevitable failures" is. This is the design principle of chaos engineering. |

---

### 🚨 Failure Modes & Diagnosis

**High MTTD (Monitoring Gap)**

**Symptom:**
Users report via social media that the service is
down. The on-call engineer has received no alerts.
Service has been down for 25 minutes undetected.

**Root Cause:**
A new failure mode (database connection pool exhaustion)
is not covered by existing alerts. The monitoring
system checks server health (CPU, memory) but not
application-level behavior (successful response to
test requests).

**Diagnostic:**
```bash
# Check monitoring coverage: for each critical
# dependency, is there an end-to-end health check?
# Test: call the actual user-facing endpoint
# not just the /health infrastructure endpoint

# Add synthetic monitoring: external probe
# that simulates a real user request
curl -w "@curl-format.txt" -o /dev/null -s \
  https://api.example.com/api/v1/users/health-probe
# Alert if this fails or exceeds 2s
# This catches failures that /health misses:
# - DB connection pool exhaustion
# - Downstream API failures
# - Configuration errors
```

**Fix:**
Add end-to-end synthetic monitoring that calls
production-like requests. Alert on these failing,
not just on server-level metrics. Target: MTTD < 2
minutes for any user-impacting failure.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SLA / SLO / SLI` - MTBF/MTTR are reliability metrics
  that feed into SLO calculations and error budgets
- `Availability` - the relationship `Availability =
  MTBF / (MTBF + MTTR)` connects these concepts

**Builds On This (learn these next):**
- `RTO / RPO` - RTO is the recovery time objective;
  MTTR is the measured actual recovery time. RTO
  is the target; MTTR is the reality.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MTBF          │ How often failures occur                 │
│               │ = total uptime / # failures              │
├───────────────┼──────────────────────────────────────────┤
│ MTTR          │ How fast you recover                     │
│               │ = total downtime / # failures            │
├───────────────┼──────────────────────────────────────────┤
│ AVAILABILITY  │ MTBF / (MTBF + MTTR)                    │
├───────────────┼──────────────────────────────────────────┤
│ MTTD          │ Time to DETECT failure (monitoring gap)  │
│ MTTA          │ Time to ACKNOWLEDGE (pager fatigue risk) │
├───────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT   │ In distributed systems, improve MTTR     │
│               │ first (fast, high ROI). Then MTBF.       │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "MTBF: how often it breaks.              │
│               │  MTTR: how fast you fix it.              │
│               │  Availability depends on both."          │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ RTO / RPO → Redundancy and Failover      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Availability = MTBF / (MTBF + MTTR) - both matter.
2. MTTR is usually easier to improve than MTBF (better
   runbooks, monitoring, auto-recovery).
3. Decompose MTTR into MTTD + MTTA + diagnose + fix +
   verify to find where time is actually lost.

**Interview one-liner:**
"MTBF is the average time between failures - how reliable
the system is. MTTR is the average time to recover - how
fast the team responds. Availability = MTBF / (MTBF + MTTR).
For most distributed systems, improving MTTR yields higher
ROI than improving MTBF: fast recovery from inevitable
failures is more achievable than preventing all failures.
Key tactic: decompose MTTR into detection, acknowledgement,
diagnosis, fix, and verify to find where time is lost."

---

### 🎯 Interview Deep-Dive

**Q1: Your service has 99.9% availability but the
team reports "we feel like we're always on-call
fighting fires." How would you investigate?**
*Why they ask:* Tests whether the candidate can go
beyond a single availability number.
*Strong answer includes:*
- Check MTBF: are there many small incidents? 99.9%
  = 43.2 min downtime. If that is 50 incidents at
  0.86 min each, the team IS fighting fires (50 alerts,
  50 postmortems), even though availability looks fine.
- Check MTTD/MTTA: are alerts noisy (many false positives)?
  High alert volume causes burnout regardless of actual
  failures.
- Check incident severity distribution: many P2/P3
  that never hit the SLO but still require attention.
- Solution: reduce incident frequency (improve MTBF)
  OR reduce recovery complexity (improve MTTR, better
  automation, fewer manual steps). Also audit alert
  quality to reduce false positive on-call interruptions.

**Q2: Design a strategy to get a service from 99.5%
to 99.9% availability. What would you investigate
first?**
*Why they ask:* Tests systematic reliability improvement thinking.
*Strong answer includes:*
- Current profile: 99.5% = 216 min/month downtime.
  Target: 43.2 min/month. Need to cut downtime by 5x.
- Step 1: Measure MTBF and MTTR for the current
  99.5%. Are incidents few and long (low MTBF, high
  MTTR) or many and short (low MTBF, low MTTR)?
- Step 2: Identify highest-impact failure causes via
  postmortem analysis. What failures account for 80%
  of downtime?
- Step 3: For each top failure: can it be prevented
  (MTBF) or automatically recovered from (MTTR)?
  Quick wins: automated circuit breakers, runbooks,
  better alerts for known failure modes.
- Step 4: Measure after each change. Track MTBF and
  MTTR separately, not just availability.
