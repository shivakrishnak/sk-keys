---
layout: default
title: "Full GC"
parent: "Java & JVM Internals"
nav_order: 23
permalink: /java/full-gc/
number: "023"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Heap Memory, Young Generation, Old Generation, Metaspace, Minor GC, Major GC
used_by: GC, OutOfMemoryError, JVM Performance, Memory Leak Diagnosis
tags: #java #jvm #memory #gc #internals #deep-dive
---
# 023 — Full GC

`#java` `#jvm` `#memory` `#gc` `#internals` `#deep-dive`

⚡ TL;DR — The most expensive JVM garbage collection event that simultaneously collects Young Generation, Old Generation, and Metaspace in a single Stop-The-World pause — a symptom of a problem, not a normal operation.

| #023 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, Young Generation, Old Generation, Metaspace, Minor GC, Major GC | |
| **Used by:** | GC, OutOfMemoryError, JVM Performance, Memory Leak Diagnosis | |

---

### 📘 Textbook Definition

Full GC is a **complete heap collection event** that reclaims memory from all JVM memory regions simultaneously: Young Generation (Eden + Survivor spaces), Old Generation, and Metaspace. It is triggered by promotion failure, explicit `System.gc()` calls, Metaspace exhaustion, or GC algorithm failure conditions. Full GC is always Stop-The-World, uses a single-threaded or parallel mark-sweep-compact algorithm across all regions, and typically produces the longest GC pauses — ranging from hundreds of milliseconds to tens of seconds on large heaps.

---

### 🟢 Simple Definition (Easy)

Full GC is the JVM's **emergency whole-heap cleanup** — everything stops, every memory region is collected at once. Seeing Full GC in production is almost always a sign something is wrong.

---

### 🔵 Simple Definition (Elaborated)

Minor GC and Major GC each handle their respective regions independently. Full GC abandons that separation and collects everything at once — Young Gen, Old Gen, and Metaspace — in the most expensive operation the JVM can perform. It's the GC algorithm's last resort when incremental collection has failed. In production, frequent Full GCs are a red flag: they indicate memory pressure, a memory leak, a misconfigured heap, or an allocation rate that has overwhelmed the normal GC cycle.

---

### 🔩 First Principles Explanation

**When normal GC fails — the escalation chain:**

```
Normal operation:
  Minor GC → reclaims Young Gen → fast ✅

Minor GC tries to promote to Old Gen:
  Old Gen has no space → Promotion Failure
  → Minor GC cannot complete normally
  → Must escalate

Escalation attempt 1 — Major GC:
  Collect Old Gen → free space → retry promotion
  If Major GC runs concurrently and Old Gen
  fills before it finishes:
  → Concurrent Mode Failure
  → Must escalate further

Escalation attempt 2 — Full GC:
  Stop everything
  Collect ALL regions simultaneously
  Use most aggressive compaction
  Last resort before OutOfMemoryError

If Full GC still can't free enough:
  → OutOfMemoryError thrown
```

**Why Full GC is so expensive:**

```
Full GC must:
  1. Stop ALL application threads (STW)
  2. Mark ALL live objects (Young + Old + Metaspace)
  3. Sweep ALL dead objects
  4. Compact ALL live objects (slide to one end)
  5. Update ALL references to moved objects
  6. Resume threads

For a 16GB heap with 12GB live:
  Mark 12GB of live objects → scan every field
  Compact 12GB → physically move all data
  Update references → scan everything again
  Time: potentially 10-30 seconds
  During this: zero application progress
  All requests timeout, queue up, or fail
```

---

### ❓ Why Does This Exist — Why Before What

**Without Full GC:**

