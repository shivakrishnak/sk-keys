---
layout: default
title: "QoS Classes"
parent: "Kubernetes"
nav_order: 42
permalink: /kubernetes/qos-classes/
number: "K8S-042"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Resource Requests / Limits", "Pod", "Node"]
used_by: ["K8s Security Hardening", "K8s Cost Optimization"]
related:
  [
    "Resource Requests / Limits",
    "VPA (Vertical Pod Autoscaler)",
    "Cluster Autoscaler",
  ]
tags: [kubernetes, qos, quality-of-service, oom, eviction, k8s]
---

# QoS Classes

## ⚡ TL;DR

Kubernetes assigns each Pod a **Quality of Service (QoS) class** based on its resource requests/limits. Three classes: `Guaranteed` (req=limits), `Burstable` (req set, req≠limits), `BestEffort` (no req/limits). QoS determines eviction priority under node memory pressure: BestEffort evicted first, Guaranteed last.

---

## 🔥 Problem This Solves

When a node runs out of memory, Kubernetes must evict (kill) Pods. Which Pods should be killed first? QoS classes provide the answer: kill workloads with no resource guarantees (BestEffort) before mission-critical guaranteed workloads.

---

## 📘 Textbook Definition

QoS classes in Kubernetes categorize Pods based on their resource specifications to guide the scheduler and kubelet in making resource allocation and eviction decisions. They determine the order of Pod eviction when nodes experience resource pressure.

---

## ⏱️ 30 Seconds

```yaml
# Guaranteed: requests == limits (for ALL containers)
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 500m           # must equal request
    memory: 512Mi       # must equal request

# Burstable: requests set but < limits (or only limits set)
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m           # higher than request
    memory: 512Mi

# BestEffort: no requests, no limits
resources: {}
```

---

## 🔩 First Principles

- QoS is **auto-assigned** based on resource spec — you can't set it manually
- QoS is Pod-level: ALL containers in a Pod determine the class (weakest container wins)
- `Guaranteed`: all containers must have both cpu AND memory request AND limit, AND req==limit
- `BestEffort`: all containers have NO resource specifications
- `Burstable`: everything else
- QoS affects: eviction order, OOM score (Linux OOM killer priority), cgroup priority

---

## 🧪 Thought Experiment

Node has 8 GiB RAM. Allocated: 3 GiB Guaranteed Pods (critical services), 3 GiB Burstable Pods (most app Pods), 1 GiB BestEffort (batch jobs). Memory spike happens. kubelet sees memory pressure. Eviction order: first kill BestEffort batch jobs → then Burstable Pods exceeding requests → Guaranteed Pods never evicted unless node is truly OOM. Critical services stay alive through memory spikes.

---

## 🧠 Mental Model / Analogy

QoS classes are like **flight boarding priority**: Guaranteed passengers = Business class (board first, guaranteed overhead bin space, last to be bumped). Burstable = Economy Plus (has a seat but overhead bin may be full). BestEffort = Standby (may not get on the flight at all if the plane is full).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Kubernetes decides pod eviction priority based on whether you set resource requests/limits. BestEffort pods are killed first.

**Level 2 — Practitioner**: Guaranteed = request equals limit. Burstable = partial spec. BestEffort = no spec. Use Guaranteed for databases and critical services; BestEffort only for batch jobs that can restart.

**Level 3 — Advanced**: OOM score: cgroup `oom_score_adj`. BestEffort: 1000 (highest priority for OOM kill). Guaranteed: -998 (lowest priority = protected). Burstable: between 2-999 based on memory usage proportion. `kubelet --eviction-hard` thresholds trigger pod eviction before OOM.

**Level 4 — Expert**: Eviction API: `kubelet` first tries soft eviction (over eviction-soft threshold → graceful). Then hard eviction (immediate). BestEffort → Burstable-over-limit → Burstable-under-limit → Guaranteed (only if node OOM). `MemoryQoS` (cgroups v2): new fine-grained memory throttling via `memory.high`. With cgroups v2, Kubernetes can throttle memory (page reclaim) before OOMKill, improving stability.

---

## ⚙️ How It Works

### QoS Determination Logic

```
For each container in Pod:
  - Has CPU request? Has CPU limit?
  - Has memory request? Has memory limit?
  - Are requests == limits?

Pod is Guaranteed if:
  - EVERY container has cpu request, cpu limit, memory request, memory limit
  - AND for every container: cpu request == cpu limit AND memory request == memory limit
  - Init containers also must meet criteria

Pod is BestEffort if:
  - NO container has ANY resource specification

Pod is Burstable otherwise:
  - At least one container has a request or limit
  - But not all containers have request==limit
```

