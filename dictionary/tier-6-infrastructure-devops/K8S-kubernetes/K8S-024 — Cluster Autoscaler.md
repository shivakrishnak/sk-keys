---
layout: default
title: "Cluster Autoscaler"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /kubernetes/cluster-autoscaler/
id: K8S-024
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  [
    "Node",
    "Cluster",
    "HPA (Horizontal Pod Autoscaler)",
    "Resource Requests / Limits",
  ]
used_by: ["K8s Cost Optimization", "KEDA"]
related:
  [
    "HPA (Horizontal Pod Autoscaler)",
    "VPA (Vertical Pod Autoscaler)",
    "KEDA",
    "Node",
    "K8s Cost Optimization",
  ]
tags: [kubernetes, cluster-autoscaler, node-autoscaling, cloud-scaling, k8s]
---

# Cluster Autoscaler

## ⚡ TL;DR

Cluster Autoscaler (CA) automatically **adds nodes** when Pods are stuck `Pending` due to insufficient resources, and **removes underutilized nodes** after a configurable cooldown. It integrates with cloud provider APIs (AWS ASG, GKE Node Pools, AKS VMSS).

---

## 🔥 Problem This Solves

HPA scales Pod replicas, but if all nodes are full, new Pods stay `Pending`. Someone must add nodes. CA automates this cloud-provider scaling loop: Pending Pods → add node → Pods schedule → load drops → remove idle node.

---

## 📘 Textbook Definition

The Cluster Autoscaler is a Kubernetes component that automatically adjusts the size of a Kubernetes cluster (adds or removes nodes) when workload resource requirements cannot be met with the current set of nodes or when nodes are consistently underutilized.

---

## ⏱️ 30 Seconds

```
HPA: 5 → 15 replicas (more Pods needed)
   → 5 new Pods: Pending (no node capacity)

Cluster Autoscaler:
  → Detects Pending Pods unschedulable
  → Determines how many nodes needed (simulates scheduling)
  → Calls cloud API: add 2 nodes to node group
  → Nodes join cluster (2-4 min)
  → Pods schedule on new nodes

Load drops:
  → Nodes underutilized for 10 min
  → CA: safely drain nodes (checks PDB, local storage, DaemonSets)
  → Remove nodes via cloud API
```

---

## 🔩 First Principles

- CA triggers scale-UP when: Pods are `Pending` with `Unschedulable` reason due to resource constraints
- CA triggers scale-DOWN when: node utilization < `scale-down-utilization-threshold` (default 50%) for `scale-down-unneeded-time` (default 10 min)
- CA does NOT react to CPU/memory metrics — only to **schedulability** (can Pods fit?)
- Resource requests must be accurate — CA simulates scheduling using requests, not actual usage

---

## 🧪 Thought Experiment

What if resource requests are much higher than actual usage? Node shows 90% requested but only 30% actual CPU. CA sees 90% requested → "node is not underutilized" → never scales down. You pay for idle nodes. This is why accurate resource requests + VPA work together with CA: VPA right-sizes requests, CA right-sizes node count.

---

## 🧠 Mental Model / Analogy

CA is like a **hotel manager** who adds more rooms (nodes) when all are booked (Pods Pending) and closes empty wings (removes nodes) when occupancy drops. The manager works with the cloud provider's construction crew (AWS/GCP/Azure) to build/demolish rooms on demand.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: CA adds machines when Kubernetes needs more space for Pods, and removes machines when they're empty.

**Level 2 — Practitioner**: CA integrates with cloud provider node groups (ASG, VMSS, MIG). Min/max node count per node group. Node removal protects nodes with local storage, non-migratable system Pods, and PDB constraints.

**Level 3 — Advanced**: CA can manage multiple node groups (different instance types). Node group priority: prefer cheaper spot instances. Expander strategies: `random`, `most-pods`, `least-waste`, `priority`. `--balance-similar-node-groups` spreads load across equivalent groups.

**Level 4 — Expert**: CA uses scheduling simulation (not actual scheduler) to determine if Pods can fit on new nodes. Overprovisioning trick: deploy low-priority `pause` Pods to pre-warm capacity — CA never removes nodes holding them. Scale-down safety: checks PDB compliance, local PVs, kube-system Pods, and min size constraints before draining.

---

## ⚙️ How It Works

### Scale-Up Decision

```
Every 10s (configurable):
  1. Find Pods with status Pending + reason Unschedulable
  2. Simulate: can they fit on existing nodes? No
  3. Find node group(s) that could accommodate them
  4. Select expander strategy (least-waste, priority, etc.)
  5. Call cloud API to increase node group size
  6. Wait for node to register and become Ready
  7. Pods schedule on new node
```

### Scale-Down Decision