```
When incremental GC (Minor + Major) fails:
  Memory pressure builds
  Promotion failure → unresolvable
  JVM cannot allocate new objects
  → Immediate OutOfMemoryError on every allocation
  → Application crashes

Full GC exists as:
  "Last chance to reclaim memory before OOM"
  Trades latency (long pause) for correctness
  (application keeps running vs crashing)

It's the JVM saying:
  "I've tried the fast paths (Minor, Major)
   and they're not enough. I'm going to stop
   everything and do a complete, aggressive
   collection. This will hurt, but it's better
   than crashing."
```

**What breaks without it:**
```
1. Promotion failure → immediate OOM
2. Metaspace exhaustion → immediate OOM
3. Memory leak → no last-resort collection
4. System.gc() hint → no mechanism to honour it
5. Long-running processes → more fragile
```

---

### 🧠 Mental Model / Analogy

> Normal GC cycle is like **daily office cleaning** (Minor GC) and **monthly deep office clean** (Major GC).
>
> Full GC is the **emergency total building shutdown** — fire alarm pulled, everyone evacuates (all threads stop), and a hazmat team (GC threads) goes through every room (all memory regions) simultaneously.
>
> You don't pull the fire alarm as routine maintenance. If it's going off regularly, something is seriously wrong — a real fire (memory leak), a broken sprinkler (heap misconfiguration), or someone cooking in their office (allocation rate too high).
>
> Seeing Full GC in logs = investigate immediately, don't accept it as normal.

---

### ⚙️ How It Works — Full GC Triggers and Execution

| #023 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, Young Generation, Old Generation, Metaspace, Minor GC, Major GC | |
| **Used by:** | GC, OutOfMemoryError, JVM Performance, Memory Leak Diagnosis | |

---

### 🔄 How It Connects

```
Trigger condition met
(promotion failure / CMF / Metaspace / System.gc())
      ↓
ALL application threads stopped at safe points
(longest STW event in JVM lifecycle)
      ↓
Full GC runs across ALL regions:
  ┌────────────────────────────────────┐
  │ Young Gen: Eden + Survivor wiped   │
  │ Old Gen: mark-sweep-compact        │
  │ Metaspace: dead ClassLoaders freed │
  └────────────────────────────────────┘
      ↓
All dead objects reclaimed
All live objects compacted
All references updated
      ↓
Threads resume
      ↓
If memory still insufficient:
→ OutOfMemoryError: Java heap space
→ OutOfMemoryError: Metaspace
→ OutOfMemoryError: GC overhead limit exceeded
```

---

### 💻 Code Example

**Identifying Full GC in logs:**
```bash
java -XX:+UseG1GC \
     -Xlog:gc*:file=gc.log:time,uptime,level \
     MyApp
```

```
# NORMAL operations (good):
[1.234s][info][gc] GC(12) Pause Young (Normal) ... 8.234ms
[2.891s][info][gc] GC(13) Pause Young (Normal) ... 6.891ms
[45.21s][info][gc] GC(47) Pause Mixed (G1 Mixed) ... 87ms

# FULL GC (bad — investigate):
[892.3s][info][gc] GC(203) Pause Full (Allocation Failure)
[892.3s][info][gc] GC(203) Phase 1: Mark live objects
[892.3s][info][gc] GC(203) Phase 2: Compute new object addresses
[892.3s][info][gc] GC(203) Phase 3: Adjust pointers
[892.3s][info][gc] GC(203) Phase 4: Move objects
[895.6s][info][gc] GC(203) 3892M->445M(4096M) 3421.ms
#                           Heap: before→after   3.4 SEC PAUSE!

# Diagnose cause:
grep "Pause Full" gc.log
# Count Full GCs and their causes
# "Allocation Failure" → heap too small or memory leak
# "Metadata GC Threshold" → Metaspace leak
# "System.gc()" → explicit call, find who's calling it
```

