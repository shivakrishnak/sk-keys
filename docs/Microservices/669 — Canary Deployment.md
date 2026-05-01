---
layout: default
title: "Canary Deployment"
parent: "Microservices"
nav_order: 669
permalink: /microservices/canary-deployment/
number: "669"
category: Microservices
difficulty: ★★☆
depends_on: "Zero-Downtime Deployment, Load Balancing"
used_by: "Blue-Green Deployment, Feature Flags, Graceful Shutdown"
tags: #intermediate, #microservices, #devops, #distributed, #reliability
---

# 669 — Canary Deployment

`#intermediate` `#microservices` `#devops` `#distributed` `#reliability`

⚡ TL;DR — **Canary Deployment** gradually rolls a new version to a small percentage of users (5-10%) first, monitoring error rates and latency. If metrics stay healthy, traffic is incrementally increased to 100%. If metrics degrade, rollback instantly by routing all traffic back to the old version. Minimizes blast radius of bad deployments.

| #669            | Category: Microservices                                 | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Zero-Downtime Deployment, Load Balancing                |                 |
| **Used by:**    | Blue-Green Deployment, Feature Flags, Graceful Shutdown |                 |

---

### 📘 Textbook Definition

**Canary Deployment** is a deployment strategy (named after the "canary in a coal mine" concept) where a new version of a service is deployed alongside the existing version, and a small fraction of live traffic (e.g., 5%) is routed to the new version while the remainder (95%) continues to the old version. Monitoring metrics (error rates, latency percentiles, business KPIs) are observed during the canary phase. If metrics remain within acceptable bounds, traffic is progressively increased (5% → 25% → 50% → 100%) at configurable intervals — either manually or automatically via a release automation tool (Argo Rollouts, Flagger). If metrics degrade at any stage, the deployment is immediately halted and traffic shifted back to 100% old version (rollback). Canary deployments reduce deployment risk by: limiting blast radius (only N% of users experience potential issues), validating new code under real production traffic and load patterns (which pre-production environments cannot fully replicate), and enabling automated promotion/rollback decisions based on observed metrics (progressive delivery).

---

### 🟢 Simple Definition (Easy)

Deploy the new version to just 5% of users. Watch how it performs. If error rates go up → roll back, only 5% of users were affected. If everything is fine → slowly give more users the new version. Full deploy with minimum risk.

---

### 🔵 Simple Definition (Elaborated)

v1.5.0 fixes a bug and adds a new feature. You're not sure the new feature has a performance issue. Canary: deploy v1.5.0, send 5% of requests to it. Monitor Grafana: error rate 0.1% (acceptable), p99 latency 450ms (acceptable). After 30 minutes: increase to 25%. Monitor: all good. Increase to 50%. At 50%: p99 latency spikes to 2000ms — new feature has N+1 query bug. Rollback: send 100% to v1.4.0 instantly. Only 50% of traffic saw the slow period. No incident declared. Fix the N+1 bug, redeploy canary.

---

### 🔩 First Principles Explanation

**Traffic splitting mechanics:**

```
OPTION 1: LOAD BALANCER WEIGHTS (nginx, Istio, AWS ALB):
  v1 deployment: 3 replicas
  v2 deployment: 1 replica (canary)
  Load balancer: 75%/25% weight split

  Kubernetes Ingress (nginx):
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "5"  # 5% to new version

OPTION 2: ISTIO VIRTUAL SERVICE (fine-grained):
  apiVersion: networking.istio.io/v1alpha3
  kind: VirtualService
  metadata:
    name: order-service
  spec:
    hosts: [order-service]
    http:
    - route:
      - destination:
          host: order-service-v1
        weight: 95
      - destination:
          host: order-service-v2  # canary
        weight: 5
  → Change weight to 25/75/100 progressively without redeploying

OPTION 3: ARGO ROLLOUTS (Kubernetes-native progressive delivery):
  apiVersion: argoproj.io/v1alpha1
  kind: Rollout
  spec:
    strategy:
      canary:
        steps:
        - setWeight: 5
        - pause: {duration: 10m}  # monitor for 10 minutes
        - setWeight: 25
        - pause: {duration: 10m}
        - setWeight: 50
        - pause: {}               # manual approval gate
        - setWeight: 100
        canaryMetadata:
          labels:
            role: canary
        analysis:
          templates:
          - templateName: error-rate-check  # auto-rollback if error rate > 1%
```

