---
id: LNX-072
title: "Linux Cgroups v1 and v2 (resource limits, hierarchy)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-071, LNX-022
used_by: LNX-080, LNX-106
related: LNX-071, LNX-080, LNX-083
tags: [cgroups, control-groups, cgroup-v2, resource-limits, cpu-limits, memory-limits, containers, systemd, hierarchy, cgroupfs]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 72
permalink: /technical-mastery/lnx/linux-cgroups/
---

## TL;DR

**cgroups** (control groups) limit, account for, and isolate resource usage
of process groups. cgroup v1: per-subsystem hierarchies (`/sys/fs/cgroup/
cpu/`, `/sys/fs/cgroup/memory/`). cgroup v2: unified hierarchy (`/sys/fs/
cgroup/`), introduced in kernel 4.5, default in modern distros. Key
controllers: `cpu` (CPU time allocation, `cpu.weight`, `cpu.max`), `memory`
(limit RAM, `memory.max`, `memory.swap.max`), `io` (disk throughput),
`pids` (fork bomb prevention). Interface: filesystem - write to control
files. systemd manages cgroups for all system units. Containers (Docker,
k8s) use cgroups for `--memory`, `--cpus` limits.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-072 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | cgroups, control groups, resource limits, cpu limits, memory limits, containers, systemd |
| **Prerequisites** | LNX-071 (Namespaces), LNX-022 (Process management) |

---

### The Problem This Solves

**Problem 1**: A containerized application has a memory leak and is consuming
all available RAM, causing the kernel to start killing other processes (OOM
killer). Without cgroups: no way to limit how much memory a container can
use; one runaway process can OOM-kill the entire host. With cgroups memory
controller: `memory.max=512M` - when the container exceeds 512 MB, the kernel
OOM-kills processes WITHIN the cgroup, not on the entire host. The leak is
contained.

**Problem 2**: A CPU-intensive batch job is starving web application processes
on the same host. Without cgroups: all processes compete for CPU equally.
With cgroups CPU controller: batch job gets `cpu.weight=100`, web app gets
`cpu.weight=900` - under contention, the web app gets 9x more CPU time.
This is the mechanism behind Kubernetes `requests` and `limits`.

---

### Textbook Definition

**cgroups** (control groups): A Linux kernel feature (kernel 2.6.24, 2008)
that hierarchically organizes processes into groups and applies resource
policies to those groups. Implemented as a virtual filesystem (cgroupfs)
at `/sys/fs/cgroup/`.

**cgroup v1**: Multiple separate hierarchies, one per controller (subsystem).
`/sys/fs/cgroup/memory/` is a hierarchy for memory control, independent of
`/sys/fs/cgroup/cpu/`. A process can be in different groups in each hierarchy.

**cgroup v2**: Single unified hierarchy. All controllers under one tree.
A process can only be in one cgroup. Replaces v1. Enabled in kernel 4.5,
default in: Ubuntu 21.10+, RHEL 9, Debian 11 (Bullseye), Fedora 31.

**Key controllers:**
- **cpu**: CPU time scheduling (weight-based proportional, hard limits)
- **memory**: RAM limits, swap limits, OOM behavior
- **io**: Block I/O throughput and IOPS limits
- **pids**: Maximum number of processes (prevents fork bombs)
- **cpuset**: Pin processes to specific CPUs/NUMA nodes
- **net_cls/net_prio**: Network packet classification (v1 only)

---

### Understand It in 30 Seconds