**Disabling explicit System.gc():**
```bash
# RMI registry calls System.gc() every 60 seconds by default
# This triggers Full GC in your application!

# Fix 1: disable explicit GC entirely
java -XX:+DisableExplicitGC MyApp
# System.gc() becomes a no-op

# Fix 2: make System.gc() concurrent (G1GC only)
java -XX:+ExplicitGCInvokesConcurrent MyApp
# System.gc() triggers concurrent Major GC
# not Full GC → much shorter pause

# Finding who calls System.gc():
# Add JVM flag to print stack trace on System.gc():
java -XX:+PrintGCCause MyApp
# Then in logs find "System.gc()" entries
# Stack trace shows the caller
```

**Monitoring for Full GC in production:**
```java
import java.lang.management.*;
import javax.management.*;

public class FullGCAlert {

    public static void setup() throws Exception {
        for (GarbageCollectorMXBean gc :
                ManagementFactory.getGarbageCollectorMXBeans()) {

            ((NotificationEmitter) gc)
                .addNotificationListener((notif, handback) -> {
                    var info = GarbageCollectionNotificationInfo
                        .from((CompositeData) notif.getUserData());

                    long duration = info.getGcInfo().getDuration();
                    String cause = info.getGcCause();
                    String name = info.getGcName();

                    // Full GC indicators:
                    // G1GC: name contains "G1 Full"
                    // Parallel: name contains "PS MarkSweep"
                    // Serial: name contains "MarkSweepCompact"
                    boolean isFullGC =
                        name.contains("MarkSweep") ||
                        name.contains("Full") ||
                        duration > 500; // > 500ms is likely Full GC

                    if (isFullGC) {
                        // Alert! Page the on-call engineer
                        System.err.printf(
                            "FULL GC ALERT: %s, cause=%s, " +
                            "duration=%dms%n",
                            name, cause, duration
                        );
                        // Send to monitoring: PagerDuty, OpsGenie
                        // alertingService.fire("full-gc", duration)
                    }
                }, null, null);
        }
    }
}
```

**GC overhead limit — special Full GC trigger:**
```bash
# JVM throws OOM if:
# GC is running > 98% of time AND
# < 2% of heap being freed each GC cycle

# Error: java.lang.OutOfMemoryError: GC overhead limit exceeded
# Meaning: app is spending almost all time in GC
#          but getting almost nothing back
# = effective freeze + imminent OOM

# Diagnose: heap dump immediately
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/oom.hprof \
     MyApp

# Disable if false positives (rarely recommended):
java -XX:-UseGCOverheadLimit MyApp
# Disabling means app limps along instead of fast-failing
# Usually better to let it fail fast and diagnose
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Full GC = Major GC" | Full GC collects **all regions**; Major GC collects **Old Gen only** |
| "Full GC is normal and expected" | Full GC is a **last resort** — frequent Full GC = investigate immediately |
| "System.gc() is harmless" | Can trigger Full GC → seconds-long pause → SLA violation |
| "Full GC always fixes memory problems" | If objects are still reachable (leak), Full GC reclaims nothing |
| "ZGC eliminates Full GC" | ZGC dramatically reduces STW but **can still fall back** to Full GC under extreme pressure |
| "Full GC only triggered by OOM pressure" | Also triggered by System.gc(), diagnostics tools, Metaspace, heap dumps |

---

### 🔥 Pitfalls in Production

**1. RMI/NIO silently calling System.gc()**
```java
// java.rmi.dgc.DGC calls System.gc() every 60 seconds
// by default in JVMs that use RMI (including some
// JMX implementations)

// Symptom: Full GC every 60 seconds in logs
// Cause: System.gc() calls
// Nobody on your team wrote System.gc() — but it's there

// Diagnosis:
java -XX:+PrintGCCause MyApp
# Look for: GC cause: System.gc()

// Fix A: disable explicit GC
java -XX:+DisableExplicitGC MyApp

// Fix B: disable RMI GC if not needed
java -Dsun.rmi.dgc.server.gcInterval=3600000 MyApp
# 1-hour interval instead of 60-second

