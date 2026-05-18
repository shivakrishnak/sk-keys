---
id: OSY-022
title: Top 10 OS Interview Questions (Foundational)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006, OSY-007, OSY-009, OSY-010, OSY-012, OSY-017
used_by: []
related: OSY-042, OSY-081, OSY-114
tags:
  - interview
  - foundational
  - questions
  - preparation
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/osy/interview-foundational/
---

## TL;DR

These 10 questions are asked in every junior-to-mid
backend interview. Each tests a specific OS concept.
Knowing WHY the concept exists (not just the definition)
distinguishes strong candidates from weak ones.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-022 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | interview, foundational questions |
| **Prerequisites** | OSY-006 through OSY-020 |

---

### The 10 Questions

**Q1: What is the difference between a process and a thread?**

```
What they want to hear:
  Process: isolated address space, own PID, own file descriptors.
  Thread: shares address space with its siblings, own stack/PC.
  Key distinction: isolation vs sharing.
  
Strong answer adds:
  Process switch is more expensive (TLB flush, address space change).
  Thread communication is faster (shared heap) but requires sync.
  Java: JVM = 1 process, Spring request handlers = multiple threads.
```

**Q2: What is a context switch and when does it happen?**

```
What they want to hear:
  OS saves current thread's registers + PC, loads another thread's.
  Happens: time quantum expiry, I/O blocking, yield, sleep.
  Cost: 1-10us for thread, 10-100us for process.
  
Strong answer adds:
  vmstat cs column measures context switches.
  High context switch rate = too many threads for core count.
  Virtual threads reduce OS context switches.
```

**Q3: Explain virtual memory. Why does it exist?**

```
What they want to hear:
  Each process gets own virtual address space.
  MMU maps virtual to physical; TLB caches mappings.
  Benefits: isolation, larger-than-RAM programs, overcommit.
  
Strong answer adds:
  VIRT vs RSS in ps - VIRT is claimed virtual memory, RSS is real.
  Page fault: accessing unmapped page -> kernel allocates physical.
  Swap: physical page moved to disk when RAM full -> performance cliff.
```

**Q4: What is a system call? Give 3 examples.**

```
What they want to hear:
  User space to kernel space transition for privileged operations.
  Examples: read(), write(), fork(), open(), socket()
  Costs: ~100-300ns without I/O, microseconds to milliseconds with I/O.
  
Strong answer adds:
  SYSCALL instruction on x86-64 triggers Ring 3 -> Ring 0 transition.
  strace -p <PID> shows all system calls in real time.
  io_uring batches syscalls for high-throughput I/O.
```

**Q5: What is a deadlock? How do you detect it?**

```
What they want to hear:
  4 Coffman conditions: mutual exclusion, hold-and-wait,
  no preemption, circular wait. All four must hold.
  Detection: jstack (Java), thread dump shows BLOCKED threads.
  Prevention: lock ordering (always acquire in same order).
  
Strong answer adds:
  Java ThreadMXBean.findDeadlockedThreads()
  Live deadlock example: A holds lock1, wants lock2;
  B holds lock2, wants lock1.
```

**Q6: What is a race condition?**

```
What they want to hear:
  Two threads access shared data without sync; result depends
  on execution order. Example: balance = balance - withdrawal
  (3 instructions: load, subtract, store - not atomic).
  
Strong answer adds:
  Java solutions: synchronized, AtomicInteger, volatile for visibility.
  Detection: ThreadSanitizer (-fsanitize=thread), Helgrind, Java:
  -XX:+UseHelgrind (via Valgrind), code review.
```

**Q7: What are the differences between mutex, semaphore, and monitor?**

```
What they want to hear:
  Mutex: binary, owned by one thread, only owner can unlock.
  Semaphore: counting, any thread can signal.
  Monitor: mutex + condition variable (Java synchronized object).
  
Strong answer adds:
  Java synchronized = monitor (mutex + wait/notify).
  ReentrantLock = mutex with tryLock, timed lock.
  Semaphore: use for rate limiting, connection pool size.
```

**Q8: What is the kernel vs user space distinction?**

```
What they want to hear:
  Kernel space: Ring 0, full hardware access, OS kernel.
  User space: Ring 3, restricted, applications.
  Boundary crossed by: system calls, interrupts, faults.
  
Strong answer adds:
  Meltdown (2018): speculative execution violated this boundary.
  KPTI fix: 5-30% performance regression for I/O-heavy workloads.
  seccomp: applications can restrict their own syscall set.
```

**Q9: Explain paging and virtual memory translation.**

```
What they want to hear:
  Virtual address -> MMU -> page table lookup -> physical address.
  Page = 4KB chunk of memory.
  TLB caches recent translations (1 cycle vs 50-100 cycles for miss).
  
Strong answer adds:
  Huge pages (2MB) reduce TLB pressure for large JVM heaps.
  Page fault: accessing unmapped page -> kernel trap -> allocate frame.
  Copy-on-write: fork() shares pages until written (cheap fork).
```

**Q10: What is scheduling and how does Linux schedule threads?**

```
What they want to hear:
  Scheduler decides which thread runs on which CPU core.
  Linux CFS: Completely Fair Scheduler, uses red-black tree
  sorted by virtual runtime. Low vruntime = run next.
  Time quantum: ~4ms default, then preempt.
  
Strong answer adds:
  Nice value: -20 (most favored) to +19 (least favored).
  SCHED_FIFO: real-time scheduling, no preemption by CFS.
  Too many threads: context switch overhead dominates.
```

---

### Interview Success Patterns

```
Pattern 1: Always explain WHY before WHAT
  Weak: "Virtual memory is a technique where..."
  Strong: "Virtual memory exists because multiple processes
           can't safely share physical RAM without isolation.
           It provides each process its own address space..."

Pattern 2: Give a production example
  Every OS concept has a Java/production manifestation:
    Context switch -> thread pool sizing
    Deadlock -> jstack output
    OOM -> container memory limits + OOM killer

Pattern 3: Know the failure mode
  Interviewer: "What can go wrong with mutexes?"
  Answer: "Deadlock (circular wait), priority inversion
           (low-priority thread holds lock needed by high-priority),
           and lock contention (high-concurrency starvation)."
```

---

### Mastery Checklist

- [ ] Can answer all 10 questions fluently (< 2 minutes each)
- [ ] Includes production examples in every answer
- [ ] Knows the failure mode for each concept
- [ ] Can explain concepts both bottom-up (mechanism) and top-down (why)
