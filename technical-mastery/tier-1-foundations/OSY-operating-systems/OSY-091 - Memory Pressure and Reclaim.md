---
id: OSY-091
title: Memory Pressure and Reclaim
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-054, OSY-070, OSY-090
used_by: []
related: OSY-090, OSY-092, OSY-101
tags:
  - memory-pressure
  - reclaim
  - OOM
  - kernel
  - production
  - diagnosis
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 91
permalink: /technical-mastery/osy/memory-pressure-reclaim/
---

## TL;DR

Linux reclaims memory through three mechanisms: background
kswapd (proactive), direct reclaim (synchronous, causes
latency spikes), and OOM kill (last resort). Understanding
when each triggers, what it reclaims (file-backed vs
anonymous pages), and how to tune pressure thresholds is
essential for preventing production latency degradation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-091 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | memory reclaim, kswapd, direct reclaim, OOM, page eviction |
| **Prerequisites** | OSY-054, OSY-070, OSY-090 |

---

### Memory Zones and Watermarks

```
Linux divides memory into zones (DMA, Normal, HighMem on 32-bit).
Each zone has three watermarks:
  
  min_free_kbytes (vm.min_free_kbytes):
    Below min: direct reclaim (synchronous, application blocked)
    Kernel raises this above default in high-memory servers
    Default: roughly sqrt(RAM in KB) * 4
    
  low watermark:
    kswapd wakes up to reclaim pages in background
    
  high watermark:
    kswapd stops reclaiming; memory is "comfortable"
    
  Watermark visualization:
  
  |============ Total RAM =========================|
  |                                                |
  | ^high watermark  kswapd: stops reclaiming      |
  | ^low watermark   kswapd: starts reclaiming     |
  | ^min watermark   direct reclaim (latency!)     |
  |________________________________________________|
  
  Check current watermarks:
    cat /proc/zoneinfo | grep -E 'min|low|high|free'
    
  Why this matters:
    If applications allocate memory faster than kswapd reclaims,
    free pages drop to min -> direct reclaim -> ALL allocating
    threads stall until pages are freed.
    Symptoms: allocation latency spikes; P99 jumps 10-100ms.
```

---

### Reclaim Targets: What Gets Reclaimed

```
Reclaim order (preference):
  
  1. File-backed pages (page cache):
     - Clean file pages: evict immediately (re-read from disk)
     - Dirty file pages: flush to disk first, then evict
     - Cost: disk read on next access (if evicted)
     
  2. Anonymous pages (heap, stack, mmap'd anonymous):
     - Can be swapped to swap device
     - If no swap: cannot evict! This is a hard limit.
     - Swapping: 10-1000x slower than page cache eviction
     - Swapped page re-access: disk read required
     
  vm.swappiness controls reclaim aggressiveness:
    vm.swappiness = 0: strongly prefer file cache eviction
      (swap only when no file cache left)
    vm.swappiness = 60: balanced
    vm.swappiness = 100: aggressively swap anonymous pages
    
  For JVM production servers:
    vm.swappiness = 1 (minimum non-zero):
      Avoid swapping JVM heap (would cause GC latency spikes)
      But allow swap as last resort before OOM kill
      
  For Redis, memcached:
    vm.swappiness = 0 or 1:
      Cache servers rely on memory; any swap = data unavailability
      
  Checking reclaimable memory:
    cat /proc/meminfo | grep -E 'MemAvailable|Reclaimable|Cached'
    MemAvailable: free + reclaimable (best metric for "is RAM available?")
    SReclaimable: reclaimable kernel memory (slab cache)
```

---

### kswapd: Background Reclaim

```
kswapd (one per NUMA node):
  - Kernel thread: kswapd0 (Node 0), kswapd1 (Node 1)
  - Wakes when free pages drop below low watermark
  - Scans inactive lists; evicts/swaps pages
  - Goal: replenish free pages to high watermark
  - Runs concurrently with applications (no stalls)
  
  Monitor kswapd activity:
    vmstat 1 | head -5  # si (swap in), so (swap out) columns
    vmstat 1: 
      si: pages swapped in from disk (per second)
      so: pages swapped out to disk (per second)
      Non-zero si/so: memory pressure is significant
      
    cat /proc/$(pidof kswapd0)/status | grep VmRSS
    # Low RSS: kswapd is active but lightweight
    
    perf stat -e kmem:* kswapd0  # kswapd syscall tracing
    
  When kswapd can't keep up:
    kswapd reclaims pages; but allocations are faster
    Free pages hit min watermark
    -> Direct reclaim triggered (application threads reclaim)
```

