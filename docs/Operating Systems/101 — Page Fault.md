---
layout: default
title: "Page Fault"
parent: "Operating Systems"
nav_order: 101
permalink: /operating-systems/page-fault/
number: "0101"
category: Operating Systems
difficulty: ★★☆
depends_on: Paging, Virtual Memory, User Space vs Kernel Space
used_by: TLB, Swap / Thrashing, Memory-Mapped File (mmap)
related: TLB, Swap / Thrashing, Segmentation Fault
tags:
  - os
  - memory
  - internals
  - intermediate
  - paging
---

# 101 — Page Fault

⚡ TL;DR — A page fault is the CPU's signal to the OS that a memory access hit a virtual page with no physical backing — the OS either loads it or kills the process.

| #0101           | Category: Operating Systems                        | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Paging, Virtual Memory, User Space vs Kernel Space |                 |
| **Used by:**    | TLB, Swap / Thrashing, Memory-Mapped File (mmap)   |                 |
| **Related:**    | TLB, Swap / Thrashing, Segmentation Fault          |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Without page faults, the OS would have to load a program's entire memory into RAM before allowing it to execute. A program that uses 8 GB of data structures must have all 8 GB in physical RAM even if the program only accesses 500 MB during a typical run. This wastes memory and makes startup slow. Worse, you couldn't run programs larger than physical RAM at all.

THE BREAKING POINT:
Mainframes in the 1960s faced this exact problem. Programmers had to manually manage overlays — loading and unloading segments of code from disk manually, a tedious and error-prone process.

THE INVENTION MOMENT:
This is exactly why the Page Fault mechanism was created — it allows the OS to load pages lazily, on demand, only when a process actually accesses them. Programs start instantly, memory is allocated only when used, and processes larger than RAM become possible.

### 📘 Textbook Definition

A **page fault** is a hardware exception raised by the CPU's MMU when a process accesses a virtual address whose page table entry (PTE) has the Present bit cleared. The CPU saves the faulting address in the CR2 register, transfers control to the OS page fault handler, and suspends the faulting process. The handler determines the fault type, takes the appropriate action (allocate a physical page, load from swap or file, or send SIGSEGV), updates the page table entry, and resumes the process. There are three types: minor faults (page exists but not mapped yet), major faults (page must be read from disk), and invalid faults (illegal address → SIGSEGV).

### ⏱️ Understand It in 30 Seconds

**One line:**
A page fault is a "please load this page now" interrupt — the OS pauses your program and fills in the missing memory.

**One analogy:**

> You're reading a book but page 247 is missing — it was never printed in your copy. You call the librarian (page fault handler). The librarian finds the page in the archive (swap disk or file), prints a copy, inserts it in your book, and says "continue reading from page 247." If page 247 doesn't exist in any archive (invalid address), the librarian tears your library card up (SIGSEGV).

**One insight:**
Most page faults are minor and invisible — they are the normal mechanism by which the OS delivers pages on first access (demand paging). An application that starts and runs flawlessly is generating thousands of minor page faults during startup; you just never notice because each takes < 1 microsecond. It's major page faults (disk reads) that matter for performance.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. A page fault happens when PTE.Present = 0, regardless of reason.
2. The OS — not the CPU — decides what "not present" means: lazy allocation, swapped out, file-backed, or illegal access.
3. After the fault is handled successfully, the CPU retries the faulting instruction from the beginning.

DERIVED DESIGN:
The CPU cannot distinguish "this page is swapped out" from "this address is completely invalid" — both have Present=0. The OS must decide. Linux's `do_page_fault()` handler looks up the faulting address in the process's VMA (Virtual Memory Area) list. If a VMA covers the address: it's a handleable fault — allocate a page (minor) or read from swap/file (major). If no VMA covers the address: it's an invalid access → SIGSEGV.

THE TRADE-OFFS:
Gain: Demand paging (lazy allocation), programs larger than RAM, fast startup, memory overcommit.
Cost: Major faults add 1–10 ms latency (disk read); first-access page faults add 1–10 µs (minor). Latency-sensitive apps must pre-fault pages with `mlock()` to avoid runtime faults.

