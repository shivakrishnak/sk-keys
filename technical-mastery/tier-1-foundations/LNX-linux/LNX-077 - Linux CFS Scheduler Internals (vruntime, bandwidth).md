---
id: LNX-077
title: "Linux CFS Scheduler Internals (vruntime, bandwidth)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-022, LNX-072
used_by: LNX-095, LNX-089
related: LNX-022, LNX-072, LNX-076, LNX-095
tags: [cfs, completely-fair-scheduler, vruntime, cpu-bandwidth, scheduling, sched-ext, nice, cgroup-cpu, runqueue, red-black-tree, throttling]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/lnx/linux-cfs-scheduler/
---

## TL;DR

**CFS** (Completely Fair Scheduler) is Linux's default CPU scheduler since
kernel 2.6.23. Core idea: track **virtual runtime (vruntime)** per task -
the amount of CPU time a task has "used" (weighted by priority). Always
run the task with the smallest vruntime (least-served). Data structure:
**red-black tree** sorted by vruntime (O(log n) insert/pick). `nice` values
adjust weight (nice -20 = 4x higher weight than nice 0). **CFS bandwidth**
(cgroup cpu.max): hard CPU limit via quota/period (100ms default period);
processes SLEEP if quota exhausted - causes latency spikes. Monitor throttling:
`cpu.stat nr_throttled`. Key sysctls: `sched_latency_ns`, `sched_min_granularity_ns`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-077 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | CFS, vruntime, bandwidth throttling, nice, cgroup cpu, red-black tree, scheduler, sched_latency |
| **Prerequisites** | LNX-022 (Process management), LNX-072 (cgroups) |

---

### The Problem This Solves

**Problem 1**: A system runs a web server (needs fast response) and a
batch job (CPU intensive). With equal priority: the batch job monopolizes
CPUs, the web server responses are slow. With CFS nice values: batch job
gets nice +15 (lower priority), web server stays at nice 0. CFS gives
the web server proportionally more CPU time under contention. When the
batch job is alone: it gets 100% CPU (no waste).

**Problem 2**: Kubernetes sets `cpu.max = 50000 100000` (500 millicores)
for a container. The container's application has a 10ms request handler
that briefly uses 100% of one CPU. In a 100ms period: the container uses
up to 50ms of CPU. If the handler runs at the END of a period and uses 15ms,
it gets throttled after 10ms (remaining quota), sleeps 90ms (rest of period),
resumes with fresh quota. Result: 100ms latency for a 15ms operation.
This is the CFS bandwidth throttling problem.

---

### Textbook Definition

**CFS (Completely Fair Scheduler)**: The default Linux process scheduler
(replacing the O(1) scheduler in kernel 2.6.23, 2007). Models an "ideal
multi-tasking CPU" - each of N runnable tasks gets exactly 1/N of CPU time.
Approximates this ideally using weighted virtual time.

**Key concepts:**
- **vruntime**: virtual runtime - CPU time used by a task, adjusted by weight. Low vruntime = task has been underserved -> should run next
- **Weight**: derived from `nice` value. nice 0 = weight 1024. nice -20 = weight 88761 (86x more). nice +19 = weight 15
- **Run queue (rq)**: per-CPU data structure. Contains: red-black tree of runnable tasks sorted by vruntime, current task (running task), statistics
- **sched_latency_ns**: target scheduling latency (default: 6ms on modern kernels, 24ms was old default). Time for each runnable task to get at least one time slice
- **sched_min_granularity_ns**: minimum time slice per task (default: 0.75ms). Even high-priority tasks run this long before preemption

**CFS bandwidth (group scheduling):**
- **cpu.weight**: relative share (cgroup v2). Proportional to nice weight
- **cpu.max**: hard limit. Format: `quota_us period_us`. "50000 100000" = 50ms per 100ms = 50% of one CPU
- **Throttling**: when cgroup's CPU quota is exhausted in a period, ALL tasks in that cgroup are throttled (sleep until next period)

---

### Understand It in 30 Seconds

