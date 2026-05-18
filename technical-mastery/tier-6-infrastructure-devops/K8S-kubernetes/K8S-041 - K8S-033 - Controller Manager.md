---
version: 1
layout: default
title: "Controller Manager"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/kubernetes/controller-manager/
id: K8S-041
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Architecture", "API Server", "etcd"]
used_by: ["Deployment", "ReplicaSet", "StatefulSet", "DaemonSet", "Node"]
related:
  [
    "Kubernetes Architecture",
    "API Server",
    "Operators",
    "CRD (Custom Resource Definition)",
  ]
tags:
  [
    kubernetes,
    controller-manager,
    controllers,
    reconciliation,
    k8s,
    control-loop,
  ]
---

## ⚡ TL;DR

The `kube-controller-manager` runs all built-in **controllers** - reconciliation loops that watch Kubernetes state and drive it toward desired state. Examples: Deployment Controller (ensures N replicas), Node Controller (marks failed nodes NotReady), ReplicaSet Controller (creates/deletes Pods).

---

## 🔥 Problem This Solves

Kubernetes is declarative - you say "3 replicas" and something must ensure 3 replicas exist at all times. Controllers are those somethings: they continuously watch and reconcile actual vs desired state without human intervention.

---

## 📘 Textbook Definition

The Controller Manager is a control plane component that runs controller processes. Each controller is a separate goroutine watching the cluster state via the API Server and making changes to drive actual state toward desired state.

---

## ⏱️ 30 Seconds

```
Controllers bundled in kube-controller-manager:
  - Deployment Controller
  - ReplicaSet Controller
  - StatefulSet Controller
  - DaemonSet Controller
  - Job Controller
  - Node Controller        ← marks nodes NotReady
  - Endpoints Controller   ← manages Service endpoints
  - Namespace Controller   ← handles namespace lifecycle
  - ServiceAccount Controller
  - PersistentVolume Controller
  - ... (30+ controllers)

Each follows: Watch → Compare → Act → Repeat
```

---

## 🔩 First Principles

- **Reconcile loop**: observe state, compare with desired, take action to converge
- **Level-triggered** (not edge-triggered): if action fails, retry until state matches
- **Eventually consistent**: doesn't guarantee instant convergence, but will converge
- Controllers communicate only via API Server (never peer-to-peer)
- Controller Manager uses **leader election** - one active instance, others in standby

---

## 🧪 Thought Experiment

You delete a Pod managed by a ReplicaSet (replicas=3). The ReplicaSet Controller is watching Pod events. It sees actual count (2) < desired count (3). It calls `POST /api/v1/pods` to create a new Pod. If the API Server is temporarily unavailable, the controller retries with backoff until it succeeds. It doesn't give up - it reconciles until state matches.

---

## 🧠 Mental Model / Analogy

Controller Manager is like a **building supervisor** running multiple inspectors simultaneously. Inspector A checks if all apartments (Pods) are occupied (ReplicaSet Controller). Inspector B checks if all tenants have working heat (Node Controller). Each inspector walks the same floors (watches API Server), notes discrepancies, and fixes them (creates/deletes resources).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Controller Manager keeps things running. Deployment deleted a Pod? Controller creates a new one.

**Level 2 - Practitioner**: Each controller = watch API for relevant resources + reconcile loop. ReplicaSet Controller: count Pods matching selector, create/delete to match `spec.replicas`.

**Level 3 - Advanced**: Leader election: `--leader-elect=true` uses Lease objects. Only one controller-manager runs active controllers; others are hot standby. Shared informer cache: all controllers share a reflector/cache to reduce API Server load.

**Level 4 - Expert**: Controller pattern: `Work queue` + `Reconcile(key string) error`. Rate-limited work queue prevents reconcile storms. `Informer.AddEventHandler` registers for resource events. `lister-gen` generates type-safe listers backed by in-memory cache. Custom controllers follow the same pattern via controller-runtime (Kubebuilder).

---

## ⚙️ How It Works

---

### Generic Controller Pattern

```go
// Every controller follows this pattern:
func (r *ReconcileDeployment) Reconcile(ctx context.Context,
    req Request) (Result, error) {
    // Get current state
    deployment := &appsv1.Deployment{}
    r.Get(ctx, req.NamespacedName, deployment)

    // Get desired state
    desired := deployment.Spec.Replicas

    // Get actual state
    actual := len(getMatchingPods(deployment))

    // Reconcile
    if actual < desired:
        createPods(desired - actual)
    if actual > desired:
        deletePods(actual - desired)

    return Result{}, nil
}
```

