---
id: LNX-074
title: "Linux Memory Subsystem (page cache, NUMA, huge pages)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-062, LNX-022
used_by: LNX-075, LNX-083, LNX-094
related: LNX-062, LNX-075, LNX-083, LNX-088
tags: [page-cache, NUMA, huge-pages, virtual-memory, mmap, buddy-allocator, slab, page-fault, swap, memory-zones]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/lnx/linux-memory-subsystem/
---

## TL;DR

Linux memory = physical RAM managed by the kernel as 4 KB **pages**.
**Page cache**: kernel caches all file I/O in RAM (clean=reclaimable, dirty=
pending write). `free -h` "buff/cache" = this cache; it's NOT wasted memory.
**Virtual memory**: each process sees 0-128TB virtual address space; kernel
maps virtual pages to physical pages via page tables + MMU. **Page fault**:
virtual address not mapped -> kernel loads the page (slow path). **NUMA**:
multi-socket servers have per-socket memory; cross-NUMA access is 2-4x slower.
**Huge pages**: 2 MB instead of 4 KB, reducing TLB pressure. Key tools:
`free -h`, `vmstat -s`, `/proc/meminfo`, `numastat`, `getconf PAGESIZE`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-074 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | page cache, NUMA, huge pages, virtual memory, mmap, slab, page fault, swap, memory zones |
| **Prerequisites** | LNX-062 (Memory concepts), LNX-022 (Process management) |

---

### The Problem This Solves

**Problem 1**: A DBA reports that a database server with 64 GB RAM shows
only 8 GB "free" in `free -h`. They want to add more RAM. Understanding the
page cache: the 56 GB "used" is mostly the database's data files cached in
RAM for fast reads - this is CORRECT behavior, not wasted memory. When other
processes need RAM, the kernel reclaims page cache. The database gets faster
because reads from page cache are ~100x faster than disk reads.

**Problem 2**: A high-performance application running on a 2-socket server
(NUMA system) has unpredictable latency spikes. `numastat` shows frequent
"remote NUMA hits" - the application's memory is allocated on the wrong socket,
causing 2x longer memory access latency. Pinning the application to CPUs and
memory on the same NUMA node (using `numactl --cpunodebind=0 --membind=0`)
reduces latency and eliminates the spikes.

---

### Textbook Definition

**Linux memory subsystem**: The collection of kernel subsystems that manage
physical RAM: allocation, caching, swapping, and providing virtual address
spaces to processes.

**Key abstractions:**
- **Page**: 4 KB unit of memory management (4096 bytes, `getconf PAGESIZE`)
- **Page frame**: a physical page of RAM identified by PFN (Page Frame Number)
- **Virtual address space**: per-process 0-128 TB virtual space (64-bit)
- **Page table**: kernel data structure mapping virtual -> physical addresses
- **MMU**: Memory Management Unit - CPU hardware that performs address translation

**Major components:**
- **Page allocator (buddy system)**: allocates physical pages, manages free lists
- **Slab allocator (SLUB)**: allocates kernel objects (cache-efficient, size-appropriate)
- **Page cache**: caches file data and metadata in RAM
- **Anonymous memory**: process heap/stack, not backed by files
- **Swap**: extends virtual memory to disk (slower)
- **NUMA**: Non-Uniform Memory Access - topology where memory access time depends on which socket the memory is on

---

### Understand It in 30 Seconds