```bash
# === CFS scheduling info for a process ===
# View scheduling parameters:
chrt -p <PID>    # scheduling policy and priority
# sched policy: SCHED_OTHER (= CFS), SCHED_FIFO, SCHED_RR, SCHED_DEADLINE

# Nice value:
ps -o pid,ni,comm -p <PID>
# PID  NI COMMAND
# 1234  0 nginx       <- nice 0 (normal priority)
# 5678 15 backup      <- nice +15 (lower priority)

# Scheduling stats for a process (Linux 4.13+):
cat /proc/<PID>/sched | head -20
# Interesting fields:
# nr_voluntary_switches:    1234  <- voluntary CPU yield count
# nr_involuntary_switches:  567   <- preempted by scheduler
# wait_sum:                 1234  <- total time waiting to run (ns)

# === Set nice value ===
nice -n 15 tar -czf backup.tar.gz /data/    # run new command at nice +15
renice -n 10 -p 1234                         # change nice for existing PID
renice -n 10 -g <PGRP>                       # change nice for process group

# === CPU scheduling policy ===
# CFS (default): fair, preemptable, weighted by nice
# SCHED_FIFO: real-time, first-in first-out, NOT preemptable (dangerous!)
# SCHED_RR: real-time, round-robin, preemptable with fixed slice
# SCHED_DEADLINE: real-time, earliest-deadline-first (for latency-critical)

# Set SCHED_FIFO (needs root):
chrt -f -p 50 <PID>   # FIFO with priority 50
# Set back to CFS:
chrt -o -p 0 <PID>    # SCHED_OTHER (CFS) priority 0

# === CFS bandwidth throttling (cgroup cpu.max) ===
# Find container cgroup:
CGPATH=$(cat /proc/<PID>/cgroup | grep '^0::' | cut -d: -f3)

# Check CPU limit:
cat /sys/fs/cgroup$CGPATH/cpu.max
# 50000 100000   <- 50ms quota per 100ms period = 50% CPU

# Check throttling statistics:
cat /sys/fs/cgroup$CGPATH/cpu.stat
# usage_usec 50000000      <- 50s total CPU time
# user_usec 30000000
# system_usec 20000000
# nr_periods 500           <- 500 scheduling periods elapsed
# nr_throttled 100         <- 100 periods where quota was exhausted
# throttled_usec 5000000   <- 5s of throttle time total

# Throttled percentage:
# 100 / 500 = 20% of periods throttled = significant!

# === CFS tuning ===
# Scheduling latency (how long before all tasks get a turn):
cat /proc/sys/kernel/sched_latency_ns    # default: 6000000 (6ms)
cat /proc/sys/kernel/sched_min_granularity_ns  # default: 750000 (0.75ms)

# These control the scheduler's fairness granularity:
# Lower sched_latency: more preemptions, lower latency, higher context-switch overhead
# Higher sched_latency: fewer context switches, higher throughput, higher latency

# For interactive workloads (low latency):
# sysctl -w kernel.sched_latency_ns=2000000    # 2ms
# sysctl -w kernel.sched_min_granularity_ns=500000   # 0.5ms

# For batch throughput (minimize context switches):
# sysctl -w kernel.sched_latency_ns=24000000   # 24ms
# sysctl -w kernel.sched_min_granularity_ns=3000000  # 3ms

# === Performance: view scheduler stats ===
cat /proc/schedstat    # global scheduler stats
# Format varies, use perf instead:
perf sched record -- sleep 10
perf sched latency | head -20    # per-task scheduling latency
```

---

### First Principles