### 🧪 Thought Experiment

SETUP:
A Java process with a 4 GB heap. It allocates a 1 GB byte array: `byte[] data = new byte[1_000_000_000]`.

WHAT HAPPENS WITHOUT page fault (eager allocation):

1. OS must immediately find 250,000 physical pages (4 KB each) for the 1 GB array.
2. All 1 GB is reserved and zeroed before the allocation returns.
3. If 1 GB RAM is not available immediately → allocation fails even if the array will only use 10 MB.
4. JVM startup takes longer as heap is faulted in eagerly.

WHAT HAPPENS WITH page fault (demand paging):

1. OS creates a VMA entry for 1 GB of address space — no physical pages allocated.
2. `new byte[1_000_000_000]` returns instantly.
3. As Java code accesses `data[0]`, `data[4096]`, etc., minor page faults trigger.
4. Each fault allocates one zero page (~1 µs). Only pages actually accessed consume RAM.
5. If only 10 MB is accessed, only ~2,500 physical pages are ever used.

THE INSIGHT:
Page faults turn memory allocation from an eager, physical operation into a lazy, virtual contract. "Allocating" memory is just making a promise; the OS only pays with real RAM when the process collects on the promise.

### 🧠 Mental Model / Analogy

> A page fault is an on-demand printing system. A book exists as a master template (disk/swap). Your personal copy only prints pages when you actually open to them. The first time you turn to a page, the printer fires up (minor/major fault). If you reference a page number that doesn't exist in the book at all, you get an error.

"Turning to a page" → accessing a virtual address
"Printing a new page" → minor fault — OS allocates a zero page
"Fetching from archive" → major fault — OS reads page from swap or file
"Page number doesn't exist" → invalid fault → SIGSEGV

Where this analogy breaks down: Unlike printing, a major page fault can be eliminated by pre-loading ("prefaulting") — `mlock()` pre-prints all pages before runtime access.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your program touches a part of memory that hasn't been physically loaded yet, the computer automatically pauses your program, loads that memory piece into RAM, and resumes. You don't notice this happening — it's automatic and usually very fast.

**Level 2 — How to use it (junior developer):**
Most developers interact with page faults through two symptoms: (1) an unexpected `SIGSEGV` crash (invalid fault — you dereferenced a null or freed pointer), and (2) slow startup of JVMs or large processes (major faults loading from disk). Use `mlock()` or `mlockall()` to pre-fault pages for latency-critical code (real-time audio, trading systems). Check fault rates with `/usr/bin/time -v ./myapp` or `perf stat`.

**Level 3 — How it works (mid-level engineer):**
When a page fault occurs, the CPU saves `RIP` (instruction pointer), sets CR2 to the faulting address, and vectors to `do_page_fault()` in the kernel. The handler calls `find_vma()` to locate the VMA for the faulting address. For anonymous memory: `handle_mm_fault()` → `do_anonymous_page()` allocates a zero page from the page allocator and installs it in the PTE. For file-backed pages: `do_fault()` calls the VMA's `fault()` method, which reads the page from the filesystem's page cache (a minor fault if cached, major fault if not). Copy-on-write faults: the faulting process gets its own copy of a shared page.

