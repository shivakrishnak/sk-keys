---
version: 1
layout: default
title: "Deployment"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /kubernetes/deployment/
id: K8S-012
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "ReplicaSet"]
used_by: ["Rolling Update Strategy", "HPA (Horizontal Pod Autoscaler)"]
related:
  [
    "ReplicaSet",
    "StatefulSet",
    "DaemonSet",
    "Rolling Update Strategy",
    "HPA (Horizontal Pod Autoscaler)",
  ]
tags: [kubernetes, deployment, rolling-update, replica, k8s]
---

# Deployment

## ⚡ TL;DR

A Deployment manages **ReplicaSets** to maintain a desired number of Pod replicas. It provides declarative updates (rolling updates, rollbacks), self-healing, and scaling. Most stateless apps run as Deployments.

---

## 🔥 Problem This Solves

You need to run multiple replicas of an app, update it without downtime, roll back on failure, and scale it up/down. A Deployment automates all of this declaratively.

---

## 📘 Textbook Definition

A Deployment provides declarative updates for Pods and ReplicaSets. You describe the desired state, and the Deployment Controller changes the actual state to match. It manages rolling updates and rollbacks.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1 # extra pods during update
      maxUnavailable: 0 # no downtime
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: my-app:1.1
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
```

---

## 🔩 First Principles

- A Deployment owns one or more **ReplicaSets** (old + new during updates)
- ReplicaSets ensure the desired number of Pods are running
- Rolling updates create a new ReplicaSet and gradually shift traffic
- **Rollback** = scale back up the old ReplicaSet

---

## 🧪 Thought Experiment

You deploy v1.0 (3 replicas). You push v1.1. The Deployment creates a new ReplicaSet for v1.1 and incrementally replaces v1.0 Pods. If v1.1 Pods fail readiness probes, the rollout pauses - preventing the broken version from reaching full deployment. You can run `kubectl rollout undo` to instantly restore v1.0.

---

## 🧠 Mental Model / Analogy

A Deployment is like a **HR manager**: it ensures the team (ReplicaSet) always has the right number of workers (Pods). When promoting to a new job level (new version), it gradually transitions workers while making sure the team never drops below minimum headcount.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: A Deployment keeps N copies of your app running and handles updates safely.

**Level 2 - Practitioner**: `rollingUpdate` strategy controls pace. `maxSurge`: extra Pods allowed. `maxUnavailable`: how many can be down. Rollback with `kubectl rollout undo`.

**Level 3 - Advanced**: Deployment revision history stored in old ReplicaSets (default: 10). `--revision-history-limit` controls this. Pausing a rollout: `kubectl rollout pause`. `minReadySeconds` ensures Pods are stable before proceeding.

**Level 4 - Expert**: Deployment controller reconciles via `apps/v1` controller loop. Scale-down order: newest Pods removed first. Blue-green deployments implemented via switching Service selector between two Deployments. Canary: run two Deployments with different replica ratios.

---

## ⚙️ How It Works

### Update Flow (Rolling Update)

```
Deployment spec updated (new image)
  → New ReplicaSet created (v2)
  → Scale up v2 by maxSurge
  → Wait for v2 Pods to pass readinessProbe
  → Scale down v1 by (maxSurge + maxUnavailable)
  → Repeat until all Pods are v2
  → Old ReplicaSet scaled to 0 (kept for rollback)
```

### Rollback

```bash
kubectl rollout undo deployment/my-app
# or to specific revision:
kubectl rollout undo deployment/my-app --to-revision=2
```

### Status

```bash
kubectl rollout status deployment/my-app
# Waiting for rollout to finish: 2 of 3 updated replicas are available...
# deployment "my-app" successfully rolled out
```

---

## 🔄 E2E Flow: Zero-Downtime Deploy

```
CI pushes new image → kubectl set image deployment/my-app app=my-app:1.1
  → Deployment creates ReplicaSet rs-v2
  → rs-v2 starts 1 new Pod (maxSurge=1)
  → New Pod passes readinessProbe
  → rs-v1 terminates 1 old Pod (maxUnavailable=0: only after new is ready)
  → Repeat for remaining 2 Pods
  → All traffic now on v1.1
  → rs-v1 scaled to 0, kept in history
```

---

## ⚖️ Comparison Table

|                  | Deployment     | StatefulSet           | DaemonSet              |
| ---------------- | -------------- | --------------------- | ---------------------- |
| **Pod identity** | Random names   | Stable (pod-0, pod-1) | One per node           |
| **Use case**     | Stateless apps | Databases, queues     | Log agents, monitoring |
| **Storage**      | Ephemeral      | Stable PVCs           | Usually node-local     |
| **Update order** | Any order      | Ordered (N-1 first)   | Rolling per node       |

---

## ⚠️ Common Misconceptions

| Misconception                      | Reality                                                            |
| ---------------------------------- | ------------------------------------------------------------------ |
| "Deployment manages Pods directly" | Deployment manages ReplicaSets which manage Pods                   |
| "`kubectl apply` = instant update" | Update is gradual (rolling) unless `Recreate` strategy             |
| "Old ReplicaSets waste resources"  | Old RS are scaled to 0 (no Pods), kept for rollback history        |
| "Deployments are for all apps"     | Stateful apps need StatefulSet; singletons per node need DaemonSet |

---

## 🚨 Failure Modes

| Failure                | Symptom                                 | Fix                                               |
| ---------------------- | --------------------------------------- | ------------------------------------------------- |
| Rollout stuck          | `Waiting for rollout to finish` forever | Check new Pod logs/events; `kubectl rollout undo` |
| `Recreate` downtime    | All Pods die before new ones start      | Use `RollingUpdate` strategy                      |
| Image pull failure     | New Pods `ImagePullBackOff`             | Fix image tag/registry; rollout auto-pauses       |
| Readiness never passes | Rollout stalls at `maxUnavailable`      | Check readiness probe path and app startup        |

---

## 🔗 Related Keywords

- [ReplicaSet](/kubernetes/replicaset/) - managed by Deployment
- [Rolling Update Strategy](/kubernetes/rolling-update-strategy/) - zero-downtime updates
- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - auto-scaling
- [StatefulSet](/kubernetes/statefulset/) - for stateful workloads
- [Readiness vs Liveness vs Startup Probe](/kubernetes/readiness-vs-liveness-vs-startup-probe/)

---

## 📌 Quick Reference Card

```bash
# Create deployment
kubectl create deployment my-app --image=my-app:1.0 --replicas=3

# Update image
kubectl set image deployment/my-app app=my-app:1.1

# Check rollout
kubectl rollout status deployment/my-app
kubectl rollout history deployment/my-app

# Rollback
kubectl rollout undo deployment/my-app

# Scale
kubectl scale deployment/my-app --replicas=5

# Pause/resume rollout
kubectl rollout pause deployment/my-app
kubectl rollout resume deployment/my-app
```

---

## 🧠 Think About This

`maxSurge=1, maxUnavailable=0` = zero-downtime but slightly over capacity. `maxSurge=0, maxUnavailable=1` = never over capacity but brief under-capacity. For microservices, zero-downtime matters more. For resource-constrained environments, no extra capacity matters. Choose based on your SLA and cluster resource headroom.
