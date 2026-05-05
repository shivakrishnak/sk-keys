---
layout: default
title: "Taints and Tolerations"
parent: "Kubernetes"
nav_order: 899
permalink: /kubernetes/taints-and-tolerations/
number: "0899"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Node", "Scheduler (K8s)", "Pod"]
used_by: ["DaemonSet", "Node Affinity / Anti-Affinity", "K8s Cost Optimization"]
related:
  ["Node Affinity / Anti-Affinity", "Scheduler (K8s)", "DaemonSet", "Node"]
tags: [kubernetes, taints, tolerations, scheduling, dedicated-nodes, k8s]
---

# Taints and Tolerations

## ⚡ TL;DR

A **Taint** on a Node repels Pods from being scheduled there. A **Toleration** on a Pod allows it to be scheduled on tainted nodes. Used to dedicate nodes to specific workloads (GPU nodes for ML), mark nodes as unschedulable (draining), or enable DaemonSets to run on control plane nodes.

---

## 🔥 Problem This Solves

You have expensive GPU nodes that should ONLY run ML training jobs, not general workloads. Or you're draining a node for maintenance and need to prevent new Pods from scheduling there. Taints + Tolerations solve "keep most Pods OFF this node, only allow specific Pods."

---

## 📘 Textbook Definition

Taints and Tolerations are a Kubernetes mechanism that works together to ensure pods are not scheduled onto inappropriate nodes. Taints are applied to nodes; Tolerations are applied to pods. A pod can be scheduled on a tainted node only if it has a matching toleration.

---

## ⏱️ 30 Seconds

```bash
# Taint a node (dedicate to GPU workloads)
kubectl taint nodes gpu-node-1 dedicated=gpu:NoSchedule

# Pod with toleration can schedule there
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  nodeSelector:
    accelerator: nvidia-gpu   # still need to attract to GPU node
```

---

## 🔩 First Principles

- Taint format: `key=value:effect` (key-only or key=value with effect)
- **Effects**:
  - `NoSchedule`: don't schedule new Pods without toleration (existing Pods unaffected)
  - `PreferNoSchedule`: prefer not to schedule (soft); scheduler tries to avoid
  - `NoExecute`: evict existing Pods without toleration + prevent new scheduling
- Toleration `operator: Equal` matches key+value; `operator: Exists` matches just key
- Tolerations don't guarantee placement — they just allow it; use nodeAffinity to attract
- `tolerationSeconds` with `NoExecute`: Pod tolerated for N seconds before eviction

---

## 🧪 Thought Experiment

You have 2 nodes: `cpu-node` (general purpose) and `gpu-node` (expensive GPU). You taint `gpu-node` with `dedicated=gpu:NoSchedule`. Now: regular Pods go to `cpu-node`, GPU Pods with toleration can go to either node. To ensure GPU Pods ONLY go to `gpu-node`, add `nodeAffinity` for `accelerator: nvidia-gpu`. Taints repel; affinity attracts.

---

## 🧠 Mental Model / Analogy

Taints and Tolerations are like **"No Dogs Allowed" signs**: the taint is the sign (node says "no unapproved pods"). The toleration is the service animal certification (pod says "I'm approved for this node"). Even with certification (toleration), the guide dog owner still needs to walk to the right building (nodeAffinity to attract to the node).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Taint a node to keep most Pods away. Add toleration to Pods that should be allowed on that node.

