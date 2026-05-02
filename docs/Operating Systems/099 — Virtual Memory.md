---
layout: default
title: "Virtual Memory"
parent: "Operating Systems"
nav_order: 99
permalink: /operating-systems/virtual-memory/
number: "0099"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, User Space vs Kernel Space, Memory Management Models
used_by: Paging, Page Fault, TLB, Memory-Mapped File (mmap), Swap / Thrashing
related: Paging, Physical Memory, Memory-Mapped File (mmap)
tags:
  - os
  - memory
  - internals
  - intermediate
  - virtual-memory
---

# 099 — Virtual Memory

⚡ TL;DR — Virtual memory gives every process its own private, unlimited-looking address space — the OS secretly maps it to real RAM using page tables.

| #0099           | Category: Operating Systems                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Process, User Space vs Kernel Space, Memory Management Models        |                 |
| **Used by:**    | Paging, Page Fault, TLB, Memory-Mapped File (mmap), Swap / Thrashing |                 |
| **Related:**    | Paging, Physical Memory, Memory-Mapped File (mmap)                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine 10 programs running on a machine with 4 GB of RAM, each hardcoded to use absolute physical memory addresses. Program A occupies 0x0000–0x3FFF. Program B must start at 0x4000, and the programmer must know this at compile time. If you want to run an 11th program but RAM is full, you either evict an entire program or crash. Worse, Program A can freely read and modify Program B's memory since both use real physical addresses — no isolation, no protection.

**THE BREAKING POINT:**
This is exactly how early embedded systems and MS-DOS worked. It meant: no multitasking without programmer coordination, no memory isolation, and you could never run a program that needed more memory than was physically available.

**THE INVENTION MOMENT:**
This is exactly why Virtual Memory was created — to give each process the illusion of having its own full, private address space, while the OS secretly manages which physical RAM (or disk) backs each region.

---

### 📘 Textbook Definition

**Virtual memory** is an OS abstraction that decouples the addresses a process uses (virtual addresses) from the addresses of actual physical RAM. Each process operates in its own private virtual address space, mapped to physical memory through a hardware-managed page table. The OS can store infrequently accessed pages on disk (swap), load only the needed pages into RAM (demand paging), share physical pages between processes (copy-on-write), and enforce memory protection by controlling page table entries — all transparently to the running process.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every process thinks it owns all of memory — the OS and hardware quietly manage the lie.

**One analogy:**

> A hotel has 100 rooms (physical RAM). Each guest (process) receives a key card that says "your room is #42" — but behind the scenes, the hotel management (OS) assigns whichever actual room is available. Room #42 on your key might be room #7 in reality. The guest never knows or cares — they just use their key.

**One insight:**
The most powerful consequence of virtual memory is isolation: two processes can both have a pointer to address `0x7FFF1234` and be pointing to completely different physical memory locations. This is why a crash in one process cannot corrupt another — their address spaces are entirely separate mappings.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every virtual address used by a process must be translated to a physical address before RAM can be accessed.
2. Each process has its own page table — the same virtual address in two processes maps to different (or the same, if shared) physical pages.
3. A virtual page can be backed by RAM, disk (swap), a file, or be marked "not present" — the OS decides.

**DERIVED DESIGN:**
Given that every address must be translated, the CPU needs a fast translation path. The hardware MMU (Memory Management Unit) does the translation using the page table, which is a tree structure in RAM. Since RAM access for every translation would double memory latency, the TLB (Translation Lookaside Buffer) caches recent virtual→physical translations. The OS loads the page table base pointer into the CR3 register (x86-64) on every context switch, so each process gets its own translation context.

**THE TRADE-OFFS:**
**Gain:** Process isolation, demand paging (run programs larger than RAM), memory sharing (read-only code shared between processes), memory protection.
**Cost:** Every memory access has TLB lookup overhead; page table itself consumes RAM (a 4-level page table can be 512 GB of virtual space per process); page faults (cold starts, swap) add microseconds to milliseconds of latency.

---

### 🧪 Thought Experiment

**SETUP:**
Two programs both declare `int x = 5` at address `0x601000`. Machine has 1 GB RAM.

**WHAT HAPPENS WITHOUT virtual memory:**

