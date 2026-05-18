---
id: LNX-060
title: "Process Scheduling Basics (nice, renice, priority)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-006, LNX-007
used_by: LNX-077, LNX-072
related: LNX-077, LNX-006, LNX-072
tags: [CFS, nice, renice, priority, chrt, ionice, taskset, CPU-affinity, real-time, scheduling]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/lnx/process-scheduling-basics/
---

## TL;DR

Linux uses CFS (Completely Fair Scheduler) by default: allocates CPU time
proportionally based on nice values. Nice: -20 (highest priority) to +19
(lowest), default 0. `nice -n 10 cmd` starts with nice 10. `renice -n 5 -p PID`
changes running process. `ionice -c 3 cmd` sets I/O priority (idle class).
`chrt -f 50 cmd` sets real-time FIFO priority (bypasses CFS, preempts normal
processes - use with caution). `taskset -c 2,3 cmd` pins to CPUs 2 and 3.
`numactl --cpunodebind=0 cmd` for NUMA affinity. Cgroups `cpu.shares` for
group-level CPU allocation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-060 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | CFS, nice, renice, ionice, chrt, taskset, numactl, real-time, SCHED_FIFO, CPU-affinity |
| **Prerequisites** | LNX-006 (Processes), LNX-007 (Process Management) |

---

### The Problem This Solves

**Problem 1**: A background batch job (log processing, backup compression)
is competing with the production web server on the same host. By starting
it with `nice -n 15 ./batch-job.sh`, it gets less CPU time than the web
server (which runs at nice 0) when the system is loaded. When the system
is idle, the batch job runs at full speed.

**Problem 2**: An audio processing application stutters because kernel
threads occasionally preempt it for 10-20ms. By running it with
`chrt -f 50 ./audio-app`, it gets real-time FIFO scheduling: it runs
until it voluntarily yields, never preempted by normal processes. Hard
real-time guarantee (with caveats).

---

### Textbook Definition

**CFS (Completely Fair Scheduler)**: Linux default scheduler (SCHED_OTHER
/ SCHED_NORMAL policy). Goal: give each runnable process a fair share of
CPU time, proportional to nice values. Uses a red-black tree of "virtual
runtime" (`vruntime`) values. Process with lowest vruntime runs next.
Weighted by nice value: a process with nice -20 accumulates vruntime
~90x slower than nice +19 (runs ~90x longer proportionally).

**Nice value**: User-visible priority hint for CFS. Range: -20 (highest
CPU priority) to +19 (lowest). Default: 0. Only root can set nice < 0
(increase priority). Regular users can only lower priority (increase nice
value). Maps to weight in CFS scheduler.

**Real-time scheduling** (`chrt`): Separate scheduler for time-critical
processes. Policies:
- `SCHED_FIFO`: First-in, first-out. Runs until it yields/blocks/preempted by higher RT priority. No time slice.
- `SCHED_RR` (round-robin): Like FIFO but with a time slice; within same priority, processes take turns.
- `SCHED_DEADLINE`: Specify deadline, runtime, period. Kernel guarantees periodic deadline scheduling.
Real-time priority: 1-99 (higher = more important). RT processes ALWAYS preempt CFS processes.

**CPU affinity** (`taskset`): Restrict a process to specific CPU cores.
`taskset -c 0,1 cmd`: run cmd on CPUs 0 and 1 only. Improves cache
locality (L1/L2 cache is per-core). Reduces migration overhead.

---

### Understand It in 30 Seconds

