---
layout: default
title: "Memory (free, vmstat)"
parent: "Linux"
nav_order: 154
permalink: /linux/memory-free-vmstat/
number: "0154"
category: Linux
difficulty: ★★☆
depends_on: Operating Systems, Linux File System Hierarchy
used_by: Linux Performance Tuning, Observability & SRE, Swap Management
related: Swap Management, Disk I/O (iostat, iotop), /proc File System
tags:
  - linux
  - os
  - performance
  - observability
  - intermediate
---

# 154 — Memory (free, vmstat)

⚡ TL;DR — `free` gives a snapshot of RAM and swap usage; `vmstat` shows a rolling stream of memory, CPU, and I/O counters — together they answer "is this system under memory pressure right now?"

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A server is slow. Is it CPU-bound, memory-bound, I/O-bound? Without tools that show memory state and pressure indicators, you're guessing. Restarting services at random. The root cause — a memory leak that's causing the kernel to spend 40% of CPU time doing page reclaim — is invisible.

**THE BREAKING POINT:**
Application response times jump from 50ms to 2 seconds. CPU usage is normal (30%). Nothing in the app logs. Without `vmstat 1`, you'd never see the smoking gun: `si`/`so` (swap-in/swap-out) columns are non-zero and climbing, meaning the system is actively thrashing between RAM and disk.

**THE INVENTION MOMENT:**
`vmstat 1` shows 5 lines per second: `si` (swap-in) averages 200 pages/sec, `so` (swap-out) averages 150 pages/sec. The server is swapping. `free -h` shows "available" memory is near zero. The diagnosis takes 30 seconds; the fix (restart the leaking process) takes 2 minutes.

---

### 📘 Textbook Definition

**`free`** is a tool that reads `/proc/meminfo` and displays total, used, free, shared, buff/cache, and available physical memory and swap in a concise table. The **available** column (not the same as free) estimates how much RAM can be given to new processes without swapping, accounting for reclaimable cache.

**`vmstat`** (virtual memory statistics) reports system memory, process, paging, block I/O, interrupt, and CPU activity. When run as `vmstat N` (with an interval), it outputs a new row every N seconds showing counters since the previous sample — the first row shows averages since boot. It reads from `/proc/vmstat`, `/proc/meminfo`, `/proc/stat`, and `/proc/diskstats`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`free` shows current memory state; `vmstat` shows memory (and system) dynamics over time.

**One analogy:**

> `free` is a fuel gauge — it shows how much RAM is in the tank right now. `vmstat` is the dashboard telemetry — it shows not just the gauge but also fuel consumption rate, engine load, brake activity, and whether you're burning fuel efficiently or thrashing the engine.

**One insight:**
The **`available`** column in `free` is the number that matters, not `free`. "Free" memory is memory not used for anything; "available" includes reclaimable page cache — memory that looks "used" but can be freed instantly for new allocations. A system with 100MB "free" and 8GB "available" is healthy; a system with 100MB "available" is about to OOM.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Linux uses all idle RAM as page cache — "free" memory is wasted capacity.
2. "Available" = free + reclaimable cache; this is the true measure of free capacity.
3. vmstat's first line shows boot averages; all subsequent lines show per-interval deltas.
4. Non-zero `si`/`so` in vmstat means active swapping — a critical warning sign.

**DERIVED DESIGN:**
Linux's memory allocator (buddy allocator + slab allocator) eagerly uses free RAM as page cache to improve I/O performance. This means `free` memory appears near zero on a healthy, loaded system — a common source of false alarms ("the server is almost out of memory!"). The kernel added the `MemAvailable` field to `/proc/meminfo` specifically to address this: it calculates how much memory can actually be reclaimed and given to new processes.

`vmstat` reads counters from `/proc/vmstat` (kernel accumulator of events) and divides by the elapsed interval to show rates. The most critical columns: `r` (runnable processes — CPU saturation indicator), `b` (blocked on I/O), `si`/`so` (swap-in/out rates), `us`/`sy`/`id`/`wa` (CPU breakdown). A system with high `wa` (I/O wait) and non-zero `si`/`so` is swapping — the worst state for a production system.

