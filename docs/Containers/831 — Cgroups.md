---
layout: default
title: "Cgroups"
parent: "Containers"
nav_order: 831
permalink: /containers/cgroups/
number: "0831"
category: Containers
difficulty: ★★★
depends_on: Linux Namespaces, Container, Operating Systems, Linux
used_by: Container, Docker, Container Resource Limits, Container Security, containerd
related: Linux Namespaces, Container Resource Limits, Container, Container Security, Container Health Check
tags:
  - containers
  - linux
  - internals
  - advanced
  - performance
---

# 831 — Cgroups

⚡ TL;DR — Cgroups (control groups) are a Linux kernel feature that limits, measures, and isolates resource usage (CPU, memory, I/O, network) for groups of processes — the mechanism that enforces container resource boundaries.

| #831 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Linux Namespaces, Container, Operating Systems, Linux | |
| **Used by:** | Container, Docker, Container Resource Limits, Container Security, containerd | |
| **Related:** | Linux Namespaces, Container Resource Limits, Container, Container Security, Container Health Check | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Ten containers run on the same host. Container A has a memory leak and starts consuming all available RAM. The Linux OOM (out-of-memory) killer has no container concept — it kills the process with the highest memory usage. That just happens to be the database process in Container C. Container C crashes. Five other containers that depended on Container C cascade-fail. A single buggy container in Container A has taken down the entire host.

**THE BREAKING POINT:**
Linux namespaces provide isolation of *visibility* — each container sees only its own processes and network. But without resource *limits*, a single container can consume all CPU, memory, or I/O on the host, starving all other containers. Visibility isolation without resource enforcement is insufficient for multi-tenant safety.

**THE INVENTION MOMENT:**
This is exactly why cgroups were created — a kernel mechanism that puts processes into groups and enforces maximum resource consumption per group. "This container gets at most 2 CPUs and 512 MB of RAM. No more. Ever."

---

### 📘 Textbook Definition

**Cgroups (Control Groups)** are a Linux kernel feature that organises processes into hierarchical groups and enforces resource usage limits, priorities, and accounting on those groups. Cgroups manage four main resources: **CPU** (scheduling weight and hard time limits), **memory** (maximum resident set size, swap limits, OOM kill policy), **blkio/io** (block I/O rate limits), and **network** (via tc/net_cls classifiers). There are two cgroup versions: **cgroups v1** (legacy, multiple separate hierarchies per controller) and **cgroups v2** (unified hierarchy, all controllers under one tree). Docker and Kubernetes use cgroups to enforce `--memory`, `--cpus`, resource requests, and limits per container.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cgroups are the enforcement layer that prevents any one container from consuming more than its allocated share of CPU, memory, or I/O.

**One analogy:**
> Cgroups are like the resource budget system in a hotel. Each room (container) has been allocated: a maximum 500W of electricity, a maximum 10 Mbps of Wi-Fi, and a maximum 50 L/day of water. The hotel's resource management controller tracks each room's usage in real time and rate-limits or cuts off any room that exceeds its budget. Other rooms are unaffected when one room hits its limit. Cgroups are the hotel's resource management controller for processes.

**One insight:**
Cgroups and namespaces are complementary. Namespaces provide *isolation* (what you can see). Cgroups provide *enforcement* (how much you can use). A container without cgroup limits is like an isolated villa with unlimited free electricity, water, and food — still dangerous to the shared infrastructure. Both are required for safe container isolation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A cgroup is a set of processes. Any process belongs to exactly one cgroup per controller.
2. Limits on a cgroup apply to all processes in that cgroup and all their child processes.
3. Accounting is per-cgroup — the kernel tracks cumulative resource usage for each group.

**DERIVED DESIGN:**

**Cgroup v2 unified hierarchy** (modern, default on recent kernels):
```
/sys/fs/cgroup/
├── system.slice/           ← system services
│   └── docker.service/
│       └── container-abc/  ← per-container cgroup
│           ├── memory.max         = 536870912  (512 MB)
│           ├── cpu.max            = "50000 100000"  (50%)
│           └── io.max             = "8:0 rbps=10485760"
└── user.slice/             ← user processes
```

**Memory control:**
- `memory.max`: hard limit. When a container's resident memory reaches this, new allocations fail → process is OOM-killed (within the cgroup).
- `memory.swap.max`: swap limit. Setting to 0 disables swap for the container.
- `memory.high`: soft limit. When exceeded, the kernel aggressively reclaims — processes slow down, but they are not killed.

**CPU control (cgroup v2):**
- `cpu.max = 50000 100000`: container gets at most 50,000 microseconds in every 100,000-µs period = 50% of one CPU.
- `cpu.weight = 100`: relative scheduling weight (higher = more CPU time when contended).