1. Both programs compile with absolute addresses.
2. They can't both run — address `0x601000` belongs to whoever loaded first.
3. If forced to coexist, writing `x=10` in Program A also changes Program B's `x`.
4. System is either single-tasking or requires manual address-space partitioning.

**WHAT HAPPENS WITH virtual memory:**

1. Program A's `0x601000` maps to physical page at `0x2A000` (OS choice).
2. Program B's `0x601000` maps to physical page at `0x7F000`.
3. Both write to "their" `0x601000` — they modify entirely different physical bytes.
4. OS can even swap Program B's page to disk while A runs — A sees no difference.

**THE INSIGHT:**
Virtual memory is not just about running programs larger than RAM. Its primary value is **isolation**: the same virtual address in different processes is a completely different location in physical memory. This single fact makes modern multitasking operating systems possible.

---

### 🧠 Mental Model / Analogy

> Virtual memory is like a phone book where each city (process) has its own directory, and "Main Street #42" means different physical streets in different cities. The GPS (MMU + TLB) translates your city's address to GPS coordinates (physical address) instantly.

- "City-specific phone book" → per-process page table
- "Street address" → virtual address
- "GPS coordinates" → physical address
- "Phone book lookup" → TLB hit (fast) or page table walk (slow)
- "Address not found" → page fault → OS handler

Where this analogy breaks down: Unlike a phone book, page tables are 4 levels deep and can map 128 TB of virtual space — no phone book ever handled that.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every program gets its own pretend view of memory — as if it owns the whole computer to itself. When the program uses a memory address, the operating system secretly figures out where in real memory (or even disk) that data actually lives.

**Level 2 — How to use it (junior developer):**
As a developer, virtual memory is mostly invisible — `malloc()`, stack frames, and mapped files all live in your process's virtual address space. You care about it when: (a) you get a segfault from a null/bad pointer, (b) your JVM heap or mmap region exceeds available RAM and you see swap usage spike, or (c) you use memory-mapped files (`mmap()`) for large datasets.

**Level 3 — How it works (mid-level engineer):**
On x86-64 Linux, the virtual address space is 48 bits = 256 TB. The kernel uses a 4-level page table (PGD → PUD → PMD → PTE), each level 512 entries × 8 bytes. The MMU walks the table on a TLB miss, taking ~10 memory accesses. Each PTE entry contains: physical page frame number, Present bit, Writable bit, Supervisor bit, Accessed bit, Dirty bit. `MAP_ANONYMOUS` pages start as "not present" and are only allocated on first access (demand paging). Linux uses huge pages (2 MB) to reduce TLB pressure for large memory consumers.

**Level 4 — Why it was designed this way (senior/staff):**
The 4-level page table design (vs. inverted or hashed page tables used by some architectures) trades space for speed: 4-level tables waste memory for sparse address spaces but allow fast parallel TLB reload. The 128 TB per-process limit was intentional — leaving the top 128 TB for kernel space, giving a clean split at the sign bit of a 48-bit address. Linux 5.5 extended to 5-level page tables (57-bit, 128 PB) when workloads like in-memory databases needed more than 128 TB per process. Copy-on-Write (COW) is a critical virtual memory optimization: when `fork()` is called, the child shares all parent pages with write-protect — pages are only physically copied when either process writes to them, making `fork()` + `exec()` extremely fast.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           VIRTUAL ADDRESS TRANSLATION (x86-64)          │
├─────────────────────────────────────────────────────────┤
│  Virtual Address: 0x00007F2A_3B401234                   │
│  ┌───────┬────────┬────────┬────────┬─────────────────┐ │
│  │Unused │ PGD[i] │ PUD[j] │ PMD[k] │  PTE[l] + Offs  │ │
│  │16bits │ 9 bits │ 9 bits │ 9 bits │  9 bits + 12bits│ │
│  └───────┴────────┴────────┴────────┴─────────────────┘ │
│       ↓        ↓        ↓        ↓         ↓            │
│  [CR3] → [PGD] → [PUD] → [PMD] → [PTE] → Physical page │
│                                                         │
│  TLB caches recent VA→PA mappings.                      │
│  TLB HIT: 1 cycle  │  TLB MISS: ~10 memory accesses    │
└─────────────────────────────────────────────────────────┘
```

**Step 1 — Process creation:** OS allocates a PGD (top-level page table). CR3 register points to it.

**Step 2 — Memory access:** CPU generates a virtual address. MMU checks TLB first.

**Step 3a — TLB hit:** Physical address returned immediately. ~1 cycle.

**Step 3b — TLB miss:** MMU walks the 4-level page table, reading PGD→PUD→PMD→PTE from RAM. ~10 memory accesses. Result cached in TLB.

**Step 4 — Page not present:** If PTE.Present=0, CPU raises a Page Fault (#PF). The OS page fault handler decides: load from swap, allocate a new zero page, or SIGSEGV.

**Step 5 — Context switch:** OS saves old process's CR3, loads new process's CR3. TLB is flushed (or tagged with ASID to avoid flush).

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[Process: int *p = malloc(4096)]
   → [libc: calls mmap(NULL, 4096, ...)]
   → [Kernel: creates VMA entry, no physical page yet]
   → [Process: *p = 42]
   → [MMU: TLB miss → page walk → PTE.Present=0]
   → [Page Fault ← YOU ARE HERE]
   → [Kernel: allocate physical page, update PTE]
   → [Resume: *p = 42 succeeds, 42 written to RAM]
```

