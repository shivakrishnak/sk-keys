---
layout: default
title: "Thread Lifecycle"
parent: "Java Concurrency"
nav_order: 336
permalink: /java-concurrency/thread-lifecycle/
number: "0336"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), Runnable, Operating Systems
used_by: Thread States, synchronized, ExecutorService
related: Thread States, Thread (Java), ExecutorService
tags:
  - java
  - concurrency
  - thread
  - intermediate
  - lifecycle
---

# 0336 — Thread Lifecycle

⚡ TL;DR — A Java thread passes through six states from creation to termination: NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → RUNNABLE → TERMINATED — understanding transitions reveals why threads get stuck and how to debug deadlocks.

| #0336 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), Runnable, Operating Systems | |
| **Used by:** | Thread States, synchronized, ExecutorService | |
| **Related:** | Thread States, Thread (Java), ExecutorService | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Without understanding thread lifecycle, a developer sees a JVM "frozen" but doesn't know if threads are deadlocked (waiting for locks), genuinely busy (RUNNABLE), or blocked on I/O (WAITING). Thread dump analysis is impossible without knowing what each state means. Debugging production hangs requires understanding exactly what state each thread is in and WHY it transitioned there.

THE BREAKING POINT:
A production outage: all web threads show "WAITING" in a thread dump. Without lifecycle knowledge, the developer sees `Thread.State.WAITING` and doesn't know if this is normal (waiting for incoming requests) or a bug (deadlocked on a database connection). Applying the wrong fix (restarting pods instead of releasing the lock) doesn't resolve the root cause.

THE INVENTION MOMENT:
Understanding the **Thread Lifecycle** provides the mental model to: read thread dumps, diagnose deadlocks, understand why `sleep` differs from `wait`, understand when `synchronized` blocks vs when it doesn't, and design correct thread coordination.

### 📘 Textbook Definition

The **Thread Lifecycle** defines the discrete states a Java thread occupies and the transitions between them, represented by the `Thread.State` enum (Java 5+). States: **NEW** — created, not started; **RUNNABLE** — executing or ready to execute (no distinction from JVM perspective — includes I/O wait at OS level); **BLOCKED** — waiting to acquire a monitor lock (synchronized block/method); **WAITING** — waiting indefinitely for notification (Object.wait(), Thread.join(), LockSupport.park() with no timeout); **TIMED_WAITING** — waiting with a timeout (Thread.sleep(), wait(timeout), join(timeout)); **TERMINATED** — run() completed or threw an exception.

### ⏱️ Understand It in 30 Seconds

**One line:**
A thread's state tells you WHY it isn't running — BLOCKED means waiting for a lock, WAITING means waiting for a signal, RUNNABLE means eligible to run.

**One analogy:**
> A chef's shift: HIRED but not started (NEW) → WORKING (RUNNABLE) → WAITING for an oven to be free (BLOCKED) → ON BREAK waiting for sous chef's signal (WAITING) → SET TIMER for 20 minutes (TIMED_WAITING) → SHIFT ENDED (TERMINATED). Thread dumps show all chefs' states at an instant — sleeping chef vs locked-out chef vs working chef.

