---
layout: default
title: "Disk I/O (iostat, iotop)"
parent: "Linux"
nav_order: 155
permalink: /linux/disk-io-iostat-iotop/
number: "0155"
category: Linux
difficulty: ★★☆
depends_on: Linux File System Hierarchy, /proc File System
used_by: Linux Performance Tuning, Observability & SRE, Database Fundamentals
related: Memory (free, vmstat), Swap Management, Linux Performance Tuning
tags:
  - linux
  - os
  - performance
  - observability
  - intermediate
---

# 155 — Disk I/O (iostat, iotop)

⚡ TL;DR — `iostat` shows per-device disk throughput and utilisation percentages; `iotop` shows which processes are generating that I/O — together they answer "is disk I/O the bottleneck and who is causing it?"

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Application response times are slow. CPU usage is 15%. Memory is fine. Something is making the system crawl. Without disk I/O visibility, you'd restart services, check network, check databases — all the wrong things. The actual culprit — a backup job running full sequential disk reads at 100% I/O utilisation while your database tries to do random reads — is completely invisible.

**THE BREAKING POINT:**
An on-call engineer gets paged at 2 AM: "Database queries taking 30 seconds". CPU is normal, memory is fine. Without I/O tools, the investigation takes hours. With `iostat -x 1` the story is clear in 5 seconds: `sda` shows `%util=99.8%`, `await=450ms` (average I/O latency 450 milliseconds). The disk is saturated. `iotop -o` shows `rsync` is consuming 95% of disk bandwidth. Kill the backup job — queries drop back to 50ms immediately.

**THE INVENTION MOMENT:**
This is the problem `iostat` and `iotop` solve. They make disk I/O visible at both the device level (iostat) and the process level (iotop), turning an invisible bottleneck into an actionable diagnosis in seconds.

---

### 📘 Textbook Definition

**`iostat`** (from the `sysstat` package) reads `/proc/diskstats` to report per-block-device I/O statistics: reads/writes per second, throughput (KB/s), average queue length, average wait time, and utilisation percentage. The extended statistics (`-x` flag) expose the complete set of block layer metrics including `await` (average I/O latency), `svctm` (service time), and `%util` (device saturation).

**`iotop`** reads per-process I/O accounting data from `/proc/PID/io` (Linux 2.6.20+) to show each process's current read and write rates, similar to how `top` shows CPU usage. The `-o` flag shows only processes with active I/O, making it easy to identify the specific process causing observed disk saturation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`iostat` shows what each disk is doing; `iotop` shows which process is causing it.

**One analogy:**
> `iostat` is a highway traffic monitor showing vehicles per minute and congestion percentage for each lane (disk). `iotop` is a camera that zooms in to identify the specific trucks (processes) occupying those lanes. The highway monitor tells you there's a jam; the camera tells you who caused it.

**One insight:**
`%util` in `iostat -x` is NOT utilisation in the traditional sense for SSDs. For HDDs, `%util=100%` means the disk is saturated and requests are queuing. For NVMe SSDs (which handle many parallel requests), `%util=100%` might just mean the queue is always non-empty but the device can still handle more IOPS. For SSDs, `await` and `aqu-sz` (queue depth) are the better saturation indicators.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Block device I/O is tracked in the kernel's request queue — each request has a submit time and a completion time.
2. `await` = average time from request submission to completion (includes queue wait + device service time).
3. For HDDs, `%util ≈ 100%` means saturation; for SSDs (especially NVMe), use queue depth and await instead.
4. `iotop` requires root (or CAP_NET_ADMIN) because per-process I/O accounting in `/proc/PID/io` is restricted.

**DERIVED DESIGN:**
The kernel's block layer counts reads and writes for each block device in `/proc/diskstats` (9 fields per device: reads completed, reads merged, sectors read, time spent reading, writes completed, writes merged, sectors written, time spent writing, I/Os in progress). `iostat` reads these counters, computes deltas between intervals, and derives utilisation metrics.

`iotop` reads `/proc/PID/io` for each process, which contains: `rchar` (bytes read via read syscalls), `wchar` (bytes written), `read_bytes` (bytes actually read from block devices), `write_bytes` (bytes actually written to block devices), `cancelled_write_bytes` (bytes cancelled by truncation). The `read_bytes`/`write_bytes` fields show real disk activity; `rchar`/`wchar` include buffered I/O served from page cache.

