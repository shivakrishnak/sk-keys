---
layout: default
title: "Context Switch"
parent: "Operating Systems"
nav_order: 95
permalink: /operating-systems/context-switch/
number: "095"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Thread (OS), CPU Scheduling, Virtual Memory
used_by: Scheduler / Preemption, Process vs Thread, Concurrency vs Parallelism
tags:
  - os
  - performance
  - intermediate
---

# 095 — Context Switch

`#os` `#performance` `#intermediate`

⚡ TL;DR — The OS operation of saving the current process/thread's CPU state and loading another's, enabling time-sharing — but adding latency overhead (µs to ms) that accumulates at scale.

| #095 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Process, Thread (OS), CPU Scheduling, Virtual Memory | |
| **Used by:** | Scheduler / Preemption, Process vs Thread, Concurrency vs Parallelism | |

---

### 📘 Textbook Definition

A **context switch** is the mechanism by which the OS saves the execution state (context) of the currently running process or thread — including CPU registers, program counter, stack pointer, and memory mappings — into its Process Control Block (PCB) or Thread Control Block (TCB), and restores the previously saved state of the next scheduled process or thread. Context switches are triggered by: timer interrupts (preemption), voluntary yields (system calls, sleep, I/O blocks), and higher-priority task becoming runnable. For threads within the same process, only register state is saved/restored. For processes, the address space switch (CR3 register update) and TLB flush add significant overhead.

### 🟢 Simple Definition (Easy)

A context switch is the OS pausing one running task, saving its current work, and starting or resuming another — like a surgeon pausing one operation to handle an emergency and returning later.

### 🔵 Simple Definition (Elaborated)

