---
layout: default
title: "Scheduler / Preemption"
parent: "Operating Systems"
nav_order: 96
permalink: /operating-systems/scheduler-preemption/
number: "096"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Thread (OS), Context Switch, CPU Architecture
used_by: Context Switch, Process vs Thread, Real-Time Systems, CFS (Linux)
tags:
  - os
  - performance
  - intermediate
---

# 096 — Scheduler / Preemption

`#os` `#performance` `#intermediate`

⚡ TL;DR — The OS scheduler allocates CPU time among runnable threads using scheduling algorithms (CFS, FIFO, Round-Robin); preemption forces context switches via timer interrupt so no single thread can monopolise the CPU.

| #096 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Process, Thread (OS), Context Switch, CPU Architecture | |
| **Used by:** | Context Switch, Process vs Thread, Real-Time Systems, CFS (Linux) | |

---

### 📘 Textbook Definition

The **OS scheduler** is the kernel subsystem responsible for deciding which runnable thread (or process) executes on each CPU core at any given time. **Preemption** is the act of forcefully interrupting an executing thread via a hardware timer interrupt before it voluntarily yields, enabling fair multi-tasking. Scheduling policies include: **FIFO** (first in, first out — no preemption within priority), **Round-Robin** (fixed time slices, equal priority threads rotate), and **CFS** (Completely Fair Scheduler — Linux default, virtual runtime-based proportional fairness). Real-time schedulers (SCHED_FIFO, SCHED_RR) guarantee bounded latency for high-priority threads.

### 🟢 Simple Definition (Easy)

The scheduler is the referee that decides which thread gets to run on the CPU — and for how long. Preemption is the whistle it blows to force a rotation even if a thread isn't done.

### 🔵 Simple Definition (Elaborated)

Without a scheduler, the first thread to get the CPU would run forever. The scheduler maintains a queue of runnable threads and gives each a slice of time — typically 1-4ms — on the CPU. When the slice expires, a hardware timer fires an interrupt (preemption), the OS context-switches to the next thread, and the rotation continues. More sophisticated schedulers like Linux's CFS give more time to "underserved" threads (those who've had less CPU recently), providing fairness. Real-time schedulers bypass normal scheduling entirely, guaranteeing the highest-priority SCHED_FIFO thread gets the CPU immediately.

### 🔩 First Principles Explanation

**Scheduler mechanics:**

```
Scheduler's run queue (per CPU):
  Thread 1 [priority=120, vruntime=1000ms]
  Thread 2 [priority=120, vruntime=800ms]  ← pick this (least runtime)
  Thread 4 [priority=100, vruntime=900ms]  ← priority 100 = nice -20 (higher)

CFS virtual runtime:
  Each thread has a vruntime counter (CPU time × weight)
  Scheduler always picks thread with lowest vruntime
  Higher nice value = higher weight = vruntime increases faster
  → lower nice (higher priority) threads accumulate vruntime slower
  → they get scheduled more frequently
```

**Preemption:**

```
Hardware timer fires (e.g., every 1ms at 1000 Hz):
  → CPU timer interrupt → enters kernel → checks scheduler
  → Current thread's vruntime updated
  → If next runnable thread has lower vruntime by > min_granularity:
      → preempt current thread (involuntary context switch)
      → run next thread
  → Otherwise: current thread continues

Result: no thread monopolises CPU for more than ~4ms (Linux default)
```

**Scheduling classes in Linux:**

```
SCHED_OTHER (CFS — default):
  All normal user processes/threads
  Fair sharing; time slices ~0.75-6ms; NOT real-time

SCHED_FIFO (real-time):
  Fixed priority (1-99); runs until it yields or is preempted
  by higher-priority SCHED_FIFO thread
  Used by: audio drivers, latency-sensitive daemons

SCHED_RR (real-time round-robin):
  Like SCHED_FIFO but with time slices among equal priorities

SCHED_BATCH:
  Background batch jobs; longer slices; not woken for IO
  
SCHED_IDLE:
  Lowest possible scheduling priority
```

**Java thread priorities and OS scheduling:**

