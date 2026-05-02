---
layout: default
title: "Spinlock"
parent: "Operating Systems"
nav_order: 116
permalink: /operating-systems/spinlock/
number: "0116"
category: Operating Systems
difficulty: ★★★
depends_on: Mutex, Cache Line, False Sharing, Concurrency vs Parallelism
used_by: OS Kernel, Lock-Free Data Structures, Real-Time Systems
related: Mutex, Busy-Wait, CAS, TTAS, MCS Lock
tags:
  - os
  - concurrency
  - hardware
  - performance
  - kernel
---

# 116 — Spinlock

⚡ TL;DR — A spinlock busy-waits in a tight loop instead of blocking the thread; it's faster than a mutex for very short critical sections where context-switch cost exceeds wait time.

| #0116 | Category: Operating Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Mutex, Cache Line, False Sharing, Concurrency vs Parallelism | |
| **Used by:** | OS Kernel, Lock-Free Data Structures, Real-Time Systems | |
| **Related:** | Mutex, Busy-Wait, CAS, TTAS, MCS Lock | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
The OS kernel needs to protect a per-CPU run queue with a lock. A context switch into the kernel, through a mutex acquisition, involves: user→kernel transition, thread descheduling, scheduler run, thread rescheduling. Total overhead: ~1–5µs. The protected operation (update a run queue pointer) takes < 10ns. A mutex costs 100–500× more than the operation itself.

THE BREAKING POINT:
For extremely short critical sections (< 1–2µs), the overhead of a mutex — placing the thread in a wait queue, context-switching away, being woken by the OS, returning to user space — exceeds the wait time. A thread that would wait 50ns for a lock spends 5µs in kernel overhead for that mutex.

THE INVENTION MOMENT:
The spinlock trades CPU time for latency: instead of sleeping, the waiting thread loops (spins) on a CAS or test-and-set instruction until the lock is free. No context switch. No syscall. The CPU burns cycles, but the lock is acquired the instant it's released — microsecond-latency acquisition vs millisecond for mutex.

---

### 📘 Textbook Definition

A **spinlock** is a synchronisation primitive where a thread attempting to acquire an already-held lock repeatedly executes a test-and-set (or compare-and-swap) instruction in a tight loop ("spin") without yielding the CPU or blocking. When the lock is released, the spinning thread immediately detects the state change and acquires the lock — with no OS scheduling involvement. Spinlocks are efficient when the lock is held for very short durations (nanoseconds to microseconds) and when the waiting thread can afford to consume CPU. They are inappropriate for locks held for longer durations (would burn CPU for milliseconds), for uniprocessors (spinning prevents the holder from running on the same CPU), or for user-space code where other threads also need the CPU.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A spinlock keeps the CPU busy-looping until the lock is free — no OS involvement, instant acquisition when free.

**One analogy:**
> A mutex is waiting for a bus (you sit at the stop, the OS is the bus company scheduling when the bus comes). A spinlock is standing at the door of a room and trying the handle every millisecond until it opens. The first person out: you're in. No waiting room, no scheduling. But you're standing at the door, not doing anything else.

**One insight:**
A spinlock is only correct on a multi-core machine where the lock holder is running on a different CPU. On a single CPU, spinning prevents the holder from running — the lock never gets released while you spin. This is why spinlocks are used in the OS kernel (always multi-core, short critical sections) but rarely in user-space applications.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Spinlock state: 1 integer (0 = unlocked, 1 = locked).
2. Acquire: atomic test-and-set or CAS in a loop until successful.
3. Release: atomic store 0 (with appropriate memory barrier).
4. No thread is ever put to sleep; CPU is consumed while waiting.

DERIVED DESIGN:
Simple spinlock (naive TAS — test and set):
```
lock:    while CAS(lock, 0, 1) fails: spin
unlock:  store(lock, 0)
```

Problem: Under contention, all spinning threads repeatedly execute CAS on the same lock variable. CAS = write intent → cache line is transferred to the CAS-executing CPU in Modified state → all other CPUs' copies are invalidated → they re-read → another CAS attempt → cache line bouncing. This is the "cache line thundering herd": N spinners create O(N²) cache coherence traffic.

Solution — TTAS (Test-and-Test-and-Set):
```
lock:    loop:
           while load(lock) != 0: spin (read-only)
           if CAS(lock, 0, 1) succeeds: done
           else: continue loop
```

