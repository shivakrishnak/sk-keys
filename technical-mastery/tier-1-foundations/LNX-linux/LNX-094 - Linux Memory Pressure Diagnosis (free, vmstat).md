---
id: LNX-094
title: "Linux Memory Pressure Diagnosis (free, vmstat)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-063, LNX-093
used_by: LNX-093, LNX-095, LNX-096
related: LNX-063, LNX-083, LNX-093
tags: [memory-pressure, free, vmstat, meminfo, psi, pressure-stall-information, kswapd, oom-killer, smem, slabtop, numa, numastat, available-memory, buff-cache, swap, memory-diagnosis, page-cache, anonymous-pages, rss, uss, pss]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 94
permalink: /technical-mastery/lnx/linux-memory-pressure-diagnosis/
---

## TL;DR

The most important memory metric is `MemAvailable` (from `free -h`'s
"available" column and `/proc/meminfo`), not "free" - available includes
reclaimable page cache. Memory PRESSURE (not just usage) is diagnosed via:
`vmstat 1` for `si/so` (swap in/out, > 0 = paging), `dmesg` for OOM kills,
`/proc/pressure/memory` for PSI (Pressure Stall Information). Key metrics:
`smem -s pss -r` for per-process PSS memory (proportional, not inflated by
shared libs). `slabtop` for kernel slab cache usage. `numastat` for NUMA
imbalance. Early warning: `sar -B` `pgscank/s` > 0 (kswapd is scanning
= memory under pressure). Late warning: si/so > 0 in vmstat (already swapping).
Emergency: OOM kill in `dmesg`. Memory cgroup pressure: `memory.pressure`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-094 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | memory pressure, free, vmstat, PSI, kswapd, smem, slabtop, OOM, numastat, MemAvailable |
| **Prerequisites** | LNX-063 (memory management), LNX-083 (OOM killer) |

---

### The Problem This Solves

**Problem 1**: "The server ran out of memory" - but `free -h` shows 2GB free
with 4GB in buff/cache. Engineer allocates more RAM or reduces the cache.
Neither helps: the system actually had 5.5GB available (free + reclaimable
cache). The real issue was something else entirely. Misreading `free` output
leads to wrong diagnosis, wrong fix, and wasted engineering time.

**Problem 2**: Production service degrades slowly over hours. CPU is fine,
disk is fine. No OOM kills. The issue is invisible until the system becomes
unresponsive. With PSI (/proc/pressure/memory): `full` stall metric starts
increasing 2 hours before the incident. Memory pressure is detectable before
swapping starts and before OOM fires. PSI allows proactive action (restart
service, add capacity) instead of reactive recovery.

---

### Textbook Definition

**Memory pressure**: The condition where the system's demand for physical
memory exceeds or approaches available supply, causing the kernel to spend
increasing time reclaiming pages, potentially degrading performance before
running completely out of memory.

**Key memory states (from worst to best):**

| State | Indicator | Severity |
|-------|-----------|----------|
| OOM kill | `dmesg` OOM entries | Emergency - process killed |
| Active swap I/O | `vmstat` si/so > 0 | Critical - severe slowdown |
| Page cache pressure | `vmstat` `pgscank/s` > 0 | Warning - kswapd scanning |
| PSI full stall | `/proc/pressure/memory` full > 0 | Moderate - some stalls |
| Low available | `MemAvailable` < 10% total | Monitoring - watch closely |
| Normal | `MemAvailable` > 20% total | Healthy |

---

### Understand It in 30 Seconds

