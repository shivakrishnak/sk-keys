---
layout: default
title: "Linux Performance Tuning"
parent: "Linux"
nav_order: 165
permalink: /linux/linux-performance-tuning/
number: "0165"
category: Linux
difficulty: ★★★
depends_on: Linux File System Hierarchy, /proc File System, /sys File System
used_by: Site Reliability Engineering, DevOps, Systems Programming
related: /proc File System, /sys File System, Cgroups, Observability
tags:
  - linux
  - os
  - performance
  - sre
  - deep-dive
---

# 165 — Linux Performance Tuning

⚡ TL;DR — Linux performance tuning is the art of identifying the binding constraint (CPU, memory, I/O, network, or contention) and adjusting kernel parameters, scheduling, I/O, and memory settings to remove that constraint — always measuring before and after, never tuning by intuition alone.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java microservice handles 500 requests/second in testing but only 200/second in production on the same hardware. The developer assumes it needs more instances. They add 3 more replicas — cost doubles. Throughput improves to 250/second. Something is fundamentally wrong. The problem isn't capacity — it's configuration.

**THE BREAKING POINT:**
Linux defaults are optimised for general-purpose workloads, not for high-throughput databases, network proxies, or latency-sensitive services. The default TCP receive buffer (87KB) may be far too small for a 10Gbps NIC. The default I/O scheduler may be optimised for rotational disks on an SSD system. The default virtual memory pressure settings may cause application swap thrashing that makes response times unpredictable.

**THE INVENTION MOMENT:**
Linux exposes virtually every kernel parameter through `/proc/sys/` and `/sys/` virtual filesystems — sysctl settings, I/O scheduler choices, CPU frequency governors, TCP buffer sizes, NUMA policies, huge pages, and more. Linux performance tuning is the discipline of: (1) measuring to identify the bottleneck; (2) understanding which kernel settings affect that bottleneck; (3) applying targeted changes; (4) measuring again to verify improvement. Without measurement, tuning is guesswork.

---

### 📘 Textbook Definition

**Linux performance tuning** is the systematic process of: (1) profiling system and application behaviour under realistic load; (2) identifying the resource that is the binding constraint (CPU, memory bandwidth, disk I/O, network I/O, or lock contention); (3) adjusting Linux kernel configuration — via sysctl, scheduler parameters, I/O scheduler, NUMA topology, transparent huge pages, CPU frequency scaling, and network stack settings — to better match workload characteristics; (4) validating that the change produced the intended improvement without introducing regressions. Primary reference: USE method (Brendan Gregg): for each resource, measure Utilisation, Saturation, and Errors.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Find the bottleneck with data, tune the specific kernel setting that controls it, measure again — never tune by assumption.

**One analogy:**

> Performance tuning is like diagnosing a car that won't reach highway speed. You don't just replace the engine (more hardware). You first check: is the handbrake on (lock contention)? Is the fuel line narrow (I/O bandwidth)? Are the tyres under-inflated (memory pressure)? Is the throttle cable stretched (CPU scheduler)? Each symptom points to a specific system. Fixing the wrong thing costs time and money and doesn't help. Measure, diagnose the binding constraint, fix specifically.

**One insight:**
The USE method (Utilisation, Saturation, Errors) is the most systematic approach to performance diagnosis. For each resource: is it fully utilised? Is there a queue forming (saturation)? Are there errors? These three questions per resource typically identify the bottleneck within minutes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Every system has one binding constraint** (Theory of Constraints): fixing non-bottlenecks wastes effort and may move the constraint elsewhere.
2. **Measure before and after**: without baseline and post-change measurements, you don't know if a change helped or harmed.
3. **Regressions happen**: a change that improves throughput may worsen latency, or vice versa; test all relevant dimensions.
4. **Workload-specific tuning**: a setting optimal for a database is counterproductive for a web server; there are no universal "performance settings."

**TUNING DOMAINS:**

_CPU tuning:_