**Level 2 — Practitioner**: Three effects: NoSchedule (don't schedule new), PreferNoSchedule (try to avoid), NoExecute (evict existing + block new). Control plane nodes have `node-role.kubernetes.io/control-plane:NoSchedule` by default.

**Level 3 — Advanced**: System-added taints: `node.kubernetes.io/not-ready:NoExecute` (node unhealthy), `node.kubernetes.io/unreachable:NoExecute` (network issue), `node.kubernetes.io/memory-pressure:NoSchedule`. Default toleration `tolerationSeconds: 300` for `not-ready` and `unreachable` on all pods (5 min before eviction). DaemonSets automatically get tolerations for these system taints.

**Level 4 — Expert**: `tolerationSeconds: 0` = immediate eviction when NoExecute taint added (for critical workload migration). Multiple taints on a node: pod must tolerate ALL taints to be scheduled. Taint-based eviction: when node condition worsens (MemoryPressure, DiskPressure), kubelet auto-taints node. StatefulSet pods with PVCs on local storage: taint eviction requires manual handling (PV stays on node).

---

## ⚙️ How It Works

### Taint Operations

```bash
# Add taint
kubectl taint nodes worker-1 dedicated=gpu:NoSchedule
kubectl taint nodes worker-1 maintenance=true:NoExecute

# Remove taint (append -)
kubectl taint nodes worker-1 dedicated=gpu:NoSchedule-

# View taints on node
kubectl describe node worker-1 | grep Taints

# Taint all nodes in a group (e.g., GPU node group)
kubectl taint nodes -l node.kubernetes.io/instance-type=p3.2xlarge dedicated=gpu:NoSchedule
```

### Toleration Patterns

```yaml
# Exact match: key=value:effect
tolerations:
- key: "dedicated"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"

# Key only (any value): key exists
tolerations:
- key: "dedicated"
  operator: "Exists"
  effect: "NoSchedule"

# Tolerate all taints (DaemonSet pattern - dangerous for regular pods)
tolerations:
- operator: "Exists"    # matches all keys, all effects

# With expiry for NoExecute (stay 10 minutes)
tolerations:
- key: "node.kubernetes.io/not-ready"
  operator: "Exists"
  effect: "NoExecute"
  tolerationSeconds: 600
```

### Dedicated Node Pattern (Full Setup)

```yaml
# Node setup:
# kubectl taint nodes gpu-1 nvidia.com/gpu=present:NoSchedule
# kubectl label nodes gpu-1 accelerator=nvidia-tesla-v100

# Pod spec:
spec:
  tolerations:
    - key: "nvidia.com/gpu"
      operator: "Equal"
      value: "present"
      effect: "NoSchedule"
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: accelerator
                operator: In
                values: [nvidia-tesla-v100]
  containers:
    - name: ml-training
      resources:
        limits:
          nvidia.com/gpu: 1 # GPU resource request
```

### System Taints (Auto-Added by Kubernetes)

```
node.kubernetes.io/not-ready:NoExecute          → added when Ready condition False
node.kubernetes.io/unreachable:NoExecute        → added when node unreachable
node.kubernetes.io/memory-pressure:NoSchedule  → added when MemoryPressure
node.kubernetes.io/disk-pressure:NoSchedule    → added when DiskPressure
node.kubernetes.io/pid-pressure:NoSchedule     → added when PIDPressure
node.kubernetes.io/unschedulable:NoSchedule    → added when kubectl cordon
node.kubernetes.io/network-unavailable:NoSchedule → added when network not configured
```

---

## 🔄 E2E Flow: Node Drain with Taint

```
Operations team: kubectl drain worker-1 --ignore-daemonsets --delete-emptydir-data

  → kubectl cordon worker-1:
      Adds taint: node.kubernetes.io/unschedulable:NoSchedule
      Node.spec.unschedulable = true
      New Pods NOT scheduled here

  → kubectl drain evicts running Pods:
      For each Pod (except DaemonSet):
        - Sends evict API call
        - Pod gracefully terminates (preStop + SIGTERM)
        - Pod controller creates replacement on other node

  → Maintenance done: kubectl uncordon worker-1
      Removes unschedulable taint
      Node accepts new Pods again
```

---

## ⚖️ Comparison Table

|                           | Taints                         | nodeAffinity           | nodeSelector           |
| ------------------------- | ------------------------------ | ---------------------- | ---------------------- |
| **Direction**             | Node repels                    | Pod attracts           | Pod attracts           |
| **Effect on existing**    | NoExecute evicts               | IgnoredDuringExecution | IgnoredDuringExecution |
| **Use case**              | Dedicated/drain nodes          | AZ/GPU targeting       | Simple node selection  |
| **Required or preferred** | Hard + soft (PreferNoSchedule) | Both                   | Hard only              |

---

## ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                   |
| ------------------------------------------ | ------------------------------------------------------------------------- |
| "Toleration = Pod must go to tainted node" | Toleration allows it, doesn't attract it; add nodeAffinity to attract     |
| "NoSchedule evicts running pods"           | NoSchedule only affects NEW scheduling; NoExecute evicts running pods     |
| "Taints are only for dedicated nodes"      | Also auto-applied by K8s for node conditions (not-ready, memory-pressure) |
| "Multiple taints: one toleration needed"   | Pod must tolerate ALL taints on a node to be scheduled there              |

---

## 🚨 Failure Modes

| Failure                                | Symptom                             | Fix                                                                   |
| -------------------------------------- | ----------------------------------- | --------------------------------------------------------------------- |
| DaemonSet not running on control plane | Pods missing on control-plane nodes | Add toleration for `node-role.kubernetes.io/control-plane:NoSchedule` |
| Pod evicted after NoExecute added      | Pod restarted on different node     | Expected; ensure no local state or use PVCs                           |
| GPU nodes running general workloads    | Expensive nodes wasted              | Add taint to GPU nodes; only GPU jobs have toleration                 |
| Pods pending after cordon/drain        | All replicas on drained node        | Ensure enough other nodes exist for rescheduling                      |

---

## 🔗 Related Keywords

- [Node Affinity / Anti-Affinity](/kubernetes/node-affinity-anti-affinity/) — attracts pods to nodes (taints repel)
- [Scheduler (K8s)](/kubernetes/scheduler-k8s/) — evaluates taints during scheduling
- [DaemonSet](/kubernetes/daemonset/) — auto-gets system taint tolerations
- [Node](/kubernetes/node/) — where taints live

---

## 📌 Quick Reference Card

```bash
# Add taint
kubectl taint node <node> key=value:NoSchedule
kubectl taint node <node> key=value:NoExecute
kubectl taint node <node> key=value:PreferNoSchedule

# Remove taint (dash suffix)
kubectl taint node <node> key=value:NoSchedule-

# Cordon (adds unschedulable, prevents new pods)
kubectl cordon <node>
kubectl uncordon <node>

# Drain (cordon + evict all pods)
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --grace-period=60

# Check node taints
kubectl describe node <node> | grep -A 5 Taints

# Effects: NoSchedule | PreferNoSchedule | NoExecute
# Operators: Equal (key=value) | Exists (key only)
```

---

## 🧠 Think About This

The system taint `node.kubernetes.io/not-ready:NoExecute` with default `tolerationSeconds: 300` means that when a node becomes `NotReady`, Kubernetes waits 5 minutes before evicting its Pods to other nodes. This is intentional: it allows the node time to recover (a brief network hiccup, kubelet restart). For stateless apps, 5 minutes is acceptable. For payment processing or trading systems, it's too long. You can override: set `tolerationSeconds: 30` for fast-failover services, `tolerationSeconds: 0` for instant eviction on node failure. This is one of the most important tuning parameters for production K8s latency SLAs.
