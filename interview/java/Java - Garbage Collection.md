---
layout: default
title: "Java - Garbage Collection"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 8
permalink: /interview/java/garbage-collection/
topic: Java
subtopic: Garbage Collection
keywords:
  - GC Algorithms
  - G1 Garbage Collector
  - ZGC
  - GC Tuning
difficulty_range: mixed
status: in-progress
version: 2
---

# GC Algorithms

**TL;DR** - Garbage collection algorithms automatically reclaim unused heap memory by identifying and collecting objects that are no longer reachable, using strategies ranging from simple mark-sweep to generational and concurrent approaches, each with different throughput/latency trade-offs.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
In C/C++, developers manually allocate and free memory. Forgetting `free()` causes memory leaks. Calling `free()` too early causes use-after-free bugs (security vulnerabilities). Calling `free()` twice causes crashes. Memory management consumes 30-40% of C/C++ development time and is the #1 source of security vulnerabilities.

**THE BREAKING POINT:**
A C server leaks 50KB per request. After 100K requests, it crashes with out-of-memory. The leak takes weeks to find - it's a deep nesting of structs where one pointer isn't freed on the error path.

**THE INVENTION MOMENT:**
"This is exactly why garbage collection was created."

**EVOLUTION:**
Manual memory management (C/C++) -> reference counting (COM, Objective-C, Python) -> tracing GC with mark-sweep (Lisp, Java) -> generational hypothesis (Java 1.2+) -> concurrent collectors (CMS, G1, ZGC, Shenandoah).

---

### Textbook Definition

Garbage collection (GC) is the automatic process of identifying objects in the heap that are no longer reachable from GC roots (thread stacks, static fields, JNI references) and reclaiming their memory. The fundamental algorithm is mark-sweep: (1) mark all reachable objects by traversing from roots, (2) sweep unmarked objects. Modern collectors add compaction (defragmentation), generational partitioning (young/old), and concurrent operation (collect while application runs).

---

### Understand It in 30 Seconds

**One line:**
GC automatically finds and removes unused objects from memory so developers never have to manually free memory.

**One analogy:**

> GC is like a city waste management system. Mark phase: inspectors walk every road starting from city hall (GC roots), marking all buildings (objects) they can reach. Sweep phase: any unmarked building is demolished and the land reclaimed. Compact phase: remaining buildings are moved together to eliminate gaps.

**One insight:**
The generational hypothesis is the key insight behind modern GC: "most objects die young." In a typical Java application, 95% of objects become garbage within milliseconds of creation (temporary strings, iterators, boxed primitives). By collecting the young generation frequently and the old generation rarely, GC optimizes for the common case.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. An object is garbage if and only if it is unreachable from any GC root
2. GC must never collect a reachable object (safety)
3. GC should eventually collect all unreachable objects (completeness)
4. GC must handle cycles (unlike reference counting)

**DERIVED DESIGN:**
Because most objects die young (generational hypothesis), the heap is divided into Young Generation (Eden + Survivor spaces) and Old Generation. Minor GC collects young gen frequently (fast, most objects are dead). Major/Full GC collects everything (slow, infrequent).

**THE TRADE-OFFS:**
**Throughput vs Latency:** High throughput (Parallel GC) means longer pauses. Low latency (ZGC) means lower throughput.
**Memory vs Speed:** More heap means less frequent GC but longer pauses when it runs.

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you create objects in Java, you never have to delete them. The garbage collector watches for objects nobody is using anymore and automatically removes them to free up memory.

**Level 2 - How to use it (junior developer):**

You don't call GC directly. You choose a collector and set heap sizes:

```
# Choose collector
java -XX:+UseG1GC -jar app.jar
java -XX:+UseZGC -jar app.jar

# Set heap sizes
java -Xms512m -Xmx4g -jar app.jar

# Enable GC logging
java -Xlog:gc*:file=gc.log -jar app.jar
```

Key rule: Don't call `System.gc()`. It's a hint, not a command, and can cause full-heap stop-the-world pauses.

**Level 3 - How it works (mid-level engineer):**

**Generational GC:**

```
+-- Young Generation --------+-- Old Gen --+
| Eden | S0 | S1 |           |             |
|      |    |    |           |             |
| new  | survivors           | long-lived  |
| objects   (age tracking)   | objects     |
+----------------------------+-------------+

Minor GC flow:
1. Eden fills up
2. Copy live objects from Eden to S0
3. Objects surviving N minor GCs -> Old Gen
4. Clear Eden (very fast - most objects dead)

Major GC: collect Old Gen (slower, less frequent)
```

**Algorithm comparison:**

| Algorithm             | How it works                                   | Pause      | Throughput         |
| --------------------- | ---------------------------------------------- | ---------- | ------------------ |
| Mark-Sweep            | Mark reachable, sweep dead                     | Long STW   | Good               |
| Mark-Compact          | Mark, then compact to eliminate fragmentation  | Long STW   | Good               |
| Copying               | Copy live objects to new space, free old space | Medium STW | Good for young gen |
| Concurrent Mark-Sweep | Mark concurrently, sweep during STW            | Short STW  | Lower              |

**Level 4 - Mastery (senior/staff+ engineer):**

**GC roots (where tracing begins):**

