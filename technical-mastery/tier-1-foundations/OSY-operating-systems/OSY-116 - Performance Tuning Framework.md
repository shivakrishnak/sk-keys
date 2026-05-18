---
id: OSY-116
title: Performance Tuning Framework
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-085, OSY-089, OSY-090, OSY-099
used_by: []
related: OSY-115, OSY-117, OSY-119
tags:
  - performance-tuning
  - framework
  - methodology
  - production
  - sysctl
  - Java
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 116
permalink: /technical-mastery/osy/performance-tuning-framework/
---

## TL;DR

A systematic OS performance tuning framework for Java
production services. Covers the diagnosis-before-tuning
principle, the USE method (Utilization, Saturation, Errors),
and specific sysctl/JVM knobs for CPU, memory, I/O, and
networking. Never tune blindly - measure first, change one
variable at a time, validate with a load test.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-116 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | performance tuning, USE method, sysctl, JVM tuning, methodology |
| **Prerequisites** | OSY-085, OSY-089, OSY-090, OSY-099 |

---

### The USE Method (Foundation of Performance Tuning)

```
USE = Utilization, Saturation, Errors

Brendan Gregg's framework for systematic performance analysis:

For every resource (CPU, memory, disk, network):
  
  Utilization: % of time the resource is busy
    Low utilization: resource not the bottleneck
    High utilization (> 70%): resource may be bottleneck
    
  Saturation: work waiting for the resource
    > 0: resource is overloaded (work queuing)
    Queue depth > 1: definite saturation
    
  Errors: error events in the resource path
    Dropped packets, corrected ECC errors, disk errors
    Any error = investigate regardless of utilization

Apply to each layer:
  CPU: utilization = us+sy%, saturation = load average > N_CPU
  Memory: utilization = used/total, saturation = swap, OOM
  Disk: utilization = %util (iostat), saturation = avgqu-sz > 1
  Network: utilization = Mbps/max, saturation = retransmits
  
Start with the resource showing BOTH high utilization AND saturation.
That resource is likely the bottleneck.
```

---

### Diagnosis Workflow (Before Any Tuning)

```bash
# Phase 1: Macro view (< 2 minutes)
top          # CPU, load average, memory at a glance
vmstat 1 5   # CPU states, memory, I/O, context switches
iostat -x 1  # disk utilization and latency
ss -s        # socket summary (connections, TIME_WAIT count)

# Phase 2: Identify the bottleneck
# CPU-bound: high us%, load average > N_CPU
# Memory-bound: high swap usage, major page faults
# I/O-bound: high wa%, iostat %util near 100%
# Network-bound: ss shows high retransmits, drops

# Phase 3: Drill into the bottleneck
# If CPU: perf top / async-profiler / jstack for hot methods
# If memory: jcmd PID VM.native_memory / heap dump
# If I/O: iotop, iostat -xz, blktrace
# If network: ss -tin, netstat -s | grep -i retrans

# Phase 4: Form a hypothesis
# Write it down: "I believe X is causing Y because Z"
# Testable: "If I change A, metric B should change by C"

# Phase 5: Change ONE thing; measure; validate
# Never change multiple tuning parameters simultaneously
# Before: record baseline metrics
# After: same workload, same duration; compare
```

---

### CPU Tuning

```bash
# Identify what CPUs are doing:
perf stat -a sleep 10
# Instructions per cycle (IPC): low IPC = memory-bound
# Cache misses: high = thrashing

# Check CPU frequency scaling:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# performance: always max frequency (use for latency-sensitive)
# powersave: saves power; slower ramp-up
# Tuning for Java services: performance governor
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Check NUMA topology:
numactl --hardware
# Cores per NUMA node, memory per node
# For JVM on multi-socket: numactl --interleave=all java ...
# Or: numactl --membind=0 --cpunodebind=0 java ... (pin to NUMA node)

# Disable CPU frequency throttling in BIOS (if possible):
# Look for: Intel SpeedStep, AMD Cool'n'Quiet, C-states
# These cause latency spikes on first requests after idle

# Isolate CPUs for a latency-sensitive Java service:
# Kernel boot param: isolcpus=4-7 (don't schedule OS tasks on 4-7)
# Then pin Java: taskset -c 4-7 java -jar app.jar
# Result: Java gets CPUs 4-7 exclusively; OS tasks on 0-3
```

---

### Memory Tuning

```bash
# Check for swap usage (any swap = problem for Java):
free -h
swapon --show
# If swap used: reduce RSS or add RAM
# Prevent JVM from swapping:
# /etc/security/limits.conf: java soft memlock unlimited
# JVM option: -XX:+AlwaysPreTouch (touch all pages at startup)

# vm.swappiness - how aggressively OS uses swap:
cat /proc/sys/vm/swappiness  # default: 60
# For Java production servers:
sysctl vm.swappiness=1       # strongly prefer not swapping
# Not 0: can cause issues with some cgroup memory reclaim

# Dirty page thresholds:
cat /proc/sys/vm/dirty_background_ratio  # 10 (default)
cat /proc/sys/vm/dirty_ratio             # 20 (default)
# Background writeback starts at 10% of RAM dirty
# Forced writeback (blocks writes) at 20%
# For write-heavy services: reduce to avoid burst flushes:
sysctl vm.dirty_background_ratio=2
sysctl vm.dirty_ratio=5

# Huge pages for JVM (reduces TLB pressure for large heaps):
# Method 1: Transparent Huge Pages (automatic, possible latency spikes)
echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
# madvise: only use THP when explicitly requested (better for Java)

# Method 2: Explicit huge pages (pre-allocated, no collapse spikes)
sysctl vm.nr_hugepages=2048   # 2048 * 2MB = 4GB huge pages
java -XX:+UseHugeTLBFS -Xmx3g -jar app.jar
```

