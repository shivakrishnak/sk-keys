---
id: MSV-067
title: Canary Deployment
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-020, MSV-010, MSV-065
used_by: MSV-066, MSV-068
related: MSV-068, MSV-066, MSV-010, MSV-020, MSV-065, MSV-078
tags:
  - microservices
  - devops
  - deep-dive
  - deployment
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /microservices/canary-deployment/
---

# MSV-067 - Canary Deployment

⚡ TL;DR - Canary Deployment: deploy a new version
to a SMALL percentage of production traffic (5-10%)
before promoting to all users. Named after "canary
in a coal mine": if the canary (small traffic slice)
shows problems (elevated error rate, latency
regression), roll back before all users are
affected. Implemented via: Kubernetes + Argo
Rollouts or Istio VirtualService traffic splitting.
Key metrics: error rate, p99 latency, business
metrics (conversion rate). If metrics stable after
observation window: promote to 100%. If degraded:
automatic or manual rollback.

| #067 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Mesh, Service Discovery, OpenTelemetry in Microservices | |
| **Used by:** | Chaos Engineering, Zero-Downtime Deployment | |
| **Related:** | Zero-Downtime Deployment, Chaos Engineering, Service Discovery, Service Mesh, OpenTelemetry in Microservices, Service Mesh Traffic Management | |

---

### 🔥 The Problem This Solves

**BIG-BANG DEPLOYMENT RISK:**
Deploy new version to 100% of traffic at once.
If the new version has a bug: 100% of users
immediately affected. Rollback: 5-10 minutes
(re-deploy old version). Total incident duration:
5-15 minutes of 100% error rate. At 1000 RPS:
300,000-900,000 failed requests. Canary:
only 5% of users see the new version first.
If bug: 95% of users unaffected. Rollback:
instantaneous (just shift traffic back).

---

### 📘 Textbook Definition

**Canary Deployment** is a progressive delivery
strategy where a new software version is released
to a small subset (the "canary") of production
users or traffic first, while the majority
continues running the previous stable version.
The canary is monitored for errors, performance
regressions, and business metric anomalies. If
the canary is healthy: traffic percentage is
gradually increased (5% -> 20% -> 50% -> 100%).
If the canary shows problems: traffic is shifted
back to the stable version (rollback) with minimal
impact. Implementation approaches: (1) Kubernetes
native (run 1 canary pod alongside 9 stable pods
= ~10% canary traffic); (2) Service mesh (Istio
VirtualService: weight-based routing); (3) Argo
Rollouts (controller that automates progressive
delivery with metric analysis); (4) Feature flags
(user-level canary for specific users regardless
of infrastructure). Variants: blue/green deployment
(two full environments, instant switch), A/B
testing (different features, not versions; based
on user attributes).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Canary: deploy to 5% of traffic, watch metrics,
promote if healthy or rollback if not. Limits
blast radius of bad deployments.

**One analogy:**
> Pharmaceutical drug trials: Phase I (5%: small
> group of healthy volunteers). Phase II (larger
> group; verify efficacy). Phase III (large, diverse
> group). Full approval (100% population). Canary
> deployment: the same staged rollout for software.
> Phase I (5% canary): find critical bugs. Phase
> II (20%): verify performance at scale. Phase III
> (50%): validate business metrics. Full rollout
> (100%): only after each phase confirms safety.
> Rollback: immediately remove the drug from trial
> if adverse effects detected (rollback deployment).

**One insight:**
Canary deployment's value is not the technical
mechanism (traffic splitting) but the OBSERVATION
window it creates. Deploying to 5% is not useful
if you're not measuring anything during those 15
minutes. The value: you have 15 minutes with real
production traffic to detect issues before they
affect everyone. Without metrics: you're just
slowing down your deployment for no benefit. With
metrics: you're running a scientific validation
experiment on your deployment.

---

### 🔩 First Principles Explanation

