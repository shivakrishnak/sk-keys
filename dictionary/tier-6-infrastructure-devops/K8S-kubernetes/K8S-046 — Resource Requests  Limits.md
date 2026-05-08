---
layout: default
title: "Resource Requests  Limits"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /kubernetes/resource-requests-limits/
id: K8S-046
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Node", "Scheduler (K8s)"]
used_by:
  [
    "HPA (Horizontal Pod Autoscaler)",
    "VPA (Vertical Pod Autoscaler)",
    "QoS Classes",
    "Cluster Autoscaler",
  ]
related:
  [
    "QoS Classes",
    "HPA (Horizontal Pod Autoscaler)",
    "VPA (Vertical Pod Autoscaler)",
    "Scheduler (K8s)",
  ]
tags: [kubernetes, resources, requests, limits, cpu, memory, k8s]
---

# Resource Requests / Limits

## ⚡ TL;DR

**Requests** = minimum guaranteed resources for scheduling (CPU/memory); the scheduler places Pods where `allocatable - sum(requests) >= Pod request`. **Limits** = maximum resource consumption; exceeding CPU limit causes throttling, exceeding memory limit causes OOMKill.

---

## 🔥 Problem This Solves

Without resource specifications, Pods compete for CPU/memory, noisy neighbors starve others, schedulers can't make intelligent placement decisions, and HPA/VPA have no baseline to scale from. Requests/Limits provide resource governance and guaranteed QoS.

---

## 📘 Textbook Definition

Resource requests specify the minimum resources guaranteed to a container (used by the scheduler for placement). Resource limits specify the maximum resources a container can use. CPU is compressible (throttled at limit); memory is incompressible (OOMKilled at limit).

---

## ⏱️ 30 Seconds

```yaml
containers:
  - name: app
    resources:
      requests:
        cpu: 250m # 0.25 cores guaranteed
        memory: 256Mi # 256 MiB guaranteed
      limits:
        cpu: 500m # max 0.5 cores (throttled if exceeded)
        memory: 512Mi # max 512 MiB (OOMKilled if exceeded)
```

---

## 🔩 First Principles

- `1 CPU` = 1 vCPU/core; `1000m` = 1 core; `250m` = 0.25 core
- Memory: `Mi` = mebibytes (1 MiB = 1048576 bytes); `Gi` = gibibytes
- **Requests**: used by Scheduler for node selection; cgroups set `cpu.shares`; memory soft limit
- **Limits**: enforced by cgroups; CPU throttled (SIGSTOP) at limit; memory OOMKilled (SIGKILL) at limit
- Setting limits = limits.cpu only: CPU throttled; memory is `requests.memory` = limit
- Setting no requests: Pod gets `BestEffort` QoS — first killed under pressure

---

## 🧪 Thought Experiment

Node has 2 CPU cores. Pod A has `requests.cpu: 1`. Pod B has `requests.cpu: 1`. Scheduler places both. Total requests = 2 CPU (100% allocated). Pod C wants `requests.cpu: 0.5` — scheduler sees 0 free capacity, places on different node (or Cluster Autoscaler adds a node). Now at runtime: Pod A uses 0.3 CPU, Pod B uses 0.2 CPU. Actual usage = 0.5 CPU total, but scheduled capacity is full — this is intentional over-provisioning.

---

## 🧠 Mental Model / Analogy

Requests are like **hotel room reservations**: the hotel guarantees you a room even if you don't use all the amenities. Limits are like **credit card limits**: you can't spend more, and trying to do so gets rejected. The hotel (node) accepts bookings until full (requests = allocatable) even if actual guests use less (utilization < requests).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: `requests` = what Kubernetes promises the Pod; `limits` = maximum the Pod can use.

**Level 2 — Practitioner**: Requests → scheduler placement. Limits → cgroup enforcement. CPU limit: throttled (slow but running). Memory limit: OOMKilled (crash). Set memory request = limit for predictable behavior (Guaranteed QoS).

**Level 3 — Advanced**: `LimitRange`: default requests/limits per namespace. `ResourceQuota`: total requests/limits cap per namespace. CPU throttling causes latency spikes even if app is not CPU-bound (CFS scheduler). Memory request vs limit gap = burstable QoS — risky under node pressure.

**Level 4 — Expert**: CPU CFS quota: `cpu.cfs_quota_us` / `cpu.cfs_period_us`. 100m CPU = 10ms per 100ms period. Throttling happens at period boundaries — causes tail latency even at < 50% average utilization. Solution: avoid CPU limits for latency-sensitive apps, rely on requests only. Memory: `memory.limit_in_bytes` in cgroups. OOM score: higher when more memory used relative to request. VPA recommends right-sized requests based on actual usage. Pod-level requests/limits = sum of containers.

---

## ⚙️ How It Works

### CPU Behavior

```
Request (cpu.shares):
  Node has 4 CPU = 4000 shares
  Pod A requests 500m = 500 shares
  Pod B requests 1000m = 1000 shares

  When both contend for CPU:
  Pod A gets: 500/1500 = 33% of available
  Pod B gets: 1000/1500 = 67% of available
  → requests act as minimum proportion, not absolute

Limit (cpu.cfs_quota_us):
  cpu: 500m = 50ms per 100ms period
  If app tries to use 100ms in a 100ms window:
  → throttled for remaining 50ms
  → perceived as slowness, not crash
```

### Memory Behavior

