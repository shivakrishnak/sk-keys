---
layout: default
title: "Thread States"
parent: "Java Concurrency"
nav_order: 337
permalink: /java-concurrency/thread-states/
number: "0337"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), Thread Lifecycle, synchronized
used_by: Deadlock Detection (Java), Thread Dump Analysis, wait / notify / notifyAll
related: Thread Lifecycle, Deadlock Detection (Java), Thread Dump Analysis
tags:
  - java
  - concurrency
  - internals
  - intermediate
---

# 337 — Thread States

⚡ TL;DR — A Java thread cyclesthrough six defined states (NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED) that tell you exactly why it's not making progress.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #337 │ Category: Java Concurrency │ Difficulty: ★★☆ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ Thread (Java), Thread Lifecycle, │ │
│ │ synchronized │ │
│ Used by: │ Deadlock Detection, Thread Dump │ │
│ │ Analysis, wait/notify/notifyAll │ │
│ Related: │ Thread Lifecycle, Deadlock Detection, │ │
│ │ Thread Dump Analysis │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
When a multithreaded Java application slows down, you know threads aren't
making progress — but you don't know why. Is thread X waiting for a lock?
Waiting for I/O? Sleeping? Finished? Without distinct states, a thread dump
shows you stack traces with no indication of the thread's condition. You're
reading 500 stack frames with no idea which threads are the bottleneck and why.

**THE BREAKING POINT:**
A production incident: the application stopped responding. Thread dump analysis
showed 100 threads — all with stack traces. Without states, distinguishing
"thread blocked on lock" from "thread sleeping" from "thread waiting for network
response" requires reading every frame of every stack trace, which takes an expert
30+ minutes. With 100 threads, this is basically impossible under time pressure.

**THE INVENTION MOMENT:**
This is exactly why **Thread States** exist in Java's `Thread.State` enum:
a concise, machine-readable, instantly-interpretable tag on every thread that
answers "why isn't this thread doing useful work right now?"

---

### 📘 Textbook Definition

Java defines six thread states in the `java.lang.Thread.State` enumeration:
`NEW` (created, not started), `RUNNABLE` (executing or ready to execute on CPU),
`BLOCKED` (waiting to acquire a monitor/intrinsic lock via `synchronized`),
`WAITING` (waiting indefinitely for another thread via `Object.wait()`,
`Thread.join()`, or `LockSupport.park()`), `TIMED_WAITING` (waiting with a
timeout via `Thread.sleep(n)`, `Object.wait(n)`, `Thread.join(n)`, or
`LockSupport.parkNanos(n)`), and `TERMINATED` (execution completed). These
states reflect the JVM-level view, distinct from OS-level thread states.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Thread states are the JVM's six-word vocabulary for explaining why a thread is not running.

**One analogy:**

> A thread's state is like a traffic light explanation on a dashboard.
> GREEN (RUNNABLE) = driving, YELLOW (WAITING/TIMED_WAITING) = waiting at a
> scheduled stop, RED (BLOCKED) = stuck behind another car, PARKED (NEW) =
> engine not started, OFF (TERMINATED) = destination reached.

**One insight:**
BLOCKED and WAITING look the same to the naked eye ("thread isn't running")
but mean completely different things. BLOCKED means "a lock is held by someone
else — I'm in a queue." WAITING means "I voluntarily said 'notify me when
you're done'." Deadlocks involve BLOCKED threads; improper notification involves
WAITING threads. Confusing them leads to wrong diagnosis.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A thread can only be on a CPU in the RUNNABLE state.
2. A thread transitions between states based on lock acquisition, method calls,
   and OS scheduling events.
3. Only the JVM can transition a thread's state — not application code directly.
4. Each non-RUNNABLE state encodes exactly why the thread is not executing.

**DERIVED DESIGN:**
The state transitions are driven by specific JVM operations:

