---
layout: default
title: "Stop-The-World (STW)"
parent: "Java & JVM Internals"
nav_order: 24
permalink: /java/stop-the-world-stw/
number: "024"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, GC, Minor GC, Major GC, Full GC, Thread
used_by: GC, JIT Compiler, Deoptimization, Debugger, Thread Dump
tags: #java #jvm #gc #concurrency #internals #deep-dive
---
# 024 — Stop-The-World (STW)

`#java` `#jvm` `#gc` `#concurrency` `#internals` `#deep-dive`

⚡ TL;DR — A JVM pause where all application threads are suspended simultaneously at safe points so GC (or other JVM operations) can safely inspect and modify the heap without concurrent interference.

| #024 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Minor GC, Major GC, Full GC, Thread | |
| **Used by:** | GC, JIT Compiler, Deoptimization, Debugger, Thread Dump | |

---

### 📘 Textbook Definition

Stop-The-World (STW) is a **JVM mechanism that suspends all application threads at safe points** to allow the JVM to perform operations that require a consistent, non-mutating view of the heap or thread state. During an STW pause, no application code executes — all threads are frozen at known safe points where their state is fully described. STW is primarily used by garbage collectors but also by JIT deoptimisation, class redefinition (hot-swap), heap dumps, and thread dumps. Minimising STW pause duration and frequency is the primary goal of modern GC algorithm design.

---

### 🟢 Simple Definition (Easy)

Stop-The-World is the JVM hitting a **universal pause button** — every application thread freezes simultaneously while the JVM does housekeeping it can't safely do with threads running.

---

### 🔵 Simple Definition (Elaborated)

The JVM needs to periodically inspect the entire heap to find live and dead objects. But if application threads are still running and modifying references while GC is scanning, the GC might miss a newly created object (and wrongly collect it) or follow a stale reference (and corrupt memory). Stop-The-World solves this by pausing all threads first — ensuring a consistent snapshot. The cost is application latency during the pause. Modern GC algorithms minimise STW by doing most work concurrently, reserving STW for only the brief phases where consistency is absolutely required.

---

### 🔩 First Principles Explanation

**The fundamental concurrency problem in GC:**

```
GC scanning heap (marking live objects):
  GC: "Object A has reference to Object B — B is live"

Simultaneously, application thread running:
  App: "I'm nulling the reference A→B"
  App: "I'm creating new reference C→B"

Race conditions:
  1. GC marks B live via A→B
     App nulls A→B AFTER GC scans A
     App also nulls C→B before GC scans C
     GC never marks B via C (missed)
     → GC concludes B is DEAD
     → B collected → C→B now dangling pointer
     → SEGFAULT / corrupt memory

  2. GC scanning A
     App creates new object D (not yet seen by GC)
     GC doesn't know about D
     → D might be incorrectly collected
```

**The simple solution — freeze everything:**

> "Stop all application threads so the heap is
>  completely static while GC runs. No races,
>  no concurrent modifications, perfect consistency."

**The cost:**

```
STW pause = zero application progress
During STW:
  HTTP requests hang (not processed)
  Database queries queue up
  Users experience latency spike
  Timeouts possible for long pauses

This is why pause time is the #1 GC metric
for latency-sensitive applications
```

---

### ❓ Why Does This Exist — Why Before What

**Without Stop-The-World:**

```
Fully concurrent GC without any STW:
  Must handle ALL of these races:
  • Object created during marking (not seen)
  • Reference nulled during marking (incorrectly live)
  • Reference added during marking (missed)
  • Object moved while app holds reference

  Solutions attempted:
  • Write barriers: track every reference modification
    → overhead on every object write
  • Read barriers: intercept every reference read
    → even more overhead
  • SATB (Snapshot-At-The-Beginning): G1GC approach
    → complex, still needs brief STW for consistency

  Even ZGC (closest to STW-free) has:
  → Brief STW for initial mark (~1ms)
  → Brief STW for remark (~1ms)
  Total: ~2ms STW even in "concurrent" GC

  True zero-STW GC = theoretically possible
  but practically: load barriers + write barriers
  overhead is significant
  No production JVM achieves zero STW today
```

**With STW:**
```
→ Simple, correct GC algorithm
→ No barriers needed during STW phases
→ Consistent heap snapshot guaranteed
→ Trade latency (pause) for correctness
→ Modern GCs minimise STW duration
   not eliminate it entirely
```

---

### 🧠 Mental Model / Analogy

