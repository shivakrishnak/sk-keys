---
id: LNX-093
title: "Linux Performance Troubleshooting (USE Method)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-062, LNX-063, LNX-094, LNX-095
used_by: LNX-094, LNX-095, LNX-096
related: LNX-062, LNX-063, LNX-094, LNX-095, LNX-088
tags: [use-method, utilization, saturation, errors, performance-analysis, brendan-gregg, uptime, dmesg, vmstat, mpstat, pidstat, iostat, netstat, sar, top, iotop, perf, flame-graph, strace, ltrace, linux-performance, 60-second-analysis, cpu-analysis, memory-analysis, disk-io-analysis, network-analysis, performance-checklist]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 93
permalink: /technical-mastery/lnx/linux-performance-troubleshooting-use-method/
---

## TL;DR

The USE Method (Brendan Gregg): for every resource, check Utilization,
Saturation, and Errors. Resources: CPU, memory, disk I/O, network interfaces,
file descriptors. The **60-second Linux analysis** is the universal first
response: `uptime` (load average), `dmesg -T | tail -20` (kernel errors),
`vmstat 1` (runnable, blocked, swap), `mpstat -P ALL 1` (per-CPU), `pidstat 1`
(top processes), `iostat -xz 1` (disk), `free -m` (memory), `sar -n DEV 1`
(network), `top` (overall view). This sequence takes 60 seconds and surfaces
most performance issues. Key metrics: CPU steal time (st in top/mpstat = VM
hypervisor stealing CPU), CPU wait (wa = blocked on I/O), load average vs
CPU count (load > CPUs = saturation).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-093 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | USE method, performance analysis, vmstat, iostat, mpstat, sar, perf, flame graphs, 60-second analysis |
| **Prerequisites** | LNX-062, LNX-063 (CPU/memory basics), LNX-094 (memory pressure) |

---

### The Problem This Solves

**Problem 1**: Production server is slow. On-call engineer connects via SSH.
What do they check first? Without a framework: random guessing - check disk?
check memory? look at logs? The engineer checks the wrong things, wastes 30
minutes, and the incident drags on. With the USE Method + 60-second checklist:
systematic analysis in 60 seconds that covers every major resource. First
command: `uptime` (5 seconds). Shows load average - if 4.5 on a 4-CPU machine:
CPU saturation is the first suspect. Immediately narrows the investigation.

**Problem 2**: A service has high latency under load. Metrics show CPU is at
50% utilization. "CPU is not the bottleneck." But wait - looking at CPU steal
time (st): 15%. The hypervisor is stealing 15% of CPU time from this VM. The
effective CPU utilization from the application's perspective is 50% / (1-0.15)
= 59%, PLUS the time that could have been used but was stolen. Solution: move
to a dedicated host or reserved instances - not a code optimization problem.

---

### Textbook Definition

**USE Method**: A methodology by Brendan Gregg for performance analysis. For
every resource in the system, measure: **Utilization** (busy time percentage),
**Saturation** (work queued because resource is at capacity), **Errors**
(error events that indicate malfunction).

**Resources to analyze:**
| Resource | Utilization | Saturation | Errors |
|----------|-------------|------------|--------|
| CPU | `mpstat` %usr+%sys | load avg, run queue | (rare) |
| Memory | `free` used/total | swap usage, paging | OOM events |
| Disk I/O | `iostat` %util | await, avgqu-sz | `dmesg` I/O errors |
| Network | `sar -n DEV` txkB/s | drops, retransmits | `ip -s link` errors |
| File descriptors | `cat /proc/sys/fs/file-nr` | blocked on open() | (rare) |

---

### Understand It in 30 Seconds