```bash
# === The critical mistake: reading "free" instead of "available" ===

free -h
#                total        used        free      shared  buff/cache   available
# Mem:            15Gi        10Gi       876Mi       512Mi        4.5Gi        4.8Gi
#                                        ^^^^^^^                              ^^^^^^^
#              NOT USEFUL           USEFUL: what new processes can use
#
# "free" = 876MB: memory NOT being used by ANYTHING
# "buff/cache" = 4.5GB: file system cache (reclaimable!)
# "available" = 4.8GB: free + reclaimable cache = actual usable memory
# 
# The system has 4.8GB available despite only 876MB "free"!
# Allocating a new 3GB process: kernel reclaims cache -> succeeds
# "free" would have suggested danger; "available" correctly says: fine

# === /proc/meminfo: complete memory breakdown ===
cat /proc/meminfo
# MemTotal:       16252340 kB   <- total physical RAM
# MemFree:          897212 kB   <- free (not "available")
# MemAvailable:    4912568 kB   <- AVAILABLE (key metric)
# Buffers:          167512 kB   <- filesystem metadata cache
# Cached:          4098456 kB   <- file content page cache
# SwapCached:            0 kB   <- data in swap but also in RAM
# Active:          8956432 kB   <- recently used pages (hard to reclaim)
# Inactive:        3234567 kB   <- older pages (easier to reclaim)
# Active(anon):    6234567 kB   <- anonymous pages: heap, stack (no file)
# Inactive(anon):  1098765 kB   <- anonymous pages (paged to swap possible)
# Active(file):    2721865 kB   <- page cache: recently used
# Inactive(file):  2135802 kB   <- page cache: older (reclaimable)
# Unevictable:      123456 kB   <- mlock'd pages (cannot be paged)
# Mlocked:          123456 kB   <- pages locked by mlock()
# SwapTotal:       8388604 kB   <- total swap space
# SwapFree:        8388604 kB   <- free swap (if same as total: no swapping)
# Dirty:             12345 kB   <- pages modified but not written to disk
# Writeback:          1234 kB   <- pages being written to disk now
# AnonPages:       7333332 kB   <- total anonymous pages (heap, stack, mmap)
# Mapped:          1234567 kB   <- files mapped into process address space
# Shmem:            456789 kB   <- tmpfs, shared memory
# KReclaimable:    1234567 kB   <- kernel memory that CAN be reclaimed
# Slab:            2345678 kB   <- kernel slab allocator total
# SReclaimable:    1234567 kB   <- slab reclaimable (dentry, inode cache)
# SUnreclaim:      1111111 kB   <- slab not reclaimable

# Calculated values:
# Real application memory = AnonPages + Mapped (- shared library duplicates)
# Real "used" = MemTotal - MemAvailable
# Kernel overhead = Slab + KernelStack + PageTables + HardwareCorrupted

# === vmstat: memory pressure indicators ===
vmstat 1 5
#  r  b   swpd   free   buff  cache   si   so    bi    bo   cs  us sy id wa st
#  2  0      0 897212  167512 4265968   0    0     2    45 2345  15  3 81  1  0
#
# swpd: KB in swap (> 0 doesn't mean pressure if si/so=0: just memory on swap)
# si: swap in KB/s (reading FROM swap INTO RAM: demand exceeding RAM)
# so: swap out KB/s (writing FROM RAM TO swap: evicting to make room)
# If si > 0 OR so > 0: ACTIVE swapping (system is under pressure)
# bi/bo: block I/O (not just swap - includes file I/O)

# === PSI (Pressure Stall Information): early warning ===
cat /proc/pressure/memory
# some avg10=0.00 avg60=0.00 avg300=0.00 total=0
# full avg10=0.00 avg60=0.00 avg300=0.00 total=123456
#
# "some": % of time some tasks waited for memory (at least 1 task stalled)
# "full": % of time ALL tasks waited for memory (system came to a halt)
# avg10/avg60/avg300: moving averages over 10s, 60s, 300s
# total: total microseconds stalled (ever)
#
# Alert thresholds (typical):
#   some > 5% over 60s: moderate pressure, investigate
#   full > 1% over 60s: severe pressure, act now
#   full > 0.1% (any): system was completely stalled

# Compare with CPU and I/O pressure:
cat /proc/pressure/cpu
cat /proc/pressure/io

# === smem: per-process memory (accurate) ===
smem -s pss -r -t -n
# PID    Name    USS       PSS      RSS
# 1234   java    3456789   3567890  4567890
# 5678   nginx   234567    256789   345678
# 1      systemd  12345     23456    45678
#
# RSS: Resident Set Size - ALL mapped memory including shared libs
#      MISLEADING: sum of all RSS >> actual memory used (shared counted multiple times)
# PSS: Proportional Set Size - private + fair share of shared
#      ACCURATE: sum of all PSS = actual physical memory usage
# USS: Unique Set Size - only pages unique to this process
#      MOST ACCURATE for "what would be freed if this process died"
# 
# Rule: use PSS for "how much memory does this use"
#       use USS for "how much would I free by killing this"

# === slabtop: kernel slab cache ===
slabtop
# Active / Total Objects: 5432876 / 5674532
# Active / Total Slabs: 89012 / 91234
# Active / Total Caches: 112 / 156
# Active / Total Size: 1234.56M / 1456.78M
#  OBJS  ACTIVE   USE  OBJ SIZE  SLABS  OBJ/SLAB  CACHE SIZE  NAME
# 2345678 2234567  95%  0.19K  62345  38  249380K dentry
# 1234567 1198765  97%  0.62K  30864  40  246912K inode_cache
# 
# High dentry/inode cache: many files accessed (normal for busy servers)
# Unexpectedly large slab: investigate (possible leak or misconfiguration)
# slabtop -s c: sort by cache size (shows top memory consumers)

# === numastat: NUMA memory balance ===
numastat
#                            node0           node1
# numa_hit                 1234567         2345678
# numa_miss                  45678            1234
# numa_foreign               1234           45678
# interleave_hit              1234            2345
# local_node               1234567         2345678
# other_node                 45678            1234
#
# numa_miss >> numa_hit on a node: processes allocating on wrong NUMA node
# Performance impact: cross-NUMA memory access ~80ns vs local ~40ns
# Fix: taskset or numactl to pin processes to NUMA node

numastat -p java
# Shows per-NUMA-node memory usage for java process
```

