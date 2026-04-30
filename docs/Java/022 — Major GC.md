---
layout: default
title: "Major GC"
parent: "Java & JVM Internals"
nav_order: 22
permalink: /java/major-gc/
number: "022"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Old Generation, Minor GC, GC Roots, Heap Memory
used_by: GC, Full GC, Stop-The-World, JVM Performance, G1GC
tags: #java #jvm #memory #gc #internals #deep-dive
---
# 022 — Major GC

`#java` `#jvm` `#memory` `#gc` `#internals` `#deep-dive`

⚡ TL;DR — The expensive, infrequent garbage collection of the Old Generation — triggered when long-lived objects fill the tenured space, causing longer Stop-The-World pauses measured in tens to hundreds of milliseconds.

| #022 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Old Generation, Minor GC, GC Roots, Heap Memory | |
| **Used by:** | GC, Full GC, Stop-The-World, JVM Performance, G1GC | |

---

### 📘 Textbook Definition

Major GC is a **garbage collection event that targets the Old Generation** (Tenured space), collecting long-lived objects that were promoted from the Young Generation. It is triggered when the Old Generation fills to a threshold or when Minor GC promotion fails. Major GC involves tracing all live objects in the Old Gen, reclaiming dead objects, and (in most collectors) compacting the remaining live objects. It is a Stop-The-World event with pauses typically ranging from 50ms to several seconds depending on heap size, GC algorithm, and live object count.

---

### 🟢 Simple Definition (Easy)

Major GC is the **deep clean of the Old Generation** — infrequent, thorough, and much more expensive than Minor GC because it must process the large, long-lived object space.

---

### 🔵 Simple Definition (Elaborated)

While Minor GC handles the high-volume, short-lived objects cheaply, Major GC handles the opposite case — the large Old Generation filled with objects that have survived many GC cycles. These objects are hard to collect: there are fewer dead ones (death rate is low in Old Gen), the region is large (gigabytes), and compaction requires moving live objects and updating all references to them. The result is longer pauses that can significantly impact application latency — which is why modern GC algorithms (G1GC, ZGC) spend so much effort making Major GC either shorter or concurrent.

---

### 🔩 First Principles Explanation

**Why Old Gen collection is fundamentally harder:**

```
Young Gen collection is easy because:
  • Small region (256MB-2GB)
  • High death rate (~98% dead)
  • Copy collection (no fragmentation)
  • Live set is tiny → copy is fast

Old Gen collection is hard because:
  • Large region (2GB-30GB)
  • Low death rate (~10-30% dead per collection)
  • Mark-sweep-compact needed (objects can't just be copied
    efficiently when most are alive)
  • Live set is huge → compaction is slow
  • All references to moved objects must be updated
```

**The compaction problem:**

```
After marking dead objects in Old Gen:
  [LIVE][dead][LIVE][LIVE][dead][dead][LIVE]

Without compaction:
  Fragmentation builds up
  Large object allocation fails even with free space
  ("free" space is scattered, no contiguous block)

With compaction:
  [LIVE][LIVE][LIVE][LIVE][FREE FREE FREE FREE]
  Sliding live objects to one end
  All references to moved objects updated
  Cost: proportional to LIVE objects × reference count
  For 8GB Old Gen with 6GB live = very expensive
```

---

### ❓ Why Does This Exist — Why Before What

**Without Major GC:**

```
Long-lived objects promoted from Young Gen
  → accumulate in Old Gen
  → never collected
  → Old Gen fills
  → JVM throws OutOfMemoryError

Even if objects become unreachable:
  Without collection → memory never reclaimed
  → Every long-lived object = permanent memory leak
  → JVM usable only for trivial short-lived programs

Static fields, caches, singletons, session data
  → All would be permanent memory consumption
  → No way to reclaim when no longer needed
```

**What breaks without it:**
```
1. Memory reclamation for long-lived objects → impossible
2. Static cache eviction → impossible
3. Session cleanup → impossible
4. Long-running servers → always OOM eventually
5. Memory-efficient large applications → impossible
```

---

### 🧠 Mental Model / Analogy

> Minor GC = **emptying the kitchen trash daily** (fast, frequent, small bin).
>
> Major GC = **the annual whole-house deep clean** (slow, rare, everything gets reorganised).
>
> During the deep clean (Major GC), everyone must stop what they're doing (Stop-The-World) while furniture is moved (object compaction), labels are updated (reference updates), and dead items disposed of.
>
> The goal of modern GC design (G1GC, ZGC) is to make the deep clean **concurrent** — cleaners work while the family keeps living normally, pausing only for the unavoidable moments when something is being actively moved.

---

### ⚙️ How It Works — Mark-Sweep-Compact

| #022 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Old Generation, Minor GC, GC Roots, Heap Memory | |
| **Used by:** | GC, Full GC, Stop-The-World, JVM Performance, G1GC | |

---

### 🔄 How It Connects