```
CANARY TRAFFIC ROUTING:

  KUBERNETES NATIVE APPROACH:
  2 Deployments: stable (9 replicas) + canary (1)
  K8s Service: selects all pods with app=order-service
  Result: ~10% traffic to canary pod (1 of 10)
  Limitation: coarse-grained (10%, 20%, not 5%)

  ISTIO VIRTUAL SERVICE APPROACH:
  1 Deployment: stable (v1.4, 10 replicas)
  1 Deployment: canary (v2.0, 10 replicas)
  Istio VirtualService:
    weight: 95 -> v1.4 stable
    weight:  5 -> v2.0 canary
  Result: exactly 5% to canary (regardless of
          number of pods)
  Fine-grained: set any weight (1%, 5%, 0.5%)

  ARGO ROLLOUTS APPROACH:
  CRD (Rollout instead of Deployment)
  ProgressiveDelivery controller:
    step 1: setWeight: 5 (5% to canary)
    step 2: pause: {duration: 15m} (observation)
    step 3: setWeight: 20 (analysis)
    step 4: pause: {duration: 15m}
    step 5: setWeight: 100 (full rollout)
  AnalysisTemplate: automated metric checks
    - error rate < 1%: continue
    - error rate > 1%: abort rollback

CANARY ANALYSIS METRICS:
  Technical:
  - HTTP 5xx error rate vs stable baseline
  - p50/p95/p99 response latency vs stable
  - JVM heap usage (memory leak detection)
  - CPU usage (unexpected computation increase)
  
  Business:
  - Conversion rate (orders/visitors)
  - Cart abandonment rate
  - Payment success rate
  - User session duration
  
  Business metrics: catch bugs that don't produce
  errors but cause wrong behavior
  (e.g., pricing bug: no errors but revenue drops)
```

---

### 🧪 Thought Experiment

**CANARY CATCHES PERFORMANCE REGRESSION:**

```
SCENARIO: New order-service version (v2.1)
  Change: added customer preference analysis
          (calls ML model for each order)
  Developer: tested locally, all unit tests pass
  Canary: 5% of traffic
  
  METRICS DURING CANARY (15 minutes):
  Error rate: 0.02% (baseline: 0.02%) - SAME
  HTTP 5xx: 0 - SAME  
  p50 latency: 145ms (baseline: 120ms) - ELEVATED
  p99 latency: 2100ms (baseline: 180ms) - 12x WORSE
  
  Argo Rollouts AnalysisTemplate:
    p99 > 500ms: FAIL
    -> automatically aborts rollout
    -> traffic: shifts back to v2.0 stable
    -> rollback: instantaneous (Istio weight: 0% to v2.1)
  
  Impact:
    Users affected by degraded p99: 5% for 15 minutes
    (those who got canary traffic)
    Users not affected: 95%
  
  WITHOUT CANARY:
    Deploy to 100% production
    p99 latency: 2100ms for ALL users
    Customers: experience 2-second loading
    E-commerce: 2s latency = 20% conversion drop
    Revenue impact: significant
    Investigation + fix + deploy: 45 minutes
    
  ROOT CAUSE FOUND:
    ML model call: synchronous in request path
    ML service: p99 latency 1950ms under prod load
    Fix: async ML call; cache results; use
         async feature flags
```

---

### 🧠 Mental Model / Analogy

> Canary deployment is like a new restaurant dish.
> Before adding it to the full menu: the chef
> offers it as a "special" (canary) to a few tables.
> If those tables enjoy it (healthy metrics): add
> to the menu (promote to 100%). If those tables
> send it back (errors or negative feedback):
> remove the special before it reaches all customers.
> Only 5-10% of customers (the canary tables)
> experience the uncertainty. The remaining 90-95%
> get the trusted menu (stable version).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Deploy new software to 5% of users. Watch for
problems. If no problems: deploy to everyone.
If problems: roll back. Only 5% of users see the
potentially buggy version.

**Level 2 - How to implement (junior developer):**
Simplest: 9 pods running v1.4, 1 pod running v2.0.
Kubernetes Service selects both. ~10% traffic
to new version. Monitor: `kubectl top pods`,
check Grafana for error rate. Promote: scale v2.0
to 10, scale v1.4 to 0.

