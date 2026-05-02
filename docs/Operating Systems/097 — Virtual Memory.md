---
layout: default
title: "Virtual Memory"
parent: "Operating Systems"
nav_order: 97
permalink: /operating-systems/virtual-memory/
number: "097"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Memory Management Models, CPU Architecture
used_by: Paging, TLB, Swap Space, Memory-Mapped Files, Context Switch
tags:
  - os
  - memory
  - performance
  - intermediate
---

# 097 — Virtual Memory

`#os` `#memory` `#performance` `#intermediate`

⚡ TL;DR — An OS abstraction giving each process the illusion of its own large private address space, backed by physical RAM and disk (swap), managed by the MMU and OS page tables.

| #097 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Process, Memory Management Models, CPU Architecture | |
| **Used by:** | Paging, TLB, Swap Space, Memory-Mapped Files, Context Switch | |

---

### 📘 Textbook Definition

**Virtual memory** is an OS memory management technique that provides each process with an abstracted address space — its **virtual address space** — larger than and independent of physical RAM. The hardware **MMU (Memory Management Unit)** translates virtual addresses to physical addresses at runtime using **page tables** maintained per process. Physical memory is divided into **pages** (~4 KB each); virtual pages are mapped to physical frames on demand (**demand paging**). Pages not in physical RAM are stored on disk (**swap space**); accessing them triggers a **page fault**, causing the OS to load the required page from disk. This abstraction provides isolation, enables more processes than RAM can hold, and supports copy-on-write and memory-mapped files.

### 🟢 Simple Definition (Easy)

Virtual memory gives each program its own imaginary pool of memory addresses, much larger than the computer's actual RAM — the OS and hardware translate those addresses to real memory (or disk) transparently.

### 🔵 Simple Definition (Elaborated)

Without virtual memory, all programs would share and compete directly for the same physical RAM addresses — one buggy program writing to a wrong address could corrupt another. Virtual memory solves this: each process sees a private address space (e.g., 0 to 2^47 bytes on 64-bit Linux) that appears to be all its own. Write to address 0x7fff000 in process A and it writes to a physical frame mapped ONLY for process A — process B's address 0x7fff000 points to a completely different physical frame. The MMU hardware handles translation on every memory access with nanosecond overhead using a TLB cache.

### 🔩 First Principles Explanation

**The core problem: multiple processes, limited RAM:**

Without virtual memory, if Process A is at physical address 0–100 MB and Process B is at 100–200 MB, Process A cannot grow beyond 100 MB, cannot be relocated, and cannot be isolated from B. Adding a third process with different size becomes a puzzle.

**Virtual address space layout (64-bit Linux):**

```
Virtual Address Space (47 bits used = 128 TB):
0xFFFF... → Kernel (inaccessible to user)
    ...
0x7FFF... → Stack (grows down) ← ulimit -s
    ...
              Memory-mapped region (shared libs, mmap)
    ...
0x0001... → Heap (grows up via brk/mmap)
              BSS / Data / Code (text)
0x0000...0400000 → typical text segment start
0x0000...0000000 → NULL (not mapped, SIGSEGV)
```

**Address translation (page table walk):**

```
Virtual Address: [VPN2][VPN1][VPN0][Page Offset]
                  9 bits  9 bits  9 bits  12 bits (4 KB page)

1. CPU generates virtual address
2. Check TLB: if hit → physical address in ~5 ns
3. If TLB miss → hardware page table walk:
   a. CR3 → PGD (Page Global Dir)
   b. PGD[VPN2] → PUD (Page Upper Dir)
   c. PUD[VPN1] → PMD (Page Middle Dir)
   d. PMD[VPN0] → PTE (Page Table Entry)
   e. PTE contains: [Physical Frame Number | Present | RW | User | Dirty | ...]
4. Physical Address = PFN | Page Offset
5. Load TLB entry (future accesses: fast path)
Total page walk: 4 memory accesses → ~20-100 ns
```

**Page fault mechanism:**

```
Process accesses virtual address V → PTE.Present = 0 (not in RAM)
  → CPU raises page fault exception → kernel page fault handler
  → Handler checks if mapping is valid (in process's VMAs):
     a. Valid + in swap: load page from swap disk → map → retry instruction
     b. Valid + COW: copy page → map new page → retry
     c. Valid + anonymous: allocate zero page → map → retry
     d. Invalid (null deref, OOB): send SIGSEGV → process killed
  → Instruction re-executed transparently after handler returns
```

**Copy-on-Write (COW) after fork():**

