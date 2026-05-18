---
id: LNX-051
title: "System Resource Monitoring (vmstat, iostat, sar, dstat)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-020
used_by: LNX-093, LNX-094, LNX-095
related: LNX-020, LNX-093, OBS-001
tags: [vmstat, iostat, sar, dstat, mpstat, monitoring, cpu, memory, io, performance]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/lnx/system-resource-monitoring/
---

## TL;DR

Key resource monitoring commands: `vmstat 1` (CPU + memory + I/O overview,
1-second intervals), `iostat -xz 1` (per-disk I/O statistics), `mpstat -P ALL 1`
(per-CPU usage), `sar` (historical performance data via sysstat), `dstat`
(all-in-one real-time view). Critical metrics: CPU `us`/`sy`/`wa`/`si`
(user, system, I/O wait, softirq), I/O `%util` and `await` (disk utilization
and latency), memory `si`/`so` (swap in/out). Non-zero swap activity (`si/so`)
indicates memory pressure. High `%wa` (I/O wait) means CPU is idle waiting
for disk.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-051 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | vmstat, iostat, sar, dstat, mpstat, CPU, memory, I/O performance |
| **Prerequisites** | LNX-015, LNX-020 |

---

### The Problem This Solves

A production server is "slow" - users report high latency. Is it CPU-bound?
Memory pressure? Disk I/O bottleneck? Network saturation? Without knowing
which resource is the bottleneck, you're guessing. These tools give a
quantified, second-by-second view of resource consumption so you can pinpoint
the bottleneck and fix the right thing.

---

### Textbook Definition

**vmstat**: Virtual memory statistics. Reports CPU activity (user, system,
idle, wait, steal), memory (free, buffer, cache, swap), and I/O block
activity in one compact view. Essential for rapid system health overview.

**iostat**: I/O statistics per disk device. Reports throughput (kB/s read/write),
IOPS (reads/writes per second), utilization (`%util`), average wait time
(`await`), average service time (`svctm`). Part of `sysstat` package.

**mpstat**: Multiprocessor statistics. Per-CPU breakdown of user/system/
idle/wait/steal time. Identifies unbalanced CPU load across cores.

**sar** (System Activity Reporter): Collects and reports historical system
performance data. `sadc` collects data every 10 minutes (configured by
`/etc/sysstat/sysstat`). `sar -u` (CPU), `sar -r` (memory), `sar -b` (I/O),
`sar -n DEV` (network). Access yesterday's data: `sar -u -f /var/log/sysstat/sa$(date -d yesterday +%d)`.

**dstat**: Combines vmstat + iostat + ifstat into a colorful real-time view.
Replaces the three separate tools. Extensible with plugins.

---

### Understand It in 30 Seconds

