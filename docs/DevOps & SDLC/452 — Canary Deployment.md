---
layout: default
title: "Canary Deployment"
parent: "DevOps & SDLC"
nav_order: 452
permalink: /devops-sdlc/canary-deployment/
number: "452"
category: DevOps & SDLC
difficulty: ★★☆
depends_on: CI/CD Pipeline, Load Balancer, Monitoring
used_by: CI/CD Pipeline, Risk Reduction, Feature Validation
tags: #devops #sdlc #intermediate #reliability
---

# 452 — Canary Deployment

`#devops` `#sdlc` `#intermediate` `#reliability`

⚡ TL;DR — Gradually shift traffic from the old version to the new version, monitoring at each step, and rolling back immediately if metrics degrade.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #452         │ Category: DevOps & SDLC              │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ CI/CD Pipeline, Load Balancer, Monitoring                         │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ CI/CD Pipeline, Risk Reduction, Feature Validation                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

Canary Deployment is a release strategy where the new version is deployed to a small subset of production infrastructure and receives a fraction of live traffic first. If metrics remain healthy, traffic is progressively shifted to the new version. At any point, traffic can be routed back to the stable version if issues emerge.

---

## 🟢 Simple Definition (Easy)

Canary means **releasing to 1% of users first, watching, then slowly rolling out to everyone**. If those 1% hit errors, you stop and roll back — before 99% of users are affected.

---

## 🔵 Simple Definition (Elaborated)

The name comes from the "canary in a coal mine" — an early warning system. A small slice of real production traffic tests the new version before it reaches all users. Unlike blue-green (full switch), canary gives you real production signal with limited blast radius. Automated monitoring controls the progression; if error rates or latency breach thresholds, the canary is automatically rolled back.

---

## 🔩 First Principles Explanation

**The core problem:**
Even after extensive testing, some bugs only appear under real production load, data, or user behavior. Blue-green exposes 100% of users to the new version immediately — if it's broken, everyone is affected.

**The insight:**
> "Test in production with a small percentage of real users. Let real traffic validate the new version before committing to full rollout."

```
v1: 100% traffic
      ↓ deploy canary (v2 = 5% of pods)
v1: 95%, v2: 5%   <-- monitor
      ↓ healthy
v1: 80%, v2: 20%  <-- monitor
      ↓ healthy
v1: 0%,  v2: 100% <-- full rollout complete
      ↓ (or)
v1: 95%, v2: 5%   <-- anomaly detected → rollback to v1: 100%
```

---

## ❓ Why Does This Exist (Why Before What)

Without canary, every deployment is a binary risk: all users get the new version immediately. Canary converts a binary risk into a graduated exposure, limiting the blast radius of failures and providing real production signal before full commitment.

---

## 🧠 Mental Model / Analogy

> Historically, miners brought canary birds into coal mines. If the canary showed signs of distress from toxic gas, miners evacuated before breathing the gas themselves. In software, the "canary" users (small %) hit the new version first — if they experience issues, the rollout is stopped before all users are affected.

---

## ⚙️ How It Works (Mechanism)

```
Traffic splitting at load balancer / service mesh:

  [Load Balancer / Istio VirtualService]
         ↓
  5% --> [v2 pods]   <-- canary (new version)
  95% --> [v1 pods]  <-- stable (current version)

Automated progression controlled by:
  - Error rate threshold (e.g., < 0.1%)
  - P99 latency threshold (e.g., < 200ms)
  - Success rate (e.g., > 99.9%)
  - Business metric (e.g., checkout completion rate)

Auto-rollback:
  If any threshold breached → shift 100% back to v1
```

---

## 🔄 How It Connects (Mini-Map)

```
[CI/CD Pipeline]
       ↓
[Deploy v2 as Canary (5%)]
       ↓
[Monitor: error rate, latency, business metrics]
       ↓ HEALTHY         ↓ DEGRADED
[Increase % (20%)]    [Rollback to 100% v1]
       ↓
[100% v2 = full rollout]
```

---

## 💻 Code Example

```yaml
# Istio VirtualService — canary traffic splitting
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - route:
    - destination:
        host: myapp
        subset: v1     # stable
      weight: 95
    - destination:
        host: myapp
        subset: v2     # canary
      weight: 5

---
# Kubernetes Argo Rollouts — automated canary with analysis
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  strategy:
    canary:
      steps:
      - setWeight: 5          # 5% to canary
      - pause: {duration: 10m}  # observe for 10 minutes
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100        # full rollout
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 1
        args:
        - name: service-name
          value: myapp-canary
```

---

## 🔁 Flow / Lifecycle

```
1. Build and push new version (v2)
        ↓
2. Deploy v2 alongside v1 (both running)
        ↓
3. Route 5% of traffic to v2
        ↓
4. Automated analysis: error rate, latency, business KPIs
        ↓ All healthy for 10 min
5. Increase weight: 20% → 50% → 100%
        ↓
6a. 100%: complete rollout, decommission v1
6b. Any step fails: route 100% back to v1 (rollback)
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Canary = blue-green | Canary is gradual %; blue-green is instant binary switch |
| 5% canary means 5% risk | 5% canary means full production load and data — high signal value |
| Canary is only for traffic | Canary also applies to infra, config, and database changes |
| You need a service mesh for canary | Header-based routing, weighted DNS, or sticky sessions also work |

---

## 🔥 Pitfalls in Production

**Pitfall 1: No Automated Analysis**
Manual monitoring of canary — engineers forget or don't watch closely enough.
Fix: define automated metrics thresholds; use Argo Rollouts or Spinnaker for automatic progression and rollback.

**Pitfall 2: Wrong Canary Metrics**
Monitoring infrastructure metrics (CPU, memory) but not business metrics (conversion rate, order success).
Fix: instrument business KPIs in the analysis; a canary can look healthy technically while breaking revenue.

**Pitfall 3: Sticky Sessions Distort Canary**
If user sessions are sticky, the same users always hit v2 — it's a biased sample.
Fix: use header-based routing or ensure stateless sessions for accurate canary signal.

---

## 🔗 Related Keywords

- **Blue-Green Deployment** — instant full switch vs gradual canary shift
- **Rolling Update** — in-place gradual replacement of pods (simpler but less control)
- **CI/CD Pipeline** — automates the canary deployment stages
- **Feature Flags** — code-level canary; canary deployment is infra-level
- **SLO / Error Budget** — the thresholds that trigger canary rollback

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Expose a small % of real production traffic   │
│              │ to new version; roll back fast if it breaks   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ High-risk changes; validating with real       │
│              │ production traffic before full rollout        │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Changes that cannot be partially live         │
│              │ (e.g., breaking DB migration)                 │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Let 5% of users test it; protect the 95%    │
│              │  until you're confident"                      │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Blue-Green --> Rolling Update --> Argo Rollouts│
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** What is the key difference between a canary deployment and a blue-green deployment in terms of risk profile?  
**Q2.** Why is monitoring business metrics (not just technical metrics) critical for automated canary analysis?  
**Q3.** How do sticky sessions interfere with canary deployments and how do you mitigate this?

