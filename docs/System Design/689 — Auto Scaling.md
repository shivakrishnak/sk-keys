---
layout: default
title: "Auto Scaling"
parent: "System Design"
nav_order: 689
permalink: /system-design/auto-scaling/
number: "689"
category: System Design
difficulty: ★★☆
depends_on: "Horizontal Scaling, Vertical Scaling"
used_by: "Capacity Planning"
tags: #intermediate, #cloud, #distributed, #architecture, #reliability
---

# 689 — Auto Scaling

`#intermediate` `#cloud` `#distributed` `#architecture` `#reliability`

⚡ TL;DR — **Auto Scaling** automatically adjusts the number of compute instances based on load metrics (CPU, traffic, queue depth), adding capacity during peaks and removing it during troughs to control cost and maintain performance.

| #689            | Category: System Design              | Difficulty: ★★☆ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Horizontal Scaling, Vertical Scaling |                 |
| **Used by:**    | Capacity Planning                    |                 |

---

### 📘 Textbook Definition

**Auto Scaling** is the capability of a computing system to automatically provision or de-provision compute resources (virtual machines, containers, functions) in response to changes in load, without manual intervention. Auto scaling is driven by scaling policies: either **reactive** (scale when a metric crosses a threshold, e.g., CPU > 70%) or **predictive** (scale in anticipation of known traffic patterns, e.g., business hours). **Scale-out** (adding instances) handles increased load; **scale-in** (removing instances) reduces cost when load decreases. Auto scaling policies are configured with: minimum capacity (floor), maximum capacity (ceiling), desired capacity (target), cooldown periods (to prevent thrashing), and warm-up times (time for new instances to be ready). AWS Auto Scaling Groups, Kubernetes Horizontal Pod Autoscaler (HPA), and Google Cloud Instance Groups implement this concept at different levels of abstraction.

---

### 🟢 Simple Definition (Easy)

Auto Scaling automatically adds more servers when traffic is high and removes them when traffic drops. Like a restaurant adding more waitstaff during the dinner rush and sending them home after closing time — but done automatically based on how busy it is, without a manager having to make the call manually.

---

### 🔵 Simple Definition (Elaborated)

At 9 AM, your API gets 100 requests per minute — 2 servers are enough. At 2 PM, 10,000 requests per minute — you need 20 servers. At 11 PM, 50 requests per minute — 2 servers again. Auto Scaling watches metrics (CPU usage, request queue depth, latency) and automatically adds servers when load rises and removes them when it falls. The benefit: you pay for capacity only when you need it, and you don't have to manually provision during traffic spikes.

---

### 🔩 First Principles Explanation

**Why auto scaling exists — cost vs. capacity trade-off:**

