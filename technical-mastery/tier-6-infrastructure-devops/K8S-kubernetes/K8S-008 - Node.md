---
version: 1
layout: default
title: "Node"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/kubernetes/node/
id: K8S-008
category: "Kubernetes"
difficulty: "★☆☆"
depends_on: ["Kubernetes Architecture"]
used_by: ["Pod", "Cluster", "kubelet", "kube-proxy"]
related:
  [
    "Cluster",
    "kubelet",
    "Node Affinity / Anti-Affinity",
    "Taints and Tolerations",
    "Resource Requests / Limits",
  ]
tags: [kubernetes, node, worker-node, k8s, compute]
---

## ⚡ TL;DR

A **Node** is a physical or virtual machine in a Kubernetes cluster that runs Pods. Each node has a kubelet (communicates with API Server), kube-proxy (networking), and a container runtime (containerd).

---

## 🔥 Problem This Solves

Kubernetes needs compute capacity to schedule and run containers. Nodes provide that capacity - CPU, memory, storage - and the infrastructure to manage containers on those machines.

---

## 📘 Textbook Definition

A Node is a worker machine in Kubernetes, either virtual or physical, that hosts Pods. The control plane manages nodes; nodes run workloads. Each node is managed by the control plane and contains the services necessary to run Pods.

---

## ⏱️ 30 Seconds

```
Node Components:
  kubelet          → talks to API Server, manages Pod
    lifecycle
  kube-proxy       → network routing rules (iptables/IPVS)
  container runtime → containerd/CRI-O (actually runs
    containers)

Node Status:
  Ready     → healthy, can accept Pods
  NotReady  → not accepting new Pods
  Unknown   → node unreachable (network partition)

Node Info:
  kubectl get nodes
  kubectl describe node <name>
```

---

## 🔩 First Principles

- Nodes are compute workers - they run Pods and nothing else (ideally)
- Control plane nodes should have `NoSchedule` taints to prevent workloads landing there
- The kubelet is the node agent - it pulls PodSpecs from API Server and runs them
- Nodes can be labeled and tainted to control which Pods land on them

---

## 🧪 Thought Experiment

If you add a new node to the cluster, what happens? The kubelet registers itself with the API Server. The Scheduler becomes aware of the new node's capacity. Pending Pods waiting for available resources can now be scheduled. No manual action needed - the control loop handles it.

---

## 🧠 Mental Model / Analogy

Nodes are like **slots in a server rack**: each has CPU/RAM capacity. The Scheduler is the ops engineer who decides which server gets which workload based on available resources and requirements.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: A Node is a machine (VM or physical) where Kubernetes runs your apps.

**Level 2 - Practitioner**: Nodes have CPU, memory, and ephemeral storage capacity. The Scheduler places Pods on nodes with sufficient capacity. Node status is `Ready`/`NotReady`/`Unknown`.

**Level 3 - Advanced**: Node labels enable `nodeSelector` and `nodeAffinity` scheduling rules. Taints prevent Pods without matching tolerations from scheduling on a node. Resource pressure (memory/disk/PID) triggers eviction.

**Level 4 - Expert**: Node heartbeats via `NodeLease` objects in `kube-node-lease` namespace (lease renewal = heartbeat). `node-monitor-grace-period` (default 40s) before NotReady. `node-monitor-period` = 5s. Cluster Autoscaler adds/removes nodes based on pending Pods.

---

## ⚙️ How It Works

---

### Node Components

```
kubelet:
  - Watches API Server for PodSpecs assigned to this node
  - Uses CRI to start/stop containers
  - Reports node and Pod status back to API Server
  - Runs probes (liveness, readiness, startup)

kube-proxy:
  - Programs iptables/IPVS rules for Service VIPs
  - Enables Pod-to-Service communication

Container runtime (containerd):
  - OCI-compliant runtime
  - Pulls images, creates containers
  - Managed by kubelet via CRI interface
```

---

### Node Conditions

| Condition            | Meaning               |
| -------------------- | --------------------- |
| `Ready`              | Node is healthy       |
| `MemoryPressure`     | Low memory            |
| `DiskPressure`       | Low disk              |
| `PIDPressure`        | Too many processes    |
| `NetworkUnavailable` | No network configured |

---

### Node Capacity vs Allocatable

```
Capacity:    Total physical resources
Allocatable: Capacity - system-reserved - kube-reserved
             Pods can only use Allocatable resources
```

---

## 🔄 E2E Flow: Node Joins Cluster

```
New VM provisioned
  → kubeadm join (or cloud-init script)
  → kubelet starts with --kubeconfig pointing to API Server
  → kubelet sends CSR to API Server (TLS bootstrapping)
  → API Server approves CSR, issues certificate
  → kubelet registers Node object in API Server
  → Scheduler sees new node with capacity
  → Pending Pods can now be scheduled on new node
```

---

## ⚖️ Comparison Table

|                    | Control Plane Node                              | Worker Node             |
| ------------------ | ----------------------------------------------- | ----------------------- |
| **Runs**           | API Server, etcd, Scheduler, Controller Manager | Workload Pods           |
| **Scheduling**     | Tainted `NoSchedule` (usually)                  | Accepts workloads       |
| **HA requirement** | Multiple (3 or 5)                               | Multiple for redundancy |
| **Managed by**     | Cloud provider or kubeadm                       | kubelet + cloud-init    |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                     |
| --------------------------------------- | --------------------------------------------------------------------------- |
| "Nodes are managed objects"             | Nodes register themselves; Kubernetes reflects their status                 |
| "Deleting a node object deletes the VM" | Deleting the Node object just removes it from scheduling; the VM still runs |
| "All nodes are equal"                   | Node pools with labels/taints allow specialized node types                  |
| "NotReady means Pods are gone"          | Pods stay in Terminating for `pod-eviction-timeout` before rescheduling     |

---

## 🚨 Failure Modes

| Failure            | Impact                                | Mitigation                            |
| ------------------ | ------------------------------------- | ------------------------------------- |
| Node goes NotReady | Pods rescheduled after timeout        | PodDisruptionBudgets; anti-affinity   |
| OOM on node        | Pods evicted by priority              | Set resource requests; QoS Guaranteed |
| Disk pressure      | Eviction of BestEffort/Burstable Pods | Monitor disk; clean up images         |
| Network partition  | Node appears Unknown                  | Separate data/management networks     |

---

## 🔗 Related Keywords

- [Kubernetes Architecture](/kubernetes/kubernetes-architecture/) - control plane vs nodes
- [kubelet](/kubernetes/kubelet/) - node agent
- [Taints and Tolerations](/kubernetes/taints-and-tolerations/) - restrict scheduling
- [Node Affinity / Anti-Affinity](/kubernetes/node-affinity-anti-affinity/) - prefer/require nodes
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) - automatic node scaling

---

## 📌 Quick Reference Card

```bash
# List nodes
kubectl get nodes -o wide

# Node details (capacity, allocatable, conditions)
kubectl describe node <name>

# Label a node
kubectl label node <name> disktype=ssd

# Taint a node (prevent scheduling)
kubectl taint node <name> key=value:NoSchedule

# Drain (safely evict Pods)
kubectl drain <name> --ignore-daemonsets --delete-emptydir-data

# Uncordon (re-enable scheduling)
kubectl uncordon <name>
```

---

## 🧠 Think About This

Why does Kubernetes wait before rescheduling Pods from a `NotReady` node? Because a transient network issue would cause a cascade of Pod deletions and recreations. The grace period (`pod-eviction-timeout`, default 5 min) gives the node a chance to recover. In cloud environments with fast replacement VMs, tuning this down makes sense.
