---
layout: default
title: "Cgroups"
parent: "Linux"
nav_order: 158
permalink: /linux/cgroups/
number: "0158"
category: Linux
difficulty: ★★★
depends_on: Process Management, Linux Namespaces
used_by: Containers, Kubernetes, Docker
related: Linux Namespaces, ulimit, /sys File System
tags:
  - linux
  - os
  - containers
  - performance
  - deep-dive
---

# 158 — Cgroups

⚡ TL;DR — cgroups (control groups) limit and account for how much CPU, memory, I/O, and network a group of processes can consume — they are the mechanism behind `docker run --memory=512m` and Kubernetes resource limits.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Ten containers share a host. Container A starts consuming all available CPU because of a bug. All other containers starve. Container B leaks memory until the OOM killer fires and kills a random process — possibly from Container C. There's no fairness, no accounting, and no containment of bad behaviour. Namespaces give processes private views, but not resource protection.

**THE BREAKING POINT:**
A single rogue process can consume 100% of CPU, all available memory, and saturate disk I/O — affecting every other workload on the machine. Without resource limits enforced at the kernel level, multi-tenant hosting is impossible to make reliable.

**THE INVENTION MOMENT:**
This is exactly the problem cgroups solve. A container's processes are placed in a cgroup with `memory.max=512M` and `cpu.max=50000 100000` (50% of one CPU). When the container's memory hits 512MB, the kernel OOM-kills processes within that cgroup only — not random processes elsewhere. CPU usage is throttled to 50%. The blast radius is contained by design.

---

### 📘 Textbook Definition

**cgroups** (control groups) is a Linux kernel feature that organises processes into hierarchical groups and enforces per-group resource limits, accounting, and isolation for CPU, memory, block I/O, network, and other resources. cgroups v1 (Linux 2.6.24) uses separate hierarchies per resource type; **cgroups v2** (unified hierarchy, Linux 4.5, now default in most distributions) provides a single process tree with all controllers applying to it. The control interface is exposed via a virtual filesystem mounted at `/sys/fs/cgroup/`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
cgroups put processes into groups and enforce hard resource limits (CPU, memory, I/O) on each group.

**One analogy:**

> cgroups are like budget envelopes at a company. Each department (cgroup) gets an envelope with a fixed budget (resource limit): CPU budget, memory budget, disk budget. When a department overspends its memory budget, only that department faces consequences — the rest of the company is unaffected. Namespaces are about privacy (what you can see); cgroups are about budgets (what you can spend).

**One insight:**
cgroups v2's unified hierarchy was a significant architectural improvement over v1. In v2, a process can only be in one place in the hierarchy (not spread across multiple per-resource hierarchies), and resource delegation follows a consistent model. This is why Kubernetes moved to requiring cgroups v2 (Kubernetes 1.25+).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every process belongs to exactly one cgroup in each hierarchy.
2. Resource limits apply to the group, not individual processes — all processes in the group share the limit.
3. Limits are hierarchical: a child cgroup cannot exceed the limits of its parent.
4. Accounting is cumulative: a parent cgroup's usage includes all descendant cgroups.

**DERIVED DESIGN:**
cgroups expose a virtual filesystem (`cgroupfs`). Each directory is a cgroup. Each file is a controller interface:

- `memory.max` = hard memory limit (OOM kill if exceeded)
- `cpu.max` = CPU quota (e.g., `50000 100000` = 50% CPU)
- `blkio.throttle.read_bps_device` = I/O rate limit

Writing a PID to `cgroup.procs` moves that process into the cgroup. All new processes forked from it inherit the cgroup. This inheritance is what makes container process management work — the container runtime places the first process in a cgroup, and everything it spawns inherits the limits.

**THE TRADE-OFFS:**
**Gain:** Hard resource limits that cannot be exceeded; accounting for multi-tenant billing; I/O and network throttling; OOM isolation.
**Cost:** cgroups v1/v2 complexity; incorrect limits cause application failures; per-cgroup OOM kill can be difficult to debug; CPU throttling causes latency spikes at the throttle boundary.

---

### 🧪 Thought Experiment