```bash
# === vmstat: CPU + memory + I/O snapshot ===
vmstat 1 5             # 5 samples, 1 second interval
# Output columns:
# procs: r=runnable b=blocked
# memory: swpd=swap_used free buff cache
# swap: si=swap_in so=swap_out (per second)
# io: bi=blocks_in bo=blocks_out
# system: in=interrupts cs=context_switches
# cpu: us=user sy=system id=idle wa=iowait st=steal

# Quick health check:
vmstat 1 | awk '
  NR>2 {
    if ($3 > 0) print "WARN: Swap in: " $3 " kB/s"
    if ($4 > 0) print "WARN: Swap out: " $4 " kB/s"
    if ($16 > 10) print "WARN: I/O wait: " $16 "%"
    if ($11 > 500000) print "WARN: Context switches: " $11 "/s"
  }'

# === iostat: per-disk I/O ===
iostat -xz 1           # extended, skip idle, 1-second interval
# Key columns:
# rrqm/s wrqm/s: merged read/write requests per second
# r/s w/s: reads/writes per second (IOPS)
# rkB/s wkB/s: throughput (kilobytes per second)
# await: average I/O wait time (ms) - includes queue time
# svctm: average service time (ms) - device time only
# %util: percentage of time device was busy
# Rule: %util > 90% = disk is saturated
# Rule: await > 20ms for SSD = problem

# === mpstat: per-CPU ===
mpstat -P ALL 1        # all CPUs, 1-second interval
# Identifies: one CPU at 100% (single-threaded bottleneck)
# vs all CPUs at 80% (well-distributed load)

# === sar: historical data ===
sar -u 1 10            # CPU: 10 samples at 1-second interval
sar -r 1 10            # memory usage
sar -b 1 10            # I/O activity
sar -n DEV 1 5         # network by device
sar -u -f /var/log/sysstat/sa$(date +%d)  # today's historical data
sar -u 1 5 -e 14:00:00  # data from 14:00 today

# === dstat: all-in-one ===
dstat                  # default: cpu, disk, net, paging, system
dstat -tcmdn           # time, cpu, memory, disk, net
dstat --top-cpu        # process using most CPU
dstat --top-io         # process using most I/O
dstat 1 10             # 10 samples at 1 second

# === Quick diagnosis scripts ===
# CPU-bound?
sar -u 1 5 | awk 'NR>3 {if ($8 < 20) print "CPU busy: idle=" $8 "%"}'

# Memory pressure?
vmstat -s | grep -E "used swap|active memory"

# Disk saturation?
iostat -xz 1 3 | awk '/%util/{found=1} found && $NF+0 > 90 {print "SATURATED: " $0}'
```

---

### First Principles

**Interpreting vmstat output:**
```
$ vmstat 1 5
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 512000  25000 1200000   0    0     0    12  500 1200 45  5 48  2  0
 0  0      0 511000  25000 1200000   0    0     0     8  480 1100 10  3 86  1  0
 1  0      0 510000  25000 1200000   0    0     0    10  490 1100 15  4 80  1  0

Column analysis:
  r=2: 2 processes waiting to run (runnable queue > number of CPUs = CPU pressure)
  r=0: all processes satisfied (no CPU pressure)
  b>0: processes in uninterruptible sleep (often I/O wait)

  swpd>0 and si/so>0: ACTIVELY swapping = memory exhausted
  swpd>0 but si=so=0: historical swap use, not current pressure

  wa (iowait): CPU cycles spent waiting for I/O
    wa=0-5%: normal
    wa=10-30%: I/O starting to be a bottleneck
    wa>30%: significant I/O bottleneck
    wa=99%: I/O completely dominates

  st (steal): CPU stolen by hypervisor for other VMs
    st>5% on a VM: the physical host is overloaded, your VM is starved

  us+sy: application + kernel CPU usage
    us=90%, sy=5%: compute-bound application
    us=5%, sy=90%: too many system calls (context switches, networking)
    us=5%, sy=5%, wa=90%: I/O bound
```

**iostat extended output:**
```
$ iostat -xz 1
Device  r/s  w/s  rkB/s  wkB/s  await  svctm  %util
sda    50.0 200.0  400.0 1600.0   15.2    4.5   80.0
nvme0n1 500 2000  4000  16000     1.2    0.5   60.0

Interpreting:
  await: total I/O latency (queue + service)
    <1ms: NVMe SSD (excellent)
    1-5ms: SSD (good)
    5-20ms: SSD under load or HDD (acceptable)
    >20ms: SSD saturated or HDD (investigate)
    >50ms: HDD random I/O (normal for spinning disk)
    >100ms: serious I/O problem

  %util: time the device was busy
    <60%: comfortable
    60-90%: moderate load
    >90%: approaching saturation
    100%: fully saturated, all I/O queued

  r/s and w/s: IOPS (compare to device spec)
    NVMe SSD: typically 500K-1M IOPS
    SATA SSD: typically 50K-100K IOPS
    HDD: typically 100-200 IOPS random

  svctm (deprecated in newer iostat): actual device service time
    If await >> svctm: I/O is queueing (device is busy)
```

