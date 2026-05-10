---
version: 1
layout: default
title: "VPA (Vertical Pod Autoscaler)"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /kubernetes/vpa-vertical-pod-autoscaler/
id: K8S-032
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  ["Pod", "Resource Requests / Limits", "HPA (Horizontal Pod Autoscaler)"]
used_by: ["QoS Classes", "Cluster Autoscaler"]
related:
  [
    "HPA (Horizontal Pod Autoscaler)",
    "Cluster Autoscaler",
    "Resource Requests / Limits",
    "QoS Classes",
    "KEDA",
  ]
tags: [kubernetes, vpa, vertical-scaling, resource-requests, autoscaling, k8s]
---

# VPA (Vertical Pod Autoscaler)

## ⚡ TL;DR

VPA automatically **right-sizes Pod resource requests** (CPU/memory) based on actual usage history. In `Auto` mode it evicts and restarts Pods with new requests - causing brief downtime. In `Off` mode it only recommends. Don't use VPA CPU + HPA CPU on the same Deployment.

---

## 🔥 Problem This Solves

Developers guess resource requests, often over-provisioning (wasting cluster capacity) or under-provisioning (causing OOMs or CPU throttling). VPA observes actual usage and adjusts requests to fit actual needs.

---

## 📘 Textbook Definition

The Vertical Pod Autoscaler (VPA) automatically adjusts the CPU and memory requests/limits of containers in a Pod based on historical usage metrics. It can apply recommendations automatically (with Pod restarts) or provide them for manual application.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto" # Auto | Recreate | Initial | Off
  resourcePolicy:
    containerPolicies:
      - containerName: app
        minAllowed:
          cpu: 100m
          memory: 128Mi
        maxAllowed:
          cpu: 2
          memory: 4Gi
```

Check recommendations:

```bash
kubectl describe vpa my-app-vpa
# Shows: Lower Bound, Upper Bound, Target, Uncapped Target
```

---

## 🔩 First Principles

- VPA components: **Recommender** (analyzes metrics, computes recommendations), **Updater** (evicts Pods needing update), **Admission Controller** (mutates Pod requests on creation)
- `Auto` mode: evicts Pods, new Pods get updated requests via admission controller
- `Off` mode: recommendations only, no automatic changes
- Cannot be combined with HPA on CPU/memory (they conflict over the same metric)
- VPA can be combined with HPA on **custom** metrics

---

## 🧪 Thought Experiment

Your Spring Boot app has requests of 500m CPU but consistently uses only 50m. VPA observes 2 weeks of data and recommends 80m (with safety margin). In `Auto` mode, it evicts the Pod - it restarts with 80m CPU request. Cluster reclaims 420m CPU per Pod replica - multiply by 10 replicas and you've freed 4 CPU cores.

---

## 🧠 Mental Model / Analogy

VPA is like a **performance coach** who watches an athlete train for weeks, then recommends the optimal equipment (resource) for their actual performance level - not the equipment they thought they needed when they started.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: VPA watches your Pods and tells you (or automatically sets) better CPU/memory sizes based on what they actually use.

**Level 2 - Practitioner**: Three modes: `Off` (recommendations only), `Initial` (apply at Pod creation, no eviction), `Auto` (evict and update running Pods). Requires VPA components installed (not default).

**Level 3 - Advanced**: VPA uses decay-weighted histograms of CPU/memory metrics to compute recommendations. Recommendations: `LowerBound` (safe minimum), `Target` (recommended), `UpperBound` (maximum). `minAllowed`/`maxAllowed` bounds the recommendations.

**Level 4 - Expert**: VPA Admission Controller is a mutating admission webhook - all Pod creation passes through it. In `Auto` mode, the Updater selects Pods with out-of-date requests and evicts them; admission controller injects new requests on re-creation. VPA uses `checkpoints` (VPACheckpoint objects) to persist historical data. Memory recommendations use OOM kill history.

---

## ⚙️ How It Works

### VPA Architecture

```
Metrics Server → CPU/Memory per container per Pod

VPA Recommender:
  - Analyzes usage over time (default: 8 days lookback)
  - Computes CPU/memory recommendations
  - Writes to VPA status

VPA Updater:
  - Polls VPA recommendations
  - If Pod requests differ significantly: evict Pod
  - New Pod created → hits Admission Controller