**THE TRADE-OFFS:**
**Gain:** Real-time visibility into memory pressure with no overhead.
**Cost:** `vmstat` and `free` show system-wide averages — they don't identify which process is causing the pressure (need `top`, `/proc/PID/status`, or `smem` for per-process detail).

---

### 🧪 Thought Experiment

**SETUP:**
Two scenarios, both with `free` showing only 200MB "free". Which is healthy?

**Scenario A:**

```
         total   used    free   buff/cache  available
Mem:      16Gi   12Gi   200Mi       3.8Gi       3.7Gi
```

**Scenario B:**

```
         total   used    free   buff/cache  available
Mem:      16Gi   15.8Gi  200Mi      10Mi       150Mi
```

**THE ANALYSIS:**

- Scenario A: 200MB free but 3.7GB **available** — the 3.8GB in buff/cache is reclaimable page cache. The system can easily accommodate 3.7GB more allocation. Healthy.
- Scenario B: 200MB free and only 150MB **available** — virtually no reclaimable cache. The system is memory-pressured. Any significant new allocation will either OOM-kill something or force swap. Crisis.

**THE INSIGHT:**
Reading only the `free` column from `free -h` is a classic mistake. An experienced operator always reads the `available` column. The difference between scenarios A and B is massive — one is healthy, one is about to fail — and only the `available` column shows it.

---

### 🧠 Mental Model / Analogy

> Memory is like a restaurant kitchen. `free` tells you the empty counter space (literally unused RAM). `available` tells you the workable space (empty counters + counters with prep work that can be cleared instantly). `buff/cache` is prep work and ingredients staged for cooking (page cache — in-use but reclaimable). What you really want to know isn't "are any counters completely empty?" but "can a new order fit?". That's `available`.

- "Empty counter" → free memory
- "Workable space" → available memory
- "Staged prep work" → page cache (buff/cache)
- "Order can't fit" → OOM pressure

Where this analogy breaks down: in a real kitchen, staged prep can't be instantly discarded; in Linux, clean page cache CAN be instantly reclaimed — it just means the next cache miss reads from disk again.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`free` shows how much memory your computer has and how much is in use. `vmstat` shows a stream of numbers indicating how hard the computer is working — like a real-time health dashboard. Together they tell you whether the computer is struggling with memory pressure.

**Level 2 — How to use it (junior developer):**
`free -h` shows memory in human-readable format. Focus on the `available` column. `vmstat 1` runs every second; watch the `si`/`so` columns (should be 0) and the `wa` (I/O wait) column. If `si`/`so` are non-zero, the system is swapping — investigate immediately. `vmstat -s` shows a summary of memory stats since boot.

**Level 3 — How it works (mid-level engineer):**
`free` reads directly from `/proc/meminfo`. The `available` field (`MemAvailable`) was added in Linux 3.14 and estimates available memory by summing: free pages + reclaimable low-watermark pages + inactive file pages + partial slab reclaim. `vmstat`'s `pgpgin`/`pgpgout` (pages paged in/out) and `pswpin`/`pswpout` (pages swapped in/out) come from `/proc/vmstat`. The critical distinction: `pgpg` tracks all page activity (including normal file I/O); `pswp` tracks only swap activity — non-zero `pswp` means the system is under genuine memory pressure.

**Level 4 — Why it was designed this way (senior/staff):**
The confusion between "free" and "available" memory was so widespread that the Linux kernel developers added `MemAvailable` in 2014 (Linux 3.14, commit 34e431b0) specifically because monitoring systems and orchestrators were incorrectly treating page cache as unavailable memory and triggering false OOM conditions. The `free` command was updated to show "available" as a distinct column. The `vmstat` tool's design reflects UNIX heritage — a single tool showing all relevant system activity metrics in one compact line, optimised for human pattern-matching at a terminal. The `r` and `b` queue lengths (runnable vs. blocked) directly encode the classic queuing theory model: `r > nCPUs` means CPU saturation; `b > 0` means I/O saturation.

