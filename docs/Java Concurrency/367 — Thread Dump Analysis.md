---
layout: default
title: "Thread Dump Analysis"
parent: "Java Concurrency"
nav_order: 367
permalink: /java-concurrency/thread-dump-analysis/
number: "367"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread (Java), Deadlock Detection (Java), Thread Lifecycle, synchronized, ReentrantLock
used_by: Deadlock Detection (Java)
tags:
  - java
  - concurrency
  - advanced
  - observability
  - deep-dive
---

# 367 — Thread Dump Analysis

`#java` `#concurrency` `#advanced` `#observability` `#deep-dive`

⚡ TL;DR — The practice of capturing and interpreting all JVM thread states, stack traces, and lock ownership at a point in time to diagnose deadlocks, thread starvation, and concurrency bottlenecks.

| #367 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), Deadlock Detection (Java), Thread Lifecycle, synchronized, ReentrantLock | |
| **Used by:** | Deadlock Detection (Java) | |

---

### 📘 Textbook Definition

**Thread Dump Analysis** is the diagnostic process of capturing a snapshot of all threads in a JVM process — including their states (RUNNABLE, BLOCKED, WAITING, TIMED_WAITING), stack traces, and lock ownership/wait information — and interpreting this snapshot to identify problems such as deadlocks, thread contention, infinite loops, and resource starvation. Thread dumps are generated via `jcmd <pid> Thread.print`, `kill -3 <pid>` (POSIX), `jstack <pid>`, or programmatic APIs. A thread dump represents a single point-in-time snapshot; diagnosing intermittent problems often requires multiple dumps taken 5–10 seconds apart.

### 🟢 Simple Definition (Easy)

A thread dump is a freeze-frame photo of what every thread in your Java program is doing right now — and analysing it tells you what's blocked, what's stuck, and why.

### 🔵 Simple Definition (Elaborated)

When a Java application becomes unresponsive, hangs, or shows degraded performance, a thread dump reveals exactly what every thread is doing at that moment and — crucially — which locks they're holding and waiting for. You can immediately see if threads are deadlocked (a cycle of threads each waiting for the other's lock), if too many threads are stuck waiting for a single resource (contention), or if one thread has been RUNNABLE for minutes doing CPU-intensive work that blocks everything else. Thread dump analysis is the fastest first-response tool for diagnosing live production concurrency problems.

### 🔩 First Principles Explanation

**What a thread dump contains:**

For each thread:
1. **Name and ID:** `Thread-42`, `http-nio-8080-exec-1`, virtual thread ID.
2. **Daemon status:** daemon threads don't prevent JVM shutdown.
3. **Priority:** 1–10 (rarely meaningful in modern JVMs).
4. **Thread state:** `RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`, `TERMINATED`.
5. **Stack trace:** full call stack from top (current frame) to bottom (thread start).
6. **Lock information:** which locks this thread holds, which it's waiting to acquire.
7. **Deadlock detection:** JVM's built-in deadlock detector summary (for `synchronized`).

**Thread states and what they mean for diagnosis:**

```
RUNNABLE     → executing or ready to execute; use CPU profiling
BLOCKED      → waiting to acquire a monitor (synchronized block)
WAITING      → indefinitely waiting: wait(), join(), park()
TIMED_WAITING→ waiting with timeout: sleep(n), wait(n), park(n)
TERMINATED   → done executing
```

**Identifying the tell-tale patterns:**

- **Deadlock:** Threads A→B→A in lock ownership cycle; JVM prints "Found deadlock" summary.
- **Thread starvation:** Many threads BLOCKED on same monitor held by a single RUNNABLE thread.
- **Hung thread:** Single thread in RUNNABLE state with the same stack trace across multiple dumps.
- **Thread leak:** Hundreds of threads where you expect dozens — thread pool misconfiguration.
- **Lock contention:** Many threads BLOCKED at the same line; bottleneck in that synchronized block.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Thread Dump Analysis:

- You know the service is hung but not why — is it a deadlock, an infinite loop, a slow DB query?
- You add logging after the fact, redeploy, and hope to reproduce the issue.
- Intermittent hangs in production go undiagnosed for months.

What breaks without it:
1. Deadlocks can only be inferred from "service stopped responding" metrics — no root cause.
2. Thread starvation looks identical to CPU overload in external monitoring — different fixes required.

WITH Thread Dump Analysis:
→ Deadlock confirmed and root cause stack trace in < 5 minutes.
→ Contention bottleneck identified: exact `synchronized` line causing 95% thread pile-up.
→ Thread leak counted: 2,000 threads vs expected 200 — pool configuration bug.

