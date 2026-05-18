---
id: OSY-090
title: Page Cache Internals
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-012, OSY-016, OSY-054, OSY-089
used_by: []
related: OSY-089, OSY-091, OSY-096
tags:
  - page-cache
  - kernel
  - memory
  - I/O
  - mmap
  - performance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 90
permalink: /technical-mastery/osy/page-cache-internals/
---

## TL;DR

Linux page cache is the single largest consumer of RAM on most
servers. It caches all file reads and write-buffered writes.
Understanding dirty page lifecycle, eviction policy (LRU-2),
mmap sharing, and writeback tuning is essential for diagnosing
I/O latency spikes, OOM conditions, and Kafka/database
performance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-090 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | page cache, dirty pages, writeback, mmap, LRU, I/O performance |
| **Prerequisites** | OSY-012, OSY-016, OSY-054, OSY-089 |

---

### What Is the Page Cache?

```
Page cache = kernel's unified buffer for all file-backed I/O.
  
  Before page cache (early Unix):
    Every read() -> disk I/O
    Every write() -> disk I/O (synchronous)
    Very slow; disk is 10,000x slower than RAM
    
  With page cache:
    First read(file, offset, n):
      - Page fault on file-backed mapping
      - Kernel reads 4KB page from disk into RAM
      - Data served from RAM
    Second read(same file, offset, n):
      - Page already in cache
      - memcpy from kernel page to user buffer: ~100ns
      - No disk I/O
      
  write(file, buf, n):
    - Data written to page cache (kernel memory) = dirty page
    - Returns to application IMMEDIATELY
    - Kernel flushes dirty page to disk asynchronously
    
  This is why: write() returns fast, but the data may not
  survive a power failure until fsync() or kernel flushes.
```

---

### Dirty Page Lifecycle

```
Page states:
  
  CLEAN: page in cache = disk content (no writes pending)
  DIRTY: page in cache != disk (write happened; not yet flushed)
  LOCKED: page being transferred to/from disk (I/O in progress)
  
  Write lifecycle:
    1. write(fd, buf, n):
       - Page found in cache (or new page allocated)
       - Data copied from user buf to kernel page
       - Page marked DIRTY
       - Application returns immediately
       
    2. Writeback trigger (async):
       - vm.dirty_background_ratio (default 10%):
         when dirty pages > 10% of RAM:
         kernel starts background flusher (bdflush/writeback)
       - vm.dirty_ratio (default 20%):
         when dirty pages > 20% of RAM:
         ALL subsequent writes BLOCK until dirty < 20%
         (this is a write stall - application completely stops)
         
    3. Write stall diagnosis:
       cat /proc/vmstat | grep dirty_throttle_count
       # Non-zero = applications were stalled waiting for writeback
       
       cat /proc/meminfo | grep Dirty
       # Dirty: 524288 kB = 512MB of pending writes
       # If this approaches vm.dirty_ratio * RAM: stall imminent
       
  Control:
    sysctl vm.dirty_ratio=10         # Stall threshold (lower = safer)
    sysctl vm.dirty_background_ratio=5  # Background flush trigger
    sysctl vm.dirty_expire_centisecs=3000  # 30s max dirty age
    sysctl vm.dirty_writeback_centisecs=500  # Flush interval: 5s
    
  For databases (must control durability):
    Use O_DIRECT or O_SYNC: bypass dirty page buffering
    PostgreSQL: uses O_DIRECT for data files (WAL still buffered)
    MySQL InnoDB: innodb_flush_method=O_DIRECT
```

---

### LRU and Page Eviction

```
Page cache grows until all free RAM is consumed.
Eviction needed when: memory pressure (processes need more RAM).
  
  Linux LRU-2 lists:
    - Active list: recently accessed pages
    - Inactive list: less recently accessed pages (eviction candidates)
    
  Page promotion/demotion:
    New page: added to inactive list
    Accessed again: promoted to active list (PG_referenced flag)
    Not accessed for a while: demoted from active to inactive
    Memory pressure: inactive pages evicted (reclaimed)
    
  File pages vs anonymous pages:
    File pages (page cache): can be evicted and re-read from disk
    Anonymous pages (heap, stack): can be swapped (if swap enabled)
    Preference: file pages evicted first (they can be reloaded free)
    
  Huge pages and page cache:
    Huge pages (2MB): generally NOT used for page cache in Linux
    Exception: tmpfs, some special cases
    Page cache: uses 4KB pages only (base page size)
    
  Cache pressure tuning:
    vm.swappiness = 60 (default):
      60: balanced swapping of anonymous pages vs file cache eviction
      0: strongly prefer evicting file cache over swapping
      100: aggressively swap anonymous pages
    
    For database servers:
      vm.swappiness = 1 or 0:
        Never swap (database manages its own cache)
        File cache: MySQL/Postgres use O_DIRECT; no benefit from cache
        
    For general servers with page cache benefit:
      vm.swappiness = 10:
        Prefer keeping file cache; minimal swapping
```

---

### mmap and Page Cache Sharing