```bash
# === Free memory: what the numbers actually mean ===
free -h
#              total        used        free      shared  buff/cache   available
# Mem:          62Gi        12Gi       2.5Gi       1.2Gi        47Gi        48Gi
#
# "free" = 2.5 GB: pages with no data at all
# "buff/cache" = 47 GB: PAGE CACHE (file data, buffers)
#   -> this is NOT wasted! It's cached data, reclaimable
# "available" = 48 GB: what can be given to a new process
#   = free + reclaimable page cache
# RULE: "available" is what matters, not "free"
# A server with 2 GB "free" but 48 GB "available" is healthy!

# === /proc/meminfo: detailed breakdown ===
cat /proc/meminfo
# MemTotal:       65536000 kB   <- physical RAM
# MemFree:        2621440 kB    <- truly unused
# MemAvailable:   50331648 kB   <- available for new allocations
# Buffers:        2097152 kB    <- block device buffers
# Cached:         46137344 kB   <- file data cached (page cache)
# SwapCached:     0 kB          <- data in both RAM and swap
# Active:         16777216 kB   <- recently used pages
# Inactive:       30408704 kB   <- LRU candidate for reclaim
# Dirty:          2097152 kB    <- modified pages not yet written to disk
# Writeback:      0 kB          <- pages being written to disk now
# HugePages_Total: 0            <- 2MB huge pages configured
# HugePages_Free:  0
# HugePages_Rsvd:  0

# === Page cache: force flush ===
# Write dirty pages to disk:
sync

# Drop page cache (ONLY for testing, hurts performance):
echo 3 > /proc/sys/vm/drop_caches
# 1 = page cache, 2 = dentries/inodes, 3 = all

# === vmstat: memory activity ===
vmstat -s | head -20
vmstat 1 5   # 5 updates, 1 second apart
# procs -----memory------- ---swap-- -----io---- -system-- ------cpu-----
#  r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy
#  0  0      0 2621440 2097152 46137344  0    0    50   100  500  1000  5  3

# si/so: swap in/swap out (non-zero = memory pressure!)
# bi/bo: block in/out (bi high = reading from disk, usually page cache miss)

# === NUMA: check system topology ===
numactl --hardware
# available: 2 nodes (0-1)
# node 0 cpus: 0-15   node 0 size: 32768 MB
# node 1 cpus: 16-31  node 1 size: 32768 MB
# node distances:
# node  0  1
#   0:  10  20   <- local = 10, remote = 20 (2x slower!)
#   1:  20  10

# Check NUMA memory usage:
numastat
# numa_hit: memory allocated on preferred node (good!)
# numa_miss: memory allocated on non-preferred node (bad!)
# interleave_hit: from interleaved policy

# Run process on specific NUMA node:
numactl --cpunodebind=0 --membind=0 myprocess   # CPU+mem on node 0

# === Huge pages: check status ===
grep -i huge /proc/meminfo
# HugePages_Total: 0    <- 0 static huge pages configured
# Hugepagesize:   2048 kB   <- 2 MB per huge page

# Check THP (Transparent Huge Pages):
cat /sys/kernel/mm/transparent_hugepage/enabled
# [always] madvise never   <- THP is "always" enabled

# === Virtual memory maps for a process ===
cat /proc/self/maps | head -20
# 7f8a12345000-7f8a12346000 r-xp  <- virtual address range
# Permissions: r=read, w=write, x=execute, p=private, s=shared
# Maps: text, data, heap, stack, shared libraries, mmap regions
```

---

### First Principles

**Virtual address translation:**
```
Process accesses virtual address: 0x7ffe12345678

CPU's MMU translates to physical address:
  Virtual: [PGD|PUD|PMD|PTE|offset]
           (page global dir | upper | mid | table | 4KB offset)

  Page table walk:
  1. CR3 register -> Physical addr of PGD (per-process page table base)
  2. PGD[virtual bits 47:39] -> PUD page
  3. PUD[virtual bits 38:30] -> PMD page
  4. PMD[virtual bits 29:21] -> PTE page
  5. PTE[virtual bits 20:12] -> physical page frame
  6. + offset bits 11:0      -> physical address within page

TLB (Translation Lookaside Buffer):
  Hardware cache of recent virtual->physical translations
  TLB hit: translation in 1 cycle
  TLB miss: 4-level page table walk: 4 memory reads = ~200 cycles
  
  Huge pages (2 MB) = only 3-level walk for 2MB region
  TLB covers 512x more memory with same number of TLB entries
  => Key benefit for databases (large working sets)

Page fault types:
  Minor fault: page exists but not mapped (e.g., first access to mmap'd file)
    -> kernel just updates page table to point to existing page
    -> ~few hundred ns

  Major fault: page not in RAM (must read from disk)
    -> kernel allocates a page, reads from disk/swap
    -> milliseconds! (100,000x slower than a cache hit)
    -> causes measurable latency
    
  Check: /proc/[pid]/stat field 10 (minflt) and 11 (majflt)
         or: sar -B (system-wide page fault rate)
```