- CPU frequency governor: `performance` (max frequency, low latency) vs `ondemand` (power saving)
- `taskset`/`numactl`: pin processes to specific CPUs/NUMA nodes
- IRQ affinity: spread NIC interrupt handling across CPUs
- `CONFIG_HZ`: kernel tick rate (100/250/1000 Hz) — 1000Hz better for latency

_Memory tuning:_

- `vm.swappiness`: 0–100, how aggressively to swap (60 default; set to 1–10 for servers)
- `vm.dirty_ratio` / `vm.dirty_background_ratio`: how much dirty data before writeback
- Transparent Huge Pages (THP): enabled by default; causes latency spikes for some workloads (databases often disable)
- NUMA: `numactl --membind=0` pins memory to local NUMA node; reduces cross-NUMA memory latency

_I/O tuning:_

- I/O schedulers: `none`/`mq-deadline` (SSDs), `bfq` (rotational + latency-sensitive), `kyber` (NVMe)
- Read-ahead: `blockdev --setra 128 /dev/sda` (tune for streaming vs random I/O)
- `noatime` mount option: eliminate access time updates (reduce write I/O)
- `deadline` tuning for databases: max latency guarantees

_Network tuning:_

- TCP buffers: `net.core.rmem_max`, `net.core.wmem_max`, `net.ipv4.tcp_rmem`, `net.ipv4.tcp_wmem`
- `net.core.somaxconn`: listen backlog (increase for high-connection-rate servers)
- `net.ipv4.tcp_max_syn_backlog`: SYN queue depth
- `net.ipv4.ip_local_port_range`: ephemeral port range (extend for high outbound connection count)
- `net.ipv4.tcp_tw_reuse`: reuse TIME_WAIT sockets (safe to enable)
- Ring buffer sizes: `ethtool -G eth0 rx 4096` (NIC receive ring)

**THE TRADE-OFFS:**
Every tuning knob involves a trade-off: larger TCP buffers consume more memory; disabling THP helps databases but harms JVM heap-intensive workloads; setting `vm.swappiness=0` prevents swapping but may cause OOM on memory pressure; `performance` CPU governor increases power consumption.

---

### 🧪 Thought Experiment

**SETUP:**
A PostgreSQL server on a 32-core, 128GB, NVMe SSD server processes 10,000 queries/second in testing but only 3,000/second in production under load.

**DIAGNOSIS STEPS:**

**Step 1: CPU utilisation (`top`, `mpstat`):**

```
CPU usage: 25% user, 5% sys, 70% idle
→ Not CPU-bound. CPU is not the bottleneck.
```

**Step 2: I/O wait (`iostat -x 1`):**

```
Device: util 95%, await 80ms, %iowait 65%
→ I/O saturated! Disk is the bottleneck.
```

**Step 3: What kind of I/O (`iotop`, `blktrace`):**

```
PostgreSQL doing 90% random reads
I/O scheduler: mq-deadline (set for HDD, not NVMe)
Read-ahead: 256 sectors (counterproductive for random I/O)
```

**CHANGES:**

1. I/O scheduler → `none` (NVMe handles its own scheduling)
2. Read-ahead → 8 sectors (random I/O: reduce read-ahead)
3. `vm.dirty_background_ratio` → 5% (flush dirty pages sooner)
4. `vm.swappiness` → 1 (prevent swapping under memory pressure)

**RESULT:** 9,500 queries/second. The issue was I/O scheduler mismatch, not capacity.

**THE INSIGHT:**
The 30 minutes of measurement before touching any settings saved weeks of over-provisioning. The bottleneck was entirely in configuration, not hardware.

---

### 🧠 Mental Model / Analogy

> Linux performance tuning is like optimising a kitchen during dinner service. You observe: the bottleneck is the single oven (I/O), not the chefs (CPU) or the prep area (memory). Adding more chefs or prep counters (CPU/memory scaling) won't help. The fix: use the oven optimally — group similar dishes (I/O scheduler), preheat correctly (read-ahead tuning), coordinate timing (TCP buffer sizing). After the change, you measure again: is the oven now the bottleneck, or has the constraint shifted to plating (network)? Performance tuning is never "done" — the constraint shifts.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Linux performance tuning means adjusting the operating system's settings to make it work better for a specific type of job. Just like you'd arrange a workshop differently for woodworking vs metalworking, Linux can be configured differently for databases vs web servers vs video streaming. The key is: measure what's actually slow before changing anything.

