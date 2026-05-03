---
layout: default
title: "Thread Dump Analysis"
parent: "Java Concurrency"
nav_order: 367
permalink: /java-concurrency/thread-dump-analysis/
number: "0367"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread (Java), Thread States, Deadlock Detection (Java), JVM Heap
used_by: Observability & SRE, Production Debugging
related: Deadlock Detection (Java), JVM Tuning, jstack
tags:
  - java
  - concurrency
  - deep-dive
  - observability
  - debugging
---

# 0367 — Thread Dump Analysis

⚡ TL;DR — A thread dump is a point-in-time snapshot of all JVM threads and their current stack traces — it's the primary diagnostic tool for diagnosing deadlocks, thread starvation, high CPU usage, and request hangs in production Java applications.

| #0367           | Category: Java Concurrency                                        | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread (Java), Thread States, Deadlock Detection (Java), JVM Heap |                 |
| **Used by:**    | Observability & SRE, Production Debugging                         |                 |
| **Related:**    | Deadlock Detection (Java), JVM Tuning, jstack                     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java service handles 500 requests/second normally, but at some point response times climb to 30+ seconds. Some requests return 504 Gateway Timeout. The CPU is at 5% (suspiciously low). No errors in application logs. No OOM. The service is "running" but not doing work. Without a thread dump, you're blind — is it a deadlock? Thread pool exhaustion? External call hanging? A lock held too long? You have no visibility into what each thread is actually doing right now.

**THE BREAKING POINT:**
Java applications are multi-threaded by design. When something goes wrong — and it's not CPU, memory, or I/O — the problem is usually in the threads themselves: a thread blocked waiting for a lock another thread holds, a thread pool fully occupied waiting for downstream responses, or a thread in an infinite loop burning CPU. Log files only show completed operations. Thread dumps show the live, in-progress state of every thread at this exact moment.

**THE INVENTION MOMENT:**
Java's `jstack` tool (and the JVM's SIGQUIT/SIGBREAK handler) was designed to expose exactly this: take a snapshot of every thread's current call stack, lock status, and waiting target. This gives you a complete picture of the JVM's threading state at one instant — essential for diagnosing the "why is my service slow/stuck" class of production issues.

---

### 📘 Textbook Definition

**Thread dump:** A snapshot of all Java threads in a JVM process at a specific point in time, including each thread's name, ID, state (RUNNABLE, BLOCKED, WAITING, TIMED_WAITING), current call stack, and information about any locks the thread holds or is waiting for. Generated via `jstack <pid>`, `kill -3 <pid>` (Unix), `Ctrl+Break` (Windows), or JMX/JVM programmatic APIs.

**Thread state:** A value from `java.lang.Thread.State` describing what a thread is currently doing. States relevant to thread dump analysis: `RUNNABLE` (running or eligible to run), `BLOCKED` (waiting to acquire a monitor lock), `WAITING` (indefinitely waiting for notify/LockSupport.park), `TIMED_WAITING` (waiting with a timeout).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A thread dump is an X-ray of your JVM — it shows exactly what every thread is doing right now, which threads are stuck, and why.

**One analogy:**

> A thread dump is like a fire drill roll call. At the exact moment the alarm sounds, every person in the building freezes and reports their current location and activity. After the drill, you can see: 10 people were on floor 3 in a meeting room (WAITING for the meeting to start), 5 people were in the stairwell (RUNNABLE), and 2 people couldn't leave because their colleague was blocking the door (BLOCKED). The roll call gives you the complete state of everyone at that instant.

**One insight:**
Three thread dumps taken 30 seconds apart tell you more than one. A thread that appears in the same BLOCKED state with the same stack trace in all three dumps is genuinely stuck. A thread that's RUNNABLE with a changing stack across dumps is making forward progress (the service is working). This "repeated dump" pattern is the standard production diagnostic technique.

---

### 🔩 First Principles Explanation

**GENERATING A THREAD DUMP:**