**Page cache and dirty page management:**
```
All file reads go through page cache:
  read(fd, buf, 4096)
  -> kernel checks: is page at file_offset in page cache?
  -> YES: copy from page cache to buf (100 ns, RAM speed)
  -> NO: allocate a page, read 4 KB from disk (1-10 ms), cache it
         next read of same data: from cache (100 ns)

Write path:
  write(fd, buf, 4096)
  -> copy from buf to page cache (page is now "dirty")
  -> return success IMMEDIATELY (write is buffered!)
  -> Kernel's write-back threads flush dirty pages later:
       pdflush/kworker writes dirty pages to disk in background
  -> Dirty page limits:
       vm.dirty_ratio (30%): if dirty > 30% RAM, processes block to write
       vm.dirty_background_ratio (10%): kernel starts background flush

This means:
  Sequential write performance looks GREAT (writing to cache, fast)
  But: on crash/power loss, dirty pages = data loss
  For durability: fsync() forces dirty pages to disk before returning
  Databases: use O_DIRECT or fsync() to ensure durability

Control dirty page behavior:
  cat /proc/sys/vm/dirty_ratio                # currently 30
  cat /proc/sys/vm/dirty_background_ratio     # currently 10
  cat /proc/sys/vm/dirty_expire_centisecs     # 3000 = 30 seconds max age
  
  Tune for write-heavy workloads:
    sysctl -w vm.dirty_ratio=60              # allow more dirty pages
    sysctl -w vm.dirty_background_ratio=5   # start flushing earlier
```

---

### Thought Experiment

Diagnosing a memory issue in production:

```bash
# Symptom: Java application OOM killed, but 'free -h' shows 40 GB "available"
# Diagnosis approach:

# Step 1: What actually caused the OOM?
dmesg | grep -i "oom\|killed" | tail -20
# Look for: "Out of memory: Kill process XXXX (java)"
# Note the cgroup path if present (container OOM vs system OOM)

# Step 2: Check Java heap vs physical memory:
# Was the container limited?
cat /sys/fs/cgroup/memory/docker/<id>/memory.limit_in_bytes
# Compare to Java -Xmx setting

# Step 3: Understand Java memory beyond heap:
# Java uses memory OUTSIDE the heap:
# - JVM code cache (Metaspace: ~256MB default)
# - Direct ByteBuffers (off-heap)
# - Thread stacks (~512KB per thread * 200 threads = 100MB)
# - GC overhead
# 
# With -Xmx8G: actual memory = 8G heap + ~2G overhead = ~10G
# Container limit 8G: -> OOM!

# Step 4: Process-level memory accounting:
# For each Java process:
cat /proc/<PID>/status | grep -E "VmRSS|VmSwap|VmPeak"
# VmRSS:   10234567 kB   <- resident (in RAM)
# VmSwap:        0 kB    <- in swap
# VmPeak:  12345678 kB   <- peak usage

# Breakdown by memory region:
smem -p | grep java    # proportional set size (accounting for shared)
cat /proc/<PID>/smaps | grep -E "^(Rss|Private|Shared)" | \
    awk '{sum[$1]+=$2} END {for(k in sum) print k, sum[k]/1024, "MB"}'
```

---

### Mental Model / Analogy