```bash
# === View current process priorities ===
ps -eo pid,ni,pri,stat,comm | head -20
# NI = nice value, PRI = kernel priority (internal, not same as nice)
# R = running, S = sleeping, D = uninterruptible sleep

# top view:
top
# PR column: kernel priority, NI column: nice value
# PR=20 with NI=0 is default
# PR=39 with NI=19 is lowest (most deferrable)
# PR<0 or PR=rt: real-time process

# === Nice (CPU priority) ===
# Start with lower priority (nice 10 = below default):
nice -n 10 gzip bigfile.tar
nice -n 19 ./batch-job.sh    # lowest priority (background only)
nice -n -5 ./important-app   # higher priority (requires root)
sudo nice -n -20 ./critical  # max priority (root only)

# Change running process:
renice -n 15 -p 1234          # change PID 1234 to nice 15
renice -n 5 -g 1001           # change entire process group 1001
sudo renice -n -5 -p 1234     # increase priority (root only)

# === I/O Priority (ionice) ===
# Classes: 0=none, 1=realtime, 2=best-effort, 3=idle
ionice -c 3 ./backup-script.sh      # idle class: only runs when disk idle
ionice -c 2 -n 4 ./app             # best-effort, level 4 (0=highest,7=lowest)
ionice -p 1234                      # show I/O class of PID 1234
ionice -c 1 -n 0 -p 1234           # change to RT I/O (root only)

# === Real-time scheduling (chrt) ===
# DANGER: RT processes can starve normal processes and crash system!

# Set FIFO real-time priority 50:
sudo chrt -f 50 ./realtime-app

# Set Round-Robin real-time priority 20:
sudo chrt -r 20 ./rt-app

# Check current scheduling policy:
chrt -p 1234         # show policy and priority for PID

# Change running process to RT:
sudo chrt -f -p 50 1234

# Safety: always set RT watchdog:
# /proc/sys/kernel/sched_rt_period_us   (100ms default)
# /proc/sys/kernel/sched_rt_runtime_us  (95ms default = RT processes get max 95%)
cat /proc/sys/kernel/sched_rt_runtime_us   # 950000 = 95% of CPU for RT

# === CPU Affinity (taskset) ===
# Pin to specific CPU(s):
taskset -c 0 ./app         # CPU 0 only
taskset -c 2,3 ./app       # CPUs 2 and 3
taskset -c 0-3 ./app       # CPUs 0 through 3

# Show/change affinity of running process:
taskset -cp 1234           # show current affinity of PID 1234
taskset -cp 2,3 1234       # pin PID 1234 to CPUs 2 and 3

# Hexadecimal mask (older form):
# taskset 0x06 ./app   = CPUs 1 and 2 (bit mask: 0110 = CPU1, CPU2)

# === NUMA affinity (numactl) ===
numactl --hardware          # show NUMA topology (nodes, CPUs, memory)
numactl --cpunodebind=0 --membind=0 ./app  # bind to NUMA node 0
numactl --preferred=0 ./app               # prefer node 0, allow others

# === Cgroup CPU allocation ===
# For group-level CPU control (systemd service / docker):
systemctl set-property myservice.service CPUShares=512  # lower than default 1024
systemctl set-property webapp.service CPUShares=2048    # 2x default = higher priority
# Or in unit file:
# [Service]
# CPUShares=512   (for cgroups v1)
# CPUWeight=50    (for cgroups v2, 1-10000, default 100)
```

---

### First Principles

**CFS vruntime-based scheduling:**
```
Red-black tree (ordered by vruntime):

     [P4: 100ms]
       /       \
 [P1: 80ms]  [P3: 120ms]
   /
[P2: 70ms]

P2 has the lowest vruntime -> runs next
After P2 runs for 5ms:
  P2's vruntime += 5ms / nice_weight (if nice=0, weight=1024)
  vruntime grows to 75ms (still lowest -> runs again if CPU-bound)
  Or: if P2 blocks (I/O), P1 becomes the lowest -> P1 runs next

Nice value -> CFS weight (kernel-defined table):
  nice -20: weight = 88761
  nice  -5: weight = 6553
  nice   0: weight = 1024  (default)
  nice  +5: weight = 335
  nice +10: weight = 110
  nice +19: weight = 15

CPU time ratio for two processes, nice 0 vs nice 10:
  weight0 / (weight0 + weight10) = 1024 / (1024 + 110) = 90.3%
  weight10 / (weight0 + weight10) = 110 / (1024 + 110) = 9.7%
  -> nice 0 process gets 9x more CPU than nice 10 (when both runnable)
```

