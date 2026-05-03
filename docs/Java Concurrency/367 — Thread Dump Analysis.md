---
layout: default
title: "Thread Dump Analysis"
parent: "Java Concurrency"
nav_order: 367
permalink: /java-concurrency/thread-dump-analysis/
number: "0367"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread States, JVM, Deadlock, ThreadPoolExecutor, synchronized
used_by: Deadlock Diagnosis, Performance Tuning, Hung Application Triage
related: Deadlock Detection, JVM Profiling, jstack, jcmd, JFR
tags:
  - concurrency
  - java
  - thread-dump
  - diagnostics
  - advanced
  - debugging
---

# 367 — Thread Dump Analysis

⚡ TL;DR — A thread dump is a snapshot of all JVM threads and their stack traces at an instant; analysing it reveals deadlocks, lock contention, blocked threads, and thread pool exhaustion without code changes or application restart.

| #0367           | Category: Java Concurrency                                      | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread States, JVM, Deadlock, ThreadPoolExecutor, synchronized  |                 |
| **Used by:**    | Deadlock Diagnosis, Performance Tuning, Hung Application Triage |                 |
| **Related:**    | Deadlock Detection, JVM Profiling, jstack, jcmd, JFR            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application stops responding at 3 AM. CPU is 0%. No errors in logs. JVM is alive but no requests are being processed. What's wrong? Without a thread dump, you're blind: you can't tell if threads are deadlocked, blocked on I/O, stuck waiting for a lock, or exhausted in a pool. You'd have to restart the JVM (losing all state) and hope the bug reproduces.

**THE BREAKING POINT:**
Concurrency bugs are the hardest to reproduce because they are timing-dependent. A thread deadlock or pool exhaustion that manifests under load rarely happens in a debugger. You need to capture the exact state of all threads while the problem is occurring — non-intrusively, in production, without stopping the application.

**THE INVENTION MOMENT:**
The JVM has built-in thread monitoring: every thread tracks its current stack, current lock, and which locks it's waiting for. `jstack <pid>` captures a full snapshot of all threads and their states in milliseconds. This snapshot is the thread dump: the single most powerful non-intrusive diagnostic tool for production JVM concurrency issues.

---

### 📘 Textbook Definition

A **thread dump** is a point-in-time snapshot of all Java threads running in a JVM process, including each thread's: state (`RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`), full stack trace, held locks (with monitor address), locks it is waiting for, and the thread that holds those locks. Generated via `jstack <pid>`, `jcmd <pid> Thread.print`, `kill -3 <pid>` (UNIX), or programmatically via `ManagementFactory.getThreadMXBean().dumpAllThreads()`. Thread dumps detect: deadlocks (JVM identifies them explicitly), lock contention (many threads `BLOCKED` on same monitor), thread pool exhaustion (pool threads stuck in WAITING/TIMED_WAITING), CPU spins (`RUNNABLE` without progression), and memory/I/O hangs (threads stuck in native I/O calls).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A thread dump is a X-ray of your running JVM — it shows every thread, what it's doing, and what it's waiting for at that exact moment.

**One analogy:**

> A thread dump is like pausing a busy restaurant and photographing every staff member: the chef is mid-chop, the waiter is standing at table 7 waiting for the chef to finish, the sommelier is waiting for the waiter to confirm the order, and the chef is waiting for the sommelier to hand back the wine list. The photo reveals the cycle instantly — no one told management, no log said "deadlock." The photo showed it.

**One insight:**
Take three thread dumps 5–10 seconds apart. A single dump shows state at one moment. Three dumps show movement: threads that are `RUNNABLE` and stuck in the same code location across all three dumps are CPU spinning; threads that are `BLOCKED` in the same location across three dumps have sustained lock contention — the real bottleneck.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Thread states: RUNNABLE (executing or ready), BLOCKED (waiting for monitor), WAITING (indefinite wait — `Object.wait()`, `LockSupport.park()`), TIMED_WAITING, TERMINATED.
2. Each thread's stack trace shows exact code location — fully qualified class/method/line.
3. Held monitors: shown as `- locked <0x...> (a java.util....)` — the thread holds this lock.
4. Wanted monitors: shown as `- waiting to lock <0x...>` — the thread is BLOCKED waiting for this lock.
5. Deadlock cycle: JVM explicitly identifies and reports at end of dump: "Found one Java-level deadlock."

