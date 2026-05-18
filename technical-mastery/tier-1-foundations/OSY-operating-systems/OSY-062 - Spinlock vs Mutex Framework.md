---
id: OSY-062
title: Spinlock vs Mutex Framework
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-023, OSY-061
used_by: OSY-094
related: OSY-061, OSY-063, OSY-064
tags:
  - spinlock
  - mutex
  - busy-waiting
  - context-switch
  - adaptive-mutex
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/osy/spinlock-vs-mutex/
---

## TL;DR

Spinlock: busy-waits in a CPU loop until the lock is free.
Mutex: puts the thread to sleep (syscall), woken when free.
Spinlock wins when: lock held for microseconds or less,
running on multi-core. Mutex wins when: lock held for
milliseconds+, or single-core. Linux uses adaptive mutexes:
spin briefly, then sleep if not acquired - best of both.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-062 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | spinlock, mutex, busy-wait, context switch, adaptive mutex |
| **Prerequisites** | OSY-023, OSY-061 |

---

### Spinlock Mechanics

```
Spinlock: use CAS to acquire, spin on failure
  
  lock:
    while (!CAS(&lock, 0, 1)) {
      CPU_RELAX();  // PAUSE instruction on x86
      // keeps spinning... burning CPU cycles
    }
    // acquired!
    
  unlock:
    lock = 0;  // atomic write (memory barrier)
    
  PAUSE instruction (x86):
    Tells CPU: "I'm in a spin-wait loop"
    Benefits:
      1. Reduces power consumption
      2. Gives hint to hyperthreading: yield resources to sibling core
      3. Prevents memory order violation: clears store buffer
    Without PAUSE: spin loop causes memory order violations -> slower
    
Characteristics:
  No syscall: user-space only
  No context switch: thread remains RUNNING
  CPU usage: 100% while spinning (not doing useful work)
  Latency: very low if lock held for nanoseconds (no switch overhead)
  
Single-core machine NEVER use spinlock:
  The spinning thread prevents the lock-holder from running!
  Lock-holder is not running (only 1 CPU), can never release lock
  -> Deadlock / infinite spin
  Use mutex on single-core (sleep and let lock-holder run)
```

---

### Mutex Mechanics

```
Mutex: kernel-assisted sleep when contended
  
  lock:
    if (CAS(&mutex, 0, 1)) return;  // fast path: acquired
    // slow path: contended
    syscall futex_wait(&mutex, 1);  // sleep until mutex != 1
    // kernel adds thread to wait queue
    // thread state: RUNNING -> WAITING
    
  unlock:
    mutex = 0;  // release
    if (waiters exist) {
      syscall futex_wake(&mutex, 1);  // wake one waiter
      // woken thread: WAITING -> RUNNABLE -> scheduled
    }
    
  Context switch overhead:
    Save + restore registers, PC, stack pointer
    TLB flush (if different process)
    CPU pipeline flush
    Time: ~1-10 microseconds on Linux
    
Futex (Fast Userspace muTEX):
  Linux futex() syscall: combines userspace + kernel
  Uncontended: just an atomic CAS in userspace (no syscall!)
  Contended: syscall to kernel for sleep/wake
  
  Java's synchronized and ReentrantLock both use futex on Linux
  Most lock operations: no syscall at all (fast path CAS)
  Contended: one syscall for park (LockSupport.park())
```

---

### Decision Framework

```
Choose spinlock when:
  - Lock held for < 1-2 microseconds
  - Multi-core system
  - Lock holder won't sleep or be pre-empted
  - Kernel/interrupt context (cannot sleep in interrupt handler)
  
  Examples:
    Kernel spinlocks (interrupt handlers)
    Short CPU-bound critical sections
    DPDK (user-space networking): packet processing spinlocks
    
Choose mutex when:
  - Lock held for > 10 microseconds
  - Single-core possible
  - Lock holder might do I/O, allocation, or sleep
  - Need priority inheritance (avoids priority inversion)
  
  Examples:
    I/O-bound critical sections
    Database operations
    Any Java synchronized block (JVM uses futex automatically)
    
Linux adaptive mutex (best of both worlds):
  Phase 1: Spin for a short burst (microseconds)
    Only if lock holder is currently running on another CPU
    If lock-holder is on CPU: lock is likely released very soon
    Spinning avoids syscall overhead in the common case
    
  Phase 2: Sleep (call futex_wait)
    If lock-holder is not running (pre-empted or blocked)
    or if spin limit exceeded
    
  Java JVM: uses adaptive mutex internally (JVM -XX:+UseAdaptiveSpin)
  Most Java synchronized blocks: never reach kernel sleep
```

