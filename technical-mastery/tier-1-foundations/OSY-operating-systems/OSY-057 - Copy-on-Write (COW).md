---
id: OSY-057
title: Copy-on-Write (COW)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-031, OSY-054
used_by: OSY-058, OSY-089
related: OSY-054, OSY-055, OSY-072
tags:
  - copy-on-write
  - COW
  - fork
  - memory-optimization
  - ZFS
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/osy/copy-on-write/
---

## TL;DR

Copy-on-Write (COW) defers page copying until the first
write. Shared pages are mapped read-only; the first write
triggers a fault, copies the page, then allows the write.
Used by fork(), Linux page cache, ZFS/Btrfs, and Docker
overlay2 layers. Makes fork() cheap even for multi-GB
processes.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-057 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | copy-on-write, fork, page fault, ZFS, Docker layers |
| **Prerequisites** | OSY-031, OSY-054 |

---

### COW Mechanism at the Page Level

```
Initial state: parent process, 3 pages in heap
  VPN A -> PFN 100 (data: "hello")  [writable]
  VPN B -> PFN 101 (data: "world")  [writable]
  VPN C -> PFN 102 (data: "!")      [writable]

fork() called:
  1. Create child process struct (PCB, etc.)
  2. Copy parent's page table to child
  3. Mark ALL pages in BOTH tables READ-ONLY
  
  Parent:  VPN A -> PFN 100 [READ-ONLY, COW flag set]
  Child:   VPN A -> PFN 100 [READ-ONLY, COW flag set]
  (Same physical frame 100 shared by both!)

Parent writes to VPN A ("hello" -> "modified"):
  MMU: PTE is read-only -> hardware protection fault
  Kernel page fault handler:
    Is this a COW page? YES (COW flag in PTE)
    Allocate new frame: PFN 200
    Copy content: PFN 100 -> PFN 200 ("hello" -> "hello")
    Update parent PTE: VPN A -> PFN 200 [WRITABLE]
    Resume parent -> write "modified" to PFN 200
    
  Child still:  VPN A -> PFN 100 [READ-ONLY, COW flag]
  Parent now:   VPN A -> PFN 200 [WRITABLE, modified data]

Child writes to VPN B:
  Same process:
    COW fault on VPN B
    New frame PFN 201 for child
    Copy PFN 101 -> PFN 201
    Child VPN B -> PFN 201 [WRITABLE]

Pages never modified by either:
  VPN C -> PFN 102 still shared! Zero memory overhead.
```

---

### Applications of COW in the Linux Kernel

```
1. fork() - Process Creation (most common use)
   - Zero cost: 4GB process forks in ~1ms
   - Shells use fork+exec: exec() discards all COW pages anyway
   - No-exec pattern (Redis BGSAVE): parent serves requests,
     child serializes data via COW pages
     -> Child sees consistent snapshot (no lock needed)

2. Linux page cache - file page sharing
   - 10 processes exec() the same /usr/bin/java
   - Code pages: mapped READ-ONLY MAP_PRIVATE in each process
   - COW: if any process writes to code page -> private copy
   - All 10 share the same physical pages for code = saves RAM
   
3. mmap(MAP_PRIVATE) - file-backed COW
   - Pages loaded from file: shared with file's page cache
   - Write to MAP_PRIVATE page -> COW: private copy not visible
     in file and not visible to other MAP_PRIVATE mappings

4. KSM (Kernel Same-page Merging) - VM density optimization
   - Scans anonymous pages, finds identical content
   - Merges them: both VMAs point to one shared page (COW)
   - Used by hypervisors: 10 VMs running same OS -> share pages
   - Enabled: echo 1 > /sys/kernel/mm/ksm/run
```

---

### COW in Storage and File Systems

