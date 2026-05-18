---
id: OSY-011
title: CPU Scheduling Overview
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-010
used_by: OSY-026, OSY-065, OSY-066
related: OSY-010, OSY-026, OSY-065
tags:
  - foundational
  - scheduling
  - cpu
  - preemptive
  - dispatcher
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/osy/cpu-scheduling-overview/
---

## TL;DR

CPU scheduling decides which thread runs next on the CPU.
Modern Linux uses Completely Fair Scheduler (CFS):
preemptive, priority-weighted, with a 4ms default time
quantum. Scheduling directly determines application
latency and throughput.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-011 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | scheduling, CPU, preemptive, CFS |
| **Prerequisites** | OSY-010 |

---

### The Scheduling Problem

At any point, there may be 100 READY threads but only
8 CPU cores. The scheduler decides which 8 run, for how
long, and in what order. It must balance:
- **Fairness**: each thread gets CPU time proportional
  to its priority
- **Throughput**: maximize total work done per second
- **Responsiveness**: interactive threads get CPU fast
- **Efficiency**: minimize context switch overhead

No algorithm perfectly maximizes all four. Every
scheduler makes a trade-off.

---

### Scheduling Goals by System Type

```
Interactive OS (desktop/server):
  Goal: responsiveness (low latency)
  Metric: response time (time from event to reaction)
  Example: typing in editor feels instant
  Solution: short time quantum (4ms), preemptive

Batch system (compute jobs):
  Goal: throughput (max jobs/hour)
  Metric: job completion rate
  Example: video encoding batch jobs
  Solution: long time quantum (minutes), non-preemptive

Real-time system (embedded):
  Goal: determinism (hard deadline guarantees)
  Metric: worst-case response time
  Example: airbag deployment within 1ms
  Solution: SCHED_FIFO, no preemption by normal threads
```

---

### Scheduling Mechanisms

```
Preemptive scheduling:
  OS can forcibly remove a running thread from CPU.
  Uses hardware timer interrupt (every 4ms on Linux).
  Timer fires -> interrupt handler -> scheduler decision.
  Thread moved to READY queue with remaining quantum.
  
Non-preemptive (cooperative) scheduling:
  Thread runs until it voluntarily yields CPU.
  No timer interrupt preemption.
  Problem: one buggy/infinite-loop thread starves all others.
  Used by: early Windows (3.x), some embedded RTOS.
  
Dispatcher:
  The OS component that performs the actual context switch.
  Steps: save old thread context, select new thread,
         restore new thread context, jump to new thread.
  Dispatcher latency: time to stop one thread, start another.
  Goal: minimize dispatcher latency.
```

---

### Run Queue and Priority

```
Linux CFS (Completely Fair Scheduler) run queue:
  Red-black tree ordered by "virtual runtime"
  vruntime = CPU time weighted by thread priority (nice value)
  Nice -20 (high priority): vruntime increments slowly
  Nice +19 (low priority): vruntime increments quickly
  Scheduler always picks thread with LOWEST vruntime
  Result: low-priority threads eventually get CPU time
          (no starvation), but high-priority threads run more

Priority in Java context:
  Thread.setPriority(Thread.MAX_PRIORITY) maps to Linux nice -5
  (not guaranteed; JVM maps to OS hints, OS may ignore)
  For real priority control: native POSIX calls or setpriority()
```

---

### Textbook Definition

CPU scheduling is the OS mechanism for allocating CPU
time to competing threads. A preemptive scheduler uses
hardware timer interrupts to periodically preempt running
threads. The scheduler selects the next thread from the
run queue based on a scheduling algorithm (FCFS, Round
Robin, CFS, SCHED_FIFO) and dispatches it onto the CPU.

---

### Understand It in 30 Seconds

CPU scheduling is like a restaurant host managing
tables (CPUs). Many customers (threads) are waiting.
The host decides who sits next (scheduling algorithm),
for how long (time quantum), and ensures everyone
eventually gets served (no starvation).

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Higher-priority threads always run immediately" | CFS uses weighted fair sharing, not strict priority. A high-priority thread gets more CPU time but doesn't starve all others. Use SCHED_FIFO for hard real-time preemption |
| "Thread.setPriority() in Java guarantees OS priority" | JVM maps Java priorities to OS nice values as a hint. The OS may honor or ignore them. On Linux, non-root processes cannot set nice below 0 |

---

### Mastery Checklist

- [ ] Knows the three scheduling goals (responsiveness, throughput, fairness)
- [ ] Understands preemptive vs cooperative scheduling
- [ ] Knows Linux CFS uses virtual runtime (red-black tree)
- [ ] Can explain why high thread count hurts scheduling