```bash
# Method 1: jstack (most common)
jstack <pid>          # instant snapshot
jstack -l <pid>       # include lock information (recommended)

# Method 2: Unix signal (no extra tools needed)
kill -3 <pid>         # sends SIGQUIT → JVM dumps to stdout/log
kill -QUIT <pid>      # same

# Method 3: JVM process tools
jcmd <pid> Thread.print        # modern alternative to jstack
jcmd <pid> Thread.print -l     # with locks

# Method 4: Programmatic (from within JVM)
ThreadMXBean mxBean = ManagementFactory.getThreadMXBean();
ThreadInfo[] info = mxBean.dumpAllThreads(true, true);

# Production pattern: take 3 dumps, 30 seconds apart
for i in 1 2 3; do jstack -l <pid> > dump-$i.txt; sleep 30; done
```

**ANATOMY OF A THREAD DUMP ENTRY:**

```
"http-nio-8080-exec-4" #42 daemon prio=5 os_prio=0 cpu=1230.45ms elapsed=3600.12s
  java.lang.Thread.State: BLOCKED (on object monitor)
    at com.example.OrderService.processOrder(OrderService.java:87)
    - waiting to lock <0x00000006c3a0f1a8> (a com.example.OrderLock)
    at com.example.OrderController.handleRequest(OrderController.java:45)
    at org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:897)
    ...
    Locked ownable synchronizers:
    - None

Thread parts:
  "http-nio-8080-exec-4" → thread name (configurable)
  #42                    → thread ID
  daemon                 → daemon thread (dies when non-daemon threads exit)
  prio=5                 → Java thread priority
  cpu=1230.45ms          → total CPU time consumed by this thread
  elapsed=3600.12s       → thread age (running for 1 hour)
  BLOCKED                → thread state
  waiting to lock <0x...>→ the specific lock this thread is waiting for
```

**KEY PATTERNS TO RECOGNIZE:**

```
PATTERN: DEADLOCK
  Thread A: BLOCKED, waiting for lock X (held by Thread B)
  Thread B: BLOCKED, waiting for lock Y (held by Thread A)
  → Circular wait. Neither can proceed. Service hangs forever.
  Signature: jstack reports "Found one Java-level deadlock:"

PATTERN: THREAD POOL EXHAUSTION
  All worker threads: WAITING at ThreadPoolExecutor.getTask()
  OR
  All worker threads: BLOCKED/WAITING in downstream call (DB, HTTP)
  No threads RUNNABLE for incoming requests.
  Symptom: new requests queue up; response times degrade linearly.

PATTERN: HOT LOCK CONTENTION
  Many threads: BLOCKED, all waiting for the same lock address
  One thread: RUNNABLE, holding that lock
  Signature: many "waiting to lock <0xSAME_ADDRESS>" entries.

PATTERN: INFINITE LOOP / CPU HOT SPOT
  Thread: RUNNABLE, same method across dumps, CPU time growing fast
  Signature: high cpu= in thread header + same stack in all 3 dumps.

PATTERN: LEAK / THREAD ACCUMULATION
  Hundreds of threads all in WAITING or TIMED_WAITING
  Thread names suggest they're from a pool that isn't being recycled.
  Symptom: thread count grows unboundedly; eventually OOM or OS limit.
```

---

### 🧪 Thought Experiment

**SCENARIO:**
Production system. Thread pool size = 200. All 200 threads in state WAITING at `Object.wait()` inside a `ReentrantLock.lock()` call stack. Incoming requests queue up. CPU at 1%.

**DIAGNOSTIC SEQUENCE:**

1. Take 3 thread dumps, 30 seconds apart. All dumps: same 200 threads, same state, same lock address.
2. Find the thread that HOLDS the lock (search for lock address in "Locked ownable synchronizers").
3. That thread's stack trace shows it's in a `Socket.read()` — waiting for a database response that never came.
4. Root cause: one DB connection was leaked — a thread acquired the connection, started a read, and the DB server went away without closing the TCP connection. The thread is hung in `SocketInputStream.read()` indefinitely.
5. Fix: set `socket_timeout` on the JDBC connection (e.g., `socketTimeout=30000ms`), implement connection health checks in HikariCP.

**THE INSIGHT:**
The thread dump revealed the exact line of code causing the cascade: not "the database is slow" (which logs would show) but "one thread is stuck in a socket read, holding a resource that 199 other threads need." This diagnosis is impossible from logs alone.

---

### 🧠 Mental Model / Analogy

