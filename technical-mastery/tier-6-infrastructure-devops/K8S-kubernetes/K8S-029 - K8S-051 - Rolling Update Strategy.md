---
version: 1
layout: default
title: "Rolling Update Strategy"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/kubernetes/rolling-update-strategy/
id: K8S-029
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Deployment", "ReplicaSet", "Pod"]
used_by: ["Pod Disruption Budget", "K8s Upgrade Strategy"]
related:
  [
    "Deployment",
    "Pod Disruption Budget",
    "Readiness vs Liveness vs Startup Probe",
    "K8s Upgrade Strategy",
  ]
tags: [kubernetes, rolling-update, deployment-strategy, zero-downtime, k8s]
---

## ⚡ TL;DR

A **Rolling Update** replaces Pods one batch at a time, ensuring some old Pods keep running until new Pods are healthy. Controlled by `maxSurge` (extra Pods during update) and `maxUnavailable` (Pods allowed to be down). Combined with readiness probes, achieves zero-downtime deployments.

---

## 🔥 Problem This Solves

Deploying a new container image needs to replace all running Pods. Doing it all at once = downtime. Doing it one at a time with health checks = zero downtime. The rolling update strategy automates this while giving you control over speed vs risk tradeoff.

---

## 📘 Textbook Definition

A Rolling Update is a Deployment strategy that incrementally replaces the current instances of an application with new ones. It uses maxSurge (number of extra Pods that can exist during the update) and maxUnavailable (Pods that can be unavailable) to control the update pace and maintain availability.

---

## ⏱️ 30 Seconds

```yaml
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1 # 1 extra pod during update (max 6 pods)
      maxUnavailable: 0 # zero pods unavailable (safest)
  minReadySeconds: 10 # wait 10s after pod ready before next batch
```

---

## 🔩 First Principles

- Deployment creates a new ReplicaSet for the new version; scales up new RS, scales down old RS
- `maxSurge`: number (or %) of Pods ABOVE desired during update (extra capacity)
- `maxUnavailable`: number (or %) of desired Pods that can be unavailable during update
- Both can be `0` simultaneously (but at least one must be non-zero)
- Update pauses if new Pods fail readiness probes (safe rollout)
- `kubectl rollout undo` reverts to previous ReplicaSet (old RS kept alive)

---

## 🧪 Thought Experiment

3 replicas, maxSurge=1, maxUnavailable=0. Update starts: new RS scales to 1 Pod (total: 4). Old RS scales down when new Pod passes readiness probe (total: 3). New RS scales to 2. Old RS scales to 1. Eventually: new RS=3, old RS=0. At every step: always 3+ healthy pods serving traffic. Zero-downtime achieved.

---

## 🧠 Mental Model / Analogy

Rolling update is like **replacing tires while driving**: change one tire at a time while the car stays moving. The other three tires (old Pods) keep the car rolling. Only after the new tire is confirmed good (readiness probe) does work begin on the next one. You're never rolling on fewer than 3 tires (maxUnavailable=0).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: New image → K8s replaces Pods one at a time → users see no downtime.

**Level 2 - Practitioner**: `maxUnavailable: 0` = safest (never fewer than desired). `maxSurge: 1` = slightly above desired during update. `minReadySeconds: 30` = wait 30s after Pod ready before proceeding.

**Level 3 - Advanced**: `maxUnavailable: 25%` with 8 replicas = 2 can be down. `maxSurge: 25%` = 2 extra. Combined: updates 2 Pods at a time, fast. `progressDeadlineSeconds: 600` = fail if not complete in 10 min. `kubectl rollout pause` / `kubectl rollout resume` for manual canary control.

**Level 4 - Expert**: Rolling update vs: Recreate (all old → down → all new, fast but downtime), Blue-Green (new stack in parallel → switch traffic), Canary (gradual % via Ingress or service mesh). Argo Rollouts: advanced rollout controller with automated canary analysis (Prometheus metrics, error rate thresholds), blue-green with traffic shifting. `kubectl rollout history` shows revision list. `--revision=3` to rollback to specific revision.

---

## ⚙️ How It Works

---

### Update Sequence (maxSurge=1, maxUnavailable=0, replicas=3)

```
Initial state:  [v1, v1, v1] = 3 pods

Step 1: Create v2 pod (surge: 4 total)
  [v1, v1, v1, v2-pending]
  Wait for v2 to pass readiness probe...
  [v1, v1, v1, v2-ready]   → 4 pods, all healthy

Step 2: Terminate 1 v1 pod
  [v1, v1, v2-ready]       → 3 pods, 1 v2

Step 3: Create another v2 pod
  [v1, v1, v2, v2-pending]
  Wait for readiness...
  [v1, v1, v2, v2-ready]   → 4 pods

Step 4: Terminate another v1
  [v1, v2, v2]             → 3 pods, 2 v2

... continues until [v2, v2, v2]
```

---

### Rollout Commands

