---
layout: default
title: "Cluster"
parent: "Kubernetes"
nav_order: 9
permalink: /kubernetes/cluster/
id: K8S-009
category: "Kubernetes"
difficulty: "★☆☆"
depends_on: ["Kubernetes Architecture", "Node"]
used_by: ["Namespace (K8s)", "Deployment", "Service (K8s)"]
related:
  [
    "Node",
    "Namespace (K8s)",
    "etcd",
    "K8s Multi-Cluster",
    "K8s Upgrade Strategy",
  ]
tags: [kubernetes, cluster, k8s, control-plane, worker-nodes]
---

# Cluster

## ⚡ TL;DR

A Kubernetes **cluster** = one control plane + N worker nodes. It's the top-level isolation boundary. Everything (Pods, Services, ConfigMaps) lives within a cluster. Multi-tenancy within a cluster uses Namespaces; full isolation requires multiple clusters.

---

## 🔥 Problem This Solves

You need a managed pool of compute resources with scheduling, networking, and orchestration. A cluster provides that unified environment, abstracting away individual machines.

---

## 📘 Textbook Definition

A Kubernetes cluster consists of a set of worker machines (nodes) that run containerized workloads. Every cluster has at least one worker node and one control plane. The control plane manages the cluster's state; nodes run the actual workloads.

---

## ⏱️ 30 Seconds

```
Cluster = Control Plane + Worker Nodes

Control Plane (usually 1 or 3 nodes):
  kube-apiserver, etcd, kube-scheduler,
  kube-controller-manager

Worker Nodes (N):
  kubelet, kube-proxy, container runtime

Minimum for HA: 3 control plane nodes (etcd quorum)
Typical prod: 3 control plane + 3-N workers
```

---

## 🔩 First Principles

- A cluster is the **unit of Kubernetes deployment** — one cluster per environment is common
- All resources in a cluster share the same API Server, etcd, and network CIDR
- Namespaces provide logical partitioning within a cluster
- Multiple clusters are needed for strong isolation (prod vs dev, compliance boundaries)

---

## 🧪 Thought Experiment

Should you run prod and dev in the same cluster with namespaces? Probably not for strict isolation: a misconfigured ClusterRole could expose prod secrets to dev workloads. Separate clusters provide hard blast-radius boundaries at the cost of more operational overhead.

---

## 🧠 Mental Model / Analogy

A cluster is like a **data center building**: it has infrastructure (power/networking = control plane) and many servers (worker nodes). Tenants (teams) get floors (Namespaces) within the building — but the building itself is shared infrastructure.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: A cluster is the entire Kubernetes environment — it's what you get when you run `kubectl cluster-info`.

**Level 2 — Practitioner**: Clusters have a version (1.28, 1.29, etc.). You access them via kubeconfig contexts. `kubectl config use-context <cluster>` switches between clusters.

**Level 3 — Advanced**: HA clusters need 3+ control plane nodes for etcd quorum. Pod network CIDRs and Service CIDRs are cluster-scoped. Cluster CA issues all TLS certificates.

**Level 4 — Expert**: Federation (KubeFed) and multi-cluster tools (Admiralty, Liqo, fleet/Argo CD ApplicationSets) manage multiple clusters. Cluster fleet management via tools like Cluster API provisions clusters declaratively.

---

## ⚙️ How It Works

### Cluster Components Summary

```
┌─────────────────── CLUSTER ──────────────────────┐
│                                                    │
│  ┌── Control Plane ──────────────────────────┐   │
│  │  API Server  │  etcd  │  Scheduler  │  CM │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  ┌── Node 1 ─────┐  ┌── Node 2 ─────┐  ...      │
│  │ kubelet        │  │ kubelet        │           │
│  │ kube-proxy     │  │ kube-proxy     │           │
│  │ containerd     │  │ containerd     │           │
│  │ [Pod] [Pod]   │  │ [Pod] [Pod]   │           │
│  └────────────────┘  └────────────────┘           │
└────────────────────────────────────────────────────┘
```

### kubeconfig Context

```yaml
contexts:
  - name: prod-cluster
    context:
      cluster: prod
      user: admin
      namespace: default
  - name: dev-cluster
    context:
      cluster: dev
      user: admin
```

---

## 🔄 E2E Flow: Creating a Cluster (kubeadm)

```
kubeadm init (on control plane node)
  → Generates cluster CA, certificates
  → Starts API Server, etcd, Scheduler, Controller Manager
  → Creates kubeconfig for admin access
  → Outputs join command

kubeadm join <control-plane>:6443 (on worker nodes)
  → Worker node bootstraps TLS client cert
  → kubelet registers as Node with API Server

Install CNI (e.g., Calico)
  → Pod networking enabled
  → CoreDNS Pods start
  → Cluster ready
```

---

## ⚖️ Comparison Table

|                          | Single Cluster              | Multi-Cluster               |
| ------------------------ | --------------------------- | --------------------------- |
| **Isolation**            | Namespace-level only        | Hard boundary per cluster   |
| **Ops overhead**         | Low                         | High (N clusters to manage) |
| **Failure blast radius** | Entire org if misconfigured | Limited to one cluster      |
| **Cost**                 | Lower                       | Higher (N control planes)   |
| **Compliance**           | Harder                      | Easier (dedicated clusters) |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                            |
| ------------------------------------ | ------------------------------------------------------------------ |
| "Namespaces = full isolation"        | ClusterRoles can span namespaces; secrets can leak                 |
| "One cluster is fine for everything" | Prod needs dedicated cluster for blast radius and compliance       |
| "Cluster upgrade is simple"          | Upgrade control plane first, then nodes; requires careful planning |
| "etcd backup is optional"            | Without etcd backup, losing control plane = losing entire cluster  |

---

## 🚨 Failure Modes

| Failure                      | Impact                      | Mitigation                                      |
| ---------------------------- | --------------------------- | ----------------------------------------------- |
| etcd quorum loss             | Cluster writes fail         | 3-5 etcd members; regular backups               |
| All control plane nodes down | No scheduling or changes    | HA control plane + LB                           |
| Cluster CA key compromised   | All TLS certs untrustworthy | Rotate cluster CA (complex)                     |
| CIDR exhaustion              | No IP for new Pods          | Size pod-network-cidr appropriately at creation |

---

## 🔗 Related Keywords

- [Node](/kubernetes/node/) — compute members of cluster
- [Namespace (K8s)](/kubernetes/namespace-k8s/) — logical partitions within cluster
- [etcd](/kubernetes/etcd/) — cluster state store
- [K8s Multi-Cluster](/kubernetes/k8s-multi-cluster/) — federation strategies
- [K8s Upgrade Strategy](/kubernetes/k8s-upgrade-strategy/) — version upgrades

---

## 📌 Quick Reference Card

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl get componentstatuses  # (deprecated in 1.19+)

# Switch clusters (kubeconfig contexts)
kubectl config get-contexts
kubectl config use-context <name>

# Cluster version
kubectl version

# etcd backup (critical!)
ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

---

## 🧠 Think About This

How many clusters does your organization need? One per environment (dev/staging/prod) is a common starting point, but large orgs may have clusters per team, per region, or per compliance zone. The tradeoff is always control-plane cost and operational complexity vs isolation and blast-radius reduction. Platform engineering teams often use Cluster API to manage fleets of clusters declaratively.