---

### First Principles

```
Linux memory management layers:

Physical memory:
  4KB pages (standard), 2MB/1GB hugepages
  NUMA nodes: each CPU socket has directly attached RAM
  
Page cache (file cache):
  When file is read: pages cached in RAM (Cached in /proc/meminfo)
  Next read: served from cache (no disk I/O)
  When RAM needed: kernel reclaims (discards clean pages, writes dirty)
  This is why "buff/cache" is large - the kernel DELIBERATELY uses
  all available RAM for caching (free RAM = wasted RAM in Linux)

Anonymous pages:
  Heap (malloc), stack, mmap(MAP_ANONYMOUS)
  No backing file: must go to SWAP when evicted
  Cannot be simply discarded (data would be lost)
  OOM: kernel kills processes to free anonymous pages

Memory pressure escalation:
  1. Application allocates memory
  2. MemAvailable decreases
  3. Kernel reclaims inactive file cache (fast, no disk I/O)
     -> pgscank/s increases in sar -B
  4. File cache mostly reclaimed, pressure increases
  5. Kernel starts scanning active pages
  6. Dirty pages must be written before reclaim (I/O)
  7. Anonymous pages swapped out (if swap exists)
     -> so > 0 in vmstat (swap out)
  8. Swapped pages needed: swap in (performance collapse)
     -> si > 0 in vmstat (swap in)
  9. OOM: no memory can be reclaimed, kill a process

PSI (Pressure Stall Information):
  Kernel tracks: "was any task waiting for memory resource?"
  "some" time: >= 1 task stalled (partial stall)
  "full" time: ALL tasks stalled (complete stall)
  
  Why "full" matters more than "some":
  "some" can be > 0 even on healthy systems (one low-priority
  background task occasionally waiting)
  "full" means the ENTIRE system was stalled: everything stopped
  waiting for memory reclaim. A 1% full stall = 36 seconds of
  total system halt per hour!
  
  Linux kernel uses PSI for memory cgroup pressure:
  systemd-oomd uses PSI to kill cgroup before OOM hits
  cgroup2 memory.pressure file: per-cgroup PSI

vm.swappiness tuning:
  Default: 60 (kernel reclaims file cache and anonymous pages equally)
  0: maximize file cache retention, avoid swapping (but may cause OOM)
  100: swap aggressively before reclaiming file cache
  
  Controversial: swappiness=0 can cause MORE OOM kills!
  With swappiness=0: when OOM hits, no swap buffer existed
  With swappiness=60+: some pages moved to swap BEFORE OOM
    -> gives time for processes to react
  
  Best practice: swappiness=10-20 for latency-sensitive servers
  (minimal swapping but some buffer against OOM)

Memory overcommit:
  vm.overcommit_memory:
    0 (default): heuristic overcommit (allow unless clearly unfeasible)
    1: always commit (malloc always succeeds!)
    2: strict (commit <= swap + RAM * ratio)
  
  With overcommit enabled: malloc() always succeeds
  Actual pages allocated LAZILY when first written (SIGSEGV or OOM)
  This is why Java heaps don't consume RAM until actually used
```

---

