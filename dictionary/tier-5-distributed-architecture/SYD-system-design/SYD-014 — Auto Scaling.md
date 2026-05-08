---
layout: default
title: "Auto Scaling"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /system-design/auto-scaling/
id: SYD-014
category: System Design
difficulty: ★★☆
depends_on: Horizontal Scaling, Load Balancing, Monitoring
used_by: Cloud Systems, Microservices, Production Infrastructure
related: Horizontal Scaling, Load Balancing, Capacity Planning
tags:
  - scaling
  - automation
  - infrastructure
  - cloud
  - intermediate
---

# SYD-014 — Auto Scaling

⚡ TL;DR — Automatically adding or removing servers based on real-time load metrics (CPU, memory, request count) without manual intervention—enables systems to handle traffic spikes while controlling costs during low-traffic periods.

| #689            | Category: System Design                               | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Horizontal Scaling, Load Balancing                    |                 |
| **Used by:**    | Cloud Infrastructure, Microservices, Web Services     |                 |
| **Related:**    | Horizontal Scaling, Capacity Planning, Load Balancing |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You deploy 10 servers for Black Friday traffic. It's November—you have 100 daily users. The 10 servers are 99% idle, costing $10K/day. After Black Friday, traffic returns to 100 users/day, but your 10 servers keep running (you forgot to scale down). December bill: $300K for unused capacity. Nightmare.

**THE BREAKING POINT:**
Manual scaling is too slow for rapid traffic changes. Humans are slow; traffic spikes happen in minutes. You either over-provision (expensive) or under-provision (bad user experience).

**THE INVENTION MOMENT:**
"This is why auto-scaling was invented—automatically add servers when load spikes, remove them when traffic drops."

---

### 📘 Textbook Definition

Auto-scaling (automatic scaling or elasticity) is a cloud infrastructure feature that dynamically adjusts the number of running instances based on predefined metrics and rules. When metrics (CPU, memory, request count) exceed thresholds, new instances are launched. When metrics drop below thresholds, instances are terminated. Typically implemented in cloud platforms (AWS EC2 Auto-scaling Groups, Kubernetes HPA, Azure VM Scale Sets) and requires a load balancer to distribute traffic across the dynamic pool.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When things get busy, rent more computers. When they slow down, return the computers and stop paying for them.

**One analogy:**

> A movie theater hires more staff on weekends when crowds are large, fewer staff on weekdays. They don't hire 200 people and have most sit idle Tuesday afternoon. They scale up and down based on demand. Auto-scaling is doing that, automatically.

**One insight:**
Auto-scaling is only possible with horizontal scaling and a load balancer. If your app can't scale horizontally, auto-scaling is useless. Conversely, horizontal scaling without automation is tedious.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Metrics are available in real-time (CPU, memory, network, request count)
2. New servers can be provisioned quickly (minutes, not hours)
3. Servers are stateless (or state is shared), so new servers are immediately useful
4. Applications must handle varying server counts transparently

**DERIVED DESIGN:**
The auto-scaling orchestrator monitors metrics continuously. When average CPU across the pool exceeds (say) 70% for 5 minutes, a rule triggers: launch N new instances. These new instances join the load balancer's pool automatically (health checks verify they're ready). When CPU drops below 20% for 10 minutes, a rule terminates underutilized instances. The system "breathes"—expanding under load, contracting during lulls.

**THE TRADE-OFFS:**
**Gain:** Cost efficiency—pay for capacity you actually use. Handles traffic spikes automatically. Reduces manual operations.

**Cost:** Complexity—rules are hard to tune (when to scale? how many instances?). Scaling has latency (new instance takes 1–5 minutes to be ready). Can cascade (scaling events trigger more scaling events if not careful).

---

### 🧪 Thought Experiment

**SETUP:**
A web API deployed to AWS. During normal hours (9 AM–6 PM): 1000 requests/second. Current: 5 servers, 200 req/s capacity each. At midnight: traffic drops to 10 requests/second (1% of peak). Costs: 5 servers × $0.096/hour = $0.48/hour always.

**WITHOUT AUTO-SCALING:**
9 AM: Traffic spikes to 1000 req/s. Existing 5 servers maxed (100% CPU). Requests queue. Latency increases 10x. Users see errors. Manual ops team called. Takes 20 minutes to provision new servers (during which incident ongoing). Total: $0.48/hour × 24 hours = $11.52/day waste.

