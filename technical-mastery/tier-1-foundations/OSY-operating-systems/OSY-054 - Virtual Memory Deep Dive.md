---
id: OSY-054
title: Virtual Memory Deep Dive
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-012, OSY-031, OSY-033
used_by: OSY-055, OSY-089, OSY-091
related: OSY-055, OSY-056, OSY-089
tags:
  - virtual-memory
  - deep-dive
  - page-tables
  - TLB
  - address-translation
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/osy/virtual-memory-deep-dive/
---

## TL;DR

Virtual memory is a 4-level page table hierarchy on
x86-64 (PML4, PDPT, PD, PT), backed by the TLB for
caching translations. The kernel manages the page
allocator (buddy system) and address space regions
(VMAs). Understanding this explains: VIRT vs RSS,
fork() performance, mmap behavior, and JVM heap internals.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-054 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | virtual memory, page tables, TLB, buddy system, VMA |
| **Prerequisites** | OSY-012, OSY-031, OSY-033 |

---

### x86-64 4-Level Page Table Structure

```
Virtual address: 48 bits used (256TB total virtual space)
  [63..48] Sign extension (must be 0 for user, 1 for kernel)
  [47..39] PML4 index   (9 bits, 512 entries per table)
  [38..30] PDPT index   (9 bits, 512 entries per table)
  [29..21] PD index     (9 bits, 512 entries per table)
  [20..12] PT index     (9 bits, 512 entries per table)
  [11..0]  Page offset  (12 bits, 4096 bytes per page)

Page Table Walk (TLB miss):
  CR3 register -> physical addr of PML4 table
  PML4[index] -> physical addr of PDPT table
  PDPT[index] -> physical addr of PD table
  PD[index]   -> physical addr of PT table (or 2MB huge page PTE)
  PT[index]   -> physical addr of 4KB page frame
  
  Total: 4 memory reads -> physical address

TLB caches:
  Recent VPN -> PFN mappings
  L1 ITLB: ~64 entries (instruction)
  L1 DTLB: ~64 entries (data)
  L2 TLB:  ~1024-4096 entries
  Hit: 1-4 cycles; Miss: 50-100 cycles (4 memory reads)

PCID (Process Context Identifier):
  CR3 bits [11:0] = PCID (up to 4096 process IDs in TLB)
  Avoids full TLB flush on context switch between processes
  (Introduced with KPTI to reduce Spectre/Meltdown patch overhead)
```

---

### Kernel Virtual Memory Areas (VMAs)

```
Each process has a list of VMAs (virtual memory areas):
  /proc/PID/maps: one line per VMA

  7f8a00000000-7f8a20000000 rw-p 00000000 00:00 0    [heap]
  7f8b00000000-7f8b01000000 r-xp 00000000 08:01 1234 /lib/libc.so
  7fff12345000-7fff12366000 rw-p 00000000 00:00 0    [stack]
  
  Fields: start-end, permissions, offset, device, inode, name
  
  Permissions:
    r: readable, w: writable, x: executable, p: private (COW), s: shared
    
  VMA types:
    Anonymous (anon): heap, stack, malloc-ed memory
    File-backed: loaded from file (executables, libraries, mmap)
    Special: [vvar] (kernel data for vsyscalls), [vsyscall]
    
  mmap() creates a new VMA:
    Anonymous: mmap(NULL, size, PROT_RW, MAP_ANON|MAP_PRIVATE, -1, 0)
    File-backed: mmap(NULL, size, PROT_READ, MAP_SHARED, fd, 0)
```

---

### Physical Memory Allocation (Buddy System)