```
mmap(fd, offset, length, PROT_READ, MAP_SHARED):
  - Maps file region directly into virtual address space
  - Pages: backed by page cache (not separate allocation)
  - Access: directly reads/writes page cache pages
  - No copy between kernel and user space
  
mmap vs read() comparison:
  read(fd, buf, n):
    1. page cache lookup
    2. copy: page cache -> user buffer (extra copy)
    3. return to application
    Total: kernel copy + user-space access
    
  mmap + pointer access:
    1. virtual address -> page cache page (TLB lookup)
    2. Direct access (no copy)
    Total: TLB lookup + direct access
    For large files read repeatedly: mmap is faster
    
Multiple processes, same file:
  Process A: mmap(file, ...)
  Process B: mmap(file, ...)
  Result: A and B share the SAME physical page cache pages
  Memory: only one copy in RAM regardless of number of mappings
  This is why shared libraries (.so files) are memory-efficient:
    1000 processes using libc: still just ONE copy in page cache
    
Kafka and page cache:
  Producer writes: to page cache (sequential, cheap)
  Consumer reads: from page cache (if lag is low, same pages)
  Kafka's "zero-copy" consumer path:
    1. Consumer requests file segment
    2. Kafka calls sendfile(socket_fd, file_fd, offset, size)
    3. Kernel: DMA from page cache directly to NIC buffer
    4. No copy to user space; no copy to kernel socket buffer
    Result: producer writes and consumer reads share page cache;
      no additional memory needed for consumer if keeping up with producer
      
madvise and page cache hints:
  madvise(addr, len, MADV_SEQUENTIAL):
    Hint: will read sequentially; increase read-ahead
  madvise(addr, len, MADV_RANDOM):
    Hint: random access; disable read-ahead
  madvise(addr, len, MADV_DONTNEED):
    Hint: no longer needed; kernel may evict immediately
  madvise(addr, len, MADV_WILLNEED):
    Hint: will need soon; pre-fault pages (async prefetch)
```

---

### Production Tuning Scenarios

```
Scenario 1: Write Stalls During Peak Traffic
  
  Symptom: Application write latency spikes 10x for 1-2 seconds
  Cause: dirty pages hit vm.dirty_ratio; all writes throttled
  
  Diagnosis:
    cat /proc/vmstat | grep dirty_throttle_count
    watch -n1 'cat /proc/meminfo | grep Dirty'
    
  Fix:
    # Lower dirty thresholds (flush earlier, smaller dirty window)
    sysctl -w vm.dirty_ratio=5
    sysctl -w vm.dirty_background_ratio=2
    
    # If problem is log writing (lots of appends):
    # Use a separate mount with different scheduler/settings
    # Or: use O_DSYNC for critical log writes (Kafka WAL)
    
Scenario 2: OOM Kill Despite Free RAM in top
  
  Symptom: top shows 2GB free; but OOM killer fires
  Cause: "free" in top = truly free + reclaimable (includes cache)
  Page cache consuming 10GB: looks "free" to top but is in use
  When process needs 3GB: page cache must be reclaimed
  If reclaim too slow or fails: OOM kill
  
  Diagnosis:
    free -m  # Shows: Mem: used, free, shared, buff/cache, available
    "available" is the correct metric (includes reclaimable cache)
    cat /proc/meminfo | grep MemAvailable
    
  Fix:
    Alert on MemAvailable < 20% of total RAM
    Drop caches manually (testing only, never production):
      echo 1 > /proc/sys/vm/drop_caches  # drop page cache
      echo 2 > /proc/sys/vm/drop_caches  # drop dentries/inodes
      echo 3 > /proc/sys/vm/drop_caches  # drop all caches
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Free memory shown by top is available for applications" | `top`'s 'free' column shows truly free pages. But page cache (shown as 'buff/cache') is reclaimable - the kernel will evict it when applications need memory. The correct metric is 'available' from `free -m` or `/proc/meminfo MemAvailable`. |
| "write() with large buffers prevents data loss" | write() writes to page cache only. Data loss is possible until fsync() completes or the kernel flushes dirty pages. For durability guarantees: always fsync() critical data. For databases: use WAL with controlled fsync frequency. |
| "page cache always helps performance" | For databases using O_DIRECT (own buffer pool), page cache adds an extra layer of copying without benefit. A database reading a page: kernel reads to page cache, then copies to database buffer pool. Using O_DIRECT: reads go directly to database buffer pool. |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| Write stall | App writes block for seconds | `/proc/vmstat dirty_throttle_count` > 0 | Lower `vm.dirty_ratio` |
| OOM despite cache | OOM kill while `free` shows GB free | `free -m`: available < 10% | Alert on MemAvailable; tune swappiness |
| Page cache pressure on database | Database slower than expected | `iostat`: high reads despite warm cache | Use O_DIRECT; increase database buffer pool |
| Dirty page flush spikes | I/O spike every dirty_writeback_centisecs | `iostat -x`: periodic utilization spikes | Tune `dirty_background_ratio`, `dirty_expire_centisecs` |

---

### Quick Reference Card

| Concept | Detail |
|---------|--------|
| Dirty page trigger (background) | `vm.dirty_background_ratio` = 10% |
| Dirty page stall threshold | `vm.dirty_ratio` = 20% |
| View dirty memory | `cat /proc/meminfo \| grep Dirty` |
| Stall detection | `cat /proc/vmstat \| grep dirty_throttle_count` |
| True free memory | `MemAvailable` in `/proc/meminfo` |
| Drop page cache (test only) | `echo 3 > /proc/sys/vm/drop_caches` |
| mmap vs read | mmap: no copy; both share page cache |
| Kafka zero-copy | sendfile: page cache -> NIC DMA directly |
| Database recommendation | O_DIRECT + own buffer pool |