### Thought Experiment

Diagnosing slow performance on a database server with "plenty of RAM":

```bash
# Alert: PostgreSQL response times spiking to 5 seconds
# Dashboard shows: 14GB of 16GB RAM "used", 1.5GB "free"

# Step 1: Check the right metric
free -h
# Available: 8.2GB (7GB is reclaimable page cache - PostgreSQL file cache!)
# Memory is NOT the problem based on free

# Step 2: Check vmstat
vmstat 1
#  si  so
#   0  0   <- no swapping at all

# Step 3: Check PSI
cat /proc/pressure/memory
# some avg10=0.12 avg60=0.08 avg300=0.02 total=56789
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0
# Memory pressure is minimal

# Step 4: CPU pressure?
cat /proc/pressure/cpu
# some avg10=5.23 avg60=8.45 avg300=12.34 total=12345678
# CPU PRESSURE is high! avg300=12.34%: over 5 minutes, 12% of
# time tasks were waiting for CPU!

# Step 5: iostat
iostat -xz 1
# nvme0: await=450ms, %util=99.8%
# DISK I/O SATURATION!

# Root cause: disk is the bottleneck, not memory
# PostgreSQL is doing full table scans (new query, missing index)
# Explanation: 14GB "used" memory includes PostgreSQL shared_buffers
# and page cache (correct and healthy). The actual bottleneck was
# disk I/O (missing index causing sequential scans of large tables).

# Lesson: memory metrics were misleading. 
# Full investigation required disk and CPU pressure metrics too.
```

---

### Mental Model / Analogy

```
Memory = hotel with rooms and a storage facility

Physical RAM = hotel rooms (limited: 16GB = 160 rooms)
Page cache = hotel staff pre-arranging commonly requested items in rooms
  (staff fills "empty" rooms with things guests might need)
  When a guest arrives: room already set up (cache hit = fast)
  When guest needs the room: staff removes the pre-arranged items (reclaim)
  
Free rooms = truly empty, never arranged (rare in a busy hotel)
Available rooms = empty + rooms that can be instantly cleared
  ("available" in free -m = actually usable for new guests)

Anonymous pages = guest luggage (must go to storage/swap if room needed)
File cache = hotel furniture (comes from storage, easy to replace)

Memory pressure levels:
  1. Hotel is busy (available rooms dropping):
     Staff starts consolidating staging items (reclaim)
     
  2. Hotel mostly full (available < 10%):
     Staff scrambling to find rooms (kswapd active, pgscank high)
     Guests might wait briefly for room preparation
     
  3. Hotel full (swapping starts, so > 0):
     Staff moves guest luggage to storage facility (swap)
     Next time guest needs luggage: retrieve from storage (slow!)
     
  4. Hotel + storage full (OOM):
     Manager forces one guest to check out immediately (OOM kill)
     Makes room for critical guests
     
PSI = hotel efficiency monitor:
  "some" pressure: some guests waiting for rooms (normal during busy hours)
  "full" pressure: ALL guests waiting, hotel completely halted
  
  Hotel manager (systemd-oomd) watches PSI:
  full > 1% over 60 seconds: proactively ask one guest to leave
  (graceful eviction before emergency checkout / OOM kill)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`free -h`: total, used, free, available. Why "available" matters. Swap usage.
Basic `vmstat 1`: si/so columns mean swapping. OOM = process killed when
out of memory. `/proc/meminfo` exists with more detail.

**Level 2:**
`/proc/meminfo` key fields: MemAvailable, AnonPages, Cached, Slab. RSS vs
PSS vs USS (smem). `vmstat` columns: active/inactive pages, si/so. kswapd
process: kernel memory reclaim daemon. `dmesg | grep -i oom` for OOM kills.
`slabtop` for kernel slab cache. Swap behavior and vm.swappiness.

**Level 3:**
PSI (/proc/pressure/memory): some vs full, avg10/avg60/avg300 interpretation.
`sar -B` for paging statistics (pgscank, pgsteal). NUMA effects: numastat,
numastat -p, performance impact of cross-NUMA allocation. Memory cgroup:
memory.limit_in_bytes, memory.usage_in_bytes, memory.events (oom, oom_kill).
Memory overcommit (vm.overcommit_memory). Transparent Huge Pages (THP):
performance impacts.

**Level 4:**
`smem -s pss -r -t -n` for accurate per-process memory. `/proc/PID/smaps`
for virtual address space breakdown. `pmap -x PID` for process memory map.
Memory compaction (defrag for hugepages): `compact_memory` trigger. NUMA
pinning: `numactl --cpunodebind=0 --membind=0 cmd`. Memory bandwidth
saturation: `perf stat -e node-loads,node-load-misses`. `systemd-oomd`
configuration (PSI-based OOM protection). cgroup v2 memory pressure notification.

**Level 5:**
Kernel memory allocator internals: SLAB, SLUB, SLOB. Buddy allocator:
page coalescing, fragmentation. Memory compaction: synchronous (direct)
vs asynchronous (kcompactd) compaction. LRU page lists: active vs inactive,
file vs anon. kswapd and direct reclaim: when allocation blocks waiting for
reclaim. eBPF memory probing: `bpftrace -e 'kprobe:mm_page_alloc { @stack =
hist(kstack); }'` - trace which kernel code is allocating pages. Kernel
KASAN, KMSAN for memory safety. `/proc/buddyinfo` for memory fragmentation
analysis.