**THE TRADE-OFFS:**
**Gain:** Device-level and process-level I/O visibility with minimal overhead.
**Cost:** `iostat` is system-wide; per-filesystem or per-file breakdowns require other tools (iotop, lsof, strace); `iotop` requires root; process I/O accounting may not reflect the triggering process (e.g., the process that triggers a dirty page writeback is not the process that performs the write I/O).

---

### 🧪 Thought Experiment

**SETUP:**
NVMe SSD server. Your monitoring shows average disk latency has jumped from 50μs to 8ms. Application query times have jumped proportionally. What's happening?

**WITH iostat -x 1:**
```
Device     r/s    w/s  rMB/s  wMB/s  await  aqu-sz  %util
nvme0n1  12000   3000   450    200     8.2     96.3  100.0
```

Queue depth (`aqu-sz`) is 96.3 — meaning on average 96 requests are waiting. For an NVMe that normally handles 128+ parallel requests, this is extreme saturation. `%util=100%` confirms the device is fully occupied.

**WHAT THIS MEANS:**
The device is receiving 15,000 IOPS but its sustainable random IOPS (with this workload) is being exceeded. Something has dramatically increased I/O demand.

**WITH iotop -o:**
```
PID   IO     DISK READ   DISK WRITE   COMMAND
1234  99.9%  450.0 M/s     0.0 B/s   elasticsearch [flush]
```

Elasticsearch is doing a massive sequential read (index rebuild/compaction). Its sequential reads are filling the NVMe queue, starving the random reads from the application.

**THE INSIGHT:**
The iostat diagnosis (device-level: queue depth spike) combined with iotop (process-level: Elasticsearch flush) identifies both the symptom and the cause. Fix: schedule Elasticsearch flushes during low-traffic periods or use I/O cgroup limits to throttle its I/O rate.

---

### 🧠 Mental Model / Analogy

> Think of disk I/O like a post office counter. `iostat` tells you the counter's metrics: letters handled per minute, average wait time in queue, percentage of time the counter is busy. `iotop` identifies which customers are standing at the counter right now — who is submitting the most packages.

- "Letters handled/minute" → IOPS (r/s + w/s)
- "Average queue wait" → await
- "Counter busy percentage" → %util
- "Identifying customers" → iotop's per-process view
- "100% busy" → disk saturated (HDDs); or just high demand (SSDs)

Where this analogy breaks down: a single NVMe "counter" can serve many "customers" simultaneously (parallel queues); `%util` doesn't capture this parallelism — hence why `aqu-sz` (queue depth) matters more for SSDs.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`iostat` watches your disks and shows how busy they are — like a speedometer for disk activity. `iotop` shows which programs are reading or writing to the disk the most. Together they answer "is the disk too busy, and which program is responsible?"

**Level 2 — How to use it (junior developer):**
`iostat -x 1` runs every second showing extended device stats. Focus on `%util` and `await`. `iotop -o` shows only active I/O processes (needs root). `iostat -x -d sda 1` monitors only device sda. High `%util` + high `await` = disk bottleneck. Normal await for HDD: < 10ms; SSD: < 1ms; NVMe: < 0.1ms.

**Level 3 — How it works (mid-level engineer):**
`iostat` reads `/proc/diskstats` every N seconds and computes: `r/s = (reads_completed_t2 - reads_completed_t1) / interval`. The `%util` is calculated as `(time_io_t2 - time_io_t1) / (interval_ms * 10)` — percentage of time at least one I/O was in progress. `await = (total_time_reads + total_time_writes) / (reads + writes)` — average milliseconds per I/O. For SSDs: low `await` (<1ms) is healthy even with high `%util`. For HDDs: `%util > 80%` with `await > 20ms` indicates saturation. The `rrqm/s` and `wrqm/s` fields show how many adjacent requests the block scheduler merged — high merge rates indicate sequential I/O.

**Level 4 — Why it was designed this way (senior/staff):**
`/proc/diskstats` was designed to expose all the block layer's internal accounting with minimal overhead — counters are incremented atomically as requests complete, with no additional work needed. The `iostat` tool simply reads these counters. The design decision to track `time_in_io` (time with at least one I/O in progress) as the basis for `%util` was intentional for HDDs where one I/O at a time is the norm. This metric breaks down for SSDs where parallelism is native — a loaded NVMe can have 1024 outstanding requests and zero queue wait per request, while showing `%util=100%`. The industry is moving toward latency-based saturation detection (`await > baseline * 2X`) rather than `%util`-based for modern storage.