TTAS separates reading (Shared state, no coherence traffic) from writing (CAS, Modified state). Spinning threads observe the Shared-state cache line without generating coherence traffic. Only when the lock is released do they attempt CAS, and only one succeeds.

THE TRADE-OFFS:
Gain: Zero latency on acquisition (no context switch, no syscall); ideal for < 100ns critical sections; deterministic latency (no scheduler jitter).
Cost: Wastes CPU cycles while spinning; one spinning thread on a 2-core machine burns 50% CPU; not appropriate for user-space application code (preemptable threads); starvation possible under unfair implementations.

---

### 🧪 Thought Experiment

SETUP:
Critical section duration: 50ns. Mutex overhead (contended): 5µs. Spinlock overhead per spin: 4ns (CAS + L1 cache hit).

MUTEX (contended):
1. Thread B: lock() → contended → futex(WAIT) → kernel deschedule
2. Thread A: finishes work (50ns), unlock() → futex(WAKE) → kernel
3. Thread B: schedule → context restore → proceed
4. Total wait: 5,000–20,000ns (5–20µs)

SPINLOCK (contended):
1. Thread B: CAS fails → spin for 50ns
2. Thread A: finishes work (50ns), store(lock, 0)
3. Thread B: CAS succeeds → proceed
4. Total wait: 50–100ns (1 spin interval)

THE INSIGHT:
When the critical section is shorter than the mutex overhead, a spinlock is 50–100× faster. When the critical section is longer than the mutex overhead (> ~5µs), a mutex is better because a spinlock wastes CPU that could be given to the holder to finish faster.

---

### 🧠 Mental Model / Analogy

> A mutex is a queue at a deli counter: you take a number, sit down, and wait. When your number is called, you walk up. Fast for long waits. A spinlock is standing at the counter saying "are you done yet? are you done yet?" every millisecond. Obnoxious for long waits, but you'll get served the instant the counter is free.

> TTAS (test-and-test-and-set): instead of repeatedly asking "are you done yet?", you watch the counter from across the room (read the lock flag). When you see it become free, THEN you walk up and ask (do the CAS). Less shouting (less cache traffic), same first-available response.

Where the analogy breaks down: in a real spinlock under heavy contention, all waiting threads simultaneously try the CAS when the lock is released — the thundering herd. Solutions like the MCS lock (each thread spins on a private queue node) solve this by having only one thread try the CAS when the predecessor releases.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A spinlock is a lock where the waiting thread keeps trying to grab the lock in a tight loop instead of sleeping. It's fast when the wait is very short (the lock is held for nanoseconds) but wastes CPU for longer waits.

**Level 2 — How to use it (junior developer):**
Don't use spinlocks in typical application code — use `ReentrantLock` or `synchronized`. Spinlocks appear in: OS kernel code, lock-free data structures, real-time systems, game engines. In Java, `AtomicBoolean` with a CAS loop is a manual spinlock. The JDK's `synchronized` does a brief spin before inflating to an OS mutex (adaptive spinning). When diagnosing performance: if a thread is at 100% CPU but making no progress, it might be stuck in a spinlock.