**DERIVED DESIGN:**

```
SAMPLE THREAD DUMP EXCERPT:
"http-nio-8080-exec-5" #44 daemon prio=5 os_prio=0
   java.lang.Thread.State: BLOCKED (on object monitor)
    at com.example.OrderService.getOrder(OrderService.java:87)
    - waiting to lock <0x000000076b5e4f68>
         (a com.example.OrderService)        ← wants THIS lock
    at com.example.PaymentService.pay(PaymentService.java:55)
    - locked <0x000000076b5e5a20>
         (a com.example.PaymentService)      ← HOLDS THIS lock

"http-nio-8080-exec-3" #42 daemon prio=5 os_prio=0
   java.lang.Thread.State: BLOCKED (on object monitor)
    at com.example.PaymentService.refund(PaymentService.java:77)
    - waiting to lock <0x000000076b5e5a20>  ← wants what exec-5 holds
    at com.example.OrderService.cancel(OrderService.java:102)
    - locked <0x000000076b5e4f68>           ← holds what exec-5 wants

Found one Java-level deadlock:
  exec-5 → waiting for exec-3
  exec-3 → waiting for exec-5  ← CYCLE = deadlock
```

**KEY THREAD STATES TO IDENTIFY:**

| State                       | What It Means                    | Action                                    |
| --------------------------- | -------------------------------- | ----------------------------------------- |
| BLOCKED (on object monitor) | Waiting for synchronized lock    | Find lock holder; check for deadlock      |
| WAITING (in Object.wait)    | In thread pool or condition wait | Normal if in pool; check if stuck         |
| WAITING (in park)           | Parked by LockSupport            | Usually expected in AQS-based locks       |
| RUNNABLE                    | Executing                        | Check if actually progressing or spinning |
| TIMED_WAITING               | sleep/join/wait with timeout     | Usually normal                            |

---

### 🧪 Thought Experiment

**SETUP:**
Your service handles 500 RPS normally. It suddenly drops to 0 RPS with CPU near 0%. No errors. JVM alive. No recent deployments.

**WHAT A THREAD DUMP REVEALS:**

```
Thread pool: 100 threads, all states:
  90 threads: BLOCKED "waiting to lock <0x...> (a DbConnectionPool)"
  10 threads: WAITING (on object monitor) in DbConnectionPool.getConnection
  → All 100 threads are waiting for DB connections!

"db-conn-pool-cleaner-1": RUNNABLE
  at com.example.pool.DbConnectionPool.cleanup(DbConnectionPool.java:234)
  - locked <0x...> (a DbConnectionPool)  ← HOLDS the pool lock
  → cleanup thread holds pool lock for 5+ minutes (cleaning stale connections)

Root cause: DbConnectionPool.cleanup() acquires pool lock for entire cleanup
duration. With all 100 request threads blocked, no requests can be served.
```