```
ZFS COW (file system level):
  Write: never overwrites existing data in place
    1. Allocate new blocks for modified data
    2. Write new data to new blocks
    3. Update metadata (block pointers) atomically
    4. Old blocks kept until no longer referenced
  
  Benefits:
    Atomic writes: power failure -> old version intact
    Snapshots: free - just keep reference to old block pointers
    Clone: COW clone of dataset (share blocks until modified)
    
  Key difference from OS page COW:
    OS COW: copies RAM pages on write
    ZFS COW: copies disk BLOCKS on write
    Same principle: copy lazily only on write

Btrfs COW (Linux native COW file system):
  Same principle as ZFS
  subvolumes + snapshots = COW clones
  
Docker overlay2 COW layers:
  Image layer: read-only (base Ubuntu, etc.)
  Container layer: read-write (COW on top)
  File modification in container:
    1. Copy file from image layer to container layer (copy-up)
    2. Modify copy in container layer
    3. Original in image layer unchanged
  Container exit -> discard container layer (original intact)
  
  This is WHY Docker images are efficient:
    10 containers running same base image:
    All share read-only image layers
    Only differences (writes) in per-container COW layers
```

---

### Redis BGSAVE: COW in Production

```
Redis BGSAVE process (creates RDB snapshot):
  
  Redis main process: serving client requests (writing)
  
  BGSAVE:
    1. fork() -> child process (~1ms, COW copy of page table)
    2. Child: serialize ALL data to disk (reading shared pages)
    3. Parent: continues serving writes (COW on written pages)
    
  Memory during BGSAVE:
    Quiet period: minimal extra memory (few pages dirtied)
    Write-heavy period: many pages COW'd -> memory spikes
    
  Worst case: Redis uses 2x normal memory during BGSAVE
    If Redis uses 10GB RAM:
    During heavy-write BGSAVE: up to 20GB total
    -> If OOM killer fires: Redis child killed -> RDB not saved
    
  Key fact: "save latency" = COW fault overhead
    Each client write during BGSAVE:
      If page not yet COW'd: pay COW fault cost (allocate + copy 4KB)
      This adds ~microseconds latency per modified page
    Visible as: latency spikes during BGSAVE in redis-cli --latency

  Configuration implication:
    vm.overcommit_memory = 1 required for Redis fork()
    Without it: fork() may fail if RSS > 50% of RAM
    (kernel checks if committing RSS * 2 would exceed RAM)
```

---

### Failure Modes and Diagnosis

```
1. OOM during fork() (Redis/memcached pattern)
Symptom: Cannot fork: Cannot allocate memory
Diagnosis:
  cat /proc/sys/vm/overcommit_memory
  # 0 = heuristic (may deny fork for large processes)
  # 1 = always allow (Redis requirement)
  free -m  (check available memory)
Fix:
  sysctl vm.overcommit_memory=1   (allow overcommit)
  
2. COW memory spike (Redis copy-on-write amplification)
Symptom: RSS doubles during BGSAVE, OOM kills child
Diagnosis:
  watch -n 1 "cat /proc/$(pgrep redis)/status | grep VmRSS"
  Check redis log for 'Fork Cost: XXX ms'
  Large fork cost = large page table to copy
Fix:
  Enable transparent huge pages OFF for Redis:
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
  Reason: 2MB huge pages = one COW per 2MB page (vs 4KB)
    -> each write in a 2MB page COWs the ENTIRE 2MB
    -> much more data copied than necessary

3. Dirty COW vulnerability (CVE-2016-5195)
Symptom: Privilege escalation via race in COW handler
Mechanism:
  Race condition in write + madvise(MADV_DONTNEED):
  Could write to read-only mmap'd pages (e.g., SUID binaries)
Patch: kernel 4.8.3+
Lesson: COW is in the kernel; race conditions in kernel = exploitable
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "COW means data is immediately duplicated on fork()" | COW means NO data is copied at fork() time. Only the page TABLE is copied (kilobytes). Pages are copied individually, lazily, only when the parent or child first writes to each page. If neither writes a page, it is NEVER copied |
| "Docker uses more memory because each container has a copy of the image" | Docker's overlay2 filesystem uses COW. All containers sharing an image share the same read-only image layers in memory. Only files actually modified by the container exist in that container's writable layer. 10 containers running the same base OS image don't use 10x the memory for the shared layers |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| COW trigger | First write to read-only shared page -> page fault -> copy |
| fork() cost | O(page_table_size) not O(heap_size). 4GB heap = ~1ms fork |
| Redis BGSAVE | fork() for snapshot; COW means reads see old data consistently |
| ZFS/Btrfs COW | Never overwrite in-place; copies blocks on write (atomic) |
| Docker overlay2 | Image layers: read-only shared; container layer: COW per write |
| THP + COW | Bad for Redis: huge pages COW entire 2MB per write; keep THP off |
