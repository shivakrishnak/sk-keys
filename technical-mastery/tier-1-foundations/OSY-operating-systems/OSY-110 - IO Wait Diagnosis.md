---
id: OSY-110
title: I/O Wait Diagnosis
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-015, OSY-016, OSY-089, OSY-090
used_by: []
related: OSY-109, OSY-111, OSY-116
tags:
  - I/O-wait
  - diagnosis
  - iostat
  - iotop
  - production
  - disk
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 110
permalink: /technical-mastery/osy/io-wait-diagnosis/
---

## TL;DR

I/O wait (iowait in top/vmstat) is the percentage of time
CPUs are idle waiting for disk I/O completion. High iowait
(> 20%) indicates disk bottleneck. Diagnosis: identify the
process (iotop), device (iostat), and operation type
(random reads, sequential writes, sync flushes). Fixes vary:
add caching, tune I/O scheduler, increase queue depth, or
switch from HDD to NVMe.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-110 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | iowait, I/O bottleneck, iostat, iotop, disk performance |
| **Prerequisites** | OSY-015, OSY-016, OSY-089, OSY-090 |

---

### Understanding iowait

```
CPU states (top's display):
  us: user-space CPU time (your application)
  sy: kernel/system CPU time (syscalls, kernel)
  ni: nice'd processes
  id: idle (CPU has nothing to do)
  wa: iowait (CPU idle, waiting for I/O to complete)
  hi: hardware interrupt handling
  si: software interrupt handling
  st: time stolen by hypervisor (in VMs)
  
iowait definition:
  The CPU is IDLE but cannot be used because:
    At least one process is blocking on disk I/O
    CPU is waiting for that I/O to complete
    
  iowait = 0%: disk I/O never blocks CPUs (fast enough, or cached)
  iowait = 20%: 20% of CPU time wasted waiting for disk
  iowait = 80%: application completely disk-bound
  
  Important nuance:
    iowait is PER CPU measurement
    8-core machine: each core independently measured
    If only 1 of 8 cores is waiting: iowait = 12.5% max
    One process saturating one disk: remaining 7 cores free
    
  False positives:
    High iowait can mean slow disk I/O OR
    Just that the CPUs happen to be idle AND some I/O is in flight
    Use iostat to confirm ACTUAL disk utilization
```

---

### Diagnosis Workflow

```bash
# Step 1: Confirm I/O wait is happening
top -1  # -1: show all CPUs separately
# Or:
vmstat 1 10
# wa column: iowait percentage
# bi (blocks in): disk reads; bo (blocks out): disk writes

# Step 2: Identify which process is doing I/O
iotop -o  # -o: only show processes doing I/O
# Shows: process name, read DISK bandwidth, write DISK bandwidth
# Sort by: 'd' for DISK READ, 'w' for DISK WRITE

# For a specific process:
iotop -p $PID -o -b -n 5  # 5 samples, batch mode

# Step 3: Identify which device is saturated
iostat -xz 1 5  # 5 samples, 1-second intervals
# Key columns:
# %util: how busy is the device (100% = saturated)
# await: average I/O latency (ms from submit to complete)
# svctm: service time (estimated; time in device itself)
# r/s, w/s: reads and writes per second
# rMB/s, wMB/s: throughput
# rrqm/s, wrqm/s: merged requests (sequential I/O merging)
# avgqu-sz: average queue depth (> 1 = queued requests)

# If util = 100% and await >> svctm: queue building up
# If util < 100% but await high: device is slow (HDD random reads)

# Step 4: Identify what type of I/O
iostat -x 1: check r/s vs rMB/s ratio
  # Many r/s, low rMB/s: random reads (4KB each)
  # Few r/s, high rMB/s: sequential reads (large reads)
  
blktrace -d /dev/sdb -o - | blkparse -i -  # per-request tracing
# More detailed: specific block addresses (sequential vs random?)

# Step 5: Identify why (page cache miss or forced sync?)
perf trace -e block:block_rq_complete -p $PID -- sleep 10
# Shows each I/O request: size, latency, operation type
```

---

### Common I/O Wait Scenarios

