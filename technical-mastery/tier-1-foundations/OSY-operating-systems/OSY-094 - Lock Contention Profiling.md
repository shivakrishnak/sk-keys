---
id: OSY-094
title: Lock Contention Profiling
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-027, OSY-028, OSY-029, OSY-065
used_by: []
related: OSY-093, OSY-095, OSY-099
tags:
  - lock-contention
  - profiling
  - mutex
  - futex
  - perf
  - JVM
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 94
permalink: /technical-mastery/osy/lock-contention-profiling/
---

## TL;DR

Lock contention occurs when multiple threads compete for the
same lock, forcing all but one to wait. Contended locks are
a common hidden throughput bottleneck - a single hot mutex
can limit an entire 64-core server to single-threaded
throughput. Diagnosis requires profiling at the OS (futex)
or JVM (async-profiler, JFR) level.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-094 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | lock contention, futex, mutex, profiling, async-profiler, JFR |
| **Prerequisites** | OSY-027, OSY-028, OSY-029, OSY-065 |

---

### What Is Lock Contention?

```
Lock (mutex) lifecycle:
  
  Thread A acquires lock -> critical section -> releases lock
  Thread B arrives while A holds lock -> BLOCKS -> waits
  Thread C arrives while A holds lock -> BLOCKS -> waits
  
  If lock is held for 1ms and 100 threads/second try to acquire:
    Arrival rate: 100/sec = 10ms between arrivals
    Hold time: 1ms
    Utilization: 1ms / 10ms = 10% -> low contention (OK)
    
  If same lock holds for 5ms and 300 threads/second:
    Arrival rate: 300/sec = 3.3ms between arrivals
    Hold time: 5ms
    Utilization: 5ms / 3.3ms = 150% -> SATURATED
    Queue builds up; latency grows unbounded (Queueing Theory)
    
  Amdahl's Law:
    If 20% of execution requires a single lock:
      Max speedup on 64 cores: 1 / (0.2 + 0.8/64) = 4.4x
      Not 64x! The lock is the bottleneck.
      
  OS-level: futex (Fast Userspace muTEX)
    Linux mutex: uncontended = no syscall (compare-and-swap in user space)
    Contended: futex(FUTEX_WAIT) syscall -> thread sleeps
    Release: if waiters: futex(FUTEX_WAKE) syscall -> wakes one
    High contention: many futex_wait/futex_wake syscalls visible in strace/perf
```

---

### Detection: OS Level

```bash
# Method 1: strace - see futex syscalls
strace -p PID -e trace=futex -T 2>&1 | head -50
# Look for: futex(lock_addr, FUTEX_WAIT, ...) with large duration
# -T: show time spent in syscall
# High futex time = lock contention

# Method 2: perf stat - count futex calls
perf stat -e syscalls:sys_enter_futex -p PID -- sleep 30
# High counts (millions/second) = high contention

# Method 3: perf lock - lock analysis
perf lock record -p PID -- sleep 10
perf lock report --key acquired --sort acquired
# Shows: lock address, acquire count, wait time, holder time

# Method 4: pidstat - voluntary context switches
pidstat -w -p PID 1
# cswch/s: voluntary context switches
# High cswch/s for a single process = lots of blocking (lock waits)

# Method 5: /proc/PID/status
cat /proc/PID/status | grep voluntary_ctxt_switches
cat /proc/PID/status | grep nonvoluntary_ctxt_switches
# voluntary: process voluntarily gave up CPU (lock wait, I/O wait)
# High voluntary: lots of blocking = contention or I/O
```

---

### Detection: JVM Level

```bash
# Method 1: async-profiler (best for JVM lock profiling)
# Download: github.com/jvm-profiling-tools/async-profiler

./profiler.sh -d 60 -e lock -f lock-report.html $PID
# Generates flamegraph of lock acquisition with wait times
# Identify hottest locks by wait time, not just acquisition count

# Method 2: JFR (Java Flight Recorder) lock profiling
jcmd $PID JFR.start duration=60s filename=flight.jfr \
  settings=profile
jcmd $PID JFR.stop
# Analyze with JDK Mission Control (JMC):
#   Thread section -> Lock Instances
#   Shows: locked object class, contention count, duration

# Method 3: JVM thread dump
kill -3 $PID  # SIGQUIT -> thread dump to stdout
# Look for: "- waiting to lock <0x...>" 
# Count: how many threads blocked on same object

# Method 4: perf + jmaps (for JVM native locks)
# JVM ObjectMonitor uses futex internally for synchronized blocks
perf lock record -p $PID -- sleep 10
perf lock report
# Shows native lock contention including JVM monitors
```