```bash
# === 60-second Linux Performance Analysis ===
# Run each command for 1 sample (or 1 second interval)

# Step 1: uptime - load average (5 sec)
uptime
# 14:32:15 up 10 days,  3:42, 1 user, load average: 1.23, 0.89, 0.76
#                                       1-min        5-min  15-min
# Compare load average to nproc (number of CPUs):
nproc     # example: 4
# load 1.23 on 4 CPUs = 31% runnable (under-loaded)
# load 5.5 on 4 CPUs = 137% runnable (SATURATED - queue forming)

# Step 2: kernel errors (5 sec)
dmesg -T | tail -20
# Look for: OOM killer, disk errors, network errors, driver errors
# OOM: "oom_reaper: reaped process nginx, now anon-rss:0kB..."
# Disk: "blk_update_request: I/O error, dev sda, sector 123456"

# Step 3: vmstat - overall system health (10 sec)
vmstat 1 5
# procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
#  r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
#  2  0      0 456789  12345 234567    0    0     0    12  234  456  5  2 92  1  0
#
# r: runnable processes (r >> CPUs = CPU saturation)
# b: blocked (b > 0 = waiting for I/O or lock)
# si/so: swap in/out (so > 0 = memory pressure, paging out)
# bi/bo: block in/out (bo > 0 = disk writes)
# wa: CPU wait (wa > 10% = I/O bottleneck)
# st: CPU steal time (st > 0 = hypervisor stealing CPU from VM)

# Step 4: mpstat - per-CPU breakdown (10 sec)
mpstat -P ALL 1 1
# CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %idle
#   0    15.3    0.0     3.2    0.5      0.1     0.3    0.0    80.6
#   1    82.5    0.0     8.3    0.1      0.0     0.1    0.0     9.0
#   2     3.1    0.0     1.0    0.0      0.0     0.0    0.0    95.9
#   3     4.2    0.0     1.5    0.0      0.0     0.0    0.0    94.3
# CPU 1 at 82.5% usr: single-threaded hotspot!
# Look for: unbalanced load (single CPU pegged while others idle)
# %steal > 5%: cloud CPU stealing

# Step 5: pidstat - per-process CPU (5 sec)
pidstat 1 1
# PID    %usr %system  %guest   %wait   %CPU  CPU  Command
# 1234   78.2    4.3     0.0     0.0    82.5    1   java
# ^ Process 1234 using 82.5% CPU (single threaded on CPU 1)

# Step 6: iostat - disk I/O (10 sec)
iostat -xz 1 1
# Device  r/s  w/s  rkB/s  wkB/s  await  r_await  w_await  svctm  %util
# sda     0.0  24.5   0.0  198.2   1.2     0.0       1.2    0.8    2.0
# sdb     0.0  0.0    0.0    0.0   0.0     0.0       0.0    0.0    0.0
# nvme0   234  156  3456.2 1234.5  0.08    0.06      0.12   0.04   1.5
# 
# await: average I/O latency (ms). > 20ms for HDD = long queue
# %util: device utilization. 100% = saturated

# Step 7: free - memory (5 sec)
free -m
#               total        used        free      shared  buff/cache   available
# Mem:          15846       12345        1234         456        2267        3001
# "available" is the KEY metric (not "free")!
# available: what new processes can actually use (free + reclaimable cache)
# available < total * 10%: potential memory pressure

# Step 8: sar - network (5 sec)
sar -n DEV 1 1
# IFACE      rxpck/s  txpck/s  rxkB/s  txkB/s  %ifutil
# eth0         234.5    198.7  1234.5   987.3    0.1
# Check: is %ifutil approaching 100%? Any errors?

# Step 9: sar - TCP summary (5 sec)
sar -n TCP,ETCP 1 1
# active/s: TCP connections opened/sec (from this host)
# passive/s: incoming connections accepted/sec
# retrans/s: retransmitted segments/sec
# (retrans > 0 = packet loss or network issues)

# Step 10: top - overall (10 sec)
top -b -n 1 | head -20
# Shows: uptime, tasks, CPU%, memory, top processes
```

---

### First Principles

