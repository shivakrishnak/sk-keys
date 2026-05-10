---
id: SYD-058
title: Formal Capacity Planning Models
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-027, SYD-026, SYD-057
used_by:
related: SYD-053, SYD-061, SYD-062
tags:
  - architecture
  - performance
  - production
  - deep-dive
  - advanced
status: complete
version: 2
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /syd/formal-capacity-planning-models/
---

# SYD-058 - Formal Capacity Planning Models

⚡ TL;DR - Formal capacity planning replaces gut-feel provisioning with mathematical models that predict when a system will fail under load, before it actually does.

| SYD-058         | Category: System Design          | Difficulty: ★★★ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | SYD-027, SYD-026, SYD-057        |                 |
| **Used by:**    |                                  |                 |
| **Related:**    | SYD-053, SYD-061, SYD-062        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company doubles its marketing spend for Black Friday. Traffic
is 3x normal. The database connection pool hits its limit at
exactly the worst moment. The site goes down. Post-mortem: "We
didn't know 3x traffic would saturate the connection pool." The
answer was calculable 6 weeks in advance. Nobody calculated it.

**THE BREAKING POINT:**
Ad-hoc capacity planning ("let's add 20% headroom") fails because
systems do not scale linearly. Database connections, memory, and
file descriptors all have non-linear saturation behaviour.
A system running at 70% CPU might handle a 2x load spike fine;
one running at 70% of its connection pool limit might not.

**THE INVENTION MOMENT:**
Model system behaviour mathematically. Queueing theory (Erlang,
1909) provides the mathematical tools. The USL (Universal
Scalability Law) provides throughput predictions. Demand models
map expected business growth to infrastructure requirements.
With these models, you calculate the failure point before it
arrives.

**EVOLUTION:**
Erlang's telephone traffic models (1909) are the origin.
Nelson's BCMP networks (1975) extended queueing theory to
computer systems. Neil Gunther's PDQ (Pretty Damn Quick) and
USL models (1993, 2007) made these practical for web systems.
Google's Site Reliability Engineering book (2016) formalised
capacity planning as an SRE discipline.

---

### 📘 Textbook Definition

**Formal capacity planning models** are mathematical frameworks
used to predict the maximum sustainable throughput, latency
behaviour, and resource utilisation of a software system at
a given load level, enabling infrastructure provisioning
decisions to be made quantitatively rather than by intuition
or rule-of-thumb.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Calculate when your system breaks before it
actually breaks.

> Think of a bridge engineer. They do not build a bridge and
> then drive increasingly heavy trucks over it until it collapses
> to find its limit. They calculate the load capacity from
> materials and geometry before a single beam is placed. Capacity
> planning is the same: calculate the load limit before it
> is reached in production.

**One insight:** Systems do not degrade gracefully at their
limits; they collapse. A queue at 95% capacity is one burst
away from full saturation, exponential wait times, and cascade
failure. The model tells you how far the 95% mark really is.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every resource (CPU, connections, memory, threads, disk I/O)
   has a saturation point; beyond it, queueing becomes infinite
   in theory and catastrophic in practice.
2. Mean values lie; tail behaviour at saturation is what matters.
   A P99 does not reflect saturation; P99.9 at 90% utilisation
   often does.
3. Traffic distributions are bursty; mean load planning is
   insufficient; you must plan for P99 of the load distribution,
   not the mean.
4. Some resources are renewable per request (CPU time); others
   are finite pools (connection pool size, file descriptors).
   Pool resources saturate suddenly, not gradually.
5. Load testing validates the model; it does not replace it.
   Testing is too slow and expensive to be the only planning tool.

**DERIVED DESIGN:**
From invariant 4: identify finite pool resources first; model
their saturation points explicitly.
From invariant 3: model peak load as mean + 3 standard deviations
(3-sigma planning) for normal distributions; for bursty traffic,
use 95th percentile of the load distribution over a 5-minute window.
From invariant 2: monitor P99.9 latency as the saturation
proximity metric; when it diverges from P99, you are entering
the saturation zone.

**THE TRADE-OFFS:**
**Gain:** Failures are predicted and prevented; cost is minimised
by right-sizing to predicted need; no over-provisioning from fear.
**Cost:** Model accuracy depends on measurement quality; models
require maintenance as usage patterns change; initial effort
to build the model is significant.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The statistical behaviour of traffic is
inherently variable and requires probabilistic modelling.
**Accidental:** Running load tests repeatedly to "feel out"
the ceiling when the ceiling is calculable from first principles
is avoidable waste.

