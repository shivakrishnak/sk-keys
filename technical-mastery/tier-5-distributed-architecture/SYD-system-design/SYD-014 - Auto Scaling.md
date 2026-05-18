---
id: SYD-014
title: Auto Scaling
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-007
used_by: ""
related: SYD-007, SYD-008, SYD-013, SYD-027
tags:
  - architecture
  - infrastructure
  - performance
  - cloud
  - scalability
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/syd/auto-scaling/
---

⚡ TL;DR - Auto scaling automatically adds or removes
server capacity based on observed demand metrics,
turning horizontal scaling from a manual operational
task into an elastic, demand-driven infrastructure
behavior.

| #014 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Horizontal Scaling | |
| **Used by:** | (none - operational infrastructure concept) | |
| **Related:** | Horizontal Scaling, Load Balancing, Session Affinity, Capacity Planning | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A SaaS platform has predictable daytime peaks (10x
overnight traffic) and unpredictable traffic spikes
from viral content. Without auto scaling, the team
must provision for peak capacity 24/7. They run 50
servers at 4 AM when they only need 5. Cost: 10x
what is necessary at off-peak. Alternative: provision
for average load, accept that spikes cause outages.
Neither option is acceptable for a production business.

**THE BREAKING POINT:**
Traffic demand is not constant. Provisioning for
peak means paying for idle capacity. Provisioning
for average means outages at peak. The only economically
rational solution is infrastructure that automatically
expands when demand increases and contracts when it
falls.

**THE INVENTION MOMENT:**
AWS launched Auto Scaling in 2009 as part of the EC2
service. Before this, horizontal scaling required
humans to monitor metrics and manually launch/terminate
instances. Auto scaling automated this feedback loop:
observe metric → compare to threshold → adjust capacity.
Cloud elasticity was the enabling technology; auto
scaling is the policy layer on top of it.

---

### 📘 Textbook Definition

Auto scaling is an infrastructure management capability
that automatically adjusts compute capacity (number
of server instances) in response to observed demand
metrics. A scaling policy defines: the metric to
observe (CPU utilization, request count, queue depth,
latency), the threshold that triggers scaling, the
cooldown period between scaling events, and the
minimum/maximum instance bounds. Auto scaling operates
in two directions: scale-out (add instances when load
rises) and scale-in (remove instances when load falls).
Modern auto scaling includes predictive scaling
(pre-scaling before anticipated demand, based on
historical patterns) and scheduled scaling (pre-defined
scaling events at known times).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Auto scaling watches metrics and automatically adds
or removes servers to match demand, continuously.

**One analogy:**
> A smart thermostat for your server capacity. Too
> hot (high load) → it turns on more servers. Too
> cold (low load) → it turns off excess servers.
> You set the target temperature and the acceptable
> range, and the thermostat handles the rest.

**One insight:**
Auto scaling converts a capital cost problem (buy
enough hardware for peak) into an operational cost
problem (pay for what you use now). In the cloud,
this is economically transformative: you pay for
5 servers at 4 AM and 50 servers at noon.

---

### 🔩 First Principles Explanation

**THE FEEDBACK LOOP:**

```
┌─────────────────────────────────────────────────┐
│ AUTO SCALING CONTROL LOOP                       │
│                                                 │
│  Observe metric:                                │
│    avg CPU = 75% (threshold: 70%)               │
│          ↓                                      │
│  Decision: scale out                            │
│    current = 5 instances                        │
│    target  = ceil(5 × 75/70) = 6 instances     │
│          ↓                                      │
│  Action: launch 1 new instance                  │
│          ↓                                      │
│  Cooldown: wait 300s (no more scale actions)    │
│          ↓                                      │
│  Re-observe: avg CPU = 62% (below threshold)   │
│    No action needed                             │
└─────────────────────────────────────────────────┘
```

**SCALING POLICY TYPES:**

- **Target Tracking:** "Keep average CPU at 60%."
  AWS automatically calculates required instance count
  and adjusts. Simplest to configure. Recommended
  for most use cases.
- **Step Scaling:** "Add 2 instances at 70% CPU,
  add 5 instances at 85% CPU." Allows graduated
  response to different severity levels.
- **Scheduled:** "At 7:55 AM on weekdays, set min=10."
  For predictable traffic patterns (business hours,
  weekly events).
- **Predictive:** ML model analyzes historical traffic
  patterns and pre-scales before anticipated demand.
  Eliminates the latency of reactive scaling.