```
USE Method framework:

Resource lifecycle:
  1. Available capacity (max)
  2. Current utilization (% of max being used)
  3. Saturation: when utilization approaches 100%, work QUEUES
     (requests wait because resource is busy)
  4. Errors: failures that indicate resource malfunction

CPU USE analysis:
  Utilization = %usr + %sys (not idle%)
  (100% - %idle = utilization... but check %iowait separately)
  
  Saturation indicators:
    - load average / nproc > 1.0 (processes waiting for CPU)
    - run queue > nproc (r column in vmstat)
    - %wait in pidstat (process waiting for CPU to schedule it)
  
  Error indicators: hardware MCE events (rare), cpuinfo errors

Memory USE analysis:
  Utilization = MemTotal - MemAvailable (not "free"!)
  Cache is not "used" memory: it can be reclaimed
  
  Saturation indicators:
    - vmstat si/so > 0 (paging - memory is overcommitted)
    - sar -B: pgscank/s > 0 (kswapd scanning pages)
    - /proc/pressure/memory: some/full > 0
    - oom_score high for processes (near OOM kill threshold)
  
  Error indicators: OOM kills in dmesg

Disk I/O USE analysis:
  Utilization = %util from iostat (% of time device is busy)
  Note: for RAID/SSD with parallel I/O:
    %util can be 100% with no saturation (parallel I/Os in flight)
    Use: avgqu-sz (average queue size) > 1 = saturation indicator
  
  Saturation indicators:
    - await >> svctm (service time): queue is forming
    - avgqu-sz > 1: multiple I/Os waiting in queue
  
  Error indicators: dmesg I/O errors, smartctl errors

Network USE analysis:
  Utilization = txkB/s / (NIC speed in kB/s)
  Example: 1 Gbps NIC = 125,000 kB/s theoretical max
  
  Saturation indicators:
    - txdrop, rxdrop in ip -s link
    - netstat -s: retransmits, no buffer space errors
    - sar -n TCP retrans/s > 0
  
  Error indicators: ip -s link errors (CRC, framing errors)

File descriptor USE:
  cat /proc/sys/fs/file-nr
  # allocated  unused  max
  # 45632       0      12345678
  # allocated / max = utilization
  # ulimit -n per process (default 1024 on old systems)
  Saturation: blocked on open() (rare, use strace to see)

Flame graph workflow:
  Problem: "CPU is high, but which code path?"
  
  Step 1: Record CPU stack traces:
    perf record -ag -F 99 -- sleep 30
    # -a: all CPUs, -g: call graphs, -F 99: 99 Hz sampling
    # sleep 30: record for 30 seconds
  
  Step 2: Export:
    perf script > out.perf
  
  Step 3: Generate flame graph:
    stackcollapse-perf.pl out.perf > out.folded
    flamegraph.pl out.folded > cpu-flamegraph.svg
  
  Step 4: Analyze:
    - Wide plateaus at top = hot code paths (time consumed here)
    - Deep stacks = many function calls (not necessarily slow)
    - Each column = one code path, width = CPU time spent there
  
  Online alternative: flamegraph.dev (paste perf output)
```

---

### Thought Experiment

Diagnosing a "slow Java application server" using the USE Method:

```bash
# Alert: P95 response latency increased from 50ms to 500ms
# Instance: 4-CPU EC2 m5.xlarge, 16GB RAM

# === Step 1: uptime ===
uptime
# load average: 8.45, 6.23, 4.12
# 8.45 on 4 CPUs = 211% runnable rate! SEVERE CPU saturation
# -> Something is using more CPU than available

# === Step 2: dmesg ===
dmesg -T | tail -5
# [Fri May 17 10:23:45 2024] Out of memory: Kill process 12345 (java)
# ^ OOM kill! Java process was killed and restarted
# Both CPU saturation AND memory pressure!

# === Step 3: vmstat ===
vmstat 1 5
#  r  b   swpd   free   buff  cache   si   so    bi    bo   cs  us  sy  id wa st
#  9  0 2048000  12345  1234  23456  567  890    12  1234 2345  85  10   0  5  0
# r=9: 9 runnable on 4 CPUs
# swpd=2048000: 2GB swap in use
# si=567, so=890: active swap I/O! (memory thrashing)
# us=85%: high user CPU

# === Step 4: mpstat ===
mpstat -P ALL 1 1
# CPU  %usr  %sys  %idle  %steal
#   0  95.0   4.0    0.0    1.0
#   1  93.5   5.5    0.0    1.0
#   2  92.0   7.0    0.0    1.0
#   3  94.0   5.0    0.0    1.0
# All CPUs nearly 100%! Even load = process is multi-threaded

# === Step 5: pidstat ===
pidstat -u 1 1
# PID   %usr  %sys  %CPU  Command
# 12345  350   40   390   java   <- 390% = 3.9 CPUs!
# This java process is the culprit

# === Root cause analysis ===
# Hypothesis: Java GC storm
# Check: jstat -gcutil 12345 1000
# S0   S1     E    O    M   CCS    YGC   YGCT  FGC  FGCT   GCT
# 0.0  0.0 100.0 99.8 ...  ...     567   23.4  45   890.5  913.9
# FGC=45 full GCs, FGCT=890.5 seconds! GC is eating 97% of CPU!
# Old gen 99.8% full: heap is too small, GC runs constantly

# Root cause: heap is undersized, GC storms => CPU saturation
# Solution: increase -Xmx (max heap size), reducing GC frequency
# Or: analyze heap dumps for memory leak causing excessive retention
```

