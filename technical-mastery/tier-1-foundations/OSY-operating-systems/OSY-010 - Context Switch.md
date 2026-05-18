---
id: OSY-010
title: Context Switch
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006, OSY-007, OSY-009
used_by: OSY-011, OSY-070, OSY-099
related: OSY-007, OSY-011, OSY-065, OSY-099
tags:
  - foundational
  - context-switch
  - scheduling
  - overhead
  - performance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/osy/context-switch/
---

## TL;DR

A context switch is the OS operation of saving one
thread's CPU state and loading another's. It costs
1-10 microseconds for threads (register save/restore)
and up to 100 microseconds for processes (TLB flush).
High context switch rates are a common hidden cause of
application latency.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-010 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | context switch, scheduling, overhead, performance |
| **Prerequisites** | OSY-006, OSY-007, OSY-009 |

---

### The Problem This Solves

A CPU can execute only one thread at a time (per core).
Yet modern systems run thousands of threads. The OS
scheduler uses context switching to give each thread
the illusion of dedicated CPU access: each thread runs
for a brief time slice, then the OS saves its state,
loads the next thread's state, and runs that thread.

---

### What Gets Saved and Restored

```
Thread context (what the OS saves on preemption):
  - Program Counter (rip): next instruction to execute
  - Stack Pointer (rsp): current stack position
  - General registers: rax, rbx, rcx, rdx, rsi, rdi,
    r8-r15 (16 registers * 8 bytes = 128 bytes)
  - Flags register (rflags): arithmetic condition codes
  - Floating point state: xmm0-xmm15, ymm (if AVX)
    (up to 512 bytes for AVX-512 state)
  Total: ~700 bytes saved to kernel stack

Process context (additional on process switch):
  - CR3 register: pointer to page table (address space)
  - Changing CR3 = TLB flush on older CPUs
  - PCID (Process Context ID): modern CPUs use this
    to avoid full TLB flush (PCID = selective TLB use)
  
Thread context switch: ~1-10 microseconds
Process context switch: ~10-100 microseconds
  (TLB flush = all cached virtual->physical mappings gone
   = first access after switch is a TLB miss = slower)
```

---

### Context Switch Causes

```
1. Voluntary (Thread yields CPU):
   Thread calls sleep(), wait(), I/O operation, lock.acquire()
   Thread moves to BLOCKED state
   Scheduler picks next READY thread
   
2. Involuntary (Preemption by scheduler):
   Thread's time quantum expired (default 4ms in Linux)
   Higher priority thread became runnable
   Thread moves to READY state (not BLOCKED)
   
Cost breakdown:
  Save registers: ~100ns
  Kernel scheduler decision: ~500ns-1us
  Restore registers: ~100ns
  TLB invalidation (process switch): ~5-50us
  Cold cache effects after switch: ~5-100us (L1/L2 cache
    fills with new thread's working set)
  
Real cost: cache effects often dominate register save/restore
```

---

### Measuring Context Switches

```bash
# vmstat - context switches per second
vmstat 1
# cs column: context switches/second
# Healthy: < 10,000/s per CPU core
# Concerning: > 100,000/s - indicates over-threading

# pidstat - per-process context switch rate
pidstat -w -p <PID> 1
# cswch/s: voluntary context switches
# nvcswch/s: involuntary context switches (preemptions)
# High involuntary: time quantum expiring frequently
#   = threads getting preempted = latency spikes

# Per-thread in Java: JMX ThreadMXBean
ThreadMXBean mxBean = ManagementFactory.getThreadMXBean();
ThreadInfo info = mxBean.getThreadInfo(threadId);
// Blocked time reflects time waiting + context switch cost
```

---

### Context Switch and JVM Latency

