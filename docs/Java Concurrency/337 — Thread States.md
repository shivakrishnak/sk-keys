---
layout: default
title: "Thread States"
parent: "Java Concurrency"
nav_order: 337
permalink: /java-concurrency/thread-states/
number: "0337"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread Lifecycle, Thread (Java), synchronized
used_by: Thread Lifecycle, synchronized, wait / notify / notifyAll
related: Thread Lifecycle, synchronized, ReentrantLock
tags:
  - java
  - concurrency
  - thread
  - intermediate
  - diagnosis
---

# 0337 — Thread States

⚡ TL;DR — `Thread.State` is a six-value enum (NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED) that precisely identifies a thread's current situation — the essential vocabulary for reading thread dumps and diagnosing concurrency bugs.

| #0337 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread Lifecycle, Thread (Java), synchronized | |
| **Used by:** | Thread Lifecycle, synchronized, wait / notify / notifyAll | |
| **Related:** | Thread Lifecycle, synchronized, ReentrantLock | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Before `Thread.State` was formalized (Java 5), determining why a thread was not executing required parsing low-level OS thread states or JVM internals — different JVMs reported thread status differently. There was no standard API to programmatically ask "why is this thread not running right now?"

THE BREAKING POINT:
Two threads in the same frozen application: one waiting for I/O, one deadlocked. Both appear "not running." Without standard thread states, an APM tool can't distinguish "this is healthy waiting" from "this is a bug." Every production diagnosis required JVM-specific knowledge.

THE INVENTION MOMENT:
`Thread.State` was created to standardize thread state reporting across all JVM implementations, making thread dumps portable and programmatic monitoring of thread health possible.

### 📘 Textbook Definition

**`Thread.State`** is an enum in `java.lang.Thread` (Java 5+) with six values representing the execution state of a Java thread: `NEW`, `RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`, `TERMINATED`. Retrieved via `thread.getState()` or via `ThreadMXBean`. Used in thread dumps produced by `jstack`, JVisualVM, and Java Flight Recorder. Each state corresponds precisely to specific JVM events — what called caused the transition, what event will transition out.

### ⏱️ Understand It in 30 Seconds

**One line:**
`Thread.State` is the answer to "why is this thread not currently executing?"

**One analogy:**
> A hospital triage system: NOT ADMITTED (NEW), BEING TREATED (RUNNABLE), WAITING FOR AN OR (BLOCKED), WAITING FOR TEST RESULTS (WAITING), SEDATED FOR 30 MIN (TIMED_WAITING), DISCHARGED (TERMINATED). Each status tells staff exactly what to do next.

**One insight:**
The critical diagnostic distinction: BLOCKED threads are competing for resources (fix: reduce lock contention). WAITING threads are cooperating (usually correct — signal them when ready). Treating WAITING threads as a problem leads to wrong fixes.

### 🔩 First Principles Explanation

**Each state's precise meaning and transitions:**

| State | Meaning | Entered By | Exited By |
|---|---|---|---|
| NEW | Created, `start()` not called | `new Thread(runnable)` | `.start()` |
| RUNNABLE | Eligible to run (on CPU or ready) | `.start()`, returning from block/wait | Block/wait/terminate |
| BLOCKED | Waiting for intrinsic monitor lock | `synchronized` contention | Lock released by holder |
| WAITING | Waiting indefinitely for signal | `wait()`, `join()`, `park()` | `notify()`, `notifyAll()`, `unpark()`, join complete |
| TIMED_WAITING | Waiting with timeout | `sleep(t)`, `wait(t)`, `join(t)`, `parkNanos(t)` | Timeout expires OR signal |
| TERMINATED | Execution complete | `run()` returns or throws | N/A |