**Process priority fields in the kernel:**
```
What shows in /proc/PID/stat field 18+:
  priority: kernel's scheduling priority
    Normal processes (SCHED_OTHER): 20 (nice=0), range 0-39
    Real-time processes: negative values (-1 to -99 for RT 1-99)
    
  nice: the nice value (-20 to +19)
  
  what "top" shows:
  PR column:
    20  = SCHED_NORMAL with nice=0
    39  = SCHED_NORMAL with nice=19
    0   = SCHED_NORMAL with nice=-20
    rt  = real-time (SCHED_FIFO or SCHED_RR)
    
  NI column:
    0   = default
    19  = lowest priority (background)
    -20 = highest (root-set)
    -   = real-time (no nice value)
```

---

### Thought Experiment

Configuring a mixed workload server (web + background jobs):

```bash
# Scenario: shared server running nginx + data pipeline + backups

# Current problem: backup runs at 2am, spikes CPU and I/O,
# causes nginx latency spikes

# Step 1: Check current priorities:
ps -eo pid,ni,stat,comm | grep -E "nginx|backup|pipeline"
# nginx: ni=0, backup: ni=0, pipeline: ni=0
# All competing equally!

# Step 2: Renice the backup processes:
# Find backup PIDs:
pgrep -a backup
# Set to nice 19 + ionice idle class:
for pid in $(pgrep -a backup | awk '{print $1}'); do
    renice -n 19 -p "$pid"
    ionice -c 3 -p "$pid"
    echo "Set $pid to nice 19 + ionice idle"
done

# Step 3: For future backup runs, use nice + ionice from the start:
cat > /etc/cron.d/nightly-backup << 'EOF'
0 2 * * * root nice -n 19 ionice -c 3 /usr/local/bin/backup.sh
EOF

# Step 4: Verify nginx still runs at normal priority:
ps -eo pid,ni,comm | grep nginx
# 1234  0  nginx   <- nice 0, default

# Step 5: If nginx needs to be higher priority on loaded system:
sudo renice -n -5 -p $(pgrep nginx | head -1)
# Or: set in systemd unit file:
# [Service]
# Nice=-5

# Step 6: Monitor the effect:
# During backup window:
watch -n 2 'ps -eo pid,ni,stat,pcpu,comm | sort -k4 -rn | head -10'
# nginx: ni=0, pcpu=high
# backup: ni=19, pcpu=low (only gets CPU when nginx is idle)
# This is the correct behavior
```

---

### Mental Model / Analogy

```
CFS (Completely Fair Scheduler) = airport priority boarding

Everyone in the "normal" queue, ordered by how little they've boarded recently:
  - If you haven't boarded in a long time (low vruntime): you board first
  - After boarding (getting CPU time): you go to the back of the queue
  - Boarding frequency is proportional to your "tier" (nice value)

Nice value = boarding tier:
  nice -20 = First Class: accumulates vruntime 90x slower
            (spends 90x longer at the front of the queue)
  nice  0  = Regular passenger: default tier
  nice +19 = Standby: accumulates vruntime at normal rate
            but has very low "weight" = moves to back quickly

Real-time scheduling (SCHED_FIFO) = emergency crew:
  They DON'T wait in the boarding queue
  They board IMMEDIATELY regardless of who else is waiting
  And they stay on the plane until they're done (no preemption)
  
  DANGER: if an emergency crew member never leaves (RT process in infinite loop),
  they block everyone forever (system freeze!)
  
  RT watchdog: /proc/sys/kernel/sched_rt_runtime_us = 950000
  Means: emergency crew gets at most 95% of time; normal passengers get 5%
  (prevents total starvation)

taskset = dedicated check-in counters
  "CPU 2 and 3 only" = you always go to counters 2 and 3
  Cache benefit: the counter staff (CPU cache) knows you well
  Less context switching overhead

ionice = baggage handling priority
  class 3 (idle) = your bags are moved only when the conveyor belt is empty
  class 1 (RT) = your bags are moved first, always
```

---

### Gradual Depth - Five Levels

**Level 1:**
`nice -n VALUE cmd` for new processes, `renice` for running. Nice range:
-20 to +19 (lower = more CPU). Default 0. Root required for nice < 0.
`ionice -c 3 cmd` for background I/O. `taskset -c N cmd` for CPU affinity.
`ps -eo pid,ni,comm` to view nice values. `top` PR and NI columns.