---

### ⚙️ How It Works (Mechanism)

**`free` output explained:**

```bash
free -h
#              total   used    free  shared buff/cache  available
# Mem:          15Gi   6.2Gi  1.8Gi   523Mi      7.1Gi      8.5Gi
# Swap:          4Gi    20Mi  3.98Gi

# COLUMNS:
# total       = physical RAM installed
# used        = allocated memory (total - free - buff/cache)
# free        = completely unused pages
# shared      = tmpfs / shared memory
# buff/cache  = kernel buffers + page cache (reclaimable!)
# available   = THE IMPORTANT ONE: estimate of RAM for new allocs
#               ≈ free + most of buff/cache

# RULE: If available < 10% of total, investigate!
# RULE: If swap used > 0, investigate!

free -m   # in megabytes
free -g   # in gigabytes
free -s 2 # update every 2 seconds
```

**`vmstat` output explained:**

```bash
vmstat 1  # update every 1 second

# Header:
# procs ----memory---- ---swap-- -----io---- -system-- ------cpu-----
#  r  b  swpd   free   buff  cache  si  so   bi   bo  in   cs us sy id wa st

# COLUMNS:
# r     = runnable (waiting for CPU) — > nCPUs = CPU saturation
# b     = blocked on I/O
# swpd  = virtual memory used (swap) — KB
# free  = free memory KB
# buff  = kernel buffer memory KB
# cache = page cache KB
# si    = swap-in (KB/s from disk) — ALERT if > 0
# so    = swap-out (KB/s to disk) — ALERT if > 0
# bi    = blocks in from block devices (reads)
# bo    = blocks out to block devices (writes)
# in    = interrupts per second
# cs    = context switches per second
# us    = user CPU %
# sy    = system (kernel) CPU %
# id    = idle CPU %
# wa    = I/O wait CPU % — high = I/O bound
# st    = stolen CPU % (VM hypervisor overhead)

# Key patterns:
# Healthy:     r ≤ nCPUs, si=0, so=0, wa < 5%
# CPU sat:     r >> nCPUs, id ≈ 0
# Mem pressure: si > 0 or so > 0
# I/O bound:   wa > 20%, b > 0, high bi/bo
# Swap thrash:  si AND so both high (death spiral)
```

**Additional useful commands:**

```bash
# Memory breakdown from /proc/meminfo
cat /proc/meminfo
grep -E 'MemTotal|MemFree|MemAvailable|Cached|SwapTotal|SwapFree' \
  /proc/meminfo

# vmstat with disk stats
vmstat -d 1   # per-disk read/write stats
vmstat -D     # disk summary
vmstat -s     # event counters since boot

# Process memory usage (sorted)
ps aux --sort=-rss | head -10
# RSS = resident set size (physical RAM used)
# VSZ = virtual size (address space, includes swap + mmap)

# smem: more accurate per-process memory (PSS)
smem -s pss -r | head -15
# PSS (proportional set size): shared libs counted once,
#   divided among all sharing processes

# Memory usage per cgroup (containers)
cat /sys/fs/cgroup/memory/docker/*/memory.usage_in_bytes
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  DIAGNOSIS: Application latency spike at 3PM  │
└────────────────────────────────────────────────┘

 Step 1: vmstat 1
 Observe 60 seconds of output:
       │
       ▼
 r=2, b=0, si=0, so=0, wa=2% → baseline healthy
       │
       ▼ (at 3PM during latency spike)
 r=1, b=3, si=450, so=0, wa=35%
       │  b>0: processes blocked on I/O
       │  si=450: 450KB/s being read FROM swap
       │  wa=35%: CPU waiting on I/O
       ▼
 System is reading pages back from swap (si)
 This is the latency cause
       │
       ▼
 Step 2: free -h
 available: 150Mi (near zero!)
 swap used: 2.3Gi
       │
       ▼
 Step 3: find culprit
 for p in /proc/[0-9]*/status; do
   grep VmSwap $p | awk '{print $2, FILENAME}'
 done | sort -rn | head -5
       │  → java 12345: 2.1GB in swap
       ▼
 Java process has 2.1GB swapped out
 When requests come in at 3PM, pages fault
 back in from swap → 35% I/O wait
       │
       ▼
 Fix: Increase server RAM or reduce heap size
      Short-term: swapoff forces pages back to RAM
                  (if RAM available)
```