```
fork() creates child: page tables point to SAME physical pages
                      with COW flag set (write-protected)

Child writes to page P:
  Hardware write-protect fault → kernel handler:
    1. Allocate new physical frame P'
    2. Copy content of P → P'
    3. Update child's PTE to point to P'
    4. Clear COW flag
    5. Retry write

Result: Child gets private copy ONLY when it writes.
Memory pages not written by either process remain shared.
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Virtual Memory:

- Processes compete for fixed physical address ranges → relocation nightmare.
- Buffer overflow in one process corrupts another → security catastrophe.
- RAM limit = hard limit on running processes (no overcommit).
- No memory-mapped files, no zero-copy I/O.

What breaks without it:
1. Any pointer arithmetic error in one Java object reaches OS kernel memory.
2. fork() requires physically copying all parent memory — impossible at GB scale.

WITH Virtual Memory:
→ Each process sees isolated address space — protection guaranteed by MMU hardware.
→ fork() is O(1) via COW — no actual copy until write.
→ Overcommit: 100 processes can each allocate 2 GB even on 16 GB RAM (as long as actual usage fits).

### 🧠 Mental Model / Analogy

> Virtual memory is like a hotel's room numbering system. Every hotel on earth has rooms 101, 102, 103... (virtual addresses). Room 101 in Hotel A is completely independent of Room 101 in Hotel B — they are physically different rooms (different physical frames). The hotel management (MMU + OS) has a master key book (page tables) translating "Hotel A, Room 101" → physical floor and location. When a room is booked but not yet assigned (demand paging), the management assigns a physical room only when the guest actually checks in (first access). A full hotel can re-use rarely-used rooms by moving their guest's luggage to a storage facility (swap) temporarily.

"Hotel room number" = virtual address, "physical room" = physical RAM frame, "master key book" = page table, "storage facility" = swap space/disk.

### ⚙️ How It Works (Mechanism)

**Memory usage metrics (Java relevance):**

```
Virtual Memory (VIRT): all mapped virtual addresses — typically huge (GB+)
                       Includes: stack, heap, shared libs, mmap'd files
Resident Set Size (RSS): pages actually in physical RAM right now
                         The "real" memory usage
Shared (SHR):           pages shared with other processes (shared libs)
Anonymous Memory:       heap, stack — not backed by a file
File-backed Memory:     code segments, mmap'd files

Java process typical on 8 GB heap:
  VIRT: 10–12 GB (includes JVM internals + mapped files + compressed OOP range)
  RSS:  4–8 GB   (actual heap pages resident in RAM)
  SHR:  100–200 MB (JVM shared library code)
```

**Monitoring virtual memory:**

```bash
# Per-process virtual memory layout
cat /proc/<pid>/maps  or  cat /proc/<pid>/smaps
# Shows each virtual memory area (VMA): address range, flags, backing file

# High-level summary
cat /proc/<pid>/status | grep -E "VmRSS|VmSize|VmSwap"
# VmSize: total virtual memory
# VmRSS:  resident (in RAM) — the real memory usage
# VmSwap: pages currently swapped to disk

# System-wide virtual memory
free -h
vmstat 1 5
cat /proc/meminfo
```

### 🔄 How It Connects (Mini-Map)

```
Physical RAM (limited resource)
        ↓ abstracted by
Virtual Memory ← you are here
  (per-process address space; MMU translation)
        ↓ implemented via
Paging (4 KB pages mapping virtual → physical)
TLB (hardware cache for fast address translation)
        ↓ extends to disk
Swap Space (overflow when RAM full — very slow)
Memory-Mapped Files (file access via virtual memory)
        ↓ key property
Process Isolation (each process sees only its own pages)
Copy-on-Write (fork() efficiency)
```

### 💻 Code Example

Example 1 — Monitoring Java process RSS vs Virtual:

```bash
# Java process memory: VIRT is misleading; RSS is meaningful
ps aux | grep java
# USER    PID  %CPU %MEM    VSZ    RSS  COMMAND
# appuser 1234  45.0 12.5 10485760 2048000 java -Xmx8g ...
# VSZ (virtual) = 10 GB, RSS (resident) = 2 GB
# → Only 2 GB actually in RAM; rest is virtual reservation

# Better: smaps_rollup for RSS breakdown
cat /proc/$(pgrep java)/smaps_rollup
# RSS detail: code/stack/heap/shared-libraries
```

Example 2 — mmap-based memory-mapped file (Java MappedByteBuffer):

```java
// Memory-mapped file: virtual memory backed by file (not anonymous heap)
// OS handles paging — reads trigger page fault → loads from file
try (FileChannel channel = FileChannel.open(
        Paths.get("large-data.bin"),
        StandardOpenOption.READ)) {

    // Map 1 GB of file into virtual address space
    // No physical RAM allocated yet — demand paging
    MappedByteBuffer buf = channel.map(
        FileChannel.MapMode.READ_ONLY, 0,
        channel.size());

    // Accessing a byte triggers a page fault → OS reads 4 KB page from file
    byte firstByte = buf.get(0);  // page fault → load page → return byte
    // Subsequent accesses to same page: no page fault (page is now in RAM)
}
// Unmap: physical pages freed; virtual space reclaimed
```

Example 3 — Detecting Java heap in swap:

```bash
# DANGER: Java heap pages swapped to disk → massive GC pauses
# GC needs to access all heap objects → triggers disk reads

# Check if Java is using swap
cat /proc/$(pgrep java)/status | grep VmSwap
# VmSwap: 512000 kB  ← 512 MB of heap is on disk!
# This will cause extreme GC pause times