**FAILURE PATH:**
[Process accesses unmapped address] → [Page Fault] → [Kernel: no VMA for this address] → [SIGSEGV sent] → [Process killed]

**WHAT CHANGES AT SCALE:**
A JVM with a 256 GB heap requires millions of page table entries — the page tables themselves consume gigabytes of RAM. At this scale, huge pages (2 MB THP) reduce TLB pressure 512× compared to 4 KB pages. On NUMA systems, page placement becomes critical: accessing a physical page on the "wrong" NUMA node costs 2–4× the latency of a local page.

---

### ⚖️ Comparison Table

| Memory Model         | Isolation        | Run >RAM?  | Sharing               | Best For                  |
| -------------------- | ---------------- | ---------- | --------------------- | ------------------------- |
| **Virtual Memory**   | Full per-process | Yes (swap) | COW + shared mappings | General-purpose OS        |
| Physical flat model  | None             | No         | Direct                | Simple embedded MCUs      |
| Segmented memory     | Partial          | No         | Possible              | x86 real mode, DOS        |
| Shared memory (mmap) | Selective        | Yes        | Explicit              | IPC, file-backed mappings |

How to choose: Virtual memory is the default for all modern OS. Use shared `mmap` regions on top of virtual memory for zero-copy IPC between cooperating processes.

---

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────────────┐
│             VIRTUAL MEMORY PAGE LIFECYCLE              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [malloc/mmap] → NOT PRESENT (VMA created, no page)   │
│       ↓ first write                                    │
│  [Page Fault] → PRESENT IN RAM (physical page mapped)  │
│       ↓ under memory pressure                         │
│  [Kswapd] → SWAPPED OUT (written to swap, PTE cleared)│
│       ↓ next access                                   │
│  [Page Fault] → SWAP-IN (read from swap, re-mapped)   │
│       ↓ process exits / munmap                        │
│  [Page freed] → RELEASED (physical page returned)     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                          |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| "Virtual memory = swap space"                           | Virtual memory is the address abstraction; swap is one backing store. You can have virtual memory without swap   |
| "64-bit processes can use 16 EB of memory"              | x86-64 uses only 48 bits → 256 TB per process; 57-bit (5-level tables) gives 128 PB                              |
| "malloc() immediately uses RAM"                         | malloc returns a virtual address; physical RAM is not allocated until the page is first accessed (demand paging) |
| "Two processes with the same pointer see the same data" | Same virtual address = different physical address in different processes (unless explicitly shared)              |
| "mmap'd files are loaded into RAM immediately"          | mmap creates page table entries marked not-present; pages load on first access (page fault)                      |

---

### 🚨 Failure Modes & Diagnosis

**1. Out-of-Memory (OOM) Kill**

**Symptom:** Process suddenly killed; `dmesg` shows "oom-kill event"; no exception in application logs.

