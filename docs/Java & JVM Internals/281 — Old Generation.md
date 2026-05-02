---
layout: default
title: "Old Generation"
parent: "Java & JVM Internals"
nav_order: 281
permalink: /java/old-generation/
number: "281"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Heap Memory, Young Generation, Eden Space, Survivor Space
used_by: Major GC, Full GC, G1GC, ZGC, GC Tuning
tags:
  - java
  - jvm
  - memory
  - gc
  - internals
---

# 281 — Old Generation

`#java` `#jvm` `#memory` `#gc` `#internals`

⚡ TL;DR — The heap region that holds long-lived objects which survived multiple Young Generation collections.

| #281 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Heap Memory, Young Generation, Eden Space, Survivor Space | |
| **Used by:** | Major GC, Full GC, G1GC, ZGC, GC Tuning | |

---

### 📘 Textbook Definition

The **Old Generation** (also called Tenured Generation) is a region of the JVM heap that stores objects which have survived a configurable number of Young Generation garbage collection cycles (controlled by `-XX:MaxTenuringThreshold`). It is typically larger than the Young Generation and is collected far less frequently by a Major GC or Full GC. Fragmentation and promotion failure in the Old Generation are among the most common causes of production pauses.

### 🟢 Simple Definition (Easy)

The Old Generation is the "long-term storage" part of the JVM heap — objects that have proven they stick around for a while get moved here.

### 🔵 Simple Definition (Elaborated)

When a Java object survives several rounds of garbage collection in the Young Generation, the JVM decides it's probably going to be needed for a long time and promotes it to the Old Generation. The Old Generation is bigger because it's designed to hold many more objects. Cleaning it up (Major GC) is much more expensive than cleaning the Young Generation (Minor GC), so the JVM tries to do it as infrequently as possible. When the Old Generation fills up and can't be collected fast enough, you get `OutOfMemoryError: Java heap space`.

### 🔩 First Principles Explanation

**Problem:** Not all objects live equally long. Some are created in a loop and die within milliseconds; others are caches, session objects, or singletons that live for the application's lifetime.

**Constraint:** Collecting the entire heap every time any object becomes garbage is prohibitively expensive. A full scan of a 4 GB heap takes hundreds of milliseconds — during which all application threads may be stopped.

**Insight:** Most objects die young (the "generational hypothesis"). If you segregate objects by age, you can collect the short-lived region (Young Generation) very frequently with minimal work, and rarely touch the long-lived region (Old Generation).

**Solution:** Objects start in Eden. They get collected in Minor GC cycles. Each survivor copy increments the object's age. After reaching `MaxTenuringThreshold` (default: 15), the object is promoted to the Old Generation. Large objects (exceeding `-XX:PretenureSizeThreshold`) bypass Young Generation entirely and are allocated directly in Old.

```
Heap Layout
┌──────────────────────────────────────────┐
│           Young Generation               │
│  ┌────────┬────────────┬───────────────┐ │
│  │  Eden  │ Survivor 0 │  Survivor 1   │ │
│  └────────┴────────────┴───────────────┘ │
│           Old Generation                 │
│  ┌──────────────────────────────────┐    │
│  │    Long-lived promoted objects   │    │
│  └──────────────────────────────────┘    │
│  Metaspace (class metadata)              │
└──────────────────────────────────────────┘
```

The Old Generation is typically 2–3× larger than the Young Generation. It uses mark-sweep-compact algorithms — live objects are marked, dead space is freed, and the remaining live objects are compacted to eliminate fragmentation.

### ❓ Why Does This Exist (Why Before What)

WITHOUT the Old Generation concept:

- Every GC cycle would scan the entire heap, making even small collections slow.
- Short-lived and long-lived objects would compete for the same space.
- Minor GC pauses would scale with total heap size, not just young object count.

What breaks without it:
1. Minor GC pause times grow linearly with heap size — unacceptable for large heaps.
2. You can't tune collection frequency independently for short-lived vs long-lived data.