```
Linux physical page allocator: Buddy System
  Goal: allocate contiguous physical pages efficiently

Structure: free lists for powers-of-2 page counts
  Order 0: 1 page  (4KB)   [free_list[0]]
  Order 1: 2 pages (8KB)   [free_list[1]]
  Order 2: 4 pages (16KB)  [free_list[2]]
  ...
  Order 10: 1024 pages (4MB) [free_list[10]]

Allocation of N pages:
  Find smallest order >= log2(N)
  If not available: split larger block (split buddy)
  Example: need 1 page from empty order-2 list?
    -> Split one order-2 block into two order-1 blocks
    -> Split one order-1 block into two order-0 blocks
    -> Return one order-0 block

Deallocation (free):
  Return block to free list
  Check if "buddy" (adjacent same-size block) is also free
  If yes: merge into one larger block (coalesce)
  Repeat up until no more merges possible

Why buddy system?
  O(log2 N) allocation/deallocation (small, fixed overhead)
  Minimizes fragmentation (coalescing)
  Hardware page tables work in powers of 2

Java connection:
  JVM mmap()/brk() for heap uses buddy allocator internally
  Huge page allocation requires contiguous physical blocks
  -> Fragmented physical memory can prevent huge page alloc
  -> Allocate huge pages early: vm.nr_hugepages in /proc/sys
```

---

### VIRT vs RSS: What ps Shows

```
VIRT (Virtual Memory):
  Total virtual address space claimed by process
  Includes: code, heap, stack, mmap'd files, guard pages
  Can exceed physical RAM (OS overcommits by default)
  Includes pages not yet accessed (not in physical RAM)
  
RSS (Resident Set Size):
  Physical RAM currently occupied by this process
  Includes: anonymous pages, file pages in use
  Excludes: swapped-out pages, not-yet-accessed pages
  
Example: Java JVM with -Xms512m -Xmx4g
  ps output: VIRT=8192m  RSS=600m
  
  VIRT=8GB:
    Heap reservation (4GB virtual mapping even if unused)
    JVM code, libraries (~200MB)
    Metaspace, code cache (~500MB virtual)
    Thread stacks (200 threads * 1MB = 200MB virtual)
    Guard pages, mmap'd files
    
  RSS=600MB:
    Only pages that have been touched by the JVM
    Heap pages with actual objects
    Code cache for compiled methods
    Pages actively in use
    
  After Java heap fills to 4GB:
    RSS will approach 4GB (actual physical memory used)

  Check with: pmap -x PID | sort -k3 -rn | head -20
  Shows: largest RSS consumers by mapping
```

---

### Copy-on-Write (COW) Mechanics

```
fork() does NOT copy memory pages. It copies ONLY the page table.
  
Before fork():
  Parent: VPN1 -> PFN100, VPN2 -> PFN101, ... (many pages)
  
fork():
  1. Copy parent's page table to child (fast: only table pointers)
  2. Mark ALL pages in BOTH parent and child as read-only in PTE
  3. child.VPN1 -> PFN100 (same physical frame!)
  
First write to shared page (e.g., parent writes to VPN1):
  1. MMU: write to read-only page -> page fault (protection fault)
  2. Kernel: is this a COW page? YES
  3. Kernel: allocate new physical frame PFN200
  4. Copy content: PFN100 -> PFN200
  5. Update parent's PTE: VPN1 -> PFN200 (writable)
  6. Child's PTE still: VPN1 -> PFN100 (still read-only)
  7. Resume parent at faulting instruction
  
Result:
  Pages modified by either parent or child: private copy
  Pages NOT modified: still shared (zero extra memory!)
  
Fork performance:
  4GB JVM heap: fork takes ~1ms (copy page table only, not pages)
  NOT 4GB * memcpy = would take seconds
  COW means fork is O(page_table_size), not O(heap_size)
  
  But: after fork, if child modifies data:
  Each modified page: COW fault + frame allocation + copy
  If child writes all 4GB: uses 4GB extra physical memory
```

---

### mmap Deep Dive

