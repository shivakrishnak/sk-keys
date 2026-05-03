---
layout: default
title: "Container Resource Limits"
parent: "Containers"
nav_order: 844
permalink: /containers/container-resource-limits/
number: "0844"
category: Containers
difficulty: ★★☆
depends_on: Container, Cgroups, Linux Namespaces, Docker, Kubernetes Architecture
used_by: Kubernetes Architecture, QoS Classes, HPA, Container Health Check
related: Cgroups, QoS Classes, Resource Requests / Limits, Container Orchestration, Container Health Check
tags:
  - containers
  - kubernetes
  - performance
  - intermediate
  - production
---

# 844 — Container Resource Limits

⚡ TL;DR — Container resource limits cap the CPU and memory a container can consume, preventing noisy neighbours from starving other containers on the same node.

| #844 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Container, Cgroups, Linux Namespaces, Docker, Kubernetes Architecture | |
| **Used by:** | Kubernetes Architecture, QoS Classes, HPA, Container Health Check | |
| **Related:** | Cgroups, QoS Classes, Resource Requests / Limits, Container Orchestration, Container Health Check | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You run 30 containers on a single node with 16 CPU cores and 32GB RAM. One container — a batch job someone deployed at 3 PM on a Friday — starts consuming 14 of the 16 CPU cores and 28GB of RAM. All other 29 containers are starved: response times spike, health checks fail, Kubernetes restarts pods in an attempt to recover. The production API is down because someone's uncontrolled batch job ate all the resources. Without resource limits, container isolation is namespace-level only; resource usage is wide open.

**THE BREAKING POINT:**
Sharing a node among multiple containers without resource governance means any single container can consume all available resources and starve everyone else. This is the "noisy neighbour" problem — a shared infrastructure concern with direct production impact.

**THE INVENTION MOMENT:**
This is exactly why container resource limits exist — backed by Linux cgroups, they put hard caps on how much CPU and memory any container can consume, ensuring fair sharing and preventing any single container from degrading the entire node.

---

### 📘 Textbook Definition

**Container resource limits** (and requests) are specifications on a container that instruct the container runtime and Kubernetes scheduler how to allocate and cap CPU and memory usage. **Requests** are the minimum guaranteed allocation: used by the Kubernetes scheduler for pod placement. **Limits** are the maximum allowed consumption: enforced by the kernel's cgroup subsystem. If a container exceeds its memory limit, the kernel OOM-killer terminates it (OOMKilled). If a container exceeds its CPU limit, it is throttled (CPU cycles are rate-limited) but not killed. In Kubernetes, these are set in the pod spec as `resources.requests` and `resources.limits` per container.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Resource limits are the CPU and memory "lease" for each container — the request reserves capacity, the limit prevents overconsumption.

**One analogy:**
> A co-working space has 100 desks. If anyone can bring any amount of equipment without reservation, one person could set up 50 monitors and take up half the floor. Resource limits are like the desk booking system: you reserve a desk (request), and you're allowed to use at most one desk and four monitors (limit). The booking ensures you have guaranteed space. The limit ensures you don't take everyone else's.