---

### How It Works

```
MemAvailable calculation (from kernel source):
  MemAvailable = MemFree 
                + (LowFree + file_lru - min_file_kbytes)
                + SReclaimable
                
  - file LRU: Inactive(file) + Active(file) - reserved for kernel
  - SReclaimable: dentry/inode caches
  - Minus watermarks: kernel reserves some pages for emergency use
  
  Result: what can actually be allocated without triggering OOM
  Typically much larger than MemFree alone

kswapd algorithm:
  Background kernel thread, wakes when free pages < watermark
  
  Watermarks (per zone, e.g., Normal zone):
    pages_min: OOM threshold
    pages_low: kswapd wakes
    pages_high: kswapd stops
  
  Reclaim order (kswapd tries in order):
    1. LRU inactive file pages (clean: just unmap, dirty: writeback first)
    2. LRU active file pages (demote to inactive first)
    3. LRU inactive anonymous pages (write to swap)
    4. LRU active anonymous pages (demote to inactive)
    5. Slab reclaimable (dentry/inode cache shrink)
  
  If watermarks not met after full LRU scan:
    Direct reclaim: calling process stalls to reclaim pages
    OOM kill: if direct reclaim insufficient

vm.swappiness effect:
  Controls relative reclaim pressure on file cache vs anonymous pages
  swap_tendency = mapped_ratio + distress + vm.swappiness
  Higher swappiness: anonymous pages reclaimed earlier
  swappiness=0: anonymous pages reclaimed last (avoid swap)
  Effect on OOM: with swappiness=0, file cache stays longer,
    anonymous pages stay longer -> OOM hits sooner!
    With higher swappiness: anonymous pages in swap provides buffer
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "High buff/cache means memory is wasted" | buff/cache is USEFUL work. The kernel is using RAM for file system caching (page cache) - reads are served from RAM instead of disk (100x faster). This memory is "in use" but immediately reclaimable. If an application needs more RAM, the kernel silently reclaims these cache pages. A system with 90% buff/cache is HEALTHY - it means all RAM is being productively used. You should be concerned when `available` drops to near zero AND the system starts swapping (si/so > 0 in vmstat), not just because buff/cache is high. |
| "Setting vm.swappiness=0 prevents swapping and improves performance" | vm.swappiness=0 means the kernel avoids swapping anonymous pages BUT still SWAPS if memory is exhausted (it's not a hard prohibition). More importantly: it can cause worse outcomes. With swappiness=0, the kernel aggressively reclaims page cache instead of moving anonymous pages to swap. For database servers: this kills database file caching performance. For general servers: losing page cache forces re-reads from disk when swap would have been cheaper. The trade-off: for latency-sensitive applications where swap causes unacceptable latency spikes, swappiness=1-10 provides a reasonable middle ground. For databases that manage their own cache (MySQL, PostgreSQL): swappiness=10 is often recommended. |
| "RSS is the most accurate measure of process memory" | RSS (Resident Set Size) is the MOST MISLEADING common memory metric. It counts ALL pages mapped by the process, including shared library pages counted multiple times across all processes. A Node.js server with 50 workers might show RSS=100MB each (50 * 100MB = 5GB) while the actual physical memory usage is only 200MB (50 workers sharing the same Node.js binary and V8 engine pages). PSS (Proportional Set Size) divides shared pages proportionally. USS (Unique Set Size) counts only truly private pages. For "how much memory does this process use": PSS. For "how much would be freed by killing this process": USS. RSS: useful for detecting memory leaks within a single process over time (if RSS grows unbounded, there's a leak). |
| "Swap space is a sign of a poorly configured system" | Swap serves multiple important purposes. (1) Emergency buffer: allows processes to survive brief memory spikes without OOM kills. (2) Idle process paging: rarely-used process pages can reside on swap, freeing RAM for active processes. (3) Hibernate/suspend: full system state saved to swap. The issue is not HAVING swap but USING it heavily (high si/so rates). A system with 16GB RAM and 8GB swap at 0% active swap usage is healthy. A system without swap: any OOM condition immediately kills processes with no buffer. Kubernetes nodes often use no swap (pods should have predictable memory requirements), but general-purpose Linux servers benefit from having swap configured. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: OOM kill diagnosis ===
dmesg -T | grep -i "oom\|out of memory\|killed process"
# [Fri May 17 14:32:15 2024] Out of memory: Kill process 1234 (java) 
#   score 890 or sacrifice child
# [Fri May 17 14:32:15 2024] Killed process 1234 (java) total-vm:8388608kB,
#   anon-rss:7340032kB, file-rss:0kB, shmem-rss:0kB

# Analyze OOM score:
cat /proc/1234/oom_score       # 0-1000, higher = more likely to be killed
cat /proc/1234/oom_score_adj   # -1000 to 1000, adjust score
# Protect a process from OOM kill:
echo -1000 > /proc/1234/oom_score_adj
# (requires root, value -1000 = never kill)

# Find which process has highest oom_score:
for pid in /proc/[0-9]*/; do
    pid_num=${pid#/proc/}; pid_num=${pid_num%/}
    score=$(cat /proc/$pid_num/oom_score 2>/dev/null || echo 0)
    name=$(cat /proc/$pid_num/comm 2>/dev/null || echo unknown)
    echo "$score $pid_num $name"
done | sort -rn | head -10

# === Failure: memory leak diagnosis ===
# Process RSS growing unbounded:
ps -o pid,comm,rss --sort=-rss | head -10
# If RSS grows 10MB/hour: potential leak

# Track RSS over time:
while true; do
    ps -p 1234 -o rss --no-headers
    sleep 60
done | awk '{print NR, $1}'
# If consistently increasing: memory leak

# Detailed breakdown:
cat /proc/1234/smaps | grep -E "^(Rss|Pss|Size|Anon|Heap)"
# Heap entry showing large Size+Rss: heap leak
# Many small anonymous mappings: fragmented allocation leak

# For Java: jmap -histo 1234 (heap histogram)
# For C/C++: valgrind --leak-check=full (development only)

# === Diagnosis: high kernel slab cache ===
slabtop -s c -o
# If kmalloc-* entries are large: kernel driver allocating and not freeing
# If dentry cache very large: many files being accessed (normal for web server)
# If inode_cache large: many open files (check ulimit -n and /proc/sys/fs/file-nr)

# Drop slab cache (ONLY for testing/diagnosis, impacts performance):
echo 2 > /proc/sys/vm/drop_caches  # drop dentry/inode cache
echo 3 > /proc/sys/vm/drop_caches  # drop all caches (page + slab)
# WARNING: causes performance degradation as caches rebuild
# NEVER use on production under load!

# === NUMA imbalance diagnosis ===
numastat
# If numa_miss is high on node0, numa_foreign is high on node1:
# Processes on CPU0 are allocating on NUMA node 1 (non-local)
# Fix: check BIOS NUMA settings, check process pinning
numastat -m | grep -E "MemFree|MemUsed"
# Is one NUMA node nearly full while other has plenty?
# Fix: numactl to distribute processes across NUMA nodes

# === PSI-based alerting ===
# Alert when memory full stall > 1% over 60 seconds:
awk '/full/ {if ($4 > 1.0) print "ALERT: memory pressure " $4}' \
    /proc/pressure/memory
```

