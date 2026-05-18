---
id: OSY-007
title: Thread (Definition and vs Process)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006
used_by: OSY-017, OSY-018, OSY-020, OSY-029
related: OSY-006, OSY-010, OSY-029, OSY-051
tags:
  - foundational
  - thread
  - concurrency
  - process-vs-thread
  - scheduling
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/osy/thread/
---

## TL;DR

A thread is an execution unit within a process that
shares the process's address space but has its own
stack, program counter, and CPU registers. Multiple
threads in one process share memory, enabling fast
communication at the cost of requiring synchronization.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-007 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | thread, process, concurrency, stack |
| **Prerequisites** | OSY-006 |

---

### The Problem This Solves

Processes are isolated: cross-process communication
requires IPC (pipes, sockets, shared memory) which has
overhead. For parallel work within one program that
needs to share data - like a web server handling
multiple requests while sharing a cache - threads
provide parallelism without the IPC overhead.

---

### Thread vs Process

```
PROCESS:
  Private virtual address space (memory isolation)
  Private file descriptor table
  Own PID
  Context switch: save/restore full address space (expensive)
  Communication: IPC (pipe, socket, shared memory)
  Crash isolation: process A crash doesn't kill process B
  
THREAD (within a process):
  SHARED address space (same virtual memory)
  SHARED file descriptor table
  Own stack (typically 1-8MB per thread)
  Own program counter and CPU registers
  Context switch: save/restore registers only (cheap)
  Communication: shared memory (direct pointer access)
  Crash isolation: NONE - buggy thread can corrupt all

Java analogy:
  JVM = 1 process
  Spring Boot HTTP request handling = multiple threads
  @Service bean = shared singleton in heap memory
  Thread stack = local variables per HTTP request
```

---

### Thread Data Layout

```
Process address space (shared by all threads):
┌─────────────────────────────┐ High address
│ Stack (Thread 1)            │ ← Thread 1 stack
│ Stack (Thread 2)            │ ← Thread 2 stack
│ Stack (Thread N)            │ ← Thread N stack
│ ...                         │
├─────────────────────────────┤
│ Heap (shared)               │ ← new Object() - SHARED
├─────────────────────────────┤
│ BSS (uninitialized data)    │ ← static int x; - SHARED
├─────────────────────────────┤
│ Data (initialized data)     │ ← static int y=5; - SHARED
├─────────────────────────────┤
│ Code (text segment)         │ ← program code - SHARED
└─────────────────────────────┘ Low address (0x400000)

Thread-private: stack, registers, program counter
Shared: heap, data, code
```

---

### Java Thread Types

```java
// OS Thread (1:1 with kernel thread)
Thread t = new Thread(() -> {
    // Runs as a real OS thread
    // OS sees it as a kernel-scheduled task
    System.out.println("OS thread");
});
t.start();

// Virtual Thread (Project Loom, Java 21+)
Thread vt = Thread.ofVirtual().start(() -> {
    // Lightweight: multiplexed onto OS threads
    // 10 million virtual threads possible (vs ~10K OS threads)
    // Blocks I/O without blocking OS thread
    System.out.println("Virtual thread");
});

// Thread pool (Executor - production pattern)
ExecutorService pool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors() * 2);
pool.submit(() -> handleRequest());
// NEVER create unbounded threads (OSY-111 anti-pattern)
```

---

### Textbook Definition

A thread is the smallest unit of execution within a
process. All threads of a process share the same virtual
address space, code, and heap, but each thread has its
own stack (local variables and call frames), program
counter (current instruction), and CPU registers.
The OS schedules threads independently.

---

### Understand It in 30 Seconds

A process is an office building; threads are workers
in that building. All workers share the same office
(memory, files). Each worker has their own desk
(stack). They can talk directly (shared memory) but
need to coordinate (locks) to avoid chaos.

---

### How It Works