> Thread dump analysis is like reading a photograph of a traffic intersection. A 30-second video tells you about flow. But a single photograph (or three photos taken 10 seconds apart) tells you: which cars are stopped at the red light (WAITING/BLOCKED), which are moving (RUNNABLE), and whether two cars are blocking each other (deadlock). The photos don't show cause — but they show the state, which points directly to the cause.

Explicit mapping:

- "photograph" → thread dump (point-in-time snapshot)
- "cars stopped at red light" → threads in WAITING/BLOCKED state
- "moving cars" → RUNNABLE threads (doing actual work)
- "two cars blocking each other" → deadlock (Thread A blocks B, B blocks A)
- "same car stopped in all 3 photos" → genuinely stuck thread (not just transient)
- "traffic signal" → lock/monitor being contended

Where this analogy breaks down: a thread dump doesn't slow down traffic to take it (minimal JVM overhead). It's a snapshot taken while the JVM is live — though with `jstack -l`, there is a brief STW pause for lock enumeration.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A thread dump is a list of everything your Java application's threads are doing right now. It's like asking every worker "what are you working on right now?" and getting an instant report. It's used when your application seems stuck or slow and you want to know why.

**Level 2 — How to use it (junior developer):**
Run `jstack -l <pid>` to generate a dump. Look at the `java.lang.Thread.State` for each thread. Search for `BLOCKED` — those threads are waiting for a lock. Search for `"Found one Java-level deadlock:"` — jstack auto-detects deadlocks. Take 3 dumps 30 seconds apart and compare — threads that don't change state are genuinely stuck.

**Level 3 — How it works (mid-level engineer):**
jstack sends a signal to the JVM (or uses Attach API on Windows) to trigger the ThreadMXBean dump. The JVM iterates over all Java threads, captures each thread's current stack frame, and reports the `ObjectMonitor` state (what monitor the thread holds, what it's waiting for). The lock address `<0x00000006c3a0f1a8>` in the dump is the heap address of the monitor object — you can cross-reference it across threads to find which thread holds a lock and which threads are waiting for it.

**Level 4 — Why this matters for production systems (senior/staff):**
Thread dump analysis is the first-line diagnostic for the entire class of "something is wrong but we have no errors" production incidents. The pattern `N threads BLOCKED on lock X, one thread holding X and waiting for Y` is the classic deadlock signature. `All N pool threads BLOCKED/WAITING in an I/O call` is the thread pool exhaustion pattern — often caused by a missing connection timeout. `One thread RUNNABLE with the same stack in all 3 dumps and high cpu=` is the hot loop / infinite recursion pattern. These three patterns account for the majority of Java production "mystery slowdowns." Thread dumps are the fastest way to distinguish between them.

---

### ⚙️ How It Works (Mechanism)

```
THREAD DUMP GENERATION SEQUENCE:

1. Request: jstack -l <pid>
2. JVM receives signal / attach API call
3. JVM pauses to enumerate locks (brief STW for -l mode)
4. For each Java thread:
   a. Walk the stack frames from top (current method) to bottom (thread start)
   b. Capture ObjectMonitor state: held locks, waiting lock
   c. Output thread header + state + stack + lock info
5. JVM output goes to stdout (kill -3) or jstack's output (attach API)

KEY FIELDS IN DUMP:
  cpu=Xms   → total CPU consumed; high + RUNNABLE = hot thread
  elapsed=Xs → thread age; old thread with low cpu = mostly sleeping
  BLOCKED (on object monitor) → waiting for synchronized()
  WAITING (on object monitor) → in wait(); waiting for notify()
  WAITING (parking)           → in LockSupport.park(); waiting for unpark()
  TIMED_WAITING (sleeping)    → in Thread.sleep() or park(timeout)
  "waiting to lock <addr>"    → wants to acquire this monitor
  "locked <addr>"             → currently holds this monitor
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Production alert: p99 latency 30s (SLA: 500ms)
    ↓
Hypothesis: thread pool exhausted OR deadlock
    ↓
Take 3 thread dumps, 30s apart:
  jstack -l <pid> > dump1.txt
  sleep 30
  jstack -l <pid> > dump2.txt
  sleep 30
  jstack -l <pid> > dump3.txt
    ↓
Analyze:
  grep -c "BLOCKED" dump1.txt → 198 threads blocked
  grep "Found one Java-level deadlock" dump1.txt → not found
  grep "RUNNABLE" dump1.txt → 2 threads runnable (GC threads)
    ↓
Find the lock address in dump1: "waiting to lock <0xABC123>"
grep "0xABC123" dump1.txt | grep "Locked" → thread "db-pool-1"
    ↓
Check "db-pool-1" stack: blocked in SocketInputStream.read()
    ↓
Root cause: DB socket hung. All pool threads waiting for the connection.
    ↓
Fix: Set socketTimeout=30000 in JDBC URL + enable connection validation.
```