**SETUP:**
Kubernetes node has 4 CPUs and 8GB RAM. Three pods: API (requests 1 CPU / 1GB), DB (requests 2 CPUs / 4GB), Background (requests 0.5 CPU / 512MB). Total requested: 3.5 CPUs, 5.5GB — fits on the node.

**WHAT HAPPENS AT RUNTIME (without cgroups):**
All three pods share the kernel's CPU scheduler equally. Under load, if Background spawns thousands of threads, it can steal CPU from API — serving user requests. The DB pod might allocate 6GB (exceeding its 4GB "request") and trigger OOM kill of the API pod. No guarantees are enforced.

**WHAT HAPPENS WITH CGROUPS:**
Kubernetes creates cgroups for each pod:

```
/sys/fs/cgroup/kubepods/
  ├── pod-api/    cpu.max=100000 100000  memory.max=1073741824
  ├── pod-db/     cpu.max=200000 100000  memory.max=4294967296
  └── pod-bg/     cpu.max=50000 100000   memory.max=536870912
```

Background processes are throttled to 50% CPU — they cannot starve the API pod. If DB tries to allocate beyond 4GB, it is OOM-killed within its own cgroup. API pod is unaffected.

**THE INSIGHT:**
Kubernetes resource limits are not suggestions or application-level configurations — they are hard kernel-level enforcement mechanisms via cgroups. `kubectl top pod` reads cgroup accounting data. When a pod is OOM-killed, it's the cgroup memory controller that triggered it.

---

### 🧠 Mental Model / Analogy

> cgroups are like fuse boxes in an apartment building. Each apartment (cgroup) has its own fuse box with its own circuit breakers (resource limits). If apartment 5 overloads its circuits (memory limit), its breaker trips (OOM kill) — but apartment 6 is completely unaffected. The building's main panel (root cgroup) sets the maximum available power (total system resources); each floor panel (parent cgroup) distributes it among apartments (child cgroups), and no apartment can draw more than its panel allows.

- "Fuse box per apartment" → cgroup per container/pod
- "Circuit breaker trips" → OOM kill or CPU throttle
- "Building's main panel" → root cgroup
- "Subpanel limits" → child cgroup inherits from parent

Where this analogy breaks down: in a building, all circuits sharing a panel share bandwidth; in cgroups, CPU limits can be set to burstable (use spare CPU when available) or hard limits (never exceed quota).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
cgroups put processes into groups and give each group its own resource budget — like how much CPU time and memory it can use. When a group exceeds its budget, the kernel enforces the limit by slowing down the processes or killing the biggest memory user. This is how Docker's `--memory=512m` actually works.

**Level 2 — How to use it (junior developer):**
cgroups are manipulated via the virtual filesystem at `/sys/fs/cgroup/`. Create a cgroup: `mkdir /sys/fs/cgroup/myapp`. Set limits: `echo "1073741824" > /sys/fs/cgroup/myapp/memory.max` (1GB). Move a process: `echo <PID> > /sys/fs/cgroup/myapp/cgroup.procs`. In Docker: `docker run --memory=512m --cpus=0.5 myimage`. In Kubernetes: resource limits in the pod spec.

**Level 3 — How it works (mid-level engineer):**
cgroups v2 exposes a unified hierarchy. The `cgroup.controllers` file lists available controllers. `cgroup.subtree_control` enables specific controllers for child cgroups. CPU: `cpu.max` specifies `quota period` (microseconds); `cpu.weight` sets relative priority. Memory: `memory.max` is the hard limit; `memory.high` is a soft limit that triggers swap reclaim; `memory.swap.max` limits swap. On OOM: the kernel selects the process with highest `oom_score_adj` in the cgroup. `cgroup.events` provides notifications for OOM events. Kubernetes reads `/sys/fs/cgroup/kubepods/...` for per-pod resource usage for `kubectl top`.