```
mmap(addr, length, prot, flags, fd, offset):
  Creates VMA in process address space
  
Types:
  Anonymous private (heap/stack):
    mmap(NULL, 4096, PROT_RW, MAP_ANON|MAP_PRIVATE, -1, 0)
    Not backed by any file
    Pages zero-filled on first access (demand zero paging)
    
  File-backed shared (page cache):
    mmap(NULL, size, PROT_RD, MAP_SHARED, fd, 0)
    Backed by file in page cache
    Multiple processes map same file: same physical pages!
    Write to MAP_SHARED -> writes directly to page cache -> file
    Write to MAP_PRIVATE -> COW (doesn't affect file)
    
Java MappedByteBuffer:
  FileChannel.map(READ_ONLY, 0, fileSize)
    -> MAP_SHARED | MAP_PRIVATE (read-only)
    -> Zero-copy file reading: reads directly from page cache
    -> No JVM heap copy: data read directly into native memory
    -> GC cannot collect until explicitly unmap() (Java 14+)
    
munmap(addr, length):
  Release the VMA
  If file-backed: flush dirty pages to disk (async)
  If Java MappedByteBuffer: call MappedByteBuffer.force() before munmap
  
mmap performance advantage over read():
  read(): syscall -> kernel copies page cache -> JVM heap
  mmap(): no copy; access memory directly maps to page cache
  For large files: mmap is 2-3x faster
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "VIRT memory usage means the process is using that much RAM" | VIRT includes reserved virtual address space that has no physical backing. A JVM with -Xmx4g will show VIRT > 4GB even if heap is empty. RSS is the actual physical RAM in use |
| "fork() duplicates all memory, making it expensive for large processes" | fork() uses COW: only the page table is copied (fast, O(KB)). Physical pages are shared and copied lazily only when written. A 4GB JVM forks in ~1ms, not in seconds |
| "mmap is only useful for memory-mapped databases" | mmap is used for: program loading (ELF loading = mmap), shared library loading, Java NIO MappedByteBuffer, Redis AOF persistence, and log file rotation. Understanding mmap is essential for production Java debugging |

---

### Failure Modes and Diagnosis

```
1. TLB Thrashing
Symptom: Mysterious performance degradation, not CPU/IO bound
  Benchmark shows 2-3x slower than expected
Diagnosis:
  perf stat -e dTLB-load-misses,dTLB-stores -p PID -- sleep 60
  If dTLB-load-misses / total_stores > 5%: TLB pressure
Fix: Enable huge pages (-XX:+UseLargePages)
  For JVM heap: 4KB pages -> 2MB huge pages -> 512x fewer TLB entries

2. Virtual Memory Fragmentation
Symptom: mmap() fails with ENOMEM but free memory exists
Diagnosis:
  cat /proc/sys/vm/max_map_count  (default: 65536)
  cat /proc/PID/maps | wc -l     (actual VMA count)
  If VMA count near max_map_count: fragmentation
Fix: 
  sysctl -w vm.max_map_count=262144
  (Elasticsearch requires this: its JVM and mmapped segments
   can exceed default 65536 VMAs under heavy write load)

3. Huge Page Allocation Failure
Symptom: -XX:+UseLargePages fails silently, JVM falls back to 4KB
Diagnosis:
  cat /proc/sys/vm/nr_hugepages
  grep Huge /proc/meminfo
  # HugePages_Total: 0  <- not configured
Fix:
  echo 1000 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
  # Allocate at boot: hugepages=1000 in /etc/default/grub
  # Or: Transparent Huge Pages (THP): may cause GC latency spikes
```

---

### Related Keywords

**Builds on:** OSY-012 (Virtual Memory Concept),
OSY-031 (Paging and Page Tables), OSY-033 (Memory Layout)

**Leads to:** OSY-055 (Demand Paging), OSY-056 (mmap),
OSY-089 (Kernel Internals)

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| x86-64 page table levels | 4 (PML4, PDPT, PD, PT) |
| TLB miss cost | 4 memory reads, 50-100 cycles |
| fork() cost | Copies page TABLE only (~ms), not pages (COW) |
| VIRT vs RSS | VIRT = claimed, RSS = actually in RAM |
| max_map_count | Default 65536 VMAs per process (increase for Elasticsearch) |
| Huge page size | 2MB (512x fewer TLB entries vs 4KB) |