**Critical nuances:**
1. `ReentrantLock.lock()` → WAITING on `LockSupport.park()`, NOT BLOCKED
2. `Thread.sleep()` → TIMED_WAITING, does NOT release held locks
3. `Object.wait()` → WAITING, DOES release the monitor lock
4. I/O blocking → stays RUNNABLE (JVM can't see OS-level I/O wait)

```
Thread State → What's happening → What to look for in dump

BLOCKED     → Lock contention   → "waiting to lock <XX> (held by thread YY)"
WAITING     → wait() / park()   → "waiting on <object>" or "parking to wait"
TIMED_WAIT  → sleep / wait(ms)  → "sleeping" or "waiting on <object> timeout"
RUNNABLE    → running or I/O    → stack trace at execution point
TERMINATED  → done              → no stack frames
```

### 🧪 Thought Experiment

SETUP:
Thread dump snippet of a web server under load. Interpret each thread:

```
Thread "http-1" state=RUNNABLE
  at java.net.SocketInputStream.read(SocketInputStream.java:...)
  
Thread "http-2" state=BLOCKED
  waiting to lock <0x1234> (java.util.HashMap)
  locked by Thread "http-3"

Thread "http-3" state=BLOCKED  
  waiting to lock <0x5678> (java.util.ArrayList)
  locked by Thread "http-2"
  
Thread "http-4" state=WAITING
  at java.lang.Object.wait(Native Method)
  waiting on <0xabcd> (java.util.LinkedList empty queue)
```

Analysis:
- http-1: RUNNABLE but at `SocketInputStream.read` — blocked on I/O (OS-level), appears RUNNABLE at JVM level. Normal.
- http-2 and http-3: DEADLOCK — circular lock dependency. Bug.
- http-4: WAITING on empty queue — normal thread pool behavior, waiting for work.

THE INSIGHT:
One RUNNABLE, one legitimate WAITING, and one DEADLOCK — all need different responses. Thread states make diagnosis unambiguous.

### 🧠 Mental Model / Analogy

> Thread states are like a car dashboard's status lights. Red (BLOCKED) = engine overheating (actively competing for something). Yellow (WAITING/TIMED_WAITING) = waiting at a traffic light (legitimate pause). Green (RUNNABLE) = driving. Off (TERMINATED) = engine off. NEW = car assembled but ignition not turned. You read the dashboard to understand the car's status — not by guessing.

Where this analogy breaks down: Dashboard lights are binary (on/off); thread states have specific transition triggers. The RUNNABLE light doesn't tell you if you're moving or stuck in traffic (CPU vs I/O).

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is:** The label on a thread at any moment telling you what it's doing or waiting for.

**Level 2 — How to use it:** Use `jstack <pid>` to see all thread states. BLOCKED threads show what lock they're waiting for. Find the thread holding that lock — if it's also BLOCKED, deadlock. WAITING threads show what object/condition they're waiting on — check if the notifying code runs correctly.

**Level 3 — How it works:** `Thread.getState()` reads `JavaThread::_thread_state` in HotSpot JVM. The state is set atomically during transitions (entering synchronized, calling `Object.wait()`, etc.). Thread dump captures this via a safepoint — all threads are stopped momentarily to capture consistent state.

**Level 4 — Why it matters for virtual threads:** Virtual threads (Java 21) have their own state separate from the carrier thread. A virtual thread's `getState()` shows its logical state (WAITING during I/O) while the carrier OS thread's state is RUNNABLE (executing other virtual threads). Tools like JFR and thread dumps include both the virtual thread stack (user code) and the carrier thread — essential for diagnosing virtual thread issues.

### ⚙️ How It Works (Mechanism)

**Reading states programmatically:**
```java
Thread t = Thread.currentThread();
Thread.State state = t.getState(); // RUNNABLE

// Get all thread states:
ThreadMXBean mxBean =
    ManagementFactory.getThreadMXBean();
ThreadInfo[] allThreads =
    mxBean.dumpAllThreads(true, true);

for (ThreadInfo info : allThreads) {
    System.out.printf(
        "Thread: %s State: %s%n",
        info.getThreadName(),
        info.getThreadState()
    );
    if (info.getThreadState() == Thread.State.BLOCKED) {
        System.out.printf(
            "  Waiting for: %s (held by: %s)%n",
            info.getLockName(),
            info.getLockOwnerName()
        );
    }
}
```

**Deadlock detection:**
```java
long[] deadlockedIds =
    mxBean.findDeadlockedThreads();
if (deadlockedIds != null) {
    // Deadlock detected — alert, dump state, decide action
    throw new RuntimeException("DEADLOCK DETECTED");
}
```

**JFR event for thread state changes:**
```bash
jcmd <pid> JFR.start filename=states.jfr duration=30s
jfr print --events jdk.JavaMonitorWait,jdk.ThreadPark \
  states.jfr | head -100
```

### 🔄 The Complete Picture — End-to-End Flow

```
[Thread starts: NEW]
    → [.start() called: RUNNABLE]       ← YOU ARE HERE
    → [synchronized block — contended: BLOCKED]
    → [Lock acquired: RUNNABLE]
    → [Object.wait() called: WAITING]
    → [notify() received: RUNNABLE]
    → [Thread.sleep(1000): TIMED_WAITING]
    → [Sleep expires: RUNNABLE]
    → [run() returns: TERMINATED]
```

### 💻 Code Example

Example 1 — State sequence demonstration:
```java
Object lock = new Object();
Thread t = new Thread(() -> {
    synchronized (lock) {
        try {
            lock.wait(2000); // WAITING (2s) → RUNNABLE
        } catch (InterruptedException e) {}
    }
});
// NEW
t.start();
Thread.sleep(50);
System.out.println(t.getState()); // TIMED_WAITING (wait with timeout)
t.join();
System.out.println(t.getState()); // TERMINATED
```

Example 2 — Health check endpoint using thread states:
```java
// Monitor for stuck threads:
@Scheduled(fixedRate = 60_000)
void checkThreadHealth() {
    ThreadMXBean bean = ManagementFactory.getThreadMXBean();
    long[] deadlocked = bean.findDeadlockedThreads();
    if (deadlocked != null) {
        alertingService.sendAlert("DEADLOCK: " + deadlocked.length
            + " threads deadlocked");
    }
    // Count BLOCKED threads:
    long blocked = Arrays.stream(bean.dumpAllThreads(false, false))
        .filter(i -> i.getThreadState() == Thread.State.BLOCKED)
        .count();
    metrics.gauge("jvm.threads.blocked", blocked);
}
```

### ⚖️ Comparison Table

| State | CPU Usage | Lock Held | Lock Wanted | Next Action Needed |
|---|---|---|---|---|
| NEW | None | No | No | `.start()` |
| RUNNABLE | Yes (or I/O) | Maybe | No | None |
| **BLOCKED** | None | Maybe | Yes (intrinsic) | Lock holder must release |
| WAITING | None | No (released) | On condition | `notify()`/`unpark()` |
| TIMED_WAITING | None | Maybe | On timeout/signal | Wait for timer or signal |
| TERMINATED | None | No | No | N/A |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ReentrantLock contention shows as BLOCKED | ReentrantLock uses `LockSupport.park()` internally → shows as WAITING, not BLOCKED. Only intrinsic `synchronized` lock contention shows as BLOCKED |
| RUNNABLE means the thread is active and useful | RUNNABLE includes threads blocked on socket/file reads at the OS level — they aren't consuming CPU but show as RUNNABLE to the JVM |
| TIMED_WAITING and WAITING are interchangeable | WAITING waits indefinitely (must receive notification). TIMED_WAITING has a timeout (resumes automatically if not notified). They have different timeout semantics |

### 🚨 Failure Modes & Diagnosis

**Thread Stuck in BLOCKED — Identify Lock Holder**

```bash
jstack <pid> | grep -B2 "BLOCKED" -A10
# Find "waiting to lock <0xXXXX>"
# Search for <0xXXXX> to find which thread holds it
jstack <pid> | grep "0xXXXX" -B5 -A5
```

**Zero RUNNABLE Threads — Check for Starvation**

```bash
jstack <pid> | grep "State:" | sort | uniq -c
# If all threads in WAITING with 0 in RUNNABLE:
# Pool may be exhausted or all tasks completed
# Check executor task queue depth
```

### 🔗 Related Keywords

- `Thread Lifecycle` — the transitions between states; Thread States are the nodes in the lifecycle graph
- `synchronized` — the mechanism causing BLOCKED state
- `wait / notify / notifyAll` — the mechanisms causing WAITING state

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Enum of 6 states defining a thread's      │
│              │ exact current situation                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY STATES   │ BLOCKED = waiting for intrinsic lock      │
│              │ WAITING = waiting for signal (wait/park)  │
│              │ RUNNABLE = running OR waiting for I/O     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The diagnostic label on a stuck thread"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ synchronized → volatile → wait/notify     │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Describe exactly what a thread dump line like `"pool-1-thread-3" #25 prio=5 os_prio=0 tid=0x00007f4a5c001800 nid=0x7b4 waiting on condition [0x00007f4a4f9fe000]` tells you about the thread, and explain how to correlate the `nid` field with an OS-level `top` or `ps -H` command to identify which specific thread is consuming CPU or blocking in the OS — including the base conversion needed and which OS commands to use.

**Q2.** A thread in RUNNABLE state has a stack trace showing `sun.nio.ch.NativeThread.park(NativeThread.java:...)`. This is a Java NIO non-blocking I/O selector thread waiting for I/O events. Explain why this thread is RUNNABLE (not WAITING or BLOCKED) despite "waiting" for events — what OS mechanism is being used (select/epoll/kqueue), how the JVM keeps this thread RUNNABLE, and why changing from NIO to blocking BIO (`InputStream.read()`) for the same I/O would change this thread's state in a thread dump.