**Level 4 — Why it was designed this way (senior/staff):**
cgroups v1 was designed incrementally by different Google engineers, resulting in each resource controller having its own separate hierarchy and inconsistent semantics. This created real operational problems: a process could be in different groups in different hierarchies, making resource accounting difficult. Tejun Heo's cgroups v2 design (unified hierarchy, coherent delegation model) was a deliberate redesign to fix these inconsistencies. The key insight in v2 is the "no internal process" rule: a cgroup that has child cgroups cannot also have processes directly in it — this forces a clean separation between process placement and resource organisation. This strictness enables correct accounting and prevents accounting inconsistencies that plagued v1.

---

### ⚙️ How It Works (Mechanism)

**cgroups v2 structure:**

```bash
# Mount point
ls /sys/fs/cgroup/
# cgroup.controllers  cgroup.procs  cgroup.subtree_control
# cpu.stat  memory.stat  io.stat
# system.slice/  user.slice/  kubepods/

# Key files in any cgroup directory:
# cgroup.procs        - list of PIDs in this cgroup
# cgroup.controllers  - available controllers
# cgroup.subtree_control - enabled controllers for children
# cgroup.events       - events (populated, frozen, etc)

# Memory controller files
cat /sys/fs/cgroup/memory.max      # hard limit (bytes)
cat /sys/fs/cgroup/memory.high     # soft limit
cat /sys/fs/cgroup/memory.current  # current usage
cat /sys/fs/cgroup/memory.stat     # detailed breakdown

# CPU controller files
cat /sys/fs/cgroup/cpu.max         # quota period
# e.g., "50000 100000" = 50% of 1 CPU per 100ms period
cat /sys/fs/cgroup/cpu.weight      # relative priority (1-10000)
cat /sys/fs/cgroup/cpu.stat        # usage stats

# I/O controller files
cat /sys/fs/cgroup/io.max          # I/O rate limits
cat /sys/fs/cgroup/io.stat         # per-device usage
```

**Create and use a cgroup manually:**

```bash
# Create a cgroup for a web server
mkdir /sys/fs/cgroup/webserver

# Enable memory and CPU controllers
echo "memory cpu" > \
  /sys/fs/cgroup/webserver/cgroup.subtree_control

# Set 512MB memory limit
echo 536870912 > \
  /sys/fs/cgroup/webserver/memory.max

# Set CPU limit: 50% of 1 CPU
echo "50000 100000" > \
  /sys/fs/cgroup/webserver/cpu.max

# Add a process (and all its children will inherit)
echo $$ > /sys/fs/cgroup/webserver/cgroup.procs

# Verify
cat /sys/fs/cgroup/webserver/cgroup.procs

# Monitor usage
watch -n 1 "cat /sys/fs/cgroup/webserver/memory.current"
watch -n 1 "cat /sys/fs/cgroup/webserver/cpu.stat"
```

**Docker cgroup interaction:**

```bash
# Docker creates cgroups per container
docker run --memory=512m --cpus=0.5 --name myapp nginx

# Find the cgroup
CONTAINER_ID=$(docker inspect \
  --format '{{.Id}}' myapp)
ls /sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope/

# Read current memory usage
cat /sys/fs/cgroup/system.slice/\
docker-${CONTAINER_ID}.scope/memory.current

# Read CPU stats
cat /sys/fs/cgroup/system.slice/\
docker-${CONTAINER_ID}.scope/cpu.stat
```

**Kubernetes cgroup structure:**

```bash
# Kubernetes organises cgroups:
# /sys/fs/cgroup/kubepods/
# ├── burstable/   (BestEffort + Burstable pods)
# │   └── pod<UID>/
# │       └── <container-id>/
# └── guaranteed/  (Guaranteed QoS pods)
#     └── pod<UID>/
#         └── <container-id>/

# Find a pod's cgroup
POD_UID="abc123-def456"
ls /sys/fs/cgroup/kubepods/burstable/pod${POD_UID}/

# Read pod memory usage
cat /sys/fs/cgroup/kubepods/burstable/\
pod${POD_UID}/memory.current
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  OOM KILL: Container exceeds memory limit      │
└────────────────────────────────────────────────┘

 Container process allocates memory:
 malloc(large_amount)
       │
       ▼
 Page fault → kernel allocates page
       │  Checks cgroup memory.max
       ▼
 memory.current > memory.max?
       │  YES: Memory limit exceeded
       ▼
 Kernel invokes OOM killer
 (scoped to the cgroup)
       │
       ▼
 Selects process with highest oom_score
 within the cgroup
       │  (other cgroups unaffected)
       ▼
 Sends SIGKILL to selected process
       │
       ▼
 cgroup.events: "oom 1" written
 (Kubernetes reads this)
       │
       ▼
 Kubernetes sees container exit code 137
 (128 + SIGKILL=9)
 Pod status: OOMKilled
       │
       ▼
 Pod is restarted (if restartPolicy=Always)
 Event logged: "OOMKilled"
```

