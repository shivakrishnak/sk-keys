---
id: OSY-139
title: JVM Performance Mental Model
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-085, OSY-125, OSY-138
used_by: []
related: OSY-125, OSY-138, OSY-140
tags:
  - JVM
  - mental-model
  - performance
  - memory
  - OS
  - synthesis
  - META
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 139
permalink: /technical-mastery/osy/jvm-performance-mental-model/
---

## TL;DR

A complete mental model of how JVM performance maps to OS
primitives: what happens at the OS layer for every JVM
operation. When you understand this model, performance
problems have traceable root causes rather than mysterious
symptoms. The model: JVM heap = OS pages, JVM threads = OS
threads, JVM GC = madvise/mremap, JVM I/O = syscalls.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-139 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | JVM mental model, OS mapping, performance synthesis, Java OS interaction |
| **Prerequisites** | OSY-085, OSY-125, OSY-138 |

---

### The Complete JVM-OS Mapping

```
Every JVM operation maps to one or more OS operations:

JVM: new Object()
  OS: (usually) none - object allocated on JVM heap
  JVM heap: OS pages already allocated; just write to them
  If heap expansion needed: brk() or mmap() syscall
  
JVM: GC (minor collection - young generation)
  OS: memory access to young generation pages
  If compact: mremap() to rearrange memory regions
  Objects freed: OS pages NOT returned (JVM holds them for future)
  
JVM: GC (major/full collection)
  OS: access to all live heap pages
  Memory returned to OS: madvise(MADV_DONTNEED) for freed regions
  THP: may trigger THP collapse during region allocation
  
JVM: Thread.start()
  OS: clone() syscall (creates new OS thread)
  Memory: new stack allocated (~512KB-1MB native memory, not heap)
  
JVM: synchronized block enter
  OS: futex() - if lock is uncontested (fast path: user-space only)
  OS: futex() with FUTEX_WAIT - if contended (sleeps; kernel involvement)
  
JVM: Thread.sleep(1000)
  OS: nanosleep() syscall
  Thread: moved to TIMED_WAITING; removed from run queue
  After 1s: kernel wakes thread; moves back to runnable queue
  
JVM: Files.read(path, buf)
  OS: openat() -> read() syscalls
  If data in page cache: kernel copies from page cache to buf
  If cache miss: kernel reads from block device; then copies
  
JVM: socket.read() (blocking)
  OS: read() syscall
  Thread: blocks in kernel (TASK_INTERRUPTIBLE)
  On data arrival: kernel interrupt -> wake thread
  
JVM: Thread.yield()
  OS: sched_yield() syscall
  Current thread: goes to end of run queue for its priority
  
JVM: System.exit(0)
  OS: exit_group() syscall
  All threads: terminated; memory freed; file descriptors closed
  
JVM: Runtime.gc()
  OS: no direct syscall (GC is in-process)
  GC phases: madvise() to release pages back to OS
  
JVM: direct ByteBuffer (off-heap)
  OS: mmap() allocation
  NOT on heap: not GC-managed
  Freed: when GC collects the ByteBuffer object; or explicit free()
```

---

### JVM Memory = OS Memory in Layers

```
When you allocate -Xmx4g, what actually happens at OS level:

  JVM startup:
    java process: fork()/exec() from shell
    -Xmx4g: JVM asks OS to mmap() 4GB of virtual address space
    Virtual: reservation only; no physical pages yet
    RSS: small (just JVM binary + JIT metadata + thread stacks)
    
  As application runs:
    new Object(): writes to already-mmap'd address
    First write to a page: page fault -> OS allocates physical page
    RSS grows: each new physical page = more RSS
    
  At full heap:
    RSS: approximately -Xmx + native memory (~1-3GB extra)
    Physical pages: 4GB of application data in kernel page tables
    
  During GC:
    Dead objects: GC marks their pages
    madvise(MADV_DONTNEED): OS can reclaim those pages
    RSS decreases: OS reclaims physical pages
    Virtual address space: unchanged (JVM holds virtual reservation)
    Next allocation: page fault again on same virtual address
    
  Key insight:
    VMSize > RSS > heap usage
    VMSize: all virtual addresses reserved (including mmap, stacks, JDK)
    RSS: physical pages currently in RAM (working set)
    Heap usage (jstat): bytes of heap used by live objects
    
  Relationship in practice (4GB heap JVM):
    heap used: 2GB (jstat)
    heap committed: 3.5GB (OS pages for JVM heap)
    RSS: 5GB (3.5 heap + 1.5 native: thread stacks, JIT code, etc.)
    VMSize: 12GB+ (virtual reservations, most unmapped)
```