---

### Mental Model / Analogy

```
USE Method = doctor's diagnostic checklist for each organ

Patient (server) has a symptom: "slow response"
Doctor (you) examines each organ (resource):

Lung (CPU):
  Utilization: breathing rate % of max capacity?
    mpstat: is CPU 80%+ used?
  Saturation: is there a queue of breaths waiting?
    load average > nproc? vmstat r > nproc?
  Errors: gasping, cardiac arrest?
    CPU MCE events (rare)

Heart (Memory):
  Utilization: how full is the blood supply?
    free -m: is "available" near zero?
  Saturation: is the heart overworking to compensate?
    swap activity: si/so > 0 in vmstat?
    kswapd using CPU?
  Errors: heart failure?
    OOM kills in dmesg

Kidneys (Disk):
  Utilization: how busy is waste processing?
    iostat %util: is disk 90%+ busy?
  Saturation: is there a queue of waste backed up?
    await >> svctm, avgqu-sz > 1?
  Errors: kidney stones?
    dmesg disk errors (I/O error, bad sector)

Blood vessels (Network):
  Utilization: how full are the arteries?
    sar %ifutil near 100%?
  Saturation: are packets dropping because pipes are full?
    ip -s link drops?
  Errors: blockages?
    CRC errors, bad packets

60-second analysis = 10-point vital signs check:
  uptime: pulse (load average)
  dmesg: recent medical events (errors, OOM)
  vmstat: blood pressure (runnable, swap, I/O)
  mpstat: oxygen saturation per lung (per-CPU)
  pidstat: which organ is overworking (top processes)
  iostat: kidney function (disk I/O)
  free: blood volume (memory)
  sar network: circulation (network utilization)
  sar TCP: nerve signal failures (TCP retransmits)
  top: full body overview

After vitals: targeted diagnostics
  CPU issue: perf top -> flame graph -> find hot code
  Memory issue: smem, vmstat, /proc/meminfo
  Disk I/O: iotop, blktrace, application I/O patterns
```

---

### Gradual Depth - Five Levels

**Level 1:**
The USE Method concept (Utilization, Saturation, Errors). `uptime` for load
average. `top` for overall view. `free -m` for memory. `df -h` for disk space.
`ping` for network. Basic meaning of "system is slow."

**Level 2:**
60-second analysis checklist (all 10 commands). `vmstat 1` interpretation
(r, b, si/so, wa). `iostat -xz 1` columns (await, util). `mpstat -P ALL 1`
per-CPU breakdown. Load average interpretation vs CPU count. CPU steal time
(st) in cloud VMs.

**Level 3:**
`pidstat 1` for per-process CPU/I/O. `iotop` for per-process disk I/O.
`sar` for historical metrics (SAR recording). `netstat -s` for TCP statistics.
`dmesg` error patterns (OOM, disk errors, network errors). PSI
(/proc/pressure/cpu,memory,io) for resource pressure stall information.
`perf top` for real-time CPU hotspot identification.

**Level 4:**
`perf record -ag -F 99` + flame graph workflow (perf script, stackcollapse-perf.pl,
flamegraph.pl). `bpftrace` one-liners for dynamic tracing. `strace -c` for
system call profiling. `ltrace` for library call tracing. Off-CPU flame graphs
(where time is spent waiting, not executing). `perf stat` for CPU efficiency
(IPC, cache miss rate, branch misprediction rate). `numastat` for NUMA memory
effects. `perf c2c` for cache-line contention (false sharing).

**Level 5:**
BPF-based performance tools (bcc: `profile`, `offcputime`, `runqlat` for run
queue latency histograms). Kernel scheduler analysis: `runqlat` (BCC tool)
- histogram of how long tasks wait in the run queue before getting CPU. `hardirqs`
and `softirqs` BCC tools for interrupt overhead profiling. PMU (Performance
Monitoring Unit) events in `perf stat -e cache-misses,instructions,cycles,
context-switches`. Hardware performance counters for microarchitecture analysis:
LLC miss rate, branch prediction, memory bandwidth saturation. Kernel flame
graphs (kernel code paths - requires kernel symbols and debug info).

