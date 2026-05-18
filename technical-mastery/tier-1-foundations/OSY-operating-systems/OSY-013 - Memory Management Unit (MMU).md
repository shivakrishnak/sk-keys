---
id: OSY-013
title: Memory Management Unit (MMU)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-012
used_by: OSY-031, OSY-054
related: OSY-012, OSY-031, OSY-054
tags:
  - foundational
  - mmu
  - tlb
  - page-table
  - address-translation
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/osy/mmu/
---

## TL;DR

The MMU is a CPU chip that translates virtual addresses
to physical addresses on every memory access using page
tables. The TLB is the MMU's cache for recent translations,
reducing translation overhead from ~100 cycles to ~1 cycle.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-013 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | MMU, TLB, page table, address translation |
| **Prerequisites** | OSY-012 |

---

### MMU Role

```
Without MMU: every program accesses physical RAM directly.
  No isolation, no virtual memory, no protection.
  
With MMU: every memory instruction goes through translation:
  CPU issues: mov rax, [0x7fff1234]  (virtual address)
  MMU translates: 0x7fff1234 -> physical 0x2A00001234
  Physical RAM: returns the bytes at 0x2A00001234
  
Page table:
  The OS maintains a tree structure (multi-level page table)
  mapping virtual page numbers to physical frame numbers.
  
  4-level page table (x86-64, 48-bit virtual address):
    Virtual 0x7FFF00001000:
      PML4 index = 255 -> page directory pointer
      PDP index = 510 -> page directory
      PD index = 0 -> page table
      PT index = 1 -> page frame number 0x20008
      Offset = 0x000 -> physical 0x200080000
      
  Full table walk: 4 memory accesses per translation
  (without TLB: every memory access needs 4 memory accesses!)
```

---

### TLB (Translation Lookaside Buffer)

```
TLB: hardware cache of (virtual page, physical frame) pairs
  L1 TLB: 64-128 entries, 1 cycle access
  L2 TLB: 512-1024 entries, 5-10 cycle access
  
TLB hit (>99% of accesses normally):
  Virtual address -> TLB lookup -> physical address
  Cost: ~1 CPU cycle
  
TLB miss (<1% normally, but can spike to 10%+ with huge data):
  Virtual address -> TLB miss -> page table walk
  4 memory accesses (one per page table level)
  Cost: ~50-100 CPU cycles
  
Huge pages reduce TLB pressure:
  Normal page: 4KB, covers 4KB per TLB entry
  Huge page: 2MB, covers 2MB per TLB entry (512x more)
  A JVM heap of 4GB needs:
    4KB pages: 1,048,576 TLB entries (impossible, only 512 TLB slots)
    2MB pages: 2048 TLB entries (manageable!)
  For large JVM heaps: -XX:+UseHugeTLBFS reduces TLB misses
```

---

### Textbook Definition

The Memory Management Unit (MMU) is a hardware component
in the CPU that translates virtual addresses to physical
addresses during every memory access. It uses page tables
(maintained by the OS) for translation, with the TLB
(Translation Lookaside Buffer) caching recent translations
to avoid the overhead of repeated page table walks.

---

### Understand It in 30 Seconds

The MMU is the translator at a UN conference. It converts
what each delegate says (virtual address) to what the
microphone actually broadcasts (physical address). The TLB
is the translator's notepad of recently used phrases -
most translations are instant lookups; rare ones require
consulting the full dictionary (page table walk).

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Virtual memory is software-only" | The MMU is CPU hardware. The page table is OS-managed data, but the address translation itself is done in hardware on every memory access. Without MMU hardware, virtual memory would be too slow to use |
| "TLB misses are rare and don't matter" | For data-intensive applications with large working sets (JVM with large heaps, in-memory databases), TLB misses can account for 10-30% of execution time. Huge pages are specifically designed to combat TLB miss rates at scale |

---

### Mastery Checklist

- [ ] Knows MMU translates virtual to physical on every memory access
- [ ] Understands TLB as cache for translations
- [ ] Knows why huge pages reduce TLB pressure for large JVM heaps
- [ ] Can estimate TLB miss cost (~100 cycles) vs hit cost (~1 cycle)