---

### ⚙️ How It Works (Mechanism)

**`iostat` commands:**
```bash
# Install (if missing)
apt install sysstat    # Debian/Ubuntu
yum install sysstat    # RHEL/CentOS

# Basic: all devices, 1-second interval
iostat 1

# Extended stats (the useful version)
iostat -x 1

# Specific device, human-readable
iostat -xh /dev/sda 1

# Show only deltas (skip first boot-average line)
iostat -x 1 | grep -v '^$' | tail -n +4

# Include device mapper (LVM, Docker volumes)
iostat -x -t 1      # -t adds timestamp

# Human-readable sizes (MB instead of KB)
iostat -xh 1
```

**Extended stats columns (-x):**
```
Device  r/s  w/s  rMB/s  wMB/s  rrqm/s  wrqm/s  r_await  w_await
        │    │    │      │      │        │        │        │
        │    │    │      │      │        │        │        └─ avg write latency ms
        │    │    │      │      │        │        └─ avg read latency ms
        │    │    │      │      │        └─ write requests merged/sec
        │    │    │      │      └─ read requests merged (= sequential reads)
        │    │    │      └─ write throughput MB/s
        │    │    └─ read throughput MB/s
        │    └─ writes per second
        └─ reads per second

aqu-sz  rareq-sz  wareq-sz  svctm  %util
│        │         │         │      └─ % time device was busy
│        │         │         └─ avg service time ms (deprecated on SSDs)
│        │         └─ avg write request size KB
│        └─ avg read request size KB
└─ average queue length (depth) — key SSD metric!

Normal baselines:
  HDD:  await < 10ms,  %util < 80%,  aqu-sz < 2
  SSD:  await < 1ms,   %util < 90%,  aqu-sz < 8
  NVMe: await < 0.1ms, %util < 95%,  aqu-sz < 32
```

**`iotop` commands:**
```bash
# Basic (requires root)
iotop

# Show only processes with active I/O (-o = only)
iotop -o

# Batch mode (for logging/scripting)
iotop -b -n 10 -d 1   # 10 iterations, 1s delay

# Show accumulated I/O (not rate)
iotop -a

# Filter to specific user
iotop -u www-data

# Show only specific PID
iotop -p 1234
```

**Alternative: pidstat for I/O per process:**
```bash
# Part of sysstat package — lower overhead than iotop
pidstat -d 1   # I/O stats per process, 1s interval
pidstat -d -p $(pidof postgres) 1  # specific process

# Output:
# UID  PID  kB_rd/s  kB_wr/s  kB_ccwr/s  iodelay  Command
# kB_ccwr/s = cancelled write bytes/s (truncated writes)
# iodelay = block I/O delays accumulated in clock ticks
```

**Disk latency monitoring:**
```bash
# Check current disk queue and latency
cat /proc/diskstats | awk '{
  if ($3 ~ /^(sd|nvme|vd)/) {
    rMs=$7; wMs=$11; rIO=$4; wIO=$8
    if (rIO+wIO > 0)
      printf "%s: reads=%d writes=%d \
        avg_lat=%.2f ms\n",
        $3, rIO, wIO, (rMs+wMs)/(rIO+wIO+0.001)
  }
}'

# Monitor disk saturation in real time
watch -n 1 "iostat -x | grep -v ^$  \
  | awk 'NR>2 {
    if (\$NF > 80) printf \"WARN: %s util=%s%%\n\",\$1,\$NF
  }'"
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  INVESTIGATE: High wa% in vmstat               │
└────────────────────────────────────────────────┘

 vmstat 1 shows: wa=45% (high I/O wait)
       │
       ▼
 Step 1: iostat -x 1
 → sda: await=85ms, %util=97%
       │  sda is saturated!
       ▼
 Step 2: What TYPE of I/O?
 → rMB/s=180 wMB/s=5 (mostly reads)
 → rareq-sz=512KB (large = sequential reads)
       │  Large sequential reads = backup/scan
       ▼
 Step 3: iotop -o (who is reading?)
 → PID 4567 rsync: 175 MB/s reads
       │
       ▼
 Diagnosis: rsync backup consuming
 95% of disk bandwidth during business hours
       │
       ▼
 Fix options:
  A) Schedule backup to off-hours
  B) Throttle rsync I/O:
     ionice -c 3 -p $(pidof rsync)  # idle I/O class
  C) Use cgroup I/O limits:
     systemctl set-property rsync.service \
       IOReadBandwidthMax="/dev/sda 50M"
```