**Level 3 — How it works (mid-level engineer):**
Linux kernel spinlock: `spin_lock(lock)`: `LOCK XCHG [lock], 1` instruction. If previous value was 0, acquired. If 1, spin: `rep nop` (pause instruction, hints CPU it's in a spin loop — allows HyperThreading sibling to use CPU) + re-check. The `pause` instruction is critical: without it, the CPU speculates ahead, fills the out-of-order buffer with spin iterations, and when the lock is released, must flush the entire pipeline — causing a ~20 cycle penalty. `pause` prevents this speculation. `spin_unlock`: `LOCK MOV [lock], 0` + `MFENCE` (or `xchg` for x86 implicit fence).

**Level 4 — Why it was designed this way (senior/staff):**
Modern kernel spinlocks use the **qspinlock** (queued spinlock) design (Linux 4.2+). Classic spinlock has O(N²) cache coherence traffic (N threads all spinning on the same variable, all invalidating each other on release). qspinlock uses an MCS-like queue: each waiter has a per-CPU node in the lock's wait queue; each CPU spins on its own node variable (not the shared lock). The lock holder updates only the next waiter's node — only one CPU gets the cache line invalidation on release, not all N. This reduces coherence traffic from O(N²) to O(1) per unlock. The qspinlock implementation on x86 uses 3 bytes: locked (1 byte), pending (1 byte), and tail (2 bytes, encoding the queue tail). The 4-byte atomic fits in a single L1 cache line access.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              TTAS SPINLOCK FLOW                        │
├────────────────────────────────────────────────────────┤
│  lock = 0 (unlocked)                                   │
│                                                        │
│  Thread A: lock()                                      │
│    while (load(lock) != 0) spin;  ← read-only (S)     │
│    CAS(lock, 0, 1) → success → locked (M state)       │
│                                                        │
│  Thread B: lock() [contended]                          │
│    load(lock) == 1 → spin in read loop (S state)       │
│    [CPU B's cache line: S, not generating coherence]   │
│                                                        │
│  Thread A: unlock()                                    │
│    store(lock, 0) → invalidates CPU B's S-state copy   │
│                                                        │
│  Thread B: load(lock) == 0 → exit spin loop           │
│    CAS(lock, 0, 1) → success → acquired (M state)     │
│                                                        │
│  With 100 spinners:                                    │
│    100 CPUs: all in S-state spin loop (no traffic)    │
│    Unlock: ONE invalidation (write back to lock=0)     │
│    100 CPUs: load sees 0, all attempt CAS              │
│    1 succeeds, 99 retry S-state spin → still O(N) CAS  │
│    [MCS/qspinlock solves this to O(1)]                 │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

OS KERNEL INTERRUPT HANDLER FLOW:
```
CPU 0: executing user process
  → Hardware interrupt (network packet)
  → Kernel: save user context
  → Kernel: spin_lock(&net_queue_lock)
    → CAS lock → acquired (< 5ns)
  → Enqueue packet (< 20ns)
  → spin_unlock(&net_queue_lock) → release (< 5ns)
  → Restore user context
  → Return to user process

Total interrupt handling: ~100ns
If mutex used: ~10µs (context switch overhead)
Speedup: 100× for this critical section
```

FAILURE PATH (spinlock in user space with preemption):
```
Thread A holds spinlock
  → OS scheduler preempts A (time quantum expired)
  → Thread B runs, tries to acquire spinlock
  → Thread B spins for 10ms (Thread A's quantum)
  → Thread A resumes, releases spinlock (50ns to hold)
  → Thread B wasted 10ms of CPU spinning for a 50ns wait
  → With 4 threads: 3 spinning = 75% CPU wasted
```

---

### 💻 Code Example

Example 1 — Basic TTAS spinlock in C:
```c
#include <stdatomic.h>

typedef struct {
    atomic_int locked;
} Spinlock;

void spinlock_init(Spinlock *sl) {
    atomic_store(&sl->locked, 0);
}

void spinlock_lock(Spinlock *sl) {
    for (;;) {
        // Test (read-only, S state) before test-and-set
        while (atomic_load_explicit(&sl->locked,
                                    memory_order_relaxed) != 0) {
            __asm__ volatile ("pause" ::: "memory");  // hint CPU
        }
        // Test-and-set (CAS, M state)
        int expected = 0;
        if (atomic_compare_exchange_weak_explicit(
                &sl->locked, &expected, 1,
                memory_order_acquire,
                memory_order_relaxed)) {
            return;  // acquired
        }
    }
}

void spinlock_unlock(Spinlock *sl) {
    atomic_store_explicit(&sl->locked, 0, memory_order_release);
}
```

Example 2 — Java "spinlock" using AtomicBoolean:
```java
import java.util.concurrent.atomic.AtomicBoolean;

public class SimpleSpinlock {
    private final AtomicBoolean locked = new AtomicBoolean(false);

    public void lock() {
        // TTAS: read first, CAS only when appears unlocked
        while (locked.get() ||
               !locked.compareAndSet(false, true)) {
            // Spin — in JVM, there's no 'pause' equivalent
            // Thread.onSpinWait() (Java 9+) is the closest
            Thread.onSpinWait();  // hints JIT to use PAUSE instruction
        }
    }

    public void unlock() {
        locked.set(false);  // volatile write — memory barrier
    }
}

// NOTE: In production, use synchronized or ReentrantLock
// This is an illustration — JVM spinlock in app code is almost always wrong
```

Example 3 — Adaptive spinning in JVM synchronized:
```java
// JVM does NOT expose spinlock directly, but synchronized uses it
// JVM synchronized adaptive spinning:
// 1. Try to acquire lock without kernel (spin for ~50–100 iterations)
// 2. If fails, try again with exponential backoff
// 3. If still fails, inflate to OS mutex (futex)
// This is transparent — developer just writes:
synchronized (obj) {
    // critical section
    // JVM handles spin → mutex upgrade automatically
}

// JVM tuning flags (usually leave default):
// -XX:PreBlockSpin=10  (initial spin iterations before blocking)
// -XX:+UseSpinning (enable spinning — usually on by default in server JVM)
```

Example 4 — Linux kernel spinlock usage:
```c
// Linux kernel: spin_lock_irqsave disables local interrupts + acquires
// Prevents deadlock if interrupt handler also needs the lock
#include <linux/spinlock.h>

static DEFINE_SPINLOCK(my_lock);

void kernel_function(void) {
    unsigned long flags;
    spin_lock_irqsave(&my_lock, flags);
    // Critical section: VERY short (ns)
    modify_shared_data();
    spin_unlock_irqrestore(&my_lock, flags);
}
```

---

### ⚖️ Comparison Table

| Primitive | Wait Strategy | Overhead | Best For | Bad For |
|---|---|---|---|---|
| **Spinlock** | Busy-wait (CPU cycles) | Zero latency, wastes CPU | < 100ns critical sections, kernel | User-space, long waits, single-core |
| Mutex | Sleep (OS scheduled) | ~1–10µs context switch | > 1µs critical sections | < 100ns (overhead exceeds wait) |
| Adaptive (JVM synchronized) | Spin then sleep | Variable | General purpose | Extreme real-time latency requirements |
| TTAS | Test then CAS | Less coherence than TAS | Multi-core, short critical sections | Very high contention (thundering herd) |
| MCS/qspinlock | Per-node spin | O(1) coherence traffic | High-contention, multi-socket NUMA | Simple implementations (complex code) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Spinlocks are always faster than mutexes" | Only when critical section < ~1µs AND multiple cores available AND lock is briefly held |
| "Spinlocks don't need memory barriers" | Incorrect — need at minimum `acquire` barrier on lock and `release` barrier on unlock to prevent CPU/compiler reordering across the critical section |
| "Spinlocks work fine on a single core" | No — on a single core, spinning prevents the lock holder from running; only preemptive multitasking (OS interrupt) can release the holder, but spinlocks typically disable interrupts |
| "JVM spinlocks are a good idea in application code" | Almost never — JVM has preemptive scheduling; a spinning thread may be preempted, wasting its quantum; use AtomicReference CAS for lock-free or ReentrantLock for blocking |
| "The `pause` instruction makes spinlocks faster" | Indirectly — `pause` prevents pipeline speculation during spin, reducing the pipeline flush penalty when the lock is released; it also gives the HyperThread sibling more execution resources |

---

### 🚨 Failure Modes & Diagnosis

**1. Spinlock in User Space Causing CPU Saturation**

Symptom: High CPU utilisation (100% on specific cores) with no apparent work being done; application throughput near zero.

Root Cause: User-space spinlock held by a preempted thread; other threads spin for the full scheduling quantum (10ms default) consuming entire CPU core.

Diagnostic:
```bash
# Linux: perf to find spinning CPU
perf top -e cpu-cycles -p <PID>
# If top symbol is your spinlock's CAS loop with no other work = stuck

# Java: thread dump
jstack <PID>
# Look for threads in RUNNABLE state with a spin-loop backtrace
# (spinning threads appear RUNNABLE, not BLOCKED, in thread dumps)
```

Fix: Replace user-space spinlock with `ReentrantLock` or `synchronized`. Use `Thread.onSpinWait()` if you must spin (allows JIT to emit PAUSE).

Prevention: Audit for any manual spinlock implementations in application code; replace with standard library primitives.

---

**2. Kernel Spinlock Held Across Preemptive Code**

Symptom: Linux kernel panic: "BUG: sleeping function called from invalid context" or watchdog timeout.

Root Cause: Code holding a kernel spinlock calls a function that can sleep (e.g., `kmalloc(GFP_KERNEL)`, `copy_from_user`); kernel spinlocks disable preemption and interrupts — sleeping is illegal.

Diagnostic:
```bash
# Kernel lock debugging
echo 1 > /proc/sys/kernel/lockdep_print_more
# Enables lockdep — reports lock-ordering violations and invalid sleep attempts
dmesg | grep "bad spinlock\|sleeping"
```

Fix: Replace `kmalloc(GFP_KERNEL)` with `kmalloc(GFP_ATOMIC)` (can't sleep, may fail); or release spinlock before sleeping and re-acquire after.

---

**3. False Sharing Between Spinlock Variable and Protected Data**

Symptom: Spinlock acquisition seems fast in microbenchmarks but shows high cache-to-cache traffic in production; profiler shows lock variable and protected data sharing cache lines.

Root Cause: The spinlock integer and the data it protects are on the same cache line; spinning on the lock invalidates the data's cache line.

Diagnostic:
```bash
perf c2c report
# Shows HITM on same cache line for both spinlock and data
```

Fix: Align the spinlock variable to its own cache line (64-byte aligned, padded).

Prevention: Place spinlock at the start of a struct; add `char pad[60]` after it before the protected data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Mutex` — understand blocking mutex first; spinlock is the non-blocking alternative for short waits
- `Cache Line` — spinlock spinning is cache-line-intensive; false sharing between lock and data is a common bug
- `False Sharing` — spinners generate false sharing on the lock variable; TTAS reduces this

**Builds On This (learn these next):**
- `Lock-Free Data Structures` — CAS operations are the building block of both spinlocks and lock-free algorithms
- `Deadlock` — spinlocks can deadlock on a single CPU (if the holder can't run while waiters spin)
- `Real-Time Systems` — spinlocks are the correct choice in hard real-time kernels where scheduling jitter is unacceptable

**Alternatives / Comparisons:**
- `Adaptive mutex` — spins briefly, then blocks (JVM synchronized, Linux futex with spin-before-sleep)
- `MCS lock` — queued spinlock with O(1) coherence; preferred in high-contention scenarios
- `RCU (Read-Copy-Update)` — kernel's most scalable read-concurrent protection; replaces spinlocks for read-heavy kernel data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lock that busy-waits (spins) instead of  │
│              │ sleeping until the lock is free          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Mutex overhead (5µs) >> short critical    │
│ SOLVES       │ section (50ns); spinlock is instant       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ TTAS: spin on read (S state, no traffic)  │
│              │ CAS only when appears free               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ OS kernel, < 100ns critical sections,    │
│              │ multi-core, real-time latency requirements│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ User-space application code; holds for   │
│              │ > 1µs; single-core systems               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero acquisition latency vs CPU waste     │
│              │ while waiting (burns cycles, not sleeping)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Spin on the door handle until it turns  │
│              │  — instant entry, but you can't sit down" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ qspinlock → MCS Lock → Lock-Free → RCU   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Linux kernel introduced `qspinlock` (queued spinlock) in Linux 4.2 to replace ticket spinlocks. A ticket spinlock uses two counters: `head` (next to be served) and `tail` (next ticket). A thread acquires by atomically incrementing `tail` and then spinning until `head == my_ticket`. This guarantees FIFO ordering and avoids thundering herd (each thread spins on its own local ticket value copy). The MCS lock (on which qspinlock is based) goes further: each thread has a private node on which it spins, and the unlock operation only modifies the immediate successor's node. Explain the exact memory ordering problem that ticket locks solve that TAS doesn't, and why qspinlock fits in 4 bytes while a naive MCS lock requires a node pointer (8 bytes). What compression does qspinlock use?

**Q2.** Rust's standard library provides `std::sync::Mutex` but also `parking_lot::Mutex` (external crate). The parking_lot mutex: uses a spinlock for the first few microseconds before falling back to OS park; has 1-byte size (vs 40 bytes for std); includes an inline spin phase using `std::thread::yield_now()` and `std::hint::spin_loop()`. Design a JVM language (Java/Kotlin) analog of parking_lot::Mutex that: (a) occupies exactly 1 word (8 bytes), (b) spins for a configurable number of iterations before blocking, (c) uses VarHandle for CAS operations, (d) handles the ABA problem. Describe the bit layout of the lock word and the exact transitions between: unlocked, spin-locked, and OS-blocked states.
