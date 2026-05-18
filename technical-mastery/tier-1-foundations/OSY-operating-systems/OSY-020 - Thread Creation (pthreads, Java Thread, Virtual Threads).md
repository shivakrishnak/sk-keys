---
id: OSY-020
title: "Thread Creation (pthreads, Java Thread, Virtual Threads)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-007
used_by: OSY-038, OSY-041
related: OSY-007, OSY-019, OSY-040
tags:
  - foundational
  - thread-creation
  - pthreads
  - java-thread
  - virtual-threads
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/osy/thread-creation/
---

## TL;DR

Thread creation uses clone() syscall (Linux) to create
a kernel thread sharing the parent's address space.
Java OS threads wrap pthreads. Java 21 virtual threads
use JVM-level cooperative scheduling and are ~1000x
cheaper to create than OS threads.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-020 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | thread creation, pthreads, virtual threads, clone() |
| **Prerequisites** | OSY-007 |

---

### Thread Creation at the OS Level

```
Linux thread creation syscall: clone()
  (fork() is actually clone() with specific flags)
  
clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND
     | CLONE_THREAD, ...)
  
CLONE_VM:      share virtual memory (heap, code)
CLONE_FS:      share filesystem state (cwd)
CLONE_FILES:   share file descriptor table
CLONE_SIGHAND: share signal handlers
CLONE_THREAD:  same thread group (same PID, new TID)

Result:
  New kernel task_struct created (PCB for thread)
  New TID assigned
  New stack allocated (1MB-8MB from virtual address space)
  Added to run queue
  
Cost: ~10-50 microseconds to create an OS thread
  (kernel allocation, stack setup, scheduler admission)
```

---

### Java Thread Creation Models

```java
// MODEL 1: OS Thread (1:1 mapping to kernel thread)
// Cost: ~10-50us to create, ~1MB stack per thread
Thread osThread = new Thread(() -> {
    System.out.println("OS thread: TID = " +
        Thread.currentThread().threadId());
});
osThread.start(); // Creates kernel thread via clone()

// Practical limit: ~10,000 OS threads per JVM (stack memory)
// 10,000 threads * 1MB stack = 10GB virtual memory

// MODEL 2: Thread Pool (OS threads, reused)
// Best for CPU-bound work (I/O bound wastes blocked threads)
ExecutorService pool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors());
pool.submit(() -> cpuIntensiveWork());

// MODEL 3: Virtual Thread (Java 21, JEP 444)
// Cost: ~200ns to create, ~few KB stack per thread
// Backed by a shared pool of OS carrier threads
Thread vt = Thread.ofVirtual().start(() -> {
    // Looks like blocking code:
    String data = ioOperation(); // blocks? No!
    // Virtual thread parks on I/O, OS carrier thread
    // moves to next virtual thread. Resumes when I/O done.
});

// Create 1 million virtual threads? Fine:
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 1_000_000).forEach(i ->
        executor.submit(() -> simulateRequest(i)));
} // Waits for all to complete
```

---

### Virtual Threads vs OS Threads Comparison

| Aspect | OS Thread | Virtual Thread |
|--------|-----------|---------------|
| Creation cost | ~10-50 microseconds | ~200 nanoseconds |
| Stack size | 512KB-8MB (fixed) | ~few KB (grows dynamically) |
| Max practical count | ~10,000 per JVM | ~millions per JVM |
| Blocking I/O behavior | OS thread blocked | Parks; carrier thread free |
| CPU-bound suitability | Yes | Same as OS thread |
| Available since | Java 1.0 | Java 21 |

---

### Textbook Definition

Thread creation allocates a new stack and creates a
kernel scheduler entity (kernel thread on Linux via
`clone()`). Java OS threads map 1:1 to kernel threads.
Java 21 virtual threads are JVM-managed lightweight
threads multiplexed over a pool of OS carrier threads,
created at the JVM level without necessarily creating
a new kernel thread.

---

### Understand It in 30 Seconds

OS thread = hiring a new full-time employee (expensive,
permanent overhead). Virtual thread = hiring a
contractor who only bills for actual work time (cheap,
immediate). The contractor uses the same office desk
(OS carrier thread) as others, just at different times.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Virtual threads are green threads (old Java pre-JDK 1.2)" | Green threads (JDK 1.1) were M:1 (all Java threads on 1 OS thread = no true parallelism). Virtual threads are M:N (many virtual threads on N OS threads = true parallelism). Completely different |
| "Virtual threads work well for CPU-bound work" | Virtual threads have same per-CPU performance as OS threads for CPU-bound work. The benefit is for I/O-bound work: virtual threads don't waste OS threads on I/O blocking |

---

### Mastery Checklist

- [ ] Knows OS thread creation uses clone() syscall with CLONE_VM flag
- [ ] Understands the 3 Java thread models (OS thread, pool, virtual)
- [ ] Can explain why virtual threads handle I/O better than OS threads
- [ ] Knows virtual thread creation cost (~200ns vs ~50us for OS thread)
