---
layout: default
title: "Scheduler (K8s)"
parent: "Kubernetes"
nav_order: 32
permalink: /kubernetes/scheduler-k8s/
id: K8S-032
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  ["Pod", "Node", "Kubernetes Architecture", "Resource Requests / Limits"]
used_by:
  [
    "Deployment",
    "StatefulSet",
    "Node Affinity / Anti-Affinity",
    "Taints and Tolerations",
  ]
related:
  [
    "Node Affinity / Anti-Affinity",
    "Taints and Tolerations",
    "Resource Requests / Limits",
    "Pod Disruption Budget",
    "QoS Classes",
  ]
tags: [kubernetes, scheduler, pod-placement, node-selection, affinity, k8s]
---

# Scheduler (K8s)

## ⚡ TL;DR

The Kubernetes Scheduler watches for **unscheduled Pods** and assigns them to nodes using a two-phase process: **Filter** (eliminate ineligible nodes) + **Score** (rank eligible nodes). It considers resource requests, affinity, taints/tolerations, topology, and custom plugins.

---

## 🔥 Problem This Solves

Someone must decide which node each Pod runs on, considering resources, constraints, anti-affinity, taints, and topology. The Scheduler automates this placement decision continuously as Pods are created.

---

## 📘 Textbook Definition

The Kubernetes Scheduler is a control plane component that watches for newly created Pods with no assigned node and selects a node for them to run on. It makes scheduling decisions based on resource requirements, hardware/software/policy constraints, affinity/anti-affinity, data locality, and inter-workload interference.

---

## ⏱️ 30 Seconds

```
Scheduling pipeline for each unscheduled Pod:

Phase 1 - FILTER (eliminate nodes):
  ✓ Node has enough CPU/memory (PodFitsResources)
  ✓ Port is not already in use (PodFitsHostPorts)
  ✓ Node matches nodeSelector (MatchNodeSelector)
  ✓ Node is not tainted or Pod has toleration (TaintToleration)
  ✓ Node satisfies Pod's affinity rules (PodAffinity)
  ✓ Volume can be attached (VolumeBinding)

Phase 2 - SCORE (rank remaining nodes):
  ↑ Less requested resources (LeastAllocated)
  ↑ Image already cached (ImageLocality)
  ↑ Fewer existing Pods (BalancedAllocation)

→ Highest scored node wins → Pod bound to node
```

---

## 🔩 First Principles

- Scheduler is **pluggable** — scheduling framework with extension points
- Scheduling is done per-Pod — no batch or global optimization
- Resource requests (not limits) determine feasibility
- Scheduler writes `pod.spec.nodeName` — kubelet sees this and runs the Pod
- Anti-affinity and topology spread constraints are hints, not hard blocks (unless `required`)

---

## 🧪 Thought Experiment

Three nodes: A (2 CPU free), B (4 CPU free), C (0.5 CPU free, correct zone). Pod needs 1 CPU. Filter: C eliminated (insufficient CPU). Score: B wins (more free CPU, better balanced allocation). But Pod has `nodeAffinity: requiredDuringScheduling: zone=us-east-1a` and C is the only node in that zone. Result: Pod stays `Pending` until more capacity in us-east-1a. Hard constraints override scoring.

---

## 🧠 Mental Model / Analogy

The Scheduler is like an **HR recruitment team**: first they filter candidates who don't meet minimum qualifications (can't run this Pod), then they rank the remaining candidates by fit (best resource match). The highest-ranked candidate gets the job (node assignment).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: The Scheduler picks which machine each Pod runs on, based on available resources.

**Level 2 — Practitioner**: Uses `nodeSelector` for simple node selection. Affinity for complex rules. Taints/tolerations to prevent/allow scheduling on specific nodes.

**Level 3 — Advanced**: Scheduling framework: Filter, Score, Reserve, Permit, Bind extension points. Custom schedulers via `schedulerName` in PodSpec. Topology spread constraints: spread Pods across zones/nodes.

**Level 4 — Expert**: Preemption: Scheduler can evict lower-priority Pods to make room for higher-priority Pods. `PriorityClass` assigns priority. Gang scheduling: batch workloads need all-or-nothing scheduling (handled by `Coscheduling` plugin). Scheduler extenders and plugins via `KubeSchedulerConfiguration`.

