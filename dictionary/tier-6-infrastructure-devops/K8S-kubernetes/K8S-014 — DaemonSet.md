---
layout: default
title: "DaemonSet"
parent: "Kubernetes"
nav_order: 14
permalink: /kubernetes/daemonset/
id: K8S-014
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Node", "Deployment"]
used_by:
  ["Kubernetes Observability", "Calico / Cilium", "Kubernetes Networking (CNI)"]
related:
  [
    "Deployment",
    "StatefulSet",
    "Node",
    "Taints and Tolerations",
    "Node Affinity / Anti-Affinity",
  ]
tags: [kubernetes, daemonset, node-agent, monitoring, logging, k8s]
---

# DaemonSet

## ⚡ TL;DR

A DaemonSet ensures **one Pod runs on every node** (or a subset). When nodes join the cluster, DaemonSet Pods are automatically added. Use for: log collection agents, monitoring agents, network plugins (CNI), and node-level security tools.

---

## 🔥 Problem This Solves

Infrastructure agents (Fluentd, Datadog Agent, Calico node daemon, etc.) need to run on every node exactly once. Managing this manually is error-prone. DaemonSet automates "one pod per node" as nodes scale in/out.

---

## 📘 Textbook Definition

A DaemonSet ensures that all (or some) Nodes run a copy of a Pod. As nodes are added to the cluster, Pods are added to them. As nodes are removed from the cluster, those Pods are garbage collected.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          effect: NoSchedule
      containers:
        - name: fluentd
          image: fluentd:v1.16
          volumeMounts:
            - name: varlog
              mountPath: /var/log
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
```

---

## 🔩 First Principles

- DaemonSet bypasses the Scheduler — it places Pods directly on nodes via `nodeName`
- New node joins cluster → DaemonSet controller immediately creates a Pod on it
- Node removed → DaemonSet Pod is garbage collected
- By default runs on ALL nodes; use `nodeSelector` or `nodeAffinity` to target a subset
- Needs `tolerations` to run on control-plane nodes (which have `NoSchedule` taint)

---

## 🧪 Thought Experiment

Your monitoring agent needs to read `/proc` and node-level metrics. It must run on every node, including new ones that join via autoscaling. A Deployment with `replicas=N` breaks when nodes scale — you'd constantly update the replica count. A DaemonSet handles this automatically, always ensuring exactly one per node.

---

## 🧠 Mental Model / Analogy

A DaemonSet is like a **health inspector assigned to every restaurant**: when a new restaurant opens (node joins), an inspector is automatically assigned to it. When a restaurant closes (node removed), the inspector moves on. The manager doesn't assign inspectors manually.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: DaemonSet = one Pod per node. Use it for things that every node needs: logs, metrics, network.

**Level 2 — Practitioner**: DaemonSet respects `nodeSelector` and `nodeAffinity` to run on specific node pools (e.g., only GPU nodes). Needs tolerations for tainted nodes.

**Level 3 — Advanced**: DaemonSet Pods are scheduled directly by the DaemonSet controller (bypasses kube-scheduler). `updateStrategy: RollingUpdate` — one node at a time. `maxUnavailable` controls rollout speed.

**Level 4 — Expert**: DaemonSet uses `nodeName` in PodSpec to bypass scheduler. Critical system DaemonSets (kube-proxy, CNI) use `priorityClass: system-node-critical` to prevent eviction. Preemption: system critical DaemonSets preempt lower-priority Pods on resource-starved nodes.

---

## ⚙️ How It Works

### DaemonSet vs Deployment Scheduling

```
Deployment → kube-scheduler assigns nodes
DaemonSet  → DaemonSet controller sets nodeName directly
             (bypasses scheduler completely)
```

### Node Targeting

```yaml
# Only GPU nodes
spec:
  template:
    spec:
      nodeSelector:
        hardware: gpu
```

### Rolling Update

```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1 # update 1 node at a time
```

### Common DaemonSets in Every Cluster

| DaemonSet                        | Purpose                         |
| -------------------------------- | ------------------------------- |
| kube-proxy                       | Service routing (iptables/IPVS) |
| CNI plugin (Calico/Cilium node)  | Pod networking                  |
| fluentd/filebeat                 | Log collection                  |
| Datadog/Prometheus node-exporter | Node metrics                    |
| gVisor/kata-containers           | Container security sandbox      |

---

## 🔄 E2E Flow: Log Collection

```
Fluentd DaemonSet deployed
  → One Fluentd Pod per node (mounts /var/log via hostPath)
  → Node-2 autoscales into cluster
  → DaemonSet controller detects: Node-2 has no Fluentd Pod
  → Creates Fluentd Pod on Node-2 with nodeName=Node-2
  → Fluentd reads /var/log on Node-2
  → Streams logs to Elasticsearch
```

---

## ⚖️ Comparison Table

|                | DaemonSet                               | Deployment         | StatefulSet              |
| -------------- | --------------------------------------- | ------------------ | ------------------------ |
| **Count**      | 1 per node                              | N total            | N with stable identity   |
| **Scheduling** | DaemonSet controller (bypass scheduler) | kube-scheduler     | kube-scheduler (ordered) |
| **Use case**   | Node agents                             | Stateless services | Stateful services        |
| **Scaling**    | Auto with nodes                         | Manual/HPA         | Manual                   |

---

## ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| "DaemonSet uses the scheduler"                 | DaemonSet controller sets `nodeName` directly, bypassing scheduler     |
| "DaemonSet always runs on all nodes"           | `nodeSelector` / `affinity` can restrict to a subset                   |
| "DaemonSet runs on control plane by default"   | Control plane nodes have `NoSchedule` taint; add toleration explicitly |
| "DaemonSet and Deployment are interchangeable" | DaemonSet is specifically for per-node infrastructure agents           |

---

## 🚨 Failure Modes

| Failure                    | Symptom                                | Fix                                                             |
| -------------------------- | -------------------------------------- | --------------------------------------------------------------- |
| Missing toleration         | DaemonSet not on tainted nodes         | Add toleration for control-plane/custom taints                  |
| hostPath permission denied | Container can't read node files        | Set `securityContext.privileged: true` or adjust hostPath perms |
| Too many log agents        | Duplicate logs in aggregator           | Ensure one DaemonSet, not multiple overlapping ones             |
| DaemonSet Pod evicted      | Agent missing on resource-starved node | Set `priorityClass: system-node-critical`                       |

---

## 🔗 Related Keywords

- [Deployment](/kubernetes/deployment/) — stateless workloads
- [StatefulSet](/kubernetes/statefulset/) — stateful workloads
- [Taints and Tolerations](/kubernetes/taints-and-tolerations/) — control which nodes get DaemonSet Pods
- [Kubernetes Networking (CNI)](/kubernetes/kubernetes-networking-cni/) — CNI plugins run as DaemonSets

---

## 📌 Quick Reference Card

```bash
# Get DaemonSets
kubectl get daemonsets -A

# Describe DaemonSet
kubectl describe ds fluentd

# Check which nodes have DaemonSet Pods
kubectl get pods -l app=fluentd -o wide

# Update DaemonSet (rolling update)
kubectl rollout status ds/fluentd
kubectl rollout history ds/fluentd
kubectl rollout undo ds/fluentd
```

---

## 🧠 Think About This

Why does kube-proxy run as a DaemonSet rather than a Deployment? Because Service routing must work on **every node** — if a node lacks kube-proxy, Pods on that node can't reach Kubernetes Services. The "1 per node" guarantee is fundamental to cluster networking correctness, not just a convenience. This is the canonical use case DaemonSets were designed for.