**Level 2:**
CFS vruntime concept. `chrt -f PRIORITY cmd` for real-time FIFO. Scheduling
policies: SCHED_OTHER (CFS), SCHED_FIFO, SCHED_RR, SCHED_BATCH, SCHED_IDLE.
`chrt -p PID` to check. `SCHED_BATCH`: optimized for batch (no interactive
priority boost). `SCHED_IDLE`: even lower than nice +19 (real idle class).
`cpulimit -p PID -l 50`: limit a process to 50% CPU (not a scheduler, uses SIGSTOP/SIGCONT).

**Level 3:**
Systemd slice/cgroup CPU control: `CPUShares=512` (cgroups v1), `CPUWeight=50`
(cgroups v2). `SCHED_DEADLINE`: specify deadline, runtime, period for periodic
real-time tasks (more predictable than FIFO). `numactl` for NUMA topology.
`taskset` with hex mask vs `-c` format. Kernel preemption models (from
`/boot/config-*`): `PREEMPT_VOLUNTARY` (desktop default), `PREEMPT` (full
preemption), `PREEMPT_RT` (real-time kernel patch).

**Level 4:**
CFS internals: bandwidth control (`cpu.cfs_period_us`, `cpu.cfs_quota_us`).
CPU throttling in containers: `docker --cpu-period=100000 --cpu-quota=25000`
= 25% of one core. Kubernetes `resources.limits.cpu`: maps to cgroup
cpu.cfs_quota_us. CFS group scheduling: each cgroup gets a vruntime and
is scheduled fairly against other cgroups. RT group scheduling: RT fraction
per cgroup. Soft RT: SCHED_FIFO with `ulimit -r 50` (without full root via
`CAP_SYS_NICE`). `thread_affinity` in Java: `Thread.MIN_PRIORITY` to
`Thread.MAX_PRIORITY` map to nice via JVM.

**Level 5:**
RT Linux (`PREEMPT_RT` kernel patch): makes nearly all kernel code preemptible.
Even interrupts are threaded (can be preempted by RT processes). Required
for hard real-time guarantees. Used in industrial control, professional audio
(JACK audio server). `cyclictest`: measures RT scheduling latency.
Intel/AMD hardware support: Intel Speed Step/Core Boost interacts with
scheduling: a core running at 4.5 GHz boost gets "done" with its tasks faster,
reducing context switches. CPU frequency governors: `performance`, `powersave`,
`ondemand` (in `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`).
For latency-sensitive workloads: always use `performance` governor.

---

### Code Example

**BAD - scheduling mistakes:**
```bash
# BAD 1: Running backup/batch at default priority:
# backup.sh runs at nice 0, same as web server
# During backup: web server CPU usage spikes 20-30%
# Users notice latency degradation

# GOOD: always run batch jobs at lower priority:
nice -n 15 ionice -c 2 -n 6 ./backup.sh  # lower CPU + lower I/O priority

# BAD 2: Using SCHED_FIFO for a process that has a bug:
sudo chrt -f 99 ./my-app    # highest RT priority
# If my-app has an infinite loop or hangs:
# ALL other processes starve, including the kernel watchdog
# System becomes completely unresponsive
# Only hard reboot recovers

# GOOD: use lower RT priorities and test thoroughly:
sudo chrt -f 20 ./my-app    # modest RT priority
# Ensure RT watchdog is enabled:
cat /proc/sys/kernel/sched_rt_runtime_us   # should be > 0 (not -1)
# If it's -1, enable:
sysctl -w kernel.sched_rt_runtime_us=950000   # 95% max for RT

# BAD 3: Using cpulimit instead of nice for throttling:
cpulimit -p 1234 -l 30    # limits to 30% CPU
# cpulimit sends SIGSTOP/SIGCONT: causes process to be stopped/started
# repeatedly (not graceful, causes latency spikes in the process itself)

# GOOD: use cgroup cpu quota for clean throttling:
# In systemd unit file:
# [Service]
# CPUQuota=30%   # clean kernel-level quota without SIGSTOP
```