**Memory OOM killer:** When a container exceeds `memory.max`, the kernel's OOM killer kills the process with the highest `oom_score_adj` within the container's cgroup — it does NOT kill processes outside the cgroup. This is scoped OOM killing: the container is killed, not the host.

**THE TRADE-OFFS:**
**Gain:** Resource guarantee per container; scoped OOM kills (container does not take down host); resource accounting (observability); fair CPU scheduling under contention.
**Cost:** Setting limits incorrectly causes premature OOM kills (under-limit) or allows noisy neighbours (over-limit); cgroup overhead is negligible for most workloads but significant for high-syscall-rate applications.

---

### 🧪 Thought Experiment

**SETUP:**
A host has 8 GB RAM. Two containers: Container A (application, limited 6 GB) and Container B (database, limited 4 GB) — total limit: 10 GB > physical memory. Container A has a memory leak.

**WITHOUT CGROUPS:**
Container A's leak consumes memory without limit. Once physical RAM + swap is exhausted, the kernel's global OOM killer picks the process with the highest memory usage. That might be the PostgreSQL process in Container B. Database crashes, data potentially corrupted.

**WITH CGROUPS (correct configuration):**
Container A is in its cgroup with `memory.max = 6GB`. When Container A's RSS reaches 6 GB, the kernel's OOM killer runs *inside Container A's cgroup only*. It kills the leaking process within Container A. Container B is completely unaffected — its 4 GB cgroup limit is independent. The database continues operating. The host is stable.

**THE INSIGHT:**
Cgroup-scoped OOM killing is one of the most important properties for multi-tenant container hosts. Without it, a memory leak in any container can corrupt or terminate an entirely unrelated container. With it, resource failures are contained within the cgroup boundary.

---

### 🧠 Mental Model / Analogy

> Cgroups are like electricity circuit breakers in an apartment building. Each apartment (cgroup/container) has its own circuit breaker. If an apartment overloads its circuit (exceeds memory/CPU limit), its breaker trips — only that apartment loses power. The building's main grid and all other apartments are unaffected. The maintenance team (OOM killer) resets only the tripped apartment's circuit. Without individual circuit breakers, one overloaded apartment would trip the building's main breaker and kill everyone's power.

**Mapping:**
- "Apartment building" → multi-container host
- "Each apartment's circuit" → per-container cgroup
- "Circuit breaker limit" → `memory.max`, `cpu.max` cgroup limits
- "Circuit breaker trips" → OOM killer kills process within cgroup
- "Building's main grid unaffected" → host and other containers not affected
- "Maintenance resets circuit" → container is restarted by orchestrator

**Where this analogy breaks down:** Electricity circuit breakers are binary (on/off). CPU cgroups are smoother — a container that exceeds its CPU budget is throttled (slowed down), not killed. Memory is closer to the breaker model — it triggers OOM kill when the limit is exhausted.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Cgroups give each container a resource budget — "you get at most 2 CPUs and 512 MB of RAM." If the container tries to use more, the kernel enforces the limit. This prevents one container from slowing down or crashing everything else on the same machine.

**Level 2 — How to use it (junior developer):**
In Docker: `docker run --memory=512m --cpus=0.5 myapp` — sets memory limit (512 MB hard limit), CPU limit (50% of one CPU). In Kubernetes pod spec: set `resources.limits.memory` and `resources.limits.cpu`. Kubernetes translates these into cgroup settings on the node. Check container resource usage: `docker stats` (live) or `kubectl top pods`.

**Level 3 — How it works (mid-level engineer):**
At container creation, Docker/containerd creates a directory in the cgroup filesystem (`/sys/fs/cgroup/memory/docker/<container_id>/`) and writes the limit values to the controller files (`memory.limit_in_bytes`). The kernel then tracks all memory allocations by processes in this cgroup and enforces the limit. For CPU, the `cpu.cfs_quota_us` and `cpu.cfs_period_us` files implement the Completely Fair Scheduler (CFS) bandwidth controller — the process can use `quota` microseconds in every `period` microseconds. CPU throttling: when quota is exhausted, the container's processes are descheduled until the next period.