**THE INSIGHT:**
This bug would be impossible to find in logs (no errors), impossible to reproduce in dev (pool doesn't fill up). A single thread dump taken during the incident reveals the exact code location and root cause in 30 seconds.

---

### 🧠 Mental Model / Analogy

> Reading a thread dump is like reading a fire drill safety report for a building. Each floor is a thread. Each room is a stack frame. If the emergency exit is locked (blocked on lock), the report notes which guard has the key (lock holder). The fire marshal (JVM deadlock detector) checks whether any chain of blocked people leads in a cycle — if so, it's a deadlock. The most valuable insight: which room has the most people crowded outside the door (most threads BLOCKED on same lock = hot contention point).

- "Floor/thread" → each thread in the dump
- "Room" → stack frame (class/method/line)
- "Emergency exit locked" → thread BLOCKED waiting for monitor
- "Guard with key" → thread holding the lock (`locked <0x...>`)
- "People crowded at door" → many threads BLOCKED on same monitor address

Where this analogy breaks down: unlike a building, multiple threads can hold different locks simultaneously. The more interesting cases involve chains of locks across multiple threads — harder to visualise than a single bottleneck.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A thread dump is a snapshot of what every thread in your Java program is doing right now. You can capture it without stopping the program. It's like taking a photo of everyone in a busy office — you can see who is working, who is waiting, and who is stuck.

**Level 2 — How to use it (junior developer):**
Capture: `jstack <pid> > dump.txt` (or `jcmd <pid> Thread.print`). Open the file. Look for "Found Java-level deadlock" at the bottom first. Scan for threads with state `BLOCKED` — these are waiting for locks. Count how many threads are blocked on the same lock address (hex like `0x0000000...`) — the most-blocked lock is your hotspot. Identify the thread that holds the hot lock and look at what it's doing.

**Level 3 — How it works (mid-level engineer):**
The JVM maintains per-thread state as part of the `JavaThread` C++ structure. `jstack` attaches to the JVM via `JVMTI` (JVM Tool Interface) or `SA` (Serviceability Agent) to safely pause and read thread state. Each stack frame corresponds to a JVM stack entry. Monitor ownership is tracked in the object header (mark word) or in a `BasicObjectLock` list per thread frame. The JVM's deadlock detection algorithm (called at dump time) is a cycle detection on the "waits-for" graph: thread A waits for lock held by thread B, which waits for lock held by thread C, etc. A cycle in this graph = deadlock. The JVM detects only `synchronized` block deadlocks natively; `java.util.concurrent` lock deadlocks require looking at `- parking to wait for <address> (a java.util.concurrent.locks.ReentrantLock$NonfairSync)`.

**Level 4 — Why it was designed this way (senior/staff):**
The safe thread dump design uses JVM safepoints: `jstack` signals the JVM to reach a safepoint (where no thread is in the middle of a bytecode boundary), then reads thread state. This prevents capturing a partially-updated stack frame. The JVMTI mechanism is designed for external monitoring tools without requiring application source changes or recompilation — "zero instrumentation observability." Modern alternatives (JFR — Java Flight Recorder) continuously record thread state at microsecond granularity, enabling post-mortem analysis without needing to catch the exact moment of a bug. JFR is the evolution of thread dumps: always-on, fine-grained, with minimal overhead.

---

### ⚙️ How It Works (Mechanism)

```bash
# CAPTURING A THREAD DUMP:

# Method 1: jstack (most common, low overhead)
jstack <pid> > thread-dump-$(date +%s).txt

# Method 2: jcmd (preferred on modern JDKs)
jcmd <pid> Thread.print > thread-dump.txt

# Method 3: via kill signal (Linux/Mac only)
kill -3 <pid>  # writes to stdout/log of the process

# Method 4: Programmatic (from within the JVM)
import java.lang.management.*;
ThreadMXBean tmx = ManagementFactory.getThreadMXBean();
ThreadInfo[] infos = tmx.dumpAllThreads(true, true);
// true,true = include locked monitors, include sync

# TAKING MULTIPLE DUMPS (recommended — 3 × 10s apart):
for i in 1 2 3; do
    jstack <pid> > dump-$i.txt
    sleep 10
done

# ANALYSING FOR DEADLOCKS:
grep -A 10 "Found.*deadlock" thread-dump.txt

# FINDING BLOCKED THREADS:
grep "BLOCKED" thread-dump.txt | wc -l

# FINDING THE HOT LOCK (most-waited lock):
grep "waiting to lock" thread-dump.txt | sort | uniq -c | sort -rn | head
```

```
READING A THREAD DUMP — KEY PATTERNS:

Pattern 1: DEADLOCK
Thread A: BLOCKED on 0x001, holds 0x002
Thread B: BLOCKED on 0x002, holds 0x001
→ Cycle → deadlock

Pattern 2: LOCK CONTENTION HOTSPOT
50 threads all "waiting to lock <0x000000076b5e4f68>"
→ Check which thread holds 0x...68 and what it's doing
→ Might be a shared singleton with synchronized method

Pattern 3: THREAD POOL EXHAUSTION
All pool threads in WAITING at ThreadPoolExecutor.getTask()
→ Pool waiting for more work OR
All pool threads in BLOCKED at same application lock
→ Pool exhausted by slow/locked operations

Pattern 4: CPU SPIN (RUNNABLE but stuck)
Thread X: RUNNABLE at MyClass.process:42 (same across 3 dumps)
→ Hot loop, spinning on condition without progress
→ Profile to find the tight loop
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (incident response):
Application hangs (CPU=0, no responses)
→ Engineer captures 3 thread dumps (jstack × 3, 10s apart)
→ Open dump 1: search "deadlock" → found → identify threads
→ [Thread Dump Analysis ← YOU ARE HERE]
→ Trace lock cycle: thread A holds lock X, waits for Y
→              thread B holds lock Y, waits for X
→ Find lock acquisition order in source code
→ Fix: establish consistent lock ordering in code
→ Deploy fix → verify no BLOCKED threads in next dump

FAILURE PATH:
Concurrent lock bug only in ReentrantLock (not synchronized)
→ JVM "Found deadlock" message does NOT appear
→ Must manually identify park/unpark chains
→ Grep for "parking to wait for" lines
→ Trace lock addresses manually
→ Consider using jcmd ThreadMXBean.findDeadlockedThreads()
   which covers java.util.concurrent locks

WHAT CHANGES AT SCALE:
With virtual threads (Java 21+), thread dumps can contain
millions of virtual thread entries. Regular thread dump tools
may truncate or time out. Use:
jcmd <pid> Thread.dump_to_file -format=json threads.json
for structured virtual thread dumps. JFR is preferred for
continuous monitoring at virtual-thread scale.
```

---

### 💻 Code Example

```java
// Example 1 — Programmatic thread dump (logging on hang detection)
import java.lang.management.*;
import java.util.Arrays;

void dumpThreadsOnHang() {
    ThreadMXBean tmx = ManagementFactory.getThreadMXBean();

    // Detect deadlocks programmatically
    long[] deadlocked = tmx.findDeadlockedThreads(); // java.util.concurrent too
    if (deadlocked != null) {
        ThreadInfo[] infos = tmx.getThreadInfo(deadlocked, true, true);
        for (ThreadInfo info : infos) {
            log.error("DEADLOCK: {}", info.toString());
        }
    }

    // Full thread dump to log
    ThreadInfo[] allThreads = tmx.dumpAllThreads(true, true);
    for (ThreadInfo info : allThreads) {
        log.debug("Thread: {}\nState: {}\n{}",
            info.getThreadName(),
            info.getThreadState(),
            Arrays.stream(info.getStackTrace())
                  .map(StackTraceElement::toString)
                  .collect(Collectors.joining("\n  at ")));
    }
}

// Example 2 — Watchdog that triggers dump on request timeout
ScheduledExecutorService watchdog = Executors.newSingleThreadScheduledExecutor();
watchdog.scheduleAtFixedRate(() -> {
    long blockedCount = ManagementFactory.getThreadMXBean()
        .getThreadCount(); // approximation
    if (blockedCount > ALERT_THRESHOLD) {
        log.warn("High thread count: {} — dumping threads", blockedCount);
        dumpThreadsOnHang();
    }
}, 0, 30, TimeUnit.SECONDS);
```

---

### ⚖️ Comparison Table

| Tool                       | Real-Time           | Post-Mortem       | Overhead | Best For                        |
| -------------------------- | ------------------- | ----------------- | -------- | ------------------------------- |
| **jstack**                 | Yes (point-in-time) | No                | Very low | Immediate diagnosis             |
| jcmd Thread.print          | Yes (point-in-time) | No                | Very low | Modern replacement for jstack   |
| JFR (Java Flight Recorder) | Yes (continuous)    | Yes (replay file) | <1% CPU  | Always-on monitoring            |
| VisualVM                   | Yes (GUI)           | No                | Medium   | Interactive analysis            |
| async-profiler             | Yes (sampling)      | Yes               | <3% CPU  | CPU profiling + thread analysis |

**How to choose:** Use `jstack` or `jcmd` for immediate incident triage. Enable JFR in production for always-on diagnostics that cover thread state, GC, allocation, I/O — replay after an incident.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                      |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "RUNNABLE" means the thread is actively making progress | RUNNABLE means the thread is eligible to run or is running on a CPU. A thread stuck in a CPU spin loop (infinite while) is RUNNABLE — jstack can't distinguish productive work from spinning. Take 3 dumps and compare stack positions                       |
| JVM deadlock detection catches all deadlocks            | The built-in deadlock detector (`findDeadlockedThreads`) detects cycles in `synchronized` locks AND `java.util.concurrent` locks. But it won't detect application-level deadlocks (e.g., two threads each waiting for the other to put a message in a queue) |
| Thread dumps pause the application significantly        | `jstack` uses JVMTI to read thread state at safepoints — typical overhead is 50–200ms. This is safe in production. `kill -3` has near-zero overhead. Neither crashes the application                                                                         |
| A single thread dump is sufficient for diagnosis        | A single dump shows state at one moment. Lock contention might be transient. Deadlocks ARE stable (same threads stay blocked). For contention and CPU issues, always take 3 dumps 10 seconds apart to observe dynamics                                       |

---

### 🚨 Failure Modes & Diagnosis

**Thread Pool Exhaustion (No Errors, Zero RPS)**

**Symptom:** Application serves zero requests; all active threads in WAITING state; no errors in logs.

**Root Cause:** All thread-pool threads are blocked waiting for a downstream resource (DB connection, HTTP call, distributed lock). No threads available to accept new requests.

**Diagnostic Command:**

```bash
# Capture and analyse:
jstack <pid> > dump.txt
# Find the pool's waiting threads:
grep -c "BLOCKED\|WAITING" dump.txt
# Find what they're waiting for:
grep -B 5 "waiting to lock\|waiting on\|parking to wait" dump.txt \
  | grep "at com.example" | sort | uniq -c | sort -rn
```

**Fix:** Identify and fix the downstream bottleneck. Add timeouts to all blocking calls. Increase thread pool size as temporary mitigation.

**Prevention:** Always set timeouts on DB connections and HTTP calls. Monitor thread pool queue depth as a metric.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread States` — must understand BLOCKED/WAITING/RUNNABLE before reading dumps
- `synchronized` — most lock contention in dumps involves `synchronized` monitors
- `Deadlock` — the primary thing thread dumps are used to diagnose

**Builds On This (learn these next):**

- `Deadlock Detection (Java)` — using `ThreadMXBean.findDeadlockedThreads()` programmatically
- `JFR (Java Flight Recorder)` — always-on thread monitoring beyond point-in-time dumps
- `JVM Profiling` — sampling profilers (async-profiler) complement thread dumps

**Alternatives / Comparisons:**

- `Heap Dump` — captures object graph (OutOfMemoryError diagnosis); thread dump captures thread state
- `JFR` — continuous recording vs point-in-time snapshot; prefer JFR for production monitoring
- `async-profiler` — CPU sampling with flamegraph output; better for performance profiling than lock diagnosis

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Point-in-time snapshot of all JVM         │
│              │ threads, stacks, and lock relationships   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Application hangs: CPU=0, no errors;      │
│ SOLVES       │ need to find deadlocks/blocked threads    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Take 3 dumps 10s apart — movement shows   │
│              │ contention; no movement shows deadlock    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Application hangs; high CPU with low      │
│              │ throughput; suspected deadlock            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Not needed for memory issues (heap dump); │
│              │ not a substitute for continuous monitoring│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero code changes needed vs point-in-time │
│              │ only (JFR is continuous but more setup)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An X-ray of your running JVM: shows every│
│              │  thread, its state, and who it's waiting  │
│              │  for — taken without stopping anything"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JFR → async-profiler → Deadlock Detection │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Thread dumps show `BLOCKED` state for `synchronized` lock contention and `WAITING` state for `java.util.concurrent` lock contention (via `LockSupport.park`). In practice, a `ReentrantLock.lock()` call first performs a CAS (non-blocking) and only parks the thread if the CAS fails. Describe the exact sequence of states a thread transitions through when calling `reentrantLock.lock()` on a contended lock — and explain why diagnosing ReentrantLock contention from a thread dump requires different grep patterns than `synchronized` contention.

**Q2.** Java 21 virtual threads can number in the millions per JVM. Traditional `jstack` produces one entry per thread. If a JVM has 1,000,000 virtual threads, estimating dump file size and parse time: at ~500 bytes per thread entry, that's 500MB of dump. Propose a thread dump strategy for virtual-thread-heavy applications that reduces dump size while retaining enough information to diagnose deadlocks and thread pool exhaustion.