**One insight:**
Requests and limits serve two different systems. Requests inform the **scheduler** (which node can fit this container?). Limits instruct the **kernel cgroup** (at the node level, cap this process). You can set them independently: low request (fits easily on a node) with high limit (can burst if resources are free) — or set them equal for fully predictable resource usage (Guaranteed QoS class).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Memory is incompressible — exceeding a memory limit kills the process (no graceful degradation).
2. CPU is compressible — exceeding a CPU limit throttles the process (slows down, doesn't kill).
3. Requests are scheduling hints; limits are enforceable kernel contracts.

**DERIVED DESIGN:**

**CPU units:**
- `1` = 1 core = 1000m (millicores)
- `100m` = 100 millicores = 10% of one CPU core
- CPU throttling: the kernel's CFS (Completely Fair Scheduler) uses `cpu.cfs_quota_us` and `cpu.cfs_period_us` cgroup parameters to throttle containers to their CPU limit.

**Memory units:**
- `Mi` (mebibytes), `Gi` (gibibytes)
- Memory enforcement: `memory.limit_in_bytes` cgroup parameter. When exceeded, the OOM killer terminates the container process.

**Request vs Limit:**
```
┌──────────────────────────────────────────────────────────┐
│        Request vs Limit — Two Systems                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Request (scheduling):                                   │
│    scheduler: node.allocatable >= pod.requests?          │
│    → reserves this capacity on the node                  │
│    → guarantees this resource is available               │
│                                                          │
│  Limit (enforcement):                                    │
│    cgroup: process uses > limit? → throttle / OOMKill    │
│    → caps consumption at runtime                         │
│                                                          │
│  Key: node.allocatable is based on requests, not limits  │
│  → multiple containers can have limit > request          │
│     (overcommit) — works until actual usage hits limits  │
└──────────────────────────────────────────────────────────┘
```

**QoS Classes (Kubernetes):**
- `Guaranteed`: requests == limits for all containers → highest priority, never evicted under memory pressure
- `Burstable`: limits > requests (or only requests set) → can burst, evicted under pressure
- `BestEffort`: no requests or limits set → lowest priority, first to be evicted

**THE TRADE-OFFS:**

**Gain:** Predictable resource consumption, fair sharing, prevention of noisy neighbours, OOM event isolation.

**Cost:** Incorrect limits cause OOMKills (too-low memory limit) or CPU throttling (too-low CPU limit). Over-provisioned limits waste capacity. Finding correct values requires profiling under production load.

---

### 🧪 Thought Experiment

**SETUP:**
A Java Spring Boot API sets `memory limit: 256Mi`. Under load, the JVM heap grows to 300MB during a memory-intensive request.

**WHAT HAPPENS WITHOUT CORRECT MEMORY LIMITS:**
With no limit, the JVM heap grows unboundedly. A memory leak or large request payload could cause the JVM to consume all 32GB of node RAM, OOMKilling every other container on the node. Production outage.

**WHAT HAPPENS WITH TOO-LOW MEMORY LIMIT (256Mi):**
The JVM tries to allocate the 300MB heap. The kernel's OOM killer fires. The container process receives SIGKILL. The container is restarted. `kubectl describe pod` shows: `OOMKilled`. This will keep happening under load — the limit is set below the application's actual memory requirement.

**WHAT HAPPENS WITH CORRECTLY PROFILED LIMITS (600Mi):**
The 300MB heap fits within the 600Mi limit. The container runs normally under load. Other containers on the node are protected from this container consuming more than 600Mi. The limit correctly reflects the application's actual maximum memory need.

**THE INSIGHT:**
Resource limits are not "set once, forget." They must be set based on profiled actual usage (P99 plus safety margin), not guessed or left at defaults. Incorrect limits cause hard failures.

---

### 🧠 Mental Model / Analogy

> CPU and memory limits are like the guaranteed and maximum data plans on a mobile phone. Your "request" is like a guaranteed minimum plan — the carrier reserves this bandwidth for you. Your "limit" is like the maximum data cap — the carrier throttles (CPU) or cuts off (memory/OOM) your connection when you try to exceed it. On a congested network (busy node), your guarantee is protected even when others are bursting. But if you consistently need more than your guarantee, you'll always hit the throttle.

Mapping:
- "Guaranteed minimum plan" → resource request (scheduler reserves this)
- "Maximum data cap" → resource limit (cgroup enforces this)
- "Throttled when exceeding the cap (CPU)" → CPU throttling via CFS
- "Completely cut off (memory)" → OOMKilled when exceeding memory limit
- "Others on the network" → other containers on the same node

Where this analogy breaks down: mobile plans are shared over a network; container resources are local to a node. Memory OOMKill is immediate (SIGKILL); mobile cutoffs are often gradual (speed reduction before full stop).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Resource limits tell the container how much CPU power and memory it can use. Without them, one container could use all the computer's resources and starve everything else. Limits are like per-apartment utility caps — you can't use more than your allocation.

**Level 2 — How to use it (junior developer):**
Set `resources.requests` and `resources.limits` in your pod spec. Start with: profile your app at peak load. Set request to the average usage; set limit to the P99 usage plus 20% buffer. For Java: memory limit must account for JVM metaspace, thread stacks, and off-heap buffers in addition to heap. For CPU: be generous with limits — CPU throttling is silent and hard to diagnose.

**Level 3 — How it works (mid-level engineer):**
Memory limits map directly to the `memory.limit_in_bytes` cgroup v1 (or `memory.max` in cgroup v2) parameter. When a container process tries to allocate memory and the cgroup limit is reached, the kernel's OOM killer selects the process to kill (typically the container's PID 1). The `oom_score_adj` is set higher for containers to ensure they are selected over host processes. CPU limits use the CFS bandwidth controller: `cpu.cfs_quota_us = limit_cpu * cpu.cfs_period_us`. If the container uses its full CPU quota in a period, it is throttled for the remainder of the period. CPU throttling is invisible to the application — it just runs slower.