**WITH AUTO-SCALING:**
9 AM: Traffic spikes. Auto-scaler detects CPU > 70% for 5 minutes. Launches 10 new servers automatically. After 2 minutes, new servers join pool. Traffic distributes. Latency returns to normal.
Midnight: Traffic drops. Auto-scaler detects CPU < 20%. Terminates 10 servers. Keeps minimum 2 servers for residual traffic.
Cost: ~$0.48/hour during peak, ~$0.19/hour at night. Total: $0.48 × 16 + $0.19 × 8 = $9.28/day (77% savings).

**THE INSIGHT:**
Auto-scaling is about matching capacity to demand dynamically. Done right, it saves money and improves user experience.

---

### 🧠 Mental Model / Analogy

> A delivery service has trucks (servers). On Monday, they need 2 trucks for light delivery. Friday, they need 10 trucks for holiday shopping. They don't buy and maintain 10 trucks year-round (too expensive). They lease trucks dynamically—rent more on Friday, return them Monday. Auto-scaling = automatic truck leasing based on delivery volume.

- "Trucks" → servers
- "Delivery volume" → traffic / requests per second
- "Leasing vs buying" → cost efficiency through elasticity
- "Demand forecast" → metrics (CPU, request count)
- "Automatic rental/return" → auto-scaling rules

**Where this analogy breaks down:** Trucks take days to acquire; cloud servers take minutes. Trucks don't warm up in parallel; cloud can scale simultaneously.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When lots of users arrive, the system automatically spins up more computers to handle them. When users leave, it shuts down extra computers to save money. No human decides when—rules automated.

**Level 2 — How to use it (junior developer):**
Configure an auto-scaling group (ASG) in your cloud provider. Set rules: if average CPU > 70% for 5 minutes, add 2 servers. If CPU < 30% for 10 minutes, remove 1 server. Set min=2, max=20 servers. Deploy your application. It scales automatically.

**Level 3 — How it works (mid-level engineer):**
The cloud provider runs an orchestrator. Every minute, it fetches metrics from all servers in the ASG (e.g., CloudWatch). Computes aggregate (average CPU). Evaluates rules: if avg_cpu > threshold and duration > cooldown, trigger ScaleUp (add instances). If avg_cpu < threshold and duration > cooldown, trigger ScaleDown (terminate instances). New instances are launched from a template (AMI, Docker image) with the app pre-installed. They receive traffic after health checks pass (~2 minutes). Terminating instances: graceful shutdown (drain existing connections first), then terminate.

**Level 4 — Why it was designed this way (senior/staff):**
Auto-scaling emerged as cloud computing commoditized resources (2010s). Before cloud, buying servers meant 3–6 month procurement. With cloud, provisioning is instant. The capability made elasticity valuable. Amazon (AWS) pioneered auto-scaling; now all cloud providers have it. The fundamental insight: capacity should be dynamic, not static. This drove the adoption of horizontal scaling, stateless design, and container orchestration (Kubernetes).

---

### ⚙️ How It Works (Mechanism)

Auto-scaling operation:

```
SETUP: Define Auto-Scaling Group (ASG)
  Min instances: 2
  Max instances: 20
  Desired: 5 (initial)
  Scale-up rule: CPU > 70% for 5 min → add 2 instances
  Scale-down rule: CPU < 30% for 10 min → remove 1 instance
  Cooldown: 300 seconds (prevent rapid flapping)

CONTINUOUS MONITORING:
  Every 1 minute:
    1. Fetch metrics from all instances
    2. Compute aggregate (e.g., avg CPU)
    3. Evaluate rules
    4. If rule triggers, execute action (after cooldown)

EXAMPLE TRACE:
  T=0min: 5 instances, avg CPU = 20% → Idle
  T=5min: Traffic arrives, avg CPU = 65% → Still below threshold
  T=10min: avg CPU = 75% for 5 consecutive minutes → THRESHOLD HIT
  T=11min: Rule triggered (cooldown elapsed). Launch 2 new instances.
    New instances boot (2–3 min). Health checks verify.
  T=14min: 7 instances running. Traffic distributes. Avg CPU = 50%.
  T=15min: avg CPU = 45%
  ...
  T=30min: Traffic drops. avg CPU = 15% for 10 consecutive minutes → THRESHOLD HIT
  T=31min: Rule triggered. Terminate 1 instance (graceful drain).
  T=36min: 6 instances running. Cooldown prevents further termination.
  T=50min: avg CPU = 12% for 20 minutes → THRESHOLD HIT again.
  T=51min: Terminate 1 instance.
  Final: 5 instances (desired count).
```