---

### 💻 Code Example

**Example 1 — Memory health check script:**

```bash
#!/bin/bash
# Snapshot memory health for monitoring
WARN_AVAIL_PCT=15  # warn below 15% available
CRIT_AVAIL_PCT=5   # critical below 5%

MEM_TOTAL=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_AVAIL=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
SWAP_TOTAL=$(grep SwapTotal /proc/meminfo | awk '{print $2}')
SWAP_USED=$(( $(grep SwapTotal /proc/meminfo | awk '{print $2}')
            - $(grep SwapFree /proc/meminfo | awk '{print $2}') ))

AVAIL_PCT=$(( MEM_AVAIL * 100 / MEM_TOTAL ))

echo "Memory Available: ${MEM_AVAIL}KB (${AVAIL_PCT}% of total)"

if [ "$AVAIL_PCT" -lt "$CRIT_AVAIL_PCT" ]; then
  echo "CRITICAL: Low memory!"
  STATUS=2
elif [ "$AVAIL_PCT" -lt "$WARN_AVAIL_PCT" ]; then
  echo "WARNING: Memory pressure"
  STATUS=1
else
  echo "OK: Memory healthy"
  STATUS=0
fi

if [ "$SWAP_USED" -gt 0 ]; then
  echo "WARNING: Swap in use: ${SWAP_USED}KB"
  # Check for active swap I/O
  SI=$(grep pswpin /proc/vmstat | awk '{print $2}')
  SO=$(grep pswpout /proc/vmstat | awk '{print $2}')
  echo "Cumulative swap-in: $SI pages, out: $SO pages"
fi

exit $STATUS
```

**Example 2 — Continuous memory monitoring with vmstat:**

```bash
#!/bin/bash
# Log vmstat to file, alert on swap I/O
LOG="/var/log/vmstat_$(date +%Y%m%d).log"

vmstat 5 | while read line; do
  echo "$(date '+%H:%M:%S') $line" | tee -a "$LOG"

  # Check si/so columns (columns 7 and 8, 0-indexed)
  SI=$(echo "$line" | awk 'NR>1{print $7}')
  SO=$(echo "$line" | awk 'NR>1{print $8}')

  if [[ "$SI" =~ ^[0-9]+$ ]] && [ "$SI" -gt 0 ]; then
    echo "SWAP-IN ALERT: ${SI} KB/s" | \
      logger -p daemon.warning
  fi
done
```

---

### ⚖️ Comparison Table

| Tool          | Scope       | Real-time  | Memory Detail | I/O Stats |
| ------------- | ----------- | ---------- | ------------- | --------- |
| **free**      | System-wide | Snapshot   | High          | No        |
| **vmstat**    | System-wide | Streaming  | Medium        | Yes       |
| top / htop    | Per-process | Streaming  | Medium        | Partial   |
| /proc/meminfo | System-wide | Raw data   | Highest       | No        |
| smem          | Per-process | Snapshot   | PSS/RSS/VSS   | No        |
| sar           | System-wide | Historical | Medium        | Yes       |

How to choose: use `free -h` for quick memory state; `vmstat 1` for real-time pressure monitoring; `top`/`htop` for per-process breakdown; `/proc/meminfo` for scripting with complete detail.

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                               |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Low "free" means memory pressure        | `free` shows literally unused pages — on a healthy server, free is often near 0 because Linux uses all idle RAM as page cache; **available** is the correct indicator |
| vmstat's first line shows current state | The first line shows averages since boot — always skip it; only lines 2+ show meaningful per-interval activity                                                        |
| High buff/cache means memory is wasted  | buff/cache is page cache — it actively improves performance and is reclaimed instantly when processes need it                                                         |
| vmstat -s shows real-time stats         | vmstat -s shows cumulative counters since boot; it's historical, not instantaneous                                                                                    |
| si=0 means no swap is being used        | si=0 means no swap-in is happening RIGHT NOW; `free` may still show swap is used (previously swapped pages not yet reclaimed)                                         |