```
Linux memory subsystem = a library with a limited number of reading tables

Physical RAM = total reading table space in the library
Pages = individual tables (all same size: 4 KB)

Virtual memory = librarian's reservation system:
  Each visitor (process) gets a "virtual floor plan" showing
  their own private reading rooms (virtual addresses)
  Real tables (physical pages) are assigned on demand
  Two visitors can have different maps that point to the SAME
  physical table (shared pages, copy-on-write)

Page cache = frequently-used book shelf (kept at visitor tables):
  Popular books (frequently read files) stay at the tables
  If visitor A reads /var/log/syslog: library fetches from archive (disk)
  The book stays at a table (page cache)
  Visitor B reads same file: it's already at the table (100x faster!)
  
  The "buff/cache" in 'free' = books currently at tables
  "free" = empty tables with no books
  When a new visitor needs a table: library removes oldest book
  (LRU - least recently used reclaim)

Dirty pages = books with sticky notes (pending annotations):
  Modified pages = books with changes not yet filed back to archive
  sync/fsync = "please file these changes now"
  Machine crash = sticky notes lost (unflushed data lost)

NUMA = two-building library:
  Building A (socket 0): floors 1-10, own archive, own librarians
  Building B (socket 1): floors 11-20, own archive, own librarians
  Visitor on floor 5 (CPU core 5, socket 0):
    Fetching from Building A archive: 10 minutes (local)
    Fetching from Building B archive: 20 minutes (remote, cross-NUMA)
  
  numactl --membind=0: "only use Building A tables for my process"
  Ensures visitor always fetches from local archive (consistent fast access)

Huge pages = larger tables (2 MB instead of 4 KB):
  Same visitor, same books - but each "table" holds 512 books
  The librarian's table index (TLB) has limited slots
  With huge tables: each slot represents 512x more data
  Less index misses, less time finding the right table
  Key for databases: large working sets, constant TLB misses with 4 KB pages
```

---

### Gradual Depth - Five Levels

**Level 1:**
`free -h` output interpretation: "available" not "free". Page cache as
beneficial. `vmstat 1` for memory activity. `swap` usage as memory pressure
indicator. `/proc/meminfo` basic fields. Physical vs virtual memory concept.

**Level 2:**
Virtual address spaces, page tables, MMU. Page fault: minor vs major.
Dirty pages: write-back mechanism. `vm.dirty_ratio`/`vm.dirty_background_ratio`.
NUMA: `numastat`, `numactl`. HugePages static configuration. THP (transparent
huge pages): always/madvise/never.

**Level 3:**
Buddy allocator (free lists of 2^n pages). SLUB allocator for kernel objects.
`/proc/[pid]/smaps` for process memory breakdown. `smem` for proportional set
size. Memory zones: `ZONE_DMA`, `ZONE_NORMAL`, `ZONE_HIGHMEM`. LRU lists:
active/inactive (file, anonymous). Page reclaim: kswapd, direct reclaim.
`vm.swappiness` control. Memory compaction and defragmentation.

**Level 4:**
Memory overcommit: `vm.overcommit_memory` (0=heuristic, 1=always, 2=strict).
OOM killer: scoring (`/proc/[pid]/oom_score`, `oom_score_adj`). NUMA balancing:
kernel's automatic NUMA placement. `mbind()` and `set_mempolicy()` syscalls.
Memory hotplug. `perf mem` for memory access profiling. `/proc/zoneinfo` for
zone-level stats. Memory pressure notifications via cgroup memory.pressure.

**Level 5:**
Page table entry formats (64-bit): PFN bits, present bit, dirty bit, accessed
bit. Copy-on-write mechanics: fork() + page fault. KSM (Kernel Same-page
Merging) for identical pages in VMs. Memory-mapped I/O vs regular file I/O
trade-offs. NUMA + HPC workloads: first-touch policy, interleave policy.
Memory bandwidth saturation at scale. Page cache writeback storm prevention.
`vm.vfs_cache_pressure` for inode/dentry cache vs page cache balance.

---

### Code Example