**Automated analysis — when to proceed vs rollback:**

```yaml
# Argo Rollouts AnalysisTemplate:
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
spec:
  metrics:
    - name: error-rate
      interval: 1m
      failureLimit: 2 # fail experiment if metric fails twice
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_server_requests_total{
              app="order-service", status=~"5..", version="v2"
            }[2m]))
            /
            sum(rate(http_server_requests_total{
              app="order-service", version="v2"
            }[2m]))
      successCondition: result[0] <= 0.01 # error rate must be <= 1%
      failureCondition: result[0] > 0.05 # fail immediately if > 5%

    - name: p99-latency
      interval: 1m
      failureLimit: 2
      provider:
        prometheus:
          query: |
            histogram_quantile(0.99,
              rate(http_server_requests_seconds_bucket{
                app="order-service", version="v2"
              }[2m]))
      successCondition: result[0] <= 0.5 # p99 must be <= 500ms
      failureCondition: result[0] > 1.0 # fail if p99 > 1 second
```

**Canary vs user cohort targeting:**

```
RANDOM TRAFFIC SPLIT (default):
  Random 5% of all requests → new version
  Pros: simple, no state
  Cons: same user may hit v1 on one request, v2 on next
        Creates inconsistent UX for features that change UI

STICKY SESSIONS / USER COHORT (better UX):
  Route based on user ID hash → always same version for same user
  5% of users: always go to v2 (for their entire session)
  95% of users: always stay on v1

  Istio:
  spec:
    http:
    - match:
      - headers:
          x-user-id:
            regex: ".*[0-4]$"  # users with ID ending in 0-4 → v2 (50% example)
      route:
      - destination: {host: order-service-v2}

  Feature flags (LaunchDarkly / Unleash):
  → Targeting by user ID, cohort, geography, account type
  → More granular than traffic weight (send canary only to beta users, internal staff, etc.)
```

---

### ❓ Why Does This Exist (Why Before What)

Deployments fail. Even with unit tests, integration tests, and staging environments, new code sometimes misbehaves under real production traffic patterns that tests can't replicate. Canary deployment limits the cost of a bad deployment to a small percentage of users rather than 100%, and enables observation under real conditions before committing fully.

---

### 🧠 Mental Model / Analogy

> Canary deployment is like a new menu item at a restaurant. Instead of replacing the entire menu and finding out customers hate it, you offer the new dish to 5 tables as a "special." Watch the feedback: any complaints? Any leftover food? If well received: add it to the full menu. If disaster: remove it from the specials, only 5 tables were disappointed. Your regular menu (v1) remains available to everyone else.

---

### ⚙️ How It Works (Mechanism)

**Kubernetes Deployment with Argo Rollouts — complete canary config:**

```yaml
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
          image: myrepo/order-service:v2.0.0 # new version
  strategy:
    canary:
      stableService: order-service-stable
      canaryService: order-service-canary
      trafficRouting:
        istio:
          virtualService:
            name: order-service-vsvc
      steps:
        - setWeight: 5
        - pause: { duration: 15m }
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 25
        - pause: { duration: 15m }
        - setWeight: 100
```

---

### 🔄 How It Connects (Mini-Map)

```
Zero-Downtime Deployment
(deployment without user impact)
        │
        ▼
Canary Deployment  ◄──── (you are here)
(gradual traffic shift to new version)
        │
        ├── Blue-Green Deployment → alternative strategy (all-or-nothing swap)
        ├── Feature Flags → enable targeted feature rollout without deployment
        └── Load Balancing → the mechanism for traffic weight splitting
```

---

### 💻 Code Example

**Manual canary with kubectl (without Argo Rollouts):**