---

## ⚙️ How It Works

### Scheduling Framework Extension Points

```
Scheduling cycle (per pod):
  PreFilter → Filter → PostFilter (preemption)
  → PreScore → Score → NormalizeScore → Reserve

Binding cycle:
  Permit → PreBind → Bind → PostBind
```

### Topology Spread Constraints

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1 # max difference across zones
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: my-app
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname # spread across nodes too
      whenUnsatisfiable: ScheduleAnyway # soft constraint
```

### Priority and Preemption

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
preemptionPolicy: PreemptLowerPriority
---
spec:
  priorityClassName: high-priority
```

---

## 🔄 E2E Flow: Preemption

```
Cluster: all nodes nearly full
High-priority Pod created (PriorityClass: 1000000)
  → Scheduler: filter phase → NO eligible nodes
  → PostFilter: can preemption help?
      - Find node with BestEffort/Burstable Pods
      - Evict lowest-priority Pods
      - High-priority Pod fits on now-freed node
  → PodDisruptionBudget check: eviction allowed?
  → Evict target Pods (graceful termination)
  → Bind high-priority Pod to node
```

---

## ⚖️ Comparison Table

|                           | Hard Constraint                                  | Soft Preference                                   |
| ------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| **Affinity**              | `requiredDuringSchedulingIgnoredDuringExecution` | `preferredDuringSchedulingIgnoredDuringExecution` |
| **Topology spread**       | `DoNotSchedule`                                  | `ScheduleAnyway`                                  |
| **Taint**                 | `NoSchedule`                                     | `PreferNoSchedule`                                |
| **Result if unsatisfied** | Pod stays Pending                                | Best-effort placement                             |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                      |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| "Scheduler uses actual CPU usage"     | Scheduler uses **resource requests** only (not actual usage)                 |
| "Hard anti-affinity ensures spread"   | Hard anti-affinity can cause Pods to stay Pending if no valid node           |
| "Default scheduler handles all cases" | Complex batch scheduling (gang scheduling) needs custom scheduler or plugins |
| "Scheduler runs continuously"         | Scheduler only acts on `nodeName: ""` Pods (newly created, no assignment)    |

---

## 🚨 Failure Modes

| Failure                   | Symptom                 | Fix                                                                     |
| ------------------------- | ----------------------- | ----------------------------------------------------------------------- |
| Scheduler down            | New Pods stay Pending   | Run 2 scheduler instances (leader-elected)                              |
| Over-constrained Pods     | Pods Pending forever    | Check constraints: `kubectl describe pod` → "Events: Failed scheduling" |
| Preemption cascades       | Production Pods evicted | Set proper `PriorityClass` hierarchy; use `PodDisruptionBudget`         |
| Taint/toleration mismatch | Pods avoid needed nodes | Check node taints: `kubectl describe node`                              |

---

## 🔗 Related Keywords

- [Node Affinity / Anti-Affinity](/kubernetes/node-affinity-anti-affinity/) — scheduling constraints
- [Taints and Tolerations](/kubernetes/taints-and-tolerations/) — node-level scheduling control
- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) — determines feasibility
- [Pod Disruption Budget](/kubernetes/pod-disruption-budget/) — protects during preemption
- [QoS Classes](/kubernetes/qos-classes/) — affects eviction priority

---

## 📌 Quick Reference Card

```bash
# Check pending Pod scheduling reason
kubectl describe pod <pending-pod>
# Look in Events: "Failed scheduling": reason

# Check node resources
kubectl describe node <name>
# Look for: "Allocated resources:" section

# Use custom scheduler
spec:
  schedulerName: my-custom-scheduler

# Debug scheduling (enable verbose logs on kube-scheduler)
--v=10

# Topology spread: check zone labels
kubectl get nodes -L topology.kubernetes.io/zone
```

---

## 🧠 Think About This

The Scheduler makes decisions based on **requested** resources, not actual usage. A node where Pods request 90% CPU but use only 30% looks "full" to the Scheduler. VPA right-sizes requests to match actual usage, making Scheduler decisions more accurate — this is why VPA + Cluster Autoscaler together can dramatically improve cluster bin-packing efficiency. Without accurate requests, you're either over-provisioning nodes or leaving schedulable capacity unused.