**BAD - memory misunderstandings:**
```bash
# BAD 1: Treating "available" low memory as a crisis:
free -h
# Mem:  62Gi  59Gi  100Mi  1.2Gi  2.8Gi  50Gi
# Operator: "Only 100 MB free! Add more RAM urgently!"
# Reality: 50 GB AVAILABLE (reclaimable page cache)
# Correct read: system is healthy, cache is working as designed

# BAD 2: Dropping page cache in production:
echo 3 > /proc/sys/vm/drop_caches   # NEVER in production!
# Immediately frees 50 GB of page cache
# Next DB query: must re-read from disk
# Result: 10-100x slower reads for next 10-30 minutes while cache rebuilds
# Only use for: performance testing (reset to known state), never for "freeing memory"

# BAD 3: Running a memory-intensive app without NUMA awareness:
./big_java_app -Xmx64G &
# On a 2-socket server: memory may be allocated interleaved across sockets
# OR allocated entirely on socket 1 (far from CPUs on socket 0)
# Result: 2x memory latency for some/all memory accesses
# High p99 latency, unexplained performance variance

# GOOD 3: NUMA-aware application startup:
numastat -p $(pgrep big_java_app)  # check current NUMA balance
# If numa_miss is high: process is in wrong NUMA node

numactl --cpunodebind=0 --membind=0 \
    ./big_java_app -Xmx30G &
# Pin to socket 0 CPUs AND socket 0 memory (max 32 GB per node)
# All memory accesses are local (10 ns vs 20 ns cross-NUMA)
```

**GOOD - memory investigation sequence:**
```bash
# === Systematic memory investigation ===

# Step 1: High-level health check:
free -h
# Focus on "available" column - is it sufficient?

# Step 2: Activity (is memory under pressure?):
vmstat 1 5
# Watch: si/so (swap I/O = bad), free column trend

# Step 3: Detailed breakdown:
cat /proc/meminfo | grep -E "MemAvailable|Dirty|Writeback|SwapUsed|Shmem"

# Step 4: Process-level if process-specific issue:
# Sort by RSS (resident set = actual RAM):
ps aux --sort=-%mem | head -10
# or: top (M to sort by memory)

# Step 5: NUMA stats if multi-socket:
numastat  # check numa_miss vs numa_hit ratios
numastat -m  # per-NUMA zone stats

# Step 6: Detailed process breakdown (if needed):
smem -tk -p | sort -k5rn | head   # proportional set size, sorted

# Step 7: Page fault rate (is application reading data off-disk?):
sar -B 1 5   # pgpgin/s = pages read from disk (page cache miss)
# High pgpgin: insufficient RAM for working set (page cache thrashing)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Low 'free' memory means the system is running out of memory" | Linux's design philosophy: unused RAM is wasted RAM. The kernel uses all available RAM as page cache. `free` shows RAM with no data at all. `available` (from `free -h`) shows what can be given to new processes = free + reclaimable cache. A system showing 200 MB free but 40 GB available is healthy - the 40 GB of cache will be reclaimed on demand. Add RAM when `available` is consistently below your expected process needs, not when `free` is low. |
| "Swap usage always means the system is in trouble" | Non-zero swap usage doesn't indicate a problem. When the kernel has swapped out an anonymous page (heap/stack), it often stays in swap even after the process doesn't need it urgently - because swapping it back in costs an I/O. Inactive anonymous pages may sit in swap for hours without any performance impact. The concerning metrics are: `si`/`so` in `vmstat` (continuous swap I/O = swapping IN frequently = process keeps needing swapped-out pages = memory too small), or `available` dropping to near zero (kernel running out of reclaimable memory). |
| "NUMA only matters for HPC (high-performance computing) systems" | NUMA is relevant for ANY multi-socket server, which includes most production database hosts, large application servers, and cloud instances with >32 GB RAM. A 2-socket server with a Java application: if the JVM heap is allocated on the wrong socket, every GC cycle and every object access incurs 20-40 ns of extra latency (cross-NUMA penalty). At 100M operations/second: 40 ns * 100M = 4 seconds of extra latency per second = system at 100% overhead. Databases (PostgreSQL, MySQL) and in-memory caches (Redis) particularly benefit from NUMA pinning on multi-socket systems. Cloud instance note: AWS c5.18xlarge, m5.24xlarge are multi-socket; use `numactl --hardware` to check. |
| "Huge pages always improve performance" | Static huge pages (HugeTLB) can HURT performance if: (a) the working set is smaller than the huge page pool (waste of pre-allocated RAM), (b) the huge page pool is too large (reduces available memory for page cache), (c) the application allocates many small objects with sparse access patterns (internal fragmentation: 2 MB huge page for 8 KB of actually accessed data). THP (Transparent Huge Pages) has its own issues: THP compaction causes latency spikes when the kernel tries to merge 4 KB pages into 2 MB pages (common in databases - often recommended: `THP=madvise` or `THP=never` for Redis, MongoDB). Huge pages clearly help: databases with large working sets, in-memory data grids (Elasticsearch, Cassandra), scientific computing with large arrays. |

---

### Failure Modes & Diagnosis

**OOM diagnosis:**
```bash
# Symptom: Process killed, "Killed" in logs, no error message