---

### Direct Reclaim: The Latency Killer

```
Direct reclaim: application thread performing memory allocation
  must reclaim pages itself before allocation can complete.
  
  Impact:
    malloc(100MB) might take 5-50ms instead of microseconds
    GC allocation path hits direct reclaim: GC pause extends
    Web request handler allocates: request latency spikes
    
  Identify direct reclaim:
    cat /proc/vmstat | grep allocstall
    # allocstall: times direct reclaim was triggered
    # Monotonically increasing; non-zero = memory pressure history
    
    perf trace -e mm_vmscan_direct_reclaim_begin PID
    # Traces start of direct reclaim events for a process
    
    /proc/PID/status | grep VmPeak
    # Growing VmPeak: process is allocating more memory over time
    
  Fix:
    1. More RAM (obvious but sometimes the correct answer)
    2. Increase vm.min_free_kbytes:
       Forces kswapd to maintain larger free pool
       Tradeoff: less RAM for application working set
    3. Reduce application memory footprint:
       JVM: -XX:MaxRAMPercentage, check for off-heap leaks
       Databases: reduce buffer pool
    4. Faster reclaim: lower vm.dirty_ratio so writeback starts
       sooner (less time dirty pages block reclaim)
```

---

### Memory Pressure Metrics for Alerting

```
The three-tier alert strategy:
  
  Tier 1 (warning): MemAvailable drops below 20% of total
    alert: MemAvailable < 0.20 * MemTotal
    Action: investigate; prepare to scale
    Metric: node_memory_MemAvailable_bytes (Prometheus)
    
  Tier 2 (critical): vmstat si > 0 (swap activity starts)
    alert: node_vmstat_pswpin > 0 for 60 seconds
    Action: immediate investigation; possible scale-out
    
  Tier 3 (page): allocstall rate increasing
    cat /proc/vmstat | grep allocstall
    alert: allocstall increasing > 10/minute
    Action: application memory leak or load spike
    
  Container-specific metrics:
    container_memory_working_set_bytes:
      RSS + anonymous = actual physical memory needed
      Alert: working_set > 80% of container limit
    container_oom_events_total:
      Any increment: containers being OOM killed
      
  Quick health check:
    free -h
    # If "available" is < 500MB on a 16GB server: investigate
    
    cat /proc/buddyinfo
    # Shows contiguous free page blocks by size
    # All small (order 0-2): fragmentation; huge page allocation will fail
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Lots of 'buff/cache' in free means RAM is being wasted" | Page cache (buff/cache) is productive use of RAM. It caches frequently accessed files. The kernel reclaims it instantly when applications need memory. 'Available' in `free -m` correctly accounts for reclaimable cache. Don't mistake cache for waste. |
| "Enabling swap prevents OOM kills" | Swap allows anonymous pages to survive memory pressure by moving to disk. But if the swap device is slow (spinning disk), accessing swapped pages causes massive latency (10ms+ per page fault). A Java process with 4GB swapped may experience multi-second GC pauses. Swap is a safety net, not a performance strategy. |
| "vm.swappiness=0 disables swapping" | vm.swappiness=0 makes the kernel strongly prefer evicting file cache over swapping anonymous pages, but swapping still occurs as a last resort. To truly prevent swapping: disable the swap device (`swapoff -a`). |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| Direct reclaim latency | P99 spikes unpredictably | `allocstall` in `/proc/vmstat` increasing | Increase `min_free_kbytes`; add RAM |
| Swap storm | Application appears hung | `vmstat si` > 100 pages/sec | `swapoff -a`; reduce memory footprint |
| OOM kill | Process disappears; `dmesg` shows kill | `dmesg \| grep 'Killed process'` | Fix leak; set `oom_score_adj`; add RAM |
| Page cache eviction causing cache misses | DB/cache suddenly slow after memory spike | `iostat -x`: high reads; `free` shows low cache | Identify memory hog; tune `vm.swappiness` |

---

### Quick Reference Card

| Metric | Command | Interpretation |
|--------|---------|----------------|
| True free memory | `free -m` available | < 20% total = warning |
| Swap activity | `vmstat 1` si/so | > 0 = active swapping |
| Direct reclaim count | `/proc/vmstat allocstall` | Any increase = pressure |
| OOM kill log | `dmesg \| grep -i 'oom\|killed'` | Any = investigate |
| kswapd activity | `ps aux \| grep kswapd` | CPU > 1% = sustained pressure |
| Reclaimable cache | `cat /proc/meminfo \| grep SReclaimable` | Slab cache that can be freed |