**Level 2 — How to use it (junior developer):**
Quick wins: check current settings with `sysctl -a | grep <param>`. Apply temporarily: `sysctl -w vm.swappiness=10`. Apply permanently: add to `/etc/sysctl.d/99-performance.conf`. Check I/O scheduler: `cat /sys/block/sda/queue/scheduler`. Change scheduler: `echo mq-deadline > /sys/block/sda/queue/scheduler`. Use Brendan Gregg's USE method: `top`, `iostat -x 1`, `free -h`, `ss -s`, `vmstat 1`.

**Level 3 — How it works (mid-level engineer):**
Key sysctl namespaces: `vm.*` (virtual memory), `net.ipv4.*` / `net.core.*` (networking), `kernel.*` (scheduler and process), `fs.*` (file system). Changes via `sysctl` modify `/proc/sys/<namespace>/<parameter>` in real time. I/O schedulers (Linux 5+): BFQ (Budget Fair Queuing — latency guarantees, good for mixed workloads), mq-deadline (hard deadline enforcement, good for databases), kyber (high IOPS SSDs/NVMe), none (let device do its own scheduling — best for NVMe). CPU governor (`/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`): `performance` (max frequency always — lowest latency), `powersave` (minimum frequency), `ondemand`/`schedutil` (dynamic — balances latency and power). NUMA: `numactl --hardware` shows NUMA topology. Cross-NUMA memory access is 30-50% slower. Bind latency-sensitive processes with `numactl -N 0 -m 0 myprocess`.

