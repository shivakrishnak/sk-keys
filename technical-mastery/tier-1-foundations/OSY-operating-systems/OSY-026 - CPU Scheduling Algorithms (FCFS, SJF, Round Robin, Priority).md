---
id: OSY-026
title: "CPU Scheduling Algorithms (FCFS, SJF, Round Robin, Priority)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-006, OSY-011
used_by: OSY-064, OSY-073
related: OSY-011, OSY-064, OSY-073
tags:
  - scheduling
  - algorithms
  - FCFS
  - round-robin
  - priority
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/osy/cpu-scheduling-algorithms/
---

## TL;DR

CPU scheduling algorithms decide which ready thread runs
next. FCFS is simple but causes convoy effect. SJF
minimizes turnaround but requires knowing burst time.
Round Robin gives fairness at the cost of context
switches. Linux CFS combines weighted fairness with
virtual runtime tracking.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-026 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | scheduling, FCFS, SJF, round robin, priority, CFS |
| **Prerequisites** | OSY-006, OSY-011 |

---

### The Problem This Solves

Multiple threads are ready to run but only N CPU cores
exist. The scheduler must decide which thread runs next.
The choice affects: throughput (jobs completed/sec),
latency (time from submit to completion), fairness
(preventing starvation), and CPU utilization.

---

### Four Classic Algorithms

**FCFS (First Come, First Served)**

```
Queue: [P1(24ms), P2(3ms), P3(3ms)]
Runs:   P1 -> P2 -> P3
Gantt:  |----P1(24)----||P2(3)||P3(3)|

Turnaround:  P1=24, P2=27, P3=30 -> avg=27ms
Waiting:     P1=0,  P2=24, P3=27 -> avg=17ms

Problem: Convoy Effect
  Short P2, P3 wait behind long P1
  I/O-bound requests wait behind CPU-bound burst
  Web server: 1ms request waits behind 30s database backup
```

**SJF (Shortest Job First) - Optimal but impractical**

```
Queue: [P1(24ms), P2(3ms), P3(3ms)]
Runs:   P2 -> P3 -> P1 (shortest first)
Gantt:  |P2(3)||P3(3)||----P1(24)----|

Turnaround:  P2=3, P3=6, P1=30 -> avg=13ms
Waiting:     P2=0, P3=3, P1=6  -> avg=3ms

Problem: Requires knowing future burst time
  Preemptive version (SRTF): context switch when shorter arrives
  Starvation: long jobs never run if short jobs keep arriving
  Estimation: exponential averaging of past bursts
```

**Round Robin (RR) - Used by Linux base scheduler**

```
Time quantum q = 4ms
Queue: [P1(24ms), P2(3ms), P3(3ms)]
Runs:   P1(4) -> P2(3) -> P3(3) -> P1(4) -> ... -> P1

Gantt:  |P1(4)|P2(3)|P3(3)|P1(4)|P1(4)|P1(4)|P1(4)|P1(4)|P1(4)|

Waiting: P1=10, P2=4, P3=7 -> avg=7ms
Context switches: 8 total (vs 2 for FCFS)

Key tradeoff:
  q too small: many context switches, high overhead
  q too large: degenerates to FCFS
  q=20ms with 10ms context switch: 33% CPU wasted on switching
```

**Priority Scheduling**

```
Higher priority = runs sooner
Static: assigned at creation (POSIX nice values)
Dynamic: adjusts based on behavior (I/O-bound gets boost)

Problem: Priority Inversion
  High priority thread H needs lock held by low priority thread L
  Medium priority thread M keeps running (preempts L)
  H is blocked, M runs, L never gets CPU
  
  Famous: Mars Pathfinder 1997 priority inversion
  watchdog reset (fixed by enabling priority inheritance)
  
Priority Inheritance Solution:
  L temporarily inherits H's priority while holding H's lock
  L runs, releases lock, H unblocks, priority restored
```

---

### Linux CFS (Completely Fair Scheduler)