**In Happy Path:**
Traffic spike → Auto-scale up → Requests handled → Cost controlled.

**When Something Goes Wrong:**
Rule misbehaved. Threshold too low → constant scaling (flapping). Minimum too low → can't handle failure of one server.

---

### 🔄 The Complete Picture — End-to-End Flow

```
User Traffic Arrives
    ↓
Load Balancer distributes to N servers
    ↓
METRICS COLLECTION (YOU ARE HERE)
Orchestrator polls CPU, memory, request count
    ↓
Rule Evaluation
    ├─ CPU > threshold for duration? → ScaleUp
    ├─ CPU < threshold for duration? → ScaleDown
    └─ Within cooldown? → No action
    ↓
ScaleUp Path:
    Launch new instances
    ↓ (2–5 min provisioning)
    Health checks pass
    ↓
    Add to load balancer pool
    ↓
    Traffic routes to new instances

ScaleDown Path:
    Identify instance to terminate
    ↓
    Drain existing connections (graceful)
    ↓
    Remove from load balancer pool
    ↓
    Terminate instance
    ↓
    Save cost
```

**WHAT CHANGES AT SCALE:**
At 1000 req/s with scale-up events every hour, launching 5 instances each time is routine. At 100,000 req/s, scaling is massive (100s of instances launching/terminating). Orchestrator becomes CPU-intensive. Cloud providers optimize (batching, parallel launches). Cooldown periods become critical—prevent cascading failures if multiple rules trigger.

---

### 💻 Code Example

Auto-scaling is configured, not coded, but examples:

**Example 1 — AWS EC2 Auto Scaling Group (Terraform):**

```terraform
resource "aws_autoscaling_group" "api" {
    name = "api-asg"
    max_size = 20
    min_size = 2
    desired_capacity = 5

    vpc_zone_identifier = ["subnet-1a", "subnet-1b"]

    launch_configuration = aws_launch_configuration.api.name

    health_check_type = "ELB"
    health_check_grace_period = 300

    tag {
        key = "Name"
        value = "api-server"
        propagate_at_launch = true
    }
}

# Scale-up policy: add 2 instances when CPU > 70%
resource "aws_autoscaling_policy" "scale_up" {
    name = "scale-up"
    adjustment_type = "ChangeInCapacity"
    adjustment_magnitude = 2
    autoscaling_group_name = aws_autoscaling_group.api.name
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
    alarm_name = "high-cpu"
    metric_name = "CPUUtilization"
    threshold = 70
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods = 1  # 1 minute
    period = 60

    alarm_actions = [aws_autoscaling_policy.scale_up.arn]
}

# Scale-down policy: remove 1 instance when CPU < 30%
resource "aws_autoscaling_policy" "scale_down" {
    name = "scale-down"
    adjustment_type = "ChangeInCapacity"
    adjustment_magnitude = -1
    autoscaling_group_name = aws_autoscaling_group.api.name
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
    alarm_name = "low-cpu"
    metric_name = "CPUUtilization"
    threshold = 30
    comparison_operator = "LessThanThreshold"
    evaluation_periods = 10  # 10 minutes
    period = 60

    alarm_actions = [aws_autoscaling_policy.scale_down.arn]
}
```

**Example 2 — Kubernetes Horizontal Pod Autoscaler (HPA):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300 # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 50 # Remove 50% of pods
    scaleUp:
      stabilizationWindowSeconds: 0 # Scale up immediately
      policies:
        - type: Percent
          value: 100 # Add 100% more pods
```

**Example 3 — Custom Python Auto-scaling Logic (Pseudocode):**

```python
import boto3
import time

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')
asg_name = 'api-asg'