### 🧠 Mental Model / Analogy

> A thread dump is like a sudden power outage that freezes everyone in a busy factory in place. You walk through the frozen factory and ask each worker: "What were you doing? What tools are you holding? What are you waiting for?" Some are frozen mid-task (RUNNABLE). Some are arms-crossed waiting for a machine (BLOCKED). Some are waiting for a coworker to finish something (WAITING). Two workers are found each waiting for the other's tool — deadlock. The freeze reveals the invisible dynamics of the running factory.

"Factory" = JVM, "power outage" = thread dump, "frozen workers" = threads, "tools" = locks, "machine" = monitor.

The key insight: you need the freeze to see the dynamics — continuous monitoring can't capture a deadlock state.

### ⚙️ How It Works (Mechanism)

**Generating a Thread Dump:**

```bash
# Method 1: jcmd (recommended, Java 11+)
jcmd <pid> Thread.print > thread_dump.txt

# Method 2: jstack (legacy, but widely available)
jstack <pid> > thread_dump.txt

# Method 3: OS signal (Linux/macOS)
kill -3 <pid>  # outputs to stdout/stderr of the process

# Method 4: IntelliJ / JConsole / VisualVM:
# GUI button "Get Thread Dump"

# For virtual threads (Java 21):
jcmd <pid> Thread.print -e   # extended: includes virtual threads
```

**Reading a Thread Dump Entry:**

```
"http-nio-8080-exec-1" #32 daemon prio=5 os_prio=0
  java.lang.Thread.State: BLOCKED (on object monitor)
    at com.example.OrderService.processOrder(OrderService.java:78)
    - waiting to lock <0x00000007d2b3c1a0> (a java.lang.Object)
    at com.example.RequestHandler.handle(RequestHandler.java:34)
    ...

Breakdown:
  "http-nio-8080-exec-1" → thread name
  #32                    → thread number
  daemon                 → daemon thread
  BLOCKED                → state: waiting for a lock
  waiting to lock <0x...>→ waiting to acquire THIS monitor
  OrderService.java:78   → the blocked line
```

**Deadlock pattern:**

```
Found one Java-level deadlock:
"Thread-A":
  waiting to lock monitor 0x00007f8c1c003f08 (obj foo),
  which is held by "Thread-B"
"Thread-B":
  waiting to lock monitor 0x00007f8c1c004010 (obj bar),
  which is held by "Thread-A"
```

**Multiple dumps for intermittent problems:**

```bash
# Capture 3 dumps 5 seconds apart
for i in 1 2 3; do
    jcmd <pid> Thread.print > dump_$i.txt
    sleep 5
done
# If Thread-X is RUNNABLE with same stack in all 3 → true hang
# If state changes between dumps → transient issue
```

### 🔄 How It Connects (Mini-Map)

```
JVM Process running (threads in various states)
           ↓
Thread Dump captured (jcmd / jstack / kill -3)
           ↓
Thread Dump Analysis ← you are here
           ↓
Diagnosis:
  Deadlock → Deadlock Detection (Java)
  Contention → synchronized / ReentrantLock
  Starvation → Thread priority / executor sizing
  Leak → ThreadPoolExecutor config
```

### 💻 Code Example

Example 1 — Programmatic thread dump via ThreadMXBean:

```java
import java.lang.management.*;

public class ThreadDumpCollector {
    public static String captureThreadDump() {
        ThreadMXBean tmx =
            ManagementFactory.getThreadMXBean();
        StringBuilder sb = new StringBuilder();

        // Detect deadlocks immediately
        long[] deadlockedIds = tmx.findDeadlockedThreads();
        if (deadlockedIds != null) {
            sb.append("DEADLOCK DETECTED on threads: ")
              .append(java.util.Arrays.toString(deadlockedIds))
              .append("\n");
        }

        // All thread info with lock/monitor data
        ThreadInfo[] infos = tmx.dumpAllThreads(
            true,  // lockedMonitors
            true   // lockedSynchronizers (j.u.c. locks)
        );
        for (ThreadInfo info : infos) {
            sb.append(info.toString());
        }
        return sb.toString();
    }
}
```

Example 2 — Detecting thread starvation pattern:

```bash
# In the dump, count threads BLOCKED on same monitor
grep -A2 "BLOCKED" thread_dump.txt | grep "waiting to lock" | \
  sort | uniq -c | sort -rn | head -5

# Output like:
# 156  - waiting to lock <0x7f8c1c003f08> (a java.util.HashMap)
# → 156 threads blocked on a single HashMap
# → Root cause: HashMap not thread-safe, should use ConcurrentHashMap
```

