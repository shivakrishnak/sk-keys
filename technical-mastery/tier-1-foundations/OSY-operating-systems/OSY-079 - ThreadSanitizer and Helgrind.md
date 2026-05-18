---
id: OSY-079
title: ThreadSanitizer and Helgrind
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-023, OSY-025, OSY-063
used_by: []
related: OSY-025, OSY-060, OSY-094
tags:
  - ThreadSanitizer
  - TSan
  - Helgrind
  - data-race
  - race-condition-detection
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/osy/thread-sanitizer-helgrind/
---

## TL;DR

ThreadSanitizer (TSan) and Helgrind are race-condition
detection tools. TSan: compiler instrumentation (2-20x
overhead, very fast), built into Clang/GCC. Helgrind:
Valgrind-based (slower, works on existing binaries).
Both detect: data races (concurrent access without
synchronization), lock-order inversions, and incorrect
mutex usage. For Java: use JCStress or IntelliJ's data
race inspection.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-079 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | TSan, ThreadSanitizer, Helgrind, data race, race detection |
| **Prerequisites** | OSY-023, OSY-025, OSY-063 |

---

### ThreadSanitizer (TSan)

```
TSan: compile-time instrumentation for race detection
  
  How it works:
    At compile time: instrument every memory access and sync operation
    At runtime: track "shadow state" for each memory location
      Shadow: which thread last read/wrote, which lock was held
    When thread A accesses addr X:
      Check: is any other thread concurrently accessing X?
      Check: are they holding a common lock?
      If no common lock AND concurrent access = DATA RACE -> report
      
  Enable (C/C++ with Clang or GCC):
    clang -fsanitize=thread -g my_program.c
    gcc   -fsanitize=thread -g my_program.c
    ./my_program  # races reported at runtime
    
  Overhead:
    Memory: 5-10x more RAM (shadow state storage)
    Speed: 2-20x slower (instrumentation on every access)
    Not suitable for production; used in CI/testing
    
TSan output example:
  ==================
  WARNING: ThreadSanitizer: data race (pid=12345)
    Write of size 4 at 0x7f8c00d04050 by thread T2:
      #0 update_counter counter.c:15
      #1 worker_thread main.c:42
    
    Previous read of size 4 at 0x7f8c00d04050 by thread T1:
      #0 read_counter counter.c:20
      #1 monitor_thread main.c:58
    
    Thread T2 (tid=67892, running) created at:
      #0 pthread_create main.c:71
  ==================
```

---

### Helgrind (Valgrind-based)

```
Helgrind: Valgrind tool for race detection

  How it works:
    Dynamic binary instrumentation (no recompile needed!)
    Instruments locks, condition variables, and memory accesses
    Tracks: "happens-before" relationship between operations
    
  Usage:
    valgrind --tool=helgrind ./my_program
    valgrind --tool=helgrind --log-file=helgrind.txt ./my_program
    
  Overhead:
    50-100x slowdown (Valgrind overhead + Helgrind tracking)
    Much slower than TSan
    Advantage: works on existing binaries (no recompile)
    
  Helgrind detects:
    1. Data races (same as TSan)
    2. Lock order violations: if A acquired before B in one path
       and B acquired before A in another -> deadlock potential
    3. POSIX mutex misuse (unlock from different thread)
    
  Helgrind output:
    ==12345== ---Thread-Announcement--
    ==12345== Thread #2 was created
    ==12345==    at 0x...: pthread_create (hg_intercepts.c:427)
    ==12345==
    ==12345== Possible data race during write of size 4 at 0x...
    ==12345==    at 0x...: worker (program.c:42)
    ==12345==
    ==12345==  This conflicts with a previous read of size 4
    ==12345==    at 0x...: reader (program.c:30)
```

---

### Java Race Detection

```java
// Java: no TSan equivalent (JVM manages threads differently)
// Approaches:

// 1. JCStress (Java Concurrency Stress tests)
// Build and run concurrency tests:
// @JCStressTest
// @Outcome(id = "1, 1", expect = Expect.ACCEPTABLE, desc = "ok")
// @Outcome(id = "0, 0", expect = Expect.FORBIDDEN, desc = "race!")
// @State
// public class CounterRaceTest {
//     int counter = 0;
//     @Actor
//     public void actor1(II_Result r) { r.r1 = ++counter; }
//     @Actor
//     public void actor2(II_Result r) { r.r2 = ++counter; }
// }

// 2. Java Thread Dump Analysis (for deadlocks):
// jstack PID
// Look for: "deadlock detected" section at bottom
// Thread waiting for lock held by thread waiting for lock = cycle

// 3. IntelliJ IDEA: inspections for common race patterns
//   - Non-thread-safe access to Collection
//   - Missing synchronization on field
//   - Double-checked locking without volatile

// 4. FindBugs/SpotBugs: static analysis for thread safety
//   @GuardedBy("lock") annotation + SpotBugs -> detects misuse

// 5. Java Flight Recorder: monitors lock contention
//   jcmd PID JFR.start settings=profile duration=60s
//   Shows: locks held longest, threads waiting longest

// Common Java races that tools detect:
public class RaceExample {
    // BAD: race on int field (not volatile, not synchronized)
    private int counter = 0;
    
    public void increment() { counter++; }  // not atomic! r-m-w race
    public int get() { return counter; }    // may read stale value
    
    // GOOD: use AtomicInteger
    private final AtomicInteger atomicCounter = new AtomicInteger(0);
    public void atomicIncrement() { atomicCounter.incrementAndGet(); }
}
```

---

### Diagnosing Race Conditions Without Tools

```
Signs of a race condition:
  - Behavior changes when adding print statements (Heisenbug)
  - Passes in single-threaded test, fails under load
  - Fails intermittently (1 in 100,000 runs)
  - Results vary with CPU count or OS scheduling
  
Manual analysis strategy:
  1. Identify shared mutable state
     (non-final, non-volatile fields accessed by multiple threads)
  
  2. For each shared field:
     Is every write to it protected by a lock?
     Is every read protected by the SAME lock?
     If not: potential race
     
  3. Check volatile: is visibility ensured?
     volatile = visibility + prevents instruction reordering
     NOT volatile: CPU cache may return stale value
     
  4. Check compound operations:
     i++: read, increment, write (3 separate steps -> not atomic!)
     Use AtomicInteger.incrementAndGet() instead
     
  5. Check check-then-act:
     if (!map.containsKey(k)) { map.put(k, v); }
     -> Not atomic! Another thread can put between check and put
     Use: map.putIfAbsent(k, v) (atomic)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "If it works in testing, there's no race condition" | Race conditions are timing-dependent. A data race may only manifest when specific CPU scheduling order occurs. Test environments (single-core VM, lighter load) have different scheduling patterns than production (multi-core, high load). Tools like TSan expose races in testing that only trigger rarely in production |
| "Java synchronized keyword eliminates all race conditions" | Synchronized ensures mutual exclusion for a specific object's monitor. Race conditions can still occur: reading a field without synchronization while another thread writes it (missing synchronized on the read), using different lock objects for the same data, or compound operations across multiple synchronized blocks |

---

### Quick Reference Card

| Tool | Language | Overhead | Approach |
|------|---------|----------|---------|
| ThreadSanitizer (TSan) | C/C++, Go | 2-20x | Compiler instrumentation |
| Helgrind | C/C++ | 50-100x | Binary instrumentation |
| JCStress | Java | N/A | Stress testing framework |
| JFR lock profiling | Java | < 1% | Lock contention monitoring |
| SpotBugs | Java | N/A | Static analysis |
| Race pattern | Any | - | volatile/atomic/synchronized |
