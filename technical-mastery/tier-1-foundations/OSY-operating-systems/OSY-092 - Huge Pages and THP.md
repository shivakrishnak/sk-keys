---
id: OSY-092
title: Huge Pages and Transparent Huge Pages
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-054, OSY-055, OSY-057, OSY-091
used_by: []
related: OSY-088, OSY-091, OSY-093
tags:
  - huge-pages
  - THP
  - TLB
  - memory
  - JVM
  - performance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 92
permalink: /technical-mastery/osy/huge-pages-thp/
---

## TL;DR

Huge pages (2MB on x86-64 vs default 4KB) reduce TLB pressure
for large working sets. Two variants: explicit huge pages
(pre-allocated, guaranteed) and Transparent Huge Pages (THP,
kernel-managed). THP is convenient but causes latency spikes
(compaction stalls). For JVMs and Redis: explicit huge pages
preferred. THP causes notorious Redis latency spikes and JVM
GC pauses.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-092 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | huge pages, THP, TLB, 2MB pages, JVM tuning, Redis |
| **Prerequisites** | OSY-054, OSY-055, OSY-057, OSY-091 |

---

### Why Huge Pages?

```
Normal pages: 4KB (x86-64 base page size)
Huge pages: 2MB (512x larger) or 1GB (gigantic pages)

The TLB (Translation Lookaside Buffer) problem:
  TLB caches: virtual address -> physical address mappings
  Each TLB entry: covers ONE page (4KB by default)
  L1 TLB: 64 entries -> covers 64 * 4KB = 256KB of memory
  L2 TLB: 1024 entries -> covers 1024 * 4KB = 4MB of memory
  
  Problem: a JVM with 4GB active heap needs:
    4GB / 4KB = 1M TLB entries
    L2 TLB has 1024 entries
    Working set 1000x bigger than TLB capacity
    Result: constant TLB misses -> 4 memory lookups per page access
    
  With 2MB huge pages:
    4GB / 2MB = 2048 TLB entries needed
    L2 TLB: 1024 entries (still not all, but 500x better!)
    TLB coverage: 1024 * 2MB = 2GB of working set
    
  perf stat shows:
    Before huge pages: dTLB-load-misses = 15%
    After huge pages: dTLB-load-misses = 0.5%
    Real workload improvement: 10-30% for memory-intensive apps
```

---

### Explicit Huge Pages (Static)

```
Pre-allocated huge pages: reserved at boot or runtime.
Cannot be used for other purposes (not reclaimable).
  
  Check available huge page sizes:
    ls /sys/kernel/mm/hugepages/
    # hugepages-1048576kB (1GB pages)
    # hugepages-2048kB (2MB pages)
    
  Allocate 2MB huge pages at runtime:
    # Request 2048 huge pages = 4GB of huge page memory
    echo 2048 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
    
    # Verify allocation:
    cat /proc/meminfo | grep HugePages
    # HugePages_Total: 2048
    # HugePages_Free: 2048
    # HugePages_Rsvd: 0
    # Hugepagesize: 2048 kB
    
  Make persistent (add to /etc/sysctl.conf):
    vm.nr_hugepages = 2048
    
  JVM huge pages configuration:
    java -XX:+UseLargePages \
         -XX:LargePageSizeInBytes=2m \
         -jar application.jar
         
    Requirements:
      1. Huge pages allocated: nr_hugepages >= heap_size / 2MB
      2. JVM user in hugepages group or capable user
      3. /etc/security/limits.conf:
         * soft memlock unlimited
         * hard memlock unlimited
         
    Verification:
      After JVM starts:
      cat /proc/meminfo | grep HugePages_Free
      # Should decrease by heap_size / 2MB
      
  Advantage: zero compaction overhead; always 2MB pages
  Disadvantage: reserved memory; cannot be used by other processes
```

---

### Transparent Huge Pages (THP)