---

### JVM Thread Scheduling = OS Scheduling

```
JVM thread states (java.lang.Thread.State) map to OS states:

  JVM RUNNABLE:
    Either: actually running on a CPU core (OS TASK_RUNNING, on CPU)
    Or: ready to run, waiting for CPU (OS TASK_RUNNING, in run queue)
    Can't distinguish from Java without perf/top
    
  JVM BLOCKED:
    Waiting for synchronized monitor
    OS state: TASK_INTERRUPTIBLE (in kernel wait queue for futex)
    CPU: 0% while blocked
    
  JVM WAITING:
    Object.wait(), Thread.join() with no timeout, LockSupport.park()
    OS state: TASK_INTERRUPTIBLE (in wait queue)
    CPU: 0% while waiting
    
  JVM TIMED_WAITING:
    Thread.sleep(), Object.wait(timeout), LockSupport.parkNanos()
    OS state: TASK_INTERRUPTIBLE with timeout
    CPU: 0% while sleeping
    
  JVM TERMINATED:
    Thread finished; OS thread exited; memory freed
    
  What vmstat cs (context switches) actually counts:
    Voluntary: JVM thread goes RUNNABLE -> BLOCKED/WAITING (futex wait)
    Involuntary: OS preempts a RUNNABLE thread to schedule another
    
  High voluntary cs: many threads blocking on locks or I/O
  High involuntary cs: too many threads competing for CPU
```

---

### The Diagnostic Mapping

```
Given a symptom: find the OS root cause

Symptom: "Unexpected GC pauses (100ms+)"
  OS mapping check:
    Is THP enabled (always or madvise)?
    -> madvise: khugepaged collapse during GC region allocation
    -> Fix: THP=madvise for JVM heap explicitly, or disable THP
    
    Is NUMA mismatch happening?
    -> numastat -p $PID: check cross-NUMA memory access
    -> Fix: -XX:+UseNUMA or numactl --membind
    
    CPU steal time?
    -> top: check %st column
    -> GC threads preempted by hypervisor during STW pause
    -> Fix: dedicated host or fewer co-tenants

Symptom: "Latency spikes at irregular intervals (10-30s)"
  OS mapping check:
    Dirty page flush spike?
    -> iostat: periodic %util=100% for ~10s every 30s
    -> vmstat bo: large bo value periodically
    -> Fix: vm.dirty_background_ratio=2, vm.dirty_ratio=5
    
    Swap?
    -> free -h: any swap used?
    -> GC pause extended by swapping heap pages to disk
    -> Fix: vm.swappiness=1; ensure -Xmx fits in available RAM

Symptom: "Container OOM killed despite -Xmx set"
  OS mapping check:
    RSS > container limit?
    -> Native memory exceeded container cgroup limit
    -> jcmd VM.native_memory: find large section
    -> Fix: reduce MaxRAMPercentage; check thread count; check Metaspace

Symptom: "Service slow but CPU only 30%"
  OS mapping check:
    vmstat wa% high?
    -> iowait: disk is bottleneck
    -> iostat: find saturated device
    
    vmstat cs high?
    -> Context switches: too many blocking threads
    -> Thread dump: look for BLOCKED/WAITING
    
    Load average >> CPU count?
    -> Run queue full: threads waiting for CPU
    -> But CPU seems low: could be I/O wait inflating load average
```

---

### Mental Model Summary

| JVM Concept | OS Primitive | Diagnostic Tool |
|-------------|--------------|-----------------|
| Heap allocation | mmap + page fault | /proc/$PID/status VmRSS |
| GC release | madvise(MADV_DONTNEED) | vmstat, RSS trend |
| Thread creation | clone() | ps, thread count trend |
| synchronized | futex() | Thread dump, vmstat cs |
| I/O operations | read/write/sendfile | iotop, strace |
| Network I/O | socket + epoll | ss, netstat |
| Thread.sleep | nanosleep | Thread dump TIMED_WAITING |
| JVM GC pause | CPU + madvise + THP | jstat, async-profiler |
| Container limit | cgroup memory.max | /sys/fs/cgroup/*/memory.current |
| NUMA mismatch | cross-socket memory | numastat -p |
