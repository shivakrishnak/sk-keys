---
layout: default
title: "Pod Disruption Budget"
parent: "Kubernetes"
nav_order: 50
permalink: /kubernetes/pod-disruption-budget/
id: K8S-050
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Deployment", "Pod", "Node Affinity / Anti-Affinity"]
used_by:
  [
    "K8s Upgrade Strategy",
    "VPA (Vertical Pod Autoscaler)",
    "Cluster Autoscaler",
  ]
related:
  [
    "Rolling Update Strategy",
    "K8s Upgrade Strategy",
    "Cluster Autoscaler",
    "VPA (Vertical Pod Autoscaler)",
  ]
tags: [kubernetes, pdb, pod-disruption-budget, availability, maintenance, k8s]
---

# Pod Disruption Budget

## ⚡ TL;DR

A **PodDisruptionBudget (PDB)** limits how many Pods of a Deployment/StatefulSet can be simultaneously disrupted during voluntary disruptions (node drain, cluster upgrade). It guarantees minimum availability: "always keep at least N replicas running" or "allow at most N replicas to be unavailable."

---

## 🔥 Problem This Solves

During a rolling upgrade or node drain, Kubernetes may evict multiple Pods of the same service at once, causing an outage. PDB tells Kubernetes: "don't evict more than 1 Pod of this service at a time." This ensures the cluster can be maintained safely without downtime.

---

## 📘 Textbook Definition

A PodDisruptionBudget is a Kubernetes resource that limits the number of pods of a replicated application that are down simultaneously during voluntary disruptions. It provides a way to ensure high availability of applications during maintenance operations.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: my-app
spec:
  minAvailable: 2 # or use maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

```
# Result: during drain, cluster will not evict pods if it would bring
# available my-app pods below 2
```

---

## 🔩 First Principles

- PDB applies only to **voluntary disruptions** (drain, cluster upgrade, Cluster Autoscaler scale-down)
- NOT applied for **involuntary disruptions** (node crash, OOMKill, hardware failure)
- `minAvailable`: absolute number or percentage (e.g., `"50%"`) of pods that must remain available
- `maxUnavailable`: max pods that can be unavailable simultaneously
- PDB blocks `kubectl drain` until conditions are met (or `--disable-eviction` flag overrides)
- PDB selector must match the pods you want to protect

---

## 🧪 Thought Experiment

You have 3 replicas across 3 nodes. PDB says `minAvailable: 2`. Node drain starts:

- Node 1 drained → Pod 1 evicted → 2 running (at minimum) → Node 1 fully drained ✅
- Node 2 drain attempt → would evict Pod 2 → only 1 running (below minAvailable: 2) → BLOCKED
- Drain waits until new Pod scheduled on another node → 3 running → drain proceeds ✅
  PDB acted as a safety valve: drains succeed but never below 2 running pods.

---

## 🧠 Mental Model / Analogy

PDB is like **bridge single-lane traffic control**: work crew can close one lane, but a spotter ensures at least one lane is always open. If the crew wants to close a second lane temporarily, they must wait until the first lane is reopened. Cars (traffic) keep flowing (service stays up) throughout the construction.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: PDB ensures some Pods are always running during maintenance. Create a PDB for every important service.

**Level 2 — Practitioner**: `minAvailable: 2` = at least 2 pods always running. `maxUnavailable: 1` = at most 1 pod down at once. Percentage: `minAvailable: "50%"`. Blocks `kubectl drain` and Cluster Autoscaler until safe.

