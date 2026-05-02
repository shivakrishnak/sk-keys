---
layout: default
title: "Mutex"
parent: "Operating Systems"
nav_order: 114
permalink: /operating-systems/mutex/
number: "0114"
category: Operating Systems
difficulty: ★★☆
depends_on: Thread, Concurrency vs Parallelism, Synchronous vs Asynchronous
used_by: Critical Sections, Monitor, ReentrantLock, synchronized
related: Semaphore, Spinlock, Condition Variable, Monitor
tags:
  - os
  - concurrency
  - synchronization
  - fundamentals
---

# 114 — Mutex

⚡ TL;DR — A mutex (mutual exclusion lock) allows only one thread to enter a critical section at a time; every other thread blocks until the lock is released.

| #0114           | Category: Operating Systems                                     | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread, Concurrency vs Parallelism, Synchronous vs Asynchronous |                 |
| **Used by:**    | Critical Sections, Monitor, ReentrantLock, synchronized         |                 |
| **Related:**    | Semaphore, Spinlock, Condition Variable, Monitor                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two threads both read a shared counter (value=5), both increment it (+1), and both write back. Both write 6. The counter should be 7. This is a **data race** — the result depends on the interleaving of reads and writes across threads. Data races corrupt shared state silently.

**THE BREAKING POINT:**
Any operation on shared mutable state that takes more than one instruction (read-modify-write) can be interleaved by the thread scheduler at any point. Without protection, programs produce non-deterministic results that are correct on some runs and wrong on others — the hardest class of bugs to diagnose.

**THE INVENTION MOMENT:**
Edsger Dijkstra introduced the concept of mutual exclusion in 1965 with the critical section problem. The mutex is the hardware-supported implementation: use an atomic instruction (compare-and-swap, test-and-set) to acquire a lock before entering a critical section and release it after, ensuring only one thread executes the section at a time.

---

### 📘 Textbook Definition

A **mutex** (mutual exclusion lock) is a synchronisation primitive that prevents concurrent execution of a critical section (code that accesses shared mutable state). A mutex has two states: **locked** and **unlocked**. A thread **acquires** (locks) the mutex before entering the critical section; if the mutex is already locked by another thread, the acquiring thread **blocks** (is descheduled) until the mutex is released. The mutex is **released** (unlocked) by the holding thread when it exits the critical section, at which point the OS unblocks one waiting thread. A mutex is **non-reentrant** by default: a thread attempting to acquire a mutex it already holds will deadlock. A **reentrant (recursive) mutex** allows the same thread to acquire it multiple times (with a matching number of releases).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A mutex is a token — only the thread holding it can enter a protected region; all others wait.

**One analogy:**

> A single-stall bathroom with a key on a hook (the mutex). Before entering, you take the key. When you're done, you hang it back. Only one person inside at a time. If the key is missing, you wait outside. There's no "partly in the bathroom" — it's atomic.

**One insight:**
A mutex doesn't protect data — it protects code paths. You must ensure every code path that accesses the shared data acquires the mutex. Missing even one path breaks the guarantee. This is why higher-level abstractions (monitors, lock guards) are preferred: they make it structurally impossible to forget the lock.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. At most one thread holds the mutex at any moment.
2. A thread blocked on mutex acquisition will eventually acquire it (unless the holder is deadlocked or starved).
3. The holding thread must release the mutex — releasing from a non-holding thread is undefined behaviour in POSIX.
4. Lock and unlock form a **happens-before** edge: all writes before `unlock()` are visible to the thread that subsequently acquires the lock.

**DERIVED DESIGN:**
At the hardware level, mutex acquisition uses an atomic instruction (on x86: `LOCK CMPXCHG` or `XCHG`). The atomic ensures: read, compare, and write are a single indivisible step — no interleaving possible. If acquisition fails (lock already held), the OS kernel puts the thread in a wait queue and switches to another thread (blocking/sleeping). When the lock is released, the OS picks one waiting thread, moves it to the run queue, and it acquires the lock.

The Linux **futex** (fast userspace mutex) optimises the common case: if no contention, lock/unlock require only a single atomic instruction in user space — no kernel involvement. Only when contention occurs does the kernel get involved (to put threads to sleep and wake them).

**THE TRADE-OFFS:**
**Gain:** Prevents data races; provides happens-before guarantee; enables safe shared state.
**Cost:** Lock contention serialises threads (reduces parallelism); potential for deadlock (if multiple mutexes acquired in inconsistent order); priority inversion (high-priority thread blocked behind low-priority mutex holder); context-switch overhead when blocking occurs.

---

### 🧪 Thought Experiment

**SETUP:**
Thread A and Thread B both execute: `count++` (which compiles to: load count, add 1, store count).

WITHOUT MUTEX:

```
Time 1: Thread A loads count = 5
Time 2: [Thread B runs] loads count = 5
Time 3: [Thread B runs] stores count = 6
Time 4: Thread A stores count = 6   ← LOST UPDATE: expected 7
```

WITH MUTEX:

```
Time 1: Thread A: lock() → succeeds
Time 2: Thread A: loads count = 5, adds 1, stores count = 6
Time 3: Thread A: unlock()
Time 4: Thread B: lock() → succeeds (Thread A released it)
Time 5: Thread B: loads count = 6, adds 1, stores count = 7  ✓
```

**THE INSIGHT:**
The mutex transforms a concurrent read-modify-write into a sequential one. The price is the serial execution — during the critical section, only one thread makes progress.

---

### 🧠 Mental Model / Analogy

> A mutex is a single-occupancy office with a door lock. You enter, lock the door, do your work, and unlock on the way out. No one can enter while the door is locked. Everyone waiting outside is blocked. The first person to try the door after it unlocks gets in.

> Key distinctions:
>
> - "Non-reentrant": you cannot lock the door from inside (you'd deadlock — lock the lock, find yourself blocked).
> - "Reentrant mutex": the door records who locked it; if you already hold the lock, you can enter again (with a counter).
> - "Lock guard": the door has a spring — it automatically unlocks when you leave (RAII in C++, try-with-resources in Java).

Where the analogy breaks down: real mutexes don't guarantee FIFO ordering of waiting threads. The OS may wake any waiting thread. Fairness policies (like `ReentrantLock(true)` in Java) add FIFO queuing at additional overhead.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A mutex is a lock that makes sure only one thread at a time can access a piece of shared data. If another thread tries to access it while the first is using it, the second waits until the lock is released. This prevents corruption from simultaneous access.

**Level 2 — How to use it (junior developer):**
In Java: `synchronized(obj) { ... }` or `ReentrantLock lock = new ReentrantLock(); lock.lock(); try { ... } finally { lock.unlock(); }`. Always release in `finally` to prevent lock leaks on exception. In C POSIX: `pthread_mutex_lock/unlock`. In Python: `threading.Lock()`. Key rules: (1) protect every access to shared mutable state, (2) keep critical sections short, (3) avoid I/O or blocking calls inside a lock.

**Level 3 — How it works (mid-level engineer):**
Linux mutex = **futex** (fast userspace mutex). State: 1 `int` in user memory (0=unlocked, 1=locked-uncontested, 2=locked-contested). `lock()`: CAS(0→1). If succeeds: lock acquired, no syscall. If fails: CAS(1→2) + `futex(WAIT)` syscall → kernel puts thread in wait queue. `unlock()`: `atomic_dec` (2→1, then 1→0). If 0: no waiters, done. If previous value was 2: call `futex(WAKE)` → kernel unblocks one waiter. This means: zero-contention path has zero syscall overhead (~10ns); contended path has kernel scheduling overhead (~1–10µs).

**Level 4 — Why it was designed this way (senior/staff):**
The futex design (2002) solved a fundamental inefficiency: POSIX `pthread_mutex_lock` originally always made a syscall, even when no contention. At 100,000 lock/unlock pairs per second, this was measurable. The key insight was: contention is the rare case. The futex places the lock state in user memory, visible to both user and kernel, and only escalates to the kernel when a thread must truly block. The atomic CAS in user space is lock-free — paradoxically, the mutex's uncontested path is lock-free. Contended acquisitions are blocking, but that's unavoidable for mutual exclusion. Modern JVM: `synchronized` uses biased locking (JDK 8–14), lightweight locking (CAS spin), and inflation to a monitor (OS mutex) as contention increases — the same futex layering, reimplemented in the JVM.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│                FUTEX MUTEX FLOW                        │
├────────────────────────────────────────────────────────┤
│  Lock state: int mutex = 0  (in user memory)           │
│                                                        │
│  Thread A: lock()                                      │
│    CAS(mutex, 0, 1) → success → locked (no syscall)   │
│                                                        │
│  Thread B: lock() while A holds:                       │
│    CAS(mutex, 0, 1) → fail (mutex = 1)                 │
│    CAS(mutex, 1, 2) → success (mark contested)         │
│    futex(FUTEX_WAIT, mutex, 2) → kernel                │
│    Kernel: add Thread B to wait queue, deschedule      │
│                                                        │
│  Thread A: unlock()                                    │
│    atomic_exchange(mutex, 0) → previous=2 (contested)  │
│    futex(FUTEX_WAKE, mutex, 1) → kernel                │
│    Kernel: dequeue Thread B, move to run queue         │
│                                                        │
│  Thread B: resumes → CAS(mutex, 0, 1) → lock acquired  │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

JAVA synchronized KEYWORD FLOW:

```
Thread A: synchronized(obj) { count++; }
  1. Check obj's mark word: biased? (JDK 8–14)
     → If biased to A: no CAS needed, fastest path
  2. If unbiased: CAS mark word (thin lock)
     → CAS succeeds: lightweight lock acquired (user space only)
  3. If contended: inflate to heavyweight monitor (OS mutex)
     → Thread B: block on futex(WAIT)
     → Thread A: unlock → futex(WAKE) → Thread B resumes

Thread A: unlock
  → Reverse the lock state
  → If other threads waiting: wake one
```

FAILURE PATH — lock never released (exception):

```java
// BAD: exception before unlock → lock held forever
lock.lock();
doSomethingThatThrows();  // exception here
lock.unlock();  // NEVER REACHED

// GOOD: try-finally guarantees release
lock.lock();
try {
    doSomethingThatThrows();
} finally {
    lock.unlock();  // ALWAYS executed
}
```

---

### 💻 Code Example

Example 1 — Java synchronized vs ReentrantLock:

```java
// Method 1: synchronized (implicit mutex on 'this')
public class Counter {
    private int count = 0;

    public synchronized void increment() {
        count++;  // critical section: only one thread at a time
    }

    public synchronized int get() {
        return count;  // reads also protected
    }
}

// Method 2: ReentrantLock (explicit, more control)
public class BetterCounter {
    private final ReentrantLock lock = new ReentrantLock();
    private int count = 0;

    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // always released
        }
    }

    public int get() {
        lock.lock();
        try { return count; }
        finally { lock.unlock(); }
    }

    // tryLock: non-blocking attempt (useful for avoiding deadlock)
    public boolean tryIncrement() {
        if (lock.tryLock()) {  // returns false if not immediately available
            try { count++; return true; }
            finally { lock.unlock(); }
        }
        return false;
    }
}
```

Example 2 — POSIX mutex in C:

```c
#include <pthread.h>

static int counter = 0;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void* increment_thread(void* arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        counter++;  // critical section
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, increment_thread, NULL);
    pthread_create(&t2, NULL, increment_thread, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("counter = %d\n", counter);  // always 2000000
    pthread_mutex_destroy(&mutex);
    return 0;
}
```

Example 3 — Diagnose mutex contention:

```bash
# Java: check lock contention with JStack
jstack <PID> | grep -A 5 "BLOCKED"
# Output:
# "Thread-1" #13 prio=5 os_prio=0 tid=0x...
#   java.lang.Thread.State: BLOCKED (on object monitor)
#     at Counter.increment(Counter.java:7)
#     - waiting to lock <0x...> (a Counter)
#     - locked by "Thread-0" id=12

# Linux: measure mutex wait time
perf stat -e sched:sched_stat_blocked -p <PID>
# High sched_stat_blocked = threads blocking on mutexes

# Valgrind Helgrind: detect race conditions and lock order violations
valgrind --tool=helgrind ./my_program
```

---

### ⚖️ Comparison Table

| Primitive          | Threads              | Use For                                | Reentrant?                 | Blocking?      |
| ------------------ | -------------------- | -------------------------------------- | -------------------------- | -------------- |
| **Mutex**          | 1                    | Exclusive access to shared state       | Optional (reentrant mutex) | Yes            |
| Semaphore          | N                    | Rate limiting, resource pool counting  | No                         | Yes            |
| Spinlock           | 1                    | Very short critical sections, no sleep | No                         | No (busy-wait) |
| RWLock             | N readers / 1 writer | Read-heavy shared data                 | Usually no                 | Yes (on write) |
| Condition Variable | — (used with mutex)  | Wait for condition                     | —                          | Yes            |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                            |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| "volatile replaces mutex"                          | volatile ensures visibility (no caching), not atomicity; count++ with volatile still has a data race                               |
| "mutex is slow — avoid it"                         | Uncontended mutex is ~10ns (user-space CAS only); avoid it only when profiling proves it's a bottleneck                            |
| "synchronized(this) is always safe"                | Synchronized on 'this' is vulnerable to external lock acquisition if callers also synchronize on your object                       |
| "ReentrantLock is always faster than synchronized" | Modern JVM synchronized has JIT-optimised biased locking; ReentrantLock is faster for tryLock/timed scenarios, not universally     |
| "Locking once per method is enough"                | If two methods each lock separately, the gap between them is unprotected; compound operations need a single, consistent lock scope |

---

### 🚨 Failure Modes & Diagnosis

**1. Deadlock (Two Mutexes Acquired in Inconsistent Order)**

**Symptom:** Application hangs; threads show BLOCKED state indefinitely; no CPU usage (threads are sleeping).

**Root Cause:** Thread A holds Lock1, waits for Lock2. Thread B holds Lock2, waits for Lock1. Circular dependency → neither can proceed.

**Diagnostic:**

```bash
jstack <PID> | grep -A 20 "deadlock\|BLOCKED"
# Java will report: "Found one Java-level deadlock:"
# and show the exact threads and locks involved

# Linux: gdb
gdb -p <PID>
(gdb) info threads
(gdb) thread apply all bt
# Look for pthread_mutex_lock in all thread backtraces
```

**Fix:** Always acquire multiple locks in a consistent global order. Use `tryLock()` with timeout and backoff.

**Prevention:** Enforce lock ordering via code review. Use single-lock designs where possible. Prefer higher-level concurrency primitives.

---

**2. Lock Leak (Exception Before Unlock)**

**Symptom:** Application gradually slows down; threads increasingly BLOCKED; eventually a full hang.

**Root Cause:** Exception thrown inside a critical section; no `finally` block; lock never released.

**Diagnostic:**

```bash
jstack <PID>
# All threads BLOCKED on the same lock
# The "owner" thread shows a completed/terminated stack
# → The lock is held by a dead thread or abandoned
```

**Fix:** ALWAYS use `try { ... } finally { lock.unlock(); }` pattern. Prefer `synchronized` keyword which handles this automatically.

---

**3. Priority Inversion**

**Symptom:** High-priority (latency-critical) thread has unexpectedly high latency; low-priority thread appears to be running instead.

**Root Cause:** Low-priority thread L holds a mutex needed by high-priority thread H. Medium-priority thread M preempts L. H is blocked waiting for L, but L can't run because M is always scheduled first.

**Diagnostic:**

```bash
# Linux: see priority of threads waiting on mutex
cat /proc/<PID>/status | grep -i priority
ps -eLf | grep <PID>
# Check if a low-priority thread holds a lock needed by a high-priority one
```

**Fix:** Priority inheritance protocols (`PTHREAD_PRIO_INHERIT` mutex protocol); careful lock scope minimisation; Real-Time Linux (`PREEMPT_RT`) kernel for hard real-time needs.

**Prevention:** Avoid sharing mutexes between threads of widely different priority; use lock-free data structures for RT-to-non-RT communication.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread` — a mutex protects shared state between threads; must understand threading
- `Concurrency vs Parallelism` — mutex is a concurrency control primitive
- `Synchronous vs Asynchronous` — mutex causes synchronous blocking; understand the difference for async-safe design

**Builds On This (learn these next):**

- `Condition Variable` — used with a mutex to wait for a condition to become true (producer-consumer)
- `Semaphore` — generalisation of mutex allowing N concurrent holders
- `Deadlock` — the primary failure mode of mutex-based synchronisation

**Alternatives / Comparisons:**

- `Spinlock` — non-blocking busy-wait instead of blocking; faster for very short waits
- `Lock-Free Data Structures` — CAS-based; no blocking, but complex and not universally applicable
- `Atomic variables` — for single-variable operations; eliminates the need for a mutex for simple counter/flag patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lock that allows only 1 thread to enter  │
│              │ a critical section; others block         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Data races: concurrent read-modify-write  │
│ SOLVES       │ corrupts shared state without protection  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Futex: uncontested lock = 1 CAS (user     │
│              │ space, ~10ns); contested = kernel syscall  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple threads read-modify-write same   │
│              │ data; protecting critical sections        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Atomic ops sufficient (single variable);  │
│              │ read-only access; lock-free structures     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Data safety vs parallel throughput        │
│              │ (critical section is serial)              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Take the token, do the work, return the  │
│              │  token — only one thread at a time"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Condition Variable → Deadlock → Spinlock  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `synchronized` keyword provides both mutual exclusion AND a happens-before guarantee. The happens-before guarantee means: all writes performed by Thread A before `synchronized` exit are visible to Thread B after it acquires the same monitor. POSIX pthread mutex has the same guarantee. Now consider: if Thread A writes variables X and Y while holding the mutex, then releases, and Thread B acquires and reads X and Y — this works. But what if Thread A writes Z (a different, unrelated variable) WITHOUT holding the mutex, and Thread B reads Z while holding the mutex? Is Z's value visible to Thread B? Why or why not — be precise about the Java Memory Model or POSIX memory model involved.

**Q2.** Linux's futex uses a two-word operation: `futex(FUTEX_WAIT, uaddr, val)` — the kernel only blocks the thread if `*uaddr == val` at the time of the syscall. Why is this two-step check (CAS in user space + conditional block) necessary? What is the race condition that would occur if you could simply call `futex(FUTEX_WAIT, uaddr)` unconditionally? Describe the exact interleaving that would cause a lost wake-up (spurious sleep) without the `val` parameter.