WITH the Old Generation:
→ Minor GC only scans the small Young Generation (typically 1/4 of heap) — fast pauses.
→ Old Generation collected infrequently because most objects never reach it.
→ Tuning knobs (`-Xmn`, `-XX:NewRatio`) let you control the trade-off per workload.

### 🧠 Mental Model / Analogy

> Imagine a desk (Young Generation) and a filing cabinet (Old Generation). New papers land on the desk, and most get thrown away quickly. Papers you keep using for weeks eventually go into the filing cabinet. Cleaning the desk is fast (5 seconds). Reorganising the whole filing cabinet takes an hour — so you only do it when it's nearly full.

"Papers" = objects, "desk" = Young Generation, "filing cabinet" = Old Generation, "reorganising the cabinet" = Major/Full GC.

The key insight is that the filing cabinet is rarely reorganised precisely because it holds things intentionally kept.

### ⚙️ How It Works (Mechanism)

**Object Promotion Path:**

1. New object allocated in Eden.
2. Eden fills → Minor GC triggered.
3. Surviving objects copied to a Survivor space; age incremented.
4. Objects reaching `MaxTenuringThreshold` (default 15) are promoted to Old Gen.
5. Very large objects (`PretenureSizeThreshold`) go directly to Old Gen.
6. Old Gen fills → Major GC (CMS, G1, ZGC) or Full GC triggered.

**Promotion Failure:** If Minor GC tries to promote an object but Old Gen has no contiguous free space, a Full GC is triggered — often the most painful stop-the-world event.

**Tenuring Threshold Dynamics:** The JVM can adaptively lower `MaxTenuringThreshold` when Survivor spaces overflow, causing premature promotion. This is diagnosed by enabling `-XX:+PrintTenuringDistribution`.

```
Object Age Tracking:
Age 0 (Eden) → Minor GC → Age 1 (S0)
             → Minor GC → Age 2 (S1)
             ...
             → Age 15  → Promoted to Old Gen
```

### 🔄 How It Connects (Mini-Map)

```
Eden → [Minor GC] → Survivor → [Minor GC x N]
                                      ↓
                              Old Generation  ← you are here
                                      ↓
                        [Major GC / Full GC]
                                      ↓
                          Live objects compacted
                          Dead objects reclaimed
```

### 💻 Code Example

Example 1 — Observing promotion with GC logging:

```bash
# Enable GC logging (Java 11+)
java -Xms512m -Xmx512m \
     -XX:+UseG1GC \
     -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     -XX:MaxTenuringThreshold=5 \
     MyApp
```

Example 2 — Detecting Old Gen pressure programmatically:

```java
import java.lang.management.*;
import java.util.List;

public class OldGenMonitor {
    public static void printOldGenUsage() {
        List<MemoryPoolMXBean> pools =
            ManagementFactory.getMemoryPoolMXBeans();
        for (MemoryPoolMXBean pool : pools) {
            // Old Gen names vary: "G1 Old Gen",
            // "Tenured Gen", "PS Old Gen"
            if (pool.getName().toLowerCase()
                    .contains("old")) {
                MemoryUsage usage = pool.getUsage();
                long usedMB = usage.getUsed()
                              / (1024 * 1024);
                long maxMB  = usage.getMax()
                              / (1024 * 1024);
                System.out.printf(
                    "Old Gen: %d MB / %d MB%n",
                    usedMB, maxMB);
            }
        }
    }
}
```

### 🔁 Flow / Lifecycle

