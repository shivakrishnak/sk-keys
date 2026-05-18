---
id: OSY-012
title: Virtual Memory Concept
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-009
used_by: OSY-013, OSY-025, OSY-031, OSY-054
related: OSY-013, OSY-031, OSY-054
tags:
  - foundational
  - virtual-memory
  - address-space
  - paging
  - isolation
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/osy/virtual-memory/
---

## TL;DR

Virtual memory gives each process the illusion of private,
contiguous memory from address 0 to 2^64. The OS and MMU
transparently map virtual addresses to physical RAM. This
enables isolation, memory overcommit, and larger-than-RAM
address spaces.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-012 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | virtual memory, address space, paging, isolation |
| **Prerequisites** | OSY-009 |

---

### The Three Problems Virtual Memory Solves

```
Problem 1: Isolation
  Without virtual memory: process A's pointer to address
  0x1000 could hit process B's data. One bug corrupts both.
  With VM: each process has its OWN address space.
  Same virtual address 0x1000 maps to DIFFERENT physical
  pages for each process. Collision impossible.

Problem 2: Fragmentation
  Without VM: processes need contiguous physical RAM.
  If 4 processes need 256MB each = 1GB contiguous RAM.
  RAM may have 1GB total but not 1GB contiguous -> failure.
  With VM: virtual addresses are contiguous; physical pages
  scattered. OS handles the mapping. No fragmentation issue.

Problem 3: Over-commitment
  Without VM: process must claim ALL memory it MIGHT need.
  With VM: processes can claim more virtual memory than
  physical RAM exists. OS allocates physical pages lazily
  (demand paging). 10 processes each "claim" 8GB on a
  4GB machine = works fine if they don't all use 8GB.
```

---

### Virtual vs Physical Address

```
Virtual address: what the program sees
  e.g., int* ptr = new int[1024]; // ptr = 0x7FFF00001000
  
Physical address: actual DRAM location
  e.g., DRAM address 0x200080001000 (different chip/bank)

The MMU (Memory Management Unit) hardware translates:
  virtual 0x7FFF00001000 -> physical 0x200080001000
  
This translation happens on EVERY memory access (CPU cycle).
Modern CPUs have TLB (Translation Lookaside Buffer) to
cache recent virtual->physical mappings for speed.
TLB miss: ~5-10x slower memory access (must walk page table).
```

---

### Virtual Memory in Practice (Java)

```
$ ps aux | grep java
java 42381 ... VIRT=8192MB RES=2048MB

VIRT (Virtual Memory Size): 8GB claimed by JVM
  Includes: heap max (-Xmx4g), metaspace, native memory,
            memory-mapped jars, stack for all threads
  JVM claims 8GB but doesn't need physical RAM until used
  
RES (Resident Set Size): 2GB actually in physical RAM
  Pages that have been accessed and are in physical memory
  This is the RAM your JVM actually consumes

VIRT >> RES is normal and healthy.
VIRT approaching physical RAM limit = risk of OOM or swap.

Java developers often confuse VIRT and RES:
  "My JVM is using 8GB!" -> wrong (that's VIRT)
  "My JVM is using 2GB!" -> correct (that's RES)
```

---

### Textbook Definition

Virtual memory is a memory management technique that
provides each process with an abstracted view of memory
as a private, contiguous address space. The OS maintains
a page table mapping virtual pages to physical page frames.
The MMU hardware performs address translation on every
memory access, with TLB caching frequent mappings.

---

### Understand It in 30 Seconds

Virtual memory is like hotel room numbers. Room 101 at
Hotel A and Room 101 at Hotel B are different physical
rooms. Each guest (process) thinks they have "their own"
room 101. The hotel management (OS + MMU) maps room
numbers to actual beds (physical RAM).

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "VIRT in ps output is the JVM's real memory use" | VIRT is the virtual address space claimed. RES (resident) is physical RAM in use. A JVM showing VIRT=8GB, RES=2GB uses 2GB of actual RAM |
| "Virtual memory means the OS uses disk as RAM (swap)" | Swap is an optional extension of virtual memory. VM itself is the address translation mechanism. Swap is one possible backing store for pages that don't fit in physical RAM |

---

### Mastery Checklist

- [ ] Knows the 3 problems virtual memory solves (isolation, fragmentation, overcommit)
- [ ] Understands VIRT vs RES in process memory reporting
- [ ] Knows the role of MMU in address translation
- [ ] Can explain TLB and why it exists