# Step 1: Was it OOM killed?
dmesg | grep -E "oom|Out of memory|Kill" | tail -20
# Look for: "Out of memory: Kill process <PID> (<name>) score <N>"

# Step 2: What was the memory state at OOM time?
dmesg | grep -A10 "Mem-Info" | tail -20
# Shows: free pages, page cache, per-zone breakdown at OOM time

# Step 3: What was the OOM score?
# oom_score = 0-1000 (higher = more likely to be killed)
# Adjust for your critical processes:
echo -500 > /proc/<critical_pid>/oom_score_adj  # protect critical process
echo 1000 > /proc/<expendable_pid>/oom_score_adj   # kill this first

# Step 4: Was it a cgroup OOM or system OOM?
# System OOM: dmesg shows process killed
# Cgroup OOM: check cat /sys/fs/cgroup/<path>/memory.events
#   oom: N (N OOM events)

# Symptom: Writes complete fast then suddenly block (dirty page storm)
# Diagnosis:
cat /proc/meminfo | grep Dirty
# Dirty: 15000000 kB   (15 GB dirty pages - approaching vm.dirty_ratio)
# Write-back threads can't keep up -> processes block on write()

# Check dirty ratio:
cat /proc/sys/vm/dirty_ratio           # 30% of RAM = 18 GB threshold
cat /proc/sys/vm/dirty_background_ratio  # 10% = 6 GB (start background flush)