**One insight:**
BLOCKED and WAITING look similar in code but mean very different things: BLOCKED = "I am trying to enter a synchronized block but someone holds the lock" (active competition). WAITING = "I called `wait()` and deliberately released my lock — signal me when something changes" (passive wait for event).

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A thread can be in exactly one state at any time.
2. The JVM's `Thread.State` includes OS-level "waiting for I/O" inside RUNNABLE — from the JVM's perspective, a thread doing a socket read is RUNNABLE (the JVM can't distinguish computation from I/O wait without OS hooks).
3. BLOCKED state can only be entered when waiting for a `synchronized` intrinsic lock — `ReentrantLock.lock()` puts threads in WAITING, not BLOCKED.

DERIVED DESIGN:
Given invariant 3: this is a critical distinction for thread dump analysis. `ReentrantLock` blocked threads appear as WAITING on `LockSupport.park()`, not BLOCKED. A thread dump showing all threads WAITING on `park()` may indicate lock contention on `ReentrantLock` or `Semaphore` — not just `Object.wait()`.

```
Thread Lifecycle State Machine:

  New ──── start() ──────────────────► Runnable
                                          │
                                     ┌────┴────────────────┐
                                     │                     │
                              synchronized            Object.wait()
                              lock not avail.         LockSupport.park()
                                     │                Thread.join()
                                     ▼                     │
                                   Blocked ──lock──►  Waiting
                                                      /    \
                                           notified() /      \ timeout
                                                     /        \
                                              Runnable    TimedWaiting
                                                              │
                                                        (timeout)
                                                              │
                                                         Runnable
                                                             or
                                  run() returns ────────► Terminated
```

THE TRADE-OFFS:
The lifecycle design makes debugging possible through thread dumps. The RUNNABLE state conflation is a known compromise — OS-level I/O wait is invisible to the JVM thread state model (fixed with virtual threads where carrier thread visibility is separate from virtual thread state).

### 🧪 Thought Experiment

SETUP:
Thread dump of a deadlocked application. Three threads in unexpected states.

Thread T1: BLOCKED on `java.lang.Object@0x1234abc` — trying to enter `synchronized(sharedList)` but `t2` holds the lock.
Thread T2: BLOCKED on `java.lang.Object@0x5678def` — trying to enter `synchronized(sharedMap)`, held by `t1`.
Thread T3: WAITING at `Object.wait()` — waiting for notify on some condition. Not part of the deadlock.

WITHOUT LIFECYCLE KNOWLEDGE: "All threads seem stuck — restart the server."
WITH LIFECYCLE KNOWLEDGE: "T1 and T2 are in a classic circular lock deadlock — T1 holds lock A waiting for B, T2 holds B waiting for A. T3 is fine — it's legitimately waiting. Fix: enforce lock acquisition order."

THE INSIGHT:
Thread lifecycle state in a dump is precise diagnostic data. BLOCKED = fight for lock (identify which lock). WAITING = legitimate pause (identify what signal). Reading states correctly pinpoints the root cause without guessing.

### 🧠 Mental Model / Analogy

> Thread states are like the status tags on hospital patients. RUNNABLE: "in treatment." BLOCKED: "waiting for an operating room." WAITING: "waiting for test results before doing anything." TIMED_WAITING: "sleeping off anesthesia — wake in 30 min." TERMINATED: "discharged." A hospital administrator (debugger) reads these tags to understand why a ward (thread pool) is congested.

"Waiting for operating room" → BLOCKED on synchronized lock.
"Waiting for test results" → WAITING on `Object.wait()`.
"Sleeping off anesthesia" → TIMED_WAITING in `Thread.sleep()`.

Where this analogy breaks down: Hospital patients can be in multiple stages simultaneously in different bodies; threads are in exactly one state at any moment.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A thread goes through stages: created (not yet started), running, waiting for a lock, waiting for something to happen, and finally done. Knowing which stage helps diagnose why threads aren't making progress.

**Level 2 — How to use it (junior developer):**
Read thread dumps with `jstack`. Find threads in BLOCKED state (lock contention — check "waiting to lock" and "locked by" lines). Find threads in WAITING/TIMED_WAITING (normal pool threads waiting for work, or possible deadlocks). Find threads in RUNNABLE that are consuming CPU. TERMINATED threads are gone.

**Level 3 — How it works (mid-level engineer):**
`Thread.getState()` reads the JVM's internal thread state (set by the JVM when the thread enters synchronized, calls `wait()`, etc.). `jstack` triggers a safepoint, causing all threads to report their state. BLOCKED threads report which monitor they're waiting on and which thread holds it — enabling deadlock detection. `ThreadMXBean.findDeadlockedThreads()` uses this data programmatically.

**Level 4 — Why it was designed this way (senior/staff):**
The six-state model was codified in Java 5 with `Thread.State` enum. RUNNABLE conflates "executing on CPU" and "waiting for I/O" because the JVM runs on an OS thread model where I/O blocking is opaque to the JVM. Virtual threads (Java 21) expose a richer model: the carrier OS thread is RUNNABLE while the virtual thread is WAITING (unmounted during blocking I/O). This gives better observability for virtual thread stacks — the actual user code that was executing when the I/O wait started is captured in the virtual thread's stack even though the carrier thread is free.

### ⚙️ How It Works (Mechanism)

**Thread state transitions:**
```java
Thread t = new Thread(() -> {
    synchronized (lock1) {        // may → BLOCKED
        Thread.sleep(1000);       // → TIMED_WAITING
        lock1.wait();             // → WAITING (releases lock1!)
        // after notify() → RUNNABLE
    }
});
// t.getState() = NEW before start
t.start();
// t.getState() = RUNNABLE (scheduler determines actual CPU time)
```

**Reading a thread dump:**
```text
"http-nio-8080-exec-1" #45 daemon prio=5 os_prio=0 tid=... nid=0x... BLOCKED
   java.lang.Thread.State: BLOCKED (on object monitor)
        at com.example.OrderService.process(OrderService.java:42)
        - waiting to lock <0x00000000c8b57b90> (a java.util.HashMap)
        - locked <0x00000000c8b57ba0> (a java.util.ArrayList)
        at com.example.OrderController.handle(OrderController.java:15)
```

This shows: thread is BLOCKED, waiting for HashMap lock, already holds ArrayList lock. Cross-reference: which thread holds the HashMap lock? That reveals the deadlock.

**Programmatic deadlock detection:**
```java
ThreadMXBean bean = ManagementFactory.getThreadMXBean();
long[] deadlocked = bean.findDeadlockedThreads();
if (deadlocked != null) {
    ThreadInfo[] infos =
        bean.getThreadInfo(deadlocked, true, true);
    for (ThreadInfo info : infos) {
        log.error("DEADLOCK: {} state={} waiting for={}",
            info.getThreadName(),
            info.getThreadState(),
            info.getLockName()
        );
    }
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (thread pool worker):
```
[Worker created in pool: NEW state]
    → [pool.start(): state → RUNNABLE]  ← YOU ARE HERE
    → [task queue empty: wait for work]
    → [state: WAITING (LockSupport.park)]
    → [task submitted: pool unparks worker]
    → [state: RUNNABLE (executing task)]
    → [task completes: state → WAITING again]
    → [...loop until pool shutdown]
    → [pool.shutdown() + drain: TERMINATED]
```

FAILURE PATH (deadlock):
```
[T1 acquires lock A: RUNNABLE]
    → [T1 tries to acquire lock B: BLOCKED]
    → [T2 acquires lock B: RUNNABLE]
    → [T2 tries to acquire lock A: BLOCKED]
    → [T1 waits for T2, T2 waits for T1]
    → [DEADLOCK: both BLOCKED indefinitely]
    → [Diagnose: jstack → BLOCKED threads → lock chain]
```

WHAT CHANGES AT SCALE:
At scale, a thread pool's health is visible through state distributions: all workers RUNNABLE = CPU saturation; all WAITING = idle pool (good or maybe under-allocated); BLOCKED threads > 0 = lock contention; growing BLOCKED count over time = progressive deadlock or starvation. Monitoring thread state distributions (via JMX, JFR, or APM tools) is a key production health metric.

### 💻 Code Example

Example 1 — Checking thread state:
```java
Thread t = new Thread(() -> {
    try { Thread.sleep(5000); } catch (InterruptedException e) {}
});
System.out.println(t.getState()); // NEW
t.start();
Thread.sleep(100);
System.out.println(t.getState()); // TIMED_WAITING (sleeping)
t.join();
System.out.println(t.getState()); // TERMINATED
```

Example 2 — Thread dump via JFR for production diagnosis:
```bash
# Continuous thread state sampling:
jcmd <pid> JFR.start duration=60s \
  settings=profile filename=threads.jfr
jfr print --events jdk.ThreadPark,jdk.JavaMonitorWait \
  threads.jfr | head -50
```

### ⚖️ Comparison Table

| State | Meaning | Trigger | Exit Via |
|---|---|---|---|
| NEW | Created, not started | `new Thread()` | `.start()` |
| **RUNNABLE** | Running or ready | `.start()`, resume | Blocking operation or termination |
| BLOCKED | Waiting for intrinsic lock | `synchronized` contention | Lock acquisition |
| WAITING | Waiting for notification | `wait()`, `park()`, `join()` | `notify()`, `unpark()` |
| TIMED_WAITING | Waiting with timeout | `sleep()`, `wait(t)`, `join(t)` | Timeout or notify |
| TERMINATED | Execution complete | `run()` returns/throws | N/A |

How to choose (for debugging): BLOCKED = lock problem. WAITING = check if waiting for correct signal. TIMED_WAITING = usually fine if expected. Large RUNNABLE count with high CPU = thread overload.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| RUNNABLE means the thread is executing on CPU | RUNNABLE means "eligible to run" — the OS may or may not have scheduled it on a CPU. I/O-blocked threads appear RUNNABLE at the JVM level even while waiting for data |
| BLOCKED and WAITING are the same | BLOCKED = specifically waiting for an intrinsic lock (synchronized). WAITING = waiting for a signal (Object.wait, park, join). They have completely different diagnoses |
| ReentrantLock.lock() puts threads in BLOCKED | No — `ReentrantLock.lock()` calls `LockSupport.park()` internally, putting the thread in **WAITING** state, not BLOCKED |
| sleep() releases held locks | `Thread.sleep()` does NOT release any locks. The thread moves to TIMED_WAITING while holding all its locks. `Object.wait()` DOES release the associated monitor lock |

### 🚨 Failure Modes & Diagnosis

**Deadlock — All Threads BLOCKED**

Symptom: Application frozen. Thread dump shows circular BLOCKED chains.

Diagnostic:
```bash
jstack <pid> | grep -A20 "BLOCKED"
# Find "waiting to lock" and cross-reference "locked by"
# JVM may auto-detect: "Found one Java-level deadlock:"
```

Fix: Enforce consistent lock acquisition order. Use `tryLock(timeout)` with fallback. Use `java.util.concurrent` lock utilities instead of intrinsic locks.

---

**Thread Starvation — All WAITING, None Progressing**

Symptom: Thread pool threads in WAITING; no tasks executing; work queue not empty.

Root Cause: UncaughtExceptionHandler missing; thread threw exception and terminated; pool thread count fell to zero.

Fix: Configure `UncaughtExceptionHandler` on pool threads to log and optionally replace terminated threads.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread (Java)` — lifecycle applies to thread objects; understanding threads is foundational
- `Operating Systems` — RUNNABLE conflation with I/O wait is explained by OS thread scheduling

**Builds On This (learn these next):**
- `synchronized` — the mechanism that puts threads into BLOCKED state; understanding lifecycle makes synchronized behaviour clear
- `wait / notify / notifyAll` — the mechanism that puts threads into WAITING state

**Alternatives / Comparisons:**
- `Thread States` — a deeper look at the enumerated states themselves
- `ExecutorService` — manages thread lifecycle transparently in pools

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Six states a thread passes through from   │
│              │ creation to termination                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without lifecycle knowledge, thread dump  │
│ SOLVES       │ analysis is impossible; can't distinguish │
│              │ deadlock from legitimate waiting          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ BLOCKED = waiting for intrinsic lock.     │
│              │ WAITING = waiting for signal (wait/park). │
│              │ RUNNABLE ≠ executing — may be I/O-blocked.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing thread dumps, deadlocks,       │
│              │ performance issues, pool starvation       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — lifecycle is always relevant to     │
│              │ concurrent Java debugging                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ RUNNABLE conflates CPU and I/O — fixed    │
│              │ in virtual threads (Java 21)              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "State tells you WHY a thread isn't making│
│              │  progress"                                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ synchronized → volatile → wait/notify →  │
│              │ ReentrantLock                             │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A production thread dump shows 200 HTTP request-handling threads in WAITING state and 0 in RUNNABLE. The application appears unresponsive but no deadlock is detected by `ThreadMXBean.findDeadlockedThreads()`. List all possible legitimate and bug-indicating reasons why all 200 threads could be in WAITING simultaneously, and for each reason, describe the specific waiting location (class + method name) you'd expect to see in the thread dump and how you'd distinguish it from the others.

**Q2.** Java 21 virtual threads have a different observable lifecycle from platform threads. A virtual thread blocked on `Files.readAllBytes()` appears in the virtual thread stack dump at the `readAllBytes` call site — but the carrier OS thread's state is RUNNABLE (it's executing other tasks). Explain the JVM's internal mechanism: what data structure separates the virtual thread's continuation (saved stack frame at the blocking point) from the carrier thread's current execution context, how the scheduler decides which virtual thread to mount next, and why `Thread.getState()` returns WAITING for the virtual thread even though no OS thread is WAITING.

