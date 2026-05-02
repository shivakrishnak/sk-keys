---
layout: default
title: "Swap — Thrashing"
parent: "Operating Systems"
nav_order: 124
permalink: /operating-systems/swap-thrashing/
number: "0124"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, Paging, Page Fault, TLB
used_by: Memory Management, Container Resource Limits, Performance Tuning
related: OOM Killer, Huge Pages, mlock, cgroups memory.limit
tags:
  - os
  - memory-management
  - linux
  - performance
---

# 124 — Swap — Thrashing

⚡ TL;DR — Swap extends RAM to disk for rarely-used pages; thrashing is when processes spend more time swapping pages in/out than executing — the system grinds to a halt.

| #0124           | Category: Operating Systems                                      | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, Paging, Page Fault, TLB                          |                 |
| **Used by:**    | Memory Management, Container Resource Limits, Performance Tuning |                 |
| **Related:**    | OOM Killer, Huge Pages, mlock, cgroups memory.limit              |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
RAM is finite. If a process needs 4GB but only 2GB of RAM is free, the only option is to kill the process. Systems in the 1970s with 256KB of RAM could run programs of 1MB — only because they used virtual memory + swap to page program segments from disk on demand.

THE BREAKING POINT:
Swap solves the "not enough RAM" problem by using disk space as an overflow. But it introduces a new failure mode: if the total working set of all active processes exceeds physical RAM, the OS must constantly swap pages between RAM and disk. Each swap-in evicts another needed page (swap-out). That page is soon needed again. The OS spends 100% of time in page fault handling — essentially no useful work is done. This is thrashing.

THE INVENTION MOMENT:
Peter Denning's 1968 "working set" model showed that thrashing occurs when the sum of working sets exceeds physical memory, and introduced the solution: working set policy — only keep processes whose working sets fit in memory; swap out (suspend) entire processes that can't fit.

### 📘 Textbook Definition

**Swap space** is disk space designated to hold memory pages that are evicted from RAM by the OS virtual memory manager. When physical memory is insufficient, the **page frame reclaim algorithm (PFRA)** (Linux: via `kswapd` daemon) identifies candidate pages to evict: anonymous pages (heap, stack) are written to swap; file-backed pages are simply evicted (they can be re-read from the file). When an evicted page is accessed, a **page fault** occurs, the page is read back from swap (swap-in), and another page may be evicted (swap-out).

**Thrashing** is a condition in which a system spends the majority of its time servicing page faults, resulting in negligible useful work. Thrashing occurs when the combined **working set** (set of recently-used pages) of all active processes exceeds physical memory. The system is simultaneously paging in and out continuously, with CPU utilization at 100% but effective throughput near zero.

### ⏱️ Understand It in 30 Seconds

**One line:**
Swap = overflow RAM to disk (slow, but workable); thrashing = so much swapping that the system stops doing real work.

**One analogy:**

> A restaurant kitchen with 10 active dishes. The chef can only hold 5 plates at a time. Swap is: store the other 5 plates on a shelf (slow to reach). Thrashing is: the shelf and counter are so busy being shuffled — put plate A on shelf, bring plate B to counter, put B back, bring A again — that no actual cooking happens. Everyone is moving plates but zero meals are being prepared.

**One insight:**
Thrashing is self-reinforcing: each page fault blocks a process (waiting for disk I/O) → CPU switch to another process → another page fault → all processes are blocked on page I/O → CPU spins servicing faults → zero useful throughput despite 100% CPU. Breaking out requires either reducing working set size or adding RAM.

### 🔩 First Principles Explanation

LINUX MEMORY PRESSURE:

```
Memory zones:  [Free] [Active] [Inactive] [Swap cache]

kswapd (background): continuously monitors free pages
  If free < low_watermark:
    Move Inactive pages → swap cache (mark for eviction)
    Evict swap cache → free pages

  Page eviction order:
    1. File-backed inactive pages (just drop; re-read from disk on fault)
    2. Anonymous inactive pages (write to swap partition; re-read on fault)
    3. File-backed active pages (demote to inactive first)
    4. Anonymous active pages (demote; if still needed → swap)
```

SWAP SUBSYSTEM:

```
Process accesses swapped-out page (virtual address X):
  → Page fault (not-present)
  → Kernel: page table entry has swap offset (not physical frame)
  → block_read(swap_device, offset) → read 4KB page
  → Allocate new physical frame
  → Copy page from swap into frame
  → Update PTE: virtual X → physical frame
  → Evict some other page (if memory still low)
  → Return to user process

Latency: ~10ms (SSD) to ~100ms (HDD) per swap-in
vs L3 cache hit: ~10ns
vs RAM: ~100ns
Swap is 5–6 orders of magnitude slower than RAM
```