**How CFS picks the next task to run:**
```
State: 5 runnable tasks on CPU 0

Red-black tree (sorted by vruntime):
       [B: 100ms]
      /           \
  [A: 80ms]    [D: 120ms]
  /                 \
[C: 60ms]          [E: 150ms]

Leftmost node = smallest vruntime = most "underserved" task
Scheduler always picks leftmost: C (60ms)

C runs. Its vruntime increases by (time_slice * weight_normalization):
  C has nice +5: weight = 335 (vs 1024 for nice 0)
  C runs for 0.75ms (min_granularity)
  actual_time = 0.75ms
  delta_vruntime = actual_time * (NICE_0_LOAD / task_weight)
                 = 0.75ms * (1024 / 335) = 2.29ms
  C's vruntime: 60 + 2.29 = 62.29ms

C is reinserted into tree. Pick next leftmost: A (80ms)
A has nice 0 (weight 1024):
  delta_vruntime = 0.75ms * (1024/1024) = 0.75ms
  A's vruntime: 80.75ms

Pick next: C (62.29ms) is still smallest! C gets more turns.

RESULT:
  C (nice +5, lower weight 335) accumulates vruntime 3x faster than A (nice 0, weight 1024)
  For every 3 units of vruntime A accumulates, C accumulates 1 unit
  -> C runs 3x less than A (lower weight = proportionally less CPU)

Fairness achieved: proportional to weight (nice value)

CPU LOAD:
  nice -20: weight = 88761 (accumulates vruntime SLOWLY = runs often)
  nice  0:  weight = 1024  (baseline)
  nice +19: weight = 15    (accumulates vruntime QUICKLY = runs rarely)
```

**CFS bandwidth throttling mechanics:**
```
Setup: cgroup with cpu.max = "50000 100000" (50ms/100ms period = 500m)

Timeline (one 100ms period):

t=0ms:   Period starts. Quota pool = 50ms
t=0ms:   Process A starts, uses CPU
t=10ms:  Process A used 10ms. Quota pool = 40ms
t=20ms:  Process A used 20ms. Quota pool = 20ms  
t=30ms:  Process A used 30ms. Quota pool = 20ms
t=40ms:  Process A used 10ms MORE (total 30ms). Quota pool = 20ms
t=50ms:  Process A uses LAST 20ms of quota. Quota pool = 0ms
         THROTTLE! Process A marked as THROTTLED
         Moves to throttled list, removed from runqueue
         Effective: process is SLEEPING (not getting any CPU)
t=50ms: t=100ms: Process A: THROTTLED, sleeping for 50ms
t=100ms: New period starts! Quota pool = fresh 50ms
         Process A UNTHROTTLED, added back to runqueue
         
Applications see:
  Request arrives at t=45ms:
    Process starts handling at t=45ms (in runqueue)
    Process uses 5ms of CPU (t=45ms-t=50ms)
    THROTTLED at t=50ms (quota exhausted)
    Process resumes at t=100ms
    Finishes at t=103ms (3ms remaining work)
    Total latency: 103ms - 45ms = 58ms
    (for 8ms of actual work!)

This is the "CFS bandwidth throttling problem" for latency-sensitive apps.
The 100ms period means spikes can be up to 100ms long.
```

---

### Thought Experiment

Diagnosing CPU throttling in a Kubernetes cluster:

```bash
#!/bin/bash
# Script to find throttled containers in a Kubernetes node

# For each container on this node:
for cgpath in /sys/fs/cgroup/kubepods*/*/*; do
    if [[ -f "$cgpath/cpu.stat" ]]; then
        nr_periods=$(grep nr_periods "$cgpath/cpu.stat" | awk '{print $2}')
        nr_throttled=$(grep nr_throttled "$cgpath/cpu.stat" | awk '{print $2}')
        
        [[ "$nr_periods" -gt 0 ]] || continue
        
        throttle_pct=$((nr_throttled * 100 / nr_periods))
        
        if [[ $throttle_pct -gt 5 ]]; then   # >5% throttle = investigate
            # Find container ID from cgroup path:
            container_id=$(basename "$cgpath" | grep -o '[a-f0-9]\{64\}')
            echo "THROTTLED: $container_id (${throttle_pct}%)"
            echo "  cpu.max: $(cat "$cgpath/cpu.max")"
            echo "  cpu.stat: $cgpath/cpu.stat"
        fi
    fi
done

# Resolution options:
# 1. Increase cpu.max (more quota per period):
# kubectl patch deployment myapp -p '{"spec":{"template":{"spec":{"containers":[{"name":"myapp","resources":{"limits":{"cpu":"2000m"}}}]}}}}'

# 2. Remove CPU limits entirely (use cpu.weight/requests only):
# kubectl patch deployment myapp --type='json' \
#   -p='[{"op": "remove", "path": "/spec/template/spec/containers/0/resources/limits/cpu"}]'

# 3. Increase CFS period (less frequent throttle checks, larger burst):
# --cpu-cfs-period=50ms  <- kubelet flag (halve period = less severe throttle window)

# 4. For Java: add -XX:+AlwaysPreTouch, optimize GC to avoid CPU spikes
```