# Tune:
sysctl -w vm.dirty_background_ratio=5   # start flushing earlier
sysctl -w vm.dirty_expire_centisecs=1000   # flush dirty pages within 10 sec
```

---

### Related Keywords

**Foundational:**
LNX-062 (Memory concepts), LNX-022 (Process management)

**Builds on this:**
LNX-075 (Transparent Huge Pages), LNX-083 (OOM Killer), LNX-094 (Memory pressure diagnosis)

**Related:**
LNX-088 (Disk I/O performance), LNX-076 (I/O Schedulers)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `free -h` | Memory overview (use "available" column) |
| `vmstat -s` | Memory counters summary |
| `vmstat 1` | Live memory activity (si/so = swap I/O) |
| `cat /proc/meminfo` | Detailed memory breakdown |
| `numactl --hardware` | NUMA topology |
| `numastat` | NUMA hit/miss counters |
| `numactl --cpunodebind=0 --membind=0 cmd` | Run command on NUMA node 0 |
| `smem -tk -p` | Process memory sorted by proportional size |
| `cat /proc/PID/status \| grep VmRSS` | Process resident size |

**3 things to remember:**
1. "buff/cache" in `free` is PAGE CACHE (beneficial! reclaimable) - use "available" column, not "free"
2. NUMA: multi-socket servers have 2x+ remote memory penalty - check `numastat` for `numa_miss`
3. `vm.dirty_ratio` controls when processes BLOCK on write (dirty page storm) - tune for write-heavy workloads

---

### Transferable Wisdom

Linux page cache concepts appear in: JVM's buffer pool for NIO (Direct
ByteBuffers): same idea - keep file data in RAM, avoid copy. Database buffer
pools (InnoDB buffer pool, PostgreSQL shared_buffers): do the same job as the
page cache, but in userspace and database-aware. The kernel's page cache insight -
"all unused RAM should cache recent I/O" - is the same principle as Redis as
a caching layer: cache frequently-read data in RAM to avoid slow disk reads.
NUMA awareness appears in: Java NUMA-aware allocators (`-XX:+UseNUMA`), DPDK's
per-socket memory pools, Kubernetes topology manager (NUMA-aware pod scheduling).
The TLB pressure concept (why huge pages help) explains why JVM uses large
initial heap sizes: a single 8 GB JVM heap with 4 KB pages requires 2M TLB
entries to fully map - impossible (TLB has ~1500 entries). With 2 MB huge
pages: only 4000 entries needed. Platform engineers: understanding dirty page
management explains write buffering behavior in containers and why `fsync()`-heavy
workloads (databases) benefit from `vm.dirty_ratio` tuning.

---

### The Surprising Truth

Linux's memory management makes a design choice that surprises most new system
administrators: writing to a file ALWAYS succeeds quickly, regardless of disk
speed. This is because writes go to the page cache (RAM) and return success
immediately - the kernel writes to disk asynchronously. The system looks faster
than it is. The risk: on power loss, unwritten dirty pages are lost. The
guarantee: `fsync()` forces dirty pages to disk and doesn't return until they're
physically stored. Database durability (ACID's Durability) depends entirely on
applications calling `fsync()` at the right points. The practical consequence:
`dd if=/dev/zero of=/file bs=1M count=10000` completes at RAM speed (5 GB/s)
even on a 100 MB/s disk - until the page cache fills and the kernel must throttle
writes. The `write-behind` design means: filesystem benchmarks that don't sync
are measuring RAM speed, not disk speed. Production impact: any system where
writes SEEM fast that then crashes loses all dirty data. Replicated storage
(RAID, databases with WAL) exists precisely because dirty page buffering
makes durability a separate concern from write performance.

---

### Mastery Checklist

- [ ] Can correctly interpret `free -h` output (especially "available" vs "free" vs "buff/cache")
- [ ] Understands the page cache as beneficial, not wasted RAM
- [ ] Knows when dirty page accumulation becomes a problem and how to tune it
- [ ] Can diagnose NUMA-related performance issues with `numastat` and apply `numactl`
- [ ] Understands why major page faults cause application latency spikes

---

### Think About This

1. A PostgreSQL database server has 128 GB RAM and `shared_buffers=8GB` (its
   own buffer pool). After 1 hour of operation, `free -h` shows: Total=128G,
   Used=120G, Free=1G, Buff/Cache=110G, Available=112G. A DBA wants to increase
   `shared_buffers` to 64G to improve database performance. Using your knowledge
   of the Linux page cache, explain: (a) is the current memory state a problem?
   (b) does PostgreSQL actually benefit from a larger `shared_buffers` given the
   page cache is already caching its data files? (c) what are the trade-offs?

2. A high-frequency trading application on a 2-socket server needs sub-microsecond
   memory access latency. Design the optimal NUMA configuration: which `numactl`
   options would you use, what's the maximum working set size that fits in one
   NUMA node (assume 32 GB per socket), and how would you configure huge pages
   to minimize TLB misses? Show the specific commands.

3. A write-heavy application is experiencing latency spikes every 30 seconds,
   lasting about 5 seconds each. `vmstat` during spikes shows: `bo` jumps from
   0 to 50,000 (50,000 blocks/sec written to disk). Explain the root cause using
   dirty page management (the `vm.dirty_ratio`, `vm.dirty_background_ratio`,
   `vm.dirty_expire_centisecs` interaction), and provide specific `sysctl` tuning
   to smooth out the spike pattern.

---

### Interview Deep-Dive

**Foundational:**
Q: What does "buff/cache" mean in the output of `free`, and why is it NOT a memory problem?
A: `free`'s output has three memory categories: "used" (actively used by applications), "free" (completely unused, not mapped), and "buff/cache" (used as buffers and page cache). "buff/cache" is memory used by the kernel to cache file data. Whenever a process reads a file, the kernel reads it from disk into RAM (page cache), then provides it to the process. If the same file is read again, it comes from RAM - ~100x faster than disk. "Dirty" pages are modified data not yet written to disk. The key insight: this cache is completely RECLAIMABLE. When a new application needs memory, the kernel evicts the least recently used cache pages. The decision rule: Linux uses ALL unused RAM as cache because unused RAM provides zero value, while cached RAM provides I/O acceleration. The "available" column (not shown in older `free` versions, but in `free -h` on modern systems) is the meaningful number: it's free + reclaimable cache = what a new process can actually use. A server with 64 GB RAM, 1 GB "free", and 60 GB "buff/cache" has 61 GB "available" - it's healthy, not memory-starved. It's a problem when "available" drops to near zero AND swap usage is increasing (kernel has no more pages to reclaim and is using disk swap). The `vm.vfs_cache_pressure` sysctl controls how aggressively the kernel reclaims inode/dentry cache vs page cache; default 100 = balanced.

**Expert:**
Q: Explain how NUMA affects application performance and how you would diagnose and fix NUMA-related latency issues.
A: NUMA (Non-Uniform Memory Access) is a server architecture where physical RAM is distributed across multiple memory controllers, each associated with a CPU socket. Access time depends on which socket holds the memory: local (same socket) is fast (~10 ns), remote (other socket, cross-interconnect) is 1.5-3x slower (~20-30 ns). WHY IT MATTERS: at modern CPU speeds, this latency difference is significant. A cache miss that hits local NUMA memory costs ~10 ns; the same miss crossing NUMA nodes costs 20-30 ns. For workloads with many cache misses (large working sets, pointer-chasing): this 2-3x latency penalty accumulates. Example: an in-memory database (Redis, Memcached) on a 2-socket server that allocated its memory across both NUMA nodes: every other hash lookup crosses NUMA = systematic 20 ns overhead per lookup, visible as 2x worse p99 latency. DIAGNOSIS: `numactl --hardware` - shows the NUMA topology (nodes, CPUs per node, distances). `numastat` - shows numa_hit (local allocation), numa_miss (remote allocation). High numa_miss ratio = NUMA imbalance. `numastat -p <pid>` - per-process NUMA stats. `/proc/<pid>/numa_maps` - detailed memory allocation per NUMA node. `perf stat -e cache-misses,cache-references,LLC-load-misses` - LLC (Last Level Cache) misses indicate large working sets requiring NUMA-distance memory. FIX: `numactl --cpunodebind=0 --membind=0` - run process with CPU and memory on node 0 (all local, zero cross-NUMA). For workloads that exceed a single NUMA node: `--interleave=all` distributes memory round-robin across nodes (no node is "hot"). Java: `-XX:+UseNUMA` enables NUMA-aware allocation in the JVM heap. For kernel NUMA balancing (automatic migration): `/proc/sys/kernel/numa_balancing = 1` - kernel automatically migrates pages to the node where they're accessed most. Effective for most workloads but adds migration overhead. The production pattern: for latency-sensitive services (databases, caches), explicitly pin with `numactl` rather than relying on automatic balancing. For throughput-oriented services: automatic NUMA balancing usually suffices.