---

### Related Keywords

**Foundational:**
LNX-063 (memory management), LNX-083 (OOM killer)

**Builds on this:**
LNX-093 (USE method), LNX-095 (CPU performance)

**Related:**
LNX-093 (performance troubleshooting)

---

### Quick Reference Card

| Command | What it shows |
|---------|--------------|
| `free -h` | Memory summary (focus on "available") |
| `cat /proc/meminfo` | Detailed memory breakdown |
| `vmstat 1` | si/so: swap I/O (> 0 = pressure) |
| `cat /proc/pressure/memory` | PSI: full stall % |
| `smem -s pss -r` | Per-process PSS memory |
| `slabtop -s c` | Kernel slab cache by size |
| `numastat` | NUMA memory distribution |
| `dmesg | grep -i oom` | OOM kill history |

**3 things to remember:**
1. "available" in `free -h` = what actually matters. `free` RAM is misleading. Large buff/cache is GOOD - it's the kernel using RAM productively for caching.
2. Memory pressure escalation: low available -> kswapd scans (sar -B pgscank) -> swap I/O (vmstat si/so) -> OOM kill. PSI (full stall) provides early warning before si/so > 0.
3. RSS is inflated by shared libraries. Use PSS for "how much does this process use" and USS for "how much freed if killed."