**Level 4 — Why it was designed this way (senior/staff):**
Cgroups v1 (Google, 2006) had a fragmented design — each controller (memory, cpu, blkio) had its own hierarchy, making it hard to atomically apply limits at the same level. Cgroups v2 (2016, default in Linux 5.x) unified all controllers under a single hierarchy, making it possible to set `memory.max` and `cpu.max` for the same cgroup atomically. This resolved the "split brain" problem where v1 could have a container in different places in the memory hierarchy vs the CPU hierarchy. Kubernetes migrated to cgroup v2 as its default in 1.25 (2022). The performance impact of cgroup v2 is measurable but small for most workloads: ~5 ns overhead per allocation for memory accounting, < 0.1% CPU overhead for accounting, with significant improvement in scheduling latency variance due to the unified hierarchy design.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  CGROUP V2 FILESYSTEM                                    │
│                                                          │
│  /sys/fs/cgroup/                                         │
│  ├── system.slice/                                       │
│  │   └── docker-abc123.scope/   ← container cgroup dir  │
│  │       ├── cgroup.procs       ← PIDs in this cgroup   │
│  │       ├── memory.max         ← 536870912 (512 MB)    │
│  │       ├── memory.current     ← 134217728 (128 MB)    │
│  │       ├── cpu.max            ← "50000 100000" (50%)  │
│  │       ├── cpu.stat           ← throttled time, etc.  │
│  │       └── io.max             ← I/O rate limits       │
│                                                          │
│  MEMORY ENFORCEMENT:                                     │
│  Process malloc() → kernel tracks per-cgroup RSS        │
│  RSS > memory.max → OOM kill (inside cgroup only)       │
│                                                          │
│  CPU ENFORCEMENT (CFS bandwidth):                        │
│  quota=50000µs per 100000µs period = 50% of 1 CPU       │
│  Quota exhausted → process THROTTLED until next period  │
│  Quota renewed → process eligible for scheduling        │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
docker run --memory=512m --cpus=0.5 myapp
→ containerd creates cgroup directory
→ [CGROUP CONFIGURED ← YOU ARE HERE]
→ memory.max = 512MB, cpu.max = 50000/100000
→ container process PID written to cgroup.procs
→ all memory allocations tracked by cgroup
→ container runs within limits
```

**FAILURE PATH:**
```
Container memory exceeds 512MB
→ kernel OOM killer fires within cgroup
→ kills highest oom_score process in cgroup
→ container restarts (via Kubernetes restart policy)
→ observable: OOMKilled exit code + docker inspect OOMKilled=true
```

**WHAT CHANGES AT SCALE:**
At 500 containers per host, 500 cgroup directories are created and tracked. The kernel's cgroup memory accounting overhead is linear with the number of cgroup-tracked memory pages. High container density with strict memory limits can cause frequent OOM kills if limits are set too tight — containers should have limits set at 1.5–2× their typical memory usage to absorb spikes.

---

### 💻 Code Example

Example 1 — Set resource limits with Docker:
```bash
# 512MB RAM, 0.5 CPU (50% of one core), swap disabled
docker run -d \
  --name my-app \
  --memory="512m" \
  --memory-swap="512m"  `# swap same as memory = no swap` \
  --cpus="0.5" \
  --cpu-shares=512 \    `# relative weight for CPU contention` \
  myapp:1.0

# Check live resource usage
docker stats my-app --no-stream

# Verify cgroup settings applied
cat /sys/fs/cgroup/memory/docker/$(docker inspect -f '{{.Id}}' my-app)/memory.limit_in_bytes
```

Example 2 — Kubernetes resource requests and limits:
```yaml
resources:
  requests:         # Kubernetes scheduler uses this for placement
    memory: "256Mi" # minimum guaranteed memory
    cpu: "250m"     # 250 millicores = 0.25 CPU
  limits:           # cgroup hard limits on the node
    memory: "512Mi" # OOMKilled if exceeded
    cpu: "500m"     # throttled if exceeded
```
```bash
# View actual cgroup settings for a Kubernetes pod
kubectl describe pod myapp | grep -A5 "Limits:"
kubectl top pods  # live CPU/memory usage
```

Example 3 — Read cgroup metrics directly:
```bash
# Get the container's cgroup path
CGROUP=$(cat /proc/$(docker inspect -f '{{.State.Pid}}' my-app)/cgroup \
         | grep memory | awk -F: '{print $3}')

# Read memory stats
cat /sys/fs/cgroup/memory/$CGROUP/memory.stat
# Shows: cache, rss, swap, pgfault, etc.

