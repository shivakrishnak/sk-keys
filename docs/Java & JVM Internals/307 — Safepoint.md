---
layout: default
title: "Safepoint"
parent: "Java & JVM Internals"
nav_order: 307
permalink: /java/safepoint/
number: "0307"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JVM
  - Thread (Java)
  - GC Roots
  - Stop-The-World (STW)
  - JIT Compiler
used_by:
  - Stop-The-World (STW)
  - GC Tuning
  - Deoptimization
  - OSR (On-Stack Replacement)
related:
  - Stop-The-World (STW)
  - GC Pause
  - Deoptimization
  - Write Barrier
tags:
  - jvm
  - gc
  - memory
  - java-internals
  - deep-dive
---

# 0307 — Safepoint

⚡ TL;DR — A safepoint is a JVM-controlled pause point where all threads reach a consistent state, allowing the JVM to safely perform GC, deoptimization, or thread stack inspection without live objects being modified mid-scan.

| #0307 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Thread (Java), GC Roots, Stop-The-World (STW), JIT Compiler | |
| **Used by:** | Stop-The-World (STW), GC Tuning, Deoptimization, OSR (On-Stack Replacement) | |
| **Related:** | Stop-The-World (STW), GC Pause, Deoptimization, Write Barrier | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
The GC must traverse all live objects (reachability analysis). While it scans, application threads keep running — allocating new objects, modifying references, nulling out object fields. A reference the GC just marked as reachable may be nulled a microsecond later. An object the GC hasn't scanned yet may suddenly become unreachable. Without a consistent state, the GC would either miss live objects (corruption) or retain dead objects (leak).

