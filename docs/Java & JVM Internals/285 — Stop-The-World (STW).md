---
layout: default
title: "Stop-The-World (STW)"
parent: "Java & JVM Internals"
nav_order: 285
permalink: /java/stop-the-world-stw/
number: "0285"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JVM
  - Thread (Java)
  - GC Roots
  - Safepoint
  - Memory Barrier
used_by:
  - Full GC
  - Minor GC
  - Major GC
  - GC Pause
  - Deoptimization
related:
  - Safepoint
  - GC Pause
  - ZGC
  - Shenandoah GC
  - G1GC
tags:
  - jvm
  - garbage-collection
  - concurrency
  - java-internals
  - performance
---

# 0285 — Stop-The-World (STW)

## 1. TL;DR
> **Stop-The-World (STW)** is a JVM mechanism that **suspends all application (mutator) threads** so GC threads can safely inspect and modify the heap without interference. During an STW pause, no user code runs — the application is completely frozen. Minimizing STW pause duration is one of the central challenges of modern JVM GC design.

---

## 2. Visual: How It Fits In

```
Timeline:
──────────────────────────────────────────────────────────────

Application threads running normally:
T1: ────────────────────┤  PAUSED  ├──────────────────────────
T2: ────────────────────┤  PAUSED  ├──────────────────────────
T3: ────────────────────┤  PAUSED  ├──────────────────────────
T4: ────────────────────┤  PAUSED  ├──────────────────────────

GC threads:
GC1:               ─────────────────────────────────
GC2:               ─────────────────────────────────
                   ▲                               ▲
             STW starts                       STW ends
             (Safepoint)                   (threads resume)

Pause duration = time all threads frozen
ZGC target: < 1ms
G1GC typical: 50–200ms
Serial GC: can be seconds
```

---

## 3. Core Concept

Stop-The-World is required because GC traverses object graphs to find live objects. If application threads continued running while GC scanned memory:

1. **Object references could change** — GC might mark an object as live, then the app nulls the reference, creating a floating garbage problem
2. **New objects could be allocated** — GC wouldn't account for them
3. **Object movement causes pointer invalidation** — during compaction, moving objects while references are live causes segfaults

STW ensures a **consistent heap snapshot**: GC sees a frozen view of all object references.

### Safepoints

STW is implemented via **Safepoints** — special points in bytecode execution where threads can be safely paused:
- Loop back edges
- Method returns
- JNI call/return
- NOT in the middle of arbitrary bytecodes

When the JVM requests STW, each thread runs to its next safepoint and blocks. **Time to safepoint (TTSP)** measures how long it takes for all threads to reach their safepoints.

---

## 4. Why It Matters

STW directly translates to **application latency spikes**:
- P99/P999 latency often reflects GC STW pauses
- Load balancer health checks can fail during long STW
- Connection timeouts occur if STW > timeout threshold
- In distributed systems, STW on one node can cascade to others

High-frequency trading systems, real-time games, telecom signaling — any domain with sub-10ms SLAs must minimize STW to near zero.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Who stops | All mutator (application) threads |
| Who continues | GC threads only |
| Mechanism | Safepoints |
| Minimum STW | ZGC/Shenandoah: < 1ms (just safepoint overhead) |
| Typical STW | G1GC: 50–200ms; Parallel GC: 100ms–seconds |
| Worst case | Serial/Parallel on large heaps: multiple seconds |
| JNI threads | Must also reach safepoint (can delay TTSP) |
| Monitoring | `-Xlog:safepoint*` or GC pause logs |

---

## 6. Real-World Analogy

> Imagine a massive library where hundreds of people (application threads) are constantly moving books (objects) between shelves. A librarian (GC) needs to take inventory — but if people keep moving books while the inventory happens, the count will be wrong. So the library manager rings a bell (safepoint request), everyone freezes in place (STW), the librarian takes inventory and reorganizes shelves (GC work), then rings the bell again (resume). Modern libraries (ZGC) are redesigned so the librarian can take inventory while people move — but this requires much more sophisticated tracking.

---

## 7. How It Works — Step by Step

```
1. JVM decides STW is needed (GC, deoptimization, class redefinition, etc.)

2. Safepoint request issued:
   - JVM sets a global "safepoint requested" flag
   - A special memory page is made unreadable (polling page)

3. Each thread polls the safepoint flag:
   - At method returns, loop back edges, JNI transitions
   - Thread reads the polling page → page fault → thread blocks
   - Thread is now "at safepoint" (suspended)

4. JVM waits for all threads to reach safepoint:
   - Time-to-safepoint (TTSP) begins
   - Long-running native (JNI) code can delay this

5. When ALL threads are at safepoint:
   - STW pause officially begins
   - GC threads perform their work (mark, sweep, compact)

6. GC work completes:
   - JVM issues safepoint resume signal
   - All threads unblock and continue execution
   - Application resumes from exactly where it was frozen

7. STW pause ends:
   - Duration logged in GC logs
   - JVM emits GC metrics (if using JMX, Prometheus, etc.)
```