**Level 4 — Why it was designed this way (senior/staff):**
Linux's performance tuning philosophy reflects the kernel's design goal: general-purpose OS for diverse workloads. The defaults represent conservative choices that work adequately for most cases but are not optimal for any specific case. The design decision to expose all tuning parameters via `sysfs`/`procfs` means no recompilation is needed for tuning — changes can be applied and reverted dynamically. This is a deliberate contrast to Windows, where many performance settings require registry edits and reboots. The modern performance toolchain (Brendan Gregg's BCC/eBPF tools: `execsnoop`, `biolatency`, `tcpretrans`, `offcputime`) represents a shift from sampling-based profiling to always-on, low-overhead tracing built into the kernel. eBPF-based profiling can answer "why is this specific syscall slow?" without any instrumentation overhead.

---

### ⚙️ How It Works (Mechanism)

**USE Method — systematic diagnosis:**

```bash
# UTILISATION: how busy is each resource?
# CPU
top          # overall CPU %
mpstat -P ALL 1  # per-CPU breakdown

# Memory
free -h           # RAM/swap usage
vmstat 1 5        # memory pressure, swap in/out

# Disk I/O
iostat -x 1       # per-device: util%, await, iops
iotop -b -n 3     # per-process I/O

# Network
sar -n DEV 1      # per-interface bytes/packets
ss -s             # socket stats summary

# SATURATION: are queues building up?
# CPU: load average > number of cores?
uptime
# Memory: is swap being used? High vmstat 'si'/'so'?
vmstat 1 | awk '{print $7, $8}'  # swap in/out
# Disk: are requests queueing?
iostat -x 1 | grep -A 20 Device | awk '{print $1, $8, $9}'
# avgqu-sz > 1 = saturated

# ERRORS: any hardware or software errors?
dmesg | grep -i "error\|fail\|warn" | tail -20
cat /proc/net/dev | awk '{print $1, $4, $13}'  # drops/errors
```

**Virtual memory tuning:**

```bash
# Check current swappiness
sysctl vm.swappiness
# vm.swappiness = 60 (default)

# For a database server: minimise swapping
echo "vm.swappiness = 1" | sudo tee -a \
  /etc/sysctl.d/99-db-performance.conf
sudo sysctl -p /etc/sysctl.d/99-db-performance.conf

# Transparent Huge Pages (THP) — check
cat /sys/kernel/mm/transparent_hugepage/enabled
# [always] madvise never

# Disable THP for databases (PostgreSQL, MongoDB, Redis)
echo never | sudo tee \
  /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee \
  /sys/kernel/mm/transparent_hugepage/defrag
# Make permanent:
# Add to /etc/rc.local or a systemd service

# Dirty page writeback tuning (reduce write bursts)
echo "vm.dirty_background_ratio = 5" | sudo tee -a \
  /etc/sysctl.d/99-performance.conf
echo "vm.dirty_ratio = 10" | sudo tee -a \
  /etc/sysctl.d/99-performance.conf
```

**Network stack tuning:**

```bash
# /etc/sysctl.d/99-network-performance.conf

# TCP buffer sizes (for 10Gbps networks)
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Backlog for high-connection-rate servers
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Ephemeral ports (for outbound-heavy proxies)
net.ipv4.ip_local_port_range = 1024 65535

# Reuse TIME_WAIT sockets
net.ipv4.tcp_tw_reuse = 1

# Apply:
sysctl --system
```

**I/O scheduler tuning:**

```bash
# Check current scheduler per device
cat /sys/block/sda/queue/scheduler
# [mq-deadline] kyber bfq none

# For NVMe SSD: use 'none' (hardware does own scheduling)
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler

# For a mixed-use SSD: bfq (latency + fairness)
echo bfq | sudo tee /sys/block/sda/queue/scheduler

# Make permanent via udev rule:
cat > /etc/udev/rules.d/60-scheduler.rules << 'EOF'
# NVMe: no scheduler
ACTION=="add|change", KERNEL=="nvme*", \
  ATTR{queue/scheduler}="none"
# SATA SSD: mq-deadline
ACTION=="add|change", KERNEL=="sd*", \
  ATTR{queue/rotational}=="0", \
  ATTR{queue/scheduler}="mq-deadline"
# HDD: bfq
ACTION=="add|change", KERNEL=="sd*", \
  ATTR{queue/rotational}=="1", \
  ATTR{queue/scheduler}="bfq"
EOF
udevadm control --reload-rules
```

**CPU frequency and NUMA:**

```bash
# Check available governors
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# conservative ondemand userspace powersave performance schedutil

# Set performance governor for all CPUs
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
  echo performance | sudo tee $cpu
done

# Check NUMA topology
numactl --hardware
# available: 2 nodes (0-1)
# node 0 cpus: 0-15
# node 1 cpus: 16-31

# Pin process to NUMA node 0 (local memory)
numactl --cpunodebind=0 --membind=0 ./myprocess

# Check NUMA memory statistics
numastat -p <pid>
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Performance tuning workflow (USE method)      │
└────────────────────────────────────────────────┘

 SYMPTOM: Application latency increased 3x

 1. MEASURE BASELINE
    ├── p50=20ms, p99=450ms (target: p99<100ms)
    └── Request rate: 500 rps

 2. USE METHOD — check each resource:
    ├── CPU: 15% utilised, load avg 0.8  → NOT bound
    ├── Memory: 85% used, swap: 0        → NOT bound
    ├── Disk I/O: 98% util, await=120ms  → SATURATED ←
    └── Network: 10% bandwidth           → NOT bound

 3. DRILL INTO I/O:
    ├── iotop: PostgreSQL doing 80% of I/O
    ├── iostat: random reads, large await
    └── Scheduler: bfq (set for HDD, disk is NVMe!)

 4. TUNE:
    ├── Set scheduler to 'none' for NVMe
    ├── Reduce read-ahead (random I/O)
    └── vm.dirty_background_ratio: 10→5

 5. MEASURE POST-CHANGE:
    ├── Disk util: 45%, await: 8ms  → RESOLVED
    └── p50=18ms, p99=75ms          → TARGET MET ✓

 6. DOCUMENT:
    └── Add settings to /etc/sysctl.d/
        and udev rules (permanent)
```

---

### 💻 Code Example

**Example — Performance baseline script:**

```bash
#!/bin/bash
# performance-baseline.sh
# Collect a 60-second performance snapshot

DURATION=60
OUT_DIR="/tmp/perf-baseline-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT_DIR"

echo "Collecting ${DURATION}s performance baseline..."
echo "Output: $OUT_DIR"

# CPU and memory
vmstat 1 $DURATION > "$OUT_DIR/vmstat.txt" &
mpstat -P ALL 1 $DURATION > "$OUT_DIR/mpstat.txt" &

# I/O
iostat -x 1 $DURATION > "$OUT_DIR/iostat.txt" &

# Network
sar -n DEV 1 $DURATION > "$OUT_DIR/sar-net.txt" &

# Socket stats (snapshot, repeated)
for i in $(seq 1 10); do
  echo "=== $(date) ===" >> "$OUT_DIR/ss-stats.txt"
  ss -s >> "$OUT_DIR/ss-stats.txt"
  sleep 6
done &

wait
echo ""
echo "=== SUMMARY ==="
echo "CPU (avg utilisation):"
awk '/^[0-9]/{cpu+=$3; count++} END{printf "  User: %.1f%%\n", cpu/count}' \
  "$OUT_DIR/mpstat.txt"

echo "Memory:"
awk '/^[0-9]+/{if(NR==2) printf "  Used: %dMB, Swap: %dMB\n", $4/1024, $8/1024}' \
  "$OUT_DIR/vmstat.txt"

echo "I/O (max util device):"
awk '/^[a-z]/{if($NF+0 > max){max=$NF; dev=$1}} END{printf "  %s: %.1f%% util\n", dev, max}' \
  "$OUT_DIR/iostat.txt"

echo ""
echo "Files in: $OUT_DIR"
```

---

### ⚖️ Comparison Table

| Parameter            | Default     | High-Throughput DB | High-Concurrency Web | Latency-Sensitive |
| -------------------- | ----------- | ------------------ | -------------------- | ----------------- |
| `vm.swappiness`      | 60          | 1                  | 10                   | 1                 |
| `vm.dirty_ratio`     | 20%         | 10%                | 15%                  | 5%                |
| THP                  | always      | disabled           | madvise              | disabled          |
| I/O scheduler (NVMe) | mq-deadline | none               | none                 | none              |
| `net.core.somaxconn` | 128         | 4096               | 65535                | 4096              |
| CPU governor         | ondemand    | performance        | performance          | performance       |
| NUMA policy          | default     | bind               | interleave           | bind              |

How to choose: always start from measurements; apply workload-appropriate settings from the relevant application documentation (PostgreSQL tuning guide, Redis config guide, nginx performance guide); never copy-paste "performance settings" without understanding the trade-offs.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                   |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More RAM always solves performance problems        | If the bottleneck is I/O scheduler, CPU affinity, or lock contention, adding RAM does nothing                                                             |
| Default kernel settings are "safe"                 | Defaults are safe for general workloads; for specific workloads (databases, high-concurrency servers), defaults cause significant performance degradation |
| `vm.swappiness=0` disables swap                    | `vm.swappiness=0` tells the kernel to avoid swapping unless absolutely necessary — it does not disable swap entirely; use `swapoff -a` to disable swap    |
| Transparent Huge Pages always improves performance | THP causes latency spikes during page compaction; databases (PostgreSQL, MongoDB, Redis) explicitly recommend disabling THP                               |
| Tuning is a one-time activity                      | Application behaviour, traffic patterns, and hardware change; performance baseline and tuning review should be part of regular operations                 |

---

### 🚨 Failure Modes & Diagnosis

**Periodic Latency Spikes Despite Low Average Utilisation**

**Symptom:**
P50 latency is fine (5ms). P99 latency spikes to 2 seconds every few minutes. CPU, memory, and I/O all show low average utilisation.

**Root Cause:**
THP compaction: the kernel is compacting memory to create 2MB huge pages, stalling processes for 100-500ms during compaction. Or: dirty page writeback burst — when `vm.dirty_ratio` (20%) is hit, the kernel stalls writers while it flushes dirty pages synchronously.

**Diagnostic Commands:**

```bash
# Check for THP compaction stalls
grep -i "compaction\|thp\|defrag" /proc/vmstat
# compact_stall > 0 → THP compaction stalls

# Check dirty page writeback timing
sar -B 1 10
# pgscank/s and pgscand/s high → memory pressure scanning

# Check for write stalls
iostat -x 1 | awk '/^[a-z]/{print $1, $8, $10}'
# Large await spikes despite low average

# Real-time latency histogram (BCC tool)
biolatency -D 10 1  # disk I/O latency histogram
```

**Fix:**
Disable THP: `echo never > /sys/kernel/mm/transparent_hugepage/enabled`. Tune dirty ratios: `vm.dirty_background_ratio=5`, `vm.dirty_ratio=10`. Enable per-BDI writeback with `vm.dirty_writeback_centisecs=500`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `/proc File System` — most performance metrics come from `/proc/stat`, `/proc/meminfo`, `/proc/net/dev`; understanding this filesystem is foundational
- `/sys File System` — I/O schedulers, CPU governors, and device settings are configured via `/sys`; performance tuning is largely writing to sysfs
- `Linux File System Hierarchy` — understanding where configuration files live (`/etc/sysctl.d/`, `/sys/`, `/proc/`) is required

**Builds On This (learn these next):**

- `Cgroups` — resource limits via cgroups complement performance tuning; cgroups provide per-workload guarantees
- `Observability & SRE` — performance tuning is part of the SRE toolbox; metrics, tracing, and profiling enable the measurement-first approach

**Alternatives / Comparisons:**

- `Application-level tuning` — JVM flags, connection pool sizes, query optimisation — often higher ROI than OS tuning
- `Hardware upgrades` — faster NVMe, more RAM — justified only after demonstrating the hardware is the bottleneck
- `eBPF profiling tools (BCC/bpftrace)` — modern approach to performance analysis; lower overhead than traditional profiling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Systematic kernel configuration to match  │
│              │ workload needs: CPU, memory, I/O, network │
├──────────────┼───────────────────────────────────────────┤
│ RULE #1      │ MEASURE FIRST. Find the binding           │
│              │ constraint with USE method before         │
│              │ changing any setting                      │
├──────────────┼───────────────────────────────────────────┤
│ USE METHOD   │ For each resource:                        │
│              │ Utilisation? Saturation? Errors?          │
├──────────────┼───────────────────────────────────────────┤
│ QUICK WINS   │ vm.swappiness=1 (servers)                 │
│              │ THP disabled (databases)                  │
│              │ I/O scheduler=none (NVMe)                 │
│              │ tcp buffers enlarged (high-BW networks)   │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG FILES │ /etc/sysctl.d/99-perf.conf                │
│              │ /etc/udev/rules.d/60-scheduler.rules      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Find the stuck brake, release it —       │
│              │ adding engine power won't help"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ eBPF → BCC tools → flame graphs           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Redis instance on a server with 2 NUMA nodes (each with 16 cores and 64GB RAM) is showing 40% higher latency than expected. Describe the NUMA-related performance problem that may be occurring, how to diagnose it using `numastat` and `perf stat`, what the `numactl --membind` and `--cpunodebind` flags would need to be set to, and why Redis's single-threaded main loop makes NUMA pinning especially important compared to a multi-threaded application.

**Q2.** You're handed a Linux system that "feels slow" with no other information. Describe the complete 15-minute diagnostic process using the USE method: what commands you run, in what order, what metric values indicate saturation vs normal operation for each resource type (CPU, memory, disk, network), and how you would distinguish between: (a) a runaway process consuming CPU, (b) a swap storm, (c) a full disk I/O queue, and (d) a network receive buffer overflow — citing specific `vmstat`, `iostat`, and `ss` output fields for each.