```
Request (memory soft limit):
  Used for scheduling, not enforced at runtime
  Affects OOM score (more memory relative to request = higher OOM score)

Limit (memory.limit_in_bytes):
  Hard enforcement: exceeded → SIGKILL (OOMKill)
  Visible in: kubectl describe pod → "OOMKilled"

  kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}'
  → OOMKilled
```

### LimitRange (Namespace Defaults)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: my-app
spec:
  limits:
    - type: Container
      default: # used as limit if no limit set
        cpu: 500m
        memory: 512Mi
      defaultRequest: # used as request if no request set
        cpu: 100m
        memory: 128Mi
      max: # max allowed limit
        cpu: "2"
        memory: 2Gi
      min: # min allowed request
        cpu: 50m
        memory: 64Mi
```

### ResourceQuota (Namespace Cap)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: my-app
spec:
  hard:
    requests.cpu: "4" # total requests in namespace
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20" # max pods
```

---

## 🔄 E2E Flow: Resource Scheduling

```
kubectl apply -f pod.yaml (requests: cpu=250m, memory=256Mi)
  → Scheduler:
      - Filter: find nodes with allocatable-sum(requests) >= 250m CPU + 256Mi mem
      - Score: pick best (most available resources, or least-waste)
      - Bind: assign pod to node

  → Node:
      - kubelet creates cgroups with cpu.shares, memory.limit_in_bytes
      - Container runtime starts containers with cgroup constraints

  At runtime (CPU throttle scenario):
      - App spikes to 600m CPU (limit = 500m)
      - CFS throttles: app gets 500m out of every 100ms period
      - Response time increases; no crash

  At runtime (OOM scenario):
      - App allocates memory up to 512Mi (limit)
      - Next malloc fails → OOM killer in kernel
      - Container killed with SIGKILL
      - kubectl: "OOMKilled", restarts (CrashLoopBackOff if repeated)
```

---

## ⚖️ Comparison Table

|                  | No Requests/Limits | Requests Only | Requests + Limits          |
| ---------------- | ------------------ | ------------- | -------------------------- |
| **QoS**          | BestEffort         | Burstable     | Guaranteed (if req=limits) |
| **Scheduling**   | Uncontrolled       | Correct       | Correct                    |
| **OOM priority** | Killed first       | Medium        | Killed last                |
| **CPU throttle** | None               | None          | Yes (at limit)             |
| **HPA works**    | ❌                 | ✅            | ✅                         |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                   |
| --------------------------------------- | ----------------------------------------------------------------------------------------- |
| "CPU limits prevent performance issues" | CPU throttling can cause latency even under 50% avg utilization (CFS period issue)        |
| "Requests = actual usage"               | Requests are scheduler hints; actual usage varies; check Metrics Server                   |
| "Setting no limits is dangerous"        | On a dedicated node, fine; on shared cluster with ResourceQuota, other pods are protected |
| "Memory limits = swap"                  | Kubernetes typically disables swap; memory limit = OOMKill, not swap                      |

---

## 🚨 Failure Modes

| Failure                | Symptom                               | Fix                                                   |
| ---------------------- | ------------------------------------- | ----------------------------------------------------- |
| OOMKilled in loop      | CrashLoopBackOff; `reason: OOMKilled` | Increase memory limit; fix memory leak                |
| Pending pods           | `Insufficient cpu` or `memory`        | Add nodes or reduce requests                          |
| CPU throttling latency | High p99 latency at low CPU usage     | Remove CPU limits or increase them significantly      |
| No requests set + HPA  | HPA shows `<unknown>/50%`             | Set CPU/memory requests for HPA target metric to work |

---

## 🔗 Related Keywords

- [QoS Classes](/kubernetes/qos-classes/) — determined by requests/limits ratio
- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) — scales based on requests utilization
- [VPA (Vertical Pod Autoscaler)](/kubernetes/vpa-vertical-pod-autoscaler/) — right-sizes requests
- [Scheduler (K8s)](/kubernetes/scheduler-k8s/) — uses requests for placement

---

## 📌 Quick Reference Card

```bash
# Check actual resource usage
kubectl top pods -n my-app
kubectl top nodes

# Check requests/limits
kubectl get pods -n my-app -o custom-columns=\
  "NAME:.metadata.name,CPU_REQ:.spec.containers[0].resources.requests.cpu,\
  MEM_REQ:.spec.containers[0].resources.requests.memory,\
  CPU_LIM:.spec.containers[0].resources.limits.cpu,\
  MEM_LIM:.spec.containers[0].resources.limits.memory"

# Check why pod OOMKilled
kubectl describe pod my-pod | grep -A 5 "Last State"

# Check ResourceQuota usage
kubectl describe resourcequota -n my-app

# Units
# CPU: 1 = 1000m = 1 core; 250m = 0.25 core
# Memory: 1Mi = 1048576 bytes; 1Gi = 1073741824 bytes
```

---

## 🧠 Think About This

The CPU throttling problem is one of Kubernetes' most misunderstood performance issues. The Linux CFS scheduler throttles CPU in 100ms periods. A container with `limits.cpu: 500m` gets 50ms of CPU per 100ms period. If your app happens to need 60ms in one burst, it gets throttled to 50ms — creating 10ms of wasted pause time. This manifests as p99 latency spikes even when average CPU utilization is low. The Netflix/Shopify recommendation: **don't set CPU limits** in production workloads; only set CPU requests, and use ResourceQuota to cap namespace totals. Monitor actual usage with `kubectl top` and VPA recommendations.