**Level 3 - Service mesh canary (mid-level):**
Istio VirtualService: `weight: 5` to canary,
`weight: 95` to stable. Advantages: any percentage,
not limited by pod count. Can target specific
users (header-based routing: `x-canary: true`
routes to canary regardless of weight). Argo
Rollouts: automates the entire process (setWeight
steps, pause durations, automated metric analysis).

**Level 4 - Automated promotion (senior engineer):**
Argo Rollouts `AnalysisTemplate`: runs continuously
during canary phase. Queries Prometheus: `rate
(http_requests_total{status=~"5..",version="canary"}[5m])
/ rate(http_requests_total{version="canary"}[5m])
< 0.01`. If passes: automatic promotion (next
step). If fails: automatic rollback. No human
intervention needed for happy path.

**Level 5 - Progressive delivery at scale (principal):**
Flagger (Weaveworks): Kubernetes operator for
progressive delivery. Integrates with Istio, Nginx,
Traefik, AWS ALB. Metrics providers: Prometheus,
Datadog, CloudWatch. Progressive delivery vs
canary: Flagger supports not just canary but A/B
testing (user attribute routing), blue/green
(clone environment), and Kubernetes Deployment
progressive rollout. Feature flags as canary
(LaunchDarkly/Unleash): canary at the user level
without Kubernetes changes. Useful when canary
needs to target specific user segments (beta
users, internal users) rather than random traffic %.

---

### ⚙️ How It Works (Mechanism)

```yaml
# ARGO ROLLOUTS: automated progressive delivery
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-service
  namespace: production
spec:
  replicas: 10
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:2.1.0  # new version
  strategy:
    canary:
      # Istio traffic management
      trafficRouting:
        istio:
          virtualService:
            name: order-service-vs
            routes:
            - primary
      # Automated metric analysis
      analysis:
        templates:
        - templateName: error-rate-analysis
        startingStep: 1
      steps:
      - setWeight: 5     # Step 1: 5% canary
      - analysis:        # Step 2: run metric analysis
          templates:
          - templateName: error-rate-analysis
      - pause: {duration: 15m}  # Step 3: observe
      - setWeight: 20    # Step 4: 20% canary
      - pause: {duration: 15m}  # Step 5: observe
      - setWeight: 50    # Step 6: 50% canary
      - pause: {duration: 15m}  # Step 7: observe
      # If all steps pass: promotes to 100% automatically
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-analysis
spec:
  metrics:
  - name: success-rate
    successCondition: result[0] <= 0.01  # <1% error rate
    failureCondition: result[0] > 0.05   # >5% = abort
    interval: 1m
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{
            service="order-service",
            version="canary",
            status_code=~"5.."
          }[5m]))
          /
          sum(rate(http_requests_total{
            service="order-service",
            version="canary"
          }[5m]))
  - name: latency-p99
    successCondition: result[0] <= 500
    failureCondition: result[0] > 2000
    interval: 1m
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket{
              service="order-service",
              version="canary"
            }[5m])) * 1000
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CANARY DEPLOYMENT LIFECYCLE:

  Git push: order-service v2.1 image
  |
  v
  CI: build + unit tests + Pact contracts
  |
  v
  Argo CD: detects new image tag in Helm chart
  Applies: Rollout resource update
  |
  v
  Argo Rollouts controller:
  Step 1: deploy v2.1 canary pod
  Step 2: update Istio VirtualService: 5% -> v2.1
  Step 3: start AnalysisRun (query Prometheus)
  |
  v
  AnalysisRun: every 1 minute for 15 minutes
  Check: canary error rate < 1%
  Check: canary p99 < 500ms
  |
  Result A: All checks PASS
    setWeight: 20% -> 50% -> 100%
    v2.0 pods: scaled to 0
    Deployment: complete (no human needed)
  |
  Result B: error rate > 5% FAIL
    Argo Rollouts: automatic rollback
    Istio: setWeight v2.1 -> 0%
    v2.1 pods: scaled to 0
    Alert: "Canary rollback triggered: error rate 7%"
    On-call: notified
    Only 5% of traffic affected during canary phase
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: pod-count canary vs Istio weight canary**

```yaml
# BAD: pod-count canary - coarse, cannot do 1-5%
# stable: 9 replicas, canary: 1 replica = 10%
# minimum is 10% (1/10 pods)
# Cannot test at 1% or 5% traffic first
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-canary
spec:
  replicas: 1  # ~10% traffic (1 of 10 total pods)
  # Problem: at 100 pods, 1 canary = only 1%
  # but at 10 pods, 1 canary = 10% (may be too much)
  # coarse-grained; no fine control
