---
id: OSY-065
title: CFS Linux Scheduler Internals
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-011
used_by: OSY-099, OSY-120
related: OSY-009, OSY-066, OSY-099
tags:
  - CFS
  - scheduler
  - vruntime
  - red-black-tree
  - Linux-kernel
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/osy/cfs-linux-scheduler/
---

## TL;DR

CFS (Completely Fair Scheduler) is Linux's default task
scheduler (since 2.6.23, 2007). It tracks each task's
"virtual runtime" (vruntime) in nanoseconds and always
runs the task with lowest vruntime - the least-served
task. Uses a red-black tree for O(log N) scheduling.
Niceness adjusts vruntime accumulation rate. cgroups
CPU limits use CFS bandwidth control.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-065 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | CFS, vruntime, red-black tree, cgroups, CPU shares |
| **Prerequisites** | OSY-009, OSY-011 |

---

### CFS Core Algorithm

```
CFS goal: every task gets an "equal share" of the CPU

Virtual runtime (vruntime):
  Tracks how long each task HAS run (nanoseconds, weighted by priority)
  Higher priority (lower nice) -> vruntime accumulates SLOWER
  Lower priority (higher nice) -> vruntime accumulates FASTER
  
  vruntime += actual_runtime * (NICE_0_LOAD / task_weight)
  NICE_0_LOAD: base weight (~1024)
  task_weight: priority-dependent weight (nice -20 -> 88761, nice +19 -> 15)
  
  Result:
    nice 0 task: vruntime += 1.0 * actual_runtime
    nice +19 task: vruntime += ~5.9 * actual_runtime (runs "slower")
    nice -20 task: vruntime += ~0.01 * actual_runtime (runs "faster")
    
Scheduling decision:
  Run-queue: red-black tree sorted by vruntime
  Leftmost node: task with smallest vruntime (least served)
  Pick leftmost -> run for one timeslice -> update vruntime -> re-insert
  
  O(log N): insert/remove from red-black tree
  O(1): find minimum (cached leftmost node)

Timeslice:
  Not fixed; derived from sched_latency and number of runnable tasks
  sched_latency = 6ms (default): if 6 tasks run, each gets 1ms slice
  sched_min_granularity = 0.75ms: minimum quantum (prevents tiny slices)
  /proc/sys/kernel/sched_latency_ns
  /proc/sys/kernel/sched_min_granularity_ns
```

---

### cgroups CPU Bandwidth Control

```
CFS bandwidth (cgroup v2 cpu.max):
  cpu.max: "quota period"
  quota: CPU time (microseconds) this cgroup gets per period
  period: scheduling period (100ms default)
  
  Example: cpu.max = "25000 100000"
    cgroup gets 25ms of CPU per 100ms = 25% CPU cap
  
  When quota is exhausted:
    All tasks in cgroup are throttled until next period
    Throttled tasks: moved to throttled state (not runnable)
    
  Kubernetes resource limits:
    resources:
      limits:
        cpu: "500m"    # 500 millicores = 50% of one CPU
    -> cpu.max = "50000 100000"  (50ms/100ms period)
    
CPU throttling in containers:
  Diagnosed with: container_cpu_cfs_throttled_seconds_total
    (Prometheus/cAdvisor metric)
  When throttled:
    Tasks cannot run even if CPUs are idle!
    This causes latency spikes even on idle servers
    (Request arrives; container is in throttled state for 50-90ms)
    
  This is why CPU limits can INCREASE latency:
    A container with CPU limit 500m on an idle 8-core machine:
    Can be throttled for up to 50ms even if 7 CPUs are free
    Better approach for latency-sensitive apps:
      Set CPU REQUEST (guarantees) without LIMIT
```

---

### Scheduler Tuning for Java

```bash
# View current CFS settings:
cat /proc/sys/kernel/sched_latency_ns        # default 6000000 (6ms)
cat /proc/sys/kernel/sched_min_granularity_ns # default 750000 (0.75ms)
cat /proc/sys/kernel/sched_migration_cost_ns  # default 500000 (0.5ms)

# sched_migration_cost_ns:
#   Time kernel assumes a task is "cache hot"
#   During this time: scheduler avoids migrating task to another CPU
#   Increasing: reduces task migration (good for NUMA)
#   Effect on Java: larger value = JIT-compiled code stays cache-hot longer
#   Tuning for Java: increase to 5ms for long-running compute tasks
#   sysctl -w kernel.sched_migration_cost_ns=5000000

# For low-latency services (high priority):
chrt --set --rr 50 PID   # SCHED_RR, priority 50
# Caution: real-time tasks can starve CFS tasks if they spin!
# Only for: known short bursts (not general Java services)

# View task scheduling information:
cat /proc/PID/sched
# Shows: nr_voluntary_switches (sleep/IO), nr_involuntary_switches (preempted)
# High involuntary switches: task preempted often (too many threads?)
# High voluntary switches: IO-bound or frequently waiting for locks

# numactl + CFS pinning:
taskset -c 0-7 java -jar app.jar  # pin to CPU set (avoids migration)
```

---

### CFS vs Other Schedulers

```
Linux schedulers:
  CFS (SCHED_OTHER): default; all "normal" tasks
    Fair share; vruntime; red-black tree
    
  SCHED_FIFO: real-time; no preemption within priority
    Runs until: blocks, yields, or higher-priority task arrives
    No timeslice; can monopolize CPU if it doesn't yield
    Use: hard real-time (audio, robotics)
    
  SCHED_RR: real-time with round-robin within priority
    Like SCHED_FIFO but with timeslice
    Multiple same-priority tasks: time-share
    
  SCHED_DEADLINE: EDF (Earliest Deadline First)
    Guarantee: each task gets X microseconds every Y microseconds
    Parameters: runtime, deadline, period
    Used for: multimedia, industrial control
    
  SCHED_BATCH: CPU-intensive batch jobs
    Assumes task is compute-bound; longer timeslices
    Does not benefit from interactive bonuses
    
  SCHED_IDLE: lowest possible priority
    Runs only when nothing else is runnable
    Use: background maintenance tasks

Java thread scheduling:
  Java threads mapped to OS threads (NPTL on Linux)
  setpriority() -> maps to nice values on Linux
  All Java threads: SCHED_OTHER (CFS) by default
  High-priority Java thread: lower nice value -> slower vruntime growth
  But: OS scheduler has final say
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CFS gives every task exactly equal CPU time" | CFS ensures fair CPU share WEIGHTED by priority (nice value). A nice 0 task and a nice +19 task running together: the nice 0 task gets ~6x more CPU than the nice +19 task. Equal share only among equal-priority tasks |
| "Kubernetes CPU limits improve fair sharing and are always good" | CPU limits in Kubernetes use CFS bandwidth. When a container exhausts its quota for the period, it is throttled - ALL its tasks stop running until the next period (100ms default). On an idle server, a limited container can experience 50-90ms latency spikes from CFS throttle. CPU requests (not limits) provide fair scheduling without artificial throttling |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| CFS vruntime | Smallest vruntime runs next; niceness adjusts growth rate |
| Data structure | Red-black tree; O(log N) insert; O(1) min (cached) |
| sched_latency_ns | Default 6ms: period for all N tasks to run once |
| K8s cpu.max | CFS bandwidth: quota/period (500m = 50ms/100ms) |
| Throttling | Container exhausts quota -> ALL tasks halted until next period |
| Voluntary vs involuntary | Voluntary = sleeping; involuntary = preempted (too many threads) |