```bash
# === Check whether system uses cgroup v1 or v2 ===
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2  <- v2 (unified)
# OR:
# tmpfs on /sys/fs/cgroup type tmpfs       <- v1 (multiple hierarchies)
# cgroup on /sys/fs/cgroup/memory type cgroup

# Also: check if root is unified:
ls /sys/fs/cgroup/
# v1: cpu/ memory/ blkio/ pids/ ...  (multiple dirs, one per controller)
# v2: cgroup.controllers  cgroup.procs  io.stat  memory.stat ... (files!)

# === cgroup v2: understand the hierarchy ===
ls /sys/fs/cgroup/
# cgroup.controllers  <- what controllers are available at this level
# cgroup.procs        <- PIDs in this cgroup
# cgroup.subtree_control  <- which controllers active for children
# cpu.stat  memory.stat  io.stat     <- current stats
# user.slice/  system.slice/         <- systemd-managed sub-cgroups

# === Find what cgroup a process is in ===
cat /proc/self/cgroup
# v2: 0::/user.slice/user-1000.slice/session-1.scope
# v1: 12:pids:/user.slice/...
#     11:memory:/user.slice/...
#     (separate line per controller in v1)

# === See Docker container's cgroup ===
docker run -d --name myapp --memory=512m --cpus=1.5 nginx
docker inspect --format '{{.HostConfig.Memory}}' myapp  # bytes
# On host, find the cgroup:
cat /proc/$(docker inspect -f '{{.State.Pid}}' myapp)/cgroup

# === cgroup v2: set memory limit manually ===
# Create a new cgroup:
mkdir /sys/fs/cgroup/myapp
# Add a process:
echo $$ > /sys/fs/cgroup/myapp/cgroup.procs
# Set memory limit (512 MB):
echo $((512*1024*1024)) > /sys/fs/cgroup/myapp/memory.max
# Verify:
cat /sys/fs/cgroup/myapp/memory.max    # 536870912

# Enable cpu controller for this cgroup's children:
echo "+cpu +memory +io +pids" >> /sys/fs/cgroup/cgroup.subtree_control
# Set CPU weight (default 100, range 1-10000):
echo 200 > /sys/fs/cgroup/myapp/cpu.weight  # 2x normal weight
# Set CPU hard limit: max 50% of one CPU:
echo "50000 100000" > /sys/fs/cgroup/myapp/cpu.max
# Format: "quota period_in_us" = 50000us quota per 100000us period = 50%

# === Read current resource usage ===
cat /sys/fs/cgroup/myapp/memory.current  # current bytes used
cat /sys/fs/cgroup/myapp/memory.stat     # detailed memory stats
cat /sys/fs/cgroup/myapp/cpu.stat        # CPU time used
cat /sys/fs/cgroup/myapp/io.stat         # I/O stats

# === systemd integration ===
# systemd organizes everything into cgroups:
systemctl status myapp.service | grep -A3 "CGroup:"
# Shows: /system.slice/myapp.service/  <- cgroup path
#        └─12345 /usr/bin/myapp

# Set resource limits via systemd unit:
systemctl set-property myapp.service MemoryMax=512M
systemctl set-property myapp.service CPUQuota=150%  # 1.5 CPUs

# Or in unit file:
# [Service]
# MemoryMax=512M
# CPUQuota=150%
# TasksMax=100       <- maps to pids limit
```

---

### First Principles

**The cgroup v2 hierarchy model:**
```
/sys/fs/cgroup/ (root cgroup)
  |-- cgroup.controllers: "cpu io memory pids"  <- available
  |-- cgroup.subtree_control: "cpu memory"       <- enabled for children
  |-- system.slice/        <- systemd: system services
  |   |-- nginx.service/
  |   |   |-- cgroup.procs  <- nginx's PIDs
  |   |   |-- memory.max    <- nginx's memory limit
  |   |   `-- cpu.weight    <- nginx's CPU weight
  |   `-- mysql.service/
  |       |-- cgroup.procs  <- mysql's PIDs
  |       `-- memory.max    <- mysql's memory limit
  `-- user.slice/          <- user sessions
      `-- user-1000.slice/
          `-- session-1.scope/  <- your terminal session
              `-- cgroup.procs  <- your processes

Rule: A process belongs to EXACTLY ONE cgroup.
Rule: A cgroup can have child cgroups.
Rule: Resources are distributed DOWN the hierarchy.
```

**CPU controller - how it works:**
```
cpu.weight = relative CPU share (similar to CFS weight/nice value)
cpu.max = hard limit (bandwidth throttling)

Weight example:
  nginx:  cpu.weight=200
  mysql:  cpu.weight=100
  batch:  cpu.weight=50
  