---

### Mental Model / Analogy

```
CFS = a very fair board game moderator

Board game = CPU time
Players = runnable processes (tasks)
Turn counter (vruntime) = how much CPU each player has "used" so far

Rule: the player who has taken the LEAST total turns gets to go next
      (adjusted for their "priority cards" / nice value)

Priority cards (nice values):
  Server process (nice -10): each turn only counts as 0.5 turns
    -> they run more often (their turn counter fills slower)
  Normal process (nice 0): each turn counts as 1 turn
  Batch job (nice +10): each turn counts as 2 turns
    -> they run less often (turn counter fills faster)

When multiple players want to go: pick lowest turn count
  Player A: turn count = 100 (nice 0, ran a lot recently)
  Player B: turn count = 80 (nice 0, ran less)
  Player C: turn count = 40 (nice +10, big batch job but ran less)
  
  Despite C being lower priority: C's count is lowest -> C goes next
  This prevents starvation: even low priority tasks EVENTUALLY run

Red-black tree = leaderboard sorted by turn count:
  Always pick the player at the BOTTOM of the leaderboard
  O(log n) to find bottom (efficient even with many tasks)

CFS bandwidth (cpu.max) = game time limit per round:
  Round = 100ms period
  Budget = 50ms quota (50ms of turns allowed per round)
  
  When budget runs out (at 50ms in round):
    ALL players in your group must SIT OUT until next round
    (throttled: sleep until period resets)
    
  This is why CPU limits cause latency spikes:
    Mid-game, your group gets forced to sit out for up to 100ms
    Even if other groups are idle and the "game" could continue
    
  Budget-only (cpu.weight, no cpu.max) = no forced sit-outs:
    Under contention: lower weight groups play fewer turns
    No contention: all groups play as many turns as they want
```

---

### Gradual Depth - Five Levels

**Level 1:**
CFS as a fair scheduler: each task gets proportional CPU share. `nice` value
adjusts priority. `ps -o ni` to see nice values. `renice` to change. vruntime
concept (least-served runs first). Scheduling policy: SCHED_OTHER (CFS) vs
SCHED_FIFO vs SCHED_RR.

**Level 2:**
Red-black tree sorted by vruntime. Weight table (nice to weight mapping).
`sched_latency_ns` and `sched_min_granularity_ns`. CFS bandwidth: cpu.max quota/period.
Throttling: nr_throttled in cpu.stat. Kubernetes CPU requests (weight) vs limits
(bandwidth). CPU stealing in VMs (steal time in `vmstat`).

**Level 3:**
Group scheduling (cgroups + CFS): hierarchical fairness. Task migration between
CPUs (load balancing). NUMA scheduling: topology-aware task placement. CPU
affinity: `taskset`, `sched_setaffinity`. `perf sched` for scheduling analysis.
`sched_wakeup_granularity_ns`: wakeup preemption threshold. The "big.LITTLE"
scheduler for heterogeneous CPUs.

**Level 4:**
CFS internals: `struct sched_entity`, `sched_vslice`, `calc_delta_fair`.
Load balancing algorithm: `load_balance()`, migration threshold, imbalance
detection. PELT (Per-Entity Load Tracking): CPU utilization tracking with
exponential decay. Energy-aware scheduling (EAS) for mobile/arm. Idle CPU
injection and wake-up preemption. `sched_latency_ns` interaction with CFS
period in Kubernetes (CPU throttling problem).

**Level 5:**
sched_ext (BPF-based scheduler, kernel 6.6+): write custom CFS replacement
in BPF. CFS vs EEVDF (Earliest Eligible Virtual Deadline First, kernel 6.6):
EEVDF improves on CFS for latency-sensitive workloads. The Rotating Staircase
Deadline Scheduler (RSDL) as an alternative design. CFS scheduling in
heterogeneous clusters (NUMA + big.LITTLE). Deadline scheduling
(`SCHED_DEADLINE`): CBS (Constant Bandwidth Server), GEDF, runtime/deadline/
period parameters.

---

### Code Example

