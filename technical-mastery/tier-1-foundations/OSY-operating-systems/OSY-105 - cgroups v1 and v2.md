---
id: OSY-105
title: cgroups v1 and v2
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-054, OSY-070, OSY-091
used_by: []
related: OSY-104, OSY-106, OSY-107
tags:
  - cgroups
  - Linux
  - containers
  - resource-isolation
  - Kubernetes
  - memory-limit
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 105
permalink: /technical-mastery/osy/cgroups/
---

## TL;DR

cgroups (control groups) enforce resource limits on process
groups: CPU shares, memory hard limits, I/O bandwidth,
network priority. Foundation of Docker and Kubernetes
resource isolation. cgroups v2 (2016, unified hierarchy)
replaced v1 (per-subsystem mounts). Kubernetes 1.25+ uses
cgroups v2 by default. Critical for understanding container
OOM, CPU throttling, and pod resource limits.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-105 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | cgroups, resource limits, memory limit, CPU throttle, container |
| **Prerequisites** | OSY-009, OSY-054, OSY-070, OSY-091 |

---

### cgroups Fundamentals

```
cgroup = control group = kernel feature to:
  1. GROUP processes together
  2. LIMIT their combined resource usage
  3. MONITOR their combined resource usage
  4. PRIORITIZE between groups
  
Resources controlled:
  cpu: CPU time allocation (shares and quotas)
  memory: RAM and swap limits
  blkio (v1) / io (v2): block I/O bandwidth
  net_cls / net_prio: network priority
  cpuset: allowed CPU cores and NUMA nodes
  pids: limit number of processes/threads
  devices: allow/deny device access
  freezer: pause/resume process groups
  
Relationship to containers:
  Docker container = namespaces (isolation) + cgroups (limits)
  Namespaces: process thinks it's alone (sees only its PID, network, etc.)
  cgroups: process is actually limited (can't use more than N CPU/RAM)
  
  Without cgroups:
    Container could use 100% of host CPU (noisy neighbor problem)
    Container could allocate all RAM (OOM kill other containers)
    
  With cgroups:
    Docker: --memory=2g -> sets memory.limit_in_bytes = 2GB
    Docker: --cpus=2 -> sets cpu.cfs_quota_us = 200000 (2 cores)
    Kubernetes: resources.limits.memory -> cgroup memory limit
```

---

### cgroups v1 Architecture

```
cgroups v1: one hierarchy per subsystem (pre-2016)
  
  /sys/fs/cgroup/
    memory/
      container-abc/
        memory.limit_in_bytes   <- set limit
        memory.usage_in_bytes   <- current usage
        memory.stat             <- detailed stats
    cpu/
      container-abc/
        cpu.cfs_quota_us        <- CPU quota (microseconds per period)
        cpu.cfs_period_us       <- period (default: 100000 = 100ms)
        cpu.shares              <- relative weight (soft limit)
    cpuset/
      container-abc/
        cpuset.cpus             <- allowed CPUs (e.g. "0-3")
        cpuset.mems             <- allowed NUMA nodes
    blkio/
      container-abc/
        blkio.throttle.read_bps_device   <- read bandwidth limit
    pids/
      container-abc/
        pids.max                <- max processes
        
  v1 Problem: different process in different subsystem hierarchies
    Difficult to atomically limit CPU + memory + I/O together
    Docker workaround: creates same hierarchy in each subsystem
```

---

### cgroups v2 Architecture

```
cgroups v2: single unified hierarchy (Linux 4.5+, 2016)
  
  /sys/fs/cgroup/
    user.slice/
    system.slice/
      containerd.service/
        kubepods.slice/
          besteffort/
            pod-abc-123/
              container-def/
                memory.max     <- hard limit
                memory.current <- current usage
                memory.swap.max <- swap limit
                cpu.max        <- "quota period" format: "200000 100000"
                io.max         <- I/O limits
                cgroup.controllers  <- available controllers
    
  v2 advantages:
    Unified hierarchy: any process is in exactly ONE cgroup
    Better accounting: all resources tracked together
    Memory protection: memory.min (guaranteed minimum)
    CPU burst mode: cpu.burst_us
    Pressure metrics: memory.pressure, cpu.pressure, io.pressure
    
  memory.pressure (v2 new feature):
    Reports: time processes spent waiting for memory
    Some, Full levels: granular pressure signals
    Enables: proactive scaling before OOM (vs reactive OOM kill)
    
Kubernetes and cgroups v2:
  Kubernetes 1.25+: cgroups v2 used by default (on v2-enabled nodes)
  Check: cat /sys/fs/cgroup/cgroup.controllers
  If v2: output like "cpuset cpu io memory hugetlb pids rdma"
  If v1: /sys/fs/cgroup/ has separate subdirs per controller
```

