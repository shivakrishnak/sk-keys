---
id: OSY-112
title: Expert Mastery Verification
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-001, OSY-050, OSY-100, OSY-111
used_by: []
related: OSY-113, OSY-114, OSY-115
tags:
  - mastery
  - verification
  - review
  - self-assessment
  - expert
  - checklist
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 112
permalink: /technical-mastery/osy/expert-mastery-verification/
---

## TL;DR

Expert mastery verification for OS internals: a structured
self-assessment covering all five levels of OS knowledge -
from CPU basics to fleet-scale management. Use these
scenarios to verify you can diagnose real production
issues, design OS-aware systems, and teach concepts clearly.
If you can answer all scenario questions cold: you are
genuinely expert-level.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-112 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | mastery verification, self-assessment, expert review, OS internals |
| **Prerequisites** | OSY-001, OSY-050, OSY-100, OSY-111 |

---

### Level 1 Verification: Foundations

Can you answer these without looking anything up?

```
Q1: Process vs Thread vs Goroutine vs Virtual Thread
  - What does each represent at the OS level?
  - What is shared vs isolated for each?
  - When would you choose each for a web server?
  
  Mastery indicator: you know that goroutines and virtual threads
  are multiplexed onto OS threads; explain the scheduling model.

Q2: System Call Cost
  - What happens during a system call (mode switch)?
  - What does "syscall overhead" mean in terms of CPU cycles?
  - When does syscall overhead become a bottleneck?
  
  Mastery indicator: you can explain VSYSCALL/VDSO optimization
  and when it matters (high-frequency time calls).

Q3: Page Fault Types
  - Difference between minor and major page fault?
  - When is each triggered?
  - How do you observe them in a running JVM process?
  
  Mastery indicator: you know minor = already in memory,
  just needs page table entry; major = disk I/O required.

Q4: Memory Layout of a Process
  - Draw the virtual address space layout for a Linux process
  - Where does the heap live? Stack? Shared libraries? mmap?
  - What is the kernel vs user space split (x86_64)?
  
  Mastery indicator: you know text/BSS/data/heap/mmap/stack
  arrangement; 128TB user / 128TB kernel on x86_64.

Q5: Scheduler Policy Effects
  - SCHED_FIFO vs SCHED_OTHER: when does each matter?
  - What is CFS and why was it created?
  - How does CPU pinning (taskset) help latency-sensitive apps?
```

---

### Level 2 Verification: Core Concepts

```
Q6: Virtual Memory and TLB
  - Explain a multi-level page table walk (4-level on x86_64)
  - What is a TLB miss and why is it expensive?
  - How do huge pages (2MB) reduce TLB pressure?
  
  Mastery indicator: you know that a single TLB miss can cost
  50-100 CPU cycles; huge pages reduce TLB entries needed for
  the same address range by factor of 512.

Q7: Fork and Copy-on-Write
  - What happens to memory when fork() is called?
  - Why is fork() fast despite cloning a large process?
  - What triggers the actual page copy in COW?
  
  Mastery indicator: pages marked read-only; first write
  triggers page fault -> kernel copies page -> fault resolved.

Q8: Linux File System Architecture
  - What is the VFS layer and why does it exist?
  - Difference between inode, directory entry, and file descriptor?
  - What happens when you open("/etc/passwd", O_RDONLY)?
  
  Mastery indicator: VFS abstracts different FS types;
  path resolution -> dentry cache -> inode -> open file table
  -> file descriptor table in process.

Q9: Signals and Process Control
  - What is the difference between SIGTERM and SIGKILL?
  - Why can SIGKILL not be caught or ignored?
  - What is a zombie process and when does it occur?
  
  Mastery indicator: SIGKILL handled by kernel directly
  (not delivered to process); zombie = process exited but
  parent hasn't called wait() to collect exit status.

Q10: IPC Mechanisms
  - List 6 IPC mechanisms in Linux
  - For each: typical use case and performance characteristics
  - When would you use Unix domain sockets vs shared memory?
  
  Mastery indicator: pipe, FIFO, socket, shared mem, semaphore,
  message queue; shared memory fastest (no kernel copy);
  sockets for decoupled processes; pipes for parent-child.
```

---

### Level 3 Verification: Applied OS