When all three are CPU-bound simultaneously:
  Total weight = 200+100+50 = 350
  nginx gets: 200/350 = 57% of available CPU
  mysql gets: 100/350 = 29%
  batch gets:  50/350 = 14%
  
  When mysql is idle: nginx and batch share the freed CPU
  (weight = RELATIVE priority under contention, not hard allocation)

cpu.max = hard limit (absolute cap):
  "100000 100000" = 100ms quota per 100ms period = 100% of 1 CPU
  "50000 100000"  = 50ms quota per 100ms period = 50% of 1 CPU
  "200000 100000" = 200ms quota per 100ms period = 200% = 2 CPUs
  
  With cpu.max, the process is THROTTLED even if CPUs are idle
  This is the Kubernetes CPU limits mechanism

Kubernetes mapping:
  requests.cpu = 100m (100 millicores)
  -> cpu.weight = 102 (proportional to millicores)
  
  limits.cpu = 500m (500 millicores)
  -> cpu.max = "50000 100000" (50ms per 100ms = 50%)
  
  CPU throttled = process sleeping waiting for next period
  Symptom: high latency, CPU looks "idle" but apps are slow
  Diagnosis: cat /sys/fs/cgroup/.../cpu.stat | grep throttled
```

**Memory controller - OOM behavior:**
```
memory.max: hard limit (triggers OOM kill within cgroup)
memory.high: soft limit (causes memory reclaim, throttles allocations)
memory.min: guaranteed minimum (kernel won't reclaim below this)

Memory OOM inside a cgroup (memory.max exceeded):
  1. Kernel tries to reclaim pages (shrink page cache, swap)
  2. If reclaim fails: triggers OOM killer WITHIN the cgroup
  3. OOM killer kills largest process in cgroup
  4. Writes event to memory.events (oom, oom_kill counts)
  
Unlike a system-wide OOM: only processes in THIS cgroup are at risk
The rest of the system continues normally

Check if OOM kills have occurred:
  cat /sys/fs/cgroup/myapp/memory.events
  # low 0
  # high 0
  # max 0
  # oom 1          <- 1 OOM event!
  # oom_kill 1     <- 1 process OOM killed

memory.swap.max: controls swap usage within cgroup
  "0" = no swap allowed (pure RAM limit)
  "max" = unlimited swap
  Setting both memory.max and memory.swap.max = total memory+swap budget
```

---

### Thought Experiment

Simulating Kubernetes resource limits with raw cgroups:

```bash
#!/bin/bash
# Reproduce Kubernetes memory limits at the cgroup level

# Setup: create a cgroup for our "pod":
CGROOT="/sys/fs/cgroup/k8s-demo"
mkdir -p "$CGROOT"

# Enable controllers (must be enabled at parent level first):
echo "+cpu +memory +pids" > /sys/fs/cgroup/cgroup.subtree_control

# Set limits matching k8s spec:
# resources:
#   requests:
#     memory: "128Mi"
#     cpu: "250m"
#   limits:
#     memory: "256Mi"
#     cpu: "500m"

# Memory limit = limits.memory:
echo $((256*1024*1024)) > "$CGROOT/memory.max"   # 256 MiB

# Memory guarantee = requests.memory (soft, not hard in plain cgroups):
echo $((128*1024*1024)) > "$CGROOT/memory.min"   # 128 MiB

# CPU limit: 500m = 50ms per 100ms period:
echo "50000 100000" > "$CGROOT/cpu.max"

# CPU request: 250m ~ weight 256 (k8s formula: milliCPU * 1024 / 1000):
echo 256 > "$CGROOT/cpu.weight"

# PID limit (prevent fork bombs):
echo 1000 > "$CGROOT/pids.max"

# Run our "pod":
echo $$ > "$CGROOT/cgroup.procs"

# Now run a memory hog:
python3 -c "
import sys
data = []
try:
    while True:
        data.append(bytearray(10*1024*1024))  # 10 MB chunks
        print(f'Allocated: {len(data)*10} MB')
except MemoryError:
    print('MemoryError (allocator failed before OOM kill)')
"
# Process will be OOM-killed when memory.max exceeded!

# Check what happened:
cat "$CGROOT/memory.events"
# oom: 1
# oom_kill: 1

# Cleanup:
rmdir "$CGROOT"   # only works when no processes in cgroup
```

---

### Mental Model / Analogy

```
cgroups = utility billing system for a shared office building

Office building = Linux host
Tenants = processes/process groups
Utilities = CPU, memory, disk I/O, network

v1 (old system):
  Separate meters for EACH utility:
    Electricity meter room (cpu hierarchy)
    Water meter room (memory hierarchy)
    Gas meter room (io hierarchy)
  
  Problem: same tenant has different "accounts" in each room
  Billing is complicated: have to check 3 separate rooms

v2 (unified system):
  ONE meter panel, ALL utilities on same tenant account:
  Each tenant has ONE cgroup = ONE location in hierarchy
  All utilities visible in ONE place
  
  simpler: systemctl status shows all limits in one place

cpu.weight = monthly utility BUDGET (proportional allocation):
  Tenant A: budget 200 electricity credits
  Tenant B: budget 100 electricity credits
  If both use 100% at the same time: A gets 2x more than B
  If only A is using electricity: A gets ALL of it (no waste)
  
cpu.max = circuit breaker (hard limit):
  Regardless of available electricity: Tenant A's circuit 
  trips at 500W. They physically cannot use more.
  (Even if building has extra capacity)
  
  This is why k8s CPU limits cause "CPU throttling":
  Container hits circuit breaker, must wait for next period

memory.max = storage unit size (absolute cap):
  Tenant A rented a 512 MB storage unit
  Cannot store more than 512 MB
  If tries: must throw something away (OOM kill)
  Unit is self-contained: throwing away doesn't affect others

pids.max = maximum number of keys issued:
  Prevents fork bomb: no more than 1000 keys to this storage area
```

---

### Gradual Depth - Five Levels

**Level 1:**
What cgroups do: limit resource usage per process group. v1 vs v2 distinction.
Finding a process's cgroup via `/proc/[pid]/cgroup`. systemd creates cgroups
automatically. Docker `--memory` and `--cpus` use cgroups.

**Level 2:**
Cgroup v2 filesystem structure: `cgroup.procs`, `cpu.weight`, `cpu.max`,
`memory.max`, `memory.current`, `memory.events`. Creating cgroups manually
(mkdir + write). `subtree_control` for enabling controllers at each level.
Reading `cpu.stat` for throttled time.

**Level 3:**
CPU bandwidth control: quota/period model. Memory hierarchy: max/high/min/low.
OOM events via `memory.events`. pids controller for fork bomb prevention.
io controller: `io.max` for bandwidth limits. cpuset for NUMA pinning.
cgroup freeze (`cgroup.freeze`). Systemd unit resource properties.

**Level 4:**
Cgroup v1 vs v2 coexistence (hybrid mode). Container runtimes (runc, containerd)
cgroup setup. Kubernetes cgroup driver: `systemd` vs `cgroupfs`. CPU
throttling diagnosis: `cpu.stat throttled_usec`. Memory pressure events
via `memory.pressure`. cgroup delegation: allowing unprivileged processes
to manage their own sub-cgroups. cgroup v2 writeback throttling.

**Level 5:**
CPU scheduler interaction: CFS bandwidth throttling and latency impact.
Understanding CFS periods and the CPU throttling problem in k8s (why
latency-sensitive apps should avoid CPU limits). Memory reclaim at cgroup
boundaries: `memory.reclaim`, pagetable overhead. cgroup v2 PSI (Pressure
Stall Information): per-cgroup pressure metrics. eBPF + cgroups for per-
cgroup observability. NUMA awareness in cgroup memory policies.

---

### Code Example

**BAD - common cgroup/container resource mistakes:**
```bash
# BAD 1: Setting Kubernetes CPU limits without understanding throttling:
# k8s manifest:
# resources:
#   limits:
#     cpu: "100m"    # 10% of one CPU
# 
# A web service handling 100 req/s at 50ms each = 5 CPU-seconds/second
# With 100m limit: process WILL be throttled
# Symptom: p99 latency spikes even when overall CPU usage looks low
# 
# Diagnosis:
kubectl top pod mypod   # shows CPU usage: 80m (under 100m limit)
# BUT: check throttling:
# Need to exec into node and check:
# cat /sys/fs/cgroup/.../cpu.stat | grep throttled
# throttled_periods 12345    <- high number = throttled frequently

# BAD 2: Memory limit without swap limit allows swap-thrashing:
echo 268435456 > /sys/fs/cgroup/myapp/memory.max   # 256 MB
# No memory.swap.max set: default = unlimited swap
# Application allocates 400 MB:
#   256 MB RAM + 144 MB swap (if swap exists)
#   Application "works" but is very slow (swapping)
#   memory.current shows 256 MB but actual usage is 400 MB

# BAD 3: Not enabling controllers for child cgroups:
mkdir /sys/fs/cgroup/myapp
echo $$ > /sys/fs/cgroup/myapp/cgroup.procs
echo 268435456 > /sys/fs/cgroup/myapp/memory.max
# Error! If memory controller is not in parent's subtree_control:
# write error: Invalid argument
# Fix: echo "+memory" >> /sys/fs/cgroup/cgroup.subtree_control
```

**GOOD - correct cgroup v2 setup:**
```bash
# GOOD: Full cgroup v2 resource isolation setup:
CGROOT="/sys/fs/cgroup/myapp"

# Step 1: Enable needed controllers at root level:
echo "+cpu +memory +pids +io" > /sys/fs/cgroup/cgroup.subtree_control

# Step 2: Create cgroup:
mkdir -p "$CGROOT"

# Step 3: Set resource limits:
# Memory: 512 MB hard limit, no swap:
echo $((512*1024*1024)) > "$CGROOT/memory.max"
echo 0 > "$CGROOT/memory.swap.max"   # no swap

# CPU: weight 200 (2x normal) + hard limit at 1.5 CPUs:
echo 200 > "$CGROOT/cpu.weight"
echo "150000 100000" > "$CGROOT/cpu.max"   # 150% = 1.5 CPUs

# PIDs: prevent fork bombs:
echo 500 > "$CGROOT/pids.max"

# Step 4: Assign process:
echo $PROCESS_PID > "$CGROOT/cgroup.procs"

# Step 5: Monitor (systemd-friendly):
# Read current stats:
cat "$CGROOT/memory.current"     # bytes currently used
cat "$CGROOT/memory.events"      # OOM events (oom, oom_kill)
cat "$CGROOT/cpu.stat"           # cpu time + throttling stats
awk '/throttled_usec/ {print "Throttled:", $2/1000000, "sec"}' \
    "$CGROOT/cpu.stat"

# Systemd unit alternative (preferred for services):
cat /etc/systemd/system/myapp.service
# [Service]
# ExecStart=/usr/bin/myapp
# MemoryMax=512M
# MemorySwapMax=0
# CPUQuota=150%
# CPUWeight=200
# TasksMax=500
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "cpu.max guarantees a container gets its CPU allocation" | `cpu.max` is a CEILING, not a floor. It sets the maximum CPU the container can use, but doesn't guarantee it will receive that much. If a container's processes are idle or I/O-bound, they use less than the limit. Only `cpu.weight` (relative shares) guarantees relative priority under CPU contention. In Kubernetes: CPU requests are implemented via `cpu.weight` (guaranteed relative share), CPU limits via `cpu.max` (hard ceiling). A container with CPU limits but no other containers competing for CPU can still be throttled even when the host has idle CPUs - this is the Kubernetes CPU throttling problem that causes p99 latency spikes. |
| "Setting memory.max prevents the system from running out of memory" | `memory.max` causes OOM kills WITHIN the cgroup when exceeded, but the cgroup's memory usage before the limit is reached still consumes host RAM. If you have 50 containers each with `memory.max=1GB` on a 32 GB host, and many of them simultaneously use 900 MB: the host will OOM. Cgroup memory limits protect OTHER workloads from a SINGLE container's runaway usage, but don't prevent aggregate memory exhaustion. For cluster-level protection: Kubernetes resource requests determine scheduling (ensuring total requested memory doesn't exceed node capacity). |
| "cgroup v2 is just a cleanup of v1 with no behavior differences" | cgroup v2 has significant behavioral differences: (1) Unified hierarchy - a process can only be in ONE cgroup (v1: a process could be in different cgroups in different hierarchies). (2) "No-internal-processes" rule: leaf nodes can have tasks OR children, not both (enforces cleaner hierarchy). (3) The `memory.min` guarantee didn't exist in v1. (4) PSI (Pressure Stall Information) metrics are v2-only. (5) The io controller in v2 subsumes blkio from v1 but adds writeback throttling. Migrating from v1 to v2: container runtimes had to update their cgroup driver; there was a significant transition period (Kubernetes v1.22 deprecated cgroupfs driver, moved to systemd cgroup driver). |
| "I can see all resource usage in /sys/fs/cgroup/" | `/sys/fs/cgroup/` shows resource accounting and limits, but not all resource consumers. Memory usage shown in cgroups does NOT include: kernel memory allocations attributed to kernel rather than to a specific cgroup, shared page cache pages (counted differently), memory mapped by multiple processes. For complete memory analysis, use `smem`, `/proc/[pid]/smaps`, or `memory.stat` (which shows RSS, cache, etc. separately). Also: `/sys/fs/cgroup/` shows current snapshot values; for trends, use `systemd-cgtop`, `ctop` (Docker), or Prometheus with cAdvisor. |