**BAD - CPU throttling mistakes:**
```bash
# BAD 1: Equal CPU limits and requests in Kubernetes (common but harmful):
# resources:
#   requests:
#     cpu: "500m"
#   limits:
#     cpu: "500m"   # limits = requests
#
# With 500m limit: cpu.max = "50000 100000" (50ms/100ms period)
# A Java GC pause uses 80ms of CPU: exceeds 50ms quota
# Result: GC thread throttled mid-pause -> pause lasts 100+ ms
# -> Missed SLA for a 50ms SLO

# Diagnosis:
cat /sys/fs/cgroup/..../cpu.stat | grep -E "nr_(periods|throttled)"
# nr_periods 1000
# nr_throttled 350    <- 35% throttled! Much higher than expected

# BAD 2: Running database at nice 0 with batch job at nice 0:
# Both get equal CPU share under contention
nice /usr/bin/backup.sh &       # nice 0 = same as database!
# Database requests now compete equally with backup
# p99 latency degrades 30-50% during backup

# GOOD 2: Give backup lower priority:
nice -n 15 /usr/bin/backup.sh &   # nice +15 = 1/6 the weight of nice 0
# Under CPU contention: database (nice 0) gets ~6x more CPU than backup
# When CPU is idle: backup runs at full speed (no waste)

# BAD 3: Setting SCHED_FIFO on a non-critical process:
chrt -f -p 99 my_app   # FIFO priority 99
# SCHED_FIFO is non-preemptable by normal CFS processes!
# If my_app spins in a tight loop: system becomes UNRESPONSIVE
# Only use SCHED_FIFO for real-time audio, kernel threads
```

**GOOD - CPU scheduling for production:**
```bash
# GOOD: Kubernetes CPU configuration for latency-sensitive service
# Use requests (weight/priority) WITHOUT limits (no throttling):
# resources:
#   requests:
#     cpu: "500m"    # cpu.weight proportional to 500m
#   # NO limits.cpu  <- avoid throttling entirely
#
# This gives the container priority during contention (500m weight)
# without hard limits that cause throttling during bursts

# GOOD: Monitor CFS throttling in Kubernetes:
check_throttling() {
    local pod=$1
    local namespace=${2:-default}
    
    # Get container PID:
    local pod_uid=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.metadata.uid}')
    local cg_path="/sys/fs/cgroup/kubepods*/*/*${pod_uid}*"
    
    for cg in $(ls -d $cg_path 2>/dev/null | head -1); do
        echo "=== $pod CPU stats ==="
        cat "$cg/cpu.stat"
        echo ""
        
        local nr_p=$(grep nr_periods "$cg/cpu.stat" | awk '{print $2}')
        local nr_t=$(grep nr_throttled "$cg/cpu.stat" | awk '{print $2}')
        
        if [[ "$nr_p" -gt 0 ]]; then
            echo "Throttle rate: $((nr_t * 100 / nr_p))%"
        fi
    done
}

check_throttling myapp

# GOOD: Run batch job with appropriate nice + ionice:
# CPU priority (nice) + I/O priority (ionice best-effort class 2):
nice -n 15 ionice -c 2 -n 7 ./batch_job.sh
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "CFS tasks with different nice values run in proportion at all times" | Nice values create RELATIVE weights, and proportional allocation only applies UNDER CONTENTION. When a nice +19 process is the only runnable task: it gets 100% CPU. Nice values only affect relative scheduling when multiple tasks are competing for the same CPU. Additionally: vruntime normalization means even very low-priority tasks (nice +19) WILL get CPU time eventually, preventing complete starvation. The relationship is: `nice -20` gets ~86x more CPU than `nice +19` WHEN BOTH ARE RUNNABLE. |
| "CPU limits in Kubernetes are just nice values" | CPU limits (cpu.max) are CFS BANDWIDTH LIMITS, not nice values. They use a completely different mechanism: quota exhaustion causes throttling (sleep until next period). Nice values only affect RELATIVE scheduling among runnable tasks. cpu.max makes tasks UNRUNNABLE for up to 100ms when quota is exhausted. This is why CPU limits can cause latency spikes even when the host has idle CPUs: the container is throttled regardless of system-level CPU availability. CPU requests (cpu.weight) are like nice values - only affect relative priority under contention. |
| "The CFS scheduler runs on a fixed time quantum (like old schedulers)" | CFS doesn't use fixed time quanta. The time slice is variable and depends on: number of runnable tasks, their weights, and the `sched_latency_ns` and `sched_min_granularity_ns` settings. With 10 tasks at nice 0: each gets `sched_latency_ns/10` = 0.6ms per pass (at 6ms latency). With 2 tasks: each gets 3ms per pass. With 100 tasks: each gets `sched_min_granularity_ns` = 0.75ms (minimum). This is why CFS adapts to load: more tasks = shorter slices = same target latency regardless of task count. |
| "Setting SCHED_FIFO improves performance for most applications" | SCHED_FIFO is a REAL-TIME scheduling class that is NON-PREEMPTABLE by normal CFS tasks. A SCHED_FIFO task runs until it voluntarily yields, blocks on I/O, or is preempted by a HIGHER priority SCHED_FIFO task. If a SCHED_FIFO task spins in a tight CPU loop: the system appears frozen for normal processes. Use cases for SCHED_FIFO: kernel real-time threads (ksoftirqd), real-time audio processing (JACK), hardware interrupt handlers. For regular applications including databases: CFS with appropriate nice values or cgroup cpu.weight is the correct tool. |

---

### Failure Modes & Diagnosis

**CPU scheduling issue diagnosis:**
```bash
# Symptom: Process is slow but CPU usage looks low