- Thread stack frames (local variables, parameters)
- Static fields of loaded classes
- JNI global references
- Synchronization monitors
- Internal JVM references (class loaders, etc.)

**Safe points:** The JVM can only start GC when all threads are at a safe point - a location in code where the JVM knows the exact state of every reference. The JIT compiler inserts safe point checks in:

- Method returns
- Loop back-edges
- Deoptimization points

A long-running counted loop without a safe point check (e.g., `for (int i = 0; i < 1000000000; i++)`) can delay GC because that thread can't reach a safe point. This is called "time to safe point" (TTSP) and can cause unexpected latency spikes.

**Card table and remembered sets:** Old gen objects can reference young gen objects. To avoid scanning the entire old gen during minor GC, the JVM uses a card table: a byte array where each byte represents a 512-byte region of old gen. When an old gen object's reference field is modified, the corresponding card is marked "dirty." Minor GC only scans dirty cards.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

```
  GC Roots
  (thread stacks, static fields)
      |
  Mark Phase: trace all reachable objects
      |
  +--[A]-->[B]-->[C]     [D]-->[E]
  |              |
  +--[F]         [G]     [H]
      |
  A,B,C,F,G: MARKED (reachable)
  D,E,H: NOT marked (garbage)
      |
  Sweep Phase: reclaim D, E, H
      |
  Compact Phase (optional):
  move A,B,C,F,G together
  to eliminate memory gaps
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**Monitoring GC programmatically:**

```java
// Get GC info via JMX
for (GarbageCollectorMXBean gc :
        ManagementFactory
        .getGarbageCollectorMXBeans()) {
    System.out.printf("GC: %s, Count: %d, "
        + "Time: %dms%n",
        gc.getName(),
        gc.getCollectionCount(),
        gc.getCollectionTime());
}

// Listen for GC events
for (GarbageCollectorMXBean gc :
        ManagementFactory
        .getGarbageCollectorMXBeans()) {
    NotificationEmitter emitter =
        (NotificationEmitter) gc;
    emitter.addNotificationListener(
        (notification, handback) -> {
            GcInfo info =
                ((GarbageCollectionNotification
                    Info) notification
                    .getUserData()).getGcInfo();
            System.out.printf(
                "GC pause: %dms%n",
                info.getDuration());
        }, null, null);
}
```

**BAD - Forcing GC (don't do this):**

```java
// Never do this in production
System.gc(); // hint, not command
// Can trigger full STW pause
// JVM may ignore it entirely
```

**GOOD - Reduce GC pressure by design:**

```java
// Reuse objects instead of creating new ones
// BAD: creates garbage in hot loop
for (int i = 0; i < 1000000; i++) {
    String key = "prefix_" + i;
    map.put(key, compute(i));
}