```
Java thread priority 1-10 maps to OS nice values:
  Java priority 10 → OS nice -10 (higher priority)
  Java priority 5  → OS nice 0   (default)
  Java priority 1  → OS nice 10  (lower priority)

On Linux CFS: nice values affect time slice length and scheduling
On Windows: thread priorities directly affect scheduling weight
NOTE: Java thread priority is a HINT — OS may ignore it
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT a Scheduler / Preemption:

- Single-tasking (cooperative multitasking, old macOS 9): if an application crashes or loops, the entire system freezes.
- Batch systems: long jobs starve short jobs indefinitely.
- No fairness: one CPU-hungry process gets all the CPU.

What breaks without it:
1. A user's terminal becomes unusable if a background compilation has the CPU.
2. A buggy process with an infinite loop hangs the entire system.
3. Interactive applications (mouse, keyboard) would be unresponsive during computation.

WITH Scheduler / Preemption:
→ Fair CPU sharing — every process makes progress.
→ Responsive system — timer interrupt ensures no infinite monopolisation.
→ Real-time guarantees for critical tasks (audio, real-time control).

### 🧠 Mental Model / Analogy

> The scheduler is an air traffic controller managing runway time (CPU). All planes (threads) are in a queue. The controller decides which plane gets the runway next based on priority, waiting time and fuel urgency (scheduling policy). If a plane stays on the runway past its allocated time, the control tower sends a forced-departure signal (timer interrupt/preemption) and orders the next plane to take off. Real-time (SCHED_FIFO) aircraft are emergency services — they trump all civilian flights and land/take-off immediately when needed.

"Runway" = CPU, "planes" = threads, "controller" = OS scheduler, "allocated time" = time slice, "forced departure signal" = timer interrupt, "emergency aviation" = SCHED_FIFO.

### ⚙️ How It Works (Mechanism)

**CFS algorithm (Linux default):**

```
Data structure: red-black tree keyed by vruntime
  - Always runs the leftmost node (minimum vruntime)
  - Insert/remove: O(log n) — red-black tree operations

Thread A runs:
  A.vruntime += delta_time × (default_weight / A.weight)
  (higher priority = lower weight divisor = slower vruntime growth)

When to preempt:
  After each tick: if leftmost_thread.vruntime < current.vruntime - min_granularity
  → schedule next (preempt current)

Time resolution: Linux HZ=250 → 4ms tick; HZ=1000 → 1ms tick
```

**Tuning scheduler for Java services:**

```bash
# Check current scheduler policy for Java threads
chrt -p $(pgrep -f "java.*MyApp")
# scheduling policy: SCHED_OTHER (normal)

# Set higher priority for latency-sensitive Java service
chrt --rr -p 50 $(pgrep -f "java.*MyApp")
# Makes it SCHED_RR priority 50 — real-time class!
# WARNING: misuse can starve system, causing hangs

# Reduce nice value (increase priority):
renice -n -5 -p $(pgrep -f "java.*MyApp")

# Check scheduler statistics
cat /proc/schedstat
cat /proc/<pid>/schedstat  # per-process
```

**Java and scheduler interaction:**

```bash
# JVM GC threads compete with application threads
# On low-core systems, GC can preempt app threads → latency spikes
# Mitigation:
# -XX:GCTimeRatio=99 → GC gets at most 1% CPU
# -XX:MaxGCPauseMillis=100 → hint for G1/ZGC pause target
# Or: pin GC and app threads to separate CPUs via CPU affinity
```

### 🔄 How It Connects (Mini-Map)

```
Runnable threads (in OS run queue)
        ↓ scheduled by
Scheduler ← you are here
  (CFS/FIFO/RR: decides WHICH thread runs NEXT)
        ↓ enforced by
Preemption (timer interrupt: ensures fairness)
        ↓ implemented via
Context Switch (save/restore CPU state)
        ↓ affects
Real-Time Latency | JVM GC Scheduling | Thread Starvation
```

### 💻 Code Example

Example 1 — Observing scheduler preemption impact:

```bash
# Monitor voluntary vs involuntary context switches
# nvcswch/s high = involuntary = CPU contention = over-scheduled
pidstat -wI 1 -p $(pgrep -f "java")

# Example output:
# 14:00:01  java  cswch/s  nvcswch/s
# 14:00:02  java  1234.5   5.2     ← OK: mostly voluntary (I/O bound)
# 14:00:03  java  120.3    8934.1  ← BAD: high involuntary = CPU starved

# High involuntary ctx switches indicate:
# - Too many threads competing for CPU
# - Need to reduce thread count or increase CPU allocation
```

Example 2 — Setting thread priority in Java (hint to scheduler):

```java
// Java thread priority is a HINT to the OS scheduler
Thread worker = new Thread(task);
worker.setPriority(Thread.MAX_PRIORITY);  // priority 10 → nice -5 on Linux
worker.start();

// Real-time priority for critical threads (Linux, requires root/CAP_SYS_NICE)
// Via JVM: use ProcessBuilder to run with chrt
// Or: use JNA/JNI to call sched_setscheduler()

// More reliable: CPU affinity (pinning) via ProcessBuilder
ProcessBuilder pb = new ProcessBuilder(
    "taskset", "-c", "0,1",    // pin to CPUs 0 and 1
    "java", "-jar", "app.jar"
);
```

Example 3 — Diagnosing scheduler starvation:

```bash
# Check if threads are waiting unreasonably long for CPU
# (scheduler latency)
perf sched latency -p $(pgrep -f "java") | head -20
# Shows avg/max scheduling latency per thread