```bash
# Deploy v2 as a separate Deployment with 1 replica:
kubectl apply -f order-service-v2.yaml  # 1 replica of v2

# v1 deployment: 9 replicas
# v2 deployment: 1 replica
# → Load balancer distributes 10/90 = 10% to v2 (by replica count)
# This only works if Service selector matches BOTH deployments:
# selector: app: order-service  (both v1 and v2 have this label)

# Monitor error rates for 15 minutes...
# If OK: scale v2 to 5 replicas, scale v1 to 5 → 50/50
kubectl scale deployment order-service-v2 --replicas=5
kubectl scale deployment order-service-v1 --replicas=5

# If not OK: scale v2 to 0 (instant rollback):
kubectl scale deployment order-service-v2 --replicas=0
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Canary deployment is the same as blue-green           | Blue-green: two full environments, instant switch (all or nothing). Canary: one environment, gradual percentage increase. Key difference: blue-green provides instant full rollback; canary provides gradual validation with partial rollback possible at each stage                           |
| 5% canary traffic is always enough to detect problems | 5% is sufficient for high-traffic services (1M req/day → 50K canary requests). For low-traffic services (1K req/day → 50 canary requests), a 5% canary may not generate enough traffic to produce statistically significant error rate measurements. Adjust percentage based on traffic volume |
| Canary deployment eliminates deployment risk entirely | Canary deployment reduces risk. Some issues only manifest at specific data states, user actions, or load patterns not in the 5% canary traffic. Canary + feature flags + chaos engineering together form a comprehensive risk reduction strategy                                               |

---

### 🔥 Pitfalls in Production

**Database migration incompatibility with canary:**

```
SCENARIO:
  v2 code requires new database column: orders.discount_code (NOT NULL)
  Schema migration runs before canary: ALTER TABLE + adds column
  Canary v2: works correctly (uses new column)
  v1: still running (95% of traffic) → INSERT query fails (missing column in INSERT)
  Incident: 95% of orders failing

ROOT CAUSE: Schema migration deployed simultaneously with canary
  → v1 code doesn't know about new column → NULL inserted → constraint violated

CORRECT APPROACH (expand-contract migration):
  Phase 1: Add column as NULLABLE (no constraint):
    ALTER TABLE orders ADD COLUMN discount_code VARCHAR(50) NULL
    Deploy v2 canary → v2 writes discount_code; v1 inserts NULL (no error)

  Phase 2: Canary promotion → v2 at 100%
    All traffic on v2. All rows now have discount_code populated.

  Phase 3 (after v1 is retired): Add NOT NULL constraint
    ALTER TABLE orders ALTER COLUMN discount_code SET NOT NULL
    Safe: all rows already have values populated by v2

RULE: Database migrations in canary deployments must be backward-compatible
      with the PREVIOUS version of the service code.
```

---

### 🔗 Related Keywords

- `Blue-Green Deployment` — alternative deployment strategy (instant switch, not gradual)
- `Feature Flags` — enable targeted rollout without a new deployment
- `Zero-Downtime Deployment` — the broader goal that canary helps achieve
- `Load Balancing` — the traffic weighting mechanism canary relies on

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGY     │ 5% → monitor → 25% → 50% → 100%          │
│ TRAFFIC SPLIT│ Istio VirtualService or nginx ingress      │
│ AUTOMATION   │ Argo Rollouts + Prometheus analysis        │
├──────────────┼───────────────────────────────────────────┤
│ ROLLBACK     │ Set traffic weight to 0% → instant        │
│ METRICS      │ Error rate, p99 latency, business KPIs    │
├──────────────┼───────────────────────────────────────────┤
│ DB MIGRATIONS│ Must be backward-compatible (expand-contract)│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your canary deployment is at 25% traffic for `PaymentService` v2. After 20 minutes, Argo Rollouts analysis shows: v2 error rate = 0.8% (below 1% threshold, acceptable), but v2 p99 latency = 950ms (below 1s threshold, technically acceptable). However, your business KPI shows v2 checkout completion rate is 2% lower than v1. The Prometheus metric doesn't capture this business metric. How do you incorporate business KPIs (checkout completion rate from your analytics system) into Argo Rollouts automated analysis? What is the data pipeline from your business analytics to Argo Rollouts decision engine?

**Q2.** A canary deployment scenario: you have 100 Kubernetes pods of `order-service`. v1: 90 pods, v2 (canary): 10 pods (10% traffic). A critical security vulnerability is discovered in v1 that must be patched immediately. The canary v2 includes the security fix. Do you: (a) promote the canary immediately to 100%, skipping the remaining canary validation steps, (b) run the canary analysis on an accelerated timeline, or (c) redeploy v2 as a separate emergency patch? What are the operational risks of each option, and what criteria determine which you choose?
