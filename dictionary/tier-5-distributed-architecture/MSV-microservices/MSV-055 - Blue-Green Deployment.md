---
layout: default
title: "Blue-Green Deployment"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /microservices/blue-green-deployment/
id: MSV-055
category: Microservices
difficulty: ★★☆
depends_on: Zero-Downtime Deployment, Load Balancer, Kubernetes
used_by: Zero-Downtime Deployment, Canary Deployment (Microservices)
related: Canary Deployment (Microservices), Rolling Update, Feature Flags (Microservices)
tags:
  - microservices
  - deployment
  - operations
  - intermediate
status: complete
version: 1
---

# MSV-055 - Blue-Green Deployment

⚡ TL;DR - Blue-green deployment maintains two identical production environments (blue = live, green = idle). New version is deployed to the idle environment; traffic is switched instantly. Rollback is a one-command traffic switch back.

| #670            | Category: Microservices                                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Zero-Downtime Deployment, Load Balancer, Kubernetes                              |                 |
| **Used by:**    | Zero-Downtime Deployment, Canary Deployment (Microservices)                      |                 |
| **Related:**    | Canary Deployment (Microservices), Rolling Update, Feature Flags (Microservices) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every deployment causes 2–5 minutes of downtime: stop old pods; pull new image; start new pods. Alternatively, you do rolling updates - but these take 15 minutes across 50 pods, and if a problem appears, rollback takes another 15 minutes. For a service SLA of 99.9% (8.7 hours downtime/year budget), a 15-minute rollback event costs 2.9% of your annual downtime budget - for a single deployment.

**THE BREAKING POINT:**
Rollback speed is the critical difference between a 5-minute incident and a 30-minute incident. Rollback must be instant or as close to it as possible.

**THE INVENTION MOMENT:**
Blue-green deployment separates deployment (to the idle environment) from release (traffic switch). Deployment can take 10 minutes (spinning up new version on green). Release is instantaneous (change load balancer to point at green). Rollback is equally instantaneous (change load balancer back to blue).


**EVOLUTION:**
Blue-Green deployment was described by Martin Fowler and popularised in Jez Humble and David Farley's 'Continuous Delivery' (2010) as a pattern for zero-downtime deployments. The pattern pre-dates microservices (used with monoliths and SOA) but became prominent with microservices due to higher deployment frequency. Cloud infrastructure made it operationally feasible by making duplicate environments cheap. Kubernetes Service objects and load balancer integrations made blue-green a native platform capability. The discipline evolved from a manual 'swap the load balancer' operation to automated, tested, rollback-capable deployment pipelines.
---

### 📘 Textbook Definition

**Blue-green deployment** is a release strategy that uses two identical, parallel production environments: **blue** (currently serving traffic) and **green** (idle, used for new version deployment). The new version is deployed and validated on the green environment while blue continues to serve all traffic. When green is ready, a load balancer rule switch routes all traffic from blue to green - instantly. Blue remains running and idle, enabling instant rollback by switching traffic back. Eventually, blue is updated and becomes the next idle environment for the following deployment.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Keep a spare identical environment ready; deploy to the spare; flip a switch to make it live; keep the old one running for instant rollback.

**One analogy:**

> Railway signal switching. Train line A (blue) is the active line. A new track B (green) is prepared in parallel. When track B is ready and validated, the switch flips: all trains now run on track B. If track B has a problem, flip the switch back to track A - instantly. Trains never stop; only the track they run on changes.

**One insight:**
The key property of blue-green is that **deployment is decoupled from release**. You deploy to green at your leisure. Release is one atomic switch. Rollback is the same one atomic switch in reverse.

---

### 🔩 First Principles Explanation

**THE TIMELINE:**

```
T=0:  Blue = v1 (live, 100% traffic)
      Green = idle (running v1)

T=5:  Deploy v2 to Green:
      Green = v2 (deployed, 0% traffic)
      Blue  = v1 (live, 100% traffic)

T=15: Validate Green (smoke tests, health checks)
      Green = v2 (validated, 0% traffic)
      Blue  = v1 (live, 100% traffic)

T=16: TRAFFIC SWITCH
      Green = v2 (live, 100% traffic) ← new "blue"
      Blue  = v1 (idle) ← ready for rollback

T+1h: If all good, decommission v1 on Blue
      Deploy next version to Blue for next release cycle
```