THRASHING DETECTION:

```
Metric: CPU busy % vs useful work %
Normal: CPU 70% busy → 70% executing instructions
Thrashing: CPU 98% busy → 2% executing instructions, 96% handling page faults

Linux: /proc/vmstat
  pswpin  (pages swapped in per second)  > 1000 → severe swap
  pgscan_kswapd (pages scanned by kswapd) spikes → memory pressure
  pgmajfault (major page faults) spikes → pages being read from swap
```

THE TRADE-OFFS:
Gain: System remains functional under moderate overcommit; processes don't OOM on occasional memory spikes.
Cost: Swap-in latency is 5–6 orders of magnitude higher than RAM; under overcommit, swap can make the system worse (thrashing) compared to just killing processes (OOM killer).

### 🧪 Thought Experiment

KUBERNETES CONTAINER SWAP DEBATE:
A container with `memory: limit: 2Gi` allocates 2.5GB. Without swap: kernel OOM killer kills the container. With swap enabled on the node: the extra 512MB goes to swap (SSD). The container continues with degraded performance.

Which is better?

- **OOM kill**: container crashes → Kubernetes restarts it → clean state in seconds.
- **Swap overflow**: container continues but at degraded performance for the duration of the load spike. If the spike is transient (5s), swap is better. If the spike is sustained (hours), thrashing is worse than a restart.

This is why Kubernetes historically recommended `vm.swappiness=0` (disable swap): container restarts are clean and fast; thrashing is unpredictable and hard to debug. Kubernetes 1.28+ adds swap support (opt-in) with `LimitedSwap` policy for exactly this reason — but only for cgroup v2 where swap limits are enforceable per-container.

### 🧠 Mental Model / Analogy

> Physical RAM = your desk. Swap = filing cabinet (slow, across the room). Your working set = the documents you need right now. Normal work: desk holds everything you need; filing cabinet rarely accessed. Memory pressure: some documents go to filing cabinet. Thrashing: desk is so small that every time you pick up Document A, you have to return Documents B and C to the cabinet; but B and C are needed immediately after A — so you're constantly walking to and from the cabinet. Actual document-reading time: 5% of your day.

> Fix: bigger desk (more RAM), fewer simultaneous projects (fewer processes), or park a whole project in a drawer (swap out entire process — working set model).

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a computer runs out of RAM, it moves less-used parts of programs to disk (swap). It works but is slow. If the computer is constantly moving stuff to disk and back, it's "thrashing" — spending all its time on the moving instead of the actual work.

**Level 2 — How to use it (junior developer):**
Monitor: `free -h` (swap usage), `vmstat 1` (si/so columns = swap-in/swap-out pages/second), `iotop` (see swap I/O). For Java: disable swap for JVM processes if possible (`mlockall` or `-XX:+AlwaysPreTouch`) — JVM pause times explode when heap pages are swapped. For containers: `--memory-swap=<value>` controls swap (set equal to `--memory` to disable swap for that container). Linux tuning: `vm.swappiness=10` (lean toward not swapping) vs `vm.swappiness=60` (default, aggressive swap). `vm.swappiness=0` = avoid swap entirely (swap only under extreme pressure).

**Level 3 — How it works (mid-level engineer):**
`kswapd` is a kernel thread per NUMA node. Wakes when free pages fall below `pages_low` watermark. Scans LRU lists: active/inactive anon (heap/stack pages) and active/inactive file (page-cache pages). Uses clock algorithm: pages are "referenced" on access, "aged" (moved to inactive) on each pass. Anonymous pages below working set size stay resident; those not accessed in `vm.min_free_kbytes` reclaim cycles are written to swap. `swapd` (synchronous page reclaim) is triggered when `kswapd` can't keep up — direct reclaim from the allocating process's context, which causes allocation latency.