**THE FUNDAMENTAL CONSTRAINT:**
Auto scaling has a response latency: time to detect
the metric change + time to launch a new instance
(1-5 minutes for a VM, 10-60 seconds for a container).
During this window, existing instances must absorb
the increased load. Instance startup time is the
key variable in auto scaling responsiveness.

**THE TRADE-OFFS:**

**Gain:** Elastic cost (pay for actual use); automatic
high-availability response to instance failures;
handles unpredictable traffic spikes without human
intervention.

**Cost:** Scale-out latency means instances must have
capacity headroom; application must be stateless
(or sessions must survive instance replacement);
cost optimization requires tuning (aggressive scale-in
can cause thrashing; conservative scale-in wastes cost).

---

### 🧪 Thought Experiment

**SCENARIO: Viral tweet + auto scaling**

A company has a media site with auto scaling configured:
- Target: CPU at 60%, scale-out when > 70% for 3 minutes
- Min: 3 instances, Max: 50 instances
- Instance warmup: 90 seconds
- Cooldown: 300 seconds

At 2:00 PM, a viral tweet sends 10x normal traffic:
```
2:00 PM: Traffic 10x. CPU jumps from 40% to 95%.
2:03 PM: Metric threshold reached (3 min sustained).
2:03 PM: Scale-out triggered: 3 → 9 instances.
2:04:30 PM: 6 new instances healthy. CPU: ~50%.
2:05 PM: Viral traffic continues. CPU stabilizes at 50%.
2:10 PM: Traffic declines. CPU drops to 25%.
2:15 PM: Scale-in trigger: 9 → 6 instances.
2:20 PM: Traffic normalizes. 6 → 3 instances.
```

**WITHOUT auto scaling:** 3 instances at 95% CPU for
20+ minutes. p99 latency > 30 seconds. Users give up.

**WITH auto scaling:** 3-minute degradation window
during scale-out startup, then normal performance.

**THE INSIGHT:**
Auto scaling does not prevent the initial degradation
during the scale-out startup window. Headroom (setting
target CPU at 60% instead of 90%) is what determines
how much traffic the existing instances can absorb
while new ones start. Under-provisioning headroom
means 3 minutes of degraded performance; over-
provisioning means paying for more idle capacity.
The target CPU threshold is the cost-vs-headroom knob.

---

### 🧠 Mental Model / Analogy

> Auto scaling is like a restaurant that calls in
> extra waitstaff when the reservation book shows
> a full house tonight. If a party of 50 walks in
> unexpectedly, there is a gap (short-staffed for
> the first 30 minutes while extra staff arrive).
> Setting a lower reservation threshold for calling
> in extra staff gives more buffer but costs more
> on slow nights.

- "Calling in extra staff" → launching new instances
- "Party of 50 walks in" → unexpected traffic spike
- "30 minutes while staff arrive" → instance warmup
- "Lower threshold" → lower CPU target (more headroom,
  more cost)
- "Slow nights" → low-traffic periods (idle instances)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The cloud automatically adds more servers when your
app gets busy, and removes them when it quiets down.

**Level 2 - How to use it (junior developer):**
In AWS: create an Auto Scaling Group (ASG) with a
target tracking policy targeting 60% CPU utilization.
Set min=2 (for HA) and max=20 (cost ceiling). The ASG
automatically adjusts instance count to keep CPU
near 60%.

**Level 3 - How it works (mid-level engineer):**
Auto scaling uses CloudWatch metrics (CPU, requests,
queue depth) with alarms. When an alarm fires, the
ASG launches or terminates instances. New instances
are registered with the load balancer after passing
health checks. Target tracking policies use a control
algorithm: `desired_instances = current × (current_metric
/ target_metric)`, rounded up for scale-out.

**Level 4 - Why it was designed this way (senior/staff):**
The cooldown period exists to prevent thrashing: without
it, the system would keep launching instances as
existing instances start up and the metric temporarily
remains high. The cooldown ensures the system waits
to see the effect of launched instances before scaling
again. Setting cooldown too high wastes time waiting
to scale. Setting it too low causes thrashing. The
optimal cooldown is approximately equal to the instance
warmup time plus one metric evaluation period.