---

### 🧪 Thought Experiment

**SETUP:** Your service handles 1,000 RPS today. The CEO
announces a feature that will 5x traffic in 30 days.

**WHAT HAPPENS WITHOUT FORMAL CAPACITY PLANNING:**
You provision "about 5x the current servers." Day of launch:
the DB connection pool exhausts at 2x load (not 5x) because
you did not model the connection pool separately. Service is
down for 3 hours.

**WHAT HAPPENS WITH FORMAL CAPACITY PLANNING:**
You model each resource. DB connection pool: current pool size
is 100; each request holds a connection for 50ms. At 1000 RPS:
L = 1000 * 0.05 = 50 connections (50% utilisation). At 5000 RPS:
L = 5000 * 0.05 = 250 connections needed. Pool size must be
300+ (safety margin). You increase it 2 weeks before launch.
Zero incidents.

**THE INSIGHT:**
The failure was foreseeable and calculable. The lack of a formal
model meant the failure was invisible until it happened. The
model costs hours; the incident costs days and revenue.

---

### 🧠 Mental Model / Analogy

> Think of formal capacity planning as the load calculations
> an engineer does for a building. Before construction, the
> structural engineer calculates: what is the maximum weight
> per floor, per column, per foundation? They do not build the
> building and then add people until a column cracks. The
> calculations happen before concrete is poured.

- **Floor weight limit** = resource saturation point
- **People on the floor** = concurrent requests
- **Column load** = connection pool or thread pool utilisation
- **Foundation** = database / persistence layer
- **Structural calculation** = formal capacity model

Where this analogy breaks down: buildings have static loads;
software systems have dynamic, bursty traffic patterns that
require probabilistic modelling, not just static load calculations.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of guessing how many servers you need, you calculate
it using math. The math models how busy each part of the system
will be as traffic grows, and tells you exactly when each part
will break.

**Level 2 - How to use it (junior developer):**
Start with Little's Law for each resource pool:
`L = λ × W` (pool occupancy = arrival rate × service time).
If L > pool_size, the pool saturates. Calculate the arrival rate
that saturates each pool. That is your capacity limit.

**Level 3 - How it works (mid-level engineer):**
Model each resource as a queue:
- **M/M/1 queue:** single server, Poisson arrivals, exponential
  service time. Mean queue length: `ρ / (1 - ρ)` where
  `ρ = λ / μ` (utilisation). At ρ > 0.8, mean wait time
  grows faster than linearly.
- **Connection pools:** model as M/M/c queue (c servers).
  At c = 100, ρ = 0.9: mean wait ≈ 0.5ms. At ρ = 0.99:
  mean wait ≈ 50ms (100x increase from ρ ≈ 0.9).
- **USL:** `X(N) = N / (1 + σ(N-1) + κN(N-1))`. Fit σ and κ
  from load test data; predict throughput at any N.

**Level 4 - Why it was designed this way (senior/staff):**
Queueing theory shows that near saturation (ρ → 1.0), mean
wait time grows to infinity, not just "gets slower." This is
the non-linear collapse behaviour. Traditional capacity planning
(add 20% headroom to current utilisation) gives you 80-100%
utilisation - exactly where collapse begins. Formal models
expose this: you need 50-60% utilisation on finite pools to
maintain stable latency under burst traffic.

**Expert Thinking Cues:**
- "What are all the finite resource pools in this system?"
- "What is the utilisation of each at current peak load?"
- "At what load (RPS) does each pool reach 80% utilisation?"
- "What is the burst multiplier for peak events vs. average?"
- "Does the capacity model still hold? When was it last validated
  against a load test?"

---

### ⚙️ How It Works (Mechanism)

**Resource saturation model:**
```
For each resource pool:
  Current utilisation:
    ρ = λ × W_per_request / pool_size

  Saturation RPS (where ρ = 0.80 for safety):
    RPS_sat = 0.80 × pool_size / W_per_request

  Current headroom:
    headroom = (RPS_sat - current_RPS) / current_RPS × 100%
```