---

## 8. Under the Hood (Deep Dive)

### Safepoint polling mechanism

```
In HotSpot JVM:
- Safepoint poll site = read from a special memory page
- When GC wants STW: mprotect() makes page unreadable
- Thread reads page → SIGSEGV → signal handler parks thread
- Fast threads reach safepoint immediately
- Slow threads (in JNI, OS syscall) may take longer

TTSP problem:
- If Thread A is in a native sleep(10000), all other threads
  are already parked, but A isn't at safepoint
- JVM must wait for A to return to Java code
- This appears as "time to safepoint" latency in GC logs
```

### Logging TTSP

```bash
# Java 11+ Unified Logging
-Xlog:safepoint*:file=safepoint.log:time,uptime

# Output example:
[0.123s][info][safepoint] Application time: 2.3456789 seconds
[0.456s][info][safepoint] Entering safepoint region: "G1 Evacuation Pause"
[0.478s][info][safepoint] Leaving safepoint region
[0.478s][info][safepoint] Total time for which application threads were stopped: 0.0215432 seconds
#                                                                               ^^^^^ STW pause
#                         Time spent spinning/blocking to reach safepoint:   0.0001234 seconds
#                                                                             ^^^^^ TTSP
```

### Concurrent GC reduces STW

```
Traditional (Parallel GC):
All GC phases are STW:
  STW: [Mark all live objects] → [Sweep garbage] → [Compact heap]

G1GC (Concurrent + STW):
Concurrent: [Mark live objects while app runs]  ← no STW
STW:        [Evacuation pause: move objects]    ← short STW
Concurrent: [Cleanup]                           ← no STW

ZGC (Almost fully concurrent):
Concurrent: [Mark, relocate, remap]             ← no STW
STW:        [Load barriers + safepoint]         ← < 1ms
```

### Non-GC STW events

```
STW is not just for GC! Other STW triggers:
- Deoptimization (JIT fallback to interpreter)
- Class redefinition (JVMTI hot swap)
- Biased lock revocation (deprecated Java 15+)
- Thread dump operations (jstack, JVMTI)
- Heap dump (jmap -dump)
- JVM TI agent operations
```

---

## 9. Comparison Table

| GC Algorithm | STW phases | Typical pause |
|-------------|-----------|---------------|
| Serial GC | All phases | Hundreds of ms to seconds |
| Parallel GC | All phases (parallel) | 100ms–seconds |
| CMS | Initial mark, final remark | ~50–200ms |
| G1GC | Evacuation, initial/final mark | 50–200ms |
| ZGC (Java 15+) | Sub-phases only | < 1ms |
| Shenandoah | Sub-phases only | < 1ms |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Latency-critical (< 10ms SLA) | Use ZGC/Shenandoah to minimize STW |
| Throughput-critical batch | Accept longer STW; use Parallel GC |
| Large heap (> 32 GB) | STW duration scales with heap; use ZGC |
| Profiling STW | `-Xlog:safepoint*` + `-Xlog:gc*` |
| Investigating TTSP | Look for long JNI calls holding up safepoint |

---

## 11. Common Pitfalls & Mistakes

```
❌ Ignoring time-to-safepoint in GC logs
   → Long TTSP looks like long GC pause but root cause is JNI code

❌ Assuming concurrent GC has zero pauses
   → Concurrent collectors still have short STW sub-phases

❌ Long-running JNI native calls
   → Delays all threads reaching safepoint → apparent STW inflation

❌ Using Thread.sleep() in tight loops
   → Thread may not yield safepoint quickly (context dependent)

❌ Forgetting deoptimization causes STW
   → JIT deopt events cause brief but real STW pauses
```

---

## 12. Code / Config Examples

```bash
# Log all STW events (GC + safepoints)
-Xlog:gc*,safepoint*:file=gc-safepoint.log:time,uptime,level

# Diagnose TTSP problems
-Xlog:safepoint=info:file=sp.log:time,uptime

# Use ZGC to minimize STW
-XX:+UseZGC

# Use Shenandoah to minimize STW (OpenJDK)
-XX:+UseShenandoahGC

# G1 with tuned max pause
-XX:+UseG1GC -XX:MaxGCPauseMillis=50
```

```java
// Pattern: Avoid holding locks during JNI calls (can delay safepoint)
// Bad: Lock held across JNI call
synchronized(lock) {
    nativeMethod(); // JNI — delays safepoint while other threads wait
}

// Better: minimize JNI lock scope
nativeResult = nativeMethod();
synchronized(lock) {
    processResult(nativeResult);
}
```