> Imagine taking a **census of a moving city**.
>
> If people keep moving between neighbourhoods while you count them, you'll double-count some and miss others. The census is wrong.
>
> **Stop-The-World = declaring a Census Day** where everyone must stay at their registered address (safe point) while counters (GC threads) visit every household (object).
>
> Once counting is done, people can move freely again.
>
> Modern GC (G1GC, ZGC) is like a **rolling census** — they count most neighbourhoods while people still move around, using special tracking (write barriers) to handle moves. They only freeze everyone for the brief moments where they must reconcile the counts. Pause = seconds → milliseconds.

---

### ⚙️ How It Works — Safe Points

| #024 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Minor GC, Major GC, Full GC, Thread | |
| **Used by:** | GC, JIT Compiler, Deoptimization, Debugger, Thread Dump | |

---

### 🔄 How It Connects

```
GC needs consistent heap view
      ↓
JVM sets safepoint request flag
      ↓
All threads reach next safe point
(method return, loop back edge)
      ↓
All threads suspended
(STW pause begins — clock starts)
      ↓
GC executes:
  Minor GC: copy Young Gen survivors
  Major GC: mark-compact Old Gen
  Full GC:  collect all regions
      ↓
GC completes
(STW pause ends — clock stops)
      ↓
All threads resume simultaneously
      ↓
Pause duration reported in GC log
```

---

### 💻 Code Example

**Measuring STW impact:**
```bash
# Log all STW pauses with timestamps
java -XX:+UseG1GC \
     -Xlog:safepoint:file=safepoint.log:time,uptime \
     -Xlog:gc:file=gc.log:time,uptime \
     MyApp
```

```
# safepoint.log — all STW events (not just GC):
[0.234s] Safepoint "G1CollectForAllocation", Time since last: 1234ms
         Reaching safepoint: 0.23ms   ← TTSP
         At safepoint: 8.91ms          ← actual pause
         Total: 9.14ms

[0.891s] Safepoint "Deoptimize", Time since last: 657ms
         Reaching safepoint: 0.11ms
         At safepoint: 0.45ms
         Total: 0.56ms                ← JIT deoptimisation pause

# Key metrics:
# "Reaching safepoint" = TTSP (time to safepoint)
# "At safepoint" = actual work duration
# Total = what application sees as pause
```

**Time-to-safepoint problem:**
```java
// PROBLEMATIC: long loop without safepoint opportunity
// JIT may optimise away safepoint checks in counted loops
public void longLoop() {
    long sum = 0;
    for (int i = 0; i < Integer.MAX_VALUE; i++) {
        sum += i;  // tight loop — JIT may omit safepoint poll
    }
    // Thread stays here for seconds
    // ALL OTHER THREADS waiting at safepoints
    // STW pause = entire loop duration!
}

// Check with:
java -XX:+PrintSafepointStatistics MyApp
# Shows if TTSP is high

// Fix: Java 10+ — JIT always includes safepoint at
// loop back edges in compiled code
// But: older JVMs or JNI calls can still cause TTSP issues
```

**Observing non-GC STW events:**
```bash
# STW is used for more than just GC:
java -Xlog:safepoint MyApp

# Common non-GC STW events:
# Deoptimize          ← JIT deoptimisation
# RevokeBias          ← biased lock revocation (pre Java 21)
# FindDeadlocks       ← deadlock detection
# ThreadDump          ← jstack / thread dump
# HeapDumper          ← jmap heap dump
# ClassRedefinition   ← hot-swap via debugger/agent
# ICBufferFull        ← inline cache buffer management

# These are usually short (<5ms)
# But if happening frequently → investigate
```

**Measuring pause impact on request latency:**
```java
// Correlate GC pauses with request latency percentiles
// using application-level timing

public class PauseTracker {

    private static volatile long lastHeartbeat =
        System.nanoTime();

    // Dedicated thread monitoring for pauses
    static {
        Thread monitor = new Thread(() -> {
            while (true) {
                long now = System.nanoTime();
                long gap = now - lastHeartbeat;

                // Gap > 50ms when we expected 10ms
                // = we were paused for ~40ms
                if (gap > 50_000_000L) {
                    System.err.printf(
                        "Detected pause: %.1fms at %s%n",
                        gap / 1_000_000.0,
                        LocalTime.now()
                    );
                }
                lastHeartbeat = now;

                try { Thread.sleep(10); }
                catch (InterruptedException e) { break; }
            }
        });
        monitor.setDaemon(true);
        monitor.start();
    }
}
// Pause gaps in this log correlate with GC log timestamps
// Proves STW pauses are affecting request latency
```

---

### ⚙️ STW Across GC Algorithms