**Level 4 — Why it was designed this way (senior/staff):**
Peter Denning's working set model (1968): process's working set W(t, Δ) = set of pages referenced in the last Δ time units. Optimal: only schedule processes whose working sets fit in memory. Linux's approximation: LRU-based active/inactive lists. The fundamental tension: LRU is Belady's "furthest in future" approximation; clock algorithm approximates LRU with single reference bit. Linux 5.2+ introduced `MGLRU` (Multi-Generational LRU): tracks page age across 4 generations rather than 2 (active/inactive), giving better reclaim decisions under adversarial workloads. The research insight (Alibaba, Google, Meta): traditional LRU severely misranks pages for mixed workloads; MGLRU reduces page reclaim cost by 40% in production.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           LINUX MEMORY PRESSURE RESPONSE               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [Physical RAM]                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ Free         │ File cache (evictable)        │      │
│  │ pages        │ Active anon │ Inactive anon   │      │
│  └──────────────┴─────────────┴─────────────────┘      │
│                                      │                 │
│  kswapd wakes:                        │                 │
│    Scan inactive anon → swap out ────►│ SWAP DEVICE     │
│    Scan inactive file → evict         │ (SSD/HDD)       │
│    Promote active → inactive          │                 │
│                                       │                 │
│  Process page fault:                  │                 │
│    swap entry in PTE → swap in ◄─────►│                 │
│    Allocates new frame                │                 │
│    Evicts another if needed ─────────►│                 │
│                                                        │
│  THRASHING: all processes stuck in page fault           │
│    CPU: 0% user, 0% kernel, 100% iowait               │
│    vmstat: si/so both 10000+ pages/sec                 │
│    Resolution: add RAM, reduce RSS, restart processes  │
└────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

JAVA HEAP SWAPPED OUT (worst case):

```
1. System memory 95% used; kswapd starts swapping Java heap pages

2. GC triggers: needs to scan entire heap (e.g., G1 full GC)
   → Must access all heap pages
   → 70% of heap pages are on swap (SSD: 0.1ms per page fault)
   → 2GB heap with 1.4GB swapped: 350,000 page faults × 0.1ms = 35 seconds

3. GC "stop-the-world" pause: 35 seconds
   → Application completely unresponsive for 35s
   → Kubernetes liveness probe times out → container killed → restart
   → Log: "GC overhead limit exceeded" or just silence then OOM kill

4. Prevention:
   a. mlock/mlockall: lock JVM pages in RAM (prevents swap of JVM)
   b. -XX:+AlwaysPreTouch: pre-fault all heap pages at JVM start
      (forces OS to allocate physical pages immediately, preventing later lazy swap)
   c. Container --memory-swap=<limit>: explicit swap limit
   d. vm.swappiness=0 on the node
```

### 💻 Code Example

Example 1 — Monitor swap activity (Linux):

```bash
# Real-time swap monitoring
vmstat 1 10   # si=swap-in, so=swap-out (KB/s); sustained > 100 = pressure

# Detailed: which processes are swapping?
for pid in /proc/[0-9]*; do
    comm=$(cat $pid/comm 2>/dev/null)
    swap=$(awk '/^VmSwap/{print $2}' $pid/status 2>/dev/null)
    [ -n "$swap" ] && [ "$swap" != "0" ] && echo "$comm ($pid): ${swap}kB"
done | sort -t: -k2 -rn | head -20
```

Example 2 — Prevent swapping for critical Java process (mlock):

```java
// Using JNA to call mlockall (lock all pages in RAM)
// In production: use -XX:+AlwaysPreTouch + systemd MemoryLock= instead

// systemd unit file approach:
// [Service]
// MemoryLock=infinity    # Allow process to lock all allocated memory
// LimitMEMLOCK=infinity  # ulimit equivalent
// ExecStart=java -XX:+AlwaysPreTouch -Xmx8g -jar app.jar

// Docker approach: disable swap for container
// docker run --memory=8g --memory-swap=8g (swap=memory means no extra swap)
```

Example 3 — Container memory limit and OOM vs swap:

```yaml
# Kubernetes pod spec
resources:
  requests:
    memory: "4Gi" # guaranteed allocation
  limits:
    memory: "6Gi" # OOM kill if exceeded (with swap disabled on node)


# Node configuration (disable swap):
# vm.swappiness=0 or kubelet --fail-swap-on=true (default Kubernetes)
# Container cgroup memory.limit = 6Gi; memory.swap.limit = 6Gi (no swap)
# If container allocates 6.1Gi: OOM killer kills container process
# Kubernetes detects: restarts container (exponential backoff)
```

### ⚖️ Comparison Table

| Memory State              | Description           | CPU impact      | Response time          |
| ------------------------- | --------------------- | --------------- | ---------------------- |
| All in RAM                | Normal operation      | 0% overhead     | Nanoseconds            |
| Some on swap (occasional) | Light pressure        | 1–5% overhead   | +10ms on swapped pages |
| Heavy swap (frequent)     | Sustained pressure    | 20–50% overhead | +100ms avg response    |
| **Thrashing**             | Continuous swap cycle | ~100% iowait    | Seconds per operation  |
| OOM kill                  | Process terminated    | —               | Process restart time   |

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| "Disabling swap is always better" | For real-time/latency-sensitive apps: yes. For desktop/batch: swap allows more concurrent work than OOM killing                     |
| "Swap to SSD is fast enough"      | SSD swap: ~0.1ms per page; RAM: ~0.0001ms. For GC scanning 2GB heap: 200M page faults × 0.1ms = 20,000 seconds of potential latency |
| "More swap = more memory"         | Swap trades latency for capacity; under overcommit, more swap extends the thrashing window rather than preventing it                |
| "kswapd at 100% CPU is normal"    | kswapd sustained at > 5–10% CPU = memory pressure; 100% = thrashing                                                                 |