**Level 4 — Why it was designed this way (senior/staff):**
The fault-and-retry design (CPU retries the faulting instruction after handling) was chosen over alternatives like interrupt-driven prefetch because it requires no compiler support — any instruction can trigger a fault. This is why demand paging is transparent to user code. The cost is that faults are synchronous and expensive on the critical path. Modern alternatives: `userfaultfd` allows user-space to handle page faults (useful for live migration, checkpoint/restore — CRIU uses it). `io_uring`'s `IORING_REGISTER_PBUFFERS` pre-registers buffers to avoid fault-on-first-access latency in I/O paths. Trading systems use `mlock()` + huge pages + `MADV_POPULATE_WRITE` (Linux 5.14) to eliminate all fault latency from the hot path.

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│               PAGE FAULT HANDLING FLOW                  │
├─────────────────────────────────────────────────────────┤
│  CPU: access 0x7f3a_1234 → PTE.Present=0               │
│       → #PF exception raised                            │
│       → CR2 = 0x7f3a_1234                               │
│       → jump to do_page_fault()                         │
│                    ↓                                    │
│  Kernel: find_vma(0x7f3a_1234)                          │
│          ├─ VMA found?                                  │
│          │   ├─ Anonymous page → alloc zero page        │
│          │   ├─ File-backed → load from page cache      │
│          │   └─ COW page → copy + map                   │
│          └─ No VMA → SIGSEGV → process killed           │
│                    ↓ (if handled)                       │
│  PTE updated: Present=1, PFN set                        │
│  Process resumed at faulting instruction (retried)      │
└─────────────────────────────────────────────────────────┘
```

**Minor fault path:** Page is in the page cache (RAM) but not mapped in this process's page table. Kernel just installs the PTE. ~1 µs.

**Major fault path:** Page is not in RAM — must be read from disk (swap or file). Kernel issues I/O, blocks the process, resumes when I/O completes. ~1–10 ms.

**Invalid fault path:** No VMA covers the address. Kernel sends SIGSEGV. ~1 µs, but fatal.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[Process: first access to malloc'd address]
   → [MMU: TLB miss → page walk → PTE.Present=0]
   → [#PF exception ← YOU ARE HERE]
   → [OS: find_vma → anonymous → alloc zero page]
   → [PTE installed: Present=1]
   → [Process retries instruction → success]
```