---

### Thought Experiment

Diagnosing a "slow database" complaint:

```bash
# Step 1: Quick overview
vmstat 1 5
# Observation: wa=45% (high I/O wait), r=0 (not CPU), swpd=0, si=so=0

# Conclusion: I/O bottleneck, not CPU or memory

# Step 2: Which disk?
iostat -xz 1 5
# sda:  %util=95%, await=80ms, r/s=500, w/s=50
# sdb:  %util=10%, await=5ms

# Conclusion: sda is saturated, await=80ms is severe

# Step 3: Which process?
# iotop -boa -d1  (requires iotop package)
# TID  PRIO  USER  DISK READ  DISK WRITE  SWAPIN  IO  COMMAND
# 1234  be/4 mysql  45.2M/s   12.3M/s      0.0%   99% mysqld

# Conclusion: MySQL is generating the I/O on sda

# Step 4: What type of I/O?
# Separate read vs write:
iostat -xz 1 | awk '$1=="sda"{printf "IOPS R:%d W:%d  Thr R:%dMB W:%dMB\n",$4,$5,$6/1024,$7/1024}'

# Step 5: Is it sequential or random?
blktrace -d /dev/sda -a issue -o - | blkparse -i - | \
    awk '{print $6}' | sort | uniq -c
# High R (read) with scattered LBAs: random I/O (bad for HDD)

# Resolution options:
# 1. Move database to NVMe SSD
# 2. Add buffer pool (more RAM for caching = fewer disk reads)
# 3. Use RAID 10 for parallel I/O
# 4. Analyze slow queries (are they doing full table scans?)
# 5. Use innodb_read_io_threads / innodb_write_io_threads

# Monitor improvement:
# Baseline: await=80ms
# After adding RAM (buffer pool): await=15ms  -> 5x improvement
# After NVMe: await=2ms -> 40x improvement
```

---

### Mental Model / Analogy

```
System resource monitoring = checking vital signs on a patient

vmstat = the doctor's quick overview panel
  - Heart rate (CPU %): is the patient working hard?
  - Breathing rate (I/O waits): is the patient struggling?
  - Blood pressure (memory): is there pressure?
  - Sweating (swap activity): emergency response activated?

iostat = disk ECG
  - Per-device: which organ (disk) is stressed?
  - %util = how hard the disk is working
  - await = how long each request is waiting (latency)

mpstat = per-CPU EEG
  - Is one brain hemisphere (CPU core) overloaded?
  - Is load balanced across all cores?

sar = medical history file
  - "What happened at 3 AM?" -> review historical data
  - Trend analysis: is performance degrading over time?

dstat = all-in-one patient monitor
  - Shows everything at once: CPU, disk, network, memory
  - Color-coded, easy to read at a glance

High I/O wait = patient is anaemic (waiting for blood/data)
  - Treatment: faster disk, more RAM (cache more data)
Swap activity = patient is stressed (using emergency reserves)
  - Treatment: add RAM or reduce memory usage
High steal = patient is sharing a hospital bed with others
  - Treatment: dedicated hardware or change VM host
```

---

### Gradual Depth - Five Levels

**Level 1:**
`vmstat 1` (overview), `iostat -xz 1` (disk), `mpstat -P ALL 1` (per-CPU).
Key signals: `wa` > 10% = I/O problem, `si`/`so` > 0 = swap pressure, `r` >
CPU count = CPU pressure, `%util` > 90% = disk saturated. Install sysstat:
`apt install sysstat` or `yum install sysstat`.

**Level 2:**
`sar` for historical data (requires sysstat enabled: `systemctl enable sysstat`).
`dstat` for real-time all-in-one view. `iotop` for per-process I/O.
`pidstat -d 1` for per-process I/O stats. `nfsstat` for NFS-specific stats.
`free -h` and `/proc/meminfo` for memory detail.