**Level 4 — Why it was designed this way (senior/staff):**
The asymmetric treatment of CPU (compressible, throttling) vs memory (incompressible, OOMKill) reflects fundamental hardware reality: CPUs can be multiplexed in time; memory cannot. A process running at 50% speed is degraded but alive. A process with no memory to allocate have no recourse — it must be killed. This is why Kubernetes QoS policy treats memory pressure more aggressively than CPU pressure: eviction under memory pressure happens sooner and with higher priority than under CPU pressure. The "requests as scheduling hints, limits as enforcement" model is a deliberate overcommit design — nodes can have containers with cumulative limits exceeding node capacity, trading best-case packing efficiency against worst-case OOM risk. Production systems should set requests = limits (Guaranteed QoS) for critical workloads to eliminate this risk.

---

### ⚙️ How It Works (Mechanism)

**cgroup hierarchy for a Kubernetes pod:**
```
┌──────────────────────────────────────────────────────────┐
│        cgroup hierarchy (cgroup v2)                      │
├──────────────────────────────────────────────────────────┤
│  /sys/fs/cgroup/                                         │
│  └── kubepods/                                           │
│      └── pod<uid>/                                       │
│          ├── memory.max = 512Mi  ← pod total memory cap  │
│          └── <container-id>/                             │
│              ├── memory.max = 256Mi  ← container limit   │
│              ├── cpu.max = 25000 100000  ← 250m CPU      │
│              │   (cpu.max = quota period                  │
│              │    25000/100000 = 25% of 1 CPU)            │
│              └── pids.max = 100  ← max process count     │
└──────────────────────────────────────────────────────────┘
```

**CPU throttling mechanism:**
- Period: 100ms window (`cpu.cfs_period_us = 100000`)
- Quota: e.g., `cpu.cfs_quota_us = 50000` = 50ms of CPU per 100ms window = 0.5 CPU
- If container uses 50ms of CPU within the 100ms window, it is throttled for the remaining 50ms
- Throttled time is measurable: `container_cpu_cfs_throttled_seconds_total` in Prometheus

**Memory limit enforcement:**
- `memory.max = 268435456` (256Mi in bytes)
- On allocation exceeding limit: kernel activates OOM killer
- OOM killer selects process with highest `oom_score`
- Container processes have elevated `oom_score_adj` to be selected before host processes
- Result: container receives SIGKILL → container restarts per restart policy

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
kubectl apply deployment.yaml (requests: 250m/256Mi, limits: 500m/512Mi)
  → scheduler: finds node with 250m CPU + 256Mi RAM allocatable
  → kubelet: creates cgroup with cpu.max 500m, memory.max 512Mi
  → containerd: starts container in that cgroup ← YOU ARE HERE
  → container runs within limits
  → HPA watches CPU: if avg > 70%, scale out replicas
```

**FAILURE PATH:**
```
Container exceeds memory limit:
  → kernel OOM killer: SIGKILL container process
  → containerd: reports container exit (OOMKilled)
  → kubelet: restarts container per restartPolicy
  → kubectl describe pod: "OOMKilled", exit code 137
  → persistent OOMKills: CrashLoopBackOff
  → fix: increase memory limit or fix memory leak