---

### CPU Throttling and CFS Bandwidth Control

```
Docker: --cpus=2 for a service
  
  Sets:
    cpu.cfs_quota_us = 200000 (200ms of CPU per period)
    cpu.cfs_period_us = 100000 (100ms period)
    
  Meaning: container gets 200ms of CPU every 100ms period
  = 2 "virtual CPUs" worth of CPU time
  
  Throttling mechanism:
    At start of period: quota = 200ms
    Container runs: depletes quota (e.g. 8 threads x 25ms = 200ms)
    Quota exhausted: THROTTLED (all container threads cannot run)
    Wait: until next 100ms period starts
    Result: container appears paused for remainder of period
    
  Java problem: GC + application = spiky CPU usage
    GC: suddenly needs 8 cores for 50ms
    With --cpus=2: quota = 200ms per 100ms period
    GC uses: 8 cores x 12.5ms = 100ms quota in one burst
    Application needs: remaining 100ms for the period
    But: 100ms just for GC = quota used up quickly
    Result: GC + application causes throttling -> latency spike
    
  Detection:
    cat /sys/fs/cgroup/cpu/container-name/cpu.stat
    # nr_throttled: number of periods throttled
    # throttled_time: total nanoseconds throttled
    
    Prometheus: container_cpu_cfs_throttled_seconds_total
    Alert: throttled_seconds increasing > 5% of total
    
  Fix: increase CPU limit or reduce GC pause time
    Option: -XX:GCPauseIntervalMillis - reduce GC burst length
    Option: G1GC concurrent work: uses less CPU in burst
    Option: increase cpus limit (--cpus=4 instead of 2)
```

---

### Memory Limits and Java

```
cgroup memory.limit_in_bytes = 4GB
  
Java < 8u191 (containers not detected):
  Reads /proc/meminfo: shows HOST memory (e.g. 128GB)
  Sets: -Xmx based on 128GB host
  Result: JVM heap can grow to 32GB (1/4 of 128GB by default)
  Container cgroup: kills process at 4GB
  SIGKILL: Java never printed OOM; just disappeared
  Fix: set explicit -Xmx or upgrade to Java 11+
  
Java 11+ (UseContainerSupport=true by default):
  Reads: /sys/fs/cgroup/memory/memory.limit_in_bytes
  Sets: default heap = max(MinRAMPercentage, initial settings)
    -XX:MaxRAMPercentage=75 -> 3GB heap out of 4GB limit
    Remaining 1GB for: metaspace, code cache, threads, native
    
  Verify container awareness:
    java -XX:+PrintFlagsFinal -version | grep UseContainerSupport
    java -XX:+PrintFlagsFinal -version | grep MaxRAMPercentage
    
  Also check: number of CPU cores seen by JVM
    Runtime.getRuntime().availableProcessors()
    # Without container awareness: returns HOST cores (32)
    # With awareness: returns fraction = quota/period
    # --cpus=4: availableProcessors() returns 4
    # JVM thread pools sized correctly: 4 threads, not 32
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Docker containers are isolated by default" | Docker uses BOTH namespaces (for isolation illusion) AND cgroups (for resource limits). But cgroup limits are NOT applied by default without explicit `--memory` and `--cpus` flags. Without limits, a container CAN consume all host memory and CPU, affecting other containers. ALWAYS set resource limits in production. |
| "cgroups v2 and v1 are interchangeable" | They have different file paths, different file names (e.g. `memory.max` in v2 vs `memory.limit_in_bytes` in v1), and different accounting semantics. Java's container support handles both. But monitoring tools, shell scripts, and some orchestrators need version-specific paths. Check which version is running before writing cgroup interaction code. |
| "CPU limit of 2 means 2 CPUs always available" | CPU limit sets a QUOTA, not a reservation. If the container doesn't use its full quota, those cycles are not saved or accumulated (in v1; v2 allows some burst). CPU throttling can cause significant latency spikes for bursty workloads (like GC) even if average CPU usage is below limit. |

---

### Quick Reference Card

| Task | v1 Path | v2 Path |
|------|---------|---------|
| Memory limit | `memory/cg/memory.limit_in_bytes` | `memory.max` |
| Memory usage | `memory/cg/memory.usage_in_bytes` | `memory.current` |
| CPU quota | `cpu/cg/cpu.cfs_quota_us` | `cpu.max` |
| Throttle stats | `cpu/cg/cpu.stat` | `cpu.stat` |
| PID limit | `pids/cg/pids.max` | `pids.max` |
| Allowed CPUs | `cpuset/cg/cpuset.cpus` | `cpuset.cpus` |
| Kubernetes version | v1 (< 1.25) | v2 (1.25+ default) |
| Java detection | `UseContainerSupport` | `UseContainerSupport` |
