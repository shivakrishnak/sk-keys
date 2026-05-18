---
version: 1
layout: default
title: "Kubernetes Architecture"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/kubernetes/kubernetes-architecture/
id: K8S-006
category: "Kubernetes"
difficulty: "★☆☆"
depends_on: ["Containers", "Docker"]
used_by: ["Pod", "Deployment", "Service (K8s)"]
related:
  [
    "etcd",
    "API Server",
    "kubelet",
    "kube-proxy",
    "Scheduler (K8s)",
    "Controller Manager",
  ]
tags: [kubernetes, architecture, control-plane, data-plane, k8s]
---

## ⚡ TL;DR

Kubernetes = **control plane** (brain) + **worker nodes** (muscle). Control plane manages state via API Server + etcd + Scheduler + Controller Manager. Worker nodes run Pods via kubelet + container runtime + kube-proxy.

---

## 🔥 Problem This Solves

Running containers at scale requires scheduling, self-healing, networking, and configuration management. Manually managing hundreds of containers across machines is impossible. Kubernetes provides a declarative, self-healing platform.

---

## 📘 Textbook Definition

Kubernetes is an open-source container orchestration system. Its architecture separates **control plane** components (which manage cluster state) from **worker node** components (which run workloads).

---

## ⏱️ 30 Seconds

```
Control Plane:
  - API Server     ← single entry point for all operations
  - etcd           ← distributed key-value store (source
    of truth)
  - Scheduler      ← assigns Pods to Nodes
  - Controller Mgr ← reconciles desired vs actual state

Worker Nodes:
  - kubelet        ← talks to API Server, runs Pods
  - kube-proxy     ← maintains network rules
  - Container RT   ← containerd/CRI-O runs containers
```

---

## 🔩 First Principles

- **Desired state**: you declare what you want; controllers reconcile to match it
- **Level-triggered**: controllers react to state differences, not events
- **API-centric**: everything goes through the API Server
- **etcd is the truth**: all cluster state lives there; components read/watch it

---

## 🧪 Thought Experiment

What if a node crashes while running 3 Pods? The Node Controller detects the node is unreachable (after `node-monitor-grace-period`), marks it `NotReady`, and the Deployment controller sees replicas < desired and schedules new Pods on healthy nodes. Zero human intervention.

---

## 🧠 Mental Model / Analogy

Think of Kubernetes as a **data center OS**:

- **API Server** = system call interface
- **etcd** = kernel state
- **Scheduler** = CPU scheduler (assigns work to nodes)
- **Controller Manager** = daemon processes (constantly correcting drift)
- **kubelet** = init system on each node (like systemd, manages Pods)

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Kubernetes runs your containers across multiple machines and keeps them healthy.

**Level 2 - Practitioner**: Control plane stores desired state in etcd. Scheduler places Pods on nodes. kubelet on each node ensures containers run. kube-proxy sets up networking rules.

**Level 3 - Advanced**: API Server is stateless - etcd holds all state. Controllers use **watch + reconcile** loops. Scheduler uses predicates (filters) and priorities (scoring) to select nodes. kubelet uses the CRI to manage containers.

**Level 4 - Expert**: etcd uses Raft consensus for fault-tolerance (need quorum of `(n/2)+1` members). API Server uses request handlers, admission webhooks, and RBAC before persisting. Custom controllers can extend the reconcile loop via CRDs + Operators.

---

## ⚙️ How It Works

---

### Control Plane Components

| Component                    | Role                                                                  |
| ---------------------------- | --------------------------------------------------------------------- |
| **kube-apiserver**           | REST API gateway; validates and persists all resource changes to etcd |
| **etcd**                     | Consistent, distributed key-value store; all cluster state            |
| **kube-scheduler**           | Watches unscheduled Pods; selects optimal node                        |
| **kube-controller-manager**  | Runs built-in controllers (Node, Deployment, ReplicaSet, etc.)        |
| **cloud-controller-manager** | Manages cloud-provider resources (LBs, volumes)                       |