VPA Admission Controller (mutating webhook):
  - Intercepts new Pod creation
  - Overwrites resource requests with VPA recommendation
  - Pod starts with right-sized resources
```

### Update Modes

| Mode       | Behavior                            | Downtime            |
| ---------- | ----------------------------------- | ------------------- |
| `Off`      | Recommendations only                | None                |
| `Initial`  | Apply on Pod creation               | None (restart-free) |
| `Recreate` | Evict and restart Pods              | Brief               |
| `Auto`     | Same as Recreate (in-place planned) | Brief               |

---

## 🔄 E2E Flow: Memory Right-Sizing

```
App running with 2Gi memory request, actually uses 300Mi

VPA Recommender:
  - Observes 300Mi average + 500Mi p95
  - Adds safety margin: recommends 600Mi
  - Writes recommendation to VPA status

VPA Updater (if mode=Auto):
  - Detects Pod requests (2Gi) >> recommendation (600Mi)
  - Evicts Pod

VPA Admission Controller:
  - New Pod creation intercepted
  - Overwrites memory request: 2Gi → 600Mi
  - Pod starts with 600Mi request
  - 1.4Gi memory freed per replica
```

---

## ⚖️ Comparison Table

|                      | VPA                              | HPA                | Manual tuning      |
| -------------------- | -------------------------------- | ------------------ | ------------------ |
| **What changes**     | Pod size (CPU/mem)               | Pod count          | Nothing (static)   |
| **Restart required** | Yes (Auto/Recreate)              | No                 | Deployment rollout |
| **Data-driven**      | Yes (historical)                 | Yes (real-time)    | No                 |
| **Best for**         | Batch jobs, stateful, singletons | Stateless services | Unknown workloads  |

---

## ⚠️ Common Misconceptions

| Misconception                     | Reality                                                             |
| --------------------------------- | ------------------------------------------------------------------- |
| "VPA and HPA work great together" | Conflict on CPU/memory; only combine with custom metrics HPA        |
| "VPA scales replicas"             | VPA changes resource _size_, not _count_                            |
| "`Off` mode is useless"           | `Off` is great for auditing - see recommendations before committing |
| "VPA is always-on after install"  | Must create VPA objects targeting specific Deployments              |

---

## 🚨 Failure Modes

| Failure                       | Symptom                         | Fix                                                          |
| ----------------------------- | ------------------------------- | ------------------------------------------------------------ |
| VPA evicts production Pods    | Unplanned restarts              | Use `PodDisruptionBudget` to limit evictions                 |
| VPA recommends too low        | OOMKill                         | Increase `minAllowed` memory; use `Off` mode to review first |
| VPA conflicts with HPA        | Replicas fight with requests    | Don't use VPA CPU + HPA CPU together                         |
| VPA Admission Controller down | Pods start with wrong resources | Ensure VPA admission controller is healthy                   |

---

## 🔗 Related Keywords

- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - scale replicas
- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) - what VPA adjusts
- [QoS Classes](/kubernetes/qos-classes/) - impacted by VPA changes
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) - VPA + CA work together for full right-sizing
- [KEDA](/kubernetes/keda/) - alternative for event-driven scaling

---

## 📌 Quick Reference Card

```bash
# Install VPA (from K8s autoscaler repo)
kubectl apply -f https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler/deploy

# Check recommendations
kubectl describe vpa my-app-vpa

# Get all VPA objects
kubectl get vpa

# Useful outputs:
# Lower Bound: safe minimum
# Target:      recommended value
# Upper Bound: don't exceed this
# Uncapped:    raw recommendation ignoring maxAllowed

# Switch to Off mode (disable automatic updates)
kubectl patch vpa my-app-vpa \
  --patch '{"spec":{"updatePolicy":{"updateMode":"Off"}}}'
```

---

## 🧠 Think About This

VPA `Auto` mode restarts your Pods. For a Java application with 60-second startup time and 3 replicas, VPA could disrupt service if it evicts all three at once. Always pair VPA `Auto` mode with `PodDisruptionBudget` that ensures at least `minAvailable: 2` (or `maxUnavailable: 1`) - this forces VPA to evict one at a time, maintaining service availability during right-sizing.