### 🚨 Failure Modes & Diagnosis

**1. Java GC Pause Explosion**

Symptom: JVM GC logs show stop-the-world pauses of 10s+ (normally <200ms); application unresponsive; Kubernetes pod restarts due to liveness probe timeout.

Diagnosis:

```bash
# Check if JVM heap pages are swapped
cat /proc/<java_pid>/status | grep VmSwap  # e.g., VmSwap: 2000000 kB = 2GB swapped

# Check swap activity during GC
vmstat 1 | awk '{print $7, $8, $17}'    # si, so, cpu_wait
# High si during GC = heap pages being swapped in
```

Fix: `vm.swappiness=0`, `--memory-swap` container limit, `-XX:+AlwaysPreTouch`, add RAM.

---

**2. OOM Kill in Production Container**

Symptom: Kubernetes event: `OOMKilled`; container restarts; memory metrics show usage near limit before death.

Diagnosis:

```bash
kubectl describe pod <pod> | grep -A 5 "OOMKilled"
# Check memory limit vs actual usage
kubectl top pod <pod>

# Linux oom-kill log:
dmesg | grep -i "oom"
# Shows: which process, RSS at kill time, memory state
```

Fix: Increase memory limit, profile for memory leaks (heap dump), enable swap with container cgroup v2 limit as temporary measure.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — swap is the backing store for virtual pages not in RAM
- `Paging` — swap is invoked when all RAM page frames are occupied
- `Page Fault` — swap-in is triggered by a major page fault

**Builds On This (learn these next):**

- `OOM Killer` — Linux's last resort when swap is also exhausted
- `Huge Pages` — large pages (2MB) reduce TLB pressure and can be locked in RAM (no swap)
- `cgroups memory` — per-container memory and swap limits

**Alternatives / Comparisons:**

- `mlock()` — lock specific pages in RAM, preventing their swap
- `zswap` / `zram` — compressed in-memory swap (faster than disk, still slower than RAM)

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Swap: overflow RAM to disk (slow)        │
│              │ Thrashing: swap so heavy, no useful work  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Physical RAM is finite; processes need   │
│ SOLVES       │ more (swap); but too much = thrashing     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Swap-in latency is 5–6 OOM slower than   │
│              │ RAM; GC scanning swapped heap = disaster  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Over-provisioned hosts with occasional   │
│              │ spikes; batch/desktop workloads           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ JVMs, databases, real-time apps: disable  │
│              │ swap (vm.swappiness=0 or mlock)           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Memory capacity (swap) vs latency        │
│              │ (swapped pages = milliseconds, not ns)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Swap = slow overflow; thrashing = when  │
│              │  overflow consumes all of your work time" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OOM Killer → Huge Pages → cgroups memory  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Linux's OOM (Out of Memory) killer is the last resort when both RAM and swap are exhausted. It uses an **OOM score** (`/proc/<pid>/oom_score`) to select a victim: score is based on RSS (larger process = higher score), process uptime (newer = higher score), and adjustments (`/proc/<pid>/oom_score_adj` can be -1000 to 1000). The OOM killer kills the highest-scoring process. If your database process (large RSS, critical, long-running) has default OOM score 800 and your Node.js HTTP server (small RSS, can restart) has score 100: the OOM killer will kill the database. Fix this by: (a) explaining `oom_score_adj = -1000` to protect the database, (b) setting `oom_score_adj = 1000` on the Node.js process to make it the preferred victim, and (c) describing why running both in separate Kubernetes pods (separate cgroups) is the architecturally correct solution.

**Q2.** `zswap` is a Linux kernel feature that acts as a compressed in-memory swap cache: pages destined for swap are first compressed (LZ4/LZO/zstd) and stored in a kernel memory pool. Only when the compressed pool is full are pages written to the actual swap device. On a system with 16GB RAM and 512MB zswap pool, with LZ4 achieving 3:1 compression, zswap effectively holds ~1.5GB of pages in memory at negligible latency (~1μs) instead of sending them to SSD (0.1ms). Calculate the performance improvement factor for a workload that generates 10GB/min of swap traffic, and explain why zswap can still cause thrashing (the pool eviction path to disk is the same bottleneck).