# Step 1: Is the process being throttled?
# Find cgroup:
cat /proc/<PID>/cgroup | grep '^0::'
# Get cpu.stat:
cat /sys/fs/cgroup/<path>/cpu.stat
# Check: throttled_usec / total_wall_time = throttle fraction

# Step 2: Is the process waiting for CPU (run queue latency)?
# Check run queue depth:
vmstat 1 5
# r: number of processes RUNNABLE but waiting for CPU
# If r > number of CPUs consistently: CPU contention

# Detailed per-process scheduling latency:
perf sched record -p <PID> -- sleep 10
perf sched latency

# Step 3: Is nice value appropriate?
ps -o pid,ni,comm -p <PID>
# If a high-priority service is at nice 0 competing with nice 0 batch jobs:
renice -n 15 -p <batch_job_pid>

# Symptom: p99 latency spikes every 100ms (CFS period)
# Classic CFS throttling pattern:
# Step 1: Confirm throttling:
cat /sys/fs/cgroup/<path>/cpu.stat | grep -E "nr_throttled|throttled_usec"
# High values: confirmed

# Step 2: Measure severity:
nr_throttled=$(grep nr_throttled /sys/fs/cgroup/<path>/cpu.stat | awk '{print $2}')
nr_periods=$(grep nr_periods /sys/fs/cgroup/<path>/cpu.stat | awk '{print $2}')
echo "Throttle rate: $((nr_throttled * 100 / nr_periods))%"