---

## 13. Interview Q&A

**Q: Why does the JVM need Stop-The-World pauses?**
> Because GC needs a consistent view of the heap's object graph. If application threads continue modifying references while GC scans, GC might miss live objects (causing premature collection) or not account for new objects. STW freezes the heap state so GC can safely traverse and modify the object graph.

**Q: How does ZGC achieve < 1ms STW pauses?**
> ZGC performs almost all work concurrently with application threads, using load barriers to handle live reference reads. It only requires STW for very short initialization phases (concurrent mark start/end). This keeps STW below 1ms regardless of heap size.

**Q: What is "time to safepoint" and why does it matter?**
> TTSP is the time between when the JVM requests a safepoint and when all application threads have actually parked. Threads in JNI calls, OS operations, or long loops may take time to reach a safepoint check point. Long TTSP adds to apparent GC pause time and is monitored via `-Xlog:safepoint`.

**Q: Are there STW events besides GC?**
> Yes. Deoptimizations (JIT fallback), class redefinition via JVMTI, thread dumps, heap dumps, and biased lock revocations (pre-Java 15) all require STW pauses.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| What does STW stand for? | Stop-The-World — all app threads suspended |
| What mechanism implements STW in HotSpot? | Safepoints — polling pages that trigger thread parking |
| What is TTSP? | Time-To-Safepoint: latency between safepoint request and all threads parked |
| Which GC achieves < 1ms STW? | ZGC and Shenandoah GC |
| Can non-GC events cause STW? | Yes: deoptimization, class redefinition, heap dumps |

---

## 15. Quick Quiz

**Question 1:** An application shows GC logs with 50ms GC pause, but the safepoint logs show 45ms "time to safepoint". What is the actual GC work time?

- A) 50ms
- B) 95ms
- C) ✅ ~5ms (50ms total - 45ms TTSP)
- D) Cannot determine

**Question 2:** A thread is executing a long JNI call when the JVM requests a safepoint. What happens?

- A) JVM immediately kills the thread
- B) JVM skips that thread's safepoint
- C) ✅ JVM waits for the JNI call to return before the thread checks safepoint
- D) Thread receives SIGKILL signal

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Equating GC pause time with GC work time
   Problem:  GC pause = TTSP + GC work; TTSP can dominate
   Fix:      Log safepoint events separately; tune JNI code

🚫 Anti-Pattern: Choosing GC algorithm without heap size consideration
   Problem:  Serial GC on 32 GB heap = minutes of STW
   Fix:      Match GC algorithm to heap size and latency requirements

🚫 Anti-Pattern: Ignoring STW from non-GC sources in latency analysis
   Problem:  Deopt/JVMTI STW pauses overlooked in profiling
   Fix:      Monitor all safepoint events, not just GC
```

---

## 17. Related Concepts Map

```
Stop-The-World (STW)
├── implemented via ──► Safepoint [#307]
├── required by ─────► Minor GC [#282]
│                  ──► Major GC [#283]
│                  ──► Full GC [#284]
├── minimized by ────► ZGC [#290]
│                  ──► Shenandoah GC [#291]
│                  ──► G1GC [#289]
├── measured as ─────► GC Pause [#294]
└── also triggered by► Deoptimization [#301]
                    ──► Safepoint operations
```

---

## 18. Further Reading

- [Safepoints in HotSpot — Nitsan Wakart](http://psy-lob-saw.blogspot.com/2015/12/safepoints.html)
- [OpenJDK: How JVM Reaches Safepoint](https://wiki.openjdk.org/display/HotSpot/Safepoints)
- [ZGC: Sub-millisecond GC pause design](https://openjdk.org/jeps/333)
- [JVM GC logs: Unified Logging (`-Xlog`)](https://openjdk.org/jeps/158)
- [Understanding TTSP in GC logs](https://blog.gceasy.io/2019/01/meet-time-to-safepoint-problem/)

---

## 19. Human Summary

Stop-The-World is not a bug — it's a fundamental tradeoff. The JVM must pause everything to get a consistent picture of memory. The question isn't whether STW happens, but how long it lasts. Understanding that STW includes both "time to safepoint" (threads finding a safe place to stop) and actual GC work gives you much better diagnostic accuracy. When someone says "our GC pauses are 200ms," they often haven't separated TTSP from actual collection work — and fixing TTSP alone can halve observed latency.

Modern GCs (ZGC, Shenandoah) reduce STW to under a millisecond by making almost all GC work concurrent. But even they can't eliminate STW entirely — the heap still needs brief consistent checkpoints. Knowing this guides collector choice for your workload.

---

## 20. Tags

`jvm` `garbage-collection` `concurrency` `java-internals` `performance` `safepoint` `latency`