while True:
    # Fetch current ASG state
    response = asg_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name]
    )
    asg = response['AutoScalingGroups'][0]
    current_count = len(asg['Instances'])

    # Fetch metrics
    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Statistics=['Average'],
        Period=60,
        StartTime=datetime.utcnow() - timedelta(minutes=5),
        EndTime=datetime.utcnow()
    )
    avg_cpu = sum(m['Average'] for m in metrics['Datapoints']) / len(metrics['Datapoints'])

    # Evaluate rules
    if avg_cpu > 70 and current_count < 20:
        asg_client.set_desired_capacity(DesiredCapacity=current_count + 2)
        print(f"Scale up: {current_count} → {current_count + 2} (CPU={avg_cpu}%)")
    elif avg_cpu < 30 and current_count > 2:
        asg_client.set_desired_capacity(DesiredCapacity=current_count - 1)
        print(f"Scale down: {current_count} → {current_count - 1} (CPU={avg_cpu}%)")

    time.sleep(60)  # Check every minute
```

---

### ⚖️ Comparison Table

| Scaling Approach       | Setup Effort                | Flexibility             | Cost                             | Speed                   | Best For                              |
| ---------------------- | --------------------------- | ----------------------- | -------------------------------- | ----------------------- | ------------------------------------- |
| **Auto-scaling**       | Medium (rules to configure) | High (multiple metrics) | Excellent (pay-per-use)          | Fast (2–5 min)          | Production systems, variable load     |
| **Manual Scaling**     | Low (just add servers)      | Low (human decision)    | Poor (over-provisioned)          | Slow (10–30 min)        | Small systems, predictable load       |
| **Reserved Instances** | Medium (forecast capacity)  | Low (fixed pool)        | Good (discount for commitment)   | Instant                 | Stable baseline load                  |
| **Scheduled Scaling**  | High (forecasting)          | Medium (pre-planned)    | Excellent (avoid surprise peaks) | Very fast (pre-planned) | Known traffic patterns (daily/weekly) |

**How to choose:** Use auto-scaling for cloud systems with variable load. Use reserved instances for baseline + auto-scaling for spikes. Use manual scaling only for small or static deployments.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                    |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| "Auto-scaling is instant"                   | New instances take 2–5 minutes to provision. Metrics have lag. Scale-up events aren't immediate.           |
| "Auto-scaling handles all traffic spikes"   | If spike exceeds max capacity before new instances boot, queuing/errors still occur. Set max high enough.  |
| "Auto-scaling saves money on all workloads" | Only saves money if load varies significantly. Stable, high load → reserved instances are cheaper.         |
| "Auto-scaling requires no tuning"           | Rules require careful tuning (threshold, duration, cooldown). Wrong rules cause flapping or under-scaling. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Scaling Thrashing (Flapping)**

**Symptom:**
Instances added, removed, added, removed constantly. Orchestrator logs show repeated scale-up/down events every few minutes. Load balancer connections drop as instances churn. Clients see connection errors.

**Root Cause:**
Scale-up threshold too close to scale-down threshold. Or cooldown too short. When scaling up, new instances bring CPU down momentarily. Scale-down rule triggers. Instances removed. Moment later, scale-up triggers again. Endless loop.

**Diagnostic Command:**

```bash
# Check ASG scaling history
aws autoscaling describe-scaling-activities --auto-scaling-group-name api-asg | tail -20

# Check metric trend
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --period 60 \
  --statistics Average \
  --start-time (1 hour ago) --end-time now
```

**Fix:**
Bad approach: Ignore and accept thrashing.
Good approach: (1) Increase cooldown (e.g., 300–600 seconds). (2) Increase gap between thresholds (70% up, 30% down, not 50/45). (3) Use different metrics (request count, not just CPU). (4) Implement "sticky" scaling decisions—don't reverse immediately.

**Prevention:**
Set cooldown appropriately. Test auto-scaling rules with simulated load before production. Monitor scaling events; alert on > 5 events per hour.

---

**Failure Mode 2: Max Capacity Reached, Traffic Still Growing**

**Symptom:**
Traffic spike. Auto-scaler launches instances until max (20 servers). But traffic keeps growing. New requests queue, latencies spike. System at max capacity but still overwhelmed.

**Root Cause:**
Max capacity too low for the traffic volume. Or scaling didn't happen fast enough (new instances took too long to provision).

**Diagnostic Command:**

```bash
# Check current ASG state
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-name api-asg | grep DesiredCapacity

