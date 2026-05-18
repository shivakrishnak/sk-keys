---
id: OSY-047
title: Segmentation vs Paging Decision Guide
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-031
used_by: []
related: OSY-031, OSY-033, OSY-054
tags:
  - segmentation
  - paging
  - memory-management
  - comparison
  - decision-guide
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/osy/segmentation-vs-paging/
---

## TL;DR

Segmentation: variable-size logical divisions (code,
stack, heap). Paging: fixed-size physical frames (4KB).
Modern OSes use paging (no external fragmentation, simple
allocation). x86 hardware supports both but Linux uses
paging with minimal segmentation (flat model). Java
programmers interact with paging via memory layout
and page faults.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-047 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | segmentation, paging, memory management, comparison |
| **Prerequisites** | OSY-031 |

---

### Segmentation

```
Segmentation: memory divided into variable-size named regions

Segment = (base address, limit, permissions)
  Code segment:  base=0x1000, limit=4096, r-x (read+execute)
  Data segment:  base=0x2000, limit=8192, rw- (read+write)
  Stack segment: base=0x8000, limit=4096, rw- grows down
  
Address translation:
  Logical address = (segment_number, offset)
  Physical address = segments[segment_number].base + offset
  
  If offset >= segment.limit -> SIGSEGV

Advantages:
  - Logical: segments map to programmer model (code, stack, heap)
  - Sharing: two processes can share code segment (same physical)
  - Protection: different permissions per segment

Disadvantages:
  - External fragmentation: variable sizes leave gaps
    After many alloc/free: RAM has many small unusable holes
  - Variable allocation: OS must find contiguous region per segment
  - Complex: segment table, hardware segment registers
  
Historical use: x86 16-bit, Intel 286, early OS/2
Current use: x86-64 has segment registers but Linux
  sets all segments to cover full address space (flat model)
  -> Segmentation effectively disabled in modern Linux
```

---

### Paging

```
Paging: memory divided into FIXED-SIZE pages (4KB)

Address translation:
  Virtual address = (virtual page number, offset)
  Physical address = page_table[VPN].frame * 4096 + offset

Advantages:
  - No external fragmentation: all frames are same size
  - Simple allocation: any free frame works
  - Large virtual address space: 64-bit = 128TB virtual space
  - Protection: per-page permissions (r, rw, rwx, none)

Disadvantages:
  - Internal fragmentation: last page of segment may be
    partially empty (max waste = page_size - 1 = 4095 bytes)
  - No logical division: address space is flat (no code/stack
    distinction in hardware, only by convention)
  - Page table overhead: 4KB pages * 16GB RAM = many PTEs
    (solved by multi-level page tables + TLB caching)
```

---

### Modern x86-64: Paging Wins

```
Linux x86-64 configuration:
  Segment registers (CS, DS, SS, GS, FS):
    All set to base=0, limit=full address space
    Effectively: segment translation disabled
    
  Page tables: fully enabled (4-level PT)
    All memory protection via page permissions
    
  Exception: FS/GS segments used for:
    FS: thread-local storage (TLS) per-thread pointer
    GS: kernel per-CPU data pointer
    These are special-purpose, not the old segmentation model
    
Why paging won:
  1. External fragmentation eliminated (fixed-size frames)
  2. Simple OS allocator (buddy system, free list of frames)
  3. Hardware TLB and multi-level PT make it efficient
  4. Demand paging: only load pages when accessed
  5. Copy-on-write: pages shared until write (cheap fork)
```

---

### Comparison Table

| Property | Segmentation | Paging |
|---------|-------------|--------|
| Division size | Variable (logical) | Fixed (4KB/2MB) |
| External fragmentation | YES | No |
| Internal fragmentation | No | Up to page_size-1 |
| Alignment requirement | Segment boundary | Page boundary |
| Programmer visibility | YES (code/stack/heap) | Hidden (flat virtual) |
| Address translation | segment + offset | VPN + offset |
| Hardware support | x86 segment registers | x86 CR3, page tables |
| Used in Linux today | No (flat model) | YES |
| Memory protection | Per-segment | Per-page |

---

### Java Relevance

```java
// Java programmers interact with paging, not segmentation

// StackOverflowError = stack page crosses into guard page
// (guard page: unmapped page at stack limit, causes SIGSEGV)
public class StackOverflowTest {
    public static void recurse(int depth) {
        recurse(depth + 1);  // infinite recursion
        // When stack exhausts its 1MB (default -Xss) allocation:
        // Next frame would map into guard page
        // MMU: no PTE -> page fault -> kernel -> SIGSEGV
        // JVM converts to StackOverflowError
    }
}

// SIGSEGV = NullPointerException in Java
// Address 0x0 (null) is never mapped (no PTE for page 0)
// MMU: page fault on address 0 -> SIGSEGV -> JVM -> NullPointerException

// Large pages for JVM heap (2MB instead of 4KB)
// Reduces TLB pressure (512x fewer TLB entries needed)
// -XX:+UseLargePages -XX:LargePageSizeInBytes=2097152
// OS must have huge pages configured:
// echo 1000 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Modern x86 systems still use segmentation" | Linux sets all segment bases to 0 and limits to max - effectively disabling the variable segmentation model. Segment registers exist but only FS/GS are used (for thread-local storage) |
| "Paging has no fragmentation" | Paging has INTERNAL fragmentation (last page partially empty, max 4095 bytes waste per segment). Paging eliminates EXTERNAL fragmentation (no variable-size holes between allocations) |

---

### Quick Reference Card

| Feature | Segmentation | Paging |
|---------|-------------|--------|
| Fragmentation type | External | Internal (small) |
| OS of choice | Historical (x86 16-bit) | All modern OSes |
| Linux usage | Minimal (flat model) | Full paging |
| Java impact | None | Page faults, TLB, huge pages |