**Example - connection pool:**
```
Pool size: 100 connections
Average time holding a connection: 20ms = 0.02s
λ_sat = 0.8 × 100 / 0.02 = 4,000 RPS

Current load: 1,000 RPS
ρ_current = 1000 × 0.02 / 100 = 0.2 (20% - healthy)
```

**Planning for 5x growth:**
```
5x load = 5,000 RPS
ρ_future = 5000 × 0.02 / 100 = 1.0 (100% - saturation!)
Pool must be: 5000 × 0.02 / 0.8 = 125 connections minimum
Add 50% safety: 190 connections
```

**USL fit from load test:**
```
Test at N = 1, 2, 4, 8, 16 nodes
Throughput: 100, 195, 380, 700, 1200 RPS
Fit USL to data: σ=0.01, κ=0.005
Predicted peak: X_max ≈ 1/(σ + 0 + √(κ)) ≈ 1,800 RPS

Architecture is bounded; no benefit beyond ~20 nodes.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
+--------------------------------------------------+
| Business projection: N% growth in M months      |
|   ↓                                              |
| Map to traffic model: peak RPS projection        |
|   ← YOU ARE HERE                                 |
| Enumerate all finite resource pools             |
|   ↓                                              |
| Model: ρ = λ × W / pool_size per resource        |
|   ↓                                              |
| Identify: which pools saturate first?           |
|   ↓                                              |
| Calculate: pool resizes, instance type changes  |
|   ↓                                              |
| Validate: load test confirms model predictions  |
|   ↓                                              |
| Monitor: track ρ per resource in production     |
+--------------------------------------------------+
```

**FAILURE PATH:**
- Model not updated → stale model predicts wrong capacity
- Burst pattern not modelled → mean traffic fine, burst causes
  saturation
- One resource pool missed → the missed pool is the failure point

**WHAT CHANGES AT SCALE:**
Small: spreadsheet model is sufficient.
Medium: automate model updates from production metrics.
Large: real-time capacity model integrated with auto-scaling
  rules; capacity plan drives cloud cost forecasting.

---

### 💻 Code Example

**BAD - guessing connection pool size:**
```yaml
# BAD: no capacity model; pool size = guess
spring:
  datasource:
    hikari:
      maximum-pool-size: 50  # "seemed reasonable"
      # At 2000 RPS: ρ = 2000 × 0.02 / 50 = 0.8 (close!)
      # At 3000 RPS: ρ = 3000 × 0.02 / 50 = 1.2 (saturated!)
```

**GOOD - connection pool sized by Little's Law:**
```yaml
# GOOD: pool sized from capacity model
# Peak RPS target: 5000
# Avg connection hold time: 20ms = 0.02s
# Target utilisation: 70% (ρ = 0.7)
# Pool = Peak_RPS × hold_time / target_rho
#       = 5000 × 0.02 / 0.7 = 143 connections
# Add safety margin: 180
spring:
  datasource:
    hikari:
      maximum-pool-size: 180
      # ρ at 5000 RPS = 5000 × 0.02 / 180 = 0.56 (healthy)
```

**BAD - no monitoring of pool utilisation:**
```java
// BAD: no visibility into connection pool health
// You discover saturation from user complaints
DataSource ds = createDataSource();
```

**GOOD - pool utilisation monitoring:**
```java
// GOOD: expose pool metrics to Prometheus
// Spring Boot + Hikari: auto-exposed via Actuator
// metrics: hikaricp.connections.active,
//          hikaricp.connections.pending
// Alert when: active / max > 0.75 for > 5 minutes
// Configuration: application.yml
management:
  metrics:
    enable:
      hikaricp: true
```

**How to test / verify correctness:**
- Run load test at 50%, 80%, and 100% of predicted capacity.
  Verify model predictions match measured saturation points
  within 10%.
- Plot P99 latency vs. load; identify the knee of the curve
  (where P99 starts growing faster than linearly). This is
  the saturation zone.
- Monitor ρ for each finite resource in production; alert when
  any ρ exceeds 0.70.

---

### ⚖️ Comparison Table