**FAILURE PATH:**
If `memory.max` is set too close to actual working set: the container constantly OOM-kills and restarts, appearing healthy (it restarts quickly) but never completing work. This is called "OOM thrashing". Solution: increase memory limit or reduce application memory usage.

---

### 💻 Code Example

**Example 1 — Kubernetes resource limits:**

```yaml
# pod.yaml — proper resource limits for production
apiVersion: v1
kind: Pod
metadata:
  name: api-server
spec:
  containers:
    - name: api
      image: myapi:latest
      resources:
        requests: # scheduler uses this for placement
          memory: "256Mi"
          cpu: "250m" # 250 millicores = 0.25 CPU
        limits: # cgroup hard limits
          memory: "512Mi"
          cpu: "500m"
      # Guaranteed QoS: requests == limits
      # (placed in /sys/fs/cgroup/kubepods/guaranteed/)
```

**Example 2 — Monitor cgroup resource usage:**

```bash
#!/bin/bash
# Monitor cgroup resource usage for a Docker container
CONTAINER=${1:-$(docker ps -q | head -1)}
CGPATH=$(docker inspect --format \
  '{{.HostConfig.CgroupParent}}' "$CONTAINER")
CID=$(docker inspect --format '{{.Id}}' "$CONTAINER")

# Find cgroup path
for path in \
  "/sys/fs/cgroup/system.slice/docker-${CID}.scope" \
  "/sys/fs/cgroup/docker/${CID}"; do
  [ -d "$path" ] && CGDIR="$path" && break
done

echo "Monitoring: $CONTAINER"
echo "Cgroup: $CGDIR"
echo ""

while true; do
  MEM=$(cat "$CGDIR/memory.current" 2>/dev/null)
  MEM_MAX=$(cat "$CGDIR/memory.max" 2>/dev/null)
  CPU_USAGE=$(cat "$CGDIR/cpu.stat" 2>/dev/null \
    | grep usage_usec | awk '{print $2}')

  MEM_MB=$(( ${MEM:-0} / 1048576 ))
  LIMIT_MB=$(( ${MEM_MAX:-0} / 1048576 ))

  printf "%s Mem: %dMB/%dMB CPU: %s μs\n" \
    "$(date +%H:%M:%S)" "$MEM_MB" "$LIMIT_MB" "$CPU_USAGE"
  sleep 2
done
```

---

### ⚖️ Comparison Table

| Feature        | cgroups v1           | cgroups v2                 | ulimit                |
| -------------- | -------------------- | -------------------------- | --------------------- |
| Process tree   | Multiple hierarchies | Single unified             | Per-process           |
| CPU control    | cpu, cpuacct         | cpu (unified)              | RLIMIT_CPU            |
| Memory control | memory               | memory                     | RLIMIT_AS, RLIMIT_RSS |
| I/O control    | blkio                | io                         | No                    |
| Default since  | Kernel 2.6.24        | Kernel 4.5 (default ~5.10) | Always                |
| Kubernetes     | v1 required pre-1.25 | v2 required 1.25+          | No                    |