```
Old Gen fills (from object promotion)
      ↓
Old Gen usage > threshold (default ~70-80%)
      ↓
Major GC triggered
      ↓
Mark phase: identify all live Old Gen objects
      ↓
Sweep phase: identify dead objects
      ↓
Compact phase: slide live objects together
Update all references to moved objects
(most expensive step)
      ↓
Old Gen: compacted, large free contiguous block
      ↓
Application resumes
      ↓
If Major GC can't free enough space:
→ Full GC triggered (includes Young Gen too)
→ If still not enough: OutOfMemoryError
```

---

### 💻 Code Example

**Reading Major GC in logs:**
```bash
java -Xmx2g \
     -XX:+UseG1GC \
     -Xlog:gc*:file=gc.log:time,uptime,level \
     MyApp
```

```
# G1GC Mixed GC (= Major GC in G1 terminology):
[45.231s][info][gc] GC(47) Pause Mixed (G1 Evacuation Pause)
[45.231s][info][gc] GC(47) Eden regions: 24->0(25)
[45.231s][info][gc] GC(47) Survivor regions: 3->3(3)
[45.231s][info][gc] GC(47) Old regions: 87->71(100)
#  Old regions reduced 87→71 = 16 regions reclaimed
[45.231s][info][gc] GC(47) Humongous regions: 0->0
[45.231s][info][gc] GC(47) Metaspace: 45M->45M(256M)
[45.231s][info][gc] GC(47) 412M->285M(2048M) 87.234ms
#  Heap: before→after(total)  Pause time = 87ms

# Concerning signs in Major GC logs:
# Pause > 500ms → tune GC or switch to ZGC
# Old regions barely decreasing → live set too large
# Concurrent Mode Failure → Old Gen filling too fast
```

**Programmatic GC monitoring:**
```java
import java.lang.management.*;
import java.util.*;
import javax.management.*;

public class MajorGCMonitor {

    public static void main(String[] args) throws Exception {
        for (GarbageCollectorMXBean gc :
                ManagementFactory.getGarbageCollectorMXBeans()) {

            System.out.printf(
                "GC: %-30s pools: %s%n",
                gc.getName(),
                Arrays.toString(gc.getMemoryPoolNames())
            );
            // Output:
            // GC: G1 Young Generation   pools: [G1 Eden Space, ...]
            // GC: G1 Old Generation     pools: [G1 Old Gen]
            //     ↑ This is the Major GC collector
        }

        // Register for GC notifications
        for (GarbageCollectorMXBean gc :
                ManagementFactory.getGarbageCollectorMXBeans()) {

            if (gc.getName().contains("Old") ||
                gc.getName().contains("MarkSweep") ||
                gc.getName().contains("Tenured")) {

                ((NotificationEmitter) gc)
                    .addNotificationListener((notif, handback) -> {
                        var info = GarbageCollectionNotificationInfo
                            .from((CompositeData) notif.getUserData());
                        System.out.printf(
                            "MAJOR GC: duration=%dms cause=%s%n",
                            info.getGcInfo().getDuration(),
                            info.getGcCause()
                        );
                    }, null, null);
            }
        }

        // Keep running to receive notifications
        Thread.sleep(Long.MAX_VALUE);
    }
}
```

**Causing and observing Major GC:**
```java
public class MajorGCDemo {

    // Promoting objects to Old Gen:
    static List<byte[]> oldGenObjects = new ArrayList<>();

    public static void main(String[] args) throws Exception {

        // Phase 1: fill Young Gen repeatedly
        // Objects that survive enough Minor GCs promoted
        for (int cycle = 0; cycle < 50; cycle++) {
            // Each iteration: allocate, hold some, release rest
            List<byte[]> temp = new ArrayList<>();
            for (int i = 0; i < 1000; i++) {
                temp.add(new byte[10240]); // 10KB each
            }
            // Hold a few across GC cycles → they get promoted
            oldGenObjects.addAll(temp.subList(0, 10));
            Thread.sleep(10); // let Minor GC run between cycles
        }

        System.out.println("Old Gen should be filling...");
        System.out.println("Old Gen objects: "
            + oldGenObjects.size()); // ~500 objects

        // Phase 2: now release them → Major GC cleans up
        oldGenObjects.clear();
        System.gc(); // hint for demo purposes

        System.out.println("After clear + GC: "
            + oldGenObjects.size()); // 0
    }
}
```

