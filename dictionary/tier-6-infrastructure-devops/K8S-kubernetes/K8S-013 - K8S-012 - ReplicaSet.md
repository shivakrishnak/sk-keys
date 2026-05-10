---
version: 1
layout: default
title: "ReplicaSet"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /kubernetes/replicaset/
id: K8S-013
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Deployment"]
used_by: ["Deployment", "HPA (Horizontal Pod Autoscaler)"]
related:
  [
    "Deployment",
    "Pod",
    "HPA (Horizontal Pod Autoscaler)",
    "Kubernetes Architecture",
  ]
tags: [kubernetes, replicaset, replicas, pod-management, k8s]
---

# ReplicaSet

## ⚡ TL;DR

A ReplicaSet ensures a **specified number of Pod replicas** are running at any time. In practice, you rarely create ReplicaSets directly - Deployments manage them for you, providing rolling updates and rollbacks.

---

## 🔥 Problem This Solves

If a Pod crashes, it doesn't restart itself. Something must watch and recreate it. A ReplicaSet watches Pods matching a label selector and ensures the count stays at `replicas`.

---

## 📘 Textbook Definition

A ReplicaSet's purpose is to maintain a stable set of replica Pods running at any given time. It is defined by a `selector`, `replicas` count, and a Pod `template`. The ReplicaSet controller reconciles actual vs desired replica count.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: my-app-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: "1.0"
  template:
    metadata:
      labels:
        app: my-app
        version: "1.0"
    spec:
      containers:
        - name: app
          image: my-app:1.0
```

---

## 🔩 First Principles

- ReplicaSet controller watches Pods matching its `selector`
- Actual < desired → creates new Pods from template
- Actual > desired → deletes excess Pods (newest first)
- Pods are **adopted** if they match the selector but weren't created by the RS
- ReplicaSet does NOT provide rolling updates - that's Deployment's job

---

## 🧪 Thought Experiment

What if you manually create a Pod with the same labels as a ReplicaSet's selector? The ReplicaSet "adopts" it (counts it toward replicas) and may delete one of its own Pods to maintain exactly `replicas` count. Labels drive ownership - be careful with label selection.

---

## 🧠 Mental Model / Analogy

A ReplicaSet is like a **headcount manager**: "I need exactly 3 developers on this project." If someone leaves, it hires a replacement. If too many show up, it sends one home. It doesn't care about career progression (updates) - that's the Deployment's concern.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: A ReplicaSet keeps N copies of your Pod running. If one dies, it creates a new one.

**Level 2 - Practitioner**: You rarely create ReplicaSets directly. Deployments manage ReplicaSets. When you update a Deployment, it creates a new ReplicaSet and scales down the old one.

**Level 3 - Advanced**: `ownerReferences` field in Pod metadata points to its ReplicaSet. Deployment's ReplicaSets are identified by pod-template-hash label. HPA scales the ReplicaSet replica count via the Deployment's scale subresource.

**Level 4 - Expert**: Reconciliation: RS controller compares `len(matchingPods)` to `spec.replicas`. Bulk creation with batch (creates Pods in groups to reduce API Server load). Orphaned Pods (RS deleted with `--cascade=orphan`) keep running until manually deleted.

---

## ⚙️ How It Works

### Reconcile Loop

```
Watch pods matching selector
  IF len(pods) < spec.replicas:
    Create (spec.replicas - len(pods)) new Pods from template
  IF len(pods) > spec.replicas:
    Delete (len(pods) - spec.replicas) Pods
    (deletes newest Pods first)
  IF len(pods) == spec.replicas:
    No action
```

### Pod Ownership

```yaml
# Pod metadata (auto-added by RS controller)
metadata:
  ownerReferences:
    - apiVersion: apps/v1
      kind: ReplicaSet
      name: my-app-rs-7d9b8c
      uid: abc123
      controller: true
      blockOwnerDeletion: true
```

---

## 🔄 E2E Flow: Pod Failure Recovery

```
ReplicaSet: replicas=3, 3 Pods running

Pod "my-app-rs-abc" crashes (OOMKill)
  → RS controller: len(pods) = 2, desired = 3
  → Creates new Pod "my-app-rs-xyz" from template
  → New Pod: Pending → Running
  → ReplicaSet: 3 Pods running ✅
```

---

## ⚖️ Comparison Table

|              | ReplicaSet                         | ReplicationController (deprecated) |
| ------------ | ---------------------------------- | ---------------------------------- |
| **Selector** | `matchLabels` + `matchExpressions` | Equality only                      |
| **Status**   | Current standard                   | Deprecated; use RS                 |
| **Usage**    | Via Deployment                     | Direct (legacy)                    |

---

## ⚠️ Common Misconceptions

| Misconception                          | Reality                                               |
| -------------------------------------- | ----------------------------------------------------- |
| "I should create ReplicaSets directly" | Create Deployments; they manage ReplicaSets           |
| "ReplicaSet handles updates"           | RS only maintains count; Deployment handles updates   |
| "Deleting RS deletes Pods"             | By default yes; `--cascade=orphan` keeps Pods running |
| "RS ensures Pod spread across nodes"   | Not by default; use Pod Anti-Affinity for spread      |

---

## 🚨 Failure Modes

| Failure                   | Symptom                            | Fix                                       |
| ------------------------- | ---------------------------------- | ----------------------------------------- |
| Label selector too broad  | RS adopts unrelated Pods           | Use unique, specific labels               |
| Template misconfiguration | RS creates crashing Pods endlessly | Fix Pod template; RS won't give up        |
| Stuck at 0 when node full | Pods `Pending` forever             | Scale cluster or reduce resource requests |

---

## 🔗 Related Keywords

- [Deployment](/kubernetes/deployment/) - manages RS lifecycle
- [Pod](/kubernetes/pod/) - unit created by ReplicaSet
- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - scales RS replicas
- [Node Affinity / Anti-Affinity](/kubernetes/node-affinity-anti-affinity/) - spread Pods across nodes

---

## 📌 Quick Reference Card

```bash
# Get ReplicaSets
kubectl get rs
kubectl describe rs my-app-rs

# Scale directly (usually via Deployment)
kubectl scale rs my-app-rs --replicas=5

# See Pods owned by RS
kubectl get pods --selector=app=my-app

# Delete RS but keep Pods running
kubectl delete rs my-app-rs --cascade=orphan
```

---

## 🧠 Think About This

Old ReplicaSets from previous Deployment revisions are kept (scaled to 0) to enable rollback. Each rollback just re-scales an old RS back up and the new RS down. This is why `kubectl rollout undo` is so fast - no new Pods are created, existing stopped Pods are just re-started from the old RS's template. The default history limit is 10 revisions.