---

### Java Locking: What Actually Happens

```java
// Java's synchronized uses multiple lock states:
// (JVM biased locking removed in Java 15; Java 21: re-added as opt-in)

// State 1: Unlocked
//   Mark word: object hash code and age bits

// State 2: Thin lock (fast path CAS, no OS involvement)
//   Mark word: thread ID of lock owner
//   Acquire: CAS mark word from thread-ID-0 to current-thread-ID
//   Release: CAS back
//   Overhead: ~1 atomic operation (few nanoseconds)

// State 3: Inflated (contended - involves OS mutex)
//   Multiple threads waiting: JVM inflates to heavyweight lock
//   Uses futex via park/unpark (LockSupport)
//   Overhead: ~1-10 microseconds (syscall)

// JVM -XX:+PrintLockingStatistics (deprecated; use JFR now)
// JFR: Java Flight Recorder shows lock contention events
//   jcmd PID JFR.start duration=60s filename=locks.jfr
//   jfr print locks.jfr | grep "Lock"

// Monitor inflation threshold:
// -XX:BiasedLockingStartupDelay=0 (no longer needed Java 15+)

// ReentrantLock (more explicit):
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // critical section
} finally {
    lock.unlock();
}
// Internally: AbstractQueuedSynchronizer (AQS)
// AQS uses CAS + LockSupport.park()/unpark()
// Same futex-based approach as synchronized
```

---

### Diagnosing Lock Contention

```bash
# Java: JVM thread dump (what threads are waiting on)
kill -3 PID  # sends SIGQUIT to Java -> thread dump to stdout

# Look for:
# "waiting to lock <0x000000076f8e7c30>" (contended lock)
# "locked <0x000000076f8e7c30>" (holder)

# JFR (modern approach):
jcmd PID JFR.start duration=60s filename=app.jfr settings=profile
# Open in JDK Mission Control -> "Lock Instances" view
# Shows: class holding lock, contending threads, wait time

# perf (kernel spinlock view):
perf lock record java -jar app.jar
perf lock report
# Shows: lock contention for kernel locks

# Linux futex wait time:
strace -T -e futex java -jar app.jar 2>&1 | grep FUTEX_WAIT
# Each FUTEX_WAIT line: one contended lock acquisition
# Duration after <>: time waiting in kernel
# High duration = severe contention

# Quick check: CPU utilization during lock wait
# Low CPU + high latency = mutex contention (sleeping)
# High CPU + high latency = spinlock contention or CPU-bound
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Spinlocks are always better because no context switch overhead" | Spinlocks waste CPU cycles proportional to wait time. If a lock is held for 1ms and 8 threads are spinning, that's 8ms of wasted CPU. Mutex: sleeping threads use zero CPU. For any lock held > a few microseconds under contention, mutex wastes LESS total CPU |
| "Java synchronized always does a system call" | Modern JVM synchronized uses a multi-phase approach: thin lock (CAS only, no syscall), adaptive spinning, then inflated (syscall). The majority of synchronized blocks never reach the kernel under low-to-medium contention. Uncontended synchronized is ~2-5ns |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Spinlock | Busy-wait; no sleep; burns CPU; best for < 2 microseconds |
| Mutex | Sleep on contention; context switch overhead ~1-10 us |
| Adaptive mutex | Spin first, then sleep; best of both worlds |
| Java synchronized | Thin lock -> adaptive spin -> futex (kernel) |
| Java ReentrantLock | AQS + CAS + LockSupport.park(); same as synchronized |
| Single-core spinlock | Never use (lock-holder can never run while spinning) |
