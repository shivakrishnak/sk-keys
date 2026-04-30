---
layout: default
title: "Rolling Update"
parent: "DevOps & SDLC"
nav_order: 453
permalink: /devops-sdlc/rolling-update/
number: "453"
category: DevOps & SDLC
difficulty: ★☆☆
depends_on: CI/CD Pipeline, Kubernetes
used_by: CI/CD Pipeline, Kubernetes Deployments
tags: #devops #sdlc #foundational #reliability
---

# 453 — Rolling Update

`#devops` `#sdlc` `#foundational` `#reliability`

⚡ TL;DR — Replace instances of the old version one-by-one (or in small batches) with the new version, keeping the service available throughout.

| #453 | Category: DevOps & SDLC | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Kubernetes | |
| **Used by:** | CI/CD Pipeline, Kubernetes Deployments | |

---

## 📘 Textbook Definition

A Rolling Update is a deployment strategy where instances of the running version are incrementally replaced with instances of the new version, one at a time or in configurable batches. At no point is the full application taken offline — a mix of old and new versions serves traffic during the transition window.

---

## 🟢 Simple Definition (Easy)

Rolling update means **swapping pods one by one** — the old version goes down, the new one comes up, repeat until all pods are updated. The service stays up the whole time.

---

## 🔵 Simple Definition (Elaborated)

Rolling updates are the default deployment strategy in Kubernetes. They balance simplicity (no separate environment needed) with availability (never takes all instances offline). The cost is that old and new versions run side-by-side briefly — APIs must be backward-compatible during this window. If the new version fails, Kubernetes stops the rollout and can automatically roll back.

---

## 🔩 First Principles Explanation

**The core problem:**
Taking all servers offline to deploy a new version causes downtime. Deploying to all servers simultaneously with a bad version crashes everything at once.

**The insight:**
> "Replace one instance at a time. If it fails, stop immediately — most instances are still running the old version."

```
Before:  [v1] [v1] [v1] [v1]  <- 4 pods, all v1

Step 1:  [v2] [v1] [v1] [v1]  <- 1 replaced
Step 2:  [v2] [v2] [v1] [v1]  <- 2 replaced
Step 3:  [v2] [v2] [v2] [v1]  <- 3 replaced
After:   [v2] [v2] [v2] [v2]  <- complete

If v2 fails at step 2: stop. Still 2 healthy v1 pods serve traffic.
```

---

## ❓ Why Does This Exist (Why Before What)

Without rolling updates, you either take downtime (replace all-at-once) or run separate environments (blue-green, which costs more). Rolling updates are the practical middle ground: zero downtime with minimal infrastructure overhead.

---

## 🧠 Mental Model / Analogy

> Think of replacing floor tiles in a busy restaurant. You don't close the restaurant — you replace one tile at a time while people walk around the area being worked on. The restaurant stays open throughout. If a new tile is defective, you stop and only one tile is bad.

---

## ⚙️ How It Works (Mechanism)

```
Kubernetes Rolling Update parameters:

  maxUnavailable: 1   -- at most 1 pod offline at any time
  maxSurge: 1         -- at most 1 extra pod (above desired count) at any time

Example with 4 replicas, maxUnavailable=1, maxSurge=1:

  Phase 1: Scale up 1 v2 pod   → 4 v1 + 1 v2 = 5 pods
  Phase 2: Terminate 1 v1 pod  → 3 v1 + 1 v2 = 4 pods (desired)
  Phase 3: Scale up 1 v2 pod   → 3 v1 + 2 v2 = 5 pods
  Phase 4: Terminate 1 v1 pod  → 2 v1 + 2 v2 = 4 pods
  ... continue until 0 v1, 4 v2
```

---

## 🔄 How It Connects (Mini-Map)

```
[CI/CD Pipeline]
       ↓
[kubectl apply / helm upgrade]
       ↓
[Kubernetes Rolling Update]
  [v1→v2] [v1→v2] [v1→v2] ...
       ↓
[Readiness Probe passes] --> proceed
[Readiness Probe fails]  --> pause + alert
       ↓
[kubectl rollout undo] --> revert to v1
```

---

## 💻 Code Example

```yaml
# Kubernetes Deployment with rolling update strategy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # never take more than 1 pod offline
      maxSurge: 1         # never run more than 5 pods total
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0
        readinessProbe:           # CRITICAL: controls rollout pace
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3
```

```bash
# Trigger rolling update by updating the image
kubectl set image deployment/myapp myapp=myapp:v2.0.0

# Watch the rollout progress
kubectl rollout status deployment/myapp

# Rollback to previous version
kubectl rollout undo deployment/myapp

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=2

# Check rollout history
kubectl rollout history deployment/myapp
```

---

## 🔁 Flow / Lifecycle

```
1. New image tag available in registry
        ↓
2. kubectl apply / CD pipeline updates deployment spec
        ↓
3. Kubernetes creates new pod (v2)
        ↓
4. Readiness probe passes → pod added to service endpoints
        ↓
5. Old pod (v1) removed from service endpoints, then terminated
        ↓
6. Repeat steps 3-5 until all pods are v2
        ↓
7. If any new pod fails readiness → rollout paused
        ↓
8. Manual investigation OR auto-rollback via kubectl rollout undo
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Rolling update = zero risk | Old and new versions co-exist; APIs must be backward-compatible |
| Rollback is instant | Rollback is another rolling update (takes time proportional to replica count) |
| It's the same as blue-green | Blue-green has instant switch; rolling update is gradual and in-place |
| maxUnavailable=0 means fully safe | maxUnavailable=0 + maxSurge=1 means slower but keeps full capacity |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Missing Readiness Probes**
Without a readiness probe, Kubernetes sends traffic to pods that aren't ready yet.
Fix: always define a readiness probe; never deploy without one in production.

**Pitfall 2: Breaking API Changes During Rollout**
v2 sends a response that v1 cannot parse, or vice versa, during the overlap window.
Fix: always maintain API backward compatibility for at least one deploy cycle.

**Pitfall 3: Too Aggressive maxUnavailable**
Setting maxUnavailable=50% means half your capacity is offline during rollout.
Fix: use maxUnavailable=1 or 25% for production; save aggressive settings for dev.

---

## 🔗 Related Keywords

- **Blue-Green Deployment** — instant full switch; no version overlap
- **Canary Deployment** — gradual % shift with monitoring gates
- **Readiness Probe** — the Kubernetes mechanism that controls rollout pacing
- **CI/CD Pipeline** — triggers rolling updates automatically after build
- **kubectl rollout undo** — the rollback command

---

## 📌 Quick Reference Card

| #453 | Category: DevOps & SDLC | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Kubernetes | |
| **Used by:** | CI/CD Pipeline, Kubernetes Deployments | |

---

## 🧠 Think About This Before We Continue

**Q1.** Why is a readiness probe critical for rolling updates, and what happens without one?  
**Q2.** How does `maxUnavailable=0, maxSurge=1` differ from `maxUnavailable=1, maxSurge=0` in practice?  
**Q3.** What API compatibility constraint must be satisfied when using rolling updates with multiple replicas?