```
Scenario 1: Random Read-Heavy (Database)
  
  iostat shows:
    r/s = 10000 (many small reads)
    rMB/s = 39 (4KB each: 10000 * 4096 = 39MB/s)
    await = 5ms (high for SSD; normal for HDD)
    %util = 95%
    
  Analysis: database doing random reads
    Random 4KB reads on HDD: 200 IOPS max
    Random 4KB reads on SATA SSD: 100K IOPS max
    Random 4KB reads on NVMe: 700K-1M IOPS max
    
  Fixes:
    Add more RAM for page cache (reads from cache = zero iowait)
    Increase database buffer pool (InnoDB buffer pool, Postgres shared_buffers)
    Upgrade storage: HDD -> SSD -> NVMe
    
Scenario 2: Dirty Page Flush Spikes (Write-Heavy Service)
  
  iostat shows: periodic %util = 100% for 10-15 seconds
    Then back to normal
    Periodic pattern: every 30 seconds
    
  Analysis: pdflush/writeback flushing dirty pages
    vm.dirty_writeback_centisecs = 3000 (30s)
    At flush time: burst of writes; device saturated
    
  Fix: lower dirty thresholds to flush continuously:
    sysctl vm.dirty_background_ratio=2
    sysctl vm.dirty_ratio=5
    Lower vm.dirty_writeback_centisecs=500 (5 second interval)
    
Scenario 3: Log Writes Causing Latency (Java App)
  
  iotop shows: java process doing 50MB/s writes
  Application: not explicitly doing disk I/O
  Investigation: logging framework writing synchronously
  
  Fix:
    Async appender (Logback): <AsyncAppender> wraps FileAppender
    Or: write to tmpfs (RAM disk) and async ship to storage
    Or: reduce log verbosity (INFO level, not DEBUG in production)
    
Scenario 4: I/O Scheduler Mismatch
  
  NVMe device with CFQ (elevator) scheduler:
    CFQ: designed for HDD (reorders requests to minimize seek)
    NVMe: no seek time; reordering wastes CPU with no benefit
    
  Fix: check and change scheduler:
    cat /sys/block/nvme0n1/queue/scheduler
    echo none > /sys/block/nvme0n1/queue/scheduler
    Or: echo mq-deadline > /sys/block/nvme0n1/queue/scheduler
```

---

### iowait and JVM Interaction

```
JVM and disk I/O causes:
  
  1. GC log writing (rarely problematic):
     -Xlog:gc*:file=/tmp/gc.log: sequential appends
     Page cache buffers: normally no iowait
     
  2. Heap dump (can cause iowait):
     jcmd GC.heap_dump /tmp/heap.hprof
     4GB heap dump: writes 4GB to disk
     If disk is slow: iowait spike for duration
     
  3. JVM crash (hs_err_pid.log):
     Written synchronously on crash
     Usually fast (small file)
     
  4. Application-level I/O (most common cause):
     File reading/writing in application code
     SQLite, H2 embedded DB: disk reads during queries
     Logging: if synchronous appender
     
  5. Memory-mapped files (mmap):
     mmap'ing a file: I/O happens as pages are accessed
     Large random mmap access on cold cache: many page faults
     Each miss: disk read -> iowait contribution
     
  Detecting Java's I/O:
    iotop -p $PID -o: shows Java's disk I/O rates
    strace -p $PID -e trace=read,write,pread64,pwrite64 -T 2>&1 | head -30
    # Shows: each syscall, file descriptor, bytes, time
    # Identify: which fd is slow (lsof maps fd -> filename)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "High iowait means the CPU is working hard" | iowait means CPUs are IDLE, waiting for I/O. The CPU is doing nothing useful. A system can have 80% iowait and 10% CPU usage simultaneously - most CPU cycles are wasted waiting. iowait is not CPU utilization; it's CPU idle time attributable to pending I/O. |
| "iowait = 0% means no disk I/O is happening" | iowait measures CPU time, not I/O amount. If I/O is fast enough to not block CPUs (because of page cache, async I/O, or fast NVMe), iowait = 0% even while doing significant I/O. Also: multi-threaded applications may have I/O in flight while other threads keep CPUs busy. |
| "The only fix for high iowait is faster storage" | Faster storage helps, but first: diagnose the TYPE of I/O. Random reads from cold page cache: add RAM (cheap). Write bursts: tune dirty page thresholds. Sequential reads: tune read-ahead. Synchronous writes: use async I/O. Faster storage is often the LAST resort, not the first. |

---

### Quick Reference Card

| Tool | Purpose | Key Column |
|------|---------|------------|
| `top -1` | System-level iowait | `wa` column |
| `vmstat 1` | Context + I/O | `bi`, `bo`, `wa` |
| `iotop -o` | Per-process I/O | Disk Read/Write MB/s |
| `iostat -xz 1` | Per-device stats | `%util`, `await`, `svctm` |
| `blktrace` | Per-request tracing | Block addresses, latency |
| Healthy iowait | - | < 5% |
| Warning | - | 5-20% |
| Critical | - | > 20% |
