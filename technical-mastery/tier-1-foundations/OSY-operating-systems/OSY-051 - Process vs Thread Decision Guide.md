---
id: OSY-051
title: Process vs Thread Decision Guide
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-006, OSY-007, OSY-019, OSY-020
used_by: []
related: OSY-007, OSY-035, OSY-040
tags:
  - process
  - thread
  - decision-guide
  - isolation
  - comparison
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/osy/process-vs-thread-decision/
---

## TL;DR

Use a separate process when you need fault isolation
(crash doesn't kill parent) or different memory space
(security boundary). Use threads when you need shared
state and low communication overhead. Virtual threads
(Java 21) collapse the thread overhead argument. For
modern Java services, threads win almost everywhere.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-051 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | process vs thread, decision guide, isolation |
| **Prerequisites** | OSY-006, OSY-007, OSY-019, OSY-020 |

---

### Key Dimensions of Choice

**Isolation**

```
Process:
  Separate virtual address space
  Crash of child: parent continues (fork() + waitpid())
  Separate file descriptor table
  OS can kill child without affecting parent
  
Thread:
  Shared address space with all threads
  Crash (SIGSEGV, uncaught exception) in any thread
    = JVM exits (kills ALL threads)
  Shared file descriptors
  
For JVM:
  JVM exception in thread: caught by Thread.UncaughtExceptionHandler
  Only native code crash (SIGSEGV) kills the JVM process
  
When to choose process isolation:
  - Executing untrusted or third-party code
  - Legacy native libraries with known memory bugs
  - Components requiring different JVM settings (-Xmx, GC tuning)
  - Microservices (each service in own container = process)
```

**Communication**

```
Process communication:
  IPC: pipes, sockets, message queues, shared memory
  Overhead: syscall boundary + data copy (except shared memory)
  Complexity: serialization, protocol design
  
Thread communication:
  Shared heap variables (direct memory access)
  No copy needed
  Overhead: lock acquisition (~10-100ns)
  Risk: race conditions (requires careful synchronization)
  
When thread communication wins:
  Frequent small data exchange (order details, user session)
  Low latency required (microsecond-level messaging)
  Tight coupling between operations (transaction processing)
```

**Resource Usage**

```
Process:
  Separate page table (fork copies page table, not pages)
  Separate kernel task_struct per process
  fork() + exec() = 0.5-5ms (page table copy + exec setup)
  Memory: separate virtual space (but shared code pages via COW)
  
Thread:
  Shared page table (no copy on creation)
  Separate kernel task_struct per thread (lightweight clone)
  Thread creation: 10-50us (much faster than fork)
  Memory: shared heap, separate stack (~1MB per thread)
  
Virtual thread (Java 21):
  Managed by JVM, not OS
  Creation: ~200ns
  Memory: ~few KB per virtual thread
  OS sees: N carrier threads for M virtual threads
```

---

### Decision Framework

```
Use SEPARATE PROCESS when:
  1. Fault isolation critical
     (crash in component must not affect main service)
  2. Different privilege levels needed
     (helper needs root, main app should not have root)
  3. Scaling independently
     (microservices: each in own container/process)
  4. Language/runtime boundary
     (Python script called from Java service)
  5. Untrusted code execution
     (sandbox: seccomp filter applied to child process only)

Use THREAD when:
  1. Shared state needed (session, cache, connection pool)
  2. Low-latency communication (in-memory method call)
  3. Parallel computation on shared data (GC, parallel streams)
  4. Single JVM scope (Spring beans, JPA entity manager)

For Java services in 2024+:
  Almost always: threads (or virtual threads) within one JVM
  Process boundary: between microservices (Docker containers)
  Inside service: threads (never separate JVM processes per request)
```

---

### Comparison Table

| Dimension | Process | Thread | Virtual Thread |
|-----------|---------|--------|---------------|
| Fault isolation | Full | None | None (same JVM) |
| Memory share | No (COW) | YES | YES (same JVM) |
| Creation cost | ~1ms (fork+exec) | ~50us | ~200ns |
| Communication | IPC (~us-ms) | Shared mem (~ns) | Shared mem (~ns) |
| Context switch | ~50-100us | ~1-10us | ~1us (cooperative) |
| Memory per unit | ~MB (own page table) | ~1MB (stack) | ~few KB |
| Security boundary | YES | No | No |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Separate processes are safer for all use cases" | Process isolation prevents crash propagation but adds communication overhead, serialization, and complexity. For most backend services, threads within one well-monitored JVM are safer and simpler to reason about than distributed processes |
| "Virtual threads are like lightweight processes" | Virtual threads are JVM-managed threads, not processes. They share the same address space as all other threads in the JVM. They provide low-cost concurrency but no fault isolation |

---

### Quick Reference Card

| Need | Use |
|------|-----|
| Crash isolation | Separate process (child crash doesn't kill parent) |
| Shared state | Thread (same heap) |
| Language boundary | Separate process + IPC |
| High concurrency, I/O-bound | Virtual threads (Java 21) |
| CPU-bound parallel | OS thread pool (N = cores) |
| Microservice | Each service = separate process in container |
| Single service | Threads within one JVM |
