---
id: OSY-075
title: Thread-per-Request Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-022, OSY-023, OSY-068
used_by: []
related: OSY-068, OSY-111, OSY-099
tags:
  - anti-pattern
  - thread-per-request
  - C10K
  - context-switch
  - virtual-threads
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 75
permalink: /technical-mastery/osy/thread-per-request-anti-pattern/
---

## TL;DR

Thread-per-request: one OS thread per incoming request.
Fails at scale: 10K concurrent requests = 10K threads,
10GB stack RAM, constant context switching. The OS was
never designed for 10K+ running threads. Modern solutions:
async/reactive (NIO + epoll) or Java virtual threads
(Java 21+). Understanding WHY this fails is foundational
to understanding Netty, Reactor, and Node.js architecture.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-075 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | thread-per-request, C10K, virtual threads, reactive, context switch |
| **Prerequisites** | OSY-022, OSY-023, OSY-068 |

---

### Why Thread-per-Request Fails at Scale

```
Resources consumed per OS thread:
  Stack memory: 1MB per thread (JVM default: -Xss1m)
  Kernel data structures: ~8KB (task_struct)
  TLS (Thread Local Storage): varies
  
  100 threads: ~100MB RAM (manageable)
  1000 threads: ~1GB RAM (acceptable)
  10000 threads: ~10GB RAM (problematic)
  100000 threads: ~100GB RAM (impossible)
  
Context switch overhead:
  OS switches between threads every few milliseconds (timeslice)
  
  Context switch cost: 1-10 microseconds
    Save: registers, PC, stack pointer, FPU state
    Load: next thread's state
    Pipeline flush, TLB invalidation
    
  10000 threads * 1000 switches/sec = 10M context switches/sec
  At 10 microseconds each: 100% CPU just doing switches!
  No CPU left for actual work.
  
Thread scheduling overhead:
  Linux O(1) scheduler: O(1) select next thread to run
  But: waking a sleeping thread requires:
    futex_wake() syscall
    Move thread from wait queue to run queue
    Potentially preempt current thread
    Context switch to new thread
  Under 10K concurrent I/O-blocked threads:
    Thousands of wake events per second
    Each triggering context switches
```

---

### The C10K Problem (1999)

```
C10K: "How to handle 10,000 concurrent connections"
Published by Dan Kegel in 1999
  
At the time:
  1999: Web servers using Apache's prefork model
  Apache: one process (or thread) per connection
  Hardware: 256MB RAM, single-core 500MHz CPU
  10K connections * 1MB stack = 10GB RAM (impossible in 1999)
  
Solutions explored:
  1. epoll/kqueue: O(1) event notification (Linux 2002, BSD 1999)
  2. Non-blocking I/O + event loop: handle many connections per thread
  3. Async programming models (callbacks, promises)
  
Modern C10K solutions:
  Nginx: event-driven; 1 process per CPU; handles 100K+ connections
    Each worker: epoll event loop; no thread per connection
    
  Node.js: single event loop; epoll under the hood
    "I/O-bound" apps: V8 thread handles 10K requests concurrently
    
  Netty (Java): NioEventLoopGroup; each loop = one thread with epoll
    Handles 10K+ connections per thread (I/O phase)
    Worker thread pool for actual business logic
    
  Spring WebFlux / Project Reactor:
    Reactive streams; non-blocking; Netty under the hood
    
  Java Virtual Threads (Java 21+):
    Millions of virtual threads on few OS threads
    Write blocking code; JVM multiplexes onto OS threads
    Best of both worlds: simple code + high scalability
```

---

### Thread-per-Request: When It's Fine

```
Thread-per-request WORKS when:
  
  Low concurrency: < 200 concurrent requests
    Traditional Spring MVC with Tomcat: 200 threads default
    Each handles one request; blocking is fine
    Works perfectly for typical enterprise apps
    
  CPU-bound work:
    More threads than CPU cores = no benefit (worse)
    Thread-per-request with CPU work: use thread pool = CPU count
    
  Simple CRUD services:
    Most Java microservices: < 100 concurrent
    Thread-per-request with 50 thread pool = perfectly fine
    Don't over-engineer: add complexity only when needed
    
Thread-per-request FAILS when:
  Long-lived connections (WebSocket, SSE): 1 thread forever
  Thousands of concurrent slow requests (slow clients, large payloads)
  I/O fan-out: one request triggers 10 parallel I/O calls
    10K requests * 10 I/O calls each = 100K waiting threads
    
Decision rule:
  Expected concurrent connections:
    < 1000: thread-per-request works (simpler code, clear reasoning)
    1000-10000: tune thread pool; possibly async for I/O hot paths
    > 10000: reactive/virtual threads; thread-per-request won't scale
```

---

### Virtual Threads (Java 21): The Solution

```java
// Before Java 21: thread pool limits scalability
// Executor with 200 threads -> 200 max concurrent requests
ExecutorService pool = Executors.newFixedThreadPool(200);
pool.submit(() -> {
    // This thread: blocked during DB query, HTTP call, etc.
    // 200 threads = 200 concurrent requests max
    String result = database.query("SELECT ...");  // blocks!
    return result;
});

// Java 21 virtual threads: 1M concurrent "threads" on 8 OS threads
ExecutorService vpool = Executors.newVirtualThreadPerTaskExecutor();
vpool.submit(() -> {
    // Virtual thread: looks like blocking code to developer
    // JVM: when this virtual thread blocks (DB, HTTP, file):
    //   1. Parks virtual thread (removes from OS thread)
    //   2. Mounts another runnable virtual thread on same OS thread
    //   3. OS thread continues; JVM multiplexes virtual threads
    String result = database.query("SELECT ...");  // "blocks" but doesn't!
    return result;
});
// 1M concurrent virtual threads -> 8 OS threads (CPU count)
// Memory: virtual thread stack ~few KB (vs 1MB for OS thread)
// JDK 21: Tomcat and Spring Boot support virtual threads natively

// Spring Boot 3.2+ with virtual threads:
// server.tomcat.threads.virtual=true  # in application.properties
// Now thread-per-request scales like reactive! Simple code, high scale.
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Thread-per-request is always bad and should always be avoided" | Thread-per-request is perfectly fine for most microservices with < 500 concurrent requests. The complexity of reactive/async code is a real cost. Only switch to reactive or virtual threads when you have measured evidence of thread pool saturation. Most enterprise Java services never hit the ceiling of a 200-thread pool |
| "Virtual threads solve all scalability problems" | Virtual threads excel for I/O-bound work (network, database, file). They do NOT help for CPU-bound work: 1M virtual threads computing prime numbers still uses only CPU-count OS threads. Virtual threads also don't help if you use synchronized blocks pinning virtual threads to OS threads (use ReentrantLock instead) |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Thread stack | 1MB per OS thread (JVM default) |
| 10K threads | ~10GB RAM + constant context switch overhead |
| C10K solution | epoll event loop + non-blocking I/O |
| Reactive (Netty) | 1 OS thread per CPU handles 100K connections (I/O bound) |
| Virtual threads (Java 21) | Write blocking code; JVM multiplexes onto OS threads |
| When thread-per-request is fine | < 500 concurrent, typical CRUD; don't over-engineer |
