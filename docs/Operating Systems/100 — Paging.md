---
layout: default
title: "Paging"
parent: "Operating Systems"
nav_order: 100
permalink: /operating-systems/paging/
number: "0100"
category: Operating Systems
difficulty: ★★☆
depends_on: Virtual Memory, User Space vs Kernel Space, Process
used_by: Page Fault, TLB, Swap / Thrashing, Buddy System / Slab Allocator
related: Page Fault, TLB, Segmentation
tags:
  - os
  - memory
  - internals
  - intermediate
  - paging
---

# 100 — Paging

⚡ TL;DR — Paging divides memory into fixed-size chunks (pages) so the OS can map any virtual page to any physical frame — enabling flexible, waste-free memory allocation.

| #0100           | Category: Operating Systems                                      | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, User Space vs Kernel Space, Process              |                 |
| **Used by:**    | Page Fault, TLB, Swap / Thrashing, Buddy System / Slab Allocator |                 |
| **Related:**    | Page Fault, TLB, Segmentation                                    |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Before paging, OSes used segmentation — memory was divided into variable-size segments (code, stack, heap). This caused **external fragmentation**: after allocating and freeing segments of different sizes, the free memory becomes a patchwork of small gaps. You might have 500 MB total free, but no single gap large enough for a 200 MB allocation. Compaction (shuffling processes around to merge gaps) is expensive — you can't move a running process's code without updating every pointer in it.

THE BREAKING POINT:
As systems ran more and longer-lived processes, fragmentation worsened over time. The "500 MB free but can't allocate 200 MB" problem caused allocation failures in production systems. Compaction could take seconds — unacceptable for interactive use.

THE INVENTION MOMENT:
This is exactly why Paging was created — fixed-size pages eliminate external fragmentation because any free page frame fits any page, and the page table handles the scattering transparently.

### 📘 Textbook Definition

**Paging** is a memory management scheme that divides both virtual memory and physical memory into fixed-size blocks called **pages** (virtual) and **frames** (physical), typically 4 KB on modern systems. The OS maintains a **page table** per process that maps each virtual page number to a physical frame number. Because all pages and frames are the same size, any free frame can hold any page — eliminating external fragmentation. Internal fragmentation (wasted space within the last page) is bounded to at most one page per allocation.

### ⏱️ Understand It in 30 Seconds

**One line:**
Memory is cut into equal-size tiles — any tile fits any slot, so nothing is ever wasted by gaps.

**One analogy:**

> A library has bookshelves with slots that all hold exactly one book. When you return a book, any empty slot anywhere in the library can take it — there's no "this slot is too small for a hardcover." The catalogue (page table) tracks which slot holds which book. A larger work (process) might be split across non-consecutive slots, but the catalogue knows where every part is.

**One insight:**
The genius of paging is that physical contiguity is no longer required. A process's code, stack, and heap can be scattered across RAM in any order — the page table makes them appear contiguous to the process. This is what allows the OS to pick up stray physical frames and use them, rather than needing a large contiguous free region.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Every page is the same size (4 KB standard; 2 MB huge pages). Every frame is the same size.
2. Any free frame can hold any page — no size mismatch possible (no external fragmentation).
3. The page table records the mapping; the hardware MMU performs the translation using it.

DERIVED DESIGN:
A virtual address is split into two fields: the high bits = page number (VPN), the low bits = offset within the page. The MMU looks up VPN in the page table to get the physical frame number (PFN), then appends the unchanged offset. Since the offset is preserved (only the high bits change), a 4 KB page needs 12 offset bits, meaning 52 bits for VPN on a 64-bit system — hence the multi-level page table structure to avoid storing 2^52 entries.

THE TRADE-OFFS:
Gain: No external fragmentation; any free frame usable anywhere; supports demand paging and swapping.
Cost: Internal fragmentation (last page partially used); page table itself uses memory (4-level table for a process can consume MBs); TLB pressure from many small pages.

### 🧪 Thought Experiment

SETUP:
100 MB RAM, three programs: A (30 MB), B (50 MB), C (15 MB). Program B exits, freeing 50 MB. New program D needs 40 MB.

WHAT HAPPENS WITHOUT paging (segmentation):

1. B's 50 MB region is freed as a single 50 MB gap.
2. D's 40 MB fits in the gap — allocate at B's old base address.
3. Now 10 MB remains free next to D, and 5 MB remains from C's gap.
4. New program E needs 14 MB: two 10 MB and 5 MB fragments exist but neither fits 14 MB → allocation fails despite 15 MB free.

WHAT HAPPENS WITH paging:

1. B's pages are freed individually — 12,800 frames returned to the free list.
2. D requests 10,240 frames — OS picks any 10,240 free frames from anywhere.
3. D's pages are mapped through the page table; D sees a contiguous virtual address space.
4. E requests 3,584 frames — picks from remaining 2,560 frames. Still works.

THE INSIGHT:
With paging, "free memory" is a pool of interchangeable tiles. Fragmentation becomes an internal property of individual allocations, bounded to < 1 page per allocation — not an external property of the entire heap.

### 🧠 Mental Model / Analogy