**Level 5 - Mastery (distinguished engineer):**
Container-based auto scaling (Kubernetes HPA, ECS)
fundamentally changes the response latency. Containers
start in 5-30 seconds vs 60-300 seconds for VMs.
This enables much lower headroom requirements (target
at 70-80% instead of 50-60%) because the response
window is shorter. Container image pre-caching
(keeping images on nodes) further reduces this to
10-15 seconds. For extremely spiky workloads (event-
driven, serverless), AWS Lambda's auto scaling is
instantaneous (0 warmup) - but with different
constraints (cold start latency, execution duration
limits, no persistent state).

---

### ⚙️ How It Works (Mechanism)

**Auto scaling architecture:**

```
┌────────────────────────────────────────────────────┐
│ AUTO SCALING ARCHITECTURE (AWS)                    │
│                                                    │
│  [CloudWatch Metric]  avg CPU = 82%                │
│          ↓                                         │
│  [Alarm]  CPU > 70% for 3 min → ALARM             │
│          ↓                                         │
│  [Scaling Policy]  target tracking 60% CPU         │
│    desired = ceil(4 × 82/60) = 6 instances         │
│          ↓                                         │
│  [Auto Scaling Group]                              │
│    Launch 2 new instances from Launch Template     │
│          ↓                                         │
│  [Instance Warmup]  90 seconds                     │
│    New instance: install app, start process        │
│    Health check: /health → 200 OK                  │
│          ↓                                         │
│  [Load Balancer]  Register new instances           │
│    Traffic now distributed to 6 instances          │
│          ↓                                         │
│  [Cooldown]  300 seconds - no scaling actions      │
└────────────────────────────────────────────────────┘
```

**Scale-in protection for stateful workloads:**

```
                   Normal scale-in:
┌──────────────────────────────────────────────────────┐
│ Instance termination sequence                        │
│                                                      │
│ 1. ASG selects instance to terminate                 │
│    (oldest, or balanced AZ selection)                │
│ 2. LB deregisters instance (connection drain starts) │
│ 3. Deregistration delay: 30s (in-flight complete)   │
│ 4. Instance terminated                              │
│                                                      │
│ For stateful instances (scale-in protection):        │
│ 1. Set scale-in protection when job starts           │
│ 2. Job completes → remove protection programmatically│
│ 3. ASG can now terminate the instance               │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - AWS: Target tracking auto scaling policy**
```bash
# Create Auto Scaling Group with target tracking
# Target: keep average CPU at 60%
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name my-app-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 60.0,
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
# ScaleInCooldown: wait 300s before scaling in again
# ScaleOutCooldown: can scale out again after 60s
# (scale out faster than scale in - asymmetric)
```

**Example 2 - Kubernetes: Horizontal Pod Autoscaler**
```yaml
# GOOD: HPA targeting 70% CPU
# Containers start faster than VMs:
# higher target is acceptable
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60  # react in 1 min
      policies:
      - type: Pods
        value: 4        # add up to 4 pods at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300 # wait 5 min to scale in
      policies:
      - type: Percent
        value: 10       # remove at most 10% at a time
        periodSeconds: 60
```

**Example 3 - Scheduled + reactive scaling combined**
```bash
# Scheduled scaling: pre-scale before known traffic peak
# (avoids the 3-minute reactive scale-out lag)
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name my-app-asg \
  --scheduled-action-name morning-ramp \
  --recurrence "0 7 * * 1-5" \
  --min-size 10 \
  --desired-capacity 15