| #024 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Minor GC, Major GC, Full GC, Thread | |
| **Used by:** | GC, JIT Compiler, Deoptimization, Debugger, Thread Dump | |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Only GC causes STW" | JIT deoptimisation, thread dumps, heap dumps, class redefinition also cause STW |
| "ZGC has no STW" | ZGC has **sub-10ms STW** — not zero; but practically negligible |
| "Concurrent GC = no pause" | Concurrent = GC runs alongside app for most work; still brief STW for consistency |
| "STW affects only the GC thread" | STW affects **ALL application threads** simultaneously |
| "More GC threads = shorter STW" | More threads helps but shows **diminishing returns** due to coordination overhead |
| "Safe points are placed everywhere" | Safe points are placed at **specific positions** by JIT — not every instruction |

---

### 🔥 Pitfalls in Production

**1. High time-to-safepoint from JNI**
```java
// JNI calls can delay safepoint for their entire duration
// Other threads waiting at safepoints
// → STW pause = GC work + JNI duration

// Symptom: GC log shows normal GC duration
//          but application sees much longer pause
// safepoint.log: "Reaching safepoint: 450ms"
// ← 450ms spent waiting for JNI thread!

// Fix: check for long-running JNI calls
// Add safepoint polls in native code if possible
// Or: use shorter JNI interactions with callbacks
```

**2. Counted loops blocking safepoints (pre-Java 10)**
```java
// DANGEROUS in Java 8 with JIT compilation:
// JIT may optimise counted loops to remove safepoint polls

// Cause: JIT proves loop terminates → optimises away poll
public void dangerousLoop(int[] data) {
    int sum = 0;
    for (int i = 0; i < data.length; i++) {
        sum += data[i];  // may have no safepoint poll
    }
}
// With data.length = 10M → loop takes 10ms
// Other threads wait at safepoint for 10ms
// Appears as 10ms "GC pause" with zero GC work

// Fix (Java 8): -XX:+UseCountedLoopSafepoints
// Java 10+: fixed by default
```

**3. Safepoint bias in profilers**
```
Traditional sampling profilers (JProfiler, YourKit)
sample thread states AT safepoints

Problem: safepoints are at:
  method returns, loop back edges, before calls
Not at:
  middle of tight inner loops

Result: profiler never samples inside tight loops
→ "Hot" code appears cold in profiler
→ Profile shows wrong bottleneck

Fix: use async-profiler (AsyncGetCallTrace)
  Samples at ANY point, not just safepoints
  True wall-clock profiling
  Shows actual hot code

java -agentpath:/path/to/async-profiler.so=\
     start,event=cpu,file=profile.html \
     MyApp
```

---

### 🔗 Related Keywords

- `GC` — primary user of Stop-The-World mechanism
- `Safe Point` — thread positions where STW can be initiated
- `Minor GC` — always STW but brief (1-50ms)
- `Full GC` — longest STW event (100ms-30s)
- `ZGC` — minimises STW to sub-10ms via concurrent collection
- `Time-to-Safepoint (TTSP)` — delay from request to all threads paused
- `JIT Compiler` — uses STW for deoptimisation
- `Thread Dump` — causes brief STW to capture all thread states
- `Write Barrier` — mechanism that allows REDUCING STW in concurrent GC
- `async-profiler` — profiles without safepoint bias

---

### 📌 Quick Reference Card
```
┌─────────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ All application threads paused while JVM        │
│              │ performs an operation requiring a safe state     │
├──────────────┼──────────────────────────────────────────────────┤
│ USE WHEN     │ Inevitable — every GC has some STW; minimise     │
│              │ with low-pause GCs (G1, ZGC, Shenandoah)        │
├──────────────┼──────────────────────────────────────────────────┤
│ AVOID WHEN   │ Long STW pauses in latency-sensitive apps —      │
│              │ switch to ZGC for sub-millisecond STW            │
├──────────────┼──────────────────────────────────────────────────┤
│ ONE-LINER    │ "The whole world stops so the JVM can            │
│              │  work in consistent, single-threaded peace"      │
├──────────────┼──────────────────────────────────────────────────┤
│ NEXT EXPLORE │ G1GC → ZGC → Shenandoah → GC Safepoint           │
└─────────────────────────────────────────────────────────────────┘
```
---

### 🧠 Think About This Before We Continue

**Q1.** ZGC claims sub-10ms STW pauses for any heap size — even 1TB heaps. Traditional GC pause time grew proportionally with live object set size (more objects to compact = longer pause). What fundamental algorithm change does ZGC make to decouple pause time from heap/live set size — and what trade-off does it make to achieve this?

**Q2.** A thread dump (jstack) causes a brief STW pause. A heap dump (jmap) causes a longer STW pause. Both require STW. Given what you know about safe points and STW mechanics — why does a heap dump require a longer pause than a thread dump, even though both just "read" JVM state?

---