```
New Object
    │
    ▼
Eden Space
    │ Eden full
    ▼
Minor GC (stop-the-world)
    │ survived?
    ├── No → garbage collected
    └── Yes → Survivor Space (age++)
                │ age >= MaxTenuringThreshold
                │ OR Survivor overflow
                ▼
          Old Generation
                │ Old Gen full
                ▼
        Major GC / Full GC
                │ survived?
                ├── No → garbage collected
                └── Yes → remains in Old Gen
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Old Gen is always collected by Full GC | Modern collectors (G1, ZGC, Shenandoah) collect Old Gen concurrently without stop-the-world pauses for most phases. |
| Increasing heap size prevents Old Gen pressure | Larger heaps delay Old Gen GC but make each collection longer; tuning `NewRatio` is often more effective. |
| All promoted objects live a long time | Promotion depends on `MaxTenuringThreshold`, not actual lifetime; short-lived objects can be promoted if Minor GC pressure is high. |
| Old Gen fragmentation is unavoidable | Compacting collectors (G1 region evacuation, CMS's foreground compaction) handle fragmentation, though at a cost. |
| `OutOfMemoryError` always means too little heap | It often means too much long-lived data — a memory leak or oversized caches filling Old Gen. |

### 🔥 Pitfalls in Production

**1. Premature Promotion from Survivor Space Overflow**

```bash
# BAD: Default Survivor space too small, causing premature promotion
java -Xmx4g -XX:NewRatio=2 MyApp
# → Eden fills quickly, Survivor overflows, objects promoted early
# → Old Gen grows with short-lived data → frequent Major GCs

# GOOD: Increase Survivor space ratio
java -Xmx4g -XX:NewRatio=2 \
     -XX:SurvivorRatio=6 \
     -XX:+PrintTenuringDistribution \
     MyApp
```

Monitor tenuring distribution and tune `SurvivorRatio` until the histogram shows objects aging naturally before promotion.

**2. Large Object Direct Allocation Bypassing Young Gen**

```java
// BAD: Creating many large objects causes direct Old Gen allocation
// with G1, regions exceeding 50% of region size go to Old Gen
byte[] bigBuffer = new byte[50 * 1024 * 1024]; // 50 MB

// GOOD: Pool and reuse large buffers
// Use ByteBuffer pools or off-heap allocation for large transient data
ByteBuffer buffer = ByteBuffer.allocateDirect(50 * 1024 * 1024);
// or use a pooling library like netty's PooledByteBufAllocator
```

**3. Memory Leak Gradually Filling Old Gen**

```java
// BAD: Static cache without eviction
private static final Map<String, Object> cache =
    new HashMap<>();  // grows unbounded

// GOOD: Use a bounded cache with eviction
private static final Map<String, Object> cache =
    Collections.synchronizedMap(
        new LinkedHashMap<>(1000, 0.75f, true) {
            protected boolean removeEldestEntry(
                    Map.Entry e) {
                return size() > 1000;
            }
        }
    );
// Or use Caffeine/Guava Cache with size limits
```

Symptom: Old Gen usage climbs monotonically on a heap dump graph without ever declining.

### 🔗 Related Keywords

- `Young Generation` — the short-lived sibling region where all objects start.
- `Minor GC` — the collection that triggers promotion from Young to Old Gen.
- `Major GC` — collection targeting primarily the Old Generation.
- `Full GC` — collects both Young and Old Generation in one stop-the-world pause.
- `G1GC` — divides heap into regions, mixing Young and Old collection concurrently.
- `Promotion Failure` — when Old Gen can't accept promoted objects, forcing a Full GC.
- `MaxTenuringThreshold` — JVM flag controlling how many GC cycles before promotion.
- `GC Tuning` — the practice of sizing generations and choosing collectors for workload.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Heap region for long-lived objects that   │
│              │ survived multiple Minor GC cycles.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding GC pauses, tuning           │
│              │ heap ratios, diagnosing memory leaks.     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Routing all large transient data here —  │
│              │ use object pooling or off-heap instead.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Old Gen fills slowly but cleans          │
│              │ painfully — keep it lean."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Major GC → G1GC → ZGC → GC Tuning        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your application runs a batch job every night that processes 10 million records, creating temporary objects for each. After batch completion, heap usage never drops back to baseline — it stays 30% higher than before the batch. No `OutOfMemoryError` yet. What is likely filling the Old Generation, and what would you check first in a heap dump?

**Q2.** You have a service with `-Xmx8g` and `-XX:NewRatio=2` (2 GB Young, 6 GB Old). Minor GC pauses are under 50ms but you're seeing 2-second Full GC pauses every 10 minutes. What does this pattern suggest about the relationship between object promotion rate and Old Generation sizing, and how would you approach rebalancing?