**Level 3:**
`perf stat` for CPU hardware counters (cache misses, branch mispredictions).
`perf top` for live CPU flame graph preview. `blktrace` + `blkparse` for
detailed I/O event analysis (per-operation timestamps). `iotop -a` for
accumulated I/O. `iostat iowait` correlation with `vmstat wa`. Identifying
NUMA effects with `numastat`. Disk queue depth with `iostat -x` `avgqu-sz`.

**Level 4:**
`sar -n EDEV` for network error statistics. `/proc/diskstats` raw format
(source for iostat). `/proc/vmstat` kernel VM counters. `perf record -g`
flame graphs for CPU profiling. `ebpf/bcc` tools (`biolatency`, `biosnoop`)
for kernel-level I/O latency histograms. `llc_stat` for last-level cache
statistics. `cpupower frequency-info` for CPU frequency scaling state.

**Level 5:**
USE Method (Utilization Saturation Errors) for systematic resource analysis.
RED Method (Rate Errors Duration) for service metrics. Brendan Gregg's Linux
Performance Analysis in 60 seconds: `uptime`, `dmesg`, `vmstat`, `mpstat`,
`pidstat`, `iostat`, `free`, `sar`, `top`. eBPF/bpftrace one-liners:
`bpftrace -e 'tracepoint:block:block_rq_issue { @[args->rwbs] = count(); }'`
(count I/O types). `perf sched` for scheduling latency. OpenTelemetry metrics
from Linux performance counters for cloud-native observability.

---

### Code Example

**BAD - reactive monitoring without context:**
```bash
# BAD: One-shot commands with no historical context:
top                  # real-time but resets on each view
# You see high CPU but can't tell if it's sustained or momentary

# BAD: Only checking CPU and ignoring I/O:
ps aux --sort=-%cpu | head    # only CPU, misses the disk bottleneck
# Server feels slow -> assume CPU -> wrong diagnosis

# GOOD: Systematic resource investigation
# Step 1: Quick overview (vmstat, 5 seconds):
vmstat 1 5 2>&1 | tee /tmp/vmstat_check.txt
# Step 2: Look at each resource:
echo "=== CPU by Core ===" && mpstat -P ALL 1 3
echo "=== Disk I/O ===" && iostat -xz 1 3
echo "=== Memory ===" && free -h && cat /proc/meminfo | grep -E "Dirty:|Writeback:|AnonPages:"
echo "=== Network ===" && sar -n DEV 1 3

# GOOD: Baseline comparison (save current state, compare later):
# Capture baseline during normal operation:
sar -u -b -r -n DEV 1 60 > /tmp/baseline_$(date +%Y%m%d_%H%M).txt
# During incident: compare
sar -u -b -r -n DEV 1 60 > /tmp/incident_$(date +%Y%m%d_%H%M).txt
diff /tmp/baseline*.txt /tmp/incident*.txt
```