Example 3 — Analysing thread dump with fastThread or jstack analysis:

```bash
# anonymise and upload to fastthread.io (online analyser)
jstack <pid> > dump.txt
# Or use command-line tools
# TDA (Thread Dump Analyser): open-source GUI tool
# jstack with -l flag for j.u.c. lock details
jstack -l <pid> > dump_with_locks.txt
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A thread dump pauses the JVM for a long time | Thread dump generation pauses the JVM briefly (< 100ms typically) to capture a consistent snapshot; not a significant production impact. |
| RUNNABLE threads are always doing CPU work | RUNNABLE includes threads waiting for I/O at the OS level; a thread blocked on socket read can appear RUNNABLE in a dump. |
| Deadlock detection catches all deadlocks | JVM deadlock detection finds `synchronized` monitor deadlocks; Lock (j.u.c.) deadlocks are found via `findDeadlockedThreads()` only if lock info was captured with `-l` flag. |
| Thread leaks always show as RUNNABLE threads | Leaked threads in WAITING/TIMED_WAITING state also consume resources even though they're not running. Count total threads, not just RUNNABLE. |
| One thread dump is sufficient for diagnosis | A single dump is a snapshot; many problems (intermittent deadlocks, GC-induced pauses) require 3–5 dumps taken seconds apart to confirm pattern. |

### 🔥 Pitfalls in Production

**1. Diagnosing a Deadlock After the Fact — No Dumps Captured**

```bash
# BAD: No thread dump collected during the freeze
# Service restarts automatically via health check
# Deadlock evidence gone forever

# GOOD: Auto-capture thread dump on health check failure
# In Kubernetes: add a preStop hook or liveness probe action
# Or: programmatically detect and log dumps via ThreadMXBean
# every 60s when GC overhead > 20%
```

**2. Confusing RUNNABLE I/O Wait with CPU Spin**

```
# Thread shows RUNNABLE at:
"http-exec-1" State: RUNNABLE
  sun.nio.ch.Net.poll(Native Method)    ← OS-level I/O wait
  sun.nio.ch.SocketDispatcher.read()

# This thread is NOT consuming CPU — it's waiting for network
# Don't try to "fix" this by interrupting it
# RUNNABLE at native socket read is expected blocking I/O
```

**3. Not Capturing Lock Ownership Info**

```bash
# BAD: Plain jstack without lock info
jstack <pid> > dump.txt
# → Doesn't show j.u.c. ReentrantLock ownership

# GOOD: Include locked synchronizers
jstack -l <pid> > dump.txt
# or
jcmd <pid> Thread.print > dump.txt  # includes j.u.c. locks
```

### 🔗 Related Keywords

- `Deadlock Detection (Java)` — what thread dump analysis is most commonly used for.
- `Thread Lifecycle` — the states (RUNNABLE, BLOCKED, WAITING) visible in thread dumps.
- `synchronized` — the source of BLOCKED state and monitor ownership in dumps.
- `ReentrantLock` — j.u.c. locks whose ownership appears in thread dumps with `-l`.
- `ThreadPoolExecutor` — thread dump shows pool thread states and task queue depth.
- `Virtual Threads (Project Loom)` — Java 21 thread dumps include virtual thread state.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Point-in-time snapshot of all JVM threads:│
│              │ states, stacks, and lock ownership.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service hangs, high CPU with no progress, │
│              │ suspected deadlock, thread leak diagnosis.│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ — (always valuable; minimal performance   │
│              │ impact; should be routine for incidents)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Thread dump: the freeze-frame that shows │
│              │ every thread's alibi."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Deadlock Detection → Lock Striping        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Three thread dumps captured 5 seconds apart all show the same 200 threads in TIMED_WAITING state, with stacks indicating `LockSupport.parkNanos()` inside `HikariCP.getConnection()`. The service is running but response times are 10× normal. What is the most likely root cause, how would you confirm it from the thread dumps alone without additional tooling, and what would you change to fix it?

**Q2.** Traditional thread dumps include platform threads with full stack traces; virtual thread dumps in Java 21 may show thousands of virtual threads but with limited carrier thread attribution. Explain why diagnosing a deadlock in a virtual-thread-heavy application is fundamentally different from diagnosing it in a platform-thread application, and what specific properties of virtual threads make some traditional deadlock patterns impossible while introducing new failure modes.