---

### 💻 Code Example

**Example 1 — Generating and parsing thread dumps:**

```bash
# Single dump with lock info
jstack -l $(pgrep -f MyApp) > /tmp/dump-$(date +%s).txt

# Three dumps 30 seconds apart (production script)
PID=$(pgrep -f MyApp)
for i in 1 2 3; do
    jstack -l $PID > /tmp/dump-$i.txt
    echo "Dump $i captured: $(grep -c "java.lang.Thread.State" /tmp/dump-$i.txt) threads"
    [ $i -lt 3 ] && sleep 30
done

# Quick analysis: count blocked threads
echo "BLOCKED in dump 1: $(grep -c "BLOCKED" /tmp/dump-1.txt)"
echo "RUNNABLE in dump 1: $(grep -c "RUNNABLE" /tmp/dump-1.txt)"
echo "Deadlock detected: $(grep -c "Found one Java-level deadlock" /tmp/dump-1.txt)"
```

**Example 2 — Programmatic thread dump (monitoring system):**

```java
import java.lang.management.*;

public class ThreadDumpCollector {
    private final ThreadMXBean mxBean = ManagementFactory.getThreadMXBean();

    public Map<Thread.State, Long> getStateDistribution() {
        ThreadInfo[] threads = mxBean.dumpAllThreads(false, false);
        return Arrays.stream(threads)
            .collect(Collectors.groupingBy(
                ThreadInfo::getThreadState,
                Collectors.counting()));
    }

    public List<ThreadInfo> getBlockedThreads() {
        return Arrays.stream(mxBean.dumpAllThreads(true, true))
            .filter(t -> t.getThreadState() == Thread.State.BLOCKED)
            .collect(Collectors.toList());
    }

    public long[] findDeadlockedThreads() {
        long[] ids = mxBean.findDeadlockedThreads();
        return ids != null ? ids : new long[0];
    }
}
```

---

### ⚖️ Comparison Table

| Tool                | Overhead | Detail                    | Auto-detect deadlock | Use case                       |
| ------------------- | -------- | ------------------------- | -------------------- | ------------------------------ |
| `jstack -l`         | Low      | High (full stack + locks) | Yes                  | Primary production diagnostic  |
| `jcmd Thread.print` | Low      | High                      | Yes                  | Modern jstack alternative      |
| `kill -3`           | Minimal  | Medium (stdout only)      | Yes                  | When jstack not available      |
| JVisualVM / JMC     | Medium   | Very high (GUI, history)  | Yes                  | Development + complex analysis |
| async-profiler      | Very low | Very high (flame graphs)  | No (sampling)        | CPU hot spots                  |

How to choose: use `jstack -l` or `jcmd Thread.print` for production diagnostics. Use GCEasy/FastThread.io (upload dump) for automated analysis. Use JMC (Java Mission Control) for GUI-based analysis with a connected JVM.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "RUNNABLE means the thread is doing useful work" | RUNNABLE means the thread is not blocked — it could be in an infinite loop, doing I/O polling, or running GC. High cpu= + RUNNABLE in same stack across 3 dumps = hot thread. |
| "WAITING threads are always a problem"           | Most thread pools have idle threads in WAITING state (waiting for work). Only threads that SHOULD be processing requests but are stuck in WAITING are a problem.              |
| "One thread dump is enough"                      | One dump shows state but not progress. Three dumps 30s apart distinguish "transitionally slow" from "permanently stuck." Automation is important.                             |
| "jstack hangs the JVM"                           | jstack briefly pauses the JVM only for lock enumeration (-l flag). Without -l, it's a rolling snapshot with minimal impact. Safe to use on production.                        |