**FAILURE PATH:**
If `iostat` shows `%util=0%` but applications report slow file access, the bottleneck is not the block device — check: network filesystem (NFS/CIFS) latency, filesystem-level locking, or excessive page faults (memory pressure causing I/O waits that don't appear in block stats).

---

### 💻 Code Example

**Example 1 — Disk performance baseline and alert:**
```bash
#!/bin/bash
# Check disk health against performance baselines
WARN_AWAIT_HDD=20     # ms
WARN_AWAIT_SSD=2      # ms
WARN_UTIL=85          # %

iostat -x 1 2 | awk 'NR>6 {
  dev=$1; util=$NF; await=$10
  # Skip header lines and empty lines
  if (dev ~ /^(sd|nvme|vd|xvd)/ && await+0 > 0) {
    type = (dev ~ /nvme/) ? "NVMe" : "disk"
    warn = (type == "NVMe") ? 1 : 20
    if (await + 0 > warn)
      printf "WARN: %s await=%.1fms (threshold=%dms)\n",
        dev, await, warn
    if (util + 0 > 85)
      printf "WARN: %s util=%.1f%% (>85%%)\n", dev, util
  }
}'
```

**Example 2 — I/O throttling with cgroups:**
```bash
# Limit a backup job's I/O to avoid saturation
# Method 1: ionice (change I/O priority class)
ionice -c 3 rsync -av /data /backup/  # idle priority

# Method 2: systemd service I/O limits
# /etc/systemd/system/backup.service
cat > /etc/systemd/system/backup.service << 'EOF'
[Unit]
Description=Daily backup

[Service]
ExecStart=/usr/local/bin/backup.sh
IOSchedulingClass=best-effort
IOSchedulingPriority=7
IOReadBandwidthMax=/dev/sda 50M
IOWriteBandwidthMax=/dev/sda 50M

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
```

**Example 3 — Find large sequential readers:**
```bash
#!/bin/bash
# Identify which processes are doing sequential
# (large block) reads — typical of backup/scan
echo "Large-block readers (likely sequential):"

# iotop batch for 5 seconds
iotop -b -n 5 -d 1 2>/dev/null | \
  awk '/K\/s|M\/s/{
    if ($4 ~ /M/) rate=$4*1024
    else rate=$4
    if (rate > 10240)  # > 10 MB/s
      print $0
  }' | sort -u | head -10
```

---

### ⚖️ Comparison Table

| Tool | Device View | Process View | Latency | Historical |
|---|---|---|---|---|
| **iostat -x** | Yes (per-device) | No | Yes (await) | No |
| **iotop** | No | Yes (per-process) | No | No |
| pidstat -d | No | Yes | No | No |
| dstat | Yes | No | Partial | No |
| sar -d | Yes | No | Partial | Yes (historical) |
| blktrace | Yes (per-request) | Partial | Yes (exact) | File |

How to choose: use `iostat -x 1` first to identify if a device is saturated; use `iotop -o` to identify which process is responsible; use `blktrace` for detailed per-request latency analysis of a specific device.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| %util=100% means the SSD is at capacity | For SSDs (especially NVMe), %util measures time with any I/O pending, not queue saturation; use aqu-sz and await to judge real saturation |
| iostat's first output line shows current activity | The first block shows averages since boot — always wait for the second iteration for meaningful real-time data |
| iotop shows all I/O a process generates | iotop shows I/O that reaches the block device; reads/writes served by page cache don't appear in iotop's block I/O counts |
| High write I/O means a process is writing that much | A process's writes go to page cache first (writeback); the kernel batches them to disk later — the writing process in iotop may differ from the process that originally wrote the data |
| ionice can guarantee I/O isolation | ionice (CFQ scheduler) is advisory; modern kernels default to mq-deadline or bfq; for guaranteed I/O isolation use cgroup I/O limits |

---

### 🚨 Failure Modes & Diagnosis

**Disk I/O Bottleneck Not Visible in iostat**

**Symptom:**
High I/O wait (`wa`) in vmstat but `iostat -x` shows all devices at low `%util`.

**Root Cause A:**
The I/O is on a network filesystem (NFS, CIFS, FUSE) — these don't appear in block device stats.

**Root Cause B:**
The wait is due to memory pressure causing page faults that the OS waits on — visible in vmstat `si` (swap-in) but not in block device stats.

**Diagnostic Command:**
```bash
# Check for NFS mounts
mount | grep -E 'nfs|cifs|fuse'
nfsiostat 1   # NFS-specific I/O stats

# Check if swap I/O is the cause
vmstat 1 | awk '{print "swap-in:"$7,"swap-out:"$8}'

# Check for kernel I/O wait cause
perf stat -e block:block_rq_issue,block:block_rq_complete \
  sleep 5
```

---

**iotop Shows No Processes Despite High Disk I/O**

**Symptom:**
`iostat -x` shows high write activity but `iotop -o` shows nothing.

**Root Cause:**
The writes are kernel writeback flushes from page cache — dirty pages accumulated by many processes are being flushed by `kworker` kernel threads. The original writing processes have already finished; the I/O is now attributed to the kernel.

**Diagnostic Command:**
```bash
# Show kernel writeback threads' I/O
iotop -o  # look for [kworker] or [flush] processes

# Check dirty page backlog
grep -E 'Dirty:|Writeback:' /proc/meminfo

# Monitor writeback rate
cat /proc/vmstat | grep -E 'nr_dirty|nr_writeback|
  pgpgout|pswpout'
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux File System Hierarchy` — understanding mount points, block devices, and the VFS layer is foundational to interpreting iostat device names and I/O paths
- `/proc File System` — iostat reads `/proc/diskstats`; iotop reads `/proc/PID/io`; understanding procfs explains these tools' capabilities

**Builds On This (learn these next):**
- `Memory (free, vmstat)` — vmstat's `wa` (I/O wait) column is the first indicator of I/O problems; iostat is the next step
- `Swap Management` — swap I/O appears in vmstat's `si`/`so` and in iostat if swap is on a block device
- `Linux Performance Tuning` — I/O scheduler tuning (`/sys/block/*/queue/scheduler`), readahead tuning, and cgroup I/O limits are the follow-on tools after diagnosis

**Alternatives / Comparisons:**
- `dstat` — combines vmstat, iostat, and network stats in one tool; useful for quick multi-resource overviews
- `blktrace` — per-request block layer tracing for detailed latency analysis
- `sar -d` — historical disk stats from the `sysstat` suite; useful for trend analysis
- `fio` — synthetic I/O benchmark tool for characterising storage performance baselines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ iostat: per-device disk metrics; iotop:   │
│              │ per-process I/O rates                     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "System is slow" — is disk the bottleneck │
│ SOLVES       │ and if so, which process is responsible?  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ For SSDs: use await and aqu-sz, not %util │
│              │ for saturation detection                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High wa% in vmstat; slow file operations; │
│              │ database query latency spikes             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ NFS/CIFS issues — iostat doesn't see      │
│              │ network filesystem I/O                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Device-level vs process-level resolution; │
│              │ iotop needs root; block vs cache I/O      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Highway congestion monitor (iostat)      │
│              │ + truck identifier (iotop)"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ blktrace → io_uring → eBPF I/O tracing  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A PostgreSQL database server has NVMe storage. During business hours, `iostat -x 1` shows `nvme0n1` with `await=3ms` (baseline is 0.08ms) and `aqu-sz=45`. At the same time, `iotop -o` shows only the PostgreSQL process with 200 MB/s reads. Explain why 200 MB/s from a single process on a modern NVMe (rated for 3GB/s) is causing 3ms average latency, what the queue depth of 45 tells you about the PostgreSQL I/O pattern, and what specific PostgreSQL configuration parameters and Linux kernel parameters you would investigate to reduce the await back toward baseline.

**Q2.** You are designing observability for a multi-tenant Kubernetes cluster where 50 pods share 4 NVMe drives. Outline a complete I/O observability strategy that provides: (1) per-pod I/O attribution, (2) early warning before a noisy-neighbour pod saturates the drives for other pods, and (3) automatic throttling when a pod exceeds its fair share — specifying the exact Linux tools and kernel features used at each layer.