> Paging is like a parking lot with identically sized spaces. Any car fits any space. The attendant (OS page table) keeps a log of which car is in which space. A truck (large process) occupies multiple spaces, and the log tracks all of them. Contrast with a valet lot that tries to park cars in order — when a van leaves, the gap is too small for a bus.

"Parking space" → physical frame
"Car" → virtual page
"Attendant's log" → page table
"Car at a different space than where it was last time" → page migration during defragmentation

Where this analogy breaks down: Physical frames are not truly interchangeable for performance — NUMA systems have local (fast) and remote (slow) frames; the allocator tries to place pages on the nearest NUMA node.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The OS divides memory into equal-sized pieces (4 KB "pages"). When your program needs memory, the OS gives it some pieces — they don't have to be next to each other. Your program sees them as if they were one big contiguous block, thanks to the page table.

**Level 2 — How to use it (junior developer):**
You don't manage paging directly — `malloc()` and the JVM heap allocator do it. But you care when: allocating huge buffers (consider huge pages to reduce TLB pressure), using memory-mapped files (`mmap()` maps at page granularity), or when a process's RSS (Resident Set Size) grows unexpectedly — each mapped file or anonymous mapping starts on a page boundary.

**Level 3 — How it works (mid-level engineer):**
x86-64 uses a 4-level page table: PGD (Page Global Directory) → PUD → PMD → PTE. Each level is a 4 KB page with 512 entries of 8 bytes each. The physical address = PFN (from PTE) << 12 | offset (low 12 bits of virtual address). PTEs contain: PFN (40 bits), Present bit, Writable bit, User/Supervisor bit, Accessed bit, Dirty bit, NX (no-execute) bit. Linux represents each mapping as a VMA (Virtual Memory Area) in the process's `mm_struct`, before allocating physical pages on demand.

**Level 4 — Why it was designed this way (senior/staff):**
The 4-level page table structure is a compromise between depth (more levels = less wasted memory for sparse spaces) and walk cost (fewer levels = faster translation). A flat page table for 64-bit addressing would need 2^52 × 8 bytes = 32 PB — absurd. The 4-level tree stores only the path to actually-mapped pages. Huge pages (2 MB via PMD, 1 GB via PUD) skip lower levels entirely, both reducing page table memory and allowing the TLB to cover 512× more memory per entry. The tradeoff: huge pages cannot be partially swapped out — you must swap or keep the full 2 MB.

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           PAGE TABLE WALK (4-level, x86-64)             │
├─────────────────────────────────────────────────────────┤
│  Virtual Address: 48 bits total                         │
│  [47:39] PGD idx [38:30] PUD idx [29:21] PMD idx        │
│  [20:12] PTE idx [11:0]  byte offset within page        │
│                                                         │
│  CR3 → PGD[idx] → PUD[idx] → PMD[idx] → PTE[idx]       │
│                                              ↓           │
│                                         PFN << 12       │
│                                         + offset        │
│                                         = Physical Addr │
└─────────────────────────────────────────────────────────┘
```

**Step 1:** MMU splits virtual address into 5 parts (4 indices + offset).

**Step 2:** MMU reads PGD entry at `CR3 + PGD_index * 8`. If not present → page fault.

**Step 3:** Follow the chain through PUD, PMD, PTE. Each level may trigger a page fault if not present.

**Step 4:** PTE contains the PFN. Physical address = `(PFN << 12) | offset`.

**Step 5:** Access the physical address. Update Accessed/Dirty bits in PTE.

**Huge page shortcut:** If PMD entry has the huge-page bit set, translation stops at PMD level — no PTE needed. The offset is now 21 bits (2 MB pages).

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[Process accesses virtual address 0x7f3a_1234]
   → [MMU: TLB lookup — miss]
   → [MMU: page table walk ← YOU ARE HERE]
   → [PTE found: PFN=0x4AB, Present=1]
   → [Physical address = 0x4AB_000 | 0x234 = 0x4AB234]
   → [Cache lookup → RAM access → data returned]
```

