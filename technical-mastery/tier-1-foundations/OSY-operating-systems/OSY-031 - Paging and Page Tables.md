---
id: OSY-031
title: Paging and Page Tables
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-012, OSY-013
used_by: OSY-032, OSY-054, OSY-055
related: OSY-032, OSY-054, OSY-055
tags:
  - paging
  - page-tables
  - virtual-memory
  - MMU
  - TLB
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/osy/paging-page-tables/
---

## TL;DR

Paging divides virtual and physical memory into fixed-
size pages (4KB). The page table maps virtual page
numbers to physical frame numbers. The MMU uses the
TLB to cache recent translations. A TLB miss triggers
a page table walk (50-100 CPU cycles). A page fault
(unmapped entry) triggers the kernel to allocate a
physical frame.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-031 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | paging, page tables, TLB, page fault, MMU |
| **Prerequisites** | OSY-012, OSY-013 |

---

### The Problem This Solves

Physical memory is fragmented. A 512MB process cannot
get a single contiguous 512MB block of physical RAM.
Paging solves this by breaking both virtual and physical
memory into fixed pages - a process's pages can scatter
across any available physical frames while appearing
contiguous to the program.

---

### Paging Mechanics

```
Virtual address structure (64-bit x86, 4KB pages):
  [47..39] PML4 index   (9 bits) -> level 4 page table
  [38..30] PDPT index   (9 bits) -> level 3 page table
  [29..21] PD index     (9 bits) -> level 2 page table
  [20..12] PT index     (9 bits) -> level 1 page table
  [11..0]  Page offset  (12 bits) -> byte within page
  
  4-level page table walk: 4 memory accesses to translate
  1 virtual address -> 1 physical address
  
Simplified address translation (32-bit, 2-level):
  Virtual address: [Page Number | Offset]
  
  MMU:
    1. Check TLB for page number
       HIT:  physical frame = TLB[page#]; cost = ~1 cycle
       MISS: walk page table (2 memory reads); cost = 50-100 cycles
    
    2. Physical address = frame_number * 4096 + offset
    3. If PTE.present = 0: PAGE FAULT (trap to kernel)
```

```
Page Table Entry (PTE) structure (simplified):
  [31..12] Physical frame number (20 bits)
  [11]     Reserved
  [10..9]  Available (OS use)
  [8]      Global (don't flush from TLB on context switch)
  [7]      Page Size (0=4KB, 1=2MB huge page)
  [6]      Dirty (modified since last disk sync)
  [5]      Accessed (read/written recently)
  [4]      Cache disable
  [3]      Write-through
  [2]      User/Supervisor (0=kernel only, 1=user accessible)
  [1]      Read/Write (0=read-only, 1=read-write)
  [0]      Present (1=in physical RAM, 0=not in RAM)
```

---

### TLB (Translation Lookaside Buffer)

```
TLB = associative cache for page table entries
  Structure: tag = virtual page number, data = physical frame
  Size: ~64-1024 entries (L1-ITLB, L1-DTLB, L2-TLB)
  Hit rate: ~99% for typical applications
  
Hit vs Miss cost:
  TLB hit:  ~1-4 cycles  (normal memory access time)
  TLB miss: ~50-100 cycles (4 memory reads for 4-level PT)
  
TLB flush cost:
  Context switch between different processes: full TLB flush
  (each process has own page tables = different mappings)
  ~100-1000 ns per flush + ~50-100 cycles per subsequent miss
  
  ASID (Address Space ID): modern CPUs tag TLB entries
  with ASID so different processes can coexist in TLB
  (reduces context switch overhead)
  
Huge pages and TLB:
  4KB page: 1GB / 4KB = 262,144 TLB entries needed
  2MB huge: 1GB / 2MB = 512 TLB entries needed
  -> 512x fewer TLB misses for large working sets
  -> Critical for JVM with large heaps (-XX:+UseHugePages)
```

---

### Page Fault Types and Handling

