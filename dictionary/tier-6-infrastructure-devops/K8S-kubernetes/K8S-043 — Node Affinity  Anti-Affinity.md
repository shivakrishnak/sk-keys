---
layout: default
title: "Node Affinity / Anti-Affinity"
parent: "Kubernetes"
nav_order: 43
permalink: /kubernetes/node-affinity-anti-affinity/
number: "K8S-043"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Scheduler (K8s)", "Node", "Pod"]
used_by: ["StatefulSet", "DaemonSet", "K8s Cost Optimization"]
related:
  ["Taints and Tolerations", "Scheduler (K8s)", "Node", "Pod Disruption Budget"]
tags: [kubernetes, affinity, node-affinity, anti-affinity, scheduling, k8s]
---

# Node Affinity / Anti-Affinity

## ⚡ TL;DR

**Node Affinity** attracts Pods to nodes with specific labels (e.g., run on GPU nodes, run in us-east-1a AZ). **Pod Anti-Affinity** repels Pods from nodes that already have similar Pods (e.g., spread replicas across AZs for HA). More expressive than `nodeSelector`; uses `requiredDuringScheduling` (hard) or `preferredDuringScheduling` (soft) rules.

---

## 🔥 Problem This Solves

You need to: run ML workloads only on GPU nodes, ensure all Pods don't pile up in one AZ (causing an AZ outage to kill all replicas), run frontend and backend on different nodes for fault isolation, or constrain expensive workloads to spot instance nodes. Affinity/Anti-Affinity enables all of this declaratively.

---

## 📘 Textbook Definition

Node Affinity allows you to constrain which nodes a Pod can be scheduled onto based on node labels. Pod Affinity/Anti-Affinity allows you to constrain which nodes a Pod can be scheduled onto based on the labels of Pods already running on that node.

---

## ⏱️ 30 Seconds

```yaml
affinity:
  # Hard: MUST run on GPU node
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: accelerator
              operator: In
              values: [nvidia-tesla-v100]

  # Soft: PREFER different nodes for replicas
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: my-service
          topologyKey: kubernetes.io/hostname
```

---

## 🔩 First Principles

- **Node Affinity**: rules on **node labels**
- **Pod Affinity**: co-locate with Pods that have specific labels
- **Pod Anti-Affinity**: avoid nodes that have Pods with specific labels
- `requiredDuringSchedulingIgnoredDuringExecution`: hard rule (unschedulable if not met); existing Pods NOT affected if node label changes
- `preferredDuringSchedulingIgnoredDuringExecution`: soft rule with weight (1-100); best effort
- `topologyKey`: the node label used as "zone" for anti-affinity (`kubernetes.io/hostname` = per-node, `topology.kubernetes.io/zone` = per-AZ)

---

## 🧪 Thought Experiment

Your API Deployment has 6 replicas across a 3-AZ cluster. Without anti-affinity: scheduler may place all 6 on AZ-A nodes (perfectly valid scheduling). AZ-A has an outage: all 6 replicas gone. With pod anti-affinity on `topology.kubernetes.io/zone`: scheduler spreads 2 replicas per AZ. AZ-A outage: 4/6 replicas survive. Service stays up.

---

## 🧠 Mental Model / Analogy

Node affinity is like **restaurant seating preferences**: "I want a table by the window" (prefer GPU nodes) or "I must sit in the non-smoking section" (require SSD nodes). Pod anti-affinity is like telling the host "please don't seat me next to another party in our group at the same table" (spread replicas across nodes).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Affinity = attract to certain nodes. Anti-affinity = spread away from certain pods. Used for GPU nodes, AZ spreading, fault isolation.

**Level 2 — Practitioner**: `nodeAffinity.required` = hard constraint (pod stays Pending if no matching node). `preferred` = soft (best effort with weight). Anti-affinity `topologyKey: kubernetes.io/hostname` = spread across different nodes.

**Level 3 — Advanced**: Multiple `matchExpressions` within one `nodeSelectorTerm` = AND. Multiple `nodeSelectorTerms` = OR. `operator` types: `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`. Pod affinity vs nodeSelector: affinity is more expressive (ranges, OR logic).

**Level 4 — Expert**: `TopologySpreadConstraint` (preferred over pod anti-affinity for spreading): `maxSkew`, `topologyKey`, `whenUnsatisfiable: DoNotSchedule/ScheduleAnyway`. More predictable than anti-affinity for large deployments. `IgnoredDuringExecution` vs `RequiredDuringExecution` (alpha): future versions will evict Pods if node labels change and they violate required affinity. Pod affinity performance: O(Pods × Rules) at scale — expensive for large clusters.

---

## ⚙️ How It Works

### Node Affinity Examples

```yaml
# Required: must run on nodes with SSD in us-east
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: topology.kubernetes.io/region
          operator: In
          values: [us-east-1]
        - key: node.kubernetes.io/instance-type
          operator: NotIn
          values: [t2.micro, t2.small]   # AND with above

# Preferred: prefer nodes with label dedicated=ml (weight 80)
# and prefer on-demand instances (weight 20)
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 80
      preference:
        matchExpressions:
        - key: dedicated
          operator: In
          values: [ml-workload]
    - weight: 20
      preference:
        matchExpressions:
        - key: node-lifecycle
          operator: In
          values: [on-demand]
```

### Pod Anti-Affinity for HA