---

### Common Contention Patterns

```java
// BAD: Synchronized on shared mutable state
public class RequestCounter {
    private int count = 0;
    
    // synchronized = one thread at a time; bottleneck at scale
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// Result with 64 threads:
//   Each increment(): acquire lock, increment, release
//   63 threads blocked while 1 runs
//   Throughput: single-threaded despite 64 cores

// GOOD: Lock-free atomic counter
public class RequestCounter {
    // LongAdder: per-CPU cells; sum() combines at read time
    // Zero contention for increment; slight cost for sum()
    private final LongAdder count = new LongAdder();
    
    public void increment() {
        count.increment();  // No lock; CAS on local cell
    }
    
    public long getCount() {
        return count.sum();  // Combines cells
    }
}

// BAD: Synchronized on object used as lock across operations
class UserCache {
    private final Map<String, User> cache = new HashMap<>();
    
    // Locks the entire cache for a potentially long operation
    public synchronized User getOrLoad(String id) {
        if (!cache.containsKey(id)) {
            cache.put(id, loadFromDB(id));  // DB call while locked!
        }
        return cache.get(id);
    }
}

// GOOD: ConcurrentHashMap + computeIfAbsent (lock-free for reads)
class UserCache {
    // ConcurrentHashMap: stripe locks (16 segments, not 1)
    private final ConcurrentHashMap<String, User> cache =
        new ConcurrentHashMap<>();
    
    public User getOrLoad(String id) {
        // computeIfAbsent: only locks the specific hash bucket
        // If key present: no lock at all
        return cache.computeIfAbsent(id, k -> loadFromDB(k));
        // Note: DB call under ConcurrentHashMap's lock per segment
        // For slow DB: still a concern; use separate Striped<Lock>
    }
}
```

---

### Production Diagnosis Workflow

```
Step 1: Identify bottleneck
  Top -1: is CPU utilization flat (< 60%) despite high load?
  If CPU is flat and throughput is limited: suspect lock contention
  
Step 2: Confirm with context switches
  pidstat -w -p PID 1
  High voluntary context switches (cswch/s > 1000): blocking detected
  
Step 3: Find the hot lock
  async-profiler: -e lock -f report.html $PID
  OR: kill -3 $PID (thread dump); count blocked threads per lock
  OR: perf lock report (native locks)
  
Step 4: Understand access pattern
  What data is protected by the hot lock?
  How often is it read vs written?
  How long is the critical section?
  
Step 5: Choose the fix
  
  Read-heavy, write-rare:
    Replace synchronized with ReadWriteLock
    Or: use immutable data + replace-on-update
    
  Counter/accumulator:
    Replace with LongAdder or AtomicLong
    
  Map/collection:
    Replace HashMap + synchronized with ConcurrentHashMap
    
  Independent data, over-synchronized:
    Partition the lock: Striped<Lock> (Guava)
    
  Long critical section (DB call, I/O):
    Move I/O outside the lock; lock only for data structure update
    
  Unavoidable single lock:
    Scale out (distribute the work to separate processes)
    Reduce critical section (precompute outside lock)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Synchronized is slow; avoid it" | Uncontended synchronized with HotSpot biased locking is near-zero overhead (just a flag bit). The problem is CONTENTION - multiple threads competing for the same lock. A synchronized method with no contention is fine. Premature lock removal introduces races. |
| "ConcurrentHashMap is always lock-free" | ConcurrentHashMap uses segment-level locks for writes. Reads (get) are lock-free. computeIfAbsent and compute operations lock the bucket. High collision rate (bad hash function) can concentrate locks. Use ConcurrentHashMap correctly: avoid long operations in compute lambdas. |
| "Adding more threads will fix slow throughput" | If throughput is limited by lock contention, adding threads makes it worse. More threads -> more contention -> longer queues -> higher latency. Diagnose FIRST: is the bottleneck CPU (add threads) or lock (reduce contention). |

---

### Quick Reference Card

| Task | Tool | Command |
|------|------|---------|
| OS-level futex tracing | strace | `strace -p PID -e futex -T` |
| OS-level futex counts | perf | `perf stat -e syscalls:sys_enter_futex -p PID` |
| OS-level lock report | perf lock | `perf lock record/report -p PID` |
| JVM lock flamegraph | async-profiler | `profiler.sh -e lock -f out.html PID` |
| JVM thread dump | kill -3 | `kill -3 PID` -> look for "waiting to lock" |
| JVM lock profile | JFR | `jcmd PID JFR.start settings=profile` |
| Context switch count | pidstat | `pidstat -w -p PID` |