THE BREAKING POINT:
Thread A holds a reference to object X. GC marks X as live. Thread B nulls out the last reference to X. GC continues scanning, never re-scans X. X is treated as live but is actually unreachable. Result: X is never collected. This is a memory leak. Worse: if the order is reversed (GC doesn't mark X yet, then Thread B nulls the reference) — X is treated as garbage and freed. Thread A still has a stale reference. The GC frees the memory. Thread A's reference now points to freed memory. Next access: memory corruption or SIGSEGV.

THE INVENTION MOMENT:
This is exactly why **Safepoints** were created — to provide controlled, predictable moments where all application threads are paused or at a known safe state, allowing the JVM to perform operations requiring a globally consistent heap view.

---

### 📘 Textbook Definition

A **safepoint** is a point in a JVM thread's execution where the thread's execution state (stack, registers, heap references) is fully known and consistent — allowing the JVM to perform globally-coordinated operations. When the JVM triggers a "safepoint stop" (e.g., for GC), it signals all threads to reach their nearest safepoint and pause ("stop the world"). Safepoints are inserted at loop back-edges, method entry/exit, and certain bytecodes in JIT-compiled code. A "safepoint poll" is a check at each safepoint location: if the JVM has requested a stop, the thread blocks until the global operation completes. The time from safepoint request to all threads reaching a safepoint is called "Time To Safepoint" (TTS).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Safepoints are designated "safe stopping spots" in every thread's execution where the JVM knows exactly what the program state looks like.

**One analogy:**
> Imagine a team of surgeons in an operating theater. The anesthetist can only administer a drug when the patient (the program's state) is in a stable position — not mid-incision (mid-object-modification). A safepoint is like the anesthetist calling "check!" at regular intervals, and all surgeons briefly freeze to confirm the patient is stable before the administration. Once all surgeons confirm safe, the drug (GC) can be administered.

**One insight:**
The "Time To Safepoint" (TTS) is often overlooked but can dominate apparent GC pause times. If one thread is executing a 500ms loop body (a tight loop with no safepoint poll inside), the JVM cannot reach a safepoint for that thread during those 500ms. All other threads are already stopped and waiting. This "safepoint bias" — where one slow-to-stop thread's execution time appears as GC pause — is a major source of unreported GC pause overhead.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. GC requires a globally consistent heap view — no thread can modify object references while GC scans.
2. Stopping threads abruptly at arbitrary points is unsafe — the thread might be mid-update of a pointer pair (two-pointer update that must be atomic).
3. All threads must pause quickly (milliseconds) when a safepoint is requested, or the GC pause extends indefinitely.

DERIVED DESIGN:
The JVM inserts "safepoint polls" at strategic locations:
- **Every loop back-edge** (so a tight loop cannot block safepoint indefinitely).
- **Every method call/return** (entry and exit are safe states).
- **Selected bytecodes** that are known safe states.

A safepoint poll is typically a memory load from a JVM-controlled page (`SafepointSynchronize::_state`). In normal operation, the page is readable — the load costs 1ns and succeeds silently. When the JVM requests a safepoint, it makes the page non-readable (SIGSEGV trap) or sets a flag. The next poll: thread reads protected memory → SIGSEGV → JVM safepoint handler pauses the thread.

```
┌──────────────────────────────────────────────────┐
│       Safepoint Mechanism                        │
│                                                  │
│  JVM requests safepoint:                         │
│    Set safepoint_flag = true                     │
│    (or mark safepoint page non-readable)         │
│                                                  │
│  Each thread at next poll:                       │
│    load [safepoint_page]  ← poll                 │
│    flag=false: continue (normal execution)       │
│    flag=true:  thread self-blocks                │
│                                                  │
│  JVM waits for all threads to block              │
│  (Time To Safepoint = wait time here)            │
│                                                  │
│  All threads at safepoint:                       │
│    [JVM performs GC / deoptimization / etc.]     │
│                                                  │
│  JVM releases safepoint:                         │
│    Clear flag, all threads resume                │
└──────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Globally consistent heap view; safe JVM operations (GC, deoptimization, stack traces, thread dumps).
Cost: Safepoint polls add tiny overhead to tight loops and method calls; TTS delays mean one slow thread can hold all others blocked; safepoints cannot occur in JNI code (external code bypasses the poll mechanism).

---

### 🧪 Thought Experiment

SETUP:
An application has 16 threads. 15 threads are executing normal request handling code with safepoint polls at each method call. One thread is executing an optimized tight loop (FFT computation): 10 million iterations with no method calls, no allocation.

JVM REQUESTS SAFEPOINT (GC needed):
- Threads 1–15: each hits a method call → reads safepoint flag → blocks. All 15 stop within 200µs.
- Thread 16 (FFT loop): JIT-compiled, no method calls inside the loop. The next safepoint poll is at the loop's back-edge. The loop takes 50ms to iterate once through its hot inner loop.

OBSERVABLE BEHAVIOR:
GC log reports: "Pause Young (Allocation Failure) 52ms". The actual GC work: 2ms. Time To Safepoint: 50ms waiting for Thread 16. 15 threads are idle for 50ms waiting. The 52ms pause is 96% TTS, 4% actual GC. Users see 52ms GC pause, blame GC, spend weeks tuning GC, never find the root cause.

THE INSIGHT:
TTS is a hidden but impactful source of pause time. Reducing TTS requires ensuring compiled code has safepoint polls at sufficient frequency — which is why `-XX:+UseCountedLoopSafepoints` (JEP 295, Java 9+) was introduced to insert safepoint polls inside counted integer loops that the JIT previously optimized away.

---

### 🧠 Mental Model / Analogy

> A safepoint is like the automatic pause in a DVR recording system. The system only inserts chapter markers at "natural breaks" — between scenes, at scene transitions. If you want to jump to exactly 01:23:45, you can only jump to the nearest chapter marker. Similarly, the JVM can only stop a thread at its nearest safepoint — not at an arbitrary instruction.

"Chapter marker" → safepoint poll location.
"Natural break" → method call, loop back-edge, safe bytecode.
"Cannot jump to arbitrary time" → JVM cannot stop a thread mid-pointer-update.
"DVR waiting for next chapter marker" → Time To Safepoint.

Where this analogy breaks down: DVR markers are fixed in the recording. JIT safepoint polls are inserted dynamically in compiled code and can be configured — a programmer can influence safepoint density via coding patterns (adding method calls in tight loops).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When the JVM needs to do maintenance (like garbage collection), all threads need to reach a safe pause point first — like a traffic light where all cars stop before a construction crew can work on the road. Safepoints are those traffic lights, and the JVM ensures each thread's path is filled with them.

**Level 2 — How to use it (junior developer):**
Safepoints are automatic. Your main concern: avoid tight loops without method calls or allocations in latency-sensitive code. These are the patterns that increase Time To Safepoint. Use `-XX:+UseCountedLoopSafepoints` (Java 9+) to add safepoint polls inside counted loops, and `-Xlog:safepoint` to monitor TTS.

**Level 3 — How it works (mid-level engineer):**
The JIT inserts safepoint poll instructions at: (1) every back-edge, (2) method entry, (3) method exit after returning object. A poll is typically a load from the safepoint page address. In amd64: `test dword ptr [rip + safepoint_offset], eax` — 1 instruction, ~1 cycle if not in safepoint. When the JVM sets the safepoint (marks page non-readable), this load triggers SIGBUS/SIGSEGV → OS delivers signal → JVM's signal handler blocks the thread. This "polling page trick" costs ~0 overhead in the normal (non-safepoint) case.

**Level 4 — Why it was designed this way (senior/staff):**
The safepoint-driven STW model is a compromise between concurrent and incremental GC approaches. STW provides simplicity (GC algorithms don't need barriers for every operation) at the cost of pauses. Fully concurrent GCs (ZGC, Shenandoah) minimize the safepoint footprint: most GC work runs concurrently, only a tiny "STW pause" (a few milliseconds for root scanning or relocation fixup) requires a safepoint. The historical shift: G1GC has multi-millisecond STW phases; ZGC has sub-millisecond STW goals. But even ZGC needs safepoints for certain metadata updates. The "elimination of all safepoints" is a research topic (JEP 461: "no-pause GC"), not yet production-ready in OpenJDK as of Java 21.

---

### ⚙️ How It Works (Mechanism)

**Safepoint Poll Instruction (x86-64):**
```asm
; Compiled method loop back-edge (JIT-generated):
loop_body:
    ... computation ...
    dec ecx
    jnz loop_body           ; loop back edge

    ; SAFEPOINT POLL (inserted here by JIT):
    test eax, [polling_page]  
    ; polling_page is a JVM-managed memory page:
    ;   Normal: page readable → load succeeds → no effect
    ;   Safepoint requested: page made non-readable
    ;   → page fault → OS signal → JVM handler → block thread
```

**Safepoint request sequence:**
1. JVM sets `SafepointSynchronize::_state = synchronizing`.
2. For each thread: set its per-thread safepoint flag OR mark the shared polling page non-readable.
3. Wait until all threads acknowledge (blocked at poll).
4. Execute global operation (GC roots scan, heap inspection, etc.).
5. Resume: set `_state = not_synchronizing`, re-enable threads.

**Safepoint logging:**
```bash
java -Xlog:safepoint=debug MyApp 2>&1 | \
  grep "Application stopped"

# Sample output:
# [GC pause (G1 Young)] 14ms (time-to-safepoint: 12ms)
#                           ^                    ^
#                     total pause         12ms waiting for threads
# Note: GC work was only 2ms; TTS was 12ms!
```

**Counted loop safepoints (Java 9+):**
```bash
# Enable safepoints inside counted int loops:
java -XX:+UseCountedLoopSafepoints MyApp
# Prevents tight numeric loops from blocking safepoint for seconds
# Slight performance overhead (~1%) on numeric code
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[GC detects Eden full / explicit request]
    → [JVM: request safepoint]
    → [All threads: reach next safepoint poll]
    → [Time To Safepoint: varies 50µs – 50ms]  ← YOU ARE HERE
    → [All threads stopped]
    → [GC: scan roots, mark/sweep/compact]
    → [JVM: release safepoint]
    → [All threads resume]
    → [GC pause observed = TTS + GC work time]
```

FAILURE PATH:
```
[One thread has tight counted loop (no safepoint poll)]
    → [TTS = entire loop execution time]
    → [All other threads idle, waiting]
    → [GC pause = TTS + GC work = inflated pause]
    → [Diagnosis: -Xlog:safepoint shows large TTS]
    → [Fix: -XX:+UseCountedLoopSafepoints or add method call]
```

WHAT CHANGES AT SCALE:
In virtual thread workloads (Java 21+), a virtual thread that is parked (waiting on I/O) does not need to reach a safepoint — it is not executing. This dramatically reduces TTS for I/O-heavy workloads. However, the carrier threads (platform threads running virtual threads) do need to reach safepoints. With 16 carrier threads, TTS depends only on those 16 threads, regardless of 100,000 virtual threads — a significant improvement over platform thread models.

---

### 💻 Code Example

Example 1 — Diagnosing high Time To Safepoint:
```bash
# Log safepoints with details:
java -Xlog:safepoint=info \
     -Xlog:gc=info MyApp 2>&1 | \
  grep -E "safepoint|Pause"

# Output:
# [GC] GC(5) Pause Young ... 48.125ms
# [info][safepoint] Safepoint "" 
#   [0.048s: Initial time: 45.1ms  total: 48.1ms]
# → 45ms of 48ms was Time To Safepoint!
```

Example 2 — Pattern causing long TTS (avoid this):
```java
// BAD: Tight counted loop with no safepoints (Java 8 behavior)
// JIT may remove safepoint polls from this:
public void processLargeArray(long[] data) {
    long sum = 0;
    for (int i = 0; i < data.length; i++) {  // counted loop
        sum += data[i];
    }
    return sum;
}
// With 100M element array and no -XX:+UseCountedLoopSafepoints:
// this loop runs for ~100ms with NO safepoint — blocks GC for 100ms
```

Example 3 — Adding safepoints to critical loops:
```java
// GOOD option 1: -XX:+UseCountedLoopSafepoints (Java 9+)
// No code change needed — JIT adds polls automatically

// GOOD option 2: Add a method call to break the loop scope:
public void processLargeArray(long[] data) {
    for (int i = 0; i < data.length; i++) {
        process(data[i]); // method call = safepoint poll
    }
}

// GOOD option 3: Process in chunks:
public void processLargeArray(long[] data) {
    int CHUNK = 100_000;
    for (int start = 0; start < data.length; start += CHUNK) {
        int end = Math.min(start + CHUNK, data.length);
        processChunk(data, start, end); // safepoint between chunks
    }
}
```

Example 4 — Monitoring safepoint time in production via JFR:
```bash
java -XX:StartFlightRecording=duration=60s,\
  filename=safepoint.jfr,settings=profile MyApp

# In JMC: JVM Internals → Safepoint tab
# Shows: TTS per safepoint, which thread blocked longest
# Sorted by Time To Safepoint
```

---

### ⚖️ Comparison Table

| GC Type | Safepoint Footprint | STW Duration | TTS Impact | Best For |
|---|---|---|---|---|
| Serial GC | One full STW | 100ms–2s | Included in pause | Single-thread batch |
| Parallel GC | One full STW | 50ms–500ms | Included in pause | Throughput batch |
| G1GC | Multiple STW phases | 5–100ms | Significant | General service |
| **ZGC** | Tiny STW roots only | <1ms (goal) | Safepoint-driven | Latency-critical services |
| Shenandoah | Tiny STW phases | <10ms | Minimal | Low-latency services |
| Epsilon GC | Normal safepoints | N/A | Minimal (no GC work) | Testing, very short-lived |

How to choose: ZGC minimizes the safepoint footprint. But regardless of GC algorithm, high TTS from application threads (tight loops) is a separate problem requiring code-level fixes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GC pause = GC work time | GC pause = TTS + GC work. A reported "50ms GC pause" could be 48ms TTS + 2ms of actual collection work — the GC algorithm is not the problem |
| Safepoints only happen during GC | Safepoints occur for GC, deoptimization, thread dumps (`jstack`/`jcmd`), class redefinition, biased lock revocation, and any other globally-coordinated JVM operation |
| JIT-compiled code has fewer safepoints than the interpreter | JIT-compiled code has safepoint polls explicitly at loop back-edges and method calls. The interpreter has them more frequently. However, JIT tight loops can (by default) omit safepoint polls from counted loops, which is the opposite of "fewer" |
| Making code faster reduces TTS | Making code faster (shorter execution time per loop iteration) does reduce TTS proportionally, but the only reliable fix is ensuring safepoint polls are present in long loops |
| Thread.sleep() counts as a safepoint | `Thread.sleep()` blocks the thread in the JVM, which implicitly reaches a safepoint. But the statement itself is not a "safepoint poll" in the code — the effect is equivalent because the blocked thread does not prevent safepoint |
| Safepoint pauses disappear with virtual threads | Virtual threads running on carrier threads still need carrier threads to reach safepoints. Parked virtual threads are not executing and don't contribute to TTS |

---

### 🚨 Failure Modes & Diagnosis

**High Time To Safepoint Causing Long GC Pauses**

Symptom:
GC logs report 50–200ms pauses on G1GC, but heap is not heavily loaded. Adding more heap doesn't help. GC work itself (Pause phase) is < 5ms.

Root Cause:
One or more threads are executing tight numeric loops (FFT, compression, image processing) without safepoint polls. These loops block the JVM's safepoint stop mechanism.

Diagnostic Command / Tool:
```bash
java -Xlog:safepoint=debug MyApp 2>&1 | \
  grep "TTS\|time-to-safepoint\|Application stopped"
# Look for large "initial time" values

# More detail with thread-level breakdown:
java -XX:+DiagnoseSyncOnValueBasedClasses \
     -Xlog:safepoint*=debug MyApp
```

Fix:
```bash
# Enable safepoint polls in counted loops (Java 9+):
java -XX:+UseCountedLoopSafepoints MyApp
# 1–3% throughput overhead on numeric workloads
# Eliminates 50–200ms TTS from counted loops
```

Prevention:
Always enable `-XX:+UseCountedLoopSafepoints` on services with numeric processing alongside request-handling code.

---

**JNI Code Preventing Safepoint**

Symptom:
Very long safepoints with a JNI-heavy service. Thread dump shows "in native" for multiple threads during GC.

Root Cause:
Threads executing JNI (native C code) do not execute JVM safepoint polls. They will not contribute to TTS until they return from native code. If a native method takes 1 second, it blocks safepoint for 1 second.

Diagnostic Command / Tool:
```bash
jstack <pid> | grep -A5 "native"
# Look for threads stuck "in native" with long duration
```

Fix:
JNI methods that will execute for > 1ms should call `JNI_EnterCritical/ExitCritical` to mark themselves as "at safepoint" (GC can proceed by pinning the native buffer). Better: minimize JNI call duration.

Prevention:
Profile JNI call duration. Any JNI method taking > 5ms should use Java-native cooperative safepoint patterns.

---

**Thread Dump Causing Application Pause**

Symptom:
`jstack <pid>` takes 1–3 seconds. During that time, the application does not respond to requests.

Root Cause:
`jstack` triggers a JVM safepoint to capture all thread stacks. TTS (waiting for all threads to reach safepoints) adds to the capture time. The application is effectively paused during the entire thread dump.

Diagnostic Command / Tool:
```bash
# Measure how long jstack takes:
time jstack <pid> > /dev/null

# Use jcmd for potentially faster thread dump:
time jcmd <pid> Thread.print > /dev/null

# JFR thread dump: minimal safepoint impact in many cases
jcmd <pid> JFR.dump filename=threads.jfr
```

Fix:
Take thread dumps during low-traffic periods. Use async-profiler's thread dump feature which may avoid full safepoints.

Prevention:
Add thread dump capability to JFR continuous recording instead of on-demand `jstack` in production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — safepoints are a fundamental JVM mechanism; understanding the JVM execution model is prerequisite
- `GC Roots` — safepoints exist primarily to allow GC to scan GC roots safely; understanding what GC roots are clarifies why safepoints matter
- `Stop-The-World (STW)` — STW events are implemented using safepoints; the two concepts are tightly coupled

**Builds On This (learn these next):**
- `GC Pause` — GC pause time = TTS + GC work; understanding safepoints explains the TTS component
- `GC Tuning` — reducing TTS is a GC tuning goal; safepoint knowledge is needed for effective tuning
- `Deoptimization` — deoptimization happens at safepoints; understanding safepoints explains when deoptimization can occur

**Alternatives / Comparisons:**
- `Write Barrier` — an alternative approach to maintaining part of the consistent heap view without requiring full safepoints; used by concurrent GCs to avoid some STW pauses
- `Card Table` — another concurrent GC mechanism that reduces the need for safepoints by tracking dirty regions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JVM-controlled thread pause points where  │
│              │ execution state is fully known & safe     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ GC cannot safely scan heap while threads  │
│ SOLVES       │ are concurrently modifying object refs    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "GC pause time" includes Time To          │
│              │ Safepoint (TTS) + actual GC work.         │
│              │ TTS can dominate — fix: add safepoint     │
│              │ polls to tight loops                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic; enable UseCountedLoopSafepoints│
│              │ for services with tight numeric loops     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cannot avoid; reduce TTS via code design  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Consistent heap view vs thread pause time │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Traffic lights for GC — no repair work  │
│              │  until every car has safely stopped"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Card Table → Write Barrier → Remembered Set│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** ZGC advertises sub-millisecond GC pauses. Given that ZGC still requires safepoints for certain operations (initial mark, final mark, relocation start), explain what ZGC does differently from G1GC to achieve sub-millisecond pause goals — specifically: what work is done concurrently (without safepoints), what work still requires a safepoint, and why the TTS problem is "solved" differently in ZGC than by simply adding more safepoint polls.

**Q2.** A production Java 17 service running G1GC experiences periodic 80ms GC pauses at exactly the same time as a background data processing thread runs a 70ms numeric computation. After enabling `-XX:+UseCountedLoopSafepoints`, the pauses reduce to 12ms. Explain why the remaining 12ms still exists (what generates the remaining safepoint pause), and design a monitoring system that would alert on high TTS specifically (separate from GC work time) using JFR and Prometheus.