---

### Failure Modes & Diagnosis

**cgroup resource issue diagnostics:**
```bash
# Symptom: Docker container being OOM killed frequently
docker logs mycontainer 2>&1 | grep -i "killed\|oom"
docker stats mycontainer   # real-time memory usage

# Get container's cgroup path:
CPID=$(docker inspect -f '{{.State.Pid}}' mycontainer)
CGPATH=$(cat /proc/$CPID/cgroup | grep -E '^0::' | cut -d: -f3)
# v2: CGPATH=/system.slice/docker-<id>.scope

# Check memory events:
cat /sys/fs/cgroup$CGPATH/memory.events
# oom: 3        <- 3 OOM events
# oom_kill: 3   <- 3 processes killed
# max: 5        <- 5 times hit memory.max (some reclaimed before kill)

# Symptom: Application latency spikes, CPU looks idle
# Diagnose CPU throttling:
cat /sys/fs/cgroup$CGPATH/cpu.stat
# usage_usec 150000000     <- CPU time used
# user_usec 100000000
# system_usec 50000000
# nr_periods 1500          <- number of measurement periods
# nr_throttled 300         <- 300 periods where process was throttled!
# throttled_usec 15000000  <- 15 seconds of throttle time total
# 300/1500 = 20% throttled - significant latency impact

# Fix: increase cpu.max or remove CPU limits if host has capacity:
echo "200000 100000" > /sys/fs/cgroup$CGPATH/cpu.max   # 2 CPUs

# Symptom: Cannot create child cgroup
mkdir /sys/fs/cgroup/myapp/child
echo "+memory" > /sys/fs/cgroup/myapp/cgroup.subtree_control
# Error: write error: Permission denied or Invalid argument
# Check: is memory enabled at parent's level?
cat /sys/fs/cgroup/myapp/cgroup.controllers
# If memory not in output: not available - enable at higher level first
cat /sys/fs/cgroup/cgroup.subtree_control   # check root
# Add if missing: echo "+memory" >> /sys/fs/cgroup/cgroup.subtree_control
```