**GOOD - systemd-based CPU control for services:**
```bash
# /etc/systemd/system/webapp.service
# [Unit]
# Description=Web Application
# [Service]
# ExecStart=/usr/bin/java -jar /opt/webapp/app.jar
# Nice=-5               # higher CPU priority
# CPUSchedulingPolicy=batch   # or other
# CPUWeight=200         # cgroups v2: 2x default weight (100)
# IOSchedulingClass=best-effort
# IOSchedulingPriority=2
# [Install]
# WantedBy=multi-user.target

# /etc/systemd/system/backup.service
# [Service]
# ExecStart=/usr/local/bin/backup.sh
# Nice=15               # lower CPU priority
# CPUWeight=25          # 1/4 of default weight
# IOSchedulingClass=idle   # only when disk is idle
# [Install]
# WantedBy=multi-user.target

# Apply changes:
systemctl daemon-reload
systemctl restart webapp backup

# Verify:
systemctl show backup | grep -E "Nice|CPUWeight|IOScheduling"
ps -eo pid,ni,comm | grep backup
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "nice -20 means the process uses 100% CPU" | Nice -20 means the process gets PROPORTIONALLY more CPU time relative to other processes when there is competition. If only one process is running, it gets 100% regardless of nice value. If two processes compete (nice -20 vs nice +19), the -20 process gets ~90% and the +19 gets ~10%. On an idle system, even a nice +19 process runs at full speed. Nice values only matter when CPU is the bottleneck. |
| "Real-time scheduling (SCHED_FIFO) means faster execution" | SCHED_FIFO means the process is NEVER preempted by normal processes. It doesn't mean it runs at higher clock speed. For a CPU-bound process, SCHED_FIFO and SCHED_OTHER with nice -20 give similar throughput. SCHED_FIFO is for LATENCY: ensuring the process gets the CPU within microseconds of becoming runnable, without waiting for CFS scheduling decisions. Used for: audio processing (consistent low latency), industrial control (deterministic response time), NOT for "making my Java app faster." |
| "renice only affects the single process" | `renice` with `-p PID` affects only that process. `renice -g PGID` affects the entire process group (all processes with the same PGID). `renice -u USER` affects all processes owned by USER. When you `renice -n 15 -p` the parent of a multiprocess server, the child processes are NOT affected (they inherit the nice value at fork time, but changing the parent after fork doesn't propagate). Check all threads/children: `ps -eo pid,ppid,ni,comm | grep <name>` to see what's running and at what nice value. |
| "CPU affinity with taskset always improves performance" | taskset helps for: processes that have hot data in L1/L2 CPU cache (pinning keeps them on the same core), latency-sensitive apps that benefit from predictable CPU placement. taskset HURTS for: processes that are I/O-bound (pinning wastes time waiting when other cores are free), on NUMA systems if pin to wrong node (data is on node 1, but process is pinned to node 0's CPUs). The kernel's scheduler generally makes good decisions about CPU placement. Only use taskset after profiling shows migration overhead or cache miss issues. |
| "ionice only affects disk I/O, not network" | Correct - `ionice` controls only BLOCK device I/O (disk reads/writes). Network I/O priority is controlled separately: `tc` (Traffic Control) for network bandwidth, socket buffer sizes for UDP/TCP. The `ionice -c 3` (idle class) means disk I/O only runs when no other process needs the disk. For databases: ionice class 1 (real-time) can improve query latency, but USE CAREFULLY - it can starve other processes of disk I/O. |

---

### Failure Modes & Diagnosis

**RT process causing system unresponsiveness:**
```bash
# Symptom: system load is high, SSH barely responds, processes seem stuck
# Cause: RT process in infinite loop or consuming 100% CPU

# Diagnosis (if you can still get a shell):
chrt --pid $(ps aux --sort=-pcpu | awk 'NR==2{print $2}')
# Shows: SCHED_FIFO priority 99 -> this process is preempting everything!

# Option 1: if sched_rt_runtime_us is not -1, wait for the OS to enforce limit
cat /proc/sys/kernel/sched_rt_runtime_us   # if positive, OS will intervene
# After 5% of time is given to normal processes, you might regain access

# Option 2: if you can reach the process, kill it:
kill -9 <PID>