---

### Transferable Wisdom

Linux memory pressure concepts transfer directly to: JVM heap management
(MemAvailable = JVM free heap, GC pressure = kswapd scanning, GC pause =
direct reclaim, OOM = OutOfMemoryError). Container memory limits (cgroup
memory.max = MemTotal for the container, PSI monitoring per cgroup). Database
buffer pools (InnoDB buffer pool = page cache, dirty pages = Dirty in
/proc/meminfo, checkpoint = kswapd writeback). The PSI (Pressure Stall
Information) concept is now used by Facebook's (Meta's) resource management
system, systemd-oomd, and cgroup2 - the idea of measuring "time stalled"
instead of just "utilization" is more accurate for capturing performance
impact. The `MemAvailable` calculation (not just `MemFree`) is the same
insight as: connection pool "available connections" = idle + ones that will
complete soon (not just idle), thread pool "available capacity" = idle +
threads that will finish current work + burst capacity. Always measure what
is actually available for new work, not just what is currently idle.

---

### The Surprising Truth

The `MemAvailable` field in `/proc/meminfo` was only added in Linux kernel
3.14 (released March 2014). Before that, the "correct" way to determine
available memory was to manually parse and calculate from multiple fields.
Many monitoring tools and scripts written before 2014 still use `MemFree`
(wrong!) because their authors didn't know about `MemAvailable` or were
written before it existed. This is why you still see cloud monitoring
dashboards from major providers that alert on "low free memory" when the
system actually has gigabytes available in page cache. The `free` command
itself was confusing users for so long (showing "used" memory that included
reclaimable cache as if it were truly consumed) that the output format was
changed in `procps` 3.3.10 (2014) to add the "available" column. Before
this change: the `free` command's output was actively misleading, showing
"used" memory that included reclaimable cache alongside truly used memory
with no distinction. The patch to add `MemAvailable` to the kernel and the
update to the `free` command happened simultaneously - fixing both the kernel
API and the userspace tool at the same time.

---

### Mastery Checklist

- [ ] Can correctly interpret `free -m` output and explain why "available" matters more than "free"
- [ ] Knows the escalation path from low memory to OOM kill and can identify the stage from metrics
- [ ] Can use PSI to detect memory pressure before swapping starts
- [ ] Understands the difference between RSS, PSS, and USS and when to use each
- [ ] Can use smem and slabtop to find the actual memory consumers on a system

---

### Think About This

1. A Kubernetes node has 32GB RAM. All pods have memory requests totaling
   28GB and limits totaling 60GB (overcommitted at limits). The node starts
   experiencing OOM kills. Walk through: (a) the sequence of events from
   normal operation to OOM, (b) what PSI metrics would show before vs during
   the crisis, (c) how Kubernetes' QoS classes (Guaranteed, Burstable,
   BestEffort) affect which pods get OOM-killed and in what order, (d) what
   monitoring alert would have warned you before the crisis, and (e) what
   capacity or configuration change would prevent recurrence.

2. A team measures their microservice memory usage and sees RSS = 512MB per
   instance, with 20 instances running = "10GB used". But the server only
   shows 4GB of memory in use. Explain the discrepancy mathematically using
   PSS and USS. What percentage of the RSS is likely shared Go/Java runtime?
   How would you design memory capacity planning for this service correctly?
   What metric would you use for per-instance memory billing in a multi-tenant
   system?