```bash
# Trigger rolling update (update image)
kubectl set image deployment/my-app app=my-registry/my-app:v2.0

# Or update deployment.yaml and apply
kubectl apply -f deployment.yaml

# Watch rollout progress
kubectl rollout status deployment/my-app

# Pause (creates natural canary checkpoint)
kubectl rollout pause deployment/my-app

# Check behavior in production, then resume
kubectl rollout resume deployment/my-app

# Undo (rollback to previous revision)
kubectl rollout undo deployment/my-app

# Rollback to specific revision
kubectl rollout history deployment/my-app
kubectl rollout undo deployment/my-app --to-revision=3
```

---

### Deployment YAML Strategy

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2 # up to 7 pods during update
      maxUnavailable: 1 # 1 can be down (4 min available)
  minReadySeconds: 30 # extra stability window
  progressDeadlineSeconds: 600 # fail after 10 min
  revisionHistoryLimit: 5 # keep 5 old RSets for rollback
  template:
    spec:
      containers:
        - name: app
          image: my-app:v2.0
          readinessProbe: # CRITICAL for safe rolling update
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
```

---

## 🔄 E2E Flow: Rolling Update with Readiness Probe Failure

```
kubectl set image deployment/my-app app=my-app:v2.0-broken

Rolling update starts:
  → Creates new Pod with v2.0-broken image
  → New Pod starts; readiness probe hits /health/ready
  → v2.0-broken has a bug; /health/ready returns 500
  → Pod never becomes Ready

Rolling update:
  → Waits... (old Pods keep serving)
  → After progressDeadlineSeconds (10 min): marks as
    "DeadlineExceeded"
  → New Pod remains NOT READY
  → Old Pods continue running (minAvailable maintained)

Operator: kubectl rollout undo deployment/my-app
  → Scales down broken RS
  → Old RS scales back up
  → Service restored

Key insight: readiness probes prevented any traffic
  reaching broken Pod
```

---

## ⚖️ Comparison Table

| Strategy          | Downtime | Speed          | Risk   | Use Case           |
| ----------------- | -------- | -------------- | ------ | ------------------ |
| **Recreate**      | Yes      | Fast           | High   | Dev/Staging        |
| **RollingUpdate** | No       | Medium         | Low    | Default production |
| **Blue-Green**    | No       | Fast (switch)  | Medium | Fast rollback      |
| **Canary**        | No       | Slow (gradual) | Lowest | Risk-averse prod   |

---

## ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                    |
| ----------------------------------------- | -------------------------------------------------------------------------- |
| "maxUnavailable: 0 means no interruption" | Pods are replaced; existing connections may drop at SIGTERM                |
| "Rolling update checks app functionality" | Only checks readiness probe; app may have bugs not caught by probe         |
| "rollout undo is instant"                 | Triggers a new rolling update of the rollback; takes same time as original |
| "maxSurge: 0 is valid alone"              | Must have at least one of maxSurge or maxUnavailable non-zero              |

---

## 🚨 Failure Modes

| Failure                  | Symptom                                 | Fix                                               |
| ------------------------ | --------------------------------------- | ------------------------------------------------- |
| No readiness probe       | Broken pods receive traffic             | Add readiness probe that tests actual health      |
| Readiness probe too fast | Pod marked ready before app initialized | Increase `initialDelaySeconds`; use startup probe |
| maxUnavailable too high  | Too many pods down during update        | Lower maxUnavailable; increase replicas           |
| Rollout stuck            | `kubectl rollout status` hangs          | Check pod events; bad image, OOMKill, CrashLoop   |

---

## 🔗 Related Keywords

- [Deployment](/kubernetes/deployment/) - resource that manages rolling updates
- [Pod Disruption Budget](/kubernetes/pod-disruption-budget/) - protects against maintenance disruptions
- [Readiness vs Liveness vs Startup Probe](/kubernetes/readiness-vs-liveness-vs-startup-probe/) - gates rolling update progress
- [K8s Upgrade Strategy](/kubernetes/k8s-upgrade-strategy/) - node-level rolling upgrades

---

## 📌 Quick Reference Card

```bash
# Watch rolling update live
watch kubectl get pods -l app=my-app

# Check rollout status
kubectl rollout status deployment/my-app --timeout=5m

# View rollout history
kubectl rollout history deployment/my-app

# Rollback
kubectl rollout undo deployment/my-app

# Check Deployment strategy
kubectl get deployment my-app -o jsonpath=\
  '{.spec.strategy.rollingUpdate}'

# Annotate for change tracking
kubectl annotate deployment/my-app \
  kubernetes.io/change-cause="v2.0: add payment feature"
```

---

## 🧠 Think About This

The combination of `maxUnavailable: 0`, `maxSurge: 1`, `minReadySeconds: 30`, and a robust readiness probe is the gold standard for zero-downtime deployments. But there's a hidden risk: if your readiness probe only checks "is the app responding?" and not "is this specific instance healthy?", a broken app that returns 200 for the health endpoint will pass through. The best readiness probes check actual dependencies: can the app connect to the database? Is the cache warm? Is the background worker pool running? This is the difference between "the container started" and "the container is serving production traffic safely."