### Check Pod QoS Class

```bash
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'
# Output: Guaranteed / Burstable / BestEffort
```

### OOM Score (Linux Kernel)

```
BestEffort:   oom_score_adj = 1000   → killed first by kernel OOM
Burstable:    oom_score_adj = 2-999  → proportional to memory usage vs request
Guaranteed:   oom_score_adj = -998   → protected from OOM kill
```

### Eviction Sequence on Memory Pressure

```
Memory pressure event:
1. kubelet eviction manager detects:
   - memoryAvailable < 100Mi (eviction-hard threshold)
2. Eviction order:
   a. BestEffort pods (any)
   b. Burstable pods exceeding their memory request
   c. Burstable pods within their memory request (fewest)
   d. Guaranteed pods (only on actual node OOM, last resort)
3. Pod evicted = graceful termination + moved to pending state
4. If node pressure not resolved, next pod evicted
```

---

## 🔄 E2E Flow: Memory Pressure Eviction

```
Node: 8Gi total, 7.9Gi used
kubelet: memoryAvailable = 100Mi < eviction-hard threshold (100Mi)

BestEffort Pods:
  - batch-job-1 (no resources spec) → evicted immediately
  - batch-job-2 (no resources spec) → evicted immediately

Still pressure? Yes.

Burstable Pods (over request):
  - cache-pod (request 256Mi, using 400Mi) → evicted (over limit)

Still pressure? No → eviction stops.

Guaranteed Pods (critical-service, request=limit 512Mi): SAFE
```

---

## ⚖️ Comparison Table

|                           | BestEffort | Burstable        | Guaranteed             |
| ------------------------- | ---------- | ---------------- | ---------------------- |
| **Resource spec**         | None       | Partial          | req = limits           |
| **Eviction priority**     | First      | Middle           | Last                   |
| **OOM kill priority**     | Highest    | Medium           | Lowest                 |
| **Scheduling guarantees** | None       | Based on request | Full                   |
| **Use case**              | Batch, dev | Most apps        | Critical services, DBs |
| **cgroup cpu.shares**     | 2 (min)    | Based on request | Based on request       |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                     |
| ------------------------------------ | ----------------------------------------------------------- |
| "Setting limits = Guaranteed QoS"    | Only if limits == requests; limit > request = Burstable     |
| "BestEffort means lower performance" | Performance depends on actual resource usage, not QoS class |
| "Guaranteed pods are never evicted"  | Evicted only when node is truly OOM (no other options)      |
| "QoS applies per container"          | QoS is per Pod; weakest container determines the Pod class  |

---

## 🚨 Failure Modes

| Failure                          | Symptom                                            | Fix                                                              |
| -------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| Critical service as BestEffort   | Service killed first during memory spikes          | Set requests = limits (Guaranteed)                               |
| All pods Guaranteed              | Cluster overprovisioned, expensive                 | Use Burstable for apps that can tolerate some memory flexibility |
| OOMKill loop                     | CrashLoopBackOff with OOMKilled                    | Increase memory limit; fix memory leak; check QoS class          |
| Init container breaks Guaranteed | Init container has different req/limit → Burstable | Set req=limit on init containers too                             |

---

## 🔗 Related Keywords

- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) — determines QoS class
- [VPA (Vertical Pod Autoscaler)](/kubernetes/vpa-vertical-pod-autoscaler/) — recommends right-sized requests
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) — uses QoS to protect pods during scale-down

---

## 📌 Quick Reference Card

```bash
# Check QoS class of pod
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'

# List all pods with QoS class
kubectl get pods -A -o custom-columns=\
  "NAME:.metadata.name,NS:.metadata.namespace,QOS:.status.qosClass"

# Check eviction thresholds
kubectl describe node | grep -A 10 "Conditions"

# See eviction events
kubectl get events --field-selector reason=Evicted -A

# OOM events
kubectl describe pod my-pod | grep -A 5 "OOMKilled"

# Node memory pressure
kubectl describe node | grep MemoryPressure
```

---

## 🧠 Think About This

The Guaranteed QoS class has a hidden cost: setting `requests == limits` means you're reserving resources on the node that the pod may not always use. A pod requesting 4Gi memory will block 4Gi of node allocatable memory even when using 1Gi. This reduces cluster bin-packing efficiency. Production clusters typically use:

- Guaranteed for stateful, latency-critical services (databases, caches)
- Burstable for stateless apps (can handle occasional eviction with graceful restart)
- BestEffort only for genuinely disposable batch jobs that checkpoint progress

Use VPA to right-size requests over time — this is more impactful for cluster efficiency than any other single optimization.