```yaml
# Spread replicas: no two on same zone
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
spec:
  replicas: 6
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: my-api
              topologyKey: topology.kubernetes.io/zone # one per zone
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: my-api
                topologyKey: kubernetes.io/hostname # prefer different nodes within zone
```

### TopologySpreadConstraint (Better Alternative)

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1 # max imbalance across zones
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: my-api
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: ScheduleAnyway # soft constraint
      labelSelector:
        matchLabels:
          app: my-api
```

### Pod Affinity (Co-locate)

```yaml
# Co-locate cache pods with app pods (latency optimization)
affinity:
  podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: main-service
          topologyKey: kubernetes.io/hostname # same node preferred
```

---

## 🔄 E2E Flow: Scheduler with Anti-Affinity

```
kubectl apply -f deployment.yaml (6 replicas, anti-affinity on zone)
Scheduler places replica 1:
  → All 3 zones empty → place in zone A → zone A count = 1

Scheduler places replica 2:
  → Zone A has label-matching pod → required anti-affinity violated
  → Zone B empty → place in zone B → zone B count = 1

Scheduler places replica 3:
  → Zone A: 1 pod, Zone B: 1 pod, Zone C: 0 pods
  → Zone A/B violate required anti-affinity (one same-label pod exists)
  → Zone C: 0 matching pods → no violation → place in zone C

Scheduler places replica 4-6:
  → All zones have 1 pod → required constraint impossible for zone-based!
  → If required: replicas 4-6 stay PENDING
  → If preferred: scheduler places best-effort → some zones get 2

Fix: use preferred for zone spreading OR use TopologySpreadConstraint with maxSkew=2
```

---

## ⚖️ Comparison Table

|                    | nodeSelector   | nodeAffinity      | podAntiAffinity | TopologySpreadConstraint |
| ------------------ | -------------- | ----------------- | --------------- | ------------------------ |
| **Target**         | Node labels    | Node labels       | Other pods      | Other pods               |
| **Expressiveness** | Low (AND only) | High (OR, ranges) | High            | Medium                   |
| **Hard/Soft**      | Hard only      | Both              | Both            | Both                     |
| **Spreading**      | ❌             | ❌                | ✅              | ✅ (better)              |
| **Performance**    | O(1)           | O(rules)          | O(pods×rules)   | O(pods×rules)            |

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                          |
| -------------------------------------------- | -------------------------------------------------------------------------------- |
| "Required anti-affinity always works"        | With more replicas than topology domains, some pods stay Pending                 |
| "Affinity evicts running pods"               | `IgnoredDuringExecution` means running pods not re-evaluated                     |
| "nodeSelector and nodeAffinity are the same" | nodeSelector is AND-only, equality-only; nodeAffinity supports OR, ranges, NotIn |
| "Pod affinity is free"                       | O(pods × rules) at scale; can cause scheduler slowness in large clusters         |

---

## 🚨 Failure Modes

| Failure                          | Symptom                                                                                 | Fix                                                           |
| -------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Too strict anti-affinity         | Pods Pending: "0/3 nodes are available: 3 node(s) didn't match pod anti-affinity rules" | Use preferred or TopologySpreadConstraint with ScheduleAnyway |
| Missing topology labels on nodes | Anti-affinity doesn't work                                                              | Ensure nodes have topology.kubernetes.io/zone labels          |
| Pod affinity deadlock            | Pod A needs to be with Pod B, Pod B needs to be with Pod A, no node has both            | Use preferred affinity; avoid circular dependencies           |
| Wrong topologyKey                | All pods pile up on one node                                                            | Check topologyKey is actually on your nodes                   |

---

## 🔗 Related Keywords

- [Taints and Tolerations](/kubernetes/taints-and-tolerations/) — complementary scheduling mechanism (repel pods from nodes)
- [Scheduler (K8s)](/kubernetes/scheduler-k8s/) — executes affinity rules
- [Node](/kubernetes/node/) — labeled for affinity targeting
- [Pod Disruption Budget](/kubernetes/pod-disruption-budget/) — protects against simultaneous eviction

---

## 📌 Quick Reference Card

```bash
# Label nodes with AZ and instance type
kubectl label node worker-1 topology.kubernetes.io/zone=us-east-1a
kubectl label node worker-1 node.kubernetes.io/instance-type=m5.large

# Check node labels
kubectl get nodes --show-labels

# Debug scheduling
kubectl describe pod my-pod | grep -A 20 "Events"
# Look for: "didn't match pod affinity/anti-affinity"

# Check pod placement
kubectl get pods -o wide   # shows NODE column

# Operators (In, NotIn, Exists, DoesNotExist, Gt, Lt)
# In: key in [v1, v2]
# NotIn: key not in [v1, v2]
# Exists: key exists (any value)
# DoesNotExist: key absent
# Gt/Lt: numeric comparison
```

---

## 🧠 Think About This

`TopologySpreadConstraint` was introduced specifically because pod anti-affinity has scaling problems: with anti-affinity on hostname, you can't have more replicas than nodes (pods stay Pending). TopologySpreadConstraint's `maxSkew` is more nuanced: "allow at most 1 extra replica compared to the least-loaded zone." This means you can run 10 replicas across 3 zones (4/3/3 distribution, maxSkew=1) where strict anti-affinity would only allow 3 replicas (one per zone). For new deployments, prefer TopologySpreadConstraint over pod anti-affinity for spreading.