# Check if at max
if desired_capacity == max_capacity:
    echo "At max capacity; requests queuing"

# Check instance launch lag
aws ec2 describe-instances | grep LaunchTime | tail -5
# If all recent: took time to scale up
```

**Fix:**
Bad approach: Increase max capacity and hope.
Good approach: (1) Analyze actual capacity needed for predicted traffic. (2) Increase max if needed. (3) Pre-warm instances before expected spike (scheduled scaling). (4) Use burst instances (AWS Spot, Azure Spot) for cost-effective scaling.

**Prevention:**
Capacity planning before launch. Run load tests to determine max needed. Monitor request queue depth. Alert before hitting max.

---

**Failure Mode 3: Cascading Failure on Scale-Down**

**Symptom:**
Traffic drops. Auto-scaler removes instances. One of the instances being removed had a critical service (DB cache warm-up). Removing it causes cascade: remaining instances become slower (cold cache). Metrics spike. Scale-up rule triggers immediately. Flapping.

**Root Cause:**
Auto-scaling doesn't know about implicit dependencies. Removing one instance has side effects (cold caches, connection pools re-establish).

**Diagnostic Command:**

```bash
# Check instance roles
aws ec2 describe-instances | grep Tags | grep -E "special|db-cache"

# Check if removing instance causes metric spike
aws autoscaling describe-scaling-activities | grep -E "Terminate|Launch"
# Correlate terminate with metric spike

# Check application logs for cache misses
grep "cache.*miss" /var/log/app.log | tail -100 | \
  awk '{print $1}' | sort | uniq -c
```

**Fix:**
Bad approach: Disable scale-down to prevent cascades.
Good approach: (1) Mark special instances (don't scale down). (2) Implement graceful degradation—system works with fewer instances, just slower. (3) Scale down gradually (1 instance at a time, wait for metrics). (4) Use connection draining—let instances finish work before removal.

**Prevention:**
Design applications to handle gradual resource reduction. Don't rely on specific instances for warmth. Use distributed caches. Implement comprehensive health checks beyond /health endpoint.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Horizontal Scaling` — the underlying technique that auto-scaling automates
- `Load Balancing` — required to distribute traffic to new instances
- `Monitoring` — provides metrics that trigger scaling decisions

**Builds On This (learn these next):**

- `Capacity Planning` — forecasting to set auto-scaling parameters
- `Circuit Breaker` — handles cascading failures during scale events
- `Graceful Shutdown` — connection draining on scale-down

**Alternatives / Comparisons:**

- `Manual Scaling` — operator-driven, not automated
- `Reserved Instances` — for stable baseline load
- `Scheduled Scaling` — predictable patterns, not reactive

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automatically add/remove servers     │
│              │ based on real-time metrics           │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Manual scaling is slow; traffic      │
│ SOLVES       │ spikes happen faster than humans     │
│              │ can provision                        │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Only works with horizontal scaling   │
│              │ and stateless design; rules need     │
│              │ careful tuning                       │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Traffic is variable; horizontal      │
│              │ scaling possible; costs matter       │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Load is constant; scaling takes      │
│              │ hours (not minutes); or app is       │
│              │ stateful and can't scale            │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Cost savings, handles spikes] vs    │
│              │ [complexity, tuning effort, lag]     │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Machines automatically show up for  │
│              │ busy times, leave when quiet."       │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Capacity Planning → Scheduled        │
│              │ Scaling → Circuit Breaker            │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Auto-scaling launches new instances based on CPU > 70%. But what if the spike is transient (1 second spike, then drops)? New instances take 2 minutes to launch. By the time they're ready, traffic has passed. Worse, now you have excess capacity that triggers scale-down. How do you avoid this wasted provisioning?

**Q2.** An instance is marked for termination (graceful shutdown). It drains existing connections but takes 5 minutes. During those 5 minutes, other instances become overloaded (one less in the pool). Their CPU spikes, triggering scale-up. New instances launch. But the terminating instance finally completes, and scale-down triggers again. How do you coordinate these events to prevent thrashing?