// Fix C: G1GC concurrent explicit GC
java -XX:+ExplicitGCInvokesConcurrent MyApp
```

**2. Full GC masking a memory leak**
```
Symptom timeline:
  Hour 1: Minor GC 5ms, no Full GC ✅
  Hour 4: Minor GC 8ms, occasional Major GC 200ms
  Hour 8: Minor GC 15ms, Major GC 500ms every 5min
  Hour 12: Full GC every 2min, 2sec pauses
  Hour 14: OutOfMemoryError

Pattern: Old Gen baseline growing every hour
Full GC buys time but can't fix the leak

Diagnosis:
  Take heap dumps 1 hour apart:
  jcmd <pid> GC.heap_dump /tmp/heap1.hprof
  # ... wait 1 hour ...
  jcmd <pid> GC.heap_dump /tmp/heap2.hprof

  Compare in Eclipse MAT:
  "Compare Snapshots" → shows what's growing
  "Path to GC Roots" → shows what's holding it

Common causes:
  Static collection without eviction
  ThreadLocal not cleaned up in thread pool
  Cache without size/TTL bounds
  Event listeners never deregistered
```

**3. Full GC during deployment**
```bash
# Spring Boot startup loads many classes
# → Metaspace fills during startup
# → Full GC triggered to collect bootstrap ClassLoaders
# → Startup appears to hang for 1-2 seconds

# Fix: pre-size Metaspace to avoid Full GC at startup
java -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=256m \
     MyApp
# Same min/max = no Metaspace resize = no startup Full GC
```

---

### 🔗 Related Keywords

- `Minor GC` — first line of defense; Full GC is the last
- `Major GC` — Old Gen only; Full GC includes all regions
- `Stop-The-World` — Full GC = longest possible STW pause
- `Promotion Failure` — most common Full GC trigger
- `OutOfMemoryError` — what Full GC is trying to prevent
- `System.gc()` — explicit trigger; use DisableExplicitGC
- `Metaspace` — exhaustion triggers Full GC
- `GC Overhead Limit` — special OOM from GC thrashing
- `Memory Leak` — root cause of most production Full GCs
- `Heap Dump` — essential diagnostic tool when Full GC appears

---

### 📌 Quick Reference Card
```
┌─────────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Entire heap + Metaspace collected at once —      │
│              │ longest STW pause; a production emergency        │
├──────────────┼──────────────────────────────────────────────────┤
│ USE WHEN     │ Unavoidable — but should be rare; frequent       │
│              │ Full GC signals a memory or tuning problem       │
├──────────────┼──────────────────────────────────────────────────┤
│ AVOID WHEN   │ Never call System.gc() in production; fix        │
│              │ memory leaks to prevent Full GC triggers         │
├──────────────┼──────────────────────────────────────────────────┤
│ ONE-LINER    │ "Full GC = the entire heap paused — the          │
│              │  symptom of a broken memory profile"             │
├──────────────┼──────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Stop-The-World → OutOfMemoryError → GC Tuning    │
└─────────────────────────────────────────────────────────────────┘
```
---

### 🧠 Think About This Before We Continue

**Q1.** A colleague argues: "We should call `System.gc()` before each nightly batch job to ensure maximum heap space is available." You disagree. Construct the complete technical argument against this practice — covering what System.gc() actually does, what the likely GC behaviour is, and what the right approach is instead.

**Q2.** Your application experiences Full GC every 4 hours with a 2-second pause. After each Full GC, Old Gen drops from 8GB to 6GB — 2GB freed. But 4 hours later it's back to 8GB. Is this a memory leak? How do you distinguish between "objects accumulating that should be freed" vs "the application legitimately needs 6-8GB of long-lived objects and this is normal Major GC behaviour"?

---
---
number: 024
category: JVM Internals
difficulty: ★★★
depends_on: JVM, GC, Minor GC, Major GC, Full GC, Thread
used_by: GC, JIT Compiler, Deoptimization, Debugger, Thread Dump
tags: #java, #jvm, #gc, #concurrency, #internals, #deep-dive

---