**Choosing the right GC for your Major GC requirements:**
```bash
# Throughput-optimised (batch jobs, offline processing)
# Parallel GC: highest throughput, longer pauses OK
java -XX:+UseParallelGC \
     -XX:MaxGCPauseMillis=500 \
     MyBatchApp

# Latency-optimised (web services, interactive apps)
# G1GC: balanced throughput + pause targets
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     MyWebApp

# Ultra-low latency (trading, real-time, large heaps)
# ZGC: sub-millisecond STW regardless of heap size
java -XX:+UseZGC \
     -XX:MaxGCPauseMillis=10 \
     MyTradingApp

# Shenandoah: similar to ZGC, different algorithm
java -XX:+UseShenandoahGC \
     MyApp
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Major GC = Full GC" | Major GC collects **Old Gen only**; Full GC collects **entire heap** including Young Gen and Metaspace |
| "Major GC is always Stop-The-World" | G1GC/ZGC do most work **concurrently** — only brief STW phases |
| "Major GC triggered on schedule" | Triggered by **Old Gen fill level** or promotion failure |
| "Major GC is rare so it doesn't matter" | One 2-second Major GC pause can violate SLAs and timeout requests |
| "Bigger heap = fewer Major GCs" | Bigger heap = **less frequent** but potentially **longer** Major GCs |
| "Major GC always compacts" | ZGC/Shenandoah compact **concurrently** — no STW compact phase |

---

### 🔥 Pitfalls in Production

**1. Concurrent Mode Failure — worst case scenario**
```bash
# CMS (deprecated) / G1GC specific:
# Old Gen fills WHILE Major GC is running concurrently
# → GC can't finish before Old Gen is full
# → Falls back to Full GC (stop everything)
# → Longest possible pause

# G1GC log:
# [gc] GC(52) Pause Full (G1 Compaction Pause)
# [gc] GC(52) 1892M->445M(2048M) 3421.234ms ← 3.4 SECONDS

# Cause: allocation rate too high for concurrent GC
# Fix 1: increase heap size
# Fix 2: increase InitiatingHeapOccupancyPercent
#        (start Major GC earlier)
java -XX:G1HeapWastePercent=5 \
     -XX:InitiatingHeapOccupancyPercent=45 \
     MyApp
# Start concurrent mark at 45% Old Gen (default 45%)
# Lower = earlier, more frequent but shorter collections
```

**2. Long Major GC pauses violating SLAs**
```bash
# REST API SLA: p99 latency < 200ms
# Major GC pause: 800ms → every Major GC violates SLA

# Step 1: measure current pauses
java -Xlog:gc:file=gc.log MyApp
grep "Pause" gc.log | sort -t= -k2 -n | tail -20
# Find worst pauses

# Step 2: switch to low-latency GC
java -XX:+UseZGC MyApp
# ZGC: STW pauses < 1ms regardless of heap size
# Trade-off: slightly lower throughput

# Step 3: verify improvement
# p99 Major GC pause should drop from 800ms to < 5ms
```

**3. Humongous object allocation causing Major GC**
```java
// G1GC: objects > half of region size = humongous
// Humongous objects allocated directly in Old Gen
// AND trigger concurrent mark immediately

// Bad: frequent large allocations
public byte[] processRequest() {
    return new byte[4 * 1024 * 1024]; // 4MB → humongous
    // Every request → 4MB in Old Gen
    // Old Gen fills fast → frequent Major GC
}

// Fix: reuse large buffers via pool
private static final Queue<byte[]> pool =
    new ConcurrentLinkedQueue<>();

public byte[] getBuffer() {
    byte[] buf = pool.poll();
    return buf != null ? buf : new byte[4 * 1024 * 1024];
}

public void returnBuffer(byte[] buf) {
    // Clear sensitive data, then return to pool
    Arrays.fill(buf, (byte) 0);
    pool.offer(buf);
}
```

---

### 🔗 Related Keywords

- `Old Generation` — the region Major GC collects
- `Minor GC` — fills Old Gen via object promotion
- `Full GC` — superset of Major GC; also collects Young Gen
- `Stop-The-World` — Major GC always has some STW phases
- `Mark-Sweep-Compact` — the algorithm used in Major GC
- `G1GC` — makes Major GC incremental (Mixed GC)
- `ZGC` — makes Major GC nearly fully concurrent
- `Concurrent Mode Failure` — Major GC can't finish before Old Gen full
- `Compaction` — the expensive phase of Major GC
- `InitiatingHeapOccupancyPercent` — G1GC trigger threshold for concurrent mark

---

### 📌 Quick Reference Card
```
┌─────────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Old Generation collection — less frequent,       │
│              │ longer pause; triggered when Old Gen fills       │
├──────────────┼──────────────────────────────────────────────────┤
│ USE WHEN     │ Unavoidable — Old Gen fills from promoted objects │
├──────────────┼──────────────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid frequent Major GC: fix promotion rates     │
│              │ and right-size Old Gen                           │
├──────────────┼──────────────────────────────────────────────────┤
│ ONE-LINER    │ "The expensive clean-up of the long-lived        │
│              │  objects warehouse"                              │
├──────────────┼──────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Full GC → Stop-The-World → G1GC → ZGC            │
└─────────────────────────────────────────────────────────────────┘
```
---

### 🧠 Think About This Before We Continue

**Q1.** G1GC replaces Major GC with "Mixed GC" — it collects a mix of Young Gen regions AND the most garbage-dense Old Gen regions in the same pause. How does this approach solve the classic problem of Major GC pause time growing proportionally with Old Gen size?

**Q2.** A production service runs with a 16GB heap. Old Gen is 12GB. Live set is 10GB (objects that are genuinely still needed). A Major GC must compact 10GB of live objects and update every reference pointing to them. Estimate the minimum time this compaction could take — and explain why ZGC and Shenandoah can claim sub-10ms pauses even with this live set size.

---