**THE TRAFFIC SWITCH MECHANICS:**

| Infrastructure     | Switch Mechanism                                                     |
| ------------------ | -------------------------------------------------------------------- |
| AWS                | Update ELB/ALB target group; Route 53 DNS swap                       |
| Kubernetes         | Update `Service` selector label (`version: blue` → `version: green`) |
| Nginx              | Upstream switch via config reload                                    |
| Istio/Service Mesh | VirtualService weight: blue=0, green=100                             |

**KUBERNETES SERVICE LABEL SWITCH:**

```yaml
# Blue deployment: pods labelled version: blue
# Green deployment: pods labelled version: green
# Service always targets `app: order-service`

# Switch: update Service selector
spec:
  selector:
    app: order-service
    version: green # ← was: blue
```

**THE TRADE-OFFS:**
**Gain:** Instant rollback (one switch); zero-downtime; deployment validation on a separate environment before release; no mixed-version serving during rollout.
**Cost:** Double infrastructure cost during transition (two full environments); database schema changes require extra care (both blue and green share the same DB); DNS-based switching has TTL propagation delay.

---

### 🧪 Thought Experiment

**SETUP:**
You deploy to green and switch traffic. Green serves 100% for 30 minutes. A critical bug is discovered in the new version (green v2).

**WITHOUT BLUE-GREEN:**
Rollback = re-deploy v1 from image registry. Steps: pull image → create pods → wait for readiness → update deployment. Time: 5–10 minutes.

**WITH BLUE-GREEN:**
Rollback = switch traffic selector back to blue (v1). Time: 5–30 seconds (Kubernetes Service update propagation). Blue has been running idle the whole time; it's already warm, already connected to dependencies. All in-flight requests on green drain; new requests immediately go to blue.

**THE SUBTLETY:**
If the v2 deployment wrote new data to the database (in the 30 minutes it served traffic), rollback to v1 means: v1 now reads data that v2 wrote. If v2 changed data format (backwards-incompatible), v1 will have problems reading that data. Blue-green does not solve database migration; it solves application rollback. Schema changes must be backward-compatible.

---

### 🧠 Mental Model / Analogy

> Blue-green deployment is like having two dressing rooms backstage. The performer (new version) gets ready in room B (green) while the show continues with the current performer in room A (blue, on stage). When B is ready, the director signals the switch: B walks on stage, A walks off. The audience (users) barely notices the transition. If B stumbles on the way to the stage, A is immediately available to return.

- "Stage" → live production traffic
- "Dressing room" → idle environment
- "Two dressing rooms" → blue and green environments
- "Director signals switch" → load balancer rule change
- "A immediately available to return" → instant rollback

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Two copies of your system, running side by side. The new copy is deployed and tested. When ready, all users are moved from the old copy to the new one instantly. If something goes wrong, move them back just as fast.

**Level 2 - Kubernetes implementation (junior developer):**
Create two `Deployment` objects (`order-service-blue`, `order-service-green`). Both run; one has `replicas: 10`, the other `replicas: 0` (or `replicas: 10` but not in the Service selector). The `Service` selector switches between `version: blue` and `version: green`. Switching is one `kubectl patch service` command.

**Level 3 - Database migration handling (mid-level engineer):**
Blue-green requires the new version (green) to be compatible with the database schema that blue also uses. This requires the expand-contract pattern: (1) expand the schema additively (add column, keep old column); (2) deploy green using both old and new columns; (3) once blue is decommissioned, contract the schema (remove old column). This ensures blue and green can coexist against the same database schema.

**Level 4 - Production blue-green at scale (senior/staff):**
At large scale, blue-green becomes expensive: 2× infrastructure cost is significant. The optimisation: run green at reduced capacity (e.g., 20% of full capacity), then scale out green and scale down blue simultaneously during the switch. Some teams use blue-green for stateless services and rolling update for stateful services. Another consideration: blue-green doesn't easily support gradual rollout (only 0% or 100%). For gradual rollout, canary deployment is superior. Many organisations use a hybrid: canary (gradual) during staging → blue-green (instant switch) for production release.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│   Blue-Green - Kubernetes Flow                          │
└─────────────────────────────────────────────────────────┘