FAILURE PATH:
[PTE.Present = 0] → [CPU: Page Fault #PF] → [OS page fault handler] → [Allocate frame, fill from swap/file/zero, set PTE.Present=1, resume]

WHAT CHANGES AT SCALE:
At 1 TB of mapped memory, a process has ~256 million PTEs consuming ~2 GB of page table memory. Linux's `khugepaged` daemon opportunistically collapses 4 KB pages into 2 MB huge pages to reduce this overhead. Database servers (PostgreSQL, MySQL) configure huge pages manually (`vm.nr_hugepages`) to avoid TLB misses on large buffer pools.

### ⚖️ Comparison Table

| Scheme            | External Frag          | Internal Frag | Flexible? | Best For                  |
| ----------------- | ---------------------- | ------------- | --------- | ------------------------- |
| **Paging (4 KB)** | None                   | < 4 KB/alloc  | Very high | General-purpose OS        |
| Huge Pages (2 MB) | None                   | < 2 MB/alloc  | High      | Large memory servers, DBs |
| Segmentation      | High over time         | None          | Medium    | Legacy x86, protection    |
| Slab Allocator    | None (built on paging) | Minimal       | High      | Kernel object allocation  |

How to choose: Use default 4 KB paging for most workloads. Enable huge pages (THP or explicit) for applications with > 4 GB working sets to cut TLB miss rate.

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                   |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "Paging eliminates all fragmentation"   | Paging eliminates external fragmentation; internal fragmentation (up to 4 KB per allocation) still exists |
| "A page and a frame are the same thing" | Pages are virtual; frames are physical. The page table maps one to the other                              |
| "Larger pages always perform better"    | Huge pages reduce TLB misses but can't be partially swapped and waste memory for small allocations        |
| "Page table walks are done in software" | On x86-64, the MMU does the page table walk in hardware; OS only intervenes on page fault (PTE missing)   |
| "malloc() allocates at page boundaries" | malloc() sub-allocates within pages; the kernel only allocates full pages to processes                    |

### 🚨 Failure Modes & Diagnosis

**1. Page Table Memory Exhaustion**

Symptom: System OOM despite application RSS appearing reasonable; `cat /proc/meminfo` shows high `PageTables` entry.

Root Cause: Process maps thousands of small anonymous regions (e.g., Java's `mmap` per class file, or many `dlopen()` calls), each requiring its own PTE chain; page table overhead exceeds heap overhead.

Diagnostic:

```bash
cat /proc/meminfo | grep PageTables
cat /proc/<PID>/status | grep VmPTE
pmap -x <PID> | wc -l  # count VMAs
```

Fix: Consolidate memory mappings; use `madvise(MADV_HUGEPAGE)` on large regions to merge PTEs. In Java, use `-XX:+UseTransparentHugePages`.

Prevention: Monitor `node_memory_PageTables_bytes` in Prometheus; alert when > 5% of total RAM.

---

**2. Internal Fragmentation from Small Allocations**

Symptom: `malloc(1)` called millions of times; process RSS is much higher than the sum of requested bytes.

Root Cause: Each `malloc(1)` is served from the heap, but the heap itself expands in page-granularity. A malloc library object header (8–16 bytes) + 1 byte payload still occupies at minimum a page's internal slot.

Diagnostic:

```bash
valgrind --tool=massif ./myapp
ms_print massif.out.<pid>
```

Fix: Batch small allocations into pools or use a slab allocator for fixed-size objects. In C++, use object pools or `std::pmr::monotonic_buffer_resource`.

Prevention: Profile memory with `massif`/`heaptrack` before scaling.

---

**3. TLB Invalidation Storms on Fork**

Symptom: `fork()`-heavy servers (pre-fork web servers like Apache) show high `%sys` under load; `perf stat` shows TLB flushes.

Root Cause: Every `fork()` requires a TLB flush on the new process (new CR3 loaded). On systems without ASID (Address Space ID), every context switch also flushes the TLB, discarding cached translations.

Diagnostic:

```bash
perf stat -e tlb:tlb_flush -p <PID> -- sleep 5
```

Fix: Use thread-per-request (shared address space, no TLB flush on switch) or `io_uring`-based event loop to reduce fork rate. On x86-64, PCIDs (Process-Context IDs) tag TLB entries, allowing partial TLB retention across context switches — ensure kernel >= 4.14 to use them.

Prevention: Prefer event-driven (Node.js/Netty style) over pre-fork multi-process architectures for latency-sensitive services.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — paging is the mechanism that implements the virtual memory abstraction
- `Process` — each process has its own page table

**Builds On This (learn these next):**

- `Page Fault` — triggered when a virtual page has no physical frame mapped
- `TLB (Translation Lookaside Buffer)` — the cache that makes repeated page table lookups fast
- `Swap / Thrashing` — paging to disk when physical RAM is exhausted

**Alternatives / Comparisons:**

- `Segmentation` — the alternative memory scheme with variable-size regions; prone to external fragmentation
- `Huge Pages` — a variant using 2 MB or 1 GB pages to reduce TLB pressure

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fixed-size (4 KB) memory chunks mapped    │
│              │ from virtual pages to physical frames     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Variable-size segments cause external     │
│ SOLVES       │ fragmentation; paging eliminates it       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Physical contiguity is no longer needed   │
│              │ — page table hides the scatter            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — foundation of all modern OS      │
│              │ memory management                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Use huge pages (2 MB) for large RAM       │
│              │ consumers to cut TLB miss rate            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No ext. fragmentation vs internal frag    │
│              │ + page table memory overhead              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Equal-size tiles mean any free space     │
│              │  fits any need"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Page Fault → TLB → Huge Pages             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Linux's Transparent Huge Pages (THP) automatically collapses groups of 4 KB pages into 2 MB huge pages when possible. Database vendors like MongoDB and Redis explicitly recommend _disabling_ THP. Given what you know about paging internals, what specific behaviour of THP causes performance problems for databases — and why doesn't the same problem affect a general-purpose application server?

**Q2.** A process calls `fork()`, and both parent and child run for an hour, each modifying different parts of a 10 GB in-memory dataset using Copy-on-Write. How much total physical RAM could this scenario consume compared to running a single process — and what determines the worst-case memory usage?