```

**WHAT CHANGES AT SCALE:**
At 10,000 pods on 500 nodes, resource accounting becomes critical. Nodes with low resources need alerting before they reach capacity. Kubernetes Resource Quotas at the namespace level cap total resource consumption per team. Vertical Pod Autoscaler (VPA) can automatically right-size resource requests based on observed usage — avoiding both over-provisioning (waste) and under-provisioning (OOMKills).

---

### 💻 Code Example

**Example 1 — Setting requests and limits:**
```yaml
containers:
- name: my-app
  image: myapp:1.0.0
  resources:
    requests:
      cpu: "250m"      # scheduler reserves 250 millicores
      memory: "256Mi"  # scheduler reserves 256 mebibytes
    limits:
      cpu: "500m"      # kernel throttles at 500 millicores
      memory: "512Mi"  # kernel OOMKills at 512 mebibytes
```

**Example 2 — Guaranteed QoS (requests == limits):**
```yaml
# For critical services: requests = limits = Guaranteed QoS
# Never evicted under memory pressure
containers:
- name: critical-api
  resources:
    requests:
      cpu: "1"        # 1 full core
      memory: "1Gi"
    limits:
      cpu: "1"        # same as request → Guaranteed QoS
      memory: "1Gi"
```

**Example 3 — Detect CPU throttling:**
```bash
# Check if container is being CPU throttled
kubectl top pod <pod-name> --containers

# Prometheus query for CPU throttling rate
rate(container_cpu_cfs_throttled_seconds_total{
  container="my-app",
  namespace="production"
}[5m])

# Node-level cgroup check (on the node)
cat /sys/fs/cgroup/kubepods/pod<uid>/<container-id>/cpu.stat
# Look for: throttled_usec / nr_throttled
```

**Example 4 — Namespace-level resource quota:**
```yaml
# Enforce total resource limits per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "20"       # max 20 CPU cores requested
    requests.memory: "40Gi"  # max 40Gi memory requested
    limits.cpu: "40"
    limits.memory: "80Gi"
```

---

### ⚖️ Comparison Table

| QoS Class | When Assigned | Eviction Priority | Best For |
|---|---|---|---|
| **Guaranteed** | requests == limits (all containers) | Last evicted | Critical production services |
| Burstable | requests < limits, or only requests | Medium priority | Normal services with variable load |
| BestEffort | No requests or limits | First evicted | Non-critical batch jobs |

How to choose: Guaranteed for stateful services, databases, and anything that cannot tolerate unexpected restarts. Burstable for typical microservices — burst when needed, evict gracefully under pressure. BestEffort only for truly non-critical batch work where restarts are acceptable.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "CPU limits prevent containers from using more than N cores" | CPU limits throttle — they rate-limit CPU usage over time, not hard-cap instantaneous usage. A container can burst above the limit briefly; the kernel averages it over the CFS period. |
| "If I set no memory limit, the container will never crash" | Without a memory limit, the container can consume all available node memory, causing the node itself to become unstable and the kubelet to OOMKill multiple pods unpredictably. |
| "Setting limits = requests wastes resources" | For critical production workloads, the predictability and Guaranteed QoS class justify the "waste." Overcommit (limits > requests) creates risk of OOMKill cascades under load spikes. |
| "CPU throttling is harmless" | CPU throttling causes latency increases — especially harmful for latency-sensitive services. A Java GC event that normally takes 50ms may take 500ms if CPU is being throttled. |
| "Memory limit should equal the JVM heap size (-Xmx)" | No. The JVM uses memory beyond the heap: Metaspace, off-heap allocations (NIO buffers, agent overhead), stack memory per thread. Set memory limit to at least heap + 256MB for JVM applications. |

---

### 🚨 Failure Modes & Diagnosis

**OOMKilled — memory limit too low**

**Symptom:**
Pod restarts with exit code 137. `kubectl describe pod` shows `OOMKilled`. Service returns 5xx errors during restarts.

**Root Cause:**
Memory limit is set below the container's actual peak memory usage. JVM heap, off-heap, GC surge, request payload surge — any cause.

**Diagnostic Command / Tool:**
```bash
# Check OOM events
kubectl describe pod <pod> | grep -A5 "OOMKilled"