Service: selector: {version: blue}
  ↓ routes to → Blue Pods (v1): ready, serving 100%
  ↓ routes to → Green Pods: none (selector doesn't match)

STEP 1: Deploy v2 to Green
  kubectl set image deployment/order-service-green \
    order-service=order-service:v2

STEP 2: Wait for Green pods to be Ready
  kubectl rollout status deployment/order-service-green

STEP 3: Run smoke tests against Green (bypassing Service)
  curl -H "Host: order-service-green" green-pod-ip/health

STEP 4: SWITCH (atomic, instant)
  kubectl patch service order-service \
    -p '{"spec":{"selector":{"version":"green"}}}'

  Service: selector: {version: green}
    ↓ routes to → Green Pods (v2): now serving 100%
    ↓ routes to → Blue Pods: idle, available for rollback

ROLLBACK (if needed):
  kubectl patch service order-service \
    -p '{"spec":{"selector":{"version":"blue"}}}'
  → Instant: Blue pods are warm and ready
```

---

### 💻 Code Example

```yaml
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-blue
spec:
  replicas: 10
  selector:
    matchLabels:
      app: order-service
      version: blue
  template:
    metadata:
      labels:
        app: order-service
        version: blue # ← key label
    spec:
      containers:
        - name: order-service
          image: order-service:v1

---
# Green deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-green
spec:
  replicas: 10
  selector:
    matchLabels:
      app: order-service
      version: green
  template:
    metadata:
      labels:
        app: order-service
        version: green # ← key label
    spec:
      containers:
        - name: order-service
          image: order-service:v2 # new version

---
# Service - points to blue OR green via label selector
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
    version: blue # ← change to 'green' to switch
  ports:
    - port: 80
      targetPort: 8080
```

**Switch command:**

```bash
# Deploy to green, validate, then switch:
kubectl patch service order-service \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback:
kubectl patch service order-service \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

### ⚖️ Comparison Table

| Strategy       | Traffic Split        | Rollback Speed          | Infrastructure Cost | Gradual Rollout |
| -------------- | -------------------- | ----------------------- | ------------------- | --------------- |
| **Blue-Green** | 0%/100% switch       | Instant                 | 2× during switch    | No              |
| Canary         | 1%→100% graduated    | Seconds (rollout abort) | 1.1× during canary  | Yes             |
| Rolling Update | Gradual (pod by pod) | Minutes (re-deploy)     | 1×                  | Yes             |
| Recreate       | 0% (downtime)        | Full re-deploy          | 1×                  | No              |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Blue-green handles database schema changes automatically | It does not - both environments share the same DB; schema must be backward-compatible                               |
| Blue-green always means double cost                      | Cost only doubles during the transition window; after decommissioning old env, cost normalises                      |
| DNS-based blue-green is always instant                   | DNS TTL means full propagation can take minutes to hours; prefer LB-based switching for instant effect              |
| You can't do both blue-green and canary                  | Many organisations combine them: canary for gradual validation, blue-green for final switch and rollback capability |

---

### 🚨 Failure Modes & Diagnosis

**Old Blue Pods Receiving Traffic After Switch**

**Symptom:** After switching selector to green, some requests still go to blue pods.

**Root Cause:** kube-proxy hasn't propagated the endpoint change yet; iptables rules are stale.

**Fix:** Add `terminationGracePeriodSeconds: 30` to blue pods; they'll drain in-flight requests gracefully. New requests immediately go to green after propagation (typically < 1 second in cluster).

---

### 🔗 Related Keywords

**Prerequisites:** `Zero-Downtime Deployment`, `Load Balancer`, `Kubernetes`

**Builds On This:** `Canary Deployment (Microservices)`, `Zero-Downtime Deployment`

**Related Patterns:** `Canary Deployment (Microservices)`, `Rolling Update`, `Feature Flags (Microservices)`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two identical envs; deploy to idle;       │
│              │ instant switch; instant rollback          │
├──────────────┼───────────────────────────────────────────┤
│ KEY PROPERTY │ Deploy ≠ Release; rollback = flip switch  │
├──────────────┼───────────────────────────────────────────┤
│ K8S SWITCH   │ patch Service selector label              │
├──────────────┼───────────────────────────────────────────┤
│ DB GOTCHA    │ Both envs share same DB - backward compat │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Prepare in spare; switch in one step"    │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Blue-green deployment separates the deployment step (deploy to green) from the release step (switch traffic from blue to green). This separation is the key insight: you can deploy without releasing, test in production without serving users, and roll back without redeploying. The same separation appears in feature flags (deploy with flag off, release by enabling it) and Expand-Contract database migrations (deploy schema change separately from application change).

**Where else this pattern appears:**
- **DNS TTL switching:** Changing an A record to point to a new IP is blue-green deployment at the DNS layer - deploy new servers, switch DNS, keep old servers for the rollback period.
- **AWS Route 53 weighted routing:** Weighted records implement blue-green at the network layer - 0% to green until ready, then flip to 100%.
- **Kubernetes Service selectors:** Changing a Service's `selector` from `version: blue` to `version: green` is blue-green at the Kubernetes platform level.

---

### 💡 The Surprising Truth

Blue-green deployment has a hidden state problem teams discover in production: the two environments share stateful infrastructure (databases, caches, message queues). When traffic switches, green starts writing to the same database blue was writing to. Blue is still running as rollback. If green writes data in a format blue cannot read (new columns, changed semantics), rolling back to blue may fail because blue cannot process green's data. Teams assuming blue-green provides database state isolation discover this is false - blue-green for applications sharing stateful backends requires careful Expand-Contract database migration strategy.
---

### 🧠 Think About This Before We Continue

**Q1.** You're performing a blue-green deployment. The new version (green) adds a feature that writes a new JSON field to the `orders` table (`promotionDetails`). Blue v1 doesn't know about this field (no column; uses `SELECT *`). Describe the exact migration sequence to make this backward-compatible between blue (v1) and green (v2).

*Hint:* Think about what backward-compatible migration means for a new `promotionDetails` JSON column: (1) add the column as nullable with no default (expand); (2) green (v2) writes `promotionDetails` when available; (3) blue (v1) uses `SELECT *` which now includes `promotionDetails` - if v1's ORM has no mapping for this field it may throw an unmapped column error. The fix: use explicit column selection (not `SELECT *`) so v1 ignores new columns, OR ensure v1's ORM uses lenient deserialization that ignores unknown JSON fields. Contract phase: make `promotionDetails` required only after v1 is fully retired.

**Q2.** You have an Order Service with 100 pods (blue: live). Green is deployed (100 pods, v2). Traffic switch is performed. 30 seconds later, you notice green is returning errors on 15% of requests - but only for requests that involve a third-party payment provider. Blue is still running idle (100 pods, v1). Describe the rollback procedure, what to investigate in the 30-second post-switch window, and how to prevent this scenario in future deployments.

*Hint:* Think about what the 30-second investigation window should reveal: (1) check green access logs for which specific requests fail (which payment provider? which request path?); (2) check green application logs for the specific error (null pointer, timeout, HTTP 400 from payment provider?); (3) check if the issue is a missing environment variable in green (payment provider API key not included in green's deployment config); (4) check if it's a code bug in how green handles the payment provider's callback. Rollback: switch Kubernetes Service selector back to blue, verify blue error rate returns to baseline within 30 seconds.

**Q3 (Design Trade-off):** 10 services use blue-green deployment. A database migration is required: add a new `order_analytics` table written by the Order Service and read by the Analytics Service. The migration must be zero-downtime and support rollback. Design the complete deployment sequence.

*Hint:* Think about what zero-downtime database migration means with blue-green: (1) run migration to add `order_analytics` table to the shared database (backward compatible - adding a table doesn't affect existing services); (2) deploy green Order Service that writes to the new table; (3) deploy green Analytics Service that reads from it; (4) switch traffic to green services; (5) rollback to blue: blue Order Service simply doesn't write to `order_analytics` (the table exists but is unused, blue works normally). Explore whether the migration should run before deploying green services (so the table exists when green starts) rather than after.