```
THP: kernel automatically promotes 4KB pages to 2MB where possible.
No explicit application code changes needed.

  Modes:
    always: THP for all anonymous memory (default on many distros)
    madvise: THP only for memory with MADV_HUGEPAGE hint
    never: THP disabled
    
  Check and set:
    cat /sys/kernel/mm/transparent_hugepage/enabled
    # [always] madvise never (brackets = current)
    
    echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
    
  How THP works:
    1. Application allocates anonymous memory (heap, stack)
    2. Normal 4KB pages are allocated initially
    3. khugepaged daemon scans memory periodically
    4. Finds 512 contiguous 4KB pages (same virtual range)
    5. Promotes to one 2MB huge page
    
  THP compaction:
    Problem: over time, memory becomes fragmented
    512 contiguous 4KB pages may not be available
    khugepaged must "compact" memory: move existing pages
    During compaction: application pages locked briefly
    Result: application pause (can be 10-100ms)
    
THP problems:
  
  1. Redis latency spikes (well-documented):
     Redis: mostly in-memory operations; low latency expected
     THP compaction: 50-100ms stall during compaction
     Redis: appears as latency spike in percentile charts
     Redis documentation: explicitly recommends disabling THP
     redis-check-aof: warns about THP being enabled
     Fix: echo never > /sys/kernel/mm/transparent_hugepage/enabled
     
  2. JVM GC pause amplification:
     G1GC: concurrent phases run alongside Java threads
     THP compaction: moves pages under GC (page table changes)
     Result: GC STW pause includes compaction delays
     Symptom: GC pause > target despite low survivor rate
     Fix: use explicit huge pages (-XX:+UseLargePages) instead of THP
     
  3. Fork + COW amplification:
     Normal fork (COW): copy only written pages
     With 2MB THP pages: writing ONE byte to a huge page
       causes copy of the entire 2MB page
     Redis BGSAVE (fork for persistence):
       Each write to a 2MB page copies 2MB (not 4KB)
       Memory amplification: 512x per write
       Redis BGSAVE with THP: 2x-10x more memory usage
```

---

### BAD vs GOOD Configuration

```java
// BAD: THP enabled (default) for Redis/JVM
// Result: unpredictable latency spikes

// In /etc/rc.local or startup script:
// (no change) = THP "always" = compaction stalls

// GOOD: Production Redis configuration
// /etc/rc.local:
/*
  echo never > /sys/kernel/mm/transparent_hugepage/enabled
  echo never > /sys/kernel/mm/transparent_hugepage/defrag
*/
// Redis.conf:
/*
  # Redis documentation says:
  # "Make sure to disable Linux kernel feature
  #  transparent huge pages"
*/
```

```bash
# BAD: JVM with THP (compaction stalls)
java -Xmx4g -jar app.jar
# THP enabled: GC pauses 10-100ms more than expected

# GOOD: JVM with explicit huge pages
# First: allocate huge pages
echo 2048 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
# Then: JVM uses them
java -Xmx4g -XX:+UseLargePages -jar app.jar
# Result: TLB misses reduced; GC pauses more predictable
```

---

### Comparison Table

| Feature | Explicit Huge Pages | THP |
|---------|---------------------|-----|
| Allocation | Pre-allocated by admin | Automatic by kernel |
| Availability | Always available | May fail if fragmented |
| Compaction overhead | None | khugepaged pauses |
| COW overhead | High (2MB page copy) | High (2MB page copy) |
| Memory reserved | Yes (locked, not reclaimable) | No |
| JVM support | -XX:+UseLargePages | Automatic (but problematic) |
| Redis recommendation | Not applicable | Disable (echo never) |
| For page cache | No (not supported) | No (anonymous only) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "THP is always better than 4KB pages" | THP reduces TLB misses but introduces compaction stalls. For latency-sensitive applications (Redis, real-time), THP stalls (10-100ms) are worse than TLB misses. For batch/throughput workloads with large stable working sets, THP can help. |
| "Huge pages waste memory by pre-allocating" | Explicit huge pages do reserve memory that can't be used for other purposes. But they eliminate runtime compaction overhead. For a dedicated JVM server (not multi-tenant), this is the correct trade-off. |
| "THP and explicit huge pages are the same thing" | Different mechanisms: THP is transparent (kernel-managed, may use 4KB or 2MB). Explicit huge pages are pre-allocated, always 2MB, accessed via mmap with MAP_HUGETLB or posix_memalign. JVM's -XX:+UseLargePages requests explicit huge pages, not THP. |

---

### Quick Reference Card

| Task | Command |
|------|---------|
| Check THP status | `cat /sys/kernel/mm/transparent_hugepage/enabled` |
| Disable THP | `echo never > /sys/kernel/mm/transparent_hugepage/enabled` |
| Allocate explicit huge pages | `echo N > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages` |
| Check huge page usage | `cat /proc/meminfo \| grep HugePages` |
| JVM huge pages flag | `-XX:+UseLargePages -XX:LargePageSizeInBytes=2m` |
| Detect TLB pressure | `perf stat -e dTLB-load-misses -p PID` |
| For Redis | Disable THP; mention in Redis docs explicitly |