```
Type 1: Minor Page Fault (fast, no disk I/O)
  Cause: page in RAM but not in page table (COW, lazy alloc)
  Handler: update PTE to point to existing frame
  Cost: ~1-10 microseconds
  Example: fork() after copy-on-write, first write to shared page

Type 2: Major Page Fault (slow, disk I/O required)
  Cause: page was swapped to disk (swap area or mmap file)
  Handler: load page from disk into free frame, update PTE
  Cost: 1-10 milliseconds (SSD: ~100us, HDD: ~10ms)
  Example: memory-mapped file read, swapped-out JVM data
  
Type 3: Invalid Page Fault -> Segfault (SIGSEGV)
  Cause: access to address with no mapping at all
  Handler: send SIGSEGV signal to process -> crash (default)
  Example: null pointer dereference (address 0x0 is unmapped)
  
Java connection:
  JVM allocates heap via mmap() -> initial page faults
  -Xms512m: JVM reserves 512MB virtual but may not commit
  -Xmx2g: can grow up to 2GB via more page faults
  GC touching cold pages: major page faults if under memory pressure
```

---

### Code Example: Observing Page Faults

```java
// Observe page faults during JVM heap allocation
// Run with: java -verbose:gc -Xms4g -Xmx4g PageFaultDemo
public class PageFaultDemo {
    public static void main(String[] args) {
        // Allocate large array - forces OS to allocate pages
        int[] arr = new int[1024 * 1024 * 256]; // 1GB
        System.out.println("Allocated. Now accessing...");
        
        // Sequential access: good spatial locality
        // Pages loaded predictably, hardware prefetcher helps
        for (int i = 0; i < arr.length; i++) {
            arr[i] = i;
        }
        System.out.println("Done.");
    }
}
```

```bash
# Run with page fault tracking
/usr/bin/time -v java PageFaultDemo
# Look for:
# "Major (requiring I/O) page faults: N"
# "Minor (reclaiming a frame) page faults: N"

# Detailed page fault stats for a running process
cat /proc/PID/stat | awk '{print "Minor:", $10, "Major:", $12}'
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Virtual address = physical address + base offset (segmentation)" | Modern OSes use paging, not segmentation. Virtual-to-physical mapping is non-contiguous. VIRT in ps can be 8GB while RSS is only 100MB because most pages are not backed by physical memory |
| "Page fault always means error or OOM" | Minor page faults are completely normal and expected (first access to newly allocated memory, copy-on-write). Only major page faults (disk I/O) hurt performance, and SIGSEGV is the "real" fault |
| "TLB is flushed only on context switch" | TLB is also flushed on: mmap/munmap of large regions, page table updates (mprotect), explicit INVLPG instruction, and VM exits in virtualized environments |

---

### Failure Modes

```
1. TLB Thrashing (huge working set, small TLB)
Symptom: application slow despite no I/O wait, no CPU bound
  (performance mystery)
Diagnosis: perf stat -e dTLB-load-misses,dTLB-stores java...
  If dTLB-load-misses > 5% of accesses: TLB pressure
Fix: Enable huge pages (2MB pages) to reduce TLB entries needed
  JVM: -XX:+UseLargePages -XX:LargePageSizeInBytes=2m
  Linux: echo 1000 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

2. Swap Thrashing
Symptom: disk I/O saturated, system unresponsive, 
  major page faults in /proc/vmstat
Diagnosis: vmstat 1 | check 'si' (swap in) and 'so' (swap out)
  If si+so > 0 constantly: swapping
Fix: Add RAM, reduce process memory, set swappiness=10,
  or disable swap for JVM containers (Java OOM >> swap)
  
3. Fork Overhead with Large JVM Heap
Symptom: fork() takes much longer than expected
Diagnosis: fork copies all page table entries (not pages)
  A 4GB JVM = ~1M PTEs to copy at fork time
Fix: Use vfork()+exec() (doesn't copy PTEs), or 
  use posix_spawn(), or avoid fork in JVM processes
```

---

### Related Keywords

**Builds on:** OSY-012 (Virtual Memory Concept), OSY-013 (MMU)

**Leads to:** OSY-032 (Page Replacement Algorithms),
OSY-054 (Virtual Memory Deep Dive)

---

### Quick Reference Card

| Property | Value |
|----------|-------|
| Standard page size | 4KB (4096 bytes) |
| Huge page size | 2MB (x86-64) |
| TLB hit cost | ~1-4 cycles |
| TLB miss cost | ~50-100 cycles (4 memory reads) |
| Minor page fault | ~1-10 microseconds |
| Major page fault (SSD) | ~100-500 microseconds |
| Major page fault (HDD) | ~1-10 milliseconds |
| x86-64 page table levels | 4 (PML4, PDPT, PD, PT) |