```
CFS goal: each thread gets equal CPU time proportionally

Data structure: Red-black tree, sorted by vruntime
  vruntime = actual runtime normalized by weight
  weight = f(nice_value)
  
  nice -20 (highest priority): vruntime increases slowly
  nice +19 (lowest priority):  vruntime increases quickly
  
Scheduling decision:
  Always pick leftmost node (smallest vruntime)
  Thread ran least is scheduled next
  
Minimum granularity: 0.75ms (no context switch too fast)
Target latency: 6ms (each runnable thread gets CPU within 6ms)

Java interaction:
  Spring request threads: default nice 0
  GC threads: default nice 0 (may compete with requests!)
  Configure: -XX:GCTaskAffinity or cgroups to isolate

// Check current niceness and scheduling policy
ps -o pid,ni,cls,cmd -p $(pgrep java)
# NI column: nice value (-20 to +19)
# CLS column: TS=time-sharing, FF=FIFO, RR=round-robin
```

---

### Comparison Table

| Algorithm | Throughput | Latency | Fair | Starvation Risk | Used In |
|-----------|-----------|---------|------|----------------|---------|
| FCFS | Medium | Poor | No | High | Batch systems |
| SJF | High | Best avg | No | High (long jobs) | Theoretical |
| Round Robin | Medium | Good | Yes | No | Linux user tasks |
| Priority | Variable | Good for high | No | Yes (low priority) | RTOS, Linux RT |
| CFS | High | Good | Weighted | No | Linux default |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Linux uses Round Robin scheduling" | Linux CFS uses virtual runtime fair queuing (red-black tree) - it's more sophisticated than pure RR. RR is used for SCHED_RR real-time threads |
| "SJF is the best algorithm to use in practice" | SJF requires knowing future CPU burst lengths (impossible). It's a theoretical lower bound, not a practical algorithm |
| "Higher thread priority always means faster execution" | Priority inversion can cause high-priority threads to block behind low-priority ones. Also, starvation: low-priority threads may never run if high-priority threads continuously arrive |

---

### Failure Modes

```
1. Priority Inversion
Symptom: High-priority thread blocked indefinitely
  while lower-priority threads run.
Diagnosis: jstack shows high-priority thread BLOCKED;
  /proc/PID/status shows high voluntary_ctxt_switches
Fix: Priority inheritance (Java: synchronized blocks
  implement priority inheritance via futex PI flag)

2. Starvation (Priority Scheduling)
Symptom: Low-priority tasks never complete.
Diagnosis: CPU profiling shows certain threads never
  appear in samples.
Fix: Aging - gradually increase priority of waiting
  threads. Linux CFS prevents this with vruntime.

3. Excessive Context Switching (Too Many Threads)
Symptom: High vmstat cs value (>100K/sec),
  low useful work output.
Diagnosis: vmstat 1 shows cs > sum of (us+sy)*cores
Fix: Reduce thread count; use thread pools sized to
  CPU core count for CPU-bound work.
```

---

### Related Keywords

**Builds on:** OSY-006 (Process States and PCB),
OSY-011 (CPU Scheduling Overview)

**Used by:** OSY-064 (Linux CFS Internals),
OSY-073 (Real-Time Scheduling)

**Related concepts:** OSY-030 (Mutex vs Semaphore vs Monitor),
OSY-051 (Process vs Thread Decision Guide)

---

### Quick Reference Card

| Algorithm | Decision Rule | Optimal For |
|-----------|-------------|------------|
| FCFS | Arrival order | Simple batch |
| SJF/SRTF | Shortest burst first | Minimizing avg wait |
| Round Robin | q-ms time slices | Interactive fairness |
| Priority | Numeric priority | Real-time systems |
| CFS (Linux) | Smallest vruntime | General purpose OS |

---

### Interview Deep-Dive

**Q1 (Easy): What is the convoy effect?**
Short tasks queue behind a long CPU-bound task in FCFS.
A web server handling a quick health check endpoint
blocks behind a long report generation request.

**Q2 (Medium): How does priority inversion occur?**
Low-priority L holds a mutex. High-priority H tries
to acquire it and blocks. Medium-priority M preempts L
(higher priority than L, doesn't need the mutex). H
is effectively blocked by M despite H > M. Mars
Pathfinder 1997 reset due to this exact scenario.

**Q3 (Hard): How does Linux CFS handle fairness while
allowing priority (nice values)?**
Each thread tracks its virtual runtime. Nice value
adjusts how fast vruntime increments (high-priority
threads: slower increment = more CPU time, but never
zero time for others). CFS always picks the thread
with smallest vruntime from the red-black tree. This
gives weighted fairness - no starvation.