**GOOD - production monitoring script:**
```bash
#!/bin/bash
# resource-health.sh: Quick resource health check

CPU_WARN=80       # % CPU usage warning threshold
IOWAIT_WARN=15    # % I/O wait warning threshold
DISK_UTIL_WARN=80 # % disk utilization warning threshold
SWAP_WARN=1       # any swap activity = warn (pages/sec)

echo "=== System Health Check - $(date) ==="

# CPU check via vmstat (skip first row = since boot average):
read -r us sy id wa st < <(vmstat 1 2 | tail -1 | awk '{print $13,$14,$15,$16,$17}')
cpu_used=$((us + sy))
echo "CPU: user=${us}% sys=${sy}% idle=${id}% iowait=${wa}% steal=${st}%"
[[ $cpu_used -gt $CPU_WARN ]] && echo "  WARN: High CPU usage: ${cpu_used}%"
[[ $wa -gt $IOWAIT_WARN ]]    && echo "  WARN: High I/O wait: ${wa}%"
[[ $st -gt 5 ]]               && echo "  WARN: High CPU steal: ${st}% (VM overcommit?)"

# Swap check:
si_so=$(vmstat 1 2 | tail -1 | awk '{print $7+$8}')
[[ $si_so -gt $SWAP_WARN ]] && echo "  ALERT: Swap activity detected: ${si_so} pages/s"

# Disk check:
echo ""
echo "Disk I/O (top devices by utilization):"
iostat -xz 1 2 2>/dev/null | awk '
  /^Device/ {header=1; next}
  header && NF>0 {
    util=$NF
    if (util+0 > 0) printf "  %-12s %util=%.1f%% await=%.1f ms\n", $1, util, $(NF-3)
  }' | sort -t= -k2 -rn | head -5

# Memory check:
echo ""
free_mem=$(free -m | awk 'NR==2{printf "%.0f", $7/$2*100}')
echo "Memory: ${free_mem}% available"
[[ $free_mem -lt 20 ]] && echo "  WARN: Low available memory: ${free_mem}%"

echo ""
echo "Run 'vmstat 1' or 'iostat -xz 1' for detailed continuous monitoring"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "High CPU usage means the system is overloaded" | High CPU usage (us=90%) might be exactly what you want - it means your compute-bound application is using resources efficiently. OVERLOADED means: processes are WAITING for CPU (`r` in vmstat > number of CPUs), meaning the CPU can't keep up. High CPU that completes work = good. High CPU that queues work (r >> CPU count) = bad. |
| "I/O wait percentage is wasted CPU time" | `wa` (iowait) means the CPU is idle BUT at least one I/O is pending. It's NOT CPU being used for I/O - that's not how CPUs work. I/O wait = CPU has nothing else to do while waiting for I/O. High `wa` means I/O is the bottleneck. Low `wa` with low `us` and high `id` means CPU is truly idle. |
| "`free` memory is wasted memory" | `free` memory is NOT wasted. But the "free" column in `free -h` (the first data row) is confusingly named. "available" is the real metric - it includes memory that can be immediately reclaimed from cache. A server with `free=100MB, available=8GB` is healthy (8GB available via cache reclaim). Only worry if `available` is low. |
| "vmstat shows real-time data for the current second" | The FIRST line of vmstat output (without interval) shows averages since boot - not the last second. Always use `vmstat 1` or `vmstat N` with an interval. The first line of interval output shows averages since last boot; subsequent lines show the actual interval. Wait for 2+ samples before drawing conclusions. |
| "High disk %util means I need more disks" | %util > 90% means the device is busy 90% of the time, but it doesn't tell you if the THROUGHPUT is the problem or the LATENCY. An SSD at 95% util with 1ms await might be fine. An HDD at 95% util with 200ms await is severely impacting application performance. Look at `await` and actual throughput vs application requirements to decide if you need more/faster disks. |

---

### Failure Modes & Diagnosis

**I/O wait spike investigation:**
```bash
# Symptom: vmstat shows wa=50%, all user applications slow

# Step 1: Confirm I/O is the bottleneck:
vmstat 1 5
# wa consistently >30%: yes, I/O bottleneck

# Step 2: Which device?
iostat -xz 1 5
# sda: %util=98% await=200ms <- identified

# Step 3: Who is causing the I/O?
iotop -bo -d 1 2>/dev/null ||
  # Fallback: pidstat
  pidstat -d 1 5 | sort -k4 -rn | head -10
# PID X: java process, 100MB/s writes

# Step 4: What is the process writing?
lsof -p PID | grep -E "REG.*[0-9]MB"  # large open files
strace -p PID -e trace=write 2>&1 | head -20  # syscall trace

# Step 5: Is it write burst or sustained?
iostat -xz 1 | grep sda  # watch for 30+ seconds
# Sustained: application design issue, needs async I/O or buffering
# Burst: might resolve, or schedule bulk writes at off-peak hours