# Check memory usage over time (Prometheus)
max_over_time(
  container_memory_working_set_bytes{container="my-app"}[24h]
)

# Java-specific: check JVM memory breakdown
kubectl exec <pod> -c my-app -- jcmd 1 VM.native_memory
```

**Fix:**
Increase memory limit to P99 peak usage + 20–30% safety margin. For JVM: set `-Xmx` to ~75% of the container memory limit to leave room for off-heap.

**Prevention:**
Monitor `container_memory_working_set_bytes`. Alert at 80% of limit. Use VPA to auto-adjust requests based on observed usage.

---

**CPU throttling — invisible latency degradation**

**Symptom:**
API p99 latency spikes during peak traffic. CPU metrics show container using < limit. No OOMKills. No crashes.

**Root Cause:**
Container's CPU limit is too low. During CPU-intensive operations (GC, request spike), the container exhausts its CFS quota and is throttled — requests queue up, latency increases.

**Diagnostic Command / Tool:**
```bash
# Check throttling metrics
kubectl exec -it <node-debug-pod> -- \
  cat /sys/fs/cgroup/kubepods/pod<uid>/<ctr-id>/cpu.stat

# Prometheus query
sum(rate(container_cpu_cfs_throttled_seconds_total[5m]))
  by (container, namespace)
```

**Fix:**
Increase CPU limit. For Guaranteed QoS critical paths, set limit equal to the core count the application actually needs.

**Prevention:**
Monitor CPU throttling metrics proactively. Any throttling > 5% is a signal to investigate. Alert rather than discover during incidents.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Cgroups` — the Linux kernel mechanism that enforces resource limits; essential to understand how limits work
- `Container` — resource limits are properties of containers
- `Kubernetes Architecture` — understand how the scheduler uses resource requests for pod placement

**Builds On This (learn these next):**
- `QoS Classes` — Kubernetes eviction priority derived from requests/limits configuration
- `HPA (Horizontal Pod Autoscaler)` — scales replicas based on CPU/memory metrics relative to requests
- `Container Health Check` — health checks combined with resource limits determine pod stability

**Alternatives / Comparisons:**
- `Resource Requests / Limits` — same concept in Kubernetes context; R&L are the K8s API for this
- `Container Orchestration` — orchestrators use resource requests for scheduling decisions
- `Cgroups` — the underlying Linux implementation that makes resource limits work

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CPU/memory caps on containers enforced    │
│              │ by Linux cgroups                          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One container consuming all node          │
│ SOLVES       │ resources (noisy neighbour problem)       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Requests = scheduler input (placement).   │
│              │ Limits = kernel enforcement (runtime).    │
│              │ Two different systems, both needed.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every production container must  │
│              │ have both requests and limits set         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — no limits = no protection    │
│              │ against resource abuse                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Predictable resource use vs right-sizing  │
│              │ effort + risk of OOMKill / CPU throttle   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Requests reserve a seat; limits ensure   │
│              │  you don't take everyone else's seats"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cgroups → QoS Classes → VPA → HPA         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Java microservice is set with `memory.limit = 512Mi` and `-Xmx=512m`. Under normal load it runs fine. Under a traffic spike, it receives 1,000 concurrent requests, each building a 1MB JSON response in memory. Trace step-by-step what happens to memory usage across heap, off-heap buffers, and thread stacks, explain why the container OOMKills despite an apparently adequate heap limit, and derive the correct memory limit formula for a Java container.

**Q2.** You have a Burstable QoS pod with CPU request=100m, limit=1000m. The node has 8 available CPU cores. During a CPU spike, 50 other Burstable pods on the node also try to burst simultaneously. The node's total CPU allocation from all requests is 6 cores, but all pods collectively try to use 40+ cores. Trace the Linux CFS scheduler's behaviour: how does it arbitrate resource allocation, which pods get throttled, and how does this differ from the Guaranteed QoS pods also running on the same node?