How to choose: use cgroups v2 for new systems (Kubernetes 1.25+, systemd 248+); use ulimit only for simple per-process limits in non-containerised environments; never mix v1 and v2 on the same system.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                         |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CPU limits prevent all CPU usage above the threshold   | CPU limits throttle the cgroup when it exceeds its quota in the period — this causes latency spikes at the throttle boundary, not just reduced throughput       |
| memory.max kills the container immediately on breach   | The OOM killer selects and kills a process within the cgroup; the container may continue running with other processes until all exit                            |
| Setting CPU requests = limits guarantees no throttling | Even with requests=limits (Guaranteed QoS), CPU throttling still occurs if the application bursts beyond the CPU limit in a 100ms period                        |
| cgroups v1 and v2 are interchangeable                  | They have different filesystem layouts, different controller semantics, and different delegation models; mixing them is unsupported                             |
| Kubernetes resource limits are respected by the JVM    | The JVM reads /proc to determine total system memory for heap sizing; without JVM flags (-Xmx or UseContainerSupport), the JVM heap can exceed the cgroup limit |

---

### 🚨 Failure Modes & Diagnosis

**CPU Throttling Causing Latency Spikes Despite "Enough" CPU**

**Symptom:**
P99 latency spikes every 100ms even though average CPU usage is below the limit. `kubectl top pod` shows 30% CPU but P99 is high.

**Root Cause:**
The application bursts above the CPU quota within a 100ms scheduling period, gets throttled. The burst is invisible in average metrics but causes latency spikes.

**Diagnostic Command:**

```bash
# Check CPU throttling stats (cgroups v2)
cat /sys/fs/cgroup/kubepods/.../cpu.stat
# throttled_usec: cumulative time throttled
# nr_throttled: number of throttle events

# In Kubernetes: check container_cpu_cfs_throttled_periods_total
# via Prometheus/metrics-server
```

**Fix:**
Increase CPU limit; use `cpu.weight` instead of hard limits for latency-sensitive workloads; implement application-level admission control to avoid bursts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management` — cgroups organise processes; understanding PIDs, fork, and process trees is required
- `Linux Namespaces` — namespaces isolate visibility; cgroups limit resources — containers need both; understanding the distinction is fundamental

**Builds On This (learn these next):**

- `Containers` — Docker and container runtimes use cgroups as their primary resource isolation mechanism
- `Kubernetes` — Kubernetes resource requests and limits map directly to cgroup `cpu.max` and `memory.max`
- `/sys File System` — the cgroup filesystem is mounted under `/sys/fs/cgroup/`; all cgroup tuning is done via sysfs writes

**Alternatives / Comparisons:**

- `ulimit` — per-process resource limits; simpler but not hierarchical and without I/O/network controls
- `systemd` resource controls — `MemoryLimit=`, `CPUQuota=` etc. use cgroups v2 under the hood
- `Kubernetes Resource Quotas` — namespace-level resource quotas built on top of cgroups

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel mechanism that groups processes    │
│              │ and enforces CPU/memory/I/O limits per    │
│              │ group via a virtual filesystem            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Rogue process consuming all resources,    │
│ SOLVES       │ starving other containers/workloads       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Docker --memory= and K8s limits= are      │
│              │ just writes to /sys/fs/cgroup/memory.max  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-tenant workloads; container         │
│              │ resource isolation; preventing noisy      │
│              │ neighbour problems                       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple single-process limits — ulimit     │
│              │ is simpler and sufficient                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Hard resource guarantees vs CPU           │
│              │ throttling latency spikes at quota        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Budget envelopes for process groups —    │
│              │ per-department spending limits"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ cgroups v2 → systemd resource mgmt → OOM │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java microservice runs in a Kubernetes pod with `limits: memory: 512Mi`. The JVM crashes with OOM error despite the application using only 300MB of heap. Explain all the memory regions a JVM uses beyond the heap (metaspace, JIT code cache, thread stacks, off-heap, native libraries), show how each contributes to the total process RSS, and determine the minimum `memory.max` cgroup value that would prevent OOM for this service — citing specific JVM flags you would use to control each memory region.

**Q2.** Your Kubernetes cluster is migrating from cgroups v1 to v2. Describe the three concrete operational impacts this migration has on: (a) how the container runtime (containerd/runc) creates and manages cgroups, (b) how Kubernetes kubelet enforces pod resource limits differently in v2 vs v1, and (c) what changes are required for applications that read `/sys/fs/cgroup/memory/...` paths (v1) for memory limit auto-detection.