# Reactive target tracking still handles
# unexpected traffic beyond the scheduled baseline
# The combination: scheduled for predictable peaks,
# reactive for unexpected spikes
```

---

### ⚖️ Comparison Table

| Scaling Policy | Response Time | Configuration | Best For |
|---|---|---|---|
| **Target Tracking** | 1-3 min | Simple (1 metric, 1 target) | Most production services |
| Step Scaling | 1-3 min | Moderate (thresholds + steps) | Graduated response needed |
| Scheduled | 0 (pre-emptive) | Simple | Predictable daily/weekly peaks |
| Predictive | 0 (pre-emptive) | Auto (ML-based) | Recurring patterns, sufficient history |
| Manual | N/A | Operator action | Planned maintenance, testing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Auto scaling eliminates all capacity incidents | It reduces them. The initial scale-out lag (1-3 minutes) still causes degradation for sudden traffic spikes. Headroom (lower CPU target) is what determines how well existing instances absorb the spike during that lag. |
| Lower CPU target always means better performance | Lower target = more idle capacity = higher cost. The optimal target balances headroom (spike absorption) against cost. For containers (fast start), 70% is often fine. For VMs (slow start), 50-60% provides more buffer. |
| Auto scaling handles database scaling automatically | Auto scaling applies to stateless compute tiers. Database scaling requires separate strategies (vertical scaling, read replicas, sharding). The database often becomes the bottleneck when the compute tier scales. |

---

### 🚨 Failure Modes & Diagnosis

**Scale-Out Thrashing (Scale In Before New Instances Warm Up)**

**Symptom:**
The auto-scaling group repeatedly adds 2 instances,
then removes them within 5 minutes, never stabilizing.
CPU oscillates between 45% and 85%. Instances are
constantly launching and terminating. Cost is 3x
expected.

**Root Cause:**
Scale-out cooldown is too short (60s). New instances
launch, metric starts to drop, scale-in triggers before
instances are fully loaded and contributing, load
spikes again, scale-out triggers again.

**Diagnostic:**
```bash
# Check scaling activity history
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name my-app-asg \
  --max-items 20 \
  --query 'Activities[*].{
    Start:StartTime,
    Status:StatusCode,
    Cause:Cause}' \
  --output table
# Look for rapid alternation between Launch and Terminate
# within short windows → thrashing

# Check instance warmup vs cooldown settings
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names my-app-asg \
  --query 'AutoScalingGroups[0].{
    DefaultCooldown:DefaultCooldown,
    WarmupTime:InstanceMaintenancePolicy}'
```

**Fix:**
Increase `ScaleInCooldown` to at least 2x the
instance warmup time. If warmup takes 90 seconds,
set cooldown to at least 300 seconds. Alternatively,
switch to target tracking (which has built-in
stabilization logic) instead of step scaling.

**Prevention:**
Set `ScaleInCooldown` ≥ instance warmup time + 1
metric evaluation period. Test scaling behavior
before production by simulating load spikes.

---

**New Instances Get Hammered (Cold Cache Under Load)**

**Symptom:**
After auto-scaling adds 5 new instances, the new
instances immediately show very high latency (10x
normal). Existing instances perform normally. Users
routed to new instances experience errors.

**Root Cause:**
New instances have empty in-process caches (Caffeine,
Guava). Each cache miss triggers a database query.
5 new instances × cache miss rate × request rate =
database overload for 5-15 minutes until caches warm.

**Diagnostic:**
```bash
# Check per-instance response time in ALB metrics
# New instances will show much higher ResponseTime
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions \
    Name=LoadBalancer,Value=... \
    Name=TargetGroup,Value=... \
  --period 60 --statistics p99 ...
# Break down by target to identify new instances
```

**Fix:**
Implement "slow start" at the load balancer: new
instances receive a gradually increasing share of
traffic over 5-15 minutes (AWS ALB `slow_start`
duration on the target group). This gives the cache
time to warm with a trickle of traffic before receiving
full load.

```bash
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:... \
  --attributes Key=slow_start.duration_seconds,Value=600
