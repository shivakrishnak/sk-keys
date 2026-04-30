---
layout: default
title: "Blue-Green Deployment"
parent: "DevOps & SDLC"
nav_order: 451
permalink: /devops-sdlc/blue-green-deployment/
number: "451"
category: DevOps & SDLC
difficulty: ★★☆
depends_on: CI/CD Pipeline, Load Balancer
used_by: CI/CD Pipeline, Zero-Downtime Deployment
tags: #devops #sdlc #intermediate #reliability
---

# 451 — Blue-Green Deployment

`#devops` `#sdlc` `#intermediate` `#reliability`

⚡ TL;DR — Run two identical production environments (blue and green); switch traffic instantly to the new version, with instant rollback by switching back.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #451         │ Category: DevOps & SDLC              │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ CI/CD Pipeline, Load Balancer                                     │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ CI/CD Pipeline, Zero-Downtime Deployment                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

Blue-Green Deployment is a release strategy that maintains two identical production environments — "blue" (current live version) and "green" (new version). After deploying and validating the new version in the green environment, traffic is switched from blue to green via a load balancer or DNS change. Rollback is instant: switch traffic back to blue.

---

## 🟢 Simple Definition (Easy)

Blue-Green means you have **two identical environments**. One is live (blue), one has the new version (green). When green is ready, you flip the switch. If something breaks, you flip back immediately — zero downtime.

---

## 🔵 Simple Definition (Elaborated)

The key insight is that deployment and release are separated. You can deploy the new version to the green environment at any time while blue continues serving all production traffic. Only after green is fully validated does the load balancer switch traffic. Rollback is always available and takes seconds — just point traffic back to blue.

---

## 🔩 First Principles Explanation

**The core problem:**
Traditional "in-place" deployment takes the running version down, deploys the new version, and brings it back up. If the new version is broken, you're stuck halfway and need to redeploy the old version under pressure.

**The insight:**
> "Never deploy over the running production system. Keep the old one alive until you're sure the new one works."

```
Blue (v1) <-- all traffic     Green (v2 deploying)
     ↓
Validate green
     ↓
Switch router: Blue (v1) idle    Green (v2) <-- all traffic
     ↓
Rollback if needed: Blue (v1) <-- all traffic  (instant)
```

---

## ❓ Why Does This Exist (Why Before What)

Without blue-green, a bad deployment means downtime while you scramble to revert. With blue-green, rollback is frictionless — flip the switch and the old version is live again in seconds, buying time to diagnose the issue.

---

## 🧠 Mental Model / Analogy

> Think of a runway at an airport. While planes land on runway A (blue), workers prepare runway B (green) for new conditions. When B is ready and inspected, air traffic control switches all landings to B. If B has a problem, they switch back to A immediately — no planes were disrupted.

---

## ⚙️ How It Works (Mechanism)

```
Load Balancer / Router
         |
   ------+------
   |             |
[Blue]         [Green]
(v1 - live)    (v2 - staging)

Steps:
1. Deploy new version to green (blue still serving all traffic)
2. Run smoke tests and validation against green
3. Route 100% of traffic to green (blue goes idle)
4. Monitor green for defined period (e.g., 15 minutes)
5. If healthy: decommission blue OR keep it for next cycle
6. If unhealthy: route traffic back to blue (seconds)
```

---

## 🔄 How It Connects (Mini-Map)

```
[CI/CD Pipeline]
       ↓
[Deploy to Green]
       ↓
[Validate]  --> FAIL --> keep blue live, debug green
       ↓ PASS
[Switch Router] --> Green is now Blue for next cycle
       ↓
[Monitor] --> auto-rollback if SLO breached
```

---

## 💻 Code Example

```yaml
# Kubernetes blue-green with service selector swap

# Blue deployment (currently live)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0

---
# Green deployment (new version, deployed in parallel)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0

---
# Service — switch traffic by changing selector
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue   # <-- change to 'green' to switch; change back to rollback
  ports:
  - port: 80
    targetPort: 8080
```

```bash
# Switch to green (instant traffic switch)
kubectl patch service myapp -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback to blue (instant)
kubectl patch service myapp -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## 🔁 Flow / Lifecycle

```
1. New version built and pushed to registry
        ↓
2. Deploy new version to green environment
        ↓
3. Run automated smoke tests against green
        ↓
4. Switch load balancer / service selector to green
        ↓
5. Monitor for 15-30 minutes
        ↓
6a. Healthy: keep green live, reset blue for next deployment
6b. Incident: switch back to blue in seconds
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Blue-green requires double the infra cost | Modern cloud: spin up green on-demand, tear down after cutover |
| It handles database migrations automatically | Schema migrations must be backward-compatible (this is the hard part) |
| Canary is the same as blue-green | Canary gradually shifts traffic; blue-green is all-or-nothing switch |
| It eliminates all deployment risk | It eliminates rollback complexity; bugs can still reach users briefly |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Database Schema Migrations**
If green requires a new DB schema that blue is incompatible with, you cannot roll back.
Fix: use expand-contract pattern — add columns in one deploy (backward-compatible), migrate data in next, remove old columns in third.

**Pitfall 2: Session State**
Users connected to blue lose sessions when switched to green (if sessions are in-memory).
Fix: externalize session state to Redis/DB before adopting blue-green.

**Pitfall 3: Forgetting to Tear Down Blue**
Blue stays running indefinitely, consuming resources and accruing cost.
Fix: automate blue teardown after green is validated stable (e.g., 1 hour after cutover).

---

## 🔗 Related Keywords

- **Canary Deployment** — gradual shift vs blue-green's instant switch
- **Rolling Update** — in-place gradual replacement, no parallel environment needed
- **CI/CD Pipeline** — the automation that deploys to green automatically
- **Load Balancer** — the control point for traffic switching
- **Feature Flags** — complement blue-green for fine-grained feature control

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Two identical envs; switch traffic instantly;  │
│              │ rollback in seconds                           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Zero-downtime releases; high-risk deployments  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ State/DB migration incompatibilities not       │
│              │ resolved with expand-contract pattern          │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Deploy first, release second — keep the       │
│              │  old version warm for instant rollback"        │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary --> Rolling Update --> Feature Flags    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** How does the expand-contract database migration pattern enable safe blue-green deployments?  
**Q2.** What is the difference between blue-green deployment and a canary release?  
**Q3.** How would you handle user sessions during a blue-green traffic switch?