**Level 3 — Advanced**: PDB status: `currentHealthy`, `desiredHealthy`, `disruptionsAllowed`. `disruptionsAllowed: 0` = no evictions currently safe. PDB with single replica: `minAvailable: 1` on a 1-replica Deployment blocks ALL drains (can't maintain). Use `minAvailable: 0` or fix: scale to 2+ replicas.

**Level 4 — Expert**: PDB and VPA: VPA Updater respects PDB when recreating Pods for resource right-sizing. PDB and Cluster Autoscaler: scale-down (node removal) checks PDB; won't remove node if it would violate PDB. PDB and rolling updates: Deployment rolling update is NOT subject to PDB (Deployment controller manages it separately via maxUnavailable in strategy). PDB `unhealthyPodEvictionPolicy: AlwaysAllow` (K8s 1.26+) — unhealthy pods can always be evicted even if it violates PDB (helps fix stuck deployments).

---

## ⚙️ How It Works

### PDB Specification Options

```yaml
# Option 1: minAvailable (min pods that must be running)
spec:
  minAvailable: 2           # absolute
  # or
  minAvailable: "75%"       # percentage of desired replicas

# Option 2: maxUnavailable (max pods that can be disrupted)
spec:
  maxUnavailable: 1         # absolute
  # or
  maxUnavailable: "25%"     # percentage

# Cannot use both minAvailable AND maxUnavailable
```

### PDB Status

```bash
kubectl get pdb -n my-app

NAME         MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
my-app-pdb   2               N/A               1                     5d

# ALLOWED DISRUPTIONS = current replicas - minAvailable
# = 3 replicas - 2 min = 1 disruption allowed
```

### Single-Replica PDB Trap

```yaml
# TRAP: single replica + minAvailable: 1 = BLOCKS ALL DRAINS
spec:
  replicas: 1
---
spec:
  minAvailable: 1     # 1 must be available, but there's only 1!
                      # Any drain would violate this → permanently blocked

# SOLUTION 1: scale to 2+ replicas
spec:
  replicas: 2         # now drain can evict 1, keeping 1 available

# SOLUTION 2: use maxUnavailable: 1 (same effect but more semantic)
spec:
  maxUnavailable: 1   # allows 1 eviction at a time
```

### PDB with StatefulSet

```yaml
# Protect Kafka (3 brokers, maintain quorum = at least 2)
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: kafka-pdb
spec:
  minAvailable: 2 # quorum: 3/2 majority
  selector:
    matchLabels:
      app: kafka
```

---

## 🔄 E2E Flow: kubectl drain with PDB

```
kubectl drain worker-2 --ignore-daemonsets

  → Drain controller: get all pods on worker-2
  → For each pod: call eviction API

  → Eviction API for pod my-app-7d8f9b-xxxxx:
      1. Find matching PDB: my-app-pdb (minAvailable: 2)
      2. Count currently healthy my-app pods: 3
      3. disruptionsAllowed = 3 - 2 = 1
      4. Is 1 > 0? YES → allow eviction

  → Pod evicted, new pod created on other node

  → Eviction API for pod my-app-7d8f9b-yyyyy (second my-app pod on same node):
      1. Count currently healthy my-app pods: 2 (one just evicted, new one not ready yet)
      2. disruptionsAllowed = 2 - 2 = 0
      3. Is 0 > 0? NO → BLOCK eviction
      4. Retry every 5 seconds...
      5. New pod becomes Ready: count = 3
      6. disruptionsAllowed = 1 → allow eviction

  → All pods evicted, node drained safely, service always had ≥ 2 pods
```

---

## ⚖️ Comparison Table

|                    | PDB minAvailable                       | PDB maxUnavailable    | Deployment maxUnavailable |
| ------------------ | -------------------------------------- | --------------------- | ------------------------- |
| **Applies to**     | Voluntary disruptions                  | Voluntary disruptions | Rolling updates           |
| **Scope**          | PDB-selected pods                      | PDB-selected pods     | Deployment spec           |
| **Blocks drain**   | ✅                                     | ✅                    | ❌                        |
| **Interacts with** | Cluster Autoscaler, kubectl drain, VPA | Same                  | Deployment controller     |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| "PDB protects against node crashes" | Only voluntary disruptions; involuntary disruptions bypass PDB                           |
| "PDB affects rolling updates"       | Deployment rolling update uses its own maxUnavailable, ignores PDB                       |
| "minAvailable: 0 is useless"        | Useful for batch jobs where any can be disrupted but Cluster Autoscaler still sees a PDB |
| "PDB blocks drain forever"          | Drain retries; once pods reschedule and become healthy, drain proceeds                   |

---

## 🚨 Failure Modes

| Failure                                | Symptom                                    | Fix                                                      |
| -------------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| Single replica + PDB blocks drain      | Drain hangs indefinitely                   | Scale to 2+ replicas; or use `--force` on drain (unsafe) |
| Missing PDB                            | Rolling upgrade kills all replicas at once | Create PDB before any maintenance                        |
| PDB selector mismatch                  | Drain proceeds without PDB protection      | Verify `kubectl get pdb` shows matching pods             |
| Very strict PDB (minAvailable = total) | No disruptions ever allowed                | Ensure minAvailable < total replicas                     |

---

## 🔗 Related Keywords

- [Rolling Update Strategy](/kubernetes/rolling-update-strategy/) — deployment rolling update (separate mechanism)
- [K8s Upgrade Strategy](/kubernetes/k8s-upgrade-strategy/) — node drains use PDB
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) — respects PDB during scale-down
- [VPA (Vertical Pod Autoscaler)](/kubernetes/vpa-vertical-pod-autoscaler/) — respects PDB when evicting for resize

---

## 📌 Quick Reference Card

```bash
# Create PDB
kubectl apply -f pdb.yaml

# List PDBs
kubectl get pdb -n my-app

# Describe PDB (shows disruptions allowed)
kubectl describe pdb my-app-pdb -n my-app

# Check if drain is blocked by PDB
kubectl drain <node> --dry-run=client

# Drain ignoring PDB (DANGEROUS - only for emergencies)
kubectl drain <node> --disable-eviction

# Check which pods a PDB protects
kubectl get pdb my-app-pdb -o jsonpath='{.spec.selector}'
kubectl get pods -l <selector-from-above>

# Monitor disruptions
kubectl get events --field-selector reason=DisruptionAllowed -A
```

---

## 🧠 Think About This

PDB is one of the most commonly forgotten Kubernetes resources. Teams add Deployments, Services, HPA, and RBAC — but skip PDB. Then during a routine cluster upgrade or node replacement, the cluster evicts all Pods of a service simultaneously (since the Deployment controller handles availability, but not voluntary eviction). PDB is the bridge between Kubernetes internals and SRE safety guarantees. The rule of thumb: **every production Deployment with more than 1 replica should have a PDB**. Create a Helm chart default or Kustomize transformer that adds PDB alongside every Deployment automatically.