With multiple threads and processes competing for limited CPU cores, the OS must share CPU time. To do this, it periodically interrupts the running task, saves everything it was doing (all its register values, which line of code it was on, what's on its stack), stores this snapshot in kernel memory, then loads the snapshot of another task and lets that one run. This pause happens thousands of times per second per CPU core. Each switch itself takes time (1–100 µs), and when switches happen too frequently (context switch storm), the CPU spends more time switching than actually doing work.

### 🔩 First Principles Explanation

**What must be saved and restored:**

```
Minimal context (registers):
  General-purpose registers: rax, rbx, rcx, rdx, rsi, rdi,
                              r8-r15 (16 × 8 bytes = 128 bytes)
  Instruction Pointer (RIP): PC = next instruction address
  Stack Pointer (RSP): current stack top
  Base Pointer (RBP): current frame
  CPU flags (RFLAGS): condition codes, interrupt flag

Extended context:
  FPU/SSE/AVX state: xsave area (512-4096 bytes for AVX-512)
  Segment registers: CS, DS, ES, FS, GS, SS

Address space (process switch only):
  CR3 register: page table base address → TLB flush
  NX/SMEP/SMAP bits
```

**Cost components:**

```
Thread switch (same process):
  1. Save registers to TCB:              ~50 ns
  2. Load registers from next TCB:       ~50 ns
  3. Stack pointer switch:               ~5 ns
  Total (no address space switch):       ~0.1-3 µs

Process switch:
  1. Save/load registers:                ~100 ns
  2. Update CR3 (page table switch):     ~100 ns
  3. TLB flush (all cached translations lost): ~500 ns-10 µs
  4. Cache warmup after switch (cold caches): ~10-100 µs
  Total (with TLB flush):               ~1-100 µs
```

**Why TLB flush is expensive:**

The TLB (Translation Lookaside Buffer) caches virtual→physical address translations. When the OS switches to a different process (different address space), all cached translations become invalid — the new process uses different virtual addresses mapping to different physical addresses. After the flush, the CPU must re-walk page tables for every memory access until the TLB warms up. For a process accessing many memory locations (e.g., database server), this cache warm-up penalty dominates context switch cost.

**Modern mitigation — PCID (Process Context Identifiers):**

Modern CPUs support PCID — tagging each TLB entry with a process identifier. Switching processes with PCID doesn't require flushing ALL TLB entries; only entries for the new process that were cached from a previous run need validation. Linux uses PCID to reduce TLB flush overhead on modern x86_64 systems.

**Voluntary vs Involuntary context switches:**

```
Voluntary (v.ctx.sw.):
  - Thread calls sleep(), wait(), blocking I/O
  - Explicitly yields CPU (sched_yield())
  - Typical rate: application-controlled

Involuntary (i.ctx.sw.):
  - Timer interrupt (100 Hz - 1000 Hz typical)
  - Higher priority task becomes runnable
  - Excessive rate indicates CPU contention or bad scheduling
  - Monitor: pidstat -wI 1 5 (Linux)
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Context Switching:

- Single-tasking (MS-DOS): one program runs to completion; nobody else gets CPU.
- No I/O during computation: if a program waits for disk, CPU sits idle.
- No preemption: a buggy program with an infinite loop hangs the entire system.

What breaks without it:
1. Multi-user systems impossible — one user's job blocks all others.
2. I/O-while-computing impossible — program must busy-wait.
3. Real-time deadlines unenforceable — no way to guarantee a task gets CPU.

WITH Context Switching:
→ Thousands of threads share CPU via time-slicing — the illusion of parallelism.
→ I/O-blocked threads yield CPU — other work proceeds while data is fetched.
→ High-priority tasks preempt low-priority ones — real-time guarantees possible.

### 🧠 Mental Model / Analogy

> Context switch is like a surgeon who must operate on multiple patients simultaneously. The surgeon saves their progress on Patient A (marks the incision location, notes the current step) — "saving context" — then moves to Patient B and resumes. But "moving between patients" isn't free: the surgeon must scrub, re-check notes, and reorient — that's the overhead. If patients require very frequent attention (high context-switch rate), the surgeon spends more time moving than operating (context switch thrashing).

"Saving progress on Patient A" = saving context to PCB/TCB, "moving between patients" = context switch overhead, "scrubbing and re-orienting" = TLB flush + cache warm-up.

### ⚙️ How It Works (Mechanism)

**x86-64 context switch sequence (simplified):**

```
Timer interrupt fires (every 1ms at 1000 Hz):
  1. CPU saves RIP, RSP, RFLAGS to kernel stack (hardware)
  2. Enters kernel mode (privilege escalation)
  3. Scheduler runs: picks next thread

  4. schedule() called:
     a. Save remaining registers (rax, rbx... xsave area)
        to current thread's TCB
     b. If switching processes: update CR3 (address space switch)
     c. If TLB flush needed: invpcid instruction
     d. Load next thread's registers from its TCB

  5. Return to next thread (IRET instruction)
  6. CPU back in user mode executing next thread's code
```

**Measuring context switches:**

```bash
# System-wide context switch rate
vmstat 1 5
# Output: "cs" column = context switches per second
# Typical healthy server: <100,000 cs/s
# Problematic: >1,000,000 cs/s (thrashing)

# Per-process context switches
pidstat -wI -p <pid> 1 5
# cswch/s = voluntary, nvcswch/s = involuntary

# Java: check context switch contribution to latency
perf stat -p <java_pid> sleep 10
# reports: context-switches, cpu-migrations
```

**Java-specific context switch sources:**

```java
// High voluntary context switches:
Thread.sleep(1);        // sleep → yield → context switch
Object.wait(timeout);   // block → yield → context switch
LockSupport.park(obj);  // park → yield → context switch

// High involuntary context switches:
// Many CPU-bound threads competing for few cores
// OS timer preempts them repeatedly

// Reduce context switches:
// 1. Fewer threads (use virtual threads for I/O-bound)
// 2. Lock-free algorithms (reduce wait/park)
// 3. Thread affinity: pin threads to CPUs with taskset
```

### 🔄 How It Connects (Mini-Map)

```
CPU core (executing instructions)
        ↓ timer interrupt or I/O block
Context Switch ← you are here
  (save current state; load next state)
        ↓ decided by
Scheduler / Preemption
  (which thread/process runs next; priority; CFS/FIFO)
        ↓ cost differs for
Process switch (expensive: TLB flush)
Thread switch (cheaper: no address space change)
Fiber switch  (cheapest: user-space only)
```

### 💻 Code Example

Example 1 — Measuring context switches per second:

```bash
# Watch context switch rate for your Java app
watch -n1 'pidstat -wI -p $(pgrep -f "java.*MyApp") | tail -3'

# Interpretation:
# cswch/s < 1000:    normal for low-traffic service
# cswch/s 1000-10000: moderate load, healthy
# cswch/s > 100000:   potential contention; investigate
# nvcswch/s >> cswch/s: many involuntary = CPU-bound contention
```

Example 2 — Reducing context switches with lock-free algorithms:

```java
// BAD: synchronized block → thread may block → context switch
synchronized (lock) {
    counter++;
}

// GOOD: AtomicInteger → CAS → no blocking → fewer context switches
AtomicInteger counter = new AtomicInteger();
counter.incrementAndGet(); // CAS loop, never parks the thread
```

Example 3 — Context switch monitoring in JVM:

```java
// Java: count context switches since process start
import com.sun.management.OperatingSystemMXBean;
OperatingSystemMXBean os = (OperatingSystemMXBean)
    ManagementFactory.getOperatingSystemMXBean();

// CPU time = total scheduled CPU time (not wall time)
long cpuTime = os.getProcessCpuTime(); // nanoseconds
long wallTime = System.nanoTime();
double cpuUtilisation = (double) cpuTime / wallTime;
// If cpuUtilisation << 1.0 for a busy service:
// threads spending time in context switch / waiting
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Context switches only happen when a program is preempted | Context switches also happen voluntarily when threads block on I/O, sleep, or wait for a lock — often the majority of context switches in I/O-bound services. |
| More CPU cores eliminate context switch overhead | More cores reduce FREQUENCY of context switches per core (more work done concurrently), but each context switch still has the same cost — and TLB warm-up may be worse with NUMA effects. |
| Context switch cost is always ~1 µs | Thread switch within a process: ~0.1-3 µs. Process switch with TLB warm-up on a cache-heavy database: can be 10-100 µs. Cost varies widely by workload. |
| Virtual threads eliminate context switching | Virtual threads replace OS context switches with cheaper user-space continuation saves/restores. Still incur context switch when the carrier OS thread itself switches. |
| Reducing thread count always reduces context switches | Fewer threads = fewer context switches is true for CPU-bound. For I/O-bound, fewer threads = each one makes more blocking calls = similar total voluntary context switches. |

### 🔥 Pitfalls in Production

**1. Context Switch Storm from Too Many Threads**

```bash
# BAD: 10,000 threads on 8-core machine
# Each thread gets CPU slice ~every 10 seconds
# → 1000 context switches/second per core just for scheduling
# → significant CPU overhead for the switches themselves

# Diagnose: vmstat 1 | awk '{print $12}' (cs column)
# cpuStealing: high in containers → noisy neighbors consuming context switch budget

# GOOD: use virtual threads or thread pools sized to CPU
# For Java: Executors.newVirtualThreadPerTaskExecutor()
```

**2. False Sharing Amplifying Cache Miss Cost After Context Switch**

```java
// BAD: Two thread-local counters in same cache line
// After context switch: CPU loads cache line containing both counters
// Thread 1 writes counter1 → invalidates Thread 2's cache of counter2
// → false sharing: each thread's write causes the other's cache to reload
class BadCounters {
    volatile long counter1; // in same 64-byte cache line
    volatile long counter2;
}

// GOOD: Pad to separate cache lines
class GoodCounters {
    volatile long counter1;
    long pad1, pad2, pad3, pad4, pad5, pad6, pad7; // 56 bytes padding
    volatile long counter2; // now in next 64-byte cache line
}
// @Contended annotation in Java: automatic padding
```

**3. Thread Affinity Ignored on NUMA Systems**

```bash
# On NUMA (Non-Uniform Memory Access) multi-socket servers:
# Thread migrated to different CPU socket (via context switch)
# loses locality to memory allocated on original socket → 2-4× slower memory access

# GOOD: Pin latency-sensitive threads to NUMA node
taskset -c 0-7 java -jar my-app.jar  # pin to first 8 CPUs (socket 0)
numactl --cpunodebind=0 --membind=0 java -jar my-app.jar
```

### 🔗 Related Keywords

- `Process` — process context switch includes expensive TLB flush.
- `Thread (OS)` — thread context switch is cheaper (same address space).
- `Scheduler / Preemption` — the OS mechanism triggering context switches.
- `TLB` — the hardware cache whose flush is the primary cost of process context switches.
- `Fiber / Coroutine` — achieves task-switching without OS context switch overhead.
- `Concurrency vs Parallelism` — concurrency's cost is the context switch overhead it introduces.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Save-state-of-A, restore-state-of-B;     │
│              │ overhead: thread ~1µs, process ~10-100µs. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Time-sharing CPU among threads/processes. │
│              │ Monitor: cs/s in vmstat; nvcswch in pidstat│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-performance: reduce context switch   │
│              │ rate via VTs, lock-free, correct pool size │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Context switch: the surgeon changing     │
│              │ tables — necessary but not free."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Scheduler/Preemption → Virtual Memory →   │
│              │ TLB → Concurrency vs Parallelism          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A high-frequency trading system runs a latency-critical Java thread processing market data. The thread must respond within 10 µs. The system has 8 cores and typically 500 other threads running (GC threads, JIT threads, monitoring). A context switch can take 1-100 µs. Describe three specific techniques to reduce context-switch-induced latency jitter for the critical thread, including OS-level isolation (isolcpus), JVM-level configuration, and algorithm-level design choices — explaining the mechanism of each.

**Q2.** Modern Intel CPUs support PCID (Process Context Identifiers, also called ASIDs) to avoid full TLB flushes on context switches. Explain exactly how PCID allows the CPU to keep TLB entries from multiple processes simultaneously and what mechanism is used to invalidate stale entries for a specific PCID when a process modifies its page tables. Then explain the Meltdown vulnerability (2018) and why its patch — adding KPTI (Kernel Page Table Isolation) — significantly increased context switch overhead on pre-PCID or partially-PCID CPUs.