# 600 seconds = 10 minute ramp to full traffic
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Horizontal Scaling` - auto scaling automates the
  process of adding/removing horizontal scale instances

**Builds On This (learn these next):**
- `Capacity Planning` - auto scaling handles reactive
  capacity adjustment; capacity planning handles the
  strategic max and min bounds

**Alternatives / Comparisons:**
- Manual scaling - always available but requires
  human intervention; appropriate for planned changes
- Scheduled scaling - complement to reactive scaling
  for predictable peaks

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automatically add/remove server instances│
│              │ based on demand metrics                  │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Traffic is not constant. Manual scaling  │
│ SOLVES       │ wastes cost or causes outages.           │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Headroom matters: the CPU target         │
│              │ determines how much spike the existing   │
│              │ instances absorb during the scale-out lag│
├──────────────┼──────────────────────────────────────────┤
│ SCALE-OUT    │ Metric > threshold for N min →           │
│ FLOW         │ Launch instances → warmup → LB register  │
├──────────────┼──────────────────────────────────────────┤
│ KEY SETTINGS │ Min/Max bounds; target metric (CPU, RPS);│
│              │ cooldown; instance warmup time           │
├──────────────┼───────�──────────────────────────────────┤
│ ANTI-PATTERN │ Thrashing: scale-in cooldown < warmup    │
│              │ time; instances terminate before others  │
│              │ stabilize                                │
├──────────────┼──────────────────────────────────────────┤
│ PRO TIP      │ Scheduled + reactive combined:           │
│              │ scheduled for predictable peaks,         │
│              │ reactive for unexpected spikes           │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Elastic capacity: pay for what you need,│
│              │  when you need it. The startup lag is the│
│              │  price of elasticity."                   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ SLA/SLO/SLI → Error Budget →             │
│              │ Capacity Planning                        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Reactive scaling has latency (1-5 min for VMs,
   10-60s for containers) - headroom is how you buffer it.
2. Scale-in cooldown must be longer than instance warmup
   - or you get thrashing.
3. Combine scheduled (predictable) + reactive (spiky)
   for the best coverage.

**Interview one-liner:**
"Auto scaling monitors a metric (usually CPU or request
rate) and automatically adds or removes server instances
to maintain a target utilization. The key tension is
between the scale-out response latency (1-5 minutes for
new instances to start) and the headroom you configure
(lower CPU target = more buffer capacity). For predictable
peaks, combine scheduled pre-scaling with reactive
auto scaling for the best of both."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any feedback-controlled system needs a response time
that is calibrated to the rate of change in what it
is controlling. Auto scaling cooldown tuning is an
application of classical control theory: if the control
response is faster than the system's settling time
(instance warmup), you get oscillation (thrashing).
If the control response is much slower than the rate
of change (traffic spikes), you are always behind.
The right cooldown is approximately equal to the
system's time constant (warmup time).

**Industry applications:**
- **Netflix:** Uses auto scaling across hundreds of
  microservices. Their key insight: different services
  scale at different rates. For services with fast
  container startup (< 30s), they set targets at 70%.
  For services with slow startup (> 5 min), they
  keep targets at 40-50% with much higher headroom.
  One-size-fits-all scaling policy is an anti-pattern.
- **Shopify Black Friday:** Pre-scales to 10x normal
  capacity starting the day before Black Friday.
  They combine scheduled scaling (pre-scaling to
  known baseline), auto scaling (handles variance
  around the baseline), and manual override capability
  (for real-time tuning during the event). Auto
  scaling alone would lag; pre-scaling alone might
  miss unexpected spikes.

---

### 🎯 Interview Deep-Dive

**Q1: Design the auto-scaling policy for an API service
that handles normal load (1,000 RPS) and a known
daily traffic spike (8,000 RPS) every weekday at 9 AM.**
*Why they ask:* Tests practical design of combined
scaling strategies.
*Strong answer includes:*
- Scheduled scaling: at 8:50 AM on weekdays, set
  minimum capacity to 8x baseline (before the spike)
- Target tracking: keep CPU at 60% for reactive scaling
  around the scheduled baseline
- Min: 3 instances (HA floor), Max: 50 (cost ceiling)
- After spike subsides (10 AM): allow scale-in with
  300s cooldown
- Instance warmup time: measure it for your app and
  set ScaleOutCooldown ≥ warmup + 1 metric period

**Q2: Your auto-scaling group just launched 10 new
instances but p99 latency is still terrible for 5
minutes after they come online. What is happening
and how would you fix it?**
*Why they ask:* Tests awareness of cold-cache
degradation from auto scaling.
*Strong answer includes:*
- Problem: new instances have cold caches; every
  request is a cache miss hitting the database;
  database becomes the bottleneck
- Fix 1: slow start at load balancer (gradually
  ramp traffic to new instances over 5-10 minutes)
- Fix 2: application-level cache pre-warming on
  startup (pre-load top N items from DB into cache
  before accepting traffic)
- Fix 3: reduce reliance on local caches; use a shared
  distributed cache (Redis) that new instances
  benefit from immediately

**Q3: How do you auto-scale a stateful service
(like a WebSocket server)?**
*Why they ask:* Tests depth of understanding where
auto scaling is complicated.
*Strong answer includes:*
- Scale-out: new connections go to new servers (fine);
  existing connections stay on their current server
  (required by protocol)
- Scale-in: cannot terminate a server with active
  connections without breaking them. Options: (1) use
  scale-in protection while connections are active -
  only allow termination when the server has drained
  to 0 active connections (natural drain over time);
  (2) implement connection migration (complex - move
  WebSocket state to new server before termination);
  (3) accept brief disconnection and implement client-
  side reconnect logic
- In practice: most WebSocket services use scale-in
  protection and rely on natural drain + client
  reconnect as the most pragmatic solution