# Prevent swapping:
# 1. Ensure enough physical RAM for heap + OS
# 2. Use mlockall() to pin Java process pages (production heavy workloads)
# 3. Enable huge pages: -XX:+UseHugeTLBFS -XX:+UseLargePages
# 4. Set vm.swappiness=10 (preference: RAM over swap)
sudo sysctl -w vm.swappiness=10
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Virtual memory size (VIRT) = memory used | VIRT shows total mapped address space. RSS (resident set size) shows pages actually in physical RAM. A Java process with -Xmx8g and VIRT=10 GB may only have RSS=4 GB. |
| More virtual address space means less RAM available | Virtual address space allocation doesn't consume physical RAM. Only RSS (resident pages) consumes physical RAM. A 100 TB virtual address space on a 16 GB machine is fine. |
| Swap is just slower RAM | Swap is 1000–10,000× slower than RAM (HDD: 10ms, SSD: 0.1ms, RAM: 100ns). Java using swap = GC disaster. |
| Two processes can never share memory | Shared libraries, anonymous mmap segments, and explicit shared memory (shmem) are all shared physical pages mapped into multiple processes' virtual address spaces. |
| Page fault is always a problem to avoid | Anonymous page faults (first access to newly allocated memory) are expected and normal. Only major page faults (loading from swap/disk) are performance problems. |

### 🔥 Pitfalls in Production

**1. Java Heap Configured Larger Than Available RAM**

```bash
# BAD: All heap in virtual address space but not RAM
java -Xmx32g -jar app.jar  # on a 16 GB machine!

# RSS grows as heap is used → eventually exceeds 16 GB
# OS starts swapping Java heap → GC touches swapped pages → 10s pauses

# GOOD: Leave RAM for OS, JVM off-heap, other processes
# Rule: -Xmx ≤ (total_RAM - 2 GB for OS/buffers) × 0.75
java -Xmx10g -jar app.jar  # on a 16 GB machine = safe
```

**2. Transparent Huge Pages Causing JVM Latency Spikes**

```bash
# Linux THP (Transparent Huge Pages) auto-coalesces 4 KB pages into 2 MB pages
# defrag process locks memory → multi-millisecond pauses in Java
# Symptom: unexplained latency spikes NOT correlated with GC

# Diagnose: check THP defrag
cat /proc/$(pgrep java)/smaps | grep AnonHugePages

# Fix: disable THP defrag (not THP itself) for Java processes
echo madvise > /sys/kernel/mm/transparent_hugepage/defrag
# Or: per-process via madvise(MADV_NOHUGEPAGE) on heap region
```

**3. Fork() + Exec() Pattern with Large JVM Heap (Memory Overcommit)**

```bash
# BAD: Spawning a process via Runtime.exec() on a 8 GB heap JVM
# fork() copies all page table entries — COW deferred copy
# All 8 GB of virtual pages marked COW → any write triggers copy
# Under load: system appears to need 2× 8 GB = 16 GB → OOM killer

# GOOD: Use ProcessBuilder (same risk) or reduce JVM heap
# Or: prefer vfork()/posix_spawn() which doesn't clone full address space
# Java ProcessBuilder uses vfork where available since JDK 14
ProcessBuilder pb = new ProcessBuilder("external_tool");
pb.start(); // Java uses vfork/posix_spawn internally → safe
```

### 🔗 Related Keywords

- `Paging` — the mechanism that divides virtual and physical memory into fixed-size pages.
- `TLB` — the hardware cache making virtual-to-physical translation fast.
- `Swap Space` — disk-backed overflow for physical RAM shortage.
- `Process` — each process has its own virtual address space.
- `Context Switch` — process context switch changes CR3 → TLB flush required.
- `Memory-Mapped Files` — file I/O via virtual memory paging mechanism.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Each process: own virtual address space;  │
│              │ MMU translates to physical RAM on demand. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Monitor: RSS (not VIRT) for Java memory;  │
│              │ avoid swap for GC-heavy heaps; mmap for   │
│              │ large file access.                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never: heap > available RAM − headroom;   │
│              │ never: allow Java heap to swap.           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Virtual memory: every process thinks it  │
│              │ owns the whole city — the OS manages the  │
│              │ population."                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Paging → TLB → Swap Space → mmap          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice running on Kubernetes has `-Xmx4g` (4 GB heap) but the container `memory.limits` is set to 4.5 GB. Over time, the pod restarts with OOMKilled even though heap dumps show only 3.5 GB heap usage. Identify at least three sources of off-heap memory usage in a JVM process that could consume the remaining memory, explain which of these is configurable, and describe the correct approach to sizing a container's memory limits relative to `-Xmx`.

**Q2.** Linux Overcommit policy (`vm.overcommit_memory=1`) allows the kernel to grant virtual memory allocations even when physical RAM + swap cannot satisfy them all — the bet being that not all allocations will be used simultaneously. A Java application calls `new byte[1_000_000_000]` on a machine with 512 MB free RAM. Trace each step: (1) the JVM's `malloc` call, (2) the kernel's response under overcommit=1, (3) what happens when the array is first accessed, and (4) what the OOM killer does if physical memory runs out — specifically, which process it targets and by what metric.