---

### How It Works

```
SAR (System Activity Reporter) - persistent metrics collection:
  systemctl enable --now sysstat
  Cron: /etc/cron.d/sysstat runs sa1 every 10 minutes
  sa1 writes binary data to /var/log/sa/saNN (NN = day of month)
  sar reads these files for historical analysis
  
  Useful historical queries:
    sar -u -f /var/log/sa/sa15    # CPU for day 15
    sar -u -s 14:00:00 -e 15:00:00  # CPU 2-3pm today
    sar -b -f /var/log/sa/sa15    # block I/O for day 15
    sar -n DEV                     # network today

perf subsystem:
  perf = Linux performance counter subsystem (perf_events)
  Accesses hardware PMU (Performance Monitoring Unit) counters
  Also hooks into software events (context switches, faults)
  
  Sampling mode (-F 99):
    Hardware PMU interrupt fires at 99 Hz (99 times per second)
    At each interrupt: capture current stack trace
    Over 30 seconds: 30 * 99 = ~3000 samples per CPU
    Stack frequency = time spent in that code path
  
  perf stat mode:
    Count hardware events: cycles, instructions, cache-misses
    Compute ratios:
      IPC = instructions / cycles (> 1.0 = good, < 0.5 = memory bound)
      Cache miss rate = LLC-misses / instructions
    Example:
      perf stat -e cycles,instructions,cache-misses sleep 10
      # 5,000,000,000 cycles
      # 3,500,000,000 instructions    # 0.70 insn per cycle
      # 125,000,000 cache-misses      # 3.57% of instructions
```

---

### Complete Picture - End-to-End Flow

```
Performance investigation flow (Brendan Gregg's methodology):

1. Initial info gathering (2 min):
   - Incident description: what is slow, when did it start?
   - Recent changes: deployment, config change, traffic spike?
   
2. 60-second analysis (1 min):
   uptime, dmesg, vmstat 1, mpstat -P ALL 1, pidstat 1,
   iostat -xz 1, free -m, sar -n DEV 1, sar -n TCP,ETCP 1, top
   -> Identifies which resource (CPU/memory/disk/network)

3. Resource-specific deep dive (5-15 min):
   CPU hotspot: perf top -> identify process/function
   Memory: smem, /proc/meminfo, vmstat -s
   Disk: iotop, iostat -d 1 (per-device), blktrace
   Network: netstat -s, ss -s, sar -n SOCK

4. Application-specific (5-30 min):
   Java: jstat, jstack, heap dump analysis
   Database: EXPLAIN ANALYZE, slow query log
   Generic: strace -c (syscall count), perf record -> flame graph

5. Hypothesis and verification:
   Formulate cause -> change one thing -> measure improvement
   Correlate timeline with deployment/change history

Decision tree:
  load avg >> nproc?
    YES -> CPU saturated
           mpstat: single CPU pegged? -> single-threaded app
           all CPUs high? -> multi-threaded or many processes
           steal time (st) high? -> cloud CPU contention
           
  load avg ok but slow?
    wa high (> 20%)? -> disk I/O bottleneck
           iostat await high? -> slow disk, tune or upgrade
           iostat util 100%? -> disk saturated
    si/so > 0? -> memory pressure (swapping)
           free available < 10%? -> add RAM or tune app memory
    network: retransmits, drops? -> network congestion
    app-specific: connections queued? GC? locks?
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "High CPU utilization means the system is struggling" | CPU utilization at 70-80% is HEALTHY and efficient. Idle CPUs are wasted resources. The concern is CPU SATURATION: when the run queue consistently exceeds the number of CPUs (load average > nproc). At 80% utilization with no queue (load = 0.8 on 1 CPU): system is responsive. At 150% utilization (load = 1.5 on 1 CPU): processes are waiting 50ms for every 100ms of CPU time - noticeable latency increase. For latency-sensitive services: keep CPU utilization under 70% to provide headroom for traffic spikes without immediately hitting saturation. |
| "free memory in `free -m` tells you if you're running low on memory" | The "free" column in `free -m` is largely meaningless on modern Linux. Linux aggressively caches disk reads in page cache (shown in buff/cache). This "used" memory can be instantly reclaimed by applications. The metric that matters is "available" - this shows free memory + reclaimable cache. A system with 100MB "free" but 2GB "available" has plenty of memory. The system is LOW on memory only when "available" approaches zero AND kswapd starts paging (si/so > 0 in vmstat). |
| "Load average > 1.0 always means trouble" | Load average is meaningful only RELATIVE TO CPU COUNT. Load 1.0 on a 1-CPU system = 100% saturation (one process always waiting). Load 1.0 on a 32-CPU system = 3% saturation (trivially low). Rule: load/nproc is the saturation ratio. Additionally: load average includes both runnable (waiting for CPU) AND uninterruptible sleeping processes (waiting for I/O or kernel lock). Load spike can be caused by disk I/O wait, not just CPU. Check `vmstat` b (blocked) column and `mpstat` %wa (iowait) to distinguish CPU saturation from I/O wait. |
| "strace slows down an application minimally" | `strace` in attach mode (`strace -p PID`) adds significant overhead - often 10-50x slowdown or more because every syscall requires two context switches into the tracer. NEVER use `strace -p` on a critical production process under heavy load. Safe alternatives: `perf trace` (uses perf_events ring buffer, much lower overhead), `bpftrace` (eBPF-based, near-zero overhead), `strace -c -p PID` (count-only mode, lower overhead but still significant). For production use: `perf trace --pid PID` is the right tool. `strace -c` (count mode without -p) on a short-lived process is safe. |

---

### Failure Modes & Diagnosis

```bash
# === Common production performance scenarios ===