```
Every 10s:
  1. Find nodes where sum(Pod requests) / Node capacity < threshold
  2. Check scale-down-unneeded-time (must be unneeded for N min)
  3. Simulate: can all Pods on this node fit elsewhere?
  4. Check PodDisruptionBudgets — would removal violate any?
  5. Check for non-migratable Pods (local storage, system)
  6. Drain node (evict Pods gracefully)
  7. Call cloud API to remove node
```

### AWS EKS Configuration

```yaml
# kube-system Deployment
containers:
  - name: cluster-autoscaler
    image: registry.k8s.io/autoscaling/cluster-autoscaler:v1.28.0
    command:
      - ./cluster-autoscaler
      - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/<cluster-name>
      - --balance-similar-node-groups
      - --skip-nodes-with-system-pods=false
      - --scale-down-utilization-threshold=0.5
      - --scale-down-unneeded-time=10m
```

---

## 🔄 E2E Flow: Scale-Out Under Load

```
App: HPA scales from 5 → 15 replicas (traffic spike)
  → 10 new Pods: Pending (2 nodes at capacity)

CA (10s check):
  → Pending Pods detected
  → Simulation: need 1 more node (m5.xlarge, 4 CPU / 16Gi)
  → AWS API: increase ASG desired=3
  → EC2 launches new instance (2-4 min)
  → kubelet starts, registers as Node
  → Scheduler places 10 Pending Pods on new node
  → All Pods: Running

Traffic drops (20 min later):
  → HPA scales back to 5 replicas
  → New node: 3 Pods, 30% utilization
  → CA: unneeded for 10 min
  → PDB check: no violations
  → Drain node, terminate EC2 instance
  → Cost savings restored
```

---

## ⚖️ Comparison Table

|                       | Cluster Autoscaler   | KEDA                        | HPA                       |
| --------------------- | -------------------- | --------------------------- | ------------------------- |
| **What scales**       | Nodes                | Pod replicas (event-driven) | Pod replicas (CPU/custom) |
| **Trigger**           | Pending Pods         | Event sources (queue depth) | Metrics threshold         |
| **Cloud integration** | Required             | Optional                    | Not needed                |
| **Delay**             | 2-5 min (VM startup) | Seconds                     | 15s-60s                   |

---

## ⚠️ Common Misconceptions

| Misconception               | Reality                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| "CA reacts to CPU usage"    | CA reacts to Pending Pods (schedulability), not CPU metrics      |
| "CA removes any empty node" | CA protects nodes with system Pods, local storage, DaemonSets    |
| "CA + HPA = instant scale"  | HPA scales Pods fast; CA adds nodes in 2-5 min (VM startup lag)  |
| "CA works on bare metal"    | CA requires cloud provider API; bare-metal needs custom provider |

---

## 🚨 Failure Modes

| Failure                          | Symptom                                       | Fix                                            |
| -------------------------------- | --------------------------------------------- | ---------------------------------------------- |
| CA can't scale (IAM permissions) | Pods Pending; CA errors in logs               | Add ASG/VMSS permissions to CA service account |
| Node group at maxSize            | Pods stay Pending despite CA                  | Increase maxSize; or add new node group        |
| Incorrect resource requests      | CA doesn't scale down (nodes "full" on paper) | Use VPA to right-size requests                 |
| Scale-down too aggressive        | Service disruption from node removal          | Tune `scale-down-unneeded-time`; use PDBs      |

---

## 🔗 Related Keywords

- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) — scales Pods (CA scales nodes)
- [VPA (Vertical Pod Autoscaler)](/kubernetes/vpa-vertical-pod-autoscaler/) — right-sizes requests
- [KEDA](/kubernetes/keda/) — event-driven scaling (complementary)
- [Node](/kubernetes/node/) — what CA adds/removes
- [K8s Cost Optimization](/kubernetes/k8s-cost-optimization/) — CA is key for cost efficiency

---

## 📌 Quick Reference Card

```bash
# Check CA logs
kubectl logs -n kube-system -l app=cluster-autoscaler

# Check why Pod is Pending (unschedulable)
kubectl describe pod <pending-pod>
# Look for: "Insufficient cpu", "Insufficient memory"

# Annotate node to prevent CA removal
kubectl annotate node <node> \
  cluster-autoscaler.kubernetes.io/scale-down-disabled=true

# Check node group status (AWS)
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names <name>

# CA status
kubectl describe configmap cluster-autoscaler-status -n kube-system
```

---

## 🧠 Think About This

The fundamental limitation of Cluster Autoscaler is the 2-5 minute VM startup latency. If your traffic spikes are fast (flash sales, viral events), CA can't react quickly enough — Pods queue up Pending for minutes during the spike. Solutions: pre-warm nodes using overprovisioning (dummy low-priority Pods keep nodes "warm"), use Spot/Preemptible with faster ASG policies, or use KEDA's scale-from-zero with pre-warming strategies.