---

### Worker Node Components

| Component             | Role                                              |
| --------------------- | ------------------------------------------------- |
| **kubelet**           | Agent on every node; ensures Pod spec is realized |
| **kube-proxy**        | Maintains iptables/IPVS rules for Service routing |
| **Container runtime** | containerd or CRI-O; runs actual containers       |

---

## 🔄 E2E Flow: `kubectl apply -f deployment.yaml`

```
User
  └─► kubectl → HTTPS → kube-apiserver
                            ├─ Authenticate (certs/tokens)
                            ├─ Authorize (RBAC)
                            ├─ Admission webhooks
                            └─ Persist to etcd

etcd write → API Server notifies watchers
  └─► kube-scheduler watches: new unscheduled Pod
         ├─ Filter nodes (resources, taints, affinity)
         └─ Score + bind Pod to best node

  └─► kubelet on selected node watches: new Pod assigned
    to it
         ├─ Pull image (via CRI)
         ├─ Create containers
         └─ Report status back to API Server
```

---

## ⚖️ Comparison Table

|                        | Kubernetes              | Docker Swarm | Nomad    |
| ---------------------- | ----------------------- | ------------ | -------- |
| **Complexity**         | High                    | Low          | Medium   |
| **Scheduling**         | Rich (affinity, taints) | Basic        | Flexible |
| **Ecosystem**          | Massive                 | Limited      | Growing  |
| **Stateful workloads** | StatefulSet             | Limited      | Yes      |
| **Learning curve**     | Steep                   | Gentle       | Medium   |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------ |
| "etcd is just a database"           | etcd is the system of record - losing it without backup = losing the cluster   |
| "Control plane runs workloads"      | Control plane should have `NoSchedule` taints; workloads go on worker nodes    |
| "kubectl talks to kubelet directly" | kubectl always talks to API Server; never directly to kubelet                  |
| "Kubernetes manages containers"     | Kubernetes manages Pods (groups of containers); the runtime manages containers |

---

## 🚨 Failure Modes

| Failure          | Impact                                                 | Mitigation                                 |
| ---------------- | ------------------------------------------------------ | ------------------------------------------ |
| etcd quorum loss | Cluster reads ok, writes fail                          | Run 3 or 5 etcd members; backup regularly  |
| API Server down  | Cannot create/update resources; existing workloads run | HA: multiple API Server replicas behind LB |
| Scheduler down   | New Pods stay `Pending`                                | Run multiple scheduler replicas            |
| Node failure     | Pods on that node lost                                 | Pod disruption budgets; pod anti-affinity  |

---

## 🔗 Related Keywords

- [Pod](/kubernetes/pod/) - basic schedulable unit
- [etcd](/kubernetes/etcd/) - cluster state store
- [API Server](/kubernetes/api-server/) - control plane entry point
- [kubelet](/kubernetes/kubelet/) - node agent
- [Scheduler (K8s)](/kubernetes/scheduler-k8s/) - Pod placement
- [Controller Manager](/kubernetes/controller-manager/) - reconciliation loops

---

## 📌 Quick Reference Card

```
Control Plane nodes: kube-apiserver, etcd, kube-scheduler,
                     kube-controller-manager

Worker nodes:        kubelet, kube-proxy, container runtime

Default ports:
  API Server: 6443 (HTTPS)
  etcd:       2379 (client), 2380 (peer)
  kubelet:    10250

Quorum (etcd):  n=3 → tolerate 1 failure
                n=5 → tolerate 2 failures
```

---

## 🧠 Think About This

If the API Server goes down but etcd and kubelets are healthy, what happens to running Pods? They keep running - kubelet doesn't need the API Server to maintain existing Pods. Only new scheduling or changes fail. This is why Kubernetes is designed for **existing workload resilience** even during control plane hiccups.