# Linux /proc/schedstat fields:
# Field 8: total time waiting on run queue (nanoseconds)
cat /proc/$(pgrep -f "java")/schedstat
# [cpu_time_ns] [wait_time_ns] [timeslices_run]
# Wait >> CPU time → thread is CPU-starved (preempted often)
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java Thread.sleep(1) sleeps for exactly 1ms | sleep(1) means "sleep AT LEAST 1ms." Actual sleep may be longer depending on scheduler granularity (typically 4ms on Linux). |
| setPriority() reliably makes a thread run more | Java thread priority is a scheduling hint. On Linux, it maps to nice values. The OS may not strictly honour it, especially in containers. Critical systems use SCHED_FIFO via JNI/taskset. |
| CFS is fair: each thread gets exactly 1/N of CPU | CFS is proportionally fair per weight/priority. A thread with higher priority (lower nice) gets proportionally MORE CPU. Equal priority and equal nice → equal CPU. |
| Preemption can interrupt a synchronized block | Preemption interrupts execution at any instruction — mid-synchronized-block. This is why synchronized is needed: preemption is unpredictable. |
| Real-time scheduling (SCHED_FIFO) makes Java predictable | SCHED_FIFO ensures a thread gets CPU promptly, but JVM pauses (GC, JIT compilation, class loading) are not affected by OS scheduling priority. |

### 🔥 Pitfalls in Production

**1. Thread Starvation from Priority Inversion**

```java
// Priority inversion scenario:
// High-priority thread H waits for a lock held by low-priority thread L
// Medium-priority thread M preempts L (M is runnable, L is low-priority)
// Result: H is blocked behind M, despite H having higher priority

// Mitigation: Priority inheritance (most JVM monitors implement this)
// Or: restructure to avoid shared locks between different-priority threads
// ReentrantLock with tryLock() + timeout to detect inversion
```

**2. Container CPU Throttling (CFS Bandwidth Enforcement)**

```bash
# In Kubernetes, container CPU limits implemented via CFS bandwidth control
# Container given cpu.cfs_quota_us microseconds per cpu.cfs_period_us

# Example: cpu.limits=0.5 → 50ms of CPU per 100ms period
# A Java GC pause lasting 50ms → container gets CPU throttled!
# Application appears to stall randomly

# Diagnose: check nr_throttled in container
cat /sys/fs/cgroup/cpu/cpu.stat | grep throttled
# throttled_time_ns: time spent throttled = hidden latency

# Fix: set appropriate CPU limits; consider cpu.limits >= cpu.requests × 2
```

**3. Ignoring JVM Scheduler Interaction**

```bash
# JVM internal threads compete for CPU with application threads:
# GC threads: can preempt application threads during GC
# JIT compiler threads: background compilation competes for CPU

# On 4-vCPU container:
# 2 GC threads + 1 JIT thread = only 1 vCPU for application!

# Tune:
# -XX:ConcGCThreads=1     (reduce GC thread count)
# -XX:+TieredCompilation  (JIT works incrementally, less burst)
# Or: increase CPU limits to account for JVM internal threads
```

### 🔗 Related Keywords

- `Context Switch` — the mechanism the scheduler uses to transition between threads.
- `Process` — the primary scheduling unit; threads within a process share the scheduler's view.
- `Thread (OS)` — the schedulable unit on modern OS kernels.
- `Concurrency vs Parallelism` — the scheduler creates concurrency on one core; N cores enable parallelism.
- `Virtual Memory` — TLB flush cost during process switches is the scheduler's most expensive operation.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Scheduler = decides who runs next;        │
│              │ Preemption = forces rotation via timer.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing: thread starvation, latency    │
│              │ spikes, high nvcswch/s, container         │
│              │ CPU throttling.                           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use SCHED_FIFO casually —           │
│              │ misuse starves entire system.             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Scheduler: the air traffic controller    │
│              │ that ensures every plane takes off."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Context Switch → Virtual Memory →         │
│              │ User Space vs Kernel Space                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kubernetes enforces container CPU limits using CFS bandwidth control: a container with `cpu.limits=2` gets at most 2 CPU-seconds of execution per 100ms scheduling period (200ms of CPU time per 100ms). A Java application's GC pause takes 60ms wall-clock time but consumes 120ms of CPU time (2 GC threads). Explain precisely why this GC pause can cause the container to be CPU-throttled — showing the CPU usage vs quota interaction — and what the externally observable symptom would look like in the container's response time metrics.

**Q2.** The Linux CFS scheduler uses a red-black tree sorted by virtual runtime (vruntime) to always select the least-run thread. A thread with nice=0 and a thread with nice=-10 are both in the run queue. Using the CFS weight table (nice=0 weight=1024, nice=-10 weight=9548), calculate the ratio of CPU time each thread receives over a given period, and explain what happens to the vruntime of a thread that sleeps for 1 second and then wakes up — specifically whether it rejoins near the front or back of the run queue and what mechanism prevents it from monopolising the CPU for 1 second of "catch-up" time.