| Approach               | Accuracy | Effort | Updates needed |
|------------------------|----------|--------|----------------|
| Rule of thumb (20% headroom) | Low | Very low | Never |
| Load test only         | Medium   | High   | Per release    |
| Little's Law model     | High     | Low    | When W changes |
| Full queueing model    | Very high| Medium | Quarterly      |
| ML-based forecasting   | High     | High   | Continuous     |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Load testing replaces capacity models" | Load tests are slow, expensive, and only tell you about today's architecture. Models predict future states and drive provisioning decisions. |
| "Average utilisation is the right metric" | Average utilisation hides burst saturation. P99 of resource utilisation over short windows (30-60 s) is the correct metric. |
| "Adding 20% headroom is standard best practice" | At 80% pool utilisation, queuing theory predicts exponential wait time increases. You need 50-60% utilisation on finite pools to be safe. |
| "The model is only valid for current traffic patterns" | Models are parametric: if W (service time) and λ (arrival rate distribution) are measured, the model scales to any projected load. |
| "Cloud auto-scaling makes capacity planning obsolete" | Auto-scaling handles compute (stateless). Databases, connection pools, and message queue depths require explicit capacity planning. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Connection pool collapse on traffic spike**

**Symptom:** During a load spike, P99 latency goes from 50ms
to 30s. DB is at 30% CPU. Application logs show
"Connection not available within timeout."

**Root Cause:** All connection pool slots are occupied;
new requests queue but time out waiting for a connection.

**Diagnostic:**
```bash
# HikariCP metrics via Actuator:
curl http://localhost:8080/actuator/metrics/\
  hikaricp.connections.active
# If value = maximum-pool-size: pool is saturated

# See pending requests waiting for connection:
curl http://localhost:8080/actuator/metrics/\
  hikaricp.connections.pending
```

**Fix:** Apply Little's Law. Calculate required pool size
at peak load. Increase pool size immediately. Longer term:
reduce W (connection hold time) by optimising queries.

**Prevention:** Set pool size using Little's Law + 40%
safety margin. Alert when pending > 0 for > 30 seconds.

---

**Failure Mode 2: Capacity model stale after architecture change**

**Symptom:** System "should" handle 5x based on the capacity
model but fails at 2x after a new feature was shipped.

**Root Cause:** The new feature added a synchronous external
API call that increased W (service time) by 200ms. The
capacity model was not updated.

**Diagnostic:**
```bash
# Compare current P99 latency per endpoint vs. baseline
# Jaeger / distributed tracing:
curl "http://jaeger:16686/api/traces?service=checkout
  &limit=20" | jq '.data[].spans
  | map(select(.operationName == "db.query"))
  | .[].duration' | sort -n
```

**Fix:** Re-measure W after every feature release that adds
external calls or DB queries. Recalculate ρ with new W.
Update capacity model and pool sizes.

**Prevention:** Capacity model must be updated as part of
every architecture review for features that change W.

---

**Failure Mode 3: Memory saturation at load not modelled**

**Symptom:** Service runs fine at 1k RPS but OOM-kills at
3k RPS. Memory usage was not modelled.

**Root Cause:** Each request holds 20KB in-flight (caching
response JSON). L = λW = 3000 × 0.05 = 150 concurrent
requests × 20KB = 3MB/s growth in live heap. Not modelled.

**Diagnostic:**
```bash
# Monitor JVM heap during load test
# Java: jstat -gcutil <pid> 1000
# Or: kubectl top pods --containers
# Look for heap growing linearly with RPS
```

**Fix:** Include memory as a resource pool in the capacity
model. Calculate: peak working set = L × per_request_memory.
Provision accordingly.

**Prevention:** Memory must be a first-class resource in all
capacity models. Measure per-request memory allocation during
profiling.

---

**Failure Mode 4 (Security): Rate limit undersized, enables abuse**

**Symptom:** DDoS attack sends 10x normal load. Rate limits
are set to "10x current peak" as margin - meaning the attacker
can send 10x before being blocked, which saturates the DB.

**Root Cause:** Rate limits were set by feel, not by the
saturation model. The correct rate limit is the saturation
throughput (ρ = 0.7), not an arbitrary multiple of average.

**Diagnostic:**
```bash
# Calculate safe rate limit from capacity model
# Safe RPS = 0.7 × pool_size / avg_hold_time
# This is the ρ=0.7 threshold; set rate limit here
```

**Fix:** Set rate limits to the ρ = 0.7 saturation threshold
for the most constrained resource, not arbitrary multiples.