```
STATIC PROVISIONING (before auto scaling):
  Problem: when to provision for peak traffic?

  OPTION A: Provision for average load
    Peak traffic: servers overwhelmed → degraded performance / outages
    Failure: during Black Friday, Christmas sale, viral events

  OPTION B: Provision for peak load
    Average: 10 servers needed
    Peak:    100 servers needed
    Provision: 100 servers always running
    Cost: paying for 90 servers 23 hours/day (idle capacity)
    Cloud cost: 100 × $0.10/hr × 8,760 hr/yr = $87,600/year
    vs.   10 × $0.10/hr × 8,760 hr/yr = $8,760/year (average need)
    Waste: $78,840/year — 90% cost overhead for peak readiness

  OPTION C: Auto Scaling (dynamic provisioning)
    Scale OUT when needed (peak): provision 100 servers for 4 hours/day
    Scale IN when load drops: de-provision back to 10 servers
    Cost: roughly:
      10 servers × 20 hours × $0.10 = $20/day (off-peak)
      100 servers × 4 hours × $0.10 = $40/day (peak)
      Total: $60/day = $21,900/year
    vs. static peak: $87,600/year
    Savings: ~75% cost reduction at same peak capacity

AUTO SCALING TRIGGER TYPES:

  1. TARGET TRACKING (recommended):
     "Maintain CPU at 50%"
     Algorithm: continuously adjusts capacity to hit target.
     Scale out: CPU rises above 50% → add instances
     Scale in: CPU falls below 50% → remove instances
     AWS: TargetTrackingScalingPolicy
     K8s: HPA with targetCPUUtilizationPercentage: 50

  2. STEP SCALING (threshold-based):
     CPU 60-70% → add 1 instance
     CPU 70-80% → add 2 instances
     CPU 80-90% → add 4 instances
     CPU >90%   → add 8 instances (aggressive scale-out for danger zone)
     Configured as step adjustments for fine-grained control.

  3. SCHEDULED SCALING (predictive):
     "Add 10 instances at 8:30 AM every weekday (before business hours)"
     "Remove 10 instances at 8 PM every weekday"
     Pre-warms capacity before predictable load spikes.
     Used when traffic pattern is known and consistent.

  4. PREDICTIVE SCALING (ML-based):
     AWS Predictive Scaling: analyses historical CloudWatch metrics.
     Forecasts future load 48 hours ahead using ML.
     Pre-provisions capacity before load arrives.
     Better than reactive: avoids scale-out lag when load spikes suddenly.

COOLDOWN PERIODS AND SCALE-IN PROTECTION:

  Cooldown: after a scale-out, wait 300 seconds before another scale-out.
  Why: new instances take 2-5 minutes to start, register, and warm up.
  Without cooldown: CPU still high (new instances not warm yet) →
    triggers another scale-out → over-provisions.

  Scale-in protection: during scale-in, don't terminate instances with
    active in-flight requests.
  AWS: Connection Draining (ALB): wait for connections to complete before
    marking instance as deregistered.
    aws ec2 modify-instance-attribute --instance-id i-xxx
      --no-instance-initiated-shutdown-behavior

WARM-UP TIME (critical for sticky sessions + caching apps):

  New instance: cold (empty local cache, no JIT compilation, no connection pool).
  First requests on new instance: slower than steady state.

  AWS: Instance Warm-Up Period in scaling policy.
    During warm-up: instance's metrics not counted toward scaling triggers.
    Prevents: warm-up load from triggering another scale-out.

  K8s HPA: readinessProbe gates traffic until application is ready:
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      initialDelaySeconds: 30  # wait 30s before first check
      periodSeconds: 10        # check every 10s
    # Pod receives traffic only when readinessProbe passes
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Auto Scaling:

- Static provisioning: either under-provisioned (outages at peak) or over-provisioned (cost waste)
- Traffic spikes: either manual emergency scaling (slow, error-prone) or pre-built headroom (expensive)
- Off-peak hours: idle servers still running and costing money

WITH Auto Scaling:
→ Automatic adaptation to demand: right capacity at right time
→ Cost reduction: pay only for what you use
→ Reliability: prevents resource exhaustion under unexpected load spikes

---

### 🧠 Mental Model / Analogy

> A call centre that automatically calls in more agents when the call queue gets long, and sends them home when it gets short. The supervisor (auto scaling policy) watches the queue length (metric). When queue > threshold (trigger): call more agents (scale out). When queue is short: tell agents to go home (scale in). The manager sets the rules (scaling policy), not the staffing decisions themselves.

"Supervisor" = auto scaling controller
"Agents" = EC2 instances / pods
"Call queue length" = scaling metric (CPU, request queue depth)
- "Queue > threshold → call agents" = scale-out policy trigger
"Agents going home" = scale-in / instance termination

---

### ⚙️ How It Works (Mechanism)

**Kubernetes Horizontal Pod Autoscaler (HPA):**

```yaml
# HPA: scale Deployment based on CPU utilisation
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 2 # always at least 2 pods (HA)
  maxReplicas: 20 # never more than 20 (cost ceiling)
  metrics:
    # Target: keep average CPU at 50% across all pods
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
    # Also scale on custom metric: requests per second per pod
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100" # target: 100 rps per pod
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0 # react immediately to scale-out need
      policies:
        - type: Percent
          value: 100 # double pods if needed
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300 # wait 5 min before scale-in
      policies:
        - type: Pods
          value: 1 # remove at most 1 pod at a time
          periodSeconds: 60 # conservative scale-in
---
# Deployment resource limits (required for HPA CPU metric):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  template:
    spec:
      containers:
        - name: api
          resources:
            requests:
              cpu: "250m" # HPA calculates utilisation relative to request
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
```

---

### 🔄 How It Connects (Mini-Map)

```
Vertical Scaling         Horizontal Scaling
(bigger instance)        (more instances)
        │                       │
        └───────────┬───────────┘
                    ▼ (automation layer)
              Auto Scaling ◄──── (you are here)
              (reactive or predictive scaling)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Load Balancing           Capacity Planning
  (distributes traffic     (auto scaling informs
  to scaled instances)     capacity requirements)
```

---

### 💻 Code Example

**AWS Auto Scaling Group with Target Tracking:**

```python
# boto3: create Auto Scaling Group with target tracking policy
import boto3

autoscaling = boto3.client('autoscaling', region_name='us-east-1')

# 1. Create Auto Scaling Group
autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='api-service-asg',
    LaunchTemplate={
        'LaunchTemplateName': 'api-service-lt',
        'Version': '$Latest'
    },
    MinSize=2,         # minimum: 2 instances always running (HA)
    MaxSize=50,        # maximum: cost ceiling
    DesiredCapacity=2, # starting capacity
    VPCZoneIdentifier='subnet-xxx,subnet-yyy,subnet-zzz',  # multi-AZ
    TargetGroupARNs=['arn:aws:elasticloadbalancing:...'],   # ALB integration
    HealthCheckType='ELB',        # use ALB health checks (not EC2 status)
    HealthCheckGracePeriod=300,   # 5 min grace period for new instances
    TerminationPolicies=['OldestInstance']  # remove oldest instances first
)