---

### 🚨 Failure Modes & Diagnosis

**"Available" Memory Near Zero but No OOM Kill**

**Symptom:**
`free -h` shows available is under 100MB. System is slow but not crashing. No OOM messages in `dmesg`.

**Root Cause:**
The system is under heavy memory pressure but has swap. The kernel is aggressively swapping anonymous pages to keep the system alive. Performance is severely degraded.

**Diagnostic Command:**

```bash
# Confirm active swapping
vmstat 1 | awk '{print $7,$8,$16}' | head -10
# Columns: swap-in, swap-out, I/O wait

# Find the memory consumers
ps aux --sort=-rss | head -10

# Find what is in swap
for pid in /proc/[0-9]*/status; do
  swap=$(grep VmSwap "$pid" 2>/dev/null | awk '{print $2}')
  name=$(grep ^Name "$pid" 2>/dev/null | awk '{print $2}')
  [ "${swap:-0}" -gt 10000 ] && echo "$swap KB: $name"
done | sort -rn
```

**Fix:**
Kill or restart the largest memory consumer; add RAM; reduce service memory footprint; add memory alerting at 20% available to get warning before crisis.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Operating Systems` — virtual memory, paging, and the distinction between physical and virtual address spaces are foundational
- `Linux File System Hierarchy` — `/proc/meminfo` and `/proc/vmstat` are the data sources; understanding procfs explains what these tools read

**Builds On This (learn these next):**

- `Swap Management` — deep dive into the swap mechanism that vmstat's si/so columns expose
- `Disk I/O (iostat, iotop)` — complements vmstat's I/O view with per-device detail
- `Linux Performance Tuning` — vm.swappiness, overcommit ratio, and huge pages are the tuning levers for what free/vmstat expose

**Alternatives / Comparisons:**

- `top` / `htop` — per-process memory breakdown; less convenient for system-level monitoring
- `sar` — historical memory statistics; complements vmstat for trend analysis
- `smem` — per-process PSS (proportional set size) accounting, more accurate than RSS

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ free: memory snapshot; vmstat: streaming  │
│              │ system counters — both from /proc/meminfo │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Is this system under memory pressure?     │
│ SOLVES       │ Which resource is the bottleneck?         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Read "available" not "free" in free -h;  │
│              │ si/so in vmstat > 0 = memory emergency    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Application slowness; memory-related      │
│              │ incidents; capacity planning              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Per-process memory profiling — use        │
│              │ smem, top, or /proc/PID/status instead    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ System-wide visibility vs per-process     │
│              │ attribution; no overhead vs limited detail│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fuel gauge (free) + dashboard telemetry  │
│              │  (vmstat) for your RAM"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ smem → /proc/meminfo → cgroups memory    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Prometheus-based monitoring system alerts on "memory usage > 85%" calculated as `(total - free) / total`. Your operations team is getting daily false-positive alerts on a healthy database server. Explain why this calculation is wrong, provide the correct PromQL formula using the available metric, and describe how to educate the team on why the corrected metric will show a very different (and accurate) picture.

**Q2.** vmstat 1 on a production server shows: `r=0 b=0 si=0 so=0 us=2 sy=1 id=97 wa=0` for 5 minutes, then suddenly: `r=12 b=8 si=800 so=0 us=15 sy=45 wa=35` for 3 minutes. Reconstruct the complete story of what happened during those 3 minutes — which kernel subsystems were involved, what the `sy=45` indicates, what triggered the `si=800`, why `b=8`, and what the state of the system likely was before the event started (hint: how does page reclaim relate to the idle period that precedes the spike?).