---

### Related Keywords

**Foundational:**
LNX-071 (Namespaces), LNX-022 (Process management)

**Builds on this:**
LNX-080 (Container internals), LNX-083 (OOM Killer), LNX-106 (Container platform architecture)

**Related:**
LNX-077 (CFS Scheduler), LNX-075 (Transparent Huge Pages)

---

### Quick Reference Card

| File | Purpose |
|------|---------|
| `cgroup.procs` | PIDs in this cgroup |
| `cgroup.controllers` | Available controllers |
| `cgroup.subtree_control` | Enabled for children |
| `memory.max` | Hard memory limit (bytes or "max") |
| `memory.current` | Current memory usage |
| `memory.events` | OOM event counters |
| `cpu.weight` | Relative CPU priority (1-10000, default 100) |
| `cpu.max` | `quota period_us` hard CPU limit |
| `cpu.stat` | `nr_throttled`, `throttled_usec` |
| `pids.max` | Max number of processes |

**3 things to remember:**
1. Namespaces = ISOLATION (what processes see); cgroups = LIMITS (how much they use)
2. CPU throttling (`cpu.max`) causes latency spikes even when host CPU is idle - check `cpu.stat` `nr_throttled`
3. `memory.max` = OOM kill WITHIN cgroup only (protects other cgroups); aggregate host OOM still possible