```
Thread creation (pthreads / Java Thread.start()):
  1. OS allocates a new stack (default 1MB-8MB, platform-dependent)
  2. OS creates a kernel thread (task_struct in Linux)
  3. Thread added to run queue (READY state)
  4. Scheduler assigns CPU core when available (RUNNING)
  
Thread context switch:
  Save: program counter, stack pointer, CPU registers (16-32 regs)
  Restore: same for the next thread
  Cost: ~1-10 microseconds (TLB flush may add more)
  No address space switch (unlike process context switch)
  
Thread termination:
  Thread returns from its run() method OR calls Thread.stop() (deprecated)
  Stack memory is freed
  Thread ID (TID) released
  Parent thread can join() to wait for completion
```

---

### Complete Picture

```
Java HTTP server: 100 simultaneous requests
  JVM process: 1 (PID 42381)
  Tomcat thread pool: 200 threads (TIDs 42381-1 to 42381-200)
  Each thread:
    - Has own stack (HTTP request state, local variables)
    - Shares heap (Spring beans, caches, connection pools)
    - Shares code (servlet classes)
    
When thread accesses shared HashMap without synchronization:
  Thread 1 reads entry A
  Thread 2 deletes entry A (concurrent modification)
  Thread 1 gets null or worse: ConcurrentModificationException
  Fix: ConcurrentHashMap, synchronized, or Lock
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "More threads = more parallelism" | True only up to core count for CPU-bound work. For I/O-bound: more threads than cores can help (waiting threads don't block the CPU). But beyond the OS scheduling point: more threads = more context switch overhead = LESS throughput |
| "Virtual threads replace thread pools" | Virtual threads (Java 21) replace thread-per-request OS threads for I/O-bound work. CPU-bound work still benefits from OS thread pools sized to core count. ForkJoinPool (used by parallel streams) remains appropriate for CPU work |
| "Thread-local variables are truly private" | ThreadLocal variables are private to each thread's logical stack, but they're stored in a JVM-internal map. Memory leaks occur when ThreadLocal is not removed and threads are pooled (the thread returns to pool but keeps ThreadLocal data) |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Thread leak | Memory grows, thread count rises | New threads created but not stopped/joined | Use fixed thread pool, monitor thread count in JMX |
| Stack overflow | StackOverflowError | Infinite recursion consumes thread stack | Fix recursion; increase -Xss if deep recursive algorithm needed |
| Race condition | Random bugs, incorrect results | Shared data accessed without synchronization | Use synchronized, Lock, atomic types, or concurrent collections |
| Security | Shared thread state crosses tenant boundaries | ThreadLocal not cleared between requests | Use MDC.clear() in finally block; review thread pool lifecycle |

---

### Related Keywords

**Prerequisites:** OSY-006 (Process)

**Next steps:** OSY-017 (Mutex), OSY-020 (Thread Creation),
OSY-029 (Race Condition), OSY-038 (Thread-Safe Programming)

**Advanced:** OSY-061 (Lock-Free), OSY-063 (Condition Variables),
OSY-064 (Priority Inversion)

---

### Quick Reference Card

| Concept | Detail |
|---------|--------|
| Thread-private | Stack, registers, PC |
| Thread-shared | Heap, code, data, FDs |
| Thread vs Process switch | Thread: ~1-10us / Process: ~10-100us |
| Stack size default | 512KB-8MB (platform) |
| Java thread pool sizing | CPU-bound: nCPU; I/O-bound: nCPU * 2 |
| Virtual threads (Java 21) | Millions; I/O-bound only for full benefit |

---

### The Surprising Truth

The original Unix did not have threads. All concurrency
was achieved via processes (fork). Threads were added
to POSIX (pthreads) in 1995, 24 years after Unix was
created. The original design choice - "use processes,
not threads" - was intentional: process isolation
prevents entire classes of bugs (race conditions,
data corruption) that are inherent to shared-memory
threads. Many modern languages (Erlang, Elixir, Go
goroutines, Rust async) implement their own lightweight
thread models precisely to avoid the complexity of
OS thread synchronization.

---

### Mastery Checklist

- [ ] Can draw the process address space showing thread stacks vs shared heap
- [ ] Knows thread-private (stack, registers) vs shared (heap, code) data
- [ ] Understands why thread context switch is cheaper than process switch
- [ ] Knows Java Virtual Threads and when to use them vs OS threads
- [ ] Can explain why ThreadLocal leaks happen in thread pools