# Step 3: Fix - options:
# Option A: Increase cpu.max (more quota):
echo "100000 100000" > /sys/fs/cgroup/<path>/cpu.max   # 1 full CPU
# Option B: Remove limits (use weight only):
echo "max" > /sys/fs/cgroup/<path>/cpu.max   # unlimited
# Option C: Reduce CFS period (shorter throttle windows):
# kubelet: --cpu-cfs-period=50ms  (50ms instead of 100ms)
```

---

### Related Keywords

**Foundational:**
LNX-022 (Process management), LNX-072 (cgroups)

**Builds on this:**
LNX-095 (CPU performance profiling), LNX-089 (Real-time scheduling)

**Related:**
LNX-076 (I/O schedulers), LNX-083 (OOM Killer)

---

### Quick Reference Card

| Concept | Tool/File | Notes |
|---------|-----------|-------|
| Nice value | `ps -o ni`, `renice` | 0=normal, -20=highest, +19=lowest |
| Scheduling policy | `chrt -p PID` | OTHER=CFS, FIFO/RR=real-time |
| CPU limit | `cpu.max` in cgroup | quota_us period_us |
| Check throttling | `cpu.stat nr_throttled` | High = CPU limit issue |
| Run queue | `vmstat r column` | r > CPUs = CPU contention |
| Scheduling latency | `sched_latency_ns` | Default 6ms |

**3 things to remember:**
1. vruntime = fairness clock: lowest vruntime runs next; nice values slow/speed up vruntime accumulation
2. CPU throttling (cpu.max) causes latency spikes - check `nr_throttled` in `cpu.stat`; consider removing CPU limits for latency-sensitive services
3. `vmstat` `r` column > number of CPUs = CPU contention (not throttling)

---

### Transferable Wisdom

CFS concepts map directly to: Kubernetes CPU resources: `requests.cpu` =
`cpu.weight` (relative priority), `limits.cpu` = `cpu.max` (bandwidth limit,
causes throttling). Java GC impact: GC pauses that burst CPU usage can trigger
CFS throttling if CPU limits are set too low. The vruntime concept (virtual
clock that advances differently per task based on weight) appears in weighted
fair queuing in networking (`tc fq` qdisc), weighted round-robin load balancers,
and token bucket rate limiters. The CFS group scheduling hierarchy mirrors
the Kubernetes resource quotas and LimitRanges: namespace quota -> pod -> container,
each level of cgroup hierarchy has its own scheduler entity. The CFS bandwidth
throttling problem (why CPU limits cause latency spikes) is a fundamental
insight for Kubernetes cluster optimization: many production SREs and platform
engineers explicitly recommend NOT setting CPU limits on latency-sensitive
workloads. Understanding the 100ms CFS period and how it creates throttling
windows explains why this recommendation exists.

---

### The Surprising Truth

The Completely Fair Scheduler's "virtual runtime" concept was inspired by
game theory and the theory of fair resource allocation, not traditional
OS scheduling theory. Ingo Molnar (CFS author) designed it in 2007 to
replace the O(1) scheduler, which had well-known fairness problems. The
key insight: instead of asking "who has the highest priority?" (priority-based),
ask "who has used the LEAST CPU?" (deficit-based). This trivial reframing
eliminated an entire class of starvation problems and made the scheduler
self-tuning with load. The red-black tree (O(log n)) seemed unnecessary when
most production systems had <100 runnable tasks, but Molnar correctly predicted
that as systems scaled (containers, microservices), the O(n) scheduler would
become a bottleneck. Today with Kubernetes nodes running 100+ containers:
the red-black tree design is critical. The CFS bandwidth throttling problem
(that cpu.max causes latency spikes) was not anticipated in 2007 and emerged
as containers became the dominant deployment model. It's a case where a
correct implementation of a correctly-specified interface (hard CPU limits)
produced unexpected behavior at scale. The Kubernetes community's evolving
recommendations (avoid CPU limits, use requests only) represent a community-
level understanding of CFS internals applied to production operations.

---

### Mastery Checklist

- [ ] Understands vruntime: lowest vruntime = runs next, nice adjusts accumulation rate
- [ ] Can use `renice` and `chrt` to adjust process scheduling priorities
- [ ] Understands CFS bandwidth throttling: cpu.max causes sleeping, check `nr_throttled`
- [ ] Can use `vmstat r` to detect CPU contention vs `cpu.stat` to detect throttling
- [ ] Knows the Kubernetes implication: CPU limits (cpu.max) cause latency, consider removing for latency-sensitive services

---

### Think About This

1. A Java application running in Kubernetes has CPU request = limit = "1000m"
   (1 CPU). The application uses a thread pool of 100 threads. During a peak
   request burst, all 100 threads briefly run Java GC. Using your knowledge
   of CFS bandwidth throttling: (a) explain why the 1000m limit might cause
   a GC pause much longer than expected, (b) calculate the maximum additional
   latency the 100ms CFS period could add, (c) propose two solutions that
   address the root cause differently.

2. On a 4-CPU server, you have 3 services: web (nice 0, important), batch (nice
   +15, background), and analytics (nice +10, medium priority). During peak
   load, all 3 are CPU-bound. Calculate the approximate CPU allocation for each
   service using nice-to-weight mapping (nice 0 = weight 1024, nice +10 ≈ weight
   110, nice +15 ≈ weight 36). Then explain what happens when the batch job
   is the ONLY running service - does it get 100% CPU despite nice +15?

3. You're debugging why a latency-sensitive service has p99 = 50ms when
   average is 2ms. The spikes happen every 100ms like clockwork. Outline the
   complete diagnosis procedure (checking throttling vs CPU contention vs
   garbage collection vs I/O wait), the specific kernel files/commands you'd
   examine, and how you'd identify which root cause it is.

---

### Interview Deep-Dive

**Foundational:**
Q: How does the Linux CFS scheduler achieve fairness, and what role does vruntime play?
A: CFS (Completely Fair Scheduler) achieves fairness through the concept of virtual runtime (vruntime). The core idea: instead of giving each task a fixed time slice, track how much CPU time each task has received (adjusted by weight). The task that has received the LEAST CPU is always scheduled next. Mechanism: each task has a `vruntime` counter that accumulates as it runs. When a task runs for delta_t nanoseconds at `nice 0` (weight 1024): vruntime += delta_t. When a higher priority task (nice -10, weight 3121) runs: vruntime += delta_t * (1024/3121) = delta_t * 0.33. The higher-priority task's vruntime increases MORE SLOWLY - meaning it appears "less served" more quickly and gets scheduled more often. Data structure: the kernel keeps all runnable tasks in a red-black tree sorted by vruntime. O(log n) to insert a task. O(1) to find the minimum (leftmost node in the tree = task to schedule next). When a task runs: update its vruntime, reinsert into tree. Pick leftmost. The result: over any period of time, each task receives CPU proportional to its weight. Nice -20 gets 86x more CPU than nice +19 WHEN BOTH ARE RUNNABLE. When a low-priority task is the only runnable task: it gets 100% CPU (no waste). Starvation prevention: new tasks start with vruntime close to the minimum in the tree (not 0), preventing a burst of CPU at the expense of existing tasks. The fairness property: take any time window T. Each task with weight W_i receives (W_i / sum(W_j)) * T seconds of CPU. This is exactly "proportional fair scheduling" in theory, approximated in practice.

**Expert:**
Q: Explain CFS bandwidth throttling, why it causes latency spikes in Kubernetes, and what the recommended mitigations are.
A: CFS bandwidth control (cpu.max in cgroup v2) implements a token bucket algorithm: a cgroup gets a CPU quota (in microseconds) per period (100ms by default). When the quota runs out, ALL tasks in the cgroup are throttled - they're removed from the run queue and sleep until the next period. WHY SPIKES: Consider a cgroup with `cpu.max = 50000 100000` (50ms quota, 100ms period). Normal operation: process uses 40ms per 100ms period, no throttle. Spike scenario: a request arrives at t=90ms of the period. The process has used 45ms of quota. The request needs 10ms of CPU. Processes runs 5ms (t=90ms to t=95ms), uses remaining 5ms of quota. THROTTLED at t=95ms. Sleeps 5ms until t=100ms (period reset). Resumes, runs remaining 5ms. Total latency: 10ms actual work + 5ms sleep = appears as 15ms latency for a 10ms operation. With GC: GC burst needs 80ms. 50ms allowed. 30ms throttled (sleeping through a GC "pause" that's artificially extended by throttle time). KUBERNETES MAGNITUDE: nr_throttled / nr_periods shows throttle rate. Even 5-10% throttle rate causes visible p99 latency degradation. MITIGATIONS: Option 1 - Remove CPU limits (use requests only): eliminates throttling entirely. Container competes with weight (nice-equivalent), no hard cap. Appropriate for latency-sensitive services on nodes with available capacity. Option 2 - Increase limits: if CPU usage legitimately spikes, increase the limit to cover peaks. `cpu.max` = 2x average CPU usage typically. Option 3 - Reduce CFS period: `kubelet --cpu-cfs-period=10ms` (10ms period). Same quota but smaller window = at most 10ms throttle window instead of 100ms. Reduces per-spike impact but increases scheduler overhead. Option 4 - Application tuning: reduce CPU burst (e.g., smaller GC generations, avoid CPU spikes). The community consensus: for latency-sensitive services (p99 < 100ms SLO), avoid CPU limits. For batch workloads (no latency SLO): CPU limits are safe and prevent noisy neighbor.