---

### Transferable Wisdom

cgroup concepts appear directly in: Kubernetes resource requests (-> cpu.weight)
and limits (-> cpu.max, memory.max). Docker `--memory`, `--cpus`, `--memory-swap`.
systemd services: `MemoryMax=`, `CPUQuota=`, `TasksMax=` in unit files - these
write directly to cgroup files. The `cpu.weight` concept (relative priority,
not hard allocation) appears in Linux nice values, `ionice`, and traffic shaping
`tc qdisc`. Understanding cgroup CPU throttling explains the Kubernetes CPU
throttling debate: why setting strict CPU limits on latency-sensitive services
can cause unexplained latency spikes (the container is SLEEPING waiting for
the next CPU period even when CPUs are available). Platform engineers
monitoring production: `container_cpu_cfs_throttled_periods_total` Prometheus
metric (from cAdvisor) directly reads `nr_throttled` from cgroup. The
cgroup hierarchy model (parent limits constrain children) appears in
Kubernetes namespace resource quotas and LimitRanges.

---

### The Surprising Truth

The Kubernetes CPU throttling problem - where pods with CPU limits experience
significant latency spikes even with idle host CPUs - is a fundamental design
consequence of how cgroup CPU bandwidth control works. The `cpu.max` hard limit
uses a quota/period model: if a process uses its CPU quota for the period, it's
throttled for the REST of that period (100ms by default). A single request
that uses 5ms of CPU but comes in at the END of a period might get only 1ms
before throttling kicks in - causing 100ms of sleep for a 5ms task. The
result: p99/p999 latency can be 100x worse than average latency purely due
to cgroup throttling. The fix debated in the Kubernetes community: don't set
CPU limits (only set requests/weights), or increase CFS period (`--cpu-cfs-period`).
Google's internal GKE workloads historically ran WITHOUT CPU limits for
latency-sensitive services. This contradicts the conventional wisdom that
all production containers should have both resource requests AND limits.
The correct advice depends on workload type: CPU limits are valuable for
batch workloads, potentially harmful for latency-sensitive services.

