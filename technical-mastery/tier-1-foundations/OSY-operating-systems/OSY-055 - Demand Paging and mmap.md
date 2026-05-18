---
id: OSY-055
title: Demand Paging and mmap
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-031, OSY-054
used_by: OSY-089
related: OSY-054, OSY-056, OSY-089
tags:
  - demand-paging
  - mmap
  - memory-mapped-file
  - lazy-allocation
  - page-fault
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/osy/demand-paging-mmap/
---

## TL;DR

Demand paging: pages loaded into physical RAM only when
first accessed (not at allocation). This enables programs
larger than RAM and fast process startup. mmap() maps
files directly into virtual address space without explicit
read() calls - the page fault mechanism loads file data on
first access, enabling zero-copy file reads.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-055 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | demand paging, mmap, lazy allocation, page fault |
| **Prerequisites** | OSY-031, OSY-054 |

---

### Demand Paging Mechanics

```
Traditional loading (NOT demand paging):
  Program starts -> OS loads ALL code and data -> start execution
  Problem: program may use only 10% of code; rest wasted I/O
  
Demand paging:
  Program starts -> OS creates VMAs, maps pages as NOT present (P=0)
  First access to any page -> PAGE FAULT -> kernel:
    1. Reads page from disk (executable or swap)
    2. Allocates physical frame
    3. Sets PTE: P=1, frame number = new frame
    4. Returns to user code at the faulting instruction
    5. Instruction re-executes successfully
  
Benefits:
  1. Fast startup: only load code/data when actually used
  2. Programs larger than physical RAM (swap inactive pages)
  3. Memory sharing: multiple processes map same executable
     -> code pages shared (not duplicated)
     
Working set principle:
  Programs have a working set: pages actively used
  If working set fits in RAM: no swap needed
  If working set > RAM: thrashing (constant page faults)
```

---

### mmap Internals

```
mmap(addr, length, prot, flags, fd, offset):
  1. Creates a VMA in the process address space
  2. VMA describes: file fd, offset, size, permissions
  3. Does NOT load any file data into RAM yet
  4. Returns virtual address of the mapping
  
First access to mapped address:
  1. MMU: PTE.present = 0 -> page fault
  2. Kernel page fault handler:
     a. Find VMA containing faulting address
     b. VMA is file-backed: find the file's page in page cache
     c. Page cache HIT: map existing physical page to PTE (fast)
     d. Page cache MISS: read from disk to page cache, map to PTE
  3. Return to user code, re-execute the load/store

  
Sequential file access with mmap:
  kernel's readahead kicks in after first few faults:
  reads ahead (async) 64-128KB in anticipation
  -> subsequent page faults served from page cache (no I/O wait)

mmap MAP_SHARED vs MAP_PRIVATE:
  MAP_SHARED:
    Writes by any process visible to all other mappers
    Write -> marks page dirty in page cache
    msync() / munmap() -> writes dirty pages to disk
    
  MAP_PRIVATE:
    Creates COW copy of the file's page
    Write -> COW fault -> allocate private frame, copy, mark dirty
    Changes NOT reflected to file or other processes
    (Used for: executable loading - code is MAP_PRIVATE | EXEC)

mmap vs read() performance:
  read():
    Syscall -> kernel reads to page cache ->
    copies from page cache to user buffer (JVM heap)
    TWO copies total: disk -> page cache -> user buffer
    
  mmap():
    Page fault -> kernel maps page cache page to VMA
    ONE mapping: disk -> page cache -> directly accessible
    Zero-copy: user accesses page cache memory directly
    
  mmap() wins for: large files, frequent re-reads (stays in cache)
  read() wins for: streaming single-pass (simpler, good readahead)
```

---

### Practical mmap Usage in Java

```java
// Memory-mapped file reading (zero-copy)
public class MmapFileReader {
    public static void readWithMmap(Path filePath) throws IOException {
        try (FileChannel channel = FileChannel.open(filePath,
                StandardOpenOption.READ)) {
            long size = channel.size();
            
            // mmap: creates read-only MAP_SHARED mapping
            MappedByteBuffer buffer = channel.map(
                FileChannel.MapMode.READ_ONLY, 0, size);
            
            // Accessing buffer data triggers page faults (first time)
            // After first access: page is in page cache, subsequent
            // accesses are pure memory reads (no syscalls)
            
            // Read data (may trigger page faults on first access):
            byte[] data = new byte[buffer.remaining()];
            buffer.get(data);  // copies from page-cache-backed memory
            
            // For truly zero-copy: use buffer directly without .get()
            // Pass MappedByteBuffer to NIO operations
        }
        // Note: MappedByteBuffer does NOT close on channel.close()
        // The mapping lives until GC or explicit unmap (Java 14+)
    }
    
    // Explicitly unmap (Java 14+, cleaner API)
    public static void unmapExplicitly(MappedByteBuffer buf) {
        buf.force();  // flush dirty pages to file
        // Java 14+: no public API; use Cleaner via reflection
        // Until Java has explicit unmap: rely on GC finalization
    }
}
```

```bash
# Observe mmap in action with strace:
strace -e trace=mmap,mprotect java MmapFileReader 2>&1 | head -20
# See: mmap() calls for file mapping
# mmap(NULL, 104857600, PROT_READ, MAP_SHARED, fd=5, 0)
#   = 0x7f8a00000000  <- virtual address of mapping

# Observe page faults (major = from disk, minor = from page cache):
/usr/bin/time -v java MmapFileReader 2>&1 | grep "page faults"
# First run: many major page faults (loading from disk)
# Second run: zero major page faults (page cache warm)
```

---

### Demand Paging in the JVM

```
JVM startup with demand paging:
  -Xms512m: "commit" 512MB - reserve virtual, touch with zeros
  -Xmx4g:   "reserve" 4GB - virtual only, no physical pages
  
  Large Pages (-XX:+UseLargePages):
    Each 2MB page: one TLB entry (vs 512 TLB entries for 4KB)
    Allocation: OS must find 2MB contiguous physical region
    First access: one page fault allocates 2MB (not 4KB)
    
  AlwaysPreTouch (-XX:+AlwaysPreTouch):
    Force touch all heap pages at startup
    Eliminates demand-paging latency during first GC cycle
    Cost: longer startup time (writes zeros to all pages)
    Benefit: predictable latency (no page fault surprises)
    Use in production: yes (startup slower, runtime more predictable)
    
  Without AlwaysPreTouch:
    First GC after startup: page faults as GC touches all heap pages
    Can cause unexpectedly long first GC pause
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "malloc() allocates physical memory immediately" | malloc() calls brk() or mmap() which creates a VMA but doesn't touch physical pages. Physical pages are allocated only when the memory is first written (demand zero paging). This is why a 4GB malloc() returns quickly even with only 1GB RAM |
| "mmap is the same as loading a file into memory" | mmap creates a virtual memory mapping; pages are loaded lazily on access. The difference: traditional file loading (read()) copies to a JVM buffer. mmap doesn't copy - it provides direct access to the page cache, enabling zero-copy reads |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Demand paging benefit | Fast startup, programs larger than RAM |
| mmap vs read | mmap: zero-copy (page cache direct access) |
| MAP_SHARED write | Writes visible to other mappers; flushed to file |
| MAP_PRIVATE write | COW; private copy; not flushed to file |
| AlwaysPreTouch | Eliminate page fault surprises in JVM; slower startup |
| Huge pages benefit | 512x fewer TLB entries; less TLB pressure |