# Check CPU throttling
cat /sys/fs/cgroup/cpu/$CGROUP/cpu.stat
# throttled_usec: time processes were throttled
```

---

### ⚖️ Comparison Table

| Resource | Controller | Enforcement Mechanism | Kubernetes Field |
|---|---|---|---|
| Memory | `memory.max` | OOM kill at limit | `resources.limits.memory` |
| CPU (hard) | `cpu.max` (v2) / `cfs_quota` | CFS throttle | `resources.limits.cpu` |
| CPU (soft) | `cpu.weight` | Scheduling priority | `resources.requests.cpu` |
| Block I/O | `io.max` | Rate limit | No direct K8s field |
| Network | `net_cls` + tc | Traffic shaping | No direct K8s field |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CPU limits prevent a container from using more CPU | CPU limits throttle the container when the quota is exhausted per period — they slow the container, they do not kill it (unlike memory limits) |
| Setting memory.limit = memory.requests prevents OOM | Requests are for Kubernetes scheduling only; limits are the actual cgroup enforcement. Setting limits ≥ requests reduces OOM risk. |
| Containers inherit host cgroup limits | Each container gets its own cgroup with independently set limits — no implicit inheritance from host |
| OOM kill crashes the entire host | Cgroup-scoped OOM kill only affects the cgroup whose limit was exceeded — the host and other containers are unaffected |
| CPU throttling is always bad | CPU throttling is intentional: it prevents workload A from starving workload B. Throttling under heavy load is expected behaviour if limits are set correctly |

---

### 🚨 Failure Modes & Diagnosis

**Container OOMKilled (Memory Limit Too Low)**

**Symptom:** Container exits suddenly; `docker inspect` shows `OOMKilled: true`; application log shows no error.

**Root Cause:** Container's memory usage exceeded `memory.max`. Kernel OOM killer fired inside the cgroup.

**Diagnostic Command / Tool:**
```bash
# Confirm OOM kill
docker inspect my-app | jq '.[0].State.OOMKilled'
# → true

# Check what the memory usage was
docker stats my-app --no-stream --format "{{.MemUsage}}"
# Observe peak usage to set a better limit

# Kubernetes
kubectl get pod myapp -o json | jq '.status.containerStatuses[].lastState.terminated.reason'
# "OOMKilled" confirms
```

**Fix:** Increase `--memory` limit or fix the memory leak in the application.

**Prevention:** Set limits at 2× average usage. Configure `memory.high` (soft limit) alerts before hitting `memory.max`.

---

**CPU Throttling Hidden Latency**

**Symptom:** Application responds slowly but CPU utilisation appears low. p99 latency is 10× median.

**Root Cause:** CPU limit is too low; application is throttled for significant fractions of each 100ms period. CPU utilisation (time used/time running) looks low because throttle time is not counted as used time.

**Diagnostic Command / Tool:**
```bash
# Check throttle statistics
cat /sys/fs/cgroup/cpu/docker/<container_id>/cpu.stat
# throttled_usec: total time container was throttled
# throttled_periods: number of periods where throttled

# Kubernetes: view CPU throttle rate
kubectl exec -it myapp -- cat /sys/fs/cgroup/cpu/cpu.stat
# or use cAdvisor: container_cpu_throttled_seconds_total
```

**Fix:** Increase CPU limit (`--cpus=1.0`) or reduce CPU limit and scale horizontally.

**Prevention:** Monitor `container_cpu_throttled_seconds_total` (Prometheus/cAdvisor). Alert on throttle rate > 25%.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux Namespaces` — visibility isolation (the complementary container primitive to cgroups)
- `Operating Systems` — process scheduling and memory management concepts

**Builds On This (learn these next):**
- `Container Resource Limits` — the application-level configuration that maps to cgroup settings
- `Container Security` — cgroups are part of the container security model

**Alternatives / Comparisons:**
- `VM Resource Limits (hypervisor)` — hardware-enforced limits; stronger isolation than cgroups
- `ulimit` — per-process limits (predecessor to cgroups, much less powerful)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel resource groups: limits CPU,      │
│              │ memory, I/O per container, scoped OOM    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without limits, one container exhausts   │
│ SOLVES       │ host resources and kills everything else  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Namespaces = visibility isolation;       │
│              │ Cgroups = resource enforcement. Need both│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every container should have     │
│              │ memory and CPU limits defined            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Limits set too low → OOM kills / CPU     │
│              │ throttle → performance degradation       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Host stability + fairness vs risk of     │
│              │ too-tight limits causing app failures    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Circuit breakers for container          │
│              │  resources — trip one, protect the rest" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Resource Limits →              │
│              │ Container Security → Linux Namespaces    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A production Kubernetes node running 40 pods suddenly has all pods experiencing 3–5× higher latency than normal. CPU utilisation on the node shows 65% (not saturated), but `kubectl top pods` shows several pods are using exactly their CPU limit. The throttle metric for those pods shows 40% throttle rate. Trace the exact mechanism: why does CPU throttling cause high latency even at apparently low utilisation, and what does this reveal about the relationship between CPU throttle percentage and p99 latency for request-latency-sensitive applications?

**Q2.** A Java application with a JVM heap of 4 GB is running in a container with `memory.limit = 4.5 GB`. The application is OOMKilled every day at random times. The developer insists "the JVM heap is only 4 GB so the container should have plenty of headroom with 4.5 GB." Identify all the sources of JVM memory consumption beyond the heap that contribute to total RSS (resident set size), calculate a realistic container memory limit, and explain why JVM memory != heap memory.