---

### Mastery Checklist

- [ ] Can distinguish cgroup v1 (per-subsystem hierarchies) from v2 (unified hierarchy)
- [ ] Can find a process's cgroup and read its resource limits and current usage
- [ ] Understands cpu.weight (relative share) vs cpu.max (hard limit) and when each is appropriate
- [ ] Can diagnose OOM kills via memory.events and CPU throttling via cpu.stat
- [ ] Understands the Kubernetes CPU throttling problem and its relationship to cgroup cpu.max

---

### Think About This

1. A Kubernetes pod has `cpu: "500m"` requests and `cpu: "500m"` limits (requests
   = limits, a common recommendation). The pod handles HTTP requests, each
   taking 10ms of CPU. The host has 8 CPUs and only 20% CPU utilization.
   Despite this, the p99 latency is 120ms. Using your knowledge of cgroup
   `cpu.max` and CFS periods, explain the exact mechanism causing these
   latency spikes. What would you change, and why might that tradeoff be
   acceptable or unacceptable?

2. You are designing a multi-tenant SaaS platform where each customer's
   workload runs in a separate container. One customer has a Python script
   with a memory leak. Describe the exact cgroup configuration that would:
   (a) limit that customer's memory to 1 GB, (b) ensure OOM kill happens
   WITHIN their container (not system-wide), (c) prevent them from using
   swap (to avoid slow degradation instead of clean failure), and (d) alert
   operations when OOM events occur. Write the cgroup file writes and the
   monitoring approach.