# 2. Add Target Tracking Policy (maintain 50% CPU)
autoscaling.put_scaling_policy(
    AutoScalingGroupName='api-service-asg',
    PolicyName='cpu-target-tracking',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization'
        },
        'TargetValue': 50.0,    # target: 50% average CPU
        'ScaleInCooldown': 300, # wait 5 min before removing instances
        'ScaleOutCooldown': 60  # wait 1 min before adding more instances
    }
)
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                                                    |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auto Scaling works instantly during traffic spikes   | Instance launch takes 2-5 minutes (AMI boot + app startup + health check). During a sudden spike, you're unprotected for those minutes. Mitigation: pre-warm with scheduled scaling, maintain a buffer above baseline, or use faster-starting containers (Fargate, Lambda) |
| Auto Scaling eliminates the need for load balancing  | Auto Scaling adds/removes instances; a Load Balancer is still needed to distribute traffic across the varying pool. They work together: Auto Scaling controls pool size, Load Balancer controls traffic distribution                                                       |
| You should scale in aggressively to save costs       | Aggressive scale-in risks: removing instances that still have active connections (session loss); leaving insufficient capacity for sudden re-spikes. Recommended: slow, conservative scale-in (remove 1 instance per minute) with long stabilisation windows (5 minutes)   |
| Auto Scaling handles database capacity automatically | Auto Scaling is for stateless compute. Databases have their own scaling approaches: read replicas, vertical scaling, Aurora Serverless (auto-scales), connection pooling. Auto Scaling of app servers + non-scaled DB = DB becomes the bottleneck                          |

---

### 🔥 Pitfalls in Production

**Auto scaling thrashing — rapid scale-out/in cycles:**

```
PROBLEM:
  Scaling policy: scale out when CPU > 70%.
  Application: spiky load pattern.

  T=0:  2 instances, CPU=75% → scale out → now 4 instances
  T=1m: 4 instances, CPU=38% (load distributed) → cool down period
  T=5m: CPU=72% → scale out → now 6 instances
  T=6m: CPU=30% → scale in → back to 4 instances
  T=10m: CPU=71% → scale out again...

  Thrashing: constant scale out/in → costs money, instances launching/terminating
              continuously → increased risk of instance launch failures.

  Symptom: CloudWatch shows zigzag instance count (2→4→2→4→2→4)

FIX 1: Use Target Tracking (instead of simple threshold)
  Target: maintain CPU at 50%
  Algorithm: calculates required capacity mathematically
  desiredInstances = ceil(currentInstances × currentCPU / targetCPU)
  = ceil(2 × 75% / 50%) = ceil(3) = 3 instances
  → smoother scaling, no thrashing

FIX 2: Increase stabilisation window for scale-in:
  scaleIn.stabilizationWindowSeconds: 600  # 10 minutes
  → Only scale in if CPU has been LOW for 10 consecutive minutes
  → Prevents scale-in triggered by a brief CPU dip during scale-out transient

FIX 3: Step scaling with aggressive scale-out, conservative scale-in:
  Scale out: immediate, large steps (fast response to load)
  Scale in:  slow, 1 instance at a time, with 5-minute wait per step

  # K8s HPA behavior (as shown in mechanism section):
  scaleUp.stabilizationWindowSeconds: 0    # immediate
  scaleDown.stabilizationWindowSeconds: 300 # 5-minute cooldown
```

---

### 🔗 Related Keywords

- `Horizontal Scaling` — the mechanism auto scaling uses (add/remove instances)
- `Vertical Scaling` — alternative to horizontal auto scaling (upsize instance); less common for auto scaling
- `Load Balancing` — required partner: distributes traffic to the auto-scaled pool
- `Capacity Planning` — auto scaling policies are informed by capacity analysis and forecasting
- `Least Connections` — load balancer algorithm that works well with auto-scaled pools (routes to least-loaded instances)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Automatically add/remove instances based  │
│              │ on metrics (CPU, RPS, queue depth)        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Variable/unpredictable traffic; cost      │
│              │ optimisation; cloud-native workloads      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Stateful apps without session migration;  │
│              │ boot-time > SLA; DB can't absorb spike    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hire more staff when the queue grows,    │
│              │  send them home when it clears."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Capacity Planning → Predictive Scaling    │
│              │ → Kubernetes KEDA                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your e-commerce platform has a flash sale every Monday at 12 PM that drives 50× normal traffic for exactly 15 minutes, then returns to baseline. Your EC2 instances take 4 minutes to boot and register with the load balancer. Design a combined reactive + scheduled + predictive auto scaling strategy that ensures: (a) sufficient capacity available at 12:00:00 PM when the sale starts, (b) scale-in doesn't begin too early (sale ends at 12:15 but you don't know exactly when), and (c) no thrashing during the cool-down period. Specify exact times, triggers, and cooldown values.

**Q2.** Kubernetes HPA scales pods based on CPU utilisation. Your application pods run a background job that uses 30% CPU regardless of HTTP traffic volume. The HTTP-serving component uses CPU proportional to traffic. Design a custom metric-based HPA that correctly scales based on HTTP traffic only, ignoring the background job's CPU. What metric would you expose, how would you configure the HPA, and what Kubernetes tooling would you use to scrape and expose this custom metric to HPA?