// GOOD: StringBuilder reuse
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000000; i++) {
    sb.setLength(0);
    sb.append("prefix_").append(i);
    map.put(sb.toString(), compute(i));
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. GC traces from roots, marks reachable objects, sweeps/compacts the rest
2. Generational hypothesis: most objects die young -> collect young gen frequently, old gen rarely
3. Throughput vs latency trade-off defines collector choice

**Interview one-liner:**
"Garbage collection traces reachable objects from GC roots, reclaims unreachable memory, and uses generational partitioning because most objects die young, with different collectors optimizing for throughput or latency."

---

### The Surprising Truth

Garbage collection can be FASTER than manual memory management. In a generational collector, allocating an object is just bumping a pointer (O(1)). In C's `malloc()`, finding a suitable free block requires searching a free list (O(n) worst case). And minor GC copies only live objects (typically 5% of young gen) - the 95% garbage costs zero to "free." The per-object cost of GC is often lower than the per-object cost of `malloc`/`free`.

---

### Interview Deep-Dive

**Q1: Explain the generational hypothesis and why it matters for GC design.**

_Why they ask:_ Tests understanding of the foundational principle behind modern GC.

_Strong answer:_

The generational hypothesis states: "Most objects die young." Empirical studies across many applications show that 90-98% of objects become garbage almost immediately after creation. Examples:

- Iterator objects: created per loop, discarded after
- String concatenation intermediates: temporary, discarded
- Lambda capture objects: short-lived
- Method parameter boxing: `Integer.valueOf(42)` in generics

This matters because:

1. **Young gen can use copying collector:** Copy the 5% survivors, implicitly free the 95% dead. Cost proportional to survivors, not garbage.
2. **Old gen collected rarely:** Objects that survive multiple young GCs are likely long-lived (caches, connection pools, singletons).
3. **Allocation is fast:** Young gen allocation is pointer bumping - as fast as stack allocation.

If the hypothesis doesn't hold (e.g., a cache that creates many long-lived objects), generational GC performs poorly - objects are repeatedly copied through survivor spaces before tenuring.

---

**Q2: What are the available garbage collectors in modern Java and when would you choose each?**

_Why they ask:_ Tests practical knowledge of GC selection.

_Strong answer:_

| Collector  | Java             | Pause target  | Best for                         |
| ---------- | ---------------- | ------------- | -------------------------------- |
| Serial     | All              | Seconds       | Small heaps (<100MB), single CPU |
| Parallel   | All              | Seconds       | Batch processing, max throughput |
| G1         | 9+ default       | 200ms default | General purpose, balanced        |
| ZGC        | 15+              | <1ms          | Large heaps, low latency         |
| Shenandoah | 12+ (non-Oracle) | <10ms         | Low latency, any heap size       |

**Decision matrix:**

- **Batch/analytics job:** Parallel GC (maximize throughput, pauses don't matter)
- **Web application (<4GB heap):** G1 GC (good balance, default choice)
- **Low-latency service (>4GB heap):** ZGC (sub-millisecond pauses)
- **Microservice (<256MB heap):** Serial GC (lowest overhead for tiny heaps)

```
java -XX:+UseG1GC -XX:MaxGCPauseMillis=200
java -XX:+UseZGC
java -XX:+UseParallelGC
java -XX:+UseSerialGC
```

---

**Q3: What is a stop-the-world pause and why can't it be completely eliminated?**

_Why they ask:_ Tests understanding of fundamental GC constraints.

_Strong answer:_

A stop-the-world (STW) pause halts all application threads so the GC can safely examine and modify the object graph. During STW, no application code runs.

**Why it's necessary:**
During GC, the collector must have a consistent view of the object graph. If application threads modify references while the GC is marking, the GC might:

- Miss a reachable object (collect something still in use - catastrophic)
- Retain garbage (safe but wasteful)

**Can it be eliminated?**
Not entirely, but it can be minimized:

- **ZGC:** Concurrent marking with colored pointers and load barriers. STW is only for root scanning (~1ms regardless of heap size)
- **Shenandoah:** Concurrent compaction with Brooks pointers. STW only for init-mark and final-mark (~1ms)

The remaining STW phases (root scanning) cannot be fully eliminated because you need a consistent snapshot of thread stacks at a safe point. Some experimental collectors use checkpoint-based approaches to reduce even this, but all production collectors have some minimal STW.

The key insight: it's not about eliminating pauses but making them O(1) with respect to heap size. ZGC achieves <1ms pauses whether the heap is 1GB or 16TB.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for GC Algorithms. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# G1 Garbage Collector

**TL;DR** - G1 (Garbage First) is Java's default garbage collector since Java 9, dividing the heap into regions and prioritizing collection of regions with the most garbage, achieving predictable pause times with good throughput.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Before G1, you had two choices: Parallel GC (high throughput but long pauses proportional to heap size) or CMS (low pauses but fragmentation over time, leading to catastrophic full GC pauses). Neither could guarantee predictable pause times.

**THE BREAKING POINT:**
A CMS-collected application runs smoothly for hours, then hits a fragmentation-induced full GC that stops the world for 30 seconds. The load balancer marks the server as dead. On restart, the same pattern repeats.

**THE INVENTION MOMENT:**
"This is exactly why G1 was created."

**EVOLUTION:**
Mark-Sweep-Compact -> Parallel GC (throughput-first) -> CMS (low-pause attempt, fragmentation) -> G1 (region-based, predictable pauses, Java 9 default) -> ZGC/Shenandoah (sub-ms pauses).

---

### Textbook Definition

G1 (Garbage First) is a region-based, generational, concurrent garbage collector. It divides the heap into equal-sized regions (1-32MB each) that can be Eden, Survivor, Old, or Humongous. G1 tracks the amount of garbage per region and collects the regions with the most garbage first (hence "Garbage First"), optimizing for a user-specified maximum pause time target.

---

### Understand It in 30 Seconds

**One line:**
G1 divides the heap into regions, collects the most garbage-filled regions first, and targets a specific maximum pause time.

**One analogy:**

> Traditional GC is like cleaning your entire house every time. G1 is like a smart cleaning robot that scans all rooms, identifies the messiest ones, and cleans only those rooms within your 15-minute budget. It always starts with the dirtiest room to maximize what it cleans per minute.

**One insight:**
G1's key innovation is the pause time target (`-XX:MaxGCPauseMillis=200`). Instead of collecting everything (unpredictable pause), G1 selects just enough regions to fit within the target pause time. If 200ms allows collecting 50 regions, it picks the 50 with the most garbage. This makes pause times proportional to the target, not the heap size.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
G1 is Java's default garbage collector. It breaks memory into small chunks and always cleans the chunks with the most garbage first, staying within a time budget you specify.

**Level 2 - How to use it (junior developer):**

```
# G1 is default since Java 9
java -Xmx4g -jar app.jar

# Explicit with pause target
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -Xmx4g -jar app.jar

# Enable GC logging
java -Xlog:gc*:file=gc.log:time,uptime,level \
     -jar app.jar
```

**Level 3 - How it works (mid-level engineer):**

**Heap layout:**

```
+---+---+---+---+---+---+---+---+
| E | E | S | O | O | H | H | O |
+---+---+---+---+---+---+---+---+
| E |   | O | O |   | O | S | E |
+---+---+---+---+---+---+---+---+

E = Eden    S = Survivor  O = Old
H = Humongous (>50% region size)
Empty = Free region
```

**GC phases:**

1. **Young GC (STW):** Collect all Eden and Survivor regions. Copy survivors to new Survivor regions or promote to Old. Pause proportional to survivor count.

2. **Concurrent marking:** Runs while application executes. Marks live objects in Old regions. Calculates garbage ratio per region.

3. **Mixed GC (STW):** Collect Young regions PLUS selected Old regions (the ones with most garbage). This is the "Garbage First" selection.

4. **Full GC (STW, emergency):** If concurrent marking can't keep up, falls back to single-threaded full GC. This is what you want to avoid.

**Level 4 - Mastery (senior/staff+ engineer):**

**Remembered Sets (RSet):** Each region maintains a set of references from other regions pointing into it. This allows G1 to collect a region without scanning the entire heap - only scan the RSet to find external references. RSets consume 5-20% of heap space (a significant overhead).

**SATB (Snapshot-At-The-Beginning):** G1 uses SATB for concurrent marking. At the start of marking, G1 takes a logical "snapshot" of the live object graph. Any reference modification during concurrent marking is tracked via write barriers. This ensures the GC never misses a live object (safety) at the cost of potentially retaining some floating garbage until the next cycle.

**Humongous objects:** Objects larger than 50% of a region are allocated directly in Old gen as "humongous" objects spanning multiple contiguous regions. These are expensive to collect and can cause fragmentation. Avoid creating large arrays or byte buffers on the heap for short-lived operations.

**Tuning guidance:**

- Start with `-XX:MaxGCPauseMillis=200` (default)
- If too many mixed GCs: increase `-XX:InitiatingHeapOccupancyPercent` (default 45%)
- If full GCs occur: lower IHOP to start concurrent marking earlier
- Increase heap rather than fine-tuning collector parameters


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**Analyzing G1 GC logs:**

```
# Enable detailed G1 logging
java -Xlog:gc*:file=gc.log:time,level \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -Xmx4g -jar app.jar

# Key log entries to look for:
# [gc,start] GC(42) Pause Young
#   (Normal) 3072M->1024M(4096M) 15.3ms
# [gc,start] GC(43) Pause Young
#   (Mixed) 2048M->512M(4096M) 45.2ms
# [gc,start] GC(44) Pause Full
#   (System.gc()) 2048M->256M(4096M) 2345ms
#                                     ^^^^
#                            AVOID THIS
```

**Monitoring in code:**

```java
// Check if G1 is active
for (GarbageCollectorMXBean gc :
        ManagementFactory
        .getGarbageCollectorMXBeans()) {
    if (gc.getName().contains("G1")) {
        System.out.printf(
            "%s: %d collections, %dms total%n",
            gc.getName(),
            gc.getCollectionCount(),
            gc.getCollectionTime());
    }
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. G1 divides heap into regions and collects the most garbage-filled regions first
2. `-XX:MaxGCPauseMillis=200` sets the pause time target (G1 adapts to meet it)
3. Young GC + concurrent marking + mixed GC = normal operation; full GC = emergency

**Interview one-liner:**
"G1 partitions the heap into regions, tracks garbage per region, and during mixed GC selects the most garbage-dense regions to collect within a configurable pause time target, making pauses predictable rather than proportional to heap size."

---

### The Surprising Truth

G1's region-based design means increasing heap size can actually DECREASE pause times. In traditional collectors, more heap = more to scan = longer pauses. In G1, more heap = more regions = G1 can be more selective, choosing only the most garbage-dense regions to meet its pause target. This breaks the conventional wisdom that "bigger heap = bigger pauses."

---

### Interview Deep-Dive

**Q1: Walk through what happens during a G1 GC cycle.**

_Why they ask:_ Tests understanding of G1's multi-phase operation.

_Strong answer:_

**Phase 1: Young GC (STW, ~10-50ms)**

- Triggered when Eden regions fill up
- Copies live objects from Eden -> Survivor or Old
- All Eden regions reclaimed (most objects are dead)
- Adjusts Eden size to meet pause target

**Phase 2: Concurrent Marking (mostly concurrent)**

- Triggered when heap occupancy exceeds IHOP (default 45%)
- Initial mark (STW, piggybacks on young GC): mark objects directly referenced from roots
- Root region scanning (concurrent): scan survivor regions for references to old gen
- Concurrent mark (concurrent): trace all live objects from marked roots
- Remark (STW): process SATB buffers, finalize marking
- Cleanup (partly STW): count live objects per region, sort by garbage density, free empty regions

**Phase 3: Mixed GC (STW, ~50-200ms)**

- Collects young regions + selected old regions with most garbage
- G1 selects N old regions that can be collected within pause target
- Multiple mixed GC cycles may run before all eligible old regions are collected

**Emergency: Full GC (STW, seconds)**

- Triggered when mixed GC can't reclaim fast enough
- Single-threaded mark-sweep-compact of entire heap
- Indicates tuning is needed (lower IHOP, more heap, or less allocation pressure)

---

**Q2: How would you diagnose and fix G1 GC performance problems?**

_Why they ask:_ Tests practical tuning and debugging skills.

_Strong answer:_

**Symptom 1: Frequent young GCs**

- Cause: High allocation rate, small Eden
- Diagnostic: `jstat -gcutil <pid> 1s` - check YGC frequency
- Fix: Increase heap or reduce allocation rate (object pooling for hot paths)

**Symptom 2: Long mixed GC pauses**

- Cause: Too many old regions selected per cycle
- Diagnostic: GC log shows mixed GC exceeding target
- Fix: Lower `-XX:G1MixedGCCountTarget` (spread across more cycles)

**Symptom 3: Full GC occurring**

- Cause: Concurrent marking starts too late, can't keep up with promotion rate
- Diagnostic: GC log shows "Pause Full" events
- Fix: Lower `-XX:InitiatingHeapOccupancyPercent` (start marking earlier)

**Symptom 4: Humongous allocation**

- Cause: Objects > 50% region size (large byte arrays, strings)
- Diagnostic: GC log shows "Humongous" allocation
- Fix: Increase region size (`-XX:G1HeapRegionSize`), reduce object size, use off-heap buffers

**General approach:**

1. Enable GC logging: `-Xlog:gc*:file=gc.log`
2. Analyze with GCViewer or GCEasy
3. Check pause time distribution, throughput percentage
4. Adjust one parameter at a time, measure impact

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for G1 Garbage Collector. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# ZGC

**TL;DR** - ZGC (Z Garbage Collector) is a scalable, low-latency garbage collector that keeps pause times under 1 millisecond regardless of heap size, from megabytes to multi-terabytes.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
G1 GC targets 200ms pauses but can spike higher under heavy allocation. For latency-sensitive applications (trading platforms, real-time bidding, interactive gaming), even 50ms pauses are unacceptable. Large heaps (>32GB) amplify the problem.

**THE BREAKING POINT:**
An ad-bidding platform must respond within 10ms. A 100ms G1 GC pause means missed auctions, lost revenue. The team considers C++ for the hot path, losing Java's productivity.

**THE INVENTION MOMENT:**
"This is exactly why ZGC was created."

**EVOLUTION:**
G1 (200ms target) -> Shenandoah (concurrent compaction, <10ms) -> ZGC (concurrent everything, <1ms). ZGC became production-ready in Java 15.

---

### Textbook Definition

ZGC is a concurrent, region-based, compacting garbage collector designed for sub-millisecond pause times. It performs almost all GC work concurrently with the application, using colored pointers (metadata embedded in object references) and load barriers (checks when loading a reference) to achieve pauseless operation. ZGC pause times are independent of heap size, live set size, and root set size.

---

### Understand It in 30 Seconds

**One line:**
ZGC achieves <1ms GC pauses at any heap size by doing all heavy work concurrently with your application.

**One analogy:**

> G1 is like a restaurant that closes for 10 minutes each hour for cleaning. ZGC is like a restaurant that never closes - cleaners work alongside diners, unobtrusively moving furniture and cleaning while guests continue eating.

**One insight:**
ZGC's breakthrough is colored pointers. Every object reference in the heap carries metadata bits that tell the GC the state of the referenced object (marked, relocated, remapped). Load barriers check these bits on every pointer load and fix up references as needed. This eliminates the need for stop-the-world phases during marking and compaction.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ZGC is a garbage collector designed for applications that cannot tolerate pauses. It keeps pauses under 1 millisecond whether your application uses 1GB or 1TB of memory.

**Level 2 - How to use it (junior developer):**

```
# Enable ZGC
java -XX:+UseZGC -Xmx16g -jar app.jar

# Generational ZGC (Java 21+, recommended)
java -XX:+UseZGC -XX:+ZGenerational \
     -Xmx16g -jar app.jar

# ZGC with monitoring
java -XX:+UseZGC \
     -Xlog:gc*:file=gc.log:time \
     -Xmx16g -jar app.jar
```

**Level 3 - How it works (mid-level engineer):**

**Colored pointers:**
ZGC uses 64-bit pointers with metadata in the upper bits:

```
  63    46  45  44  43  42  41    0
  +------+---+---+---+---+-------+
  |unused|rem|mk1|mk0|fin| addr  |
  +------+---+---+---+---+-------+
         ^-- color bits     ^-- object address (42 bits = 4TB)
```

- `marked0/marked1`: alternating mark bits per GC cycle
- `remapped`: reference has been updated after relocation
- `finalizable`: object needs finalization

**Load barrier:** When application code loads a reference, the JIT-inserted barrier checks the color bits. If the reference is "bad" (stale), the barrier fixes it in-place:

```
// Pseudocode: load barrier
Object ref = field.load();
if (ref.color != goodColor) {
    ref = zgc_relocate_and_remap(ref);
    field.store(ref); // fix in place
}
// Application sees correct reference
```

**Level 4 - Mastery (senior/staff+ engineer):**

**ZGC phases (all concurrent except brief STW):**

1. **Pause Mark Start (STW, ~1ms):** Scan thread stacks for GC roots. Set the "good color" for this cycle.

2. **Concurrent Mark:** Traverse object graph from roots. Application continues. Load barriers handle references to unmarked objects.

3. **Pause Mark End (STW, ~1ms):** Process remaining SATB buffers. Finalize the live object set.

4. **Concurrent Process Non-Strong References:** Handle soft/weak/phantom references.

5. **Concurrent Relocate Set Selection:** Identify regions to compact (most garbage).

6. **Pause Relocate Start (STW, ~1ms):** Scan roots again for relocation.

7. **Concurrent Relocate:** Move live objects from selected regions to new regions. Load barriers redirect any access to the old location to the new location.

8. **Concurrent Remap:** Update all references to relocated objects. (Merged with next marking cycle for efficiency.)

**Generational ZGC (Java 21):**
Adds the generational hypothesis to ZGC. Young objects are collected more frequently, reducing overall GC work. Recommended for all ZGC deployments on Java 21+.

**When NOT to use ZGC:**

- Small heaps (<256MB): ZGC overhead not worth it
- Maximum throughput needed: Parallel GC has higher throughput
- Java < 15: ZGC is experimental/not available
- CPU-constrained: ZGC uses more CPU for concurrent work


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**Comparing G1 vs ZGC behavior:**

```
# G1: pause scales with heap and live set
java -XX:+UseG1GC -Xmx32g -jar app.jar
# GC log: Pause Young 45ms, Mixed 120ms

# ZGC: pause is constant regardless of heap
java -XX:+UseZGC -Xmx32g -jar app.jar
# GC log: Pause Mark Start 0.5ms
#         Pause Mark End 0.3ms
#         Pause Relocate Start 0.2ms
# Total STW: ~1ms (same at 32GB or 1TB)
```

**Monitoring ZGC:**

```java
// Programmatic check
String gcName = ManagementFactory
    .getGarbageCollectorMXBeans()
    .stream()
    .map(GarbageCollectorMXBean::getName)
    .filter(n -> n.contains("ZGC"))
    .findFirst()
    .orElse("Not ZGC");
System.out.println("GC: " + gcName);
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. ZGC achieves <1ms pauses at any heap size using colored pointers and load barriers
2. Almost all GC work is concurrent - only root scanning requires brief STW
3. Use generational ZGC (`-XX:+ZGenerational`) on Java 21+ for best performance

**Interview one-liner:**
"ZGC uses colored pointers with metadata in reference bits and load barriers to perform marking, compaction, and reference updates concurrently, achieving sub-millisecond pauses independent of heap size."

---

### The Surprising Truth

ZGC can handle heaps up to 16 terabytes with the same sub-millisecond pause times as a 1GB heap. The pause time is determined only by the number of GC roots (thread stacks and static fields), not by the heap size or the number of live objects. This means ZGC's pause time is O(roots), not O(heap) or O(live_set).

---

### Interview Deep-Dive

**Q1: How do colored pointers and load barriers work together in ZGC?**

_Why they ask:_ Tests understanding of ZGC's core innovation.

_Strong answer:_

**Colored pointers** embed GC metadata in the unused high bits of 64-bit pointers. Each reference carries its own GC state:

- Which marking cycle it belongs to
- Whether it has been relocated
- Whether it needs finalization

**Load barriers** are checks inserted by the JIT compiler at every reference load. When application code loads a reference:

1. Check the color bits against the "good color" for the current phase
2. If good: use the reference directly (fast path, most common)
3. If bad: the reference is stale. Execute the slow path:
   - If during marking: mark the object and fix the color
   - If during relocation: look up the forwarding table, redirect to new location, fix the reference in place

```
// Application code:
Object obj = array[i];

// What JIT generates:
Object obj = array[i];
if (obj.colorBits != currentGoodColor) {
    obj = slowPath_fixReference(obj);
    array[i] = obj; // self-healing
}
```

The self-healing property is key: once a bad reference is fixed, it's good for all future accesses. This means the barrier overhead decreases over time as references are healed.

---

**Q2: When would you choose ZGC over G1? What are the trade-offs?**

_Why they ask:_ Tests practical decision-making.

_Strong answer:_

| Factor               | G1               | ZGC                      |
| -------------------- | ---------------- | ------------------------ |
| Pause times          | 10-200ms typical | <1ms guaranteed          |
| Throughput           | Higher (~95%)    | Lower (~90-93%)          |
| Memory overhead      | ~10-20%          | ~15-25%                  |
| Heap size sweet spot | 4-32GB           | 8GB-16TB                 |
| CPU overhead         | Lower            | Higher (barriers)        |
| Maturity             | Very mature      | Production since Java 15 |

**Choose ZGC when:**

- Latency SLAs: p99 < 10ms response time
- Large heaps: >32GB where G1 pauses become noticeable
- Real-time applications: trading, gaming, ad bidding
- User-facing services where GC pauses = user-visible lag

**Stick with G1 when:**

- Throughput is priority (batch processing, analytics)
- Small heaps (<4GB): G1 overhead is lower
- CPU is constrained: ZGC barriers consume more CPU
- Running Java < 15

**Compromise:** Use Generational ZGC (Java 21+) which improves throughput over classic ZGC while maintaining sub-ms pauses.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ZGC. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# GC Tuning

**TL;DR** - GC tuning is the process of configuring garbage collection parameters to optimize for your application's specific throughput and latency requirements, starting with the right collector choice and heap sizing.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Default GC settings are designed for general-purpose workloads. A high-throughput batch processor with defaults may spend too much time in GC. A low-latency service with defaults may have unacceptable pause spikes. Without tuning, you leave performance on the table.

**THE BREAKING POINT:**
A REST API server with 4GB heap and default G1 settings has p99 latency spikes of 500ms. Users see intermittent slowness. The team suspects network issues for weeks before realizing it's GC pauses during mixed collection.

**THE INVENTION MOMENT:**
"This is exactly why GC tuning was created."

**EVOLUTION:**
Manual tuning of 100+ flags (pre-Java 9) -> ergonomic defaults (JVM auto-tunes based on machine) -> simpler tuning (fewer flags needed with G1/ZGC) -> near-zero tuning with ZGC.

---

### Textbook Definition

GC tuning is the systematic process of selecting the appropriate garbage collector, sizing the heap and generations, and adjusting collector-specific parameters to meet application performance requirements. Modern tuning follows the principle: choose the right collector, size the heap correctly, and avoid over-tuning.

---

### Understand It in 30 Seconds

**One line:**
GC tuning = right collector + right heap size + don't over-tune.

**One analogy:**

> GC tuning is like adjusting a car's suspension. You pick the right vehicle type first (sports car = low latency, truck = high throughput). Then you adjust spring stiffness (heap size) and damping (pause target). Over-tuning makes the ride worse - a few key adjustments are better than tweaking every bolt.

**One insight:**
The #1 GC tuning mistake is over-tuning. Modern collectors (G1, ZGC) are designed to auto-adapt. Setting 20 flags usually makes things worse because the ergonomics can no longer adapt. Start with collector choice + heap size + pause target, and only add flags if measurement shows a specific problem.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
GC tuning means telling Java how much memory to use and how to clean it up, so your application runs smoothly without pauses.

**Level 2 - How to use it (junior developer):**

**Step 1: Choose collector based on requirement**

```
# Throughput first (batch jobs)
java -XX:+UseParallelGC

# Balanced (web apps, default)
java -XX:+UseG1GC

# Low latency (real-time)
java -XX:+UseZGC
```

**Step 2: Size the heap**

```
# Rule of thumb: 3-4x live data set size
# If your app needs 1GB for live objects:
java -Xms4g -Xmx4g  # min = max avoids resize
```

**Step 3: Set pause target (G1 only)**

```
java -XX:MaxGCPauseMillis=100  # 100ms target
```

**Step 4: Enable GC logging always**

```
java -Xlog:gc*:file=gc.log:time,uptime,level
```

**Level 3 - How it works (mid-level engineer):**

**Key metrics to measure:**

| Metric            | Target                   | Tool            |
| ----------------- | ------------------------ | --------------- |
| GC throughput     | >95% of time in app code | GC log analysis |
| Avg pause time    | <200ms (G1), <1ms (ZGC)  | GC log          |
| Max pause time    | <500ms (G1), <10ms (ZGC) | GC log          |
| Allocation rate   | Depends on app           | `jstat -gc`     |
| Promotion rate    | Should be low            | GC log          |
| Full GC frequency | Zero in steady state     | GC log          |

**Common tuning scenarios:**

1. **High allocation rate, frequent young GC:**
   - Increase young gen: `-XX:NewRatio=2` or `-XX:G1NewSizePercent=30`
   - Or increase total heap

2. **Objects promoted too quickly:**
   - Increase tenuring threshold: `-XX:MaxTenuringThreshold=15`
   - Increase survivor space

3. **Full GC occurring:**
   - Start concurrent marking earlier: `-XX:InitiatingHeapOccupancyPercent=35` (default 45)
   - Increase heap

4. **Long mixed GC pauses (G1):**
   - Reduce `-XX:G1MixedGCCountTarget` to spread work
   - Lower `-XX:MaxGCPauseMillis`

**Level 4 - Mastery (senior/staff+ engineer):**

**The tuning methodology:**

1. **Measure baseline:** Enable GC logging, run under production-like load
2. **Identify the constraint:** Is it throughput, latency, or memory?
3. **Make ONE change:** Never tune multiple parameters simultaneously
4. **Measure impact:** Same load, compare metrics
5. **Iterate or stop:** If target met, stop tuning

**Anti-patterns:**

- Setting `-Xms != -Xmx`: Forces heap resizing during warmup
- Setting `-XX:+DisableExplicitGC`: Hides the real problem
- Copying flags from Stack Overflow without understanding
- Tuning for micro-benchmarks instead of production load profiles
- Over-tuning: more flags = less adaptability

**Modern recommendation (Java 17+):**

```
# Most applications need only these
java -XX:+UseG1GC \
     -Xms4g -Xmx4g \
     -XX:MaxGCPauseMillis=200 \
     -Xlog:gc*:file=gc.log:time \
     -jar app.jar

# Or just use ZGC for latency-sensitive
java -XX:+UseZGC -XX:+ZGenerational \
     -Xms4g -Xmx4g \
     -jar app.jar
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**GC tuning investigation script:**

```bash
# Step 1: Check current GC configuration
jcmd <pid> VM.flags | grep -i gc

# Step 2: Monitor GC in real-time
jstat -gcutil <pid> 1000
# S0  S1    E     O     M    CCS  YGC YGCT
# 0   50.0  67.3  45.2  97.1 95.0 42  1.2
#                  ^^^^
# Old gen filling = mixed GC coming

# Step 3: Analyze GC log
# Tool: GCViewer, GCEasy, or gceasy.io
# Look for:
# - Pause time distribution
# - Throughput percentage
# - Allocation rate
# - Full GC events
```

**Application-level GC monitoring:**

```java
// Log GC pauses > threshold
long threshold = 100; // ms
for (GarbageCollectorMXBean gc :
        ManagementFactory
        .getGarbageCollectorMXBeans()) {
    NotificationEmitter emitter =
        (NotificationEmitter) gc;
    emitter.addNotificationListener(
        (notif, data) -> {
            GarbageCollectionNotificationInfo
                info = GarbageCollection
                    NotificationInfo.from(
                        (CompositeData)
                        notif.getUserData());
            long duration =
                info.getGcInfo().getDuration();
            if (duration > threshold) {
                log.warn("Long GC: {}ms, "
                    + "cause: {}, action: {}",
                    duration,
                    info.getGcCause(),
                    info.getGcAction());
            }
        }, null, null);
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Choose collector first: Parallel (throughput), G1 (balanced), ZGC (latency)
2. Size heap to 3-4x live data set, set `-Xms = -Xmx`
3. Always enable GC logging, never tune without measurement

**Interview one-liner:**
"GC tuning starts with choosing the right collector for your throughput/latency trade-off, sizing the heap to 3-4x live data, and making measured, incremental changes with GC logging always enabled."

---

### The Surprising Truth

The most effective GC tuning is often not changing GC flags at all - it's reducing allocation rate in your application code. Reusing objects, using primitive types instead of boxed types, avoiding unnecessary string concatenation in hot loops, and using off-heap buffers for large data can reduce GC pressure by 10-100x, which no amount of flag tuning can match.

---

### Interview Deep-Dive

**Q1: You have a Java service with p99 latency spikes. How do you determine if GC is the cause and fix it?**

_Why they ask:_ Tests systematic debugging approach.

_Strong answer:_

**Step 1: Confirm GC is the cause**

```
# Enable GC logging (if not already)
-Xlog:gc*:file=gc.log:time,uptime,level

# Correlate GC pauses with latency spikes
# Plot GC pause times alongside p99 latency
# If spikes align -> GC is the cause
```

**Step 2: Characterize the problem**

- What collector is running? (`jcmd <pid> VM.flags`)
- How often do pauses occur?
- How long are the pauses?
- Are there full GCs? (This is the #1 culprit for large spikes)
- What triggers the GC? (Allocation rate, heap occupancy)

**Step 3: Fix based on findings**

| Finding                  | Fix                                           |
| ------------------------ | --------------------------------------------- |
| Full GC events           | Lower IHOP, increase heap                     |
| Long mixed GC (G1)       | Lower pause target, spread across more cycles |
| Frequent young GC        | Increase young gen or reduce allocation       |
| High allocation rate     | Profile allocations, optimize hot paths       |
| GC pauses still too high | Switch to ZGC                                 |

**Step 4: Validate**

- Run under same load profile
- Compare p99 before and after
- Monitor for 24+ hours (some patterns are periodic)

---

**Q2: What's the difference between throughput and latency in GC, and how do you optimize for each?**

_Why they ask:_ Tests understanding of the fundamental GC trade-off.

_Strong answer:_

**Throughput** = percentage of time spent running application code vs GC code. A throughput of 99% means 1% of time is GC. Optimize by:

- Using Parallel GC (maximizes throughput)
- Large heap (fewer, longer GCs but more total work done between pauses)
- Accepting longer pauses

**Latency** = the duration of individual GC pauses. Optimize by:

- Using ZGC or Shenandoah (<1ms pauses)
- Or G1 with low `-XX:MaxGCPauseMillis`
- Accepting lower throughput (concurrent GC uses CPU alongside application)

These are fundamentally in tension:

- **High throughput collector** (Parallel): Stops the world, uses all CPUs for GC, gets maximum work done per pause - but pauses are long
- **Low latency collector** (ZGC): Runs concurrent with application, spreads work over time - but uses CPU concurrently, reducing throughput by 5-10%

**Decision:** Batch/analytics -> throughput. Interactive/real-time -> latency. Web applications -> balanced (G1).

---

**Q3: Explain the heap sizing rule of thumb and why `-Xms` should equal `-Xmx`.**

_Why they ask:_ Tests practical tuning knowledge.

_Strong answer:_

**Heap sizing: 3-4x live data set**

- Live data set = memory used by long-lived objects at steady state
- Measure with `jmap -heap` after application is warmed up and stable
- If live set is 1GB, set heap to 3-4GB
- Too small: frequent GC, possible OOM
- Too large: long GC pauses (more to scan), wasted memory

**Why `-Xms = -Xmx`:**

1. **Avoids heap resizing:** When `-Xms < -Xmx`, the JVM starts small and grows the heap under GC pressure. Each resize triggers a full GC and may copy the entire live set.
2. **Predictable behavior:** With fixed heap size, GC behavior is consistent from startup.
3. **Container-friendly:** In Kubernetes, resource limits should match actual usage. Dynamic heap sizing wastes the difference between min and max.
4. **Avoids RSS growth surprises:** The OS may overcommit memory if initial heap is small but max is large.

Exception: development/testing where memory is limited - use smaller `-Xms` for lower memory footprint.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for GC Tuning. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