```
Thread.start()     : NEW → RUNNABLE
monitor contention : RUNNABLE → BLOCKED
monitor acquired   : BLOCKED → RUNNABLE
Object.wait()      : RUNNABLE → WAITING
Object.notify()    : WAITING → BLOCKED (not directly RUNNABLE — must re-acquire lock)
Thread.sleep(n)    : RUNNABLE → TIMED_WAITING
sleep expires      : TIMED_WAITING → RUNNABLE
Thread.run() exit  : RUNNABLE → TERMINATED
LockSupport.park() : RUNNABLE → WAITING
```

Note the critical subtlety: `Object.notify()` does NOT move a thread from
WAITING to RUNNABLE directly. It moves it to BLOCKED (waiting to re-acquire
the monitor), then to RUNNABLE once the lock is free.

**THE TRADE-OFFS:**

- Gain: precise, language-level diagnostics for thread health.
- Gain: enables thread dump analysis tools (jstack, JMC) to classify threads.
- Cost: JVM-level states don't directly map to OS-level states (which can have
  more granular I/O wait states).
- Cost: RUNNABLE includes threads that are actually waiting for I/O at the OS
  level — you can't distinguish CPU-bound from I/O-bound with state alone.

---

### 🧪 Thought Experiment

**SETUP:**
Thread A holds lock L. Thread B calls `synchronized(L) { }`. Thread C calls
`L.wait()` inside a synchronized block. Thread D calls `Thread.sleep(5000)`.
Thread E finishes its `run()` method.

**STATES:**