```
Q11: Lock Contention Diagnosis
  Scenario: Java service; 8 cores; CPU = 30%; throughput plateau
  - What tools would you use to investigate?
  - What would you look for in thread dumps?
  - What are the top 3 root causes?
  
  Mastery indicator: you immediately think thread dump + lock
  contention; look for BLOCKED threads; causes: connection pool,
  synchronized blocks, incorrect lock granularity.

Q12: Memory Pressure Diagnosis
  Scenario: RSS slowly grows by 100MB/hour; never stops growing
  - Is this definitely a memory leak? What else could it be?
  - What's the difference if it's JVM heap vs native memory?
  - How do you diagnose each?
  
  Mastery indicator: NOT necessarily a leak (could be caches,
  allocating to working set); JVM: heap dump analysis;
  native: NMT + Valgrind/jemalloc profiling.

Q13: CPU Utilization at 100%
  Scenario: a Java service shows 100% CPU on all cores
  - Is this a problem? When would 100% CPU be expected?
  - How do you find which code is running?
  - What would indicate a spinning lock vs legitimate work?
  
  Mastery indicator: 100% CPU is fine if doing real work;
  spinning lock: CPU-bound but no useful output; async-profiler
  or perf to find hot methods; lock spin -> same locking
  code appears at top.

Q14: I/O Wait in Production
  Scenario: top shows 40% iowait; app response time: 2000ms p99
  - Walk through the diagnosis from vmstat to resolution
  - What are the 3 most likely causes for a Java web service?
  - What's the fastest fix without hardware changes?
  
  Mastery indicator: vmstat -> iostat -> iotop -> identify
  process + device; Java causes: logging sync, DB random reads,
  heap dump; fastest fix: async logging or increase page cache.

Q15: OOM Kill Prevention
  Scenario: container (1GB limit) running Java service is being
  killed by OOM. -Xmx is set to 512MB.
  - Why is -Xmx insufficient to prevent OOM?
  - What other memory regions exist in a JVM?
  - What monitoring would you add to prevent recurrence?
  
  Mastery indicator: native memory (threads, NMT), Metaspace,
  direct buffers, off-heap; JVM RSS = heap + native + meta;
  monitoring: container RSS vs limit; alert at 80%.
```

---

### Level 4 Verification: Expert Applied

```
Q16: Container Security
  Scenario: you need to run an untrusted third-party Java
  service in a container on the same host as your services
  - What isolation mechanisms would you apply?
  - What syscall restrictions would you configure?
  - What monitoring would you add to detect escape attempts?
  
  Mastery indicator: seccomp profile, no-new-privileges,
  read-only filesystem, drop capabilities, non-root UID;
  audit syscalls; separate cgroup; monitor /proc/self/status.

Q17: Performance Regression Investigation
  A service went from 10ms p99 to 200ms p99 after a deployment.
  The CPU and I/O metrics are unchanged.
  - What are the 5 most likely OS-level causes?
  - How would you prove each hypothesis?
  - What deployment-related changes could cause this?
  
  Mastery indicator: lock contention (new synchronized block),
  GC pause (new allocation pattern), THP causing latency,
  NUMA allocation change, syscall rate increase; each has
  specific diagnostic tool.

Q18: Capacity Planning
  Your Java microservice currently: 10K req/s on 4 cores.
  Next quarter: 30K req/s expected.
  - How do you predict the core count needed?
  - What OS-level factors could make linear scaling fail?
  - What would you measure now to build an accurate model?
  
  Mastery indicator: CPU utilization headroom, NUMA topology,
  L3 cache saturation, lock contention points; measure:
  context switches, lock wait time, NUMA faults, LLC miss rate.
```

---

### Self-Assessment Scoring

| Score | Indicator |
|-------|-----------|
| 14-18 correct | Expert level. Can diagnose and design. |
| 10-13 correct | Advanced practitioner. Deepen L4 area. |
| 6-9 correct | Solid foundation. Strengthen L3-L4. |
| 0-5 correct | Focus on L1-L2 fundamentals first. |

---

### Common Gaps at Each Level

| Level | Most Common Gap |
|-------|----------------|
| L1 | Confusing process vs thread isolation model |
| L2 | Not knowing TLB mechanics or COW details |
| L3 | Diagnosing iowait vs memory vs lock problems |
| L4 | Container security model (seccomp, capabilities) |
| L5 | NUMA topology effects on JVM performance |

---

### Mastery Checklist

- [ ] Can diagnose high iowait, CPU steal, context switch spikes from vmstat alone
- [ ] Can read a JVM thread dump and identify root cause of contention
- [ ] Can size a thread pool correctly for mixed CPU/I/O workloads
- [ ] Can explain virtual memory, TLB, and huge pages tradeoffs
- [ ] Can design a minimal-privilege container security profile