```
Problem: Java HTTP server p99 latency spikes
Diagnosis:
  vmstat 1 -> cs column spikes to 200,000/s
  pidstat -w -> nvcswch/s (involuntary) is high
  
Root cause: Thread pool has 500 threads, server has
  8 CPU cores. 500/8 = 62 threads per core competing.
  Each 4ms quantum = ~6ms to run all 62 = threads
  experience 60ms scheduling delay (p99 = 60ms latency)
  
Fix: Reduce thread pool size to 8-32 threads.
  Use async I/O (WebFlux, or Java 21 virtual threads)
  to avoid blocking OS threads on I/O wait.
  Result: context switches drop from 200K/s to 20K/s
          p99 drops from 60ms to 5ms
```

---

### Textbook Definition

A context switch is the process of saving the execution
state (CPU registers, program counter, stack pointer)
of the currently running thread and loading the execution
state of the next scheduled thread. The OS kernel
performs context switches during preemption (time
quantum expiry) and when a thread voluntarily yields
the CPU (waiting for I/O or a lock).

---

### Understand It in 30 Seconds

Imagine switching musicians in a concert: the performer
stops playing, puts down their sheet music (saves
registers), hands the instrument to the next performer,
who picks up their sheet music (restores registers) and
continues exactly where they were in their piece.
The concert (CPU) can only have one performer at a time,
but many get turns.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Context switches only happen between different processes" | Context switches happen between threads - which can be within the same process. A Java application context switches between its own threads constantly |
| "Virtual threads (Java 21) eliminate context switches" | Virtual threads reduce OS-level context switches by multiplexing many virtual threads onto few OS threads. But the OS still context switches between those few OS threads. Total switches decrease significantly |
| "Context switch cost is fixed at 1 microsecond" | Register save/restore: ~200ns. But cache eviction and TLB effects can add 5-50x more. True cost depends on cache temperature and working set size |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Context switch storm | p99 latency spikes, CPU high but throughput low | Thread pool too large, threads all compete for CPU | Reduce thread pool to 2x core count for I/O-bound |
| Lock convoy | High `nvcswch/s` | Threads waiting for single hot lock | Use ConcurrentHashMap, segment locks, lock-free structures |
| Latency tail | Intermittent 10-50ms spikes | Involuntary preemption during request processing | Real-time scheduling class (SCHED_FIFO) for latency-critical threads |
| Security | Thread timing attack | Context switch timing reveals information | Constant-time algorithms for security-sensitive operations |

---

### Related Keywords

**Prerequisites:** OSY-006 (Process), OSY-007 (Thread)

**Next steps:** OSY-011 (CPU Scheduling), OSY-065 (CFS Internals)

**Advanced:** OSY-099 (Context Switch Measurement),
OSY-109 (Diagnosing High Context Switches in JVM)

---

### Quick Reference Card

| Metric | Value |
|--------|-------|
| Thread context switch cost | 1-10 microseconds |
| Process context switch cost | 10-100 microseconds (TLB) |
| vmstat cs column | total context switches/second |
| Healthy cs rate | < 10K/s per CPU core |
| Linux default time quantum | 4ms (CFS-based, variable) |

---

### The Surprising Truth

Go's goroutine scheduler was designed specifically to
minimize OS context switches. A Go program with 100,000
goroutines might use only 8 OS threads (one per core),
each doing ~12,500 goroutine switches. These goroutine
switches are user-space context switches (GOMAXPROCS
cooperative switching) costing ~200ns each - 5-50x
cheaper than OS kernel context switches. This is why
Go can handle 100,000 concurrent requests on a single
machine where Java (with 100,000 OS threads) would be
paralyzed by context switch overhead. Java 21 virtual
threads achieve the same goal with the same JVM-level
cooperative scheduling mechanism.

---

### Mastery Checklist

- [ ] Knows what CPU state is saved on context switch (registers)
- [ ] Understands why process switch costs more than thread switch
- [ ] Can use vmstat to measure context switch rate
- [ ] Knows the relationship between thread count and context switch overhead
- [ ] Can explain voluntary vs involuntary context switch