---

### I/O Tuning

```bash
# Determine device type and optimal scheduler:
cat /sys/block/sda/queue/rotational  # 1=HDD, 0=SSD/NVMe
cat /sys/block/sda/queue/scheduler

# Scheduler recommendations:
# HDD: mq-deadline or bfq (elevator scheduling useful)
# SSD/NVMe: none or mq-deadline (no seek time; don't reorder)
echo mq-deadline > /sys/block/nvme0n1/queue/scheduler

# Queue depth (how many I/Os can be in flight):
cat /sys/block/sda/queue/nr_requests  # default: 128
# For NVMe: higher queue depth can help throughput
echo 512 > /sys/block/nvme0n1/queue/nr_requests

# Read-ahead (how much to prefetch on sequential reads):
blockdev --getra /dev/sda  # in 512B sectors
# Default: 256 (128KB)
# For large sequential reads (data pipeline, logs):
blockdev --setra 4096 /dev/sda  # 2MB read-ahead

# Mount options for performance:
# noatime: don't update access time on reads (reduces writes)
# nodiratime: same for directories
# data=writeback (ext4): faster writes, less metadata safety
# mount -o remount,noatime /data

# Java FileChannel tuning:
# For append-only log writes: use ByteBuffer + direct I/O
FileChannel channel = FileChannel.open(
    path,
    StandardOpenOption.WRITE,
    StandardOpenOption.APPEND,
    StandardOpenOption.CREATE
);
// For maximum write throughput: batch writes to > 4KB
// Avoid: many small writes (each = syscall + page cache dirty)
```

---

### Network Tuning

```bash
# Check for retransmits (sign of congestion or packet loss):
netstat -s | grep -i retransmit

# TCP buffer tuning for high-throughput services:
sysctl net.core.rmem_max     # default: 212992 (208KB)
sysctl net.core.wmem_max     # default: 212992
sysctl net.ipv4.tcp_rmem     # min default optimal
sysctl net.ipv4.tcp_wmem

# For services that transfer large amounts of data:
sysctl net.core.rmem_max=16777216       # 16MB
sysctl net.core.wmem_max=16777216
sysctl net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl net.ipv4.tcp_wmem="4096 65536 16777216"

# TIME_WAIT connections (too many = port exhaustion):
ss -tan state time-wait | wc -l
# Normal: hundreds; Problem: > 10,000
sysctl net.ipv4.tcp_tw_reuse=1  # reuse TIME_WAIT sockets safely
# DO NOT use tcp_tw_recycle (removed in Linux 4.12; dangerous)

# Connection backlog for high-load servers:
sysctl net.core.somaxconn        # default: 128 (too low!)
sysctl net.core.somaxconn=32768
# Spring Boot also: server.tomcat.accept-count=200

# Local port range (for outbound connections):
cat /proc/sys/net/ipv4/ip_local_port_range  # 32768-60999
# For services making many outbound connections:
sysctl net.ipv4.ip_local_port_range="1024 65535"
```

---

### Tuning Anti-Patterns

| Anti-Pattern | Why It's Wrong | Right Approach |
|-------------|----------------|----------------|
| Tuning without measuring | May tune the wrong resource | USE method first; identify bottleneck |
| Changing multiple params at once | Can't attribute improvement to any change | One change per test cycle |
| Applying generic "Java production sysctl" blindly | Every workload is different | Measure your workload; apply targeted tunings |
| Setting vm.swappiness=0 | Can break cgroup memory reclaim in some kernels | Use 1, not 0 |
| Disabling THP completely on large-heap JVM | May increase TLB pressure on large heaps | Use madvise mode or explicit huge pages |
| Increasing thread count to fix I/O | More threads = more context switches, not faster I/O | Fix the I/O bottleneck (caching, async I/O) |

---

### Validation Template

```
Before tuning:
  Workload: 10K req/s, 8 cores, 30G heap
  p99 latency: 200ms
  CPU: 70% utilization
  Context switches: 150K/sec
  iowait: 5%
  
Change: vm.swappiness=1, THP=madvise, cpufreq=performance

After tuning (same workload, 30-min run):
  p99 latency: 180ms (-10%)
  CPU: 68% utilization (-3%)
  Context switches: 140K/sec (-7%)
  iowait: 5% (unchanged)
  
Conclusion: small improvement; latency reduction from
cpufreq (no frequency scaling latency on first requests);
not the primary bottleneck; investigate further.
```