# Option 3: change its scheduling from another terminal:
chrt --other -p 0 <PID>   # demote to SCHED_OTHER (CFS)

# Prevention:
sysctl -w kernel.sched_rt_runtime_us=950000   # 95% for RT, 5% for normal
# This is the default on most distros; if changed to -1, RT can starve all
# Persist: echo "kernel.sched_rt_runtime_us=950000" >> /etc/sysctl.conf
```

---

### Related Keywords

**Foundational:**
LNX-006 (Processes), LNX-007 (Process Management)

**Builds on this:**
LNX-077 (CFS Internals), LNX-072 (cgroups)

**Related:**
LNX-072 (cgroups for group scheduling), LNX-095 (CPU Performance)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `nice -n N cmd` | Start command with nice N |
| `renice -n N -p PID` | Change priority of running process |
| `ionice -c 3 cmd` | Run with idle I/O class (background) |
| `chrt -f 50 cmd` | Run with FIFO real-time priority 50 |
| `chrt -p PID` | Show scheduling policy of process |
| `taskset -c 0,1 cmd` | Pin to CPUs 0 and 1 |
| `taskset -cp PID` | Show CPU affinity of running process |
| `ps -eo pid,ni,comm` | Show nice values of all processes |

**Nice value quick reference:**

| Nice | Priority | Use Case |
|------|----------|---------|
| -20 | Highest | Critical system processes (root only) |
| -5 | High | Important production services |
| 0 | Default | Normal processes |
| 10 | Low | Development tools, non-critical |
| 19 | Lowest | Background batch, backups |

**3 things to remember:**
1. nice values only matter when CPU is contested; idle system runs everything at full speed regardless
2. SCHED_FIFO = never preempted by normal processes (latency, not throughput) - dangerous if process misbehaves
3. `ionice -c 3` (idle class) = disk I/O only when no other process needs the disk - perfect for backups

---

### Transferable Wisdom

Scheduling concepts appear in: JVM thread priorities (`Thread.setPriority()`)
map to nice values on Linux. Kubernetes `resources.requests.cpu` and
`resources.limits.cpu` translate directly to cgroup CFS bandwidth (quota
and period). Docker `--cpu-shares` maps to cgroup `cpu.shares` (nice-like
proportional scheduling). Go runtime: uses its own goroutine scheduler
(M:N threading) on top of Linux threads. OS thread pool size in Java:
`ForkJoinPool.commonPool()` uses all CPUs unless limited by cgroup CPU quota.
Database I/O priority: PostgreSQL `default_statistics_target` and autovacuum
I/O settings are analogous to ionice for database background work. The
general pattern - "background work should yield to foreground work" - appears
everywhere from OS scheduling to Kafka consumer group rebalancing delays.

---

### The Surprising Truth

The nice value system has a counterintuitive relationship with modern
hardware: on a 32-core server running one web server (nice 0) and one
batch job (nice 19), the batch job runs at nearly FULL SPEED most of the
time. This is because CFS scheduling is per-core - if 30 cores are idle,
the batch job gets 30 free cores regardless of nice value. Nice 19 only
matters when a specific core is contested. The web server at nice 0 gets
priority on whichever core it's running on when the batch job also wants
that core. In practice: the performance difference between nice 0 and nice
19 on a multi-core server with a lightly-loaded web service is minimal -
the batch job runs at nearly the same speed either way. The real value of
nice on modern servers is not CPU throttling but INTERRUPT RESPONSE: when
a web request arrives, the nice 0 process preempts the nice 19 process on
that core within the CFS scheduling period (< 1ms), ensuring the request
gets handled promptly. This is why "set batch jobs to nice 15-19" is a
best practice: not because it dramatically reduces batch throughput, but
because it ensures web request latency doesn't spike when a core is contested.

---

### Mastery Checklist

- [ ] Understands CFS nice value scale and how proportional CPU allocation works
- [ ] Can use nice/renice for new and running processes
- [ ] Can use ionice for I/O priority control (background jobs)
- [ ] Understands SCHED_FIFO vs CFS and when real-time scheduling is appropriate
- [ ] Can use taskset for CPU affinity and understands when it helps vs hurts

---

### Think About This

1. A server runs a web API (24/7) and a nightly data processing job (2am-6am).
   Both run at nice 0. During the batch window, API latency P99 goes from
   5ms to 50ms. Design a comprehensive scheduling strategy to fix this,
   considering both CPU and I/O. What nice and ionice settings would you
   apply, and how would you make them persistent using systemd unit files?

2. A Java application is experiencing periodic GC pauses of 50-100ms that
   cause timeout errors. Someone suggests running the JVM with `chrt -f 50`
   to prevent the GC threads from being preempted. Is this a good idea?
   What are the risks? What alternatives would you recommend?

3. A multi-threaded application spawns 100 worker threads, but you want only
   4 CPUs to be used (to leave other CPUs for other services). Compare these
   three approaches: (a) `taskset -c 0-3 ./app`, (b) systemd `CPUAffinity=0-3`,
   (c) cgroup `cpuset.cpus=0-3`. What is the difference in how they enforce
   the CPU restriction, and which is appropriate for each scenario?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain how CFS (Completely Fair Scheduler) works and how nice values affect it.
A: CFS (Completely Fair Scheduler) is Linux's default CPU scheduler. Its goal is to give every runnable process a "fair" share of CPU time, weighted by nice values. Mechanism: each process has a `vruntime` (virtual runtime) counter. When a process runs, its vruntime increases at a WEIGHTED rate based on its nice value. Processes with lower nice (higher priority) accumulate vruntime SLOWER - they appear to run "less" in virtual time even when running more wall-clock time. The scheduler always picks the process with the lowest vruntime to run next. This is stored in a red-black tree, so finding the minimum is O(log n). When a sleeping process wakes up (e.g., network data arrives), CFS sets its vruntime to slightly below the minimum currently running - ensuring it gets CPU soon without starving other processes. Nice value to CFS weight mapping: nice 0 = weight 1024, nice 10 = weight 110. If nice-0 and nice-10 processes both want CPU: nice-0 gets 1024/(1024+110) = 90%, nice-10 gets 110/(1024+110) = 10%. At nice -20 vs nice 0: -20 gets ~90x more CPU. Practical effect: nice only matters when CPU is CONTESTED on a specific core. On an idle system, every process runs full speed regardless of nice. In production: set batch jobs to nice 15-19 so they don't compete with request-serving threads when a core is busy.

**Expert:**
Q: What are the trade-offs between SCHED_FIFO, SCHED_OTHER (CFS), and SCHED_DEADLINE for real-time workloads?
A: SCHED_OTHER (CFS) is the default for all normal processes. Fair sharing, proportional to nice weights. No latency guarantees - a runnable process might wait up to one scheduling period (default 6ms) before getting CPU. Use for: general-purpose code, servers, anything that doesn't require bounded latency. SCHED_FIFO (real-time): assigned priority 1-99. A SCHED_FIFO process preempts ALL CFS processes and all lower-priority RT processes immediately. Within same priority: process runs until it voluntarily yields (no time slice). No latency guarantee from kernel but in practice: sub-millisecond wake-up latency. Risks: (1) process in infinite loop starves everything, (2) requires RT kernel (`PREEMPT_RT`) for < 100us latency, (3) requires CAP_SYS_NICE or root. The `sched_rt_runtime_us` watchdog prevents complete starvation (RT gets at most `sched_rt_runtime_us / sched_rt_period_us` of CPU - default 95%). SCHED_DEADLINE: specify three parameters: (1) runtime = CPU time needed per period, (2) period = how often the job recurs, (3) deadline = when within each period it must complete. The scheduler ensures the job gets exactly `runtime` CPU in each `period` and always meets `deadline`. Much safer than FIFO: overrun is detected and handled (EDF - Earliest Deadline First algorithm). No priority inversion issues. Kernel admission control: rejects if deadlines can't be met given current load. Use SCHED_DEADLINE for: periodic control loops, audio/video encoding with hard deadlines. Use SCHED_FIFO for: legacy real-time apps that assume FIFO semantics, when deadline parameters are unknown. Use CFS for: everything else (> 99% of software).