- Thread A: **RUNNABLE** (holding and running with lock L)
- Thread B: **BLOCKED** (waiting to acquire L; it's held by A)
- Thread C: **WAITING** (released L and waiting for `L.notify()`)
- Thread D: **TIMED_WAITING** (voluntarily sleeping, will wake after 5s)
- Thread E: **TERMINATED** (run() completed)

**WHAT HAPPENED:**
Thread A calls `L.notify()` → Thread C moves from WAITING to BLOCKED (competing
with Thread B for L). When Thread A releases L, both B and C are BLOCKED —
a race to re-acquire L. One wins: BLOCKED → RUNNABLE. The other stays BLOCKED.

**THE INSIGHT:**
BLOCKED is always a lock contention signal. WAITING requires an explicit notify.
If you see many BLOCKED threads in a dump: you have a lock bottleneck.
If you see many WAITING threads with no notifiers: you may have a deadlock or
missed notification bug.

---

### 🧠 Mental Model / Analogy

> Thread states are like an office worker's availability status:
> RUNNABLE = at desk, working actively.
> BLOCKED = waiting for the meeting room to be free (someone else is using it).
> WAITING = waiting for a colleague to ping me back (no timeout — I sit and wait).
> TIMED_WAITING = took a scheduled break, back in N minutes.
> NEW = hired but hasn't started yet.
> TERMINATED = left the company.

- "Meeting room" → synchronized block / intrinsic lock
- "Colleague ping" → Object.notify() or notifyAll()
- "Scheduled break" → Thread.sleep(n)
- "Hired but not started" → new Thread() without .start()

**Where this analogy breaks down:** A BLOCKED worker can see who's in the meeting
room. A BLOCKED thread knows the lock reference but not which thread holds it
(unless you use `ReentrantLock.getOwner()` from the java.util.concurrent package).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every Java thread has a label at any moment telling you what it's doing:
running, waiting for a lock, sleeping, waiting for a signal, or done.
These labels make diagnosing multithreaded problems possible.

**Level 2 — How to use it (junior developer):**
Read thread states via `thread.getState()` or in thread dumps (jstack).
In a dump, look for: many BLOCKED threads → lock contention bottleneck.
Many RUNNABLE threads → active work (or CPU-bound code). Many WAITING/
TIMED_WAITING threads on the same object → potential misuse of wait/notify.
One TERMINATED thread you expected to be running → thread crashed.

**Level 3 — How it works (mid-level engineer):**
`java.lang.Thread.State` is queried by the JVM from the OS thread state,
with JVM-level additions. RUNNABLE means runnable OR actively running (the JVM
doesn't distinguish — both show as RUNNABLE). To differentiate: RUNNABLE
threads with CPU time progressing are actually running; those without CPU
time (via JMX or profiler) are runnable-but-scheduled-out. `LockSupport.park()`
and `Unsafe.park()` produce WAITING/TIMED_WAITING, depending on timeout.
`java.util.concurrent` locks (`ReentrantLock`) use `LockSupport.park()` —
so threads blocked on j.u.c. locks appear as WAITING, NOT BLOCKED
(unlike `synchronized` which produces BLOCKED).

**Level 4 — Why it was designed this way (senior/staff):**
The RUNNABLE state encompasses both "currently using CPU" and "scheduled,
waiting for CPU timeslice" intentionally — the JVM doesn't expose scheduling
details that are OS-specific. This is by design: Java aims for portability,
and OS scheduling is not portable. The critical distinction between BLOCKED
(intrinsic locks / `synchronized`) and WAITING (`Object.wait()`,
`LockSupport.park()`) exists because they have different resolution strategies:
BLOCKED threads are automatically unblocked when the lock owner exits the
synchronized block; WAITING threads require explicit action (notify/unpark).
This distinction drives correct diagnosis: a BLOCKED thread is waiting on a lock
acquisition path; a WAITING thread is waiting on an application-level signal.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│         JAVA THREAD STATE MACHINE                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    new Thread()                                          │
│         ↓                                               │
│    [NEW]                                                 │
│         ↓ thread.start()                               │
│    [RUNNABLE] ←──────────────────────────────────┐     │
│         │                                         │     │
│         ├─ synchronized() fails → [BLOCKED]       │     │
│         │    lock released → ────────────────────┘│    │
│         │                                          │    │
│         ├─ Object.wait() → [WAITING]               │    │
│         │  LockSupport.park()                      │    │
│         │  Thread.join()                           │    │
│         │    notify/unpark/join done → BLOCKED     │    │
│         │    then lock acquired → ───────────────┘ │   │
│         │                                           │   │
│         ├─ Thread.sleep(n) → [TIMED_WAITING]        │   │
│         │  Object.wait(n)                           │   │
│         │  LockSupport.parkNanos(n)                 │   │
│         │    timeout expires → ─────────────────────┘  │
│         │                                               │
│         └─ run() returns → [TERMINATED]                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**j.u.c. lock behaviour (important!):**

```java
// synchronized → thread appears as BLOCKED in thread dump
synchronized(obj) { ... }

// ReentrantLock.lock() → thread appears as WAITING (not BLOCKED!)
// because ReentrantLock uses LockSupport.park() internally
lock.lock(); // WAITING state, not BLOCKED
```

This is a frequent source of confusion in thread dump analysis.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────────┐
│     THREAD STATE IN PRODUCTION DIAGNOSIS                  │
├──────────────────────────────────────────────────────────┤
│  Application appears slow/hung                           │
│       ↓                                                  │
│  Take thread dump: jstack <pid> or kill -3 <pid>        │
│  ← YOU ARE HERE                                          │
│       ↓                                                  │
│  Read states:                                            │
│  Many BLOCKED → lock contention bottleneck              │
│  Many WAITING → producer/consumer imbalance or deadlock │
│  Many RUNNABLE (with CPU) → CPU-bound computation       │
│  Many RUNNABLE (no CPU) → OS scheduling pressure         │
│  Few threads total → ThreadPool exhaustion              │
│       ↓                                                  │
│  Identify problematic thread pattern                     │
│  Fix: remove lock, use j.u.c. collections, add threads, │
│       or fix notification logic                          │
└──────────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Multiple BLOCKED threads all waiting for the same lock, whose owner is also
BLOCKED waiting for a different lock → Deadlock. Neither thread will ever
transition from BLOCKED to RUNNABLE. Observable: application hangs forever.
`jstack` will print "Found one Java-level deadlock:" section automatically.

**WHAT CHANGES AT SCALE:**
At 1000 threads, state distribution analysis becomes statistical. Tools like
JMC (Java Mission Control) visualize state heat maps over time — showing which
states dominate which time windows. A critical metric: BLOCKED thread seconds
/ total thread seconds = lock contention index. > 0.1 is problematic.

---

### 💻 Code Example

```java
// Example 1 — Read thread state programmatically
Thread t = new Thread(() -> {
    try { Thread.sleep(5000); }
    catch (InterruptedException e) { }
});
System.out.println(t.getState()); // NEW
t.start();
Thread.sleep(100);
System.out.println(t.getState()); // TIMED_WAITING
t.join();
System.out.println(t.getState()); // TERMINATED
```

```java
// Example 2 — BLOCKED vs WAITING distinction
Object lock = new Object();

// Thread A: holds lock, then waits
Thread a = new Thread(() -> {
    synchronized (lock) {
        try { lock.wait(); } // state: WAITING (released lock)
        catch (InterruptedException e) {}
    }
});

// Thread B: tries to acquire lock while A holds it
Thread b = new Thread(() -> {
    synchronized (lock) {  // state: BLOCKED if A holds lock
        lock.notify();
    }
});

a.start();
Thread.sleep(100);
System.out.println("A: " + a.getState()); // WAITING (not BLOCKED)
b.start();
Thread.sleep(100);
// After a.wait() releases the lock, b acquires it:
// A transitions to BLOCKED (competing to re-acquire after notify)
```

```bash
# Example 3 — Read states from thread dump
jstack <pid> 2>&1 | grep -A1 "java.lang.Thread.State"

# Analyze state distribution:
jstack <pid> | grep "java.lang.Thread.State" | sort | uniq -c | sort -rn
# Output:
#   87 java.lang.Thread.State: WAITING  (on object monitor)
#   23 java.lang.Thread.State: RUNNABLE
#    8 java.lang.Thread.State: BLOCKED  (on object monitor)
#    5 java.lang.Thread.State: TIMED_WAITING (sleeping)
# 87 WAITING threads → potential producer/consumer problem
```

---

### ⚖️ Comparison Table

| State             | Cause                        | Woken By                              | Production Signal                           |
| ----------------- | ---------------------------- | ------------------------------------- | ------------------------------------------- |
| **NEW**           | Thread created, not started  | `.start()`                            | Thread pool not initialized                 |
| **RUNNABLE**      | Running or ready to run      | CPU scheduler                         | Normal operation or CPU saturation          |
| **BLOCKED**       | Waiting for intrinsic lock   | Lock release                          | Lock contention bottleneck                  |
| **WAITING**       | `wait()`, `park()`, `join()` | `notify()`, `unpark()`, join finishes | Producer/consumer issues, deadlock risk     |
| **TIMED_WAITING** | `sleep(n)`, `wait(n)`        | Timeout or notification               | Usually expected (polling, scheduled tasks) |
| **TERMINATED**    | `run()` finished             | N/A                                   | Expected end; if unexpected: crash          |

**How to choose:** These states are not chosen — they are observed. Focus diagnosis
on BLOCKED (lock issues) and unexpected WAITING patterns (notification bugs).

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| BLOCKED and WAITING both mean "thread is stuck" | BLOCKED = waiting for a lock; WAITING = waiting for an event. They require completely different fixes              |
| RUNNABLE means the thread is using CPU          | RUNNABLE means scheduled — the thread may be waiting for CPU timeslice without actually executing                  |
| `ReentrantLock` creates BLOCKED threads         | `ReentrantLock` uses `LockSupport.park()` → threads appear as WAITING, not BLOCKED                                 |
| A thread in WAITING will resume on its own      | WAITING threads never resume on their own — they require explicit `notify()` or `unpark()`                         |
| TERMINATED threads are cleaned up immediately   | TERMINATED thread objects remain in memory until garbage collected; the OS thread resource is released immediately |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock (Multiple BLOCKED Threads)**

Symptom:
Application hangs. Taking a thread dump shows circular dependencies:
Thread A BLOCKED waiting on lock held by B; Thread B BLOCKED waiting on lock held by A.

Root Cause:
Two or more threads acquiring locks in inconsistent order.

Diagnostic Command / Tool:

```bash
jstack <pid>
# jstack automatically prints deadlock analysis at bottom:
# "Found one Java-level deadlock:
# "Thread-0": waiting to lock <0x000...> held by "Thread-1"
# "Thread-1": waiting to lock <0x000...> held by "Thread-0""
```

Fix:
Enforce consistent lock ordering. Use `tryLock()` with timeout as fallback.

Prevention:
Always acquire locks in the same canonical order (e.g., by lock ID).

---

**WAITING Threads Never Notified (Liveness Bug)**

Symptom:
Worker threads show WAITING state indefinitely. Work queue is non-empty
but workers never pick up tasks. Application appears hung but isn't deadlocked
(no circular lock dependencies).

Root Cause:
`notify()` was called before the thread entered `wait()`. The notification was
"lost." The thread then called `wait()` and has no signal pending.

Diagnostic Command / Tool:

```bash
jstack <pid> | grep -B5 "WAITING (on object monitor)"
# Shows WAITING threads and which object they're waiting on
# Also check: is there a notifier thread still running? Its state?
```

Fix:

```java
// BAD: check condition without re-checking after wait
synchronized(queue) {
    if (queue.isEmpty()) queue.wait(); // spurious wakeup unsafe
    process(queue.remove());
}

// GOOD: always re-check condition in a loop
synchronized(queue) {
    while (queue.isEmpty()) queue.wait(); // re-check after each wakeup
    process(queue.remove());
}
```

Prevention:
Always use `while` (not `if`) for `wait()` condition checks. Prefer
`BlockingQueue` over hand-rolled wait/notify — it handles this correctly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread (Java)` — Thread States define the lifecycle of a Java thread
- `Thread Lifecycle` — Thread States is the formalization of the lifecycle phases
- `synchronized` — BLOCKED state occurs due to synchronized block contention

**Builds On This (learn these next):**

- `Thread Dump Analysis` — uses Thread States to diagnose production issues
- `Deadlock Detection (Java)` — deadlocks are diagnosed by reading BLOCKED state chains
- `wait / notify / notifyAll` — these calls drive transitions from RUNNABLE to WAITING

**Alternatives / Comparisons:**

- `Thread Lifecycle` — the sequential view; Thread States adds the concurrent, observable perspective
- `ReentrantLock` — uses WAITING (not BLOCKED) state; important distinction for diagnosis

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Six JVM-level labels for thread activity  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without states, thread dumps are          │
│ SOLVES       │ unreadable stack traces with no context   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ BLOCKED = synchronization lock contention │
│              │ WAITING = voluntary indefinite wait        │
│              │ These require different fixes             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always read states first in thread dumps  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — states are read, not chosen         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ JVM states hide OS-level I/O wait detail  │
│              │ (RUNNABLE = running OR waiting for CPU)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The six answers to 'why isn't it running'"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Dump Analysis → Deadlock Detection  │
│              │ → wait/notify → ReentrantLock              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A thread is in WAITING state on `Object.wait()`. Another thread calls
`notifyAll()`. Trace the exact sequence of state transitions: does the waiting
thread immediately become RUNNABLE? What state does it pass through and why?
At which point could another BLOCKED thread "steal" the lock before the
notified thread re-acquires it?

**Q2.** A thread pool with 50 workers all show RUNNABLE in the thread dump,
but the application is processing only 10% of expected throughput and CPU
usage is at 5%. How can threads be RUNNABLE without using CPU, and what are
three distinct root causes that would produce this observation?