**Prevention:** Capacity model drives rate limit configuration.
Rate limits are a safety valve at the capacity ceiling.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-026 - Back-of-Envelope Estimation]] - quick estimation
- [[SYD-027 - Capacity Planning]] - planning fundamentals
- [[SYD-057 - Theoretical Foundations of Scalable Systems]] -
  the theory behind the models

**Builds On This (learn these next):**
- [[SYD-061 - Scale Estimation Mental Model]] - practical
  estimation techniques

**Alternatives / Comparisons:**
- [[SYD-053 - Cost-Performance Trade-off Architecture]] -
  applying capacity models to cost decisions
- [[SYD-062 - Trade-off Navigation Framework]] - using models
  as input to trade-off decisions

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS    | Math models predicting system failure     |
| PROBLEM       | Gut-feel provisioning fails at saturation |
| KEY INSIGHT   | Systems collapse near saturation (ρ → 1); |
|               | calculate before you hit it               |
| USE WHEN      | Pre-launch, pre-peak-event, quarterly      |
| AVOID WHEN    | Prototype / pre-production                 |
| TRADE-OFF     | Effort to build model vs. cost of outage  |
| ONE-LINER     | L = λW applied to every finite resource   |
| NEXT EXPLORE  | SYD-061 Scale Estimation Mental Model      |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Every finite resource pool (connections, threads, memory)
   has a saturation point; calculate ρ = λW/pool_size for each.
2. Keep ρ below 0.70 on all finite pools to maintain stable
   P99 latency under burst traffic.
3. Load tests validate models; they are not a substitute for
   having a model in the first place.

**Interview one-liner:** "Formal capacity planning uses
queueing theory - specifically Little's Law (L = λW) and
USL - to calculate the saturation point of each finite
resource pool before it is reached, enabling proactive
provisioning rather than reactive firefighting."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any system with finite
resource pools, utilisation above 70-80% creates exponentially
increasing queue wait times; safety margins must be calculated
from the saturation model, not from intuition.

**Where else this pattern appears:**
- **Emergency room triage:** ER capacity is modelled using
  M/D/c queueing to ensure bed utilisation stays below 85%;
  beyond that, patient wait times diverge from safe levels.
- **Network engineering:** Bandwidth provisioning targets
  70% utilisation; beyond that, packet drops create
  exponential retransmit storms (TCP).
- **Coffee shop operations:** Throughput of an espresso machine
  vs. customer arrival rate determines queue depth; Starbucks
  uses traffic models to determine barista staffing.

---

### 💡 The Surprising Truth

The Erlang C formula, which is the foundation of all connection
pool capacity modelling, was derived by Agner Krarup Erlang in
1909 for telephone exchanges - 40 years before computers existed.
Erlang was calculating how many telephone operators were needed
to handle call traffic without excessive wait times. Every
database connection pool, thread pool, and HTTP connection pool
in every software system built today follows the same
mathematical behaviour Erlang described for human telephone
operators. The formula is over 100 years old and still exactly
correct.

---

### 🧠 Think About This Before We Continue

**Q1 (B - Scale):** Your service currently has P99 = 50ms at
500 RPS with a 50-connection pool and 10ms avg connection hold
time. Your CTO projects 10,000 RPS for the next product launch.
Calculate the required pool size, the expected ρ at that load,
and what happens to P99 if the pool is not resized.
*Hint: Apply Little's Law: L = λW to find current utilisation,
then project to 10k RPS. Use the M/M/c queue approximation for
wait time vs. utilisation.*

**Q2 (C - Design Trade-off):** You can handle 10x growth by
either (a) increasing database connection pool to 500, or (b)
introducing a write queue that decouples DB writes from
request processing. Model both approaches using Little's Law.
Which is correct for a write-heavy workload and why is a larger
connection pool not always the right answer?
*Hint: Consider what happens to W when the DB itself becomes
the bottleneck at high concurrency, and how a queue changes
the effective λ seen by the database.*

**Q3 (D - Root Cause):** A capacity model predicted the system
could handle 5x load but it failed at 2.5x. Post-mortem shows
the model was accurate for compute and the connection pool,
but the failure was in a third-party API rate limit that was
not in the model. What is the systematic process for ensuring
all capacity constraints are included in the model, and how
do you discover constraints that are invisible from the inside?
*Hint: Research dependency mapping, contract testing of third-
party rate limits, and chaos testing for external dependency
failures.*