3. Design a memory pressure early-warning system for a fleet of 1000 servers.
   Requirements: detect memory pressure 5 minutes before OOM kills occur,
   minimize false positives, and automatically trigger remediation (graceful
   pod eviction). What metrics would you collect? What PSI thresholds would
   you set? How would you distinguish between healthy high memory utilization
   (all RAM used for cache) vs genuine memory pressure (approaching OOM)?
   What automation would you implement to respond before humans need to?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you interpret `free -m` output correctly and what's the most important metric for available memory?
A: FREE COMMAND OUTPUT: `free -m` shows: (1) Mem row: total/used/free/shared/buff+cache/available. The columns that MATTER and don't: `total` = total physical RAM. `used` = RAM used by processes (includes stack, heap, code). `free` = RAM not used by ANYTHING - this is usually small on Linux and is NOT a useful metric. `buff/cache` = filesystem buffers and page cache - the kernel caches disk reads here to speed up repeated reads. This IS reclaimable. `available` = THE MOST IMPORTANT METRIC. It's an ESTIMATE of how much RAM can be given to new processes without swapping: free + reclaimable portion of buff/cache minus kernel reserves. WHY BUFF/CACHE IS GOOD: Linux deliberately fills empty RAM with file system cache. Empty RAM = wasted opportunity. If you read a 1GB file: it goes into page cache. Next read is served from RAM (microseconds) not disk (milliseconds). When another process needs RAM: kernel silently reclaims this cache. CORRECT INTERPRETATION: `free -h` showing available = 4GB means you can allocate 4GB of new process memory without any performance impact. Even if "free" is only 200MB, "available = 4GB" means you're fine. WHEN TO WORRY: when `available` drops below 500MB or 5% of total. Then: check vmstat si/so - if > 0: you're actively swapping (severe). Check /proc/pressure/memory full avg60 > 1%: system stalling. Check dmesg for OOM kills. The `MemAvailable` field was added to /proc/meminfo in Linux 3.14 (2014) specifically because the free/used distinction was so commonly misunderstood. Always use `available`, never `free`.

**Expert:**
Q: Explain PSI (Pressure Stall Information) and how it improves on traditional utilization-based memory monitoring.
A: TRADITIONAL MEMORY MONITORING PROBLEMS: The traditional approach measures "utilization" (how much memory is used vs total). Problem: at 90% memory utilization, the system might be perfectly healthy (90% is page cache, all reclaimable with no performance impact) OR severely degraded (90% is application heap, system constantly swapping). Utilization doesn't distinguish. Classic metrics (vmstat si/so) only trigger when swapping STARTS - by then, performance has already degraded. WHAT PSI MEASURES: PSI measures TIME STALLED waiting for a resource. For memory: "how much time did tasks spend waiting because memory was not available?" - this captures the PERFORMANCE IMPACT of memory pressure, not just the utilization state. PSI provides two metrics: (1) "some": percentage of time at least one task was stalled waiting for memory. Can be non-zero even in healthy systems. (2) "full": percentage of time ALL tasks were stalled for memory simultaneously. This is the critical metric - when full > 0, the entire system was halted. Even 0.1% full stall = 86ms/day of complete halting. PSI provides three time windows: avg10 (recent 10s), avg60 (1 minute), avg300 (5 minutes). PROGRESSIVE ALERTING: Level 1 alert: `some avg300 > 5%` (sustained moderate pressure over 5 minutes, investigate). Level 2: `some avg60 > 20%` (significant pressure, start graceful degradation). Level 3 emergency: `full avg10 > 1%` (active stalling, OOM likely imminent). SYSTEMD-OOMD: Facebook contributed PSI-based OOM daemon to systemd. It monitors cgroup PSI and kills the highest-memory cgroup before the kernel OOM killer fires. This allows graceful process selection (kill background batch jobs, not your web server) vs kernel OOM killer (kills by score, often picks the wrong process). PSI IN KUBERNETES: Kubernetes 1.27+ uses PSI for eviction decisions. Node pressure eviction can use memory.pressure PSI metrics to evict pods before OOM. ADVANTAGE OVER vmstat si/so: PSI detects pressure 30-120 seconds earlier than si/so > 0 starts appearing. This advance warning allows automated response (scale out, restart leaked process, trigger GC) before performance completely degrades.