# Resolution:
# - Move to faster storage (NVMe SSD)
# - Reduce write frequency (batch writes, async)
# - Add more RAM (page cache reduces reads)
# - I/O scheduling tuning (see LNX-076)
```

---

### Related Keywords

**Foundational:**
LNX-015 (Process Management), LNX-020 (System Monitoring Tools)

**Builds on this:**
LNX-093 (Linux Performance Troubleshooting), LNX-095 (CPU Performance)

**Related:**
LNX-094 (Memory Pressure), OBS-001 (Observability)

---

### Quick Reference Card

| Tool | Command | Measures |
|------|---------|---------|
| vmstat | `vmstat 1` | CPU, memory, swap, I/O overview |
| iostat | `iostat -xz 1` | Per-disk IOPS, throughput, utilization |
| mpstat | `mpstat -P ALL 1` | Per-CPU utilization |
| sar | `sar -u 1 10` | Historical CPU (also: -r memory, -b I/O) |
| dstat | `dstat -tcmdn` | All-in-one real-time view |
| iotop | `iotop -bo` | Per-process I/O |
| pidstat | `pidstat -d 1` | Per-process disk I/O |

**3 things to remember:**
1. `vmstat 1`: column `wa` > 15% = I/O bottleneck; `si`/`so` > 0 = swap pressure; `r` > CPU count = CPU saturated
2. `iostat -xz 1`: `%util` > 90% = disk saturated; `await` > 20ms on SSD = problem
3. First vmstat line = since-boot average; always wait for interval samples (2nd line onward)

---

### Transferable Wisdom

These metrics map directly to: cloud monitoring dashboards (AWS CloudWatch
`CPUUtilization`, `DiskReadBytes`, `NetworkIn`), Kubernetes metrics server
(`kubectl top node/pod` = CPU + memory), Prometheus node_exporter (exposes
vmstat/iostat data as Prometheus metrics for Grafana dashboards), Datadog/
New Relic agents (collect same underlying `/proc` data). The numbers you
read from `vmstat`/`iostat` are the SAME numbers cloud monitoring shows -
just wrapped in a UI.

The USE Method (Utilization, Saturation, Errors) framework: for every
resource (CPU, memory, disk, network): check utilization (busy %), saturation
(queued work), errors (error count). `vmstat` covers utilization; `r` column
covers saturation; `dmesg` covers errors. This mental model applies to any
system: database query analysis (utilization = query time, saturation = queue
depth, errors = failed queries), JVM analysis (CPU util, GC pause time,
OOM errors).

---

### The Surprising Truth

The `await` column in `iostat` that everyone watches is measuring the WRONG
thing for modern SSDs with internal parallelism. Traditional `await` measures
average I/O completion time, but NVMe SSDs process multiple queues in parallel
(up to 65,535 queues of 65,535 requests each). A device might show 5ms `await`
but actually be perfectly healthy because each individual operation takes 0.1ms -
the 5ms reflects queue depth interactions. Brendan Gregg's analysis shows
that `await` on NVMe is often 3-5x higher than actual latency due to how
`iostat` samples the kernel counters. The more reliable metrics for NVMe SSDs
are: `/sys/block/nvme0n1/stat` latency percentiles (50th, 99th), `bpftrace -e
'tracepoint:block:block_rq_complete { @usecs = hist(args->nr_sector * 512); }'`
for actual distribution. BCC's `biolatency` tool gives the real latency
histogram. The practical implication: an NVMe at "20ms await" might be
completely fine, while an HDD at "20ms await" is suffering. Know your storage
type before interpreting `await`.

---

### Mastery Checklist

- [ ] Can read vmstat output and identify CPU, memory, and I/O issues
- [ ] Can use iostat to identify saturated disks and measure latency
- [ ] Can identify per-process I/O culprits using iotop or pidstat
- [ ] Can access historical performance data using sar
- [ ] Can differentiate between CPU-bound, I/O-bound, and memory-pressure scenarios

---

### Think About This

1. `vmstat 1` shows: `us=5 sy=8 id=2 wa=85`. Your first instinct is to
   add more disks. But `iostat -xz 1` shows all disks at %util < 20%.
   How can I/O wait be 85% but disk utilization be 20%? What is the most
   likely cause? (Hint: think about what "I/O wait" actually measures
   and what other I/O sources exist besides local disks.)

2. After deploying a new service, `vmstat 1` shows `cs` (context switches)
   jumping from 50,000/s to 500,000/s. CPU usage is moderate (us=30%,
   sy=25%). Application latency has doubled. What is causing this? Which
   architectural patterns in the new service would cause 10x more context
   switches? How would you investigate and mitigate?

3. sar historical data shows CPU idle (`id`) drops from 70% to 10% every
   day at 2:00 AM, lasting 30 minutes. `wa` during that time is 5%.
   `iostat` shows disk writes peak at 2:00 AM. But no cron jobs are
   scheduled for 2:00 AM. What automated process might be causing this?
   How would you identify it? (Name at least 3 common Linux processes
   that run at scheduled times.)

---

### Interview Deep-Dive

**Foundational:**
Q: Walk me through how you would diagnose a "slow server" complaint using Linux command-line tools.
A: Systematic approach using the USE Method (Utilization, Saturation, Errors) for each resource: (1) Quick overview with `vmstat 1 5`: look at `r` (CPU queue length), `wa` (I/O wait), `si`/`so` (swap activity). This tells me which resource is the primary bottleneck in 5 seconds. (2) CPU: if `us+sy` high and `wa` low: CPU-bound. `mpstat -P ALL 1` to see if one core is maxed (single-threaded) or all cores loaded. `ps aux --sort=-%cpu | head` to identify the process. (3) Memory: if `si`/`so` > 0: actively swapping (severe memory pressure). `free -h` + `cat /proc/meminfo | grep MemAvailable`. If swap active: which process? `ps aux --sort=-%mem | head`. (4) Disk: if `wa` high: I/O-bound. `iostat -xz 1 5` to identify which disk (%util, await). `iotop -bo` to identify which process. (5) Network: `sar -n DEV 1 5` for throughput, `ss -s` for connection stats, `netstat -i` for interface errors. (6) After identifying the resource: dig deeper with process-specific tools (`lsof`, `strace`, `perf top`). Key insight: always check all resources before concluding - the symptom (slow app) might have multiple contributing factors.

**Expert:**
Q: How would you use sar to investigate a performance incident that occurred at 3 AM last night?
A: sar (System Activity Reporter) is the standard tool for historical performance analysis. Setup: `systemctl enable sysstat` and `systemctl start sysstat`. The `sadc` daemon collects data every 10 minutes (configurable in `/etc/sysstat/sysstat` or `/etc/default/sysstat`). Data stored in `/var/log/sysstat/sa<DD>` (daily files). Analysis of 3 AM incident: `sar -u -f /var/log/sysstat/sa$(date -d yesterday +%d) -s 02:50:00 -e 03:30:00` shows CPU data from 2:50 to 3:30 AM. Resources to check: CPU: `sar -u` (us/sy/wa/idle); Memory: `sar -r` (memused%, swpused%); I/O: `sar -b` (read/write IOPS) and `sar -d -p` (per-device); Network: `sar -n DEV` (RX/TX); Load: `sar -q` (run queue, load average). Correlating metrics: if memory usage spikes at 3:00 AM AND disk write IOPS spike AND CPU increases: likely a batch job (backup, cron job, log rotation, database maintenance). If network traffic spikes: DDoS attack or backup to remote storage. Typical 3 AM culprits: `rsync` backup job, `logrotate`, database WAL archiving, `updatedb` (mlocate index update), `apt-daily.timer`, `cron.daily` scripts. Enhancement: enable `SADC_OPTIONS="-S ALL"` in sysstat config for extended collection (network, hugepages, etc.).