---

### Node Controller

```
Node heartbeat timeout (default 40s):
  → Node condition: Unknown

After node-monitor-grace-period (40s):
  → Node condition: NotReady

After pod-eviction-timeout (5min default):
  → Pods on that node → Terminating
  → New Pods scheduled on healthy nodes
```

---

### Endpoints Controller

```
Service selector change / Pod readiness change
  → Endpoints Controller:
      Find Pods matching Service selector
      Filter: only Ready Pods (readinessProbe passing)
      Update Endpoints object
  → kube-proxy watches Endpoints → updates iptables
```

---

## 🔄 E2E Flow: Node Failure Recovery

```
Node-3 network failure at T=0
  → kubelet stops sending heartbeats

T=0 + 40s (node-monitor-grace-period):
  → Node Controller: Node-3 status → Unknown

T=0 + 5min (pod-eviction-timeout):
  → Node Controller: Pods on Node-3 → Terminating
  → ReplicaSet Controllers: actual < desired
  → Create replacement Pods on healthy nodes
  → Endpoints Controller: remove Node-3 Pods from endpoints
  → New Pods pass readiness → added to endpoints
```

---

## ⚖️ Comparison Table

|                       | kube-controller-manager | cloud-controller-manager | Custom Controller (Operator) |
| --------------------- | ----------------------- | ------------------------ | ---------------------------- |
| **Built in**          | Yes                     | Yes (cloud-specific)     | No (you write it)            |
| **Resources managed** | Core K8s resources      | Cloud LBs, nodes, routes | Custom CRDs                  |
| **Language**          | Go (compiled in)        | Go (compiled in)         | Any (controller-runtime)     |
| **Examples**          | Deployment, ReplicaSet  | AWS LB provisioning      | ArgoCD, cert-manager         |

---

## ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                 |
| ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| "One controller per resource type"             | Multiple controllers may watch same resources (e.g., Deployment and RS both watch Pods) |
| "Controllers run in a single thread"           | Each controller runs in its own goroutine; all run concurrently                         |
| "Controller Manager failure = cluster failure" | Existing Pods keep running; only reconciliation stops                                   |
| "Reconcile happens only on change"             | Periodic re-sync also triggers reconcile (full resync every 10-30min)                   |

---

## 🚨 Failure Modes

| Failure                 | Symptom                           | Fix                                     |
| ----------------------- | --------------------------------- | --------------------------------------- |
| Controller Manager down | Desired state drift not corrected | HA: leader election with 2 replicas     |
| Controller tight loop   | API Server throttled; CPU spike   | Add rate limiting; fix controller logic |
| Work queue backup       | Delayed reconciliation            | Monitor controller queue depth metrics  |
| Leader election failure | No active controller              | Check RBAC for lease objects access     |

---

## 🔗 Related Keywords

- [Kubernetes Architecture](/kubernetes/kubernetes-architecture/) - controller manager in context
- [API Server](/kubernetes/api-server/) - all controllers go through here
- [Operators](/kubernetes/operators/) - custom controllers for complex apps
- [CRD (Custom Resource Definition)](/kubernetes/crd-custom-resource-definition/) - custom resources for custom controllers
- [Deployment](/kubernetes/deployment/) - managed by Deployment Controller

---

## 📌 Quick Reference Card

```bash
# Check controller manager pod
kubectl get pods -n kube-system -l component=kube-controller-manager

# Controller manager logs
kubectl logs -n kube-system kube-controller-manager-<name>

# Leader election status (Lease object)
kubectl get lease kube-controller-manager -n kube-system -o yaml

# Controller manager metrics (on control plane)
curl -k https://localhost:10257/metrics | grep workqueue

# Key flags:
# --node-monitor-period=5s
# --node-monitor-grace-period=40s
# --pod-eviction-timeout=5m0s
# --leader-elect=true
```

---

## 🧠 Think About This

The reconcile loop is the heart of Kubernetes' self-healing behavior. It's why Kubernetes is described as a "control system" rather than a scripting system. Instead of "when X happens, do Y," Kubernetes controllers say "ensure the world looks like Z." This model handles all failure modes automatically: transient network failures, API Server restarts, etcd hiccups - the controller just retries until it succeeds. This idempotent, level-triggered approach is the key insight behind Kubernetes' reliability.
