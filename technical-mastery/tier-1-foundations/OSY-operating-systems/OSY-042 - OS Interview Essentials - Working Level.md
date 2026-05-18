---
id: OSY-042
title: OS Interview Essentials - Working Level
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-022, OSY-026, OSY-027, OSY-029, OSY-030, OSY-037
used_by: []
related: OSY-022, OSY-081, OSY-114
tags:
  - interview
  - working-level
  - questions
  - preparation
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/osy/interview-working-level/
---

## TL;DR

Working-level OS interview questions test your ability
to apply OS concepts to real production problems. These
go beyond definitions into: diagnosis, trade-off
analysis, and root cause reasoning. Standard for mid-
level to senior backend engineers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-042 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | interview, working level, production diagnosis |
| **Prerequisites** | OSY-026 through OSY-040 |

---

### Working-Level Question Bank

**Q1: A Java service uses 100% CPU but handles very
few requests. What do you suspect?**

```
Strong answer:
  Three main causes to distinguish:
  
  1. Tight busy-wait loop (thread spin-waiting)
     Diagnosis: top -H -p PID shows one thread at 100% CPU
     jstack: thread shows RUNNABLE in a non-useful loop
     Fix: replace busy-wait with BlockingQueue or Condition.await()
     
  2. GC thrashing (Java-specific)
     Diagnosis: jstat -gc PID 1s shows high GC time (GCT column)
     Free heap < 10% of total heap = continuous GC
     Fix: increase -Xmx, fix memory leak, tune GC
     
  3. Actual CPU-intensive computation
     Diagnosis: jstack profiling shows actual work (hash, crypto, etc.)
     Fix: optimize algorithm, parallelize, cache results
     
  4. JIT compilation storm (startup)
     Diagnosis: -XX:+PrintCompilation shows heavy compilation
     Fix: JVM warmup, use AOT (-XX:+UseGraalVM NativeImage)
```

**Q2: Your application handles 1,000 RPS fine but
degrades badly at 2,000 RPS. What OS-level issues
could cause this?**

```
Strong answer (structured by resource):

CPU:
  - Thread pool exhausted: requests queue, latency spikes
    Diagnosis: thread pool queue depth metric growing
    Fix: increase thread pool or switch to virtual threads
    
  - Context switch explosion: too many OS threads
    Diagnosis: vmstat 1 shows cs > 100K/sec under load
    Fix: reduce thread count, use async/reactive or virtual threads

Memory:
  - Page cache eviction under memory pressure
    Diagnosis: vmstat si/so > 0 (swapping)
    Fix: add RAM, reduce heap size, disable swap
    
  - GC pause time increases with more allocation rate
    Diagnosis: GC log shows full GC pauses under load
    Fix: GC tuning, reduce allocation rate

I/O:
  - Connection pool exhausted (DB, Redis)
    Diagnosis: metrics show connection pool wait time
    Fix: increase pool size, fix long-running queries
    
  - File descriptor exhaustion
    Diagnosis: lsof -p PID | wc -l near ulimit value
    Fix: ulimit -n increase, fix FD leaks
```

**Q3: Explain the difference between a synchronous,
asynchronous, and non-blocking operation in terms
of OS behavior.**

```
Strong answer:
  
  Synchronous blocking:
    Thread calls read(), OS parks thread (BLOCKED state),
    kernel performs I/O, kernel wakes thread when done.
    Thread's OS stack is held for entire I/O duration.
    Cost: 1 OS thread per concurrent I/O operation.
    
  Non-blocking:
    Thread calls read() with O_NONBLOCK flag.
    If data available: returns data immediately.
    If not: returns -1 with errno=EAGAIN (not BLOCK).
    Thread must poll via epoll or spin-wait.
    With epoll: select block once over many FDs.
    
  Asynchronous (AIO):
    Thread calls aio_read(callback), returns IMMEDIATELY.
    Kernel performs I/O in background (via worker thread pool).
    When complete: kernel invokes callback or signals.
    Thread can do other work while I/O is in progress.
    Java: AsynchronousFileChannel, Java 21 virtual threads.
```

**Q4: What happens at the OS level when a Java thread
calls Thread.sleep(1000)?**

```
Strong answer:
  
  Java Thread.sleep(1000) ->
    calls nanosleep({tv_sec=1, tv_nsec=0}) syscall
    ->OS puts thread in TIMED_WAITING state (maps to OS SLEEPING)
    ->CPU removed from ready queue for ~1000ms
    ->Timer interrupt wakes thread after 1000ms
    ->Thread moved back to READY state
    ->Scheduler places on CPU when next scheduled
    
  Key points:
    Thread does NOT consume CPU while sleeping.
    Sleep is approximate: may overshoot by 1-10ms
      (depends on system timer resolution + scheduler).
    Thread can be woken early by Thread.interrupt()
      (throws InterruptedException).
    
  strace shows: nanosleep({tv_sec=1, tv_nsec=0}, NULL) = 0
```

**Q5: A Java service has a deadlock. The health check
still returns 200. How is that possible?**

```
Strong answer:
  
  Health check thread vs deadlocked threads are different threads.
  
  Scenario:
    - Tomcat thread pool: 200 threads for HTTP requests
    - 10 threads: deadlocked (holding TransactionManager lock
      + InventoryLock in different order)
    - Health check endpoint uses a SEPARATE thread from pool
    - Health check runs in < 1ms, no locks needed
    - Health check returns 200 (it really is alive!)
    
  Meanwhile:
    - 10 threads deadlocked
    - Incoming requests needing those locks: queue up
    - Queue fills: other requests see timeout
    - Externally: some endpoints slow/timeout, /health ok
    
  Proper health check must include:
    - Deep health: can I connect to DB and execute a query?
    - Thread pool depth: is thread pool queue backing up?
    - Application-specific: can I process a test request end-to-end?
    - Liveness vs readiness (Kubernetes distinction)
```

---

### Working-Level Scenario Diagnosis Grid

```
Symptom                    Most Likely Cause         Diagnostic Tool
100% CPU, low throughput   Busy-wait or GC thrash     top -H, jstat -gc
Memory grows, OOM          Heap or off-heap leak      jmap -histo, pmap
Requests queue up          Thread pool saturated      thread pool metrics
Occasional long pauses     GC full pause or swap      GC log, vmstat
File errors at load        FD exhaustion              lsof -p PID | wc -l
Threads blocked forever    Deadlock                   jstack -l PID
Random slowness at load    Lock contention            jstack (BLOCKED%)
Process dies unexpectedly  OOM Killer                 dmesg | grep -i oom
```

---

### Common Misconceptions to Avoid in Interviews

| Wrong Answer | Right Answer |
|-------------|-------------|
| "More CPU = better performance always" | More CPU helps CPU-bound work. I/O-bound work is bottlenecked by I/O, not CPU. Adding CPU cores when app is waiting on DB does nothing |
| "Thread pool size should be as large as possible" | Too large a pool: context switch overhead, memory pressure. Too small: underutilization. Optimal for CPU-bound: N = cores. For I/O-bound: measure and tune |
| "Deadlock is rare in well-written code" | Deadlock is common in complex transactional systems. Any code that acquires multiple locks must prove consistent ordering |

---

### Mastery Checklist

- [ ] Can diagnose CPU vs I/O vs memory bottlenecks
- [ ] Explains thread states (R, S, D, T, Z) and their causes
- [ ] Describes OS behavior for sleep, lock, and I/O
- [ ] Proposes specific tools for each diagnostic scenario
- [ ] Connects OS behavior to JVM/application behavior