FAILURE PATH (major):
[Access to swapped-out page] → [#PF] → [OS: read from swap device] → [I/O waits 5ms] → [Page loaded] → [PTE installed] → [Process resumes 5ms late]

WHAT CHANGES AT SCALE:
A JVM starting with a 32 GB heap on a cold machine triggers 8 million minor page faults — visible as a 2–5 second pause before the first request is served. Production JVMs use `-XX:+AlwaysPreTouch` to pre-fault all heap pages at startup, eliminating runtime fault latency at the cost of longer startup. At 10K containers starting simultaneously on a host, page fault storms can saturate the kernel's page allocator lock.

### ⚖️ Comparison Table

| Fault Type        | Trigger                  | Latency | Action                  | User Impact   |
| ----------------- | ------------------------ | ------- | ----------------------- | ------------- |
| **Minor fault**   | Page in RAM, not mapped  | ~1 µs   | Install PTE             | Invisible     |
| **Major fault**   | Page on disk (swap/file) | 1–10 ms | Disk I/O + install PTE  | Latency spike |
| **COW fault**     | Write to shared page     | ~2 µs   | Copy page + install PTE | Invisible     |
| **Invalid fault** | No VMA covers address    | ~1 µs   | Send SIGSEGV            | Process crash |

How to choose: You don't choose fault types — the OS determines them. Optimise by: using `mlock()` to prevent major faults, huge pages to reduce minor fault frequency, and `madvise(MADV_WILLNEED)` to trigger prefetch.

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                          |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| "Page faults always mean something is wrong"     | Minor faults are normal — every first memory access causes one. They're a feature, not a bug                                     |
| "A segfault and a page fault are the same thing" | A segfault (SIGSEGV) is the result of an unhandleable page fault (invalid address); a minor/major page fault is handled silently |
| "Major page faults only happen on the first run" | Major faults recur whenever a page is evicted from RAM to swap — under memory pressure this happens constantly                   |
| "mlock() prevents page faults forever"           | mlock() prevents the OS from evicting locked pages; it doesn't prevent COW faults or initial minor faults                        |
| "More RAM = no page faults"                      | Minor faults still occur for first-access demand paging even with infinite RAM                                                   |

### 🚨 Failure Modes & Diagnosis

**1. Major Fault Storm (Swap Thrashing)**

Symptom: Application latency spikes to hundreds of milliseconds; `vmstat 1` shows high `majflt` and `pgmajfault`; disk I/O spikes on the swap device.

Root Cause: Working set larger than available RAM; pages being evicted and re-loaded continuously.

Diagnostic:

```bash
vmstat 1 5
# Look for: majflt > 0 (per-process), pgmajfault > 0 (system)
perf stat -e major-faults -p <PID> -- sleep 5
```

Fix: Increase RAM, reduce memory footprint, add swap on faster storage (NVMe), or use `cgroups` to limit competing processes.

Prevention: Monitor `node_vmstat_pgmajfault` in Prometheus; alert on > 10/sec in production.

---

**2. JVM Startup Latency from Minor Faults**

Symptom: Spring Boot app takes 30+ seconds to serve first request; `perf stat` shows millions of minor faults during startup.

Root Cause: Large JVM heap allocated but not touched during startup; first requests trigger millions of demand-paging faults.

Diagnostic:

```bash
/usr/bin/time -v java -jar app.jar 2>&1 | grep "Page faults"
# Or
perf stat -e minor-faults java -jar app.jar
```

Fix:

```bash
# BAD: default heap (demand paging on first access)
java -Xmx8g -jar app.jar

# GOOD: pre-touch all heap pages at startup
java -Xmx8g -XX:+AlwaysPreTouch -jar app.jar
# Slower startup, but zero fault latency at runtime
```

Prevention: Use container readiness probes to delay traffic until warmup completes.

---

**3. userfaultfd Page Fault Handling Latency**

Symptom: CRIU restore or VM live migration takes unexpectedly long; process appears to start but hangs on memory access.

Root Cause: `userfaultfd` handler in user space is too slow to service faults; faulting thread blocks waiting for the handler to deliver a page.

Diagnostic:

```bash
# Monitor userfaultfd events
cat /proc/<PID>/fdinfo/<fd_num>
# Or trace with ftrace
echo 1 > /sys/kernel/debug/tracing/events/mm/mm_userfaultfd_handler_enabled
```

Fix: Optimise the userfaultfd handler to use larger batch transfers and minimise locking. Pre-populate critical regions with `UFFDIO_COPY` before the process accesses them.

Prevention: Benchmark userfaultfd handler throughput vs required fault-handling rate before relying on it in latency-sensitive paths.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Paging` — page faults are the runtime event that demand paging triggers
- `Virtual Memory` — the abstraction that makes demand paging possible
- `Swap / Thrashing` — the severe consequence of too many major page faults

**Builds On This (learn these next):**

- `TLB` — a TLB miss precedes every page fault; the TLB is filled after the fault is handled
- `Memory-Mapped File (mmap)` — file-backed pages use page faults as their loading mechanism
- `Buddy System / Slab Allocator` — the kernel allocator that provides physical pages to satisfy faults

**Alternatives / Comparisons:**

- `mlock()` — prevents pages from being evicted, eliminating major faults at the cost of locked memory
- `madvise(MADV_WILLNEED)` — hints to the OS to prefetch pages before they are needed
- `io_uring IORING_REGISTER_PBUFFERS` — pre-registers I/O buffers to avoid fault overhead in I/O paths

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CPU exception when a virtual page has no  │
│              │ physical backing (PTE.Present = 0)        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without it, all pages must be loaded      │
│ SOLVES       │ eagerly — wasting RAM and time            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Minor faults (~1µs) are normal/expected;  │
│              │ major faults (~5ms) are the problem       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Default: always. Use mlock() to disable   │
│              │ for latency-critical hot paths            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Real-time systems: pre-fault all memory   │
│              │ before the deadline window                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lazy allocation efficiency vs occasional  │
│              │ latency spikes on first access            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The OS printing a page only when you     │
│              │  actually turn to it"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TLB → Swap/Thrashing → mlock()            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A high-frequency trading system uses `mlock()`ed huge pages to eliminate page fault latency from its hot path. During a market stress event, memory usage spikes and the OS cannot evict the locked pages to accommodate other processes. Trace step-by-step what happens: which processes are affected, in what order, and what the OOM killer's decision algorithm considers when choosing a victim.

**Q2.** `userfaultfd` allows a user-space process to handle page faults for another process's memory region. CRIU (Checkpoint/Restore In Userspace) uses this for live migration. Compared to the kernel's built-in page fault handling, what are the latency and throughput limits of user-space fault handling, and under what conditions would a live migration using userfaultfd fail to complete before the application's timeout?