3. Your company is migrating a Java application from a VM to a container.
   The Java heap is set to `-Xmx8G` (8 GB). The container has `memory.max`
   set to 6 GB. What will happen when the JVM tries to use more than 6 GB?
   Will the JVM see the container's memory limit and self-restrict? How should
   you properly configure Java heap for containerized workloads to avoid OOM
   kills?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between cgroups and namespaces in Linux, and why do containers need both?
A: Namespaces and cgroups solve completely different problems: NAMESPACES provide ISOLATION - they change what a process can SEE. A process in its own PID namespace sees its own process tree (its init is PID 1). In its own network namespace: sees its own network stack. In its own mount namespace: sees its own filesystem. Namespaces are about VISIBILITY - "what does this process know about the rest of the system?" CGROUPS provide RESOURCE GOVERNANCE - they control how much a process can USE. CPU: how many CPU cycles. Memory: how much RAM. IO: how much disk bandwidth. PIDs: how many processes it can fork. Cgroups are about CONSUMPTION - "how much of the machine's resources can this process group consume?" Why containers need both: without namespaces, containers would share PIDs, network ports, hostnames - two web servers couldn't both use port 80. Without cgroups, one container could consume all CPU/memory and starve others. Together: namespaces = "you can't see or interfere with other containers", cgroups = "you can't starve other containers". Classic example: two nginx containers on one host. Namespaces: each thinks it's the only process, has port 80 free, its own hostname. cgroups: each is limited to 512 MB RAM, 1 CPU - so one can't starve the other. The host kernel manages them as processes, but they're isolated and resource-constrained.

**Expert:**
Q: Explain cgroup v2's unified hierarchy and how it changes the behavior from v1, particularly for container runtimes.
A: cgroup v1 had a fundamental design flaw: independent hierarchies per controller. A process could be in `/cpu/groupA` and simultaneously in `/memory/groupB` - creating complex multi-hierarchy membership and hard-to-reason-about relationships. v2 changes this with a UNIFIED hierarchy: one tree, all controllers, each process in exactly one cgroup. Behavioral differences with production impact: (1) NO INTERNAL PROCESSES rule: in v2, a cgroup can only contain processes if it has NO children. You can't have processes in an intermediate node AND have child cgroups. This forced container runtimes to redesign their cgroup layout. Kubernetes containers must be in leaf cgroups, pods in intermediate cgroups with no direct tasks. (2) SUBTREE DELEGATION model: `cgroup.subtree_control` controls which resource controllers are active for children, allowing delegation without root. This enables rootless containers: a user can manage cgroups within their delegated subtree. (3) MEMORY GUARANTEES: `memory.min` (hard guarantee: kernel won't reclaim below this) didn't exist in v1. (4) PSI (Pressure Stall Information): per-cgroup pressure metrics available in v2 only - shows how much time processes spent waiting for CPU/memory/IO. Container runtime implications: Docker and containerd had to implement a `cgroupDriver: systemd` mode (vs `cgroupfs`) for k8s compatibility. With systemd as cgroup driver: kubelet creates cgroups via systemd APIs (not by writing to /sys/fs/cgroup directly), which integrates with the host's systemd-managed hierarchy. The transition: Kubernetes v1.22 deprecated the cgroupfs driver, and containerd 1.4+ defaults to systemd driver. For platform engineers: the systemd cgroup driver means the cgroup tree is managed consistently with the host, preventing the "two separate hierarchies" problem that caused issues in v1 mixed environments.