# Scenario 1: Database server becomes suddenly slow
# Diagnosis sequence:

uptime
# load average: 12.3, 4.5, 2.1
# Spike! 12x load on 4-CPU server

vmstat 1 3
#  r  b   swpd free   si so bi    bo   cs us sy id wa st
# 15  3  0    567   0  0  0 234000 1234  90 5  5  0 90  0
# r=15: massive CPU queue
# b=3: 3 processes blocked on I/O
# bo=234000: 234 MB/s disk writes! Abnormal
# wa=90: 90% CPU wait time = disk I/O is the bottleneck

iostat -xz 1 3
# Device  r/s w/s  await  %util
# nvme0   10  8560  25.4  100.0
# 100% util, 25ms await on NVMe (should be 0.1ms): saturated!

iotop
# Total DISK READ:  50 K/s | Total DISK WRITE: 234 M/s
# PID    IO%  COMMAND
# 1234   98%  mysql
# MySQL writing 234 MB/s: transaction log (iblogfile) fill?

# Check MySQL status:
mysql -e "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_write%';"
mysql -e "SHOW ENGINE INNODB STATUS\G" | grep -A5 "Log sequence number"
# Checkpoint too old: InnoDB flushing dirty pages desperately

# Solution: increase innodb_buffer_pool_size, innodb_log_file_size

# Scenario 2: Java application high CPU
pidstat 1 1
# PID   %CPU  Command
# 5678  395   java

# Java GC analysis:
jstat -gcutil 5678 1000 10
# S0   S1     E    O    M    YGC  YGCT  FGC  FGCT   GCT
# 0.0  0.0  100.0 99.5 94.3  123  5.6   45  450.3  455.9
# Old gen 99.5%: GC storm

# Heap dump:
jmap -dump:live,format=b,file=/tmp/heap.hprof 5678
# Analyze with Eclipse Memory Analyzer (MAT) or jhat

