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
version: 3
---

**Keywords covered in this file:**

- [GC Algorithms](#gc-algorithms)
- [G1 Garbage Collector](#g1-garbage-collector)
- [ZGC](#zgc)
- [GC Tuning](#gc-tuning)

# GC Algorithms

**TL;DR** - Garbage collection algorithms automatically reclaim unused heap memory by identifying and collecting objects that are no longer reachable, using strategies ranging from simple mark-sweep to generational and concurrent approaches, each with different throughput/latency trade-offs.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In C/C++, developers manually allocate and free memory. Forgetting `free()` causes memory leaks. Calling `free()` too early causes use-after-free bugs (security vulnerabilities). Calling `free()` twice causes crashes. Memory management consumes 30-40% of C/C++ development time and is the #1 source of security vulnerabilities.

**THE BREAKING POINT:**
A C server leaks 50KB per request. After 100K requests, it crashes with out-of-memory. The leak takes weeks to find - it's a deep nesting of structs where one pointer isn't freed on the error path.

**THE INVENTION MOMENT:**
"This is exactly why garbage collection was created."

**EVOLUTION:**
Manual memory management (C/C++) -> reference counting (COM, Objective-C, Python) -> tracing GC with mark-sweep (Lisp, Java) -> generational hypothesis (Java 1.2+) -> concurrent collectors (CMS, G1, ZGC, Shenandoah).
---

### 📘 Textbook Definition

Garbage collection (GC) is the automatic process of identifying objects in the heap that are no longer reachable from GC roots (thread stacks, static fields, JNI references) and reclaiming their memory. The fundamental algorithm is mark-sweep: (1) mark all reachable objects by traversing from roots, (2) sweep unmarked objects. Modern collectors add compaction (defragmentation), generational partitioning (young/old), and concurrent operation (collect while application runs).
---

### ⏱️ Understand It in 30 Seconds

**One line:**
GC automatically finds and removes unused objects from memory so developers never have to manually free memory.

**One analogy:**

> GC is like a city waste management system. Mark phase: inspectors walk every road starting from city hall (GC roots), marking all buildings (objects) they can reach. Sweep phase: any unmarked building is demolished and the land reclaimed. Compact phase: remaining buildings are moved together to eliminate gaps.

**One insight:**
The generational hypothesis is the key insight behind modern GC: "most objects die young." In a typical Java application, 95% of objects become garbage within milliseconds of creation (temporary strings, iterators, boxed primitives). By collecting the young generation frequently and the old generation rarely, GC optimizes for the common case.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
GC algorithm design embodies a universal engineering trade-off triangle: throughput vs latency vs memory footprint. You can optimize any two at the expense of the third. This same triangle appears in database indexes (write throughput vs read latency vs storage), network protocols (bandwidth vs latency vs reliability), and distributed consensus (consistency vs availability vs partition tolerance). The expert insight: all GC algorithms are variations of mark-sweep, mark-compact, or copying collection - combined with generational hypothesis optimizations. The generational hypothesis (most objects die young) is the single most impactful observation in GC design, enabling 10x throughput improvements by focusing collection on the young generation. If redesigning today, you would build concurrent, region-based collectors from the start (like ZGC) with automatic tuning via ML-based heuristics that adapt to workload changes in real-time.

**Expert thinking cues:**
- "What's the pause time budget?" - this determines the algorithm family
- "Is the generational hypothesis holding?" - if not (long-lived caches), generational GC hurts
- "What percentage of CPU can GC consume?" - concurrent collectors trade CPU for lower pauses
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

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** Automatic memory reclamation strategies that find and free unreachable objects on the JVM heap
**PROBLEM IT SOLVES:** Eliminates manual memory management (malloc/free) and its bugs: leaks, use-after-free, double-free
**KEY INSIGHT:** All GC is mark-sweep, mark-compact, or copying - combined with generational hypothesis optimizations
**USE WHEN:** Every Java application uses GC. Choice of algorithm depends on throughput vs latency requirements
**AVOID WHEN:** N/A - GC is mandatory. But avoid wrong algorithm for workload (e.g., Parallel for latency-sensitive)
**ANTI-PATTERN:** Calling `System.gc()` to force collection - undermines GC heuristics and causes full STW pauses
**TRADE-OFF:** Throughput (Parallel) vs latency (ZGC) vs memory footprint (Serial) - pick two
**ONE-LINER:** "GC trades CPU cycles for memory safety, and the algorithm choice determines the cost distribution"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. GC traces from roots, marks reachable objects, sweeps/compacts the rest
2. Generational hypothesis: most objects die young -> collect young gen frequently, old gen rarely
3. Throughput vs latency trade-off defines collector choice

**Interview one-liner:**
"Garbage collection traces reachable objects from GC roots, reclaims unreachable memory, and uses generational partitioning because most objects die young, with different collectors optimizing for throughput or latency."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Garbage collection can be FASTER than manual memory management. In a generational collector, allocating an object is just bumping a pointer (O(1)). In C's `malloc()`, finding a suitable free block requires searching a free list (O(n) worst case). And minor GC copies only live objects (typically 5% of young gen) - the 95% garbage costs zero to "free." The per-object cost of GC is often lower than the per-object cost of `malloc`/`free`.
---

### ⚖️ Comparison Table

| Algorithm | Type | Pause Model | Best For |
|-----------|------|-------------|---------|
| Serial | Copying + Mark-Compact | Full STW | Small heaps, single-core |
| Parallel | Copying + Mark-Compact | Full STW | Max throughput, batch |
| G1 | Region + Concurrent | Partial STW | General purpose, balanced |
| ZGC | Concurrent + Load barriers | Sub-ms STW | Ultra-low latency |
| Shenandoah | Concurrent + Brooks ptrs | Sub-ms STW | Low latency (OpenJDK) |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | GC eliminates all memory leaks | GC only collects unreachable objects. If code holds references to objects no longer needed (listeners, caches, static collections), they are reachable and never collected - this is a memory leak. |
| 2 | More heap always improves GC performance | Larger heap means more live data to scan during full GC. Doubling heap can double full GC pause time. Right-size the heap to 2-4x live data set. |
| 3 | Concurrent GC means no pauses | All JVM GCs have SOME stop-the-world pauses (root scanning, final marking). Concurrent collectors minimize pause duration but never eliminate it entirely. |
| 4 | GC overhead is always significant | Modern GC typically consumes 1-5% of CPU. For most applications, GC overhead is negligible compared to IO, network, and business logic. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Premature promotion (premature tenuring)**
**Symptom:** Old generation fills rapidly. Frequent mixed or full GC cycles. High promotion rate in GC logs.
**Root Cause:** Survivor spaces too small, causing objects to be promoted to old gen before they die. Survivor age threshold too low.
**Diagnostic:**

```
# Check promotion rate and tenuring threshold
jstat -gcutil <pid> 1000
# Look at S0/S1 utilization and O (old gen)
# GC log: -Xlog:gc*,gc+age=debug
```

**Fix:**
```java
// BAD: default survivor sizing may be wrong
// Objects promoted after 1-2 GC cycles

// GOOD: increase survivor space and threshold
// -XX:SurvivorRatio=6 (larger survivors)
// -XX:MaxTenuringThreshold=15
// -XX:+PrintTenuringDistribution (to verify)
```
**Prevention:** Monitor tenuring distribution in GC logs. Size survivors to hold objects that die within 2-5 GC cycles.

**Failure Mode 2: Full GC caused by Metaspace exhaustion**
**Symptom:** Full GC triggered despite heap having free space. GC log shows "Metadata GC Threshold" as cause.
**Root Cause:** Metaspace (class metadata) fills up, triggering full GC to attempt class unloading. Common with heavy reflection, dynamic proxies, or classloader leaks.
**Diagnostic:**

```
jstat -gcmetacapacity <pid>
# Check MCMX (Metaspace max) vs MCMN (used)
jcmd <pid> VM.classloader_stats
```

**Fix:**
```java
// BAD: default MetaspaceSize is too small
// for applications with many classes

// GOOD: size Metaspace appropriately
// -XX:MetaspaceSize=256m
// -XX:MaxMetaspaceSize=512m
// Monitor with JMX: java.lang:type=MemoryPool,
// name=Metaspace
```
**Prevention:** Set `-XX:MetaspaceSize` and `-XX:MaxMetaspaceSize` explicitly. Monitor classloader count for leaks.

**Failure Mode 3: GC thrashing (continuous full GC)**
**Symptom:** Application nearly stops. GC consumes >90% of CPU. `GCTimeRatio` or `GCOverheadLimit` exceeded.
**Root Cause:** Heap is nearly full of live data. GC runs continuously but can barely reclaim any memory.
**Diagnostic:**

```
jstat -gcutil <pid> 1000
# O (old gen) consistently >95%
# GCT (GC time) growing rapidly
# Application: OutOfMemoryError: GC overhead limit
```

**Fix:**
```java
// 1. Immediate: increase heap
// -Xmx (double current value)
// 2. Root cause: find memory leak
// jmap -histo:live <pid> | head -20
// jmap -dump:live,format=b,file=heap.hprof <pid>
// 3. Analyze with Eclipse MAT or VisualVM
```
**Prevention:** Monitor old gen utilization. Alert at 80%. Set `-XX:+HeapDumpOnOutOfMemoryError`. Profile memory usage in staging.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- JVM Memory Model - heap structure, generations, object lifecycle
- Object allocation and lifecycle - how objects are created, referenced, and become unreachable

**Builds on this (learn these next):**

- G1 Garbage Collector - the default modern GC with region-based design
- ZGC - ultra-low latency concurrent collector for demanding workloads

**Alternatives / Comparisons:**

- Manual memory management (C/C++) - explicit malloc/free, no GC overhead but error-prone
- Reference counting (Python, Swift) - deterministic destruction but circular reference issues


---

---

# G1 Garbage Collector

**TL;DR** - G1 (Garbage First) is Java's default garbage collector since Java 9, dividing the heap into regions and prioritizing collection of regions with the most garbage, achieving predictable pause times with good throughput.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before G1, you had two choices: Parallel GC (high throughput but long pauses proportional to heap size) or CMS (low pauses but fragmentation over time, leading to catastrophic full GC pauses). Neither could guarantee predictable pause times.

**THE BREAKING POINT:**
A CMS-collected application runs smoothly for hours, then hits a fragmentation-induced full GC that stops the world for 30 seconds. The load balancer marks the server as dead. On restart, the same pattern repeats.

**THE INVENTION MOMENT:**
"This is exactly why G1 was created."

**EVOLUTION:**
Mark-Sweep-Compact -> Parallel GC (throughput-first) -> CMS (low-pause attempt, fragmentation) -> G1 (region-based, predictable pauses, Java 9 default) -> ZGC/Shenandoah (sub-ms pauses).
---

### 📘 Textbook Definition

G1 (Garbage First) is a region-based, generational, concurrent garbage collector. It divides the heap into equal-sized regions (1-32MB each) that can be Eden, Survivor, Old, or Humongous. G1 tracks the amount of garbage per region and collects the regions with the most garbage first (hence "Garbage First"), optimizing for a user-specified maximum pause time target.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
G1 divides the heap into regions, collects the most garbage-filled regions first, and targets a specific maximum pause time.

**One analogy:**

> Traditional GC is like cleaning your entire house every time. G1 is like a smart cleaning robot that scans all rooms, identifies the messiest ones, and cleans only those rooms within your 15-minute budget. It always starts with the dirtiest room to maximize what it cleans per minute.

**One insight:**
G1's key innovation is the pause time target (`-XX:MaxGCPauseMillis=200`). Instead of collecting everything (unpredictable pause), G1 selects just enough regions to fit within the target pause time. If 200ms allows collecting 50 regions, it picks the 50 with the most garbage. This makes pause times proportional to the target, not the heap size.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
G1's region-based design is the JVM equivalent of database sharding: instead of one large heap to manage, it breaks the heap into hundreds of equal-sized regions that can be independently collected. This same approach appears in SSD firmware (block-based garbage collection), operating systems (page-based memory management), and distributed storage (chunk-based replication). The expert insight: G1's 'Garbage-First' name reveals its core heuristic - it always collects the region with the most garbage first, maximizing space reclaimed per unit of pause time. The remembered sets (RSets) that track cross-region references consume 5-20% of heap, which is the hidden cost of region independence. If redesigning today, you would use load barriers instead of remembered sets (as ZGC does) to eliminate the memory overhead at the cost of slight per-reference CPU overhead.

**Expert thinking cues:**
- "How many regions are in the collection set?" - more regions = longer pause but more space reclaimed
- "Is the RSet overhead acceptable?" - >20% of heap in RSets signals too many cross-region references
- "Are mixed collections keeping up?" - if old gen grows continuously, collection can't keep pace
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** Region-based, concurrent, generational GC that targets configurable pause times (default since JDK 9)
**PROBLEM IT SOLVES:** Balances throughput and latency for general-purpose workloads with predictable pause targets
**KEY INSIGHT:** Heap is divided into equal-sized regions. G1 collects the regions with the most garbage first (Garbage-First)
**USE WHEN:** General-purpose applications, 4GB+ heaps, need predictable pauses without extreme latency requirements
**AVOID WHEN:** Ultra-low latency (<10ms p99) - use ZGC. Maximum throughput batch jobs - use Parallel GC
**ANTI-PATTERN:** Setting `-XX:MaxGCPauseMillis` to unrealistically low values - G1 can't meet them and thrashes
**TRADE-OFF:** Remembered sets consume 5-20% of heap memory for cross-region reference tracking
**ONE-LINER:** "G1 breaks the heap into regions and always collects the most garbage-filled regions first"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. G1 divides heap into regions and collects the most garbage-filled regions first
2. `-XX:MaxGCPauseMillis=200` sets the pause time target (G1 adapts to meet it)
3. Young GC + concurrent marking + mixed GC = normal operation; full GC = emergency

**Interview one-liner:**
"G1 partitions the heap into regions, tracks garbage per region, and during mixed GC selects the most garbage-dense regions to collect within a configurable pause time target, making pauses predictable rather than proportional to heap size."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

G1's region-based design means increasing heap size can actually DECREASE pause times. In traditional collectors, more heap = more to scan = longer pauses. In G1, more heap = more regions = G1 can be more selective, choosing only the most garbage-dense regions to meet its pause target. This breaks the conventional wisdom that "bigger heap = bigger pauses."
---

### ⚖️ Comparison Table

| Aspect | G1 | Parallel | ZGC |
|--------|----|---------|-----|
| Pause model | Incremental mixed | Full STW | Sub-ms concurrent |
| Heap layout | Regions (1-32MB) | Contiguous gens | Regions (2MB) |
| Default | JDK 9+ | JDK 1-8 | No |
| Max pause target | Configurable | No | <1ms |
| Memory overhead | RSets (5-20%) | Minimal | No compressed oops |
| Best heap size | 4GB-64GB | Any | Any (up to 16TB) |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | G1 always meets MaxGCPauseMillis target | MaxGCPauseMillis is a soft target, not a guarantee. G1 adjusts collection work per cycle to approach the target but can exceed it during evacuation failures or humongous allocations. |
| 2 | G1 doesn't do full GC | G1 can fall back to a full, single-threaded STW collection if concurrent marking can't keep up with allocation rate. Full GCs in G1 are a serious performance problem. |
| 3 | Region size doesn't matter | Region size (1-32MB, auto-calculated) determines the humongous object threshold (>50% of region). Wrong region size causes excessive humongous allocations that bypass normal collection. |
| 4 | G1 is always better than Parallel GC | For pure throughput workloads (batch processing, offline analytics), Parallel GC can deliver 5-15% higher throughput because it has lower per-object overhead (no RSets, no barriers). |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Humongous allocation fragmentation**
**Symptom:** Unexpected full GCs despite low heap utilization. GC log shows "G1 Humongous Allocation" events.
**Root Cause:** Objects >50% of G1 region size are "humongous" - allocated directly in old gen, spanning multiple contiguous regions. They cause fragmentation and are only collected during full GC (before JDK 8u60) or concurrent cycles.
**Diagnostic:**

```
# Count humongous allocations in GC log
grep -c "humongous" gc.log
# Check region size
java -XX:+PrintFlagsFinal -version | grep G1HeapRegionSize
# Objects > regionSize/2 are humongous
```

**Fix:**
```java
// BAD: default region size with large arrays
// byte[] buf = new byte[4 * 1024 * 1024]; // 4MB
// With 4MB regions, this is humongous

// GOOD: increase region size
// -XX:G1HeapRegionSize=16m
// Or: reduce allocation size
// Use pooled buffers for large arrays
ByteBuffer buf = ByteBuffer.allocateDirect(4_000_000);
```
**Prevention:** Size G1HeapRegionSize so common allocations are <50% of region. Monitor humongous allocation count in GC logs.

**Failure Mode 2: Mixed collection evacuation failure**
**Symptom:** G1 falls back to full GC. GC log shows "to-space exhausted" or "evacuation failure".
**Root Cause:** Not enough free regions to copy live objects during mixed collection. G1 can't complete evacuation and falls back to single-threaded full compaction.
**Diagnostic:**

```
grep -i "evacuation failure\|to-space exhausted" gc.log
# Also check: IHOP (Initiating Heap Occupancy Percent)
grep "Initiate" gc.log
```

**Fix:**
```java
// BAD: IHOP too high, marking starts too late
// Allocation rate > collection rate

// GOOD: trigger marking earlier
// -XX:InitiatingHeapOccupancyPercent=35
// (default 45, lower = earlier marking)
// Increase heap: -Xmx (more breathing room)
// Set -Xms = -Xmx (prevent resizing)
```
**Prevention:** Monitor IHOP and adjust. Keep 20-30% headroom. Set `-XX:-G1UseAdaptiveIHOP` if adaptive IHOP is not converging.

**Failure Mode 3: RSet memory overhead too high**
**Symptom:** Effective heap is 15-25% smaller than -Xmx. GC spends significant time maintaining remembered sets.
**Root Cause:** Many cross-region references (e.g., large interconnected object graphs) cause RSets to consume substantial memory.
**Diagnostic:**

```
# Enable RSet statistics
# -Xlog:gc+remset*=debug
# Look for RSet memory usage in output
jcmd <pid> GC.heap_info
```

**Fix:**
```java
// Reduce cross-region references:
// 1. Co-locate related objects (improve locality)
// 2. Increase region size (fewer cross-region refs)
// -XX:G1HeapRegionSize=16m or 32m
// 3. Consider ZGC if RSet overhead is >15%
// ZGC uses load barriers instead of RSets
```
**Prevention:** Profile object graph connectivity. Choose G1HeapRegionSize to minimize cross-region references. Consider ZGC for highly connected graphs.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- GC Algorithms - foundational GC concepts (mark, sweep, compact, copy)
- JVM Heap structure - young gen, old gen, Metaspace, and their purposes

**Builds on this (learn these next):**

- GC Tuning - optimizing G1 flags for specific workload characteristics
- ZGC - alternative collector when G1 pause targets are insufficient

**Alternatives / Comparisons:**

- Parallel GC - higher throughput for batch workloads, simpler design, higher pauses
- ZGC - sub-ms pauses regardless of heap size, but higher memory overhead


---

---

# ZGC

**TL;DR** - ZGC (Z Garbage Collector) is a scalable, low-latency garbage collector that keeps pause times under 1 millisecond regardless of heap size, from megabytes to multi-terabytes.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
G1 GC targets 200ms pauses but can spike higher under heavy allocation. For latency-sensitive applications (trading platforms, real-time bidding, interactive gaming), even 50ms pauses are unacceptable. Large heaps (>32GB) amplify the problem.

**THE BREAKING POINT:**
An ad-bidding platform must respond within 10ms. A 100ms G1 GC pause means missed auctions, lost revenue. The team considers C++ for the hot path, losing Java's productivity.

**THE INVENTION MOMENT:**
"This is exactly why ZGC was created."

**EVOLUTION:**
G1 (200ms target) -> Shenandoah (concurrent compaction, <10ms) -> ZGC (concurrent everything, <1ms). ZGC became production-ready in Java 15.
---

### 📘 Textbook Definition

ZGC is a concurrent, region-based, compacting garbage collector designed for sub-millisecond pause times. It performs almost all GC work concurrently with the application, using colored pointers (metadata embedded in object references) and load barriers (checks when loading a reference) to achieve pauseless operation. ZGC pause times are independent of heap size, live set size, and root set size.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
ZGC achieves <1ms GC pauses at any heap size by doing all heavy work concurrently with your application.

**One analogy:**

> G1 is like a restaurant that closes for 10 minutes each hour for cleaning. ZGC is like a restaurant that never closes - cleaners work alongside diners, unobtrusively moving furniture and cleaning while guests continue eating.

**One insight:**
ZGC's breakthrough is colored pointers. Every object reference in the heap carries metadata bits that tell the GC the state of the referenced object (marked, relocated, remapped). Load barriers check these bits on every pointer load and fix up references as needed. This eliminates the need for stop-the-world phases during marking and compaction.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
ZGC represents the theoretical endpoint of concurrent GC design: sub-millisecond pauses regardless of heap size (tested up to 16TB). It achieves this through colored pointers (metadata stored in unused pointer bits) and load barriers (code injected at every heap reference load). This same colored-pointer technique appears in tagged architectures (SPARC, ARM MTE for memory safety), and the load-barrier concept maps to copy-on-write in OS virtual memory. The expert insight: ZGC's O(1) pause times (independent of heap/live-set size) fundamentally changes capacity planning - you can over-provision heap without pause time penalty. Since JDK 21, Generational ZGC adds young/old separation, bringing throughput within 5% of G1 while maintaining sub-ms pauses. If redesigning today, Generational ZGC would be the default collector for all workloads.

**Expert thinking cues:**
- "Is heap size the bottleneck?" - ZGC lets you use huge heaps without pause penalty
- "Are we on JDK 21+?" - Generational ZGC closes the throughput gap with G1
- "What's the pointer width?" - ZGC uses 64-bit pointers only, no compressed oops on <32GB heaps
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** Ultra-low latency concurrent GC with sub-millisecond pauses regardless of heap size (up to 16TB)
**PROBLEM IT SOLVES:** Eliminates GC-induced latency spikes for latency-sensitive applications (APIs, trading, gaming)
**KEY INSIGHT:** Colored pointers + load barriers enable concurrent relocation without stopping application threads
**USE WHEN:** Latency-critical services, large heaps (>32GB), applications where p99 latency matters more than throughput
**AVOID WHEN:** JDK <15 (experimental). Memory-constrained environments (no compressed oops). Maximum throughput batch
**ANTI-PATTERN:** Using ZGC on JDK 11-14 in production - it was experimental and lacked key optimizations
**TRADE-OFF:** No compressed oops = 1.5x memory for references on heaps <32GB. Higher CPU for load barriers
**ONE-LINER:** "ZGC achieves O(1) pause times by doing all heavy lifting concurrently with application threads"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. ZGC achieves <1ms pauses at any heap size using colored pointers and load barriers
2. Almost all GC work is concurrent - only root scanning requires brief STW
3. Use generational ZGC (`-XX:+ZGenerational`) on Java 21+ for best performance

**Interview one-liner:**
"ZGC uses colored pointers with metadata in reference bits and load barriers to perform marking, compaction, and reference updates concurrently, achieving sub-millisecond pauses independent of heap size."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

ZGC can handle heaps up to 16 terabytes with the same sub-millisecond pause times as a 1GB heap. The pause time is determined only by the number of GC roots (thread stacks and static fields), not by the heap size or the number of live objects. This means ZGC's pause time is O(roots), not O(heap) or O(live_set).
---

### ⚖️ Comparison Table

| Feature | ZGC | G1 | Shenandoah |
|---------|-----|----|------------|
| Max pause | <1ms | 200ms target | <10ms |
| Concurrent relocation | Yes (load barriers) | No (STW) | Yes (Brooks pointers) |
| Compressed oops | No | Yes | Yes |
| Generational (JDK 21+) | Yes | Yes | No |
| Max tested heap | 16TB | ~256GB | ~2TB |
| JDK production-ready | JDK 15+ | JDK 9+ | JDK 15+ |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | ZGC has no pauses at all | ZGC has brief STW pauses (<1ms) for root scanning and thread handshakes. It's sub-millisecond, not pauseless. |
| 2 | ZGC is only for huge heaps | ZGC works on any heap size. Since JDK 21 with generational mode, it's competitive with G1 even on 2-4GB heaps. |
| 3 | ZGC always uses more memory than G1 | ZGC lacks compressed oops, using 8 bytes per reference vs 4 bytes. But it doesn't need remembered sets (5-20% of heap in G1). Net overhead depends on workload. |
| 4 | ZGC can't match G1 throughput | Generational ZGC (JDK 21+) achieves throughput within 5% of G1 for most workloads. The throughput gap that existed in early ZGC versions is largely closed. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Allocation stall despite low pause times**
**Symptom:** Application threads block waiting for GC to reclaim memory. Latency spikes >100ms but GC pauses are <1ms.
**Root Cause:** ZGC's concurrent collection can't keep up with allocation rate. Application threads stall waiting for free pages.
**Diagnostic:**

```
# GC log shows "Allocation Stall" events
grep "Allocation Stall" gc.log
# Check allocation rate
grep "Allocation Rate" gc.log
# jstat shows Eden constantly full
```

**Fix:**
```java
// BAD: heap too small for allocation rate
// ZGC can't complete cycles fast enough

// GOOD: increase heap for concurrent headroom
// -Xmx (3-5x live data set for ZGC)
// ZGC needs more headroom than G1 because
// collection runs concurrently with allocation

// Or: reduce allocation rate in application
// (profile with: asprof -e alloc <pid>)
```
**Prevention:** Size heap to 3-5x live data set for ZGC. Monitor allocation rate vs GC reclamation rate. Alert on allocation stalls.

**Failure Mode 2: No compressed oops increases memory usage**
**Symptom:** Application uses 40-50% more memory than under G1 for the same workload. Heap usage higher than expected.
**Root Cause:** ZGC uses 64-bit object references (no compressed oops). Each reference is 8 bytes instead of 4 bytes. Reference-heavy workloads see significant overhead.
**Diagnostic:**

```
# Compare heap usage G1 vs ZGC
# G1: java -XX:+UseG1GC -Xmx8g -XX:+PrintFlagsFinal
# ZGC: java -XX:+UseZGC -Xmx8g -XX:+PrintFlagsFinal
# Check UseCompressedOops flag (ZGC = false)
jcmd <pid> VM.flags | grep Compressed
```

**Fix:**
```java
// Accept higher memory for lower latency:
// Size heap 1.5x what G1 needs
// -Xmx12g (instead of -Xmx8g with G1)

// Or: reduce reference count
// Use arrays of primitives instead of objects
// Flatten object hierarchies
// Use value types (JDK Valhalla, future)
```
**Prevention:** Plan for 1.5x memory budget vs G1. Profile reference density. Use Generational ZGC (JDK 21+) which partially mitigates through better young-gen collection.

**Failure Mode 3: ZGC on JDK versions before 15**
**Symptom:** Production instability, crashes, or poor performance with ZGC on JDK 11-14.
**Root Cause:** ZGC was experimental before JDK 15. Missing optimizations, known bugs, and incomplete feature set (no class unloading before JDK 12, no uncommit before JDK 13).
**Diagnostic:**

```
java -version
# If JDK < 15, ZGC is experimental
# Check: -XX:+UnlockExperimentalVMOptions required
```

**Fix:**
```java
// BAD: running ZGC on JDK 11 in production
// -XX:+UnlockExperimentalVMOptions -XX:+UseZGC

// GOOD: upgrade to JDK 17+ (LTS) or JDK 21+
// -XX:+UseZGC (no experimental flag needed)
// JDK 21: -XX:+UseZGC -XX:+ZGenerational
// (generational mode for better throughput)
```
**Prevention:** Use ZGC only on JDK 15+ in production. Prefer JDK 21+ for Generational ZGC. Test thoroughly before production deployment.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- GC Algorithms - understand mark-sweep, copying, concurrent collection concepts
- G1 Garbage Collector - the general-purpose baseline to compare against

**Builds on this (learn these next):**

- GC Tuning for ZGC - heap sizing, allocation rate management for ZGC
- Generational ZGC (JDK 21+) - generational mode that improves throughput

**Alternatives / Comparisons:**

- G1 GC - lower memory overhead, proven track record, good enough for most workloads
- Shenandoah - similar goals to ZGC using Brooks pointers instead of colored pointers


---

---

# GC Tuning

**TL;DR** - GC tuning is the process of configuring garbage collection parameters to optimize for your application's specific throughput and latency requirements, starting with the right collector choice and heap sizing.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Default GC settings are designed for general-purpose workloads. A high-throughput batch processor with defaults may spend too much time in GC. A low-latency service with defaults may have unacceptable pause spikes. Without tuning, you leave performance on the table.

**THE BREAKING POINT:**
A REST API server with 4GB heap and default G1 settings has p99 latency spikes of 500ms. Users see intermittent slowness. The team suspects network issues for weeks before realizing it's GC pauses during mixed collection.

**THE INVENTION MOMENT:**
"This is exactly why GC tuning was created."

**EVOLUTION:**
Manual tuning of 100+ flags (pre-Java 9) -> ergonomic defaults (JVM auto-tunes based on machine) -> simpler tuning (fewer flags needed with G1/ZGC) -> near-zero tuning with ZGC.
---

### 📘 Textbook Definition

GC tuning is the systematic process of selecting the appropriate garbage collector, sizing the heap and generations, and adjusting collector-specific parameters to meet application performance requirements. Modern tuning follows the principle: choose the right collector, size the heap correctly, and avoid over-tuning.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
GC tuning = right collector + right heap size + don't over-tune.

**One analogy:**

> GC tuning is like adjusting a car's suspension. You pick the right vehicle type first (sports car = low latency, truck = high throughput). Then you adjust spring stiffness (heap size) and damping (pause target). Over-tuning makes the ride worse - a few key adjustments are better than tweaking every bolt.

**One insight:**
The #1 GC tuning mistake is over-tuning. Modern collectors (G1, ZGC) are designed to auto-adapt. Setting 20 flags usually makes things worse because the ergonomics can no longer adapt. Start with collector choice + heap size + pause target, and only add flags if measurement shows a specific problem.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
GC tuning follows the universal performance optimization principle: measure first, hypothesize second, change one variable at a time, and verify. This same methodology appears in database query tuning (EXPLAIN before index), network optimization (packet capture before firewall rules), and compiler optimization (profile-guided before manual). The expert insight: 90% of GC tuning is choosing the right collector and sizing the heap correctly. The remaining 10% is fine-tuning specific flags, which has rapidly diminishing returns and creates fragile configs. The three most impactful parameters across all collectors are: `-Xmx/-Xms` (heap size), `-XX:MaxGCPauseMillis` (pause target), and `-XX:NewRatio` (generational sizing). If redesigning today, you would build auto-tuning into the collector that adapts in real-time based on application behavior (G1 already does this partially with adaptive IHOP).

**Expert thinking cues:**
- "What did the GC logs say before tuning?" - never tune without baseline data
- "How many flags were changed?" - >5 GC flags is a code smell for over-tuning
- "Is the workload stable?" - tuning for a specific load pattern breaks when load changes
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** The practice of configuring JVM garbage collector settings to optimize for specific workload requirements
**PROBLEM IT SOLVES:** Default GC settings may not match application needs - wrong settings cause latency spikes or throughput loss
**KEY INSIGHT:** 90% of GC tuning is choosing the right collector and sizing the heap. Over-tuning creates fragile configs
**USE WHEN:** GC pauses exceed SLA, throughput is below target, OOM errors, or during capacity planning
**AVOID WHEN:** Before measuring baseline. Before understanding the workload. Premature optimization without data
**ANTI-PATTERN:** Tuning 50+ GC flags without understanding workload - creates non-portable, fragile configurations
**TRADE-OFF:** More tuning = better fit for current workload but fragile to workload changes
**ONE-LINER:** "Measure with GC logs, choose the right collector, size the heap, then stop tuning"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Choose collector first: Parallel (throughput), G1 (balanced), ZGC (latency)
2. Size heap to 3-4x live data set, set `-Xms = -Xmx`
3. Always enable GC logging, never tune without measurement

**Interview one-liner:**
"GC tuning starts with choosing the right collector for your throughput/latency trade-off, sizing the heap to 3-4x live data, and making measured, incremental changes with GC logging always enabled."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

The most effective GC tuning is often not changing GC flags at all - it's reducing allocation rate in your application code. Reusing objects, using primitive types instead of boxed types, avoiding unnecessary string concatenation in hot loops, and using off-heap buffers for large data can reduce GC pressure by 10-100x, which no amount of flag tuning can match.
---

### ⚖️ Comparison Table

| Approach | Flags Changed | Effort | Risk |
|----------|--------------|--------|------|
| Default settings | 0 | None | None |
| Collector + heap sizing | 2-3 | Low | Low |
| Generation sizing | 3-5 | Medium | Medium |
| Full flag tuning | 10-50 | High | High (fragile) |
| Auto-tuning (G1 ergonomics) | 1 target | Low | Low |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | More GC flags = better performance | Over-tuning creates configurations that are optimal for one specific load pattern but break when load changes. 2-3 flags is usually sufficient. |
| 2 | GC tuning should come first in optimization | GC tuning should come LAST. First: fix algorithmic issues, reduce allocation rate, fix memory leaks. GC tuning can't compensate for application problems. |
| 3 | -Xmx and -Xms should be different | For production services, set -Xmx = -Xms. Different values cause heap resizing pauses and make GC behavior less predictable. |
| 4 | System.gc() is a valid tuning technique | System.gc() triggers an uncontrolled full GC that ignores all tuning flags. It bypasses GC ergonomics and should almost never be used. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Over-tuned configuration breaks under workload change**
**Symptom:** Application performs well under normal load but has severe GC pauses during traffic spikes or changed request patterns.
**Root Cause:** GC flags were tuned for a specific load profile. Fixed-size generation splits, explicit GC timing, and disabled ergonomics prevent adaptation.
**Diagnostic:**

```
# Count GC-related flags
java -XX:+PrintFlagsFinal | grep -c "gc\|GC"
# If many were manually set (non-default), over-tuned
jcmd <pid> VM.flags | grep -v "default"
```

**Fix:**
```java
// BAD: 20+ manually set GC flags
// -XX:NewSize=2g -XX:MaxNewSize=2g
// -XX:SurvivorRatio=8 -XX:MaxTenuringThreshold=5
// ... (fragile, non-adaptive)

// GOOD: minimal flags, let GC adapt
// -XX:+UseG1GC -Xmx8g -Xms8g
// -XX:MaxGCPauseMillis=100
// (3 flags, G1 adapts everything else)
```
**Prevention:** Use adaptive GC ergonomics. Set goals (MaxGCPauseMillis) not mechanisms (generation sizes). Test under variable load.

**Failure Mode 2: Heap sized too small for live data set**
**Symptom:** Constant GC activity. Old gen always >90% full. Frequent full GCs. Eventual OOM.
**Root Cause:** -Xmx is less than 2x the live data set. GC runs continuously trying to reclaim the thin sliver of dead objects.
**Diagnostic:**

```
# After full GC, check old gen occupancy
# If post-GC old gen > 60% of -Xmx, heap is too small
jstat -gcold <pid> 1000
# Or from GC log: post-full-GC heap usage
grep "Full" gc.log | tail -5
```

**Fix:**
```java
// BAD: live data set is 3GB, heap is 4GB
// Only 1GB free after full GC = constant GC

// GOOD: set heap to 3-4x live data set
// -Xmx12g -Xms12g
// Post-GC old gen should be 30-40% of -Xmx
```
**Prevention:** Measure live data set after full GC. Set -Xmx to 3-4x live data. Monitor post-GC occupancy.

**Failure Mode 3: GC logs not enabled in production**
**Symptom:** GC problems occur but there's no data to diagnose. Troubleshooting requires reproducing the issue with logging enabled.
**Root Cause:** GC logging was disabled or not configured. Without logs, root cause analysis is guesswork.
**Diagnostic:**

```
# Check if GC logging is enabled
jcmd <pid> VM.flags | grep "Xlog\|PrintGC"
# If empty, no GC logging
```

**Fix:**
```java
// BAD: no GC logging
// java -Xmx8g -jar app.jar

// GOOD: always enable GC logging
// JDK 9+:
// -Xlog:gc*:file=gc.log:time,level,tags:
//   filecount=5,filesize=100m
// JDK 8:
// -XX:+PrintGCDetails -XX:+PrintGCDateStamps
// -Xloggc:gc.log -XX:+UseGCLogFileRotation
```
**Prevention:** Enable GC logging in ALL environments including production. Overhead is negligible (<0.1%). Rotate log files to manage disk.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- GC Algorithms - understand which algorithms exist and their trade-offs
- JVM Profiling Tools - how to collect and analyze GC logs and metrics

**Builds on this (learn these next):**

- Production performance monitoring - integrating GC metrics into observability stack
- Capacity planning - using GC data to right-size infrastructure

**Alternatives / Comparisons:**

- Application-level optimization - reducing allocation rate is often more effective than GC tuning
- Off-heap memory (DirectByteBuffer, Unsafe) - bypass GC entirely for large data sets