```

```yaml
# GOOD: Istio VirtualService - exact weight control
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service-vs
spec:
  hosts:
  - order-service
  http:
  - route:
    - destination:
        host: order-service
        subset: stable  # v1.4
      weight: 95  # 95% to stable
    - destination:
        host: order-service
        subset: canary  # v2.1
      weight: 5   # 5% to canary (exact)
    # Can set: 1%, 0.5%, any percentage
    # Independent of pod count
```

---

### ⚖️ Comparison Table

| Strategy | Traffic Control | Rollback Speed | Risk | Complexity |
|---|---|---|---|---|
| **Big-bang deploy** | All at once | Minutes (re-deploy) | High | Low |
| **Canary (pod count)** | ~10% min | Instant | Low-Medium | Low |
| **Canary (Istio weights)** | Any % | Instant | Very low | Medium |
| **Canary (Argo Rollouts)** | Any %, automated | Instant (automated) | Very low | Medium-High |
| **Blue/Green** | 0% or 100% | Instant | Low | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Canary deployment guarantees zero impact | Canary reduces blast radius but doesn't eliminate it. 5% canary at 1000 RPS = 50 requests/second to canary. If canary crashes: 50 RPS of errors. For 15 minutes: 45,000 failed requests. For a payments API: 45,000 failed payment attempts is significant. Canary's value: 50 RPS of errors vs 1000 RPS of errors. Design canary percentage based on acceptable error count, not just percentage. |
| Canary is only for backend services | Canary is equally valuable (and more complex) for frontend. Mobile apps: cannot force user to update; A/B testing via feature flags. Web frontend: canary via CDN (serve new JS bundle to 5% of users via cookie or request hash). The principle: progressive delivery with metric observation applies to any user-facing software component. |
| Canary replaces integration testing | Canary is a production validation step, not a replacement for pre-production testing. It catches issues that can only be detected with real production traffic (specific user data patterns, real load, third-party service behavior). Pre-production testing still required for functional correctness, security, and correctness of business logic. Canary adds: production load validation and blast radius control. |

---

### 🚨 Failure Modes & Diagnosis

**Canary metrics look healthy but issue in stable version**

**Symptom:**
Canary deployed. Metrics: all healthy (error rate,
latency within bounds). Canary promotes to 100%.
5 minutes after full rollout: error rate spikes
to 15%. Rollback initiated. Canary appeared healthy.

**Root Cause:**
The bug is NOT in the canary code - it's triggered
by a database migration that ran with the canary
deployment. Migration: added a new column with
a NOT NULL constraint. Old version (stable pods)
try to INSERT without that column: SQL constraint
violation. Old pods: throwing errors. Canary pods
(with migration-aware code): working fine.

Metrics during canary: looked at CANARY error rate.
Stable error rate: also rising. Alert: should have
been watching OVERALL error rate, not just canary.

**Fix:**
1. Always watch TOTAL error rate (stable + canary)
   during canary phase, not only canary metrics.
2. Database migrations: must be backward-compatible
   (NOT NULL column -> first add as nullable, backfill,
   then add constraint in separate migration).
3. AnalysisTemplate: add metric for overall error
   rate, not just version=canary filtered metric.

---

### 🔗 Related Keywords

**Canary requires traffic management:**
- `Service Mesh Traffic Management` - Istio/Linkerd
  provide the traffic splitting infrastructure

**Related deployment strategies:**
- `Zero-Downtime Deployment` - canary is one
  technique for zero-downtime deployment
- `Chaos Engineering` - run chaos on canary
  before promoting to validate resilience

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ Deploy to 5% -> monitor -> promote/rollback│
│              │ Named after canary in coal mine           │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Argo Rollouts (automate), Istio VS (exact%)│
│              │ Flagger (Weaveworks progressive delivery)  │
├──────────────┼───────────────────────────────────────────┤
│ METRICS      │ Error rate, p99 latency, business KPIs    │
│              │ Monitor stable + canary during rollout    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Small traffic slice; real prod metrics;  │
│              │  promote or rollback with confidence"     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Deploy to 5% of traffic first. Measure error
   rate and p99 latency against baseline. Promote
   to 100% if healthy; rollback immediately if not.
2. Tools: Argo Rollouts (automated canary with
   metric gates), Istio VirtualService (fine-grained
   traffic weights, e.g., exact 5%).
3. Watch BOTH canary AND stable metrics during
   rollout. DB migrations or shared changes can
   cause stable version errors that look like
   canary health.

**Interview one-liner:**
"Canary deployment: new version gets 5% of traffic;
if error rate and p99 latency stay within threshold
(Prometheus metric), Argo Rollouts auto-promotes
(5% -> 20% -> 50% -> 100%); if metrics degrade,
auto-rollback (instant: Istio VirtualService weight
back to 0%). Advantage over blue/green: gradual
rollout catches performance regressions at increasing
load; much lower blast radius than big-bang deploy.
Business metrics (conversion rate, payment success
rate) should also be monitored - catches behavioral
bugs that don't produce HTTP errors."

---

### 💡 The Surprising Truth

The most valuable metric in a canary deployment
is often NOT the technical metric (error rate,
latency) but the BUSINESS metric (conversion rate,
revenue per session). A pricing bug: doesn't cause
HTTP 500 errors (returns 200 OK with wrong price).
A recommendation algorithm regression: no errors,
but users click fewer products (lower revenue).
Technical canary metrics would show "all clear".
Business canary metrics would catch it. Teams
that instrument business metrics in their canary
analysis find bugs that technical metrics miss.
The investment: a few Prometheus counters on
business events (order_created_total, cart_checkout_
started_total) + AnalysisTemplate comparing
canary vs stable conversion rates.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **ARGO** Write a complete Argo Rollout resource
   with Istio traffic management, 4-step canary
   progression (5% -> 20% -> 50% -> 100%),
   AnalysisTemplate querying Prometheus for error
   rate and p99 latency.
2. **ISTIO** Write Istio VirtualService and
   DestinationRule for canary: 5% to canary subset,
   95% to stable. Verify: kubectl describe virtualservice
   shows correct weights.
3. **ROLLBACK** Diagnose the stable-version-errors-
   during-canary failure: why stable pods were
   throwing errors, how to detect it (metrics
   filter), how to prevent it (backward-compatible
   DB migrations).
4. **BUSINESS METRICS** Add business canary
   analysis: Prometheus counter `order_conversion_
   rate` per version label. AnalysisTemplate:
   canary conversion rate within 5% of stable
   conversion rate.
5. **COMPARE** Explain when to use canary vs
   blue/green vs feature flags: what are the
   trade-offs for each, and which scenarios favor
   each strategy?

---

### 🧠 Think About This Before We Continue

**Q1.** You are deploying order-service v2.1 with
a database migration that adds a required field
`estimated_delivery_date` to the orders table.
The old version (v1.9) doesn't write this field.
You want to use canary deployment. What is the
migration strategy that allows both v1.9 and v2.1
to run simultaneously during the canary phase
without errors? Write the migration steps.

**Q2.** Your canary AnalysisTemplate measures:
canary error rate vs stable error rate. The analysis
passes (both 0.1%). Canary promotes to 100%.
30 minutes later: customer support reports that
"premium" users are experiencing checkout failures.
Regular users: no issues. The bug: premium-user
checkout path has a bug only triggered by a new
payment method added to the canary. How would you
modify your canary analysis to catch user-segment-
specific bugs?

**Q3.** Debate: "We should use feature flags instead
of canary deployment for safer releases." Present
both sides: what problems do feature flags solve
that canary doesn't, what problems does canary
solve that feature flags don't, and what is the
optimal combination for a high-traffic e-commerce
platform that deploys 10 times per day?