# Scenario 3: Network throughput drops
sar -n DEV 1 5
# eth0: txpck/s drops from 50000 to 12000
ip -s link show eth0
# TX errors: 1234 (tx_errors > 0: driver queue drops?)
ethtool -S eth0 | grep -i "drop\|error\|miss"
# tx_queue_stopped: 5678  <- TX queue being stopped!
# Solution: increase tx-ring-buffer, or check for NIC issues
```

---

### Related Keywords

**Foundational:**
LNX-062 (CPU fundamentals), LNX-063 (memory management)

**Builds on this:**
LNX-094 (memory pressure), LNX-095 (CPU performance)

**Related:**
LNX-088 (disk performance), LNX-096 (crash analysis)

---

### Quick Reference Card

| Command | What it shows |
|---------|--------------|
| `uptime` | Load average vs CPU count |
| `vmstat 1` | CPU run queue, swap, I/O wait |
| `mpstat -P ALL 1` | Per-CPU utilization breakdown |
| `pidstat 1` | Per-process CPU/I/O usage |
| `iostat -xz 1` | Disk I/O (await, utilization) |
| `free -m` | Memory (focus on "available") |
| `sar -n DEV 1` | Network throughput per interface |
| `sar -n TCP,ETCP 1` | TCP connections and retransmits |
| `iotop` | Per-process disk I/O |

**3 things to remember:**
1. USE Method: for every resource - Utilization, Saturation, Errors. Systematic framework, never guess.
2. 60-second analysis: uptime -> dmesg -> vmstat -> mpstat -> pidstat -> iostat -> free -> sar -> top. Run in sequence, takes 60 seconds, surfaces 90% of issues.
3. "free" in `free -m` is misleading. Watch "available". For CPU: compare load average to nproc. For disk: watch await and %util, not just read/write rates.

---

### Transferable Wisdom

The USE Method transfers directly to cloud monitoring: every cloud provider
metric maps to USE. AWS CloudWatch: CPUUtilization (utilization),
CPUCreditBalance drain (saturation), StatusCheckFailed (errors); NetworkIn/Out
(utilization), NetworkPacketsDropped (saturation). The 60-second checklist
is the Linux equivalent of a cloud provider's "health dashboard" - you are
reading the same data, just from different sources. The principle "measure
all resources with the same three metrics" applies to: database connection
pools (utilization = connections used/max, saturation = queued requests,
errors = connection failures), thread pools (utilization = active/max,
saturation = queue depth, errors = rejected tasks), HTTP servers (utilization
= concurrent requests/max, saturation = request queue, errors = 5xx responses).
Flame graphs are the most transferable advanced technique: they work for CPU
in any language (Java, Python, Go, Rust, Node.js), off-CPU time, memory
allocation, and network events. `perf` works best for native code; for JVM
use async-profiler (handles JIT-compiled code correctly).

---

### The Surprising Truth

The "60-second Linux analysis" checklist was created by Brendan Gregg at
Netflix (where he worked as a Senior Performance Engineer). He published it
in a 2015 blog post, and it went viral in the SRE/DevOps community. The list
has barely changed since. The checklist is remarkable for its simplicity: 10
commands, each takes seconds, together they cover every major resource on any
Linux system from a Raspberry Pi to a 64-CPU cloud instance. The same commands
work on a 5-year-old system as on a brand-new one. The most counterintuitive
insight from performance engineering: CPU utilization at 95% can be perfectly
fine (if the only process is a batch job with no queue), while CPU utilization
at 60% can indicate severe problems (if 10 processes are all waiting for CPU
turns, adding 100ms latency each). The metric that matters is latency of
waiting (saturation), not just busy percentage (utilization). This is why
"we have plenty of CPU headroom" is a meaningless statement without looking
at the run queue.

---

### Mastery Checklist

- [ ] Can perform the 60-second analysis and correctly interpret each command's output
- [ ] Understands the USE Method and can apply it to CPU, memory, disk, and network
- [ ] Can distinguish between CPU utilization, CPU saturation, and CPU steal time
- [ ] Knows when to use perf top vs flame graphs vs strace for CPU investigation
- [ ] Can interpret vmstat si/so and iostat await to diagnose memory/disk bottlenecks

---

### Think About This

1. A production service is experiencing high latency. You run `top` and see
   CPU at 45% utilization - "plenty of headroom." But users are still complaining.
   Using the USE Method, describe all the other things you would check. Specifically:
   how could 45% CPU utilization coexist with severe performance problems? Give
   three specific scenarios where this could happen and what metrics would
   reveal each one.

2. Design a performance baseline capture script that runs automatically every
   5 minutes on all production servers and stores the data for 30 days. The
   script should capture all USE Method metrics. What format would you store
   the data in? How would you efficiently compare "current state" to "baseline
   from last week, same day, same hour" to detect anomalies? What alerting
   thresholds would you set for each resource?

3. An engineer proposes: "Instead of the 60-second checklist, let's just put
   all of this data in Prometheus + Grafana and look at dashboards." Evaluate
   this proposal: what are the advantages and limitations of each approach
   (CLI checklist vs Prometheus metrics)? What specific performance scenarios
   would the CLI checklist catch that might be missed by standard Prometheus
   metrics? What would you monitor differently in Prometheus to approximate
   the same coverage?

---

### Interview Deep-Dive

**Foundational:**
Q: Describe the USE Method and walk through the 60-second Linux performance analysis.
A: USE METHOD: For every resource, measure three metrics: (1) UTILIZATION: how busy is the resource (% of time it is busy doing work). (2) SATURATION: how much work is queued because the resource is at capacity. (3) ERRORS: failure events indicating resource malfunction. Resources to analyze: CPU, memory, disk I/O, network interfaces, file descriptors. WHY USE METHOD: avoids "I'll randomly check things until I find the problem." Systematic coverage ensures you don't miss the bottleneck because you checked the wrong resource first. 60-SECOND ANALYSIS: (1) `uptime` - load average vs nproc (is CPU saturated?); (2) `dmesg -T | tail` - recent kernel errors (OOM kills, disk errors, network errors); (3) `vmstat 1` - r (runnable), b (blocked), si/so (swap - memory pressure), wa (disk wait), st (CPU steal from hypervisor); (4) `mpstat -P ALL 1` - per-CPU breakdown (any single CPU pegged = single-threaded hotspot?); (5) `pidstat 1` - which process is consuming CPU/I-O?; (6) `iostat -xz 1` - disk await (>10ms HDD, >1ms SSD = high), %util (100% = saturated); (7) `free -m` - "available" column (not "free" - cache is reclaimable); (8) `sar -n DEV 1` - network throughput per interface; (9) `sar -n TCP,ETCP 1` - TCP retransmits (> 0 = packet loss); (10) `top` - overall process view. Total time: about 60 seconds. This sequence covers all major resource types and reveals: CPU saturation (r > nproc), memory pressure (si/so > 0), disk bottleneck (await > threshold), network issues (drops, retransmits), hypervisor CPU contention (steal > 5%). If these are clean: the problem is application-level (not OS resource).

**Expert:**
Q: Production Java application has intermittent high latency spikes that don't correlate with high CPU or memory usage. How do you diagnose this systematically?
A: "Intermittent high latency without high CPU or memory" is a classic GC pause, lock contention, or scheduler problem. DIAGNOSIS SEQUENCE: (1) FIRST: check GC pauses. `jstat -gcutil <PID> 1000` continuously. Look for Full GC (FGC column incrementing) or long GC times (FGCT). GC pauses at G1GC can be up to hundreds of ms. Even "minor" GCs at high frequency add up. (2) CORRELATE TIMING: enable GC logging: `-Xlog:gc*:file=/tmp/gc.log:time,uptimemillis` (Java 9+) or `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/tmp/gc.log`. Then grep gc.log for timestamps during latency spikes. (3) THREAD STACKS: during a spike, `jstack <PID>` repeatedly 3 times 5 seconds apart. Look for: threads in BLOCKED state (lock contention), threads waiting on a specific lock. `jstack <PID> | grep -A3 "BLOCKED"`. (4) SCHEDULER LATENCY: `perf record -g -- sleep 30; perf script | flamegraph.pl > cpu.svg`. Off-CPU flame graph: `offcputime-bpfcc -p <PID> 30` (requires bcc tools). Shows time spent waiting for CPU schedler, I/O, or lock. (5) LINUX SCHEDULER: `runqlat-bpfcc 30` - histogram of run queue latency (how long tasks wait before getting scheduled). If p99 > 10ms: scheduler latency contributing to application latency. (6) NUMA EFFECTS: if multi-socket machine, `numastat -p <PID>` - check numa_miss rate. Cross-NUMA memory access adds 30-100ns latency per access. (7) SYSTEM CALL LATENCY: `perf trace --pid <PID>` - which syscalls are slow? (8) NETWORK I/O: `netstat -s | grep retransmit` - if retransmits increasing during spikes: downstream service is slow or network is congested. `ss -ti` shows TCP socket statistics including retransmit info. Synthesis: most common causes in order - GC pause (70%), lock contention on shared data structure (20%), downstream service timeout (7%), OS scheduler/NUMA issue (3%).