---

### 🚨 Failure Modes & Diagnosis

**1. Cannot Generate Thread Dump (jstack permission denied)**

**Symptom:** `jstack <pid>` returns "Unable to open socket file" or "Permission denied".

**Root Cause:** jstack must run as the same user as the JVM process. In container environments, the JVM may be running as a different UID.

**Fix:**

```bash
# Run jstack as the JVM process owner:
sudo -u appuser jstack <pid>
# OR use kill -3 from the JVM process's shell:
docker exec -it mycontainer /bin/bash -c "kill -3 1"
# OR use jcmd via the attach mechanism:
jcmd <pid> Thread.print
```

**Prevention:** In Kubernetes, use `kubectl exec` to exec into the pod and run jstack there, where it runs as the same user as the JVM.

---

**2. Thread Dump Shows No Deadlock But Service Is Hung**

**Symptom:** jstack doesn't report "Found one Java-level deadlock" but service is stuck.

**Root Cause:** The deadlock may involve non-Java locks (e.g., database-level locks), or threads are in WAITING state (in `LockSupport.park()`) rather than BLOCKED — jstack's deadlock detection only covers `synchronized` blocks and Java monitors, not ReentrantLock/AbstractQueuedSynchronizer in some cases.

**Fix:** Search for lock addresses manually. Find threads in `WAITING (parking)` and trace their `waiting on condition` — ReentrantLock deadlocks appear as:

```
"Thread A" WAITING (parking)
  at sun.misc.Unsafe.park(...)
  waiting on condition [0x...]
  Locked ownable synchronizers: <0xABC> (ReentrantLock$NonfairSync)
```

Match `Locked ownable synchronizers` addresses across threads to detect manual deadlocks.

**Prevention:** Enable deadlock detection for ReentrantLock by using `ThreadMXBean.findDeadlockedThreads()` programmatically — it detects both monitor and ownable synchronizer deadlocks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread (Java)` — thread dumps report Java thread state
- `Thread States` — the BLOCKED/WAITING/RUNNABLE states in the dump
- `synchronized` — the source of BLOCKED state entries
- `ReentrantLock` — the source of WAITING (parking) entries

**Builds On This (learn these next):**

- `Deadlock Detection (Java)` — the specific failure mode thread dumps are used to diagnose
- `JVM Tuning` — thread pool sizing decisions informed by thread dump analysis

**Alternatives / Comparisons:**

- `Heap Dump` — snapshot of JVM memory (for OOM analysis); thread dump = threading state
- `async-profiler` — CPU profiling via sampling (for performance hot spots); thread dump = point-in-time state

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Point-in-time snapshot of all JVM threads:│
│              │ state, stack, lock info                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Blind spots: service slow/stuck with no   │
│ SOLVES       │ errors — thread dumps reveal the cause    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Take 3 dumps 30s apart: same-state thread │
│              │ across all 3 = genuinely stuck            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service slow/hung with low CPU; high       │
│              │ latency; thread pool exhaustion suspected  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't AVOID — standard production tool;   │
│              │ safe overhead (brief STW for lock info)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Brief JVM pause (jstack -l) vs. lock       │
│              │ detail; use -l in production              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A roll call of every thread: what it's   │
│              │  doing, what it's waiting for, right now."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Deadlock Detection (Java) → JVM Tuning    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A production service has 400 threads, all in `TIMED_WAITING (sleeping)` state — they're in `Thread.sleep(Long.MAX_VALUE)`. The thread names are `"connection-reaper-pool-thread-N"` for N=1 to 400. CPU is at 0.1%. Describe the root cause (what type of bug creates hundreds of sleeping reaper threads?), the production impact, and how you'd verify this hypothesis with a second thread dump.

**Q2.** You take 3 thread dumps on a service with a deadlock. In all 3 dumps, jstack does NOT print "Found one Java-level deadlock." Yet your analysis shows Thread A holds `ReentrantLock` X and is waiting for `ReentrantLock` Y, while Thread B holds Y and waits for X. Explain exactly why jstack's deadlock detector missed this, and write the Java code to programmatically detect it using `ThreadMXBean`.