**Root Cause:** System ran out of physical RAM and swap. OOM killer selects a process to kill based on oom_score (typically the largest consumer).

**Diagnostic:**

```bash
dmesg | grep -i "oom\|killed process"
cat /proc/<PID>/status | grep VmRSS
free -h
```

**Fix:** Increase RAM or swap, reduce heap allocation, tune `vm.overcommit_memory`, or set `oom_score_adj=-1000` for critical processes.

**Prevention:** Set container memory limits (`docker run -m 512m`); monitor RSS with Prometheus `process_resident_memory_bytes`.

---

**2. TLB Thrashing (Page Table Walk Storms)**

**Symptom:** High `%sys` CPU in `perf stat`; `dTLB-load-misses` metric very high; large working sets with 4 KB pages.

**Root Cause:** Large working set exceeds TLB capacity (typically 1500–4000 entries); every access requires a slow page walk (~100 cycles each).

**Diagnostic:**

```bash
perf stat -e dTLB-loads,dTLB-load-misses,iTLB-loads \
    -p <PID> -- sleep 10
```

**Fix:** Enable Transparent Huge Pages (`echo always > /sys/kernel/mm/transparent_hugepage/enabled`) for large heap applications like JVMs and databases.

**Prevention:** JVM: add `-XX:+UseHugeTLBFS` or `-XX:+UseLargePages`. Configure huge pages: `echo 512 > /proc/sys/vm/nr_hugepages`.

---

**3. Swap Thrashing**

**Symptom:** System response becomes extremely slow; disk I/O spikes; `vmstat 1` shows high `si` (swap-in) and `so` (swap-out) values; page fault rate > 1000/sec.

**Root Cause:** Working set of active processes exceeds physical RAM; OS continuously swaps pages in and out. Each swap operation takes 1–10 ms (disk), turning normal RAM accesses (ns) into millisecond operations.

**Diagnostic:**

```bash
vmstat 1
# si > 0 = pages being swapped in
# so > 0 = pages being swapped out
sar -B 1 10  # pgfault/s and pgmajfault/s
```

**Fix:** Add RAM, reduce concurrent process count, use `cgroups` memory limits to prevent any single process from consuming all RAM.

**Prevention:** Monitor `node_vmstat_pgmajfault` in Prometheus; alert when major faults > 100/sec; set `vm.swappiness=10` to prefer keeping data in RAM.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — each process has its own virtual address space
- `User Space vs Kernel Space` — the kernel half of the virtual address space
- `Memory Management Models` — the broader context of manual vs. GC vs. virtual memory

**Builds On This (learn these next):**

- `Paging` — the mechanism that implements virtual memory in fixed-size pages
- `Page Fault` — what happens when a virtual page has no physical backing
- `TLB` — the cache that makes virtual-to-physical translation fast

**Alternatives / Comparisons:**

- `Segmentation` — the older, coarser memory protection model, superseded by paging
- `Memory-Mapped File (mmap)` — a use of virtual memory to map file contents into address space
- `NUMA` — extends virtual memory with topology-aware physical allocation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-process private address space backed  │
│              │ by RAM, disk, or files via page tables    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Physical addresses force programs to      │
│ SOLVES       │ coordinate; no isolation or overcommit    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Same virtual address = different physical │
│              │ location in each process — true isolation │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every modern OS process uses it  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Ultra-low-latency embedded: bare-metal    │
│              │ physical addressing eliminates TLB cost   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Isolation + overcommit vs TLB/page-fault  │
│              │ overhead                                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every process thinks it owns the         │
│              │  computer — the OS makes it so"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Paging → Page Fault → TLB                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Linux uses demand paging — a process can `malloc(100 GB)` on a 32 GB machine and succeed, as long as it doesn't actually touch all of it. This is called "overcommit." What are the precise conditions under which overcommit causes the OOM killer to activate, and what guarantees (if any) can a process rely on after a successful `malloc()`?

**Q2.** When `fork()` is called, Linux uses Copy-on-Write: parent and child share all physical pages until one of them writes. A process forks, and immediately the child calls `exec()` to replace itself with a new program. At what exact point do the parent's pages get copied, and how does this design make shell pipelines (`cmd1 | cmd2`) efficient even when `cmd1` produces gigabytes of output?
