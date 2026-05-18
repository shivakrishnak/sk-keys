---
id: JVM-069
title: GC Algorithm Design Principles
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-032, JVM-036
used_by: JVM-070
related: JVM-038, JVM-039, JVM-040, JVM-064
tags:
  - jvm
  - java
  - gc
  - internals
  - deep-dive
status: complete
version: 3
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/jvm/gc-algorithm-design-principles/
---

**⚡ TL;DR** - All GC algorithms make the same tri-color marking correctness argument but differ in when they pause application threads, which generation they collect, and whether they compact the heap.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-032 - Object Lifecycle]], [[JVM-036 - Generational GC]] |
| **Used by** | [[JVM-070 - GC Trade-off Framing]] |
| **Related** | [[JVM-038 - G1GC]], [[JVM-039 - ZGC]], [[JVM-040 - Shenandoah]], [[JVM-064 - JVM Specification Deep Dive]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If you freed memory manually in Java (as in C), every missing `free()` is a leak. Every double-free is a crash. Every use-after-free is undefined behaviour. 1990s C programs routinely had memory safety bugs that took months to debug and caused security vulnerabilities. Java's design goal was to eliminate this class of bug.

**THE BREAKING POINT:**
The first Java GC (1996) was a stop-the-world mark-sweep. It paused all threads, scanned all live objects, and freed dead ones. For small heaps, this was acceptable. As heaps grew to gigabytes, pauses grew to tens of seconds. Web servers with 4GB heaps experienced pauses that browsers interpreted as server timeout. GC was the primary production scalability bottleneck.

**THE INVENTION MOMENT:**
The Generational GC insight (1981, Henry Baker's research) solved the pause problem partially: most objects die young. Collect only the young generation (small, fast), and collect the old generation rarely. This reduced 90%+ of GC pauses from full-heap to nursery-only, cutting typical pause times by 10x. Every modern GC algorithm builds on this insight.

**EVOLUTION:**
- 1996: Serial GC (STW mark-sweep-compact)
- 1999: Parallel GC (multi-threaded STW)
- 2002: CMS (Concurrent Mark Sweep - first concurrent GC)
- 2009: G1GC (region-based, concurrent, low pause)
- 2018: ZGC (concurrent compaction, sub-10ms pauses)
- 2019: Shenandoah (concurrent evacuation, OpenJDK)
- 2023: ZGC generational (JDK 21, sub-1ms target)

---

### 📘 Textbook Definition

**GC algorithm design principles** encompass the correctness invariants (tri-color marking, write barriers, remembered sets) and performance trade-offs (throughput vs pause time vs memory footprint) that all garbage collector implementations must address. The core algorithmic foundation: (1) **Reachability analysis** - liveness is defined by reachability from GC roots (stack frames, static fields, JNI references). (2) **Tri-color marking** - the invariant that ensures concurrent GC finds all live objects: white (unvisited), grey (reachable but not all references scanned), black (fully scanned, reachable). (3) **Write barriers** - code injected at object reference writes to maintain GC invariants during concurrent collection. (4) **Remembered sets** - data structures tracking old-to-young references, enabling young-only collection without scanning the entire heap.

---

### ⏱️ Understand It in 30 Seconds

**One line:** GC algorithms find live objects via reachability, use tri-color marking for correctness, and choose when to stop application threads to compact or move objects.

> Like a city's property records department: assessors (GC) need to know which properties are occupied (live objects). They start from known addresses (GC roots), follow ownership chains, and mark everything reachable. Unmarked properties are demolished (freed). The trick is doing this while residents keep moving in and out (concurrent heap mutations).

**One insight:** The fundamental GC correctness challenge is concurrent mutation: application threads modify object references while GC is traversing the heap. The tri-color invariant (no black-to-white references) is the precise constraint all concurrent GC algorithms must maintain, using write barriers to enforce it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An object is live if and only if it is reachable from a GC root (stack, statics, JNI)
2. GC must not free any live object (safety)
3. GC must eventually free all unreachable objects (liveness)
4. Concurrent GC must maintain tri-color invariant: no black object references a white object

**DERIVED DESIGN:**
From invariant 1: GC must know all GC roots. JVM maintains live-variable maps at safepoints so GC can scan stack frames without misidentifying integers as pointers.
From invariant 4: write barriers intercept all reference writes during concurrent marking. When a black object writes a white reference, the barrier either re-greys the black object (SATB: Snapshot At The Beginning) or greys the written reference (incremental update).

**THE TRADE-OFFS:**

**Gain:** Automatic memory safety; no use-after-free; no double-free; no manual memory management

**Cost:** GC pauses (STW or concurrent); throughput overhead (write barriers at every reference write); memory overhead (remembered sets, mark bitmaps, card tables)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Concurrent heap mutation requires synchronisation between application threads and GC threads. Some pause is unavoidable unless GC can move objects with application threads running (concurrent compaction).

**Accidental:** Complex remembered set implementations, card table false sharing, and region-level granularity tuning are implementation choices that vary between GC algorithms.

---

### 🧪 Thought Experiment

**SETUP:** You are designing a concurrent GC. You decide to perform marking (finding live objects) while application threads continue running.

**THE CONCURRENCY PROBLEM:**
Thread A is marking object X (black). Thread B, during marking, does: `x.ref = someWhiteObject`. Now X (black) holds a reference to `someWhiteObject` (white). Your marker has already finished with X and will not re-visit it. `someWhiteObject` is now invisible to GC. Without intervention, GC will free `someWhiteObject` while thread A still holds a reference to it.

**THE FIX - Write Barrier:**
Every time any application thread writes an object reference, a write barrier fires. There are two strategies:
- **SATB (G1, Shenandoah):** Record the OLD value being overwritten. If it was grey/white, add it to a mark queue. GC processes the queue later.
- **Incremental Update (some older collectors):** Record the NEW value. Re-mark it grey. GC processes the new value.

**THE INSIGHT:**
Every concurrent GC algorithm is built around maintaining one invariant: no black object holds a reference to a white object. Write barriers are the mechanism. The choice of write barrier strategy (SATB vs incremental update) is the primary design decision of a concurrent GC, with direct impact on pause times and throughput overhead.

---

### 🧠 Mental Model / Analogy

> Think of tri-color marking as a census team collecting signatures. White = not yet visited, Grey = visited but family not yet counted, Black = fully counted. The census team (GC) marks families. Meanwhile, families move (application threads mutate references). The rule: a black family cannot have a relative who is still white - the census team already passed them and won't come back. Write barriers are the "change of address" notifications: whenever a family moves, they notify the census team so no one gets missed.

Element mapping:
- Census team = GC marking threads
- White families = unreachable/unvisited objects
- Grey families = objects reached, children not yet scanned
- Black families = fully scanned, all references visited
- Family moving = application thread writing an object reference
- Change of address notification = write barrier

Where this analogy breaks down: in a real census, families do not disappear (die); in GC, objects become unreachable. The census analogy covers finding live objects; the death/freeing side requires the separate sweep/compact phase.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
GC algorithms are the strategies the JVM uses to find and free unused objects. They differ in how long they pause your program while cleaning up, how much memory they use, and how fast they complete. Different strategies suit different programs - some prefer never pausing, others prefer maximum speed.

**Level 2 - How to use it (junior developer):**
You choose a GC with JVM flags:
- `-XX:+UseSerialGC`: single-threaded, small heap, simple apps
- `-XX:+UseParallelGC`: multi-threaded STW, highest throughput
- `-XX:+UseG1GC`: default since Java 9, balanced throughput/pause
- `-XX:+UseZGC`: sub-10ms pauses, requires Java 11+
- `-XX:+UseShenandoahGC`: concurrent compaction, OpenJDK only
Monitor pause time with GC logs: `-Xlog:gc*`.

**Level 3 - How it works (mid-level engineer):**
All GC algorithms share three phases: (1) **Mark**: traverse from GC roots, colour all reachable objects. (2) **Sweep/Select**: identify unreachable (white) regions. (3) **Compact/Evacuate**: defragment heap by moving objects to contiguous regions. STW collectors stop all threads for all three phases. Concurrent collectors (G1, ZGC, Shenandoah) run mark concurrently with application threads, using write barriers to catch mutations. The pause only occurs for short "initial mark" and "remark" phases. ZGC goes further: even evacuation (moving objects) is concurrent, using load barriers and reference coloring to redirect reads to new object locations.

**Level 4 - Why it was designed this way (senior/staff):**
The generational hypothesis drives all modern GC design: 90%+ of objects die within one or two GC cycles. This permits a key optimisation: minor GC only scans the young generation. But this requires remembered sets - data structures that record all references FROM old gen INTO young gen. Without remembered sets, minor GC would need to scan the entire old gen to find pointers into the young gen (to avoid false positives). G1GC uses region-level remembered sets (per-region reference lists). ZGC avoids remembered sets entirely (heap scanned more efficiently via coloured pointers). Shenandoah also avoids separate remembered sets. This architecture drives the major performance differences between collectors.

**Expert Thinking Cues:**
- High GC overhead with mostly long-lived objects: generational hypothesis violated; consider G1 tuning or ZGC
- Fragmentation after long run: collector not compacting; switch to G1GC or ZGC which compact
- Write barrier overhead: measured with JFR allocation profiling; ZGC's load barrier vs G1's card table have different hot-path costs

---

### ⚙️ How It Works (Mechanism)

**Tri-Color Marking State Machine:**
```
Initial: all objects WHITE (unvisited)
1. Add GC roots to GREY set (work queue)
2. While GREY set is not empty:
   a. Pop object O from GREY
   b. Scan O's reference fields
   c. For each white reference R:
      - Color R GREY, add to queue
   d. Color O BLACK (all refs scanned)
3. All WHITE objects are unreachable -> collect
```

**Write Barrier (SATB - used by G1, Shenandoah):**
```
// Application thread: x.ref = newValue
// Write barrier injected by JIT:
Object oldValue = x.ref;
if (GC_is_marking && oldValue != null &&
  !marked(oldValue)) {
    satb_queue.enqueue(oldValue);  // rescue old value
}
x.ref = newValue;  // actual write
```

**Remembered Set (Card Table - used by G1):**
```
Heap divided into 512-byte cards.
When OLD gen object writes reference to YOUNG gen:
  - Write barrier marks card as "dirty"
  - Minor GC scans dirty cards in old gen
  - Finds all old->young references efficiently
  - No need to scan entire old gen
```

**GC Algorithm Design Axes:**
| Decision | Options | Impact |
|---|---|---|
| Pause strategy | STW vs Concurrent | Pause duration vs throughput |
| Compaction | None (sweep) vs Moving | Fragmentation vs relocation cost |
| Generations | Generational vs Region vs None | Minor GC efficiency |
| Write barrier | None vs SATB vs Incremental | Barrier overhead vs GC precision |

---

### 🔄 The Complete Picture - End-to-End Flow

**G1GC MINOR GC FLOW:**
```
  Eden fills (object allocation)    <- YOU ARE HERE
       |
  GC roots identified (safepoint)
       |
  Young gen mark: trace from roots
  through young gen objects
       |
  Scan dirty cards (remembered set)
  -> find old->young references
  -> add as additional roots
       |
  Mark young gen: live objects
  identified
       |
  Evacuate: copy live young gen objects
  to survivor space or old gen
  (update all references to new locations)
       |
  Eden freed (reclaimed)
       |
  Pause ends: application resumes
  (Pause: 5-50ms for young-only GC)
```

**FAILURE PATH:**
- Promotion failure: survivor + old gen full; young objects cannot be promoted; Full GC triggered
- Concurrent mark failure (G1): allocation rate exceeds concurrent marking speed; fallback to Full GC
- High fragmentation: objects cannot be placed in contiguous region; humongous allocations trigger GC

**WHAT CHANGES AT SCALE:**
At large heap sizes (>8GB), ZGC and Shenandoah become necessary. G1GC concurrent marking cannot keep pace with high allocation rates at very large heaps. ZGC's concurrent compaction eliminates the major bottleneck. Trade-off: ZGC requires more CPU for background GC threads.

---

### 💻 Code Example

**BAD - object design that defeats generational GC:**
```java
// Long-lived cache holding short-lived objects
// Forces old gen to be large; frequent Full GC
class RequestCache {
    // PROBLEM: This Map grows unboundedly.
    // ALL entries promoted to old gen after
    // a few minor GCs. Full GC needed to clean.
    private static final Map<String, byte[]> CACHE
        = new HashMap<>();

    static void cache(String key, byte[] data) {
        CACHE.put(key, data);  // never evicted
    }
}
```

**GOOD - bounded cache respecting GC boundaries:**
```java
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;

class RequestCache {
    // Bounded LRU: entries evicted when size limit hit
    // Short-lived entries die in young gen (good!)
    // Long-lived entries collected when evicted (good!)
    private static final Cache<String, byte[]> CACHE =
        Caffeine.newBuilder()
            .maximumSize(1_000)
            .expireAfterWrite(
                Duration.ofMinutes(5))
            .build();

    static void cache(String key, byte[] data) {
        CACHE.put(key, data);
    }
}
```

**Measuring write barrier overhead (JFR):**
```bash
# Enable JFR with allocation profiling
java -XX:StartFlightRecording=\
  duration=60s,\
  filename=gc-barriers.jfr,\
  settings=profile \
  -jar app.jar

# In JMC: "Memory" -> "Allocation in new TLAB"
# High allocation in old gen -> generational hypothesis violated
# High allocation rate in nursery -> check object lifetime
```

**How to test / verify correctness:**
```bash
# Verify GC algorithm selection:
java -XX:+PrintCommandLineFlags -version 2>&1 \
  | grep UseGC

# Measure GC overhead:
java -Xlog:gc+stats:file=gc.log \
  -XX:+UseZGC -Xmx4g -jar app.jar

# After run, check total GC time vs wallclock
jcmd <pid> GC.heap_info
```

---

### ⚖️ Comparison Table

| GC Algorithm | Pause Strategy | Compaction | Best For |
|---|---|---|---|
| Serial (-XX:+UseSerialGC) | Full STW | Yes (mark-compact) | Single-core, small heap |
| Parallel (-XX:+UseParallelGC) | Multi-thread STW | Yes | Maximum throughput, batch |
| G1GC (-XX:+UseG1GC) | Short STW + concurrent | Regional (concurrent) | Default; balanced |
| ZGC (-XX:+UseZGC) | Sub-10ms STW only | Concurrent (coloured ptrs) | Latency-critical, large heap |
| Shenandoah | Sub-10ms STW only | Concurrent (Brooks ptr) | Latency-critical, OpenJDK |
| Epsilon (-XX:+UseEpsilonGC) | None (no GC) | None | Testing only; always OOM |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Concurrent GC has no pauses" | All current concurrent GCs have short STW pauses for initial mark and remark. ZGC/Shenandoah reduce these to sub-10ms, but they are not truly pause-free. |
| "More heap = fewer GC issues" | More heap delays the problem but may make Full GC pauses longer. The real fix is reducing allocation rate and object lifetime. |
| "GC only runs when heap is full" | Concurrent GCs (G1, ZGC) run in the background continuously. They aim to complete collection before heap exhaustion, not after. |
| "Generational GC is always better" | Not for large heaps with mostly long-lived objects (e.g., in-memory databases). For these, a non-generational collector like ZGC with large heap support may be better. |
| "Write barriers are free" | Write barriers add 1-5 instructions to every reference write. For allocation-heavy code, this is measurable. JFR profiling can reveal if write barrier overhead is significant. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Concurrent GC failure (G1 fallback to Full GC)**
**Symptom:** Occasional 5-10 second Full GC pauses; GC log shows `Full GC (Allocation Failure)`

**Root Cause:** Allocation rate exceeds G1 concurrent marking speed; old gen fills before GC can clear it

**Diagnostic:**
```bash
# GC log analysis:
grep "Full GC" gc.log | head -20
grep "to-space exhausted" gc.log
# Look for: allocation rate vs concurrent GC speed
jcmd <pid> GC.heap_info
```
**Fix:** Reduce allocation rate (profile with JFR allocation events); or increase `-XX:G1HeapRegionSize`; or switch to ZGC (better at high allocation rates)

**Prevention:** Alert on GC throughput metric: `(totalTime - gcTime) / totalTime < 0.90`

**Failure Mode 2: Remembered set card table thrashing**
**Symptom:** G1GC minor GCs increasingly slow; GC log shows "scan RS" time growing

**Root Cause:** Many old-to-young object references; card table has too many dirty cards; remembered set scanning dominates minor GC pause

**Diagnostic:**
```bash
# Enable detailed G1 logging:
java -Xlog:gc+remset*=debug:file=gc.log ...
# Look for: "Young-Only Collection" RS scanning time
```
**Fix:** Reduce old-to-young references; break long-lived container + short-lived element patterns; consider ZGC (no card table)

**Prevention:** JFR promotion tracking; alert when old-gen reference count grows

**Failure Mode 3: Heap fragmentation with non-compacting GC**
**Symptom:** `java.lang.OutOfMemoryError: Java heap space` but heap usage appears below Xmx

**Root Cause:** CMS or old GC algorithm left fragmented old gen; no contiguous region for large object allocation despite sufficient total free bytes

**Diagnostic:**
```bash
# Force heap dump to inspect fragmentation:
jcmd <pid> GC.heap_info
jmap -heap <pid> | grep "Free" 
# Compare total free vs usable contiguous regions
```
**Fix:** Migrate to G1GC or ZGC (both compact the heap concurrently); add `-XX:+UseLargePages` for large object allocations

**Prevention:** Avoid CMS (removed in Java 14); use G1GC or ZGC for all new deployments

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-032 - Object Lifecycle]] - Object allocation to collection path
- [[JVM-036 - Generational GC]] - The foundational hypothesis enabling all modern GCs

**Builds On This (learn these next):**
- [[JVM-070 - GC Trade-off Framing]] - Applying these principles to algorithm selection

**Alternatives / Comparisons:**
- [[JVM-038 - G1GC]] - Concrete implementation of these principles
- [[JVM-039 - ZGC]] - Next-generation concurrent GC design
- [[JVM-040 - Shenandoah]] - Alternative approach to concurrent compaction

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Design principles behind all GC  |
|               | algorithms: tri-color, barriers, |
|               | generational hypothesis, compaction|
+--------------------------------------------------+
| PROBLEM       | Automatic memory management with |
|               | acceptable pause times at scale   |
+--------------------------------------------------+
| KEY INSIGHT   | Tri-color invariant (no black->  |
|               | white) enables concurrent marking|
+--------------------------------------------------+
| USE WHEN      | Choosing GC; debugging GC pauses;|
|               | designing object allocation      |
+--------------------------------------------------+
| AVOID WHEN    | (These are principles, not a flag)|
+--------------------------------------------------+
| TRADE-OFF     | Pause time vs throughput vs       |
|               | memory footprint (pick 2)         |
+--------------------------------------------------+
| ONE-LINER     | Generational: young gen collected|
|               | cheap; old gen costly; minimize  |
|               | promotions                        |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-070 GC trade-off framing,   |
|               | JVM-039 ZGC internals             |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. All concurrent GC algorithms maintain the tri-color invariant using write barriers - this is the correctness mechanism
2. The generational hypothesis ("most objects die young") is why minor GC is cheap and why unbounded caches cause Full GC
3. GC algorithm selection is a throughput vs pause time vs footprint trade-off - no single algorithm wins on all three

**Interview one-liner:** "All GC algorithms use reachability analysis from roots, tri-color marking with write barriers for concurrent safety, and the generational hypothesis to make minor GC cheap - differing only in when they stop threads and whether compaction is concurrent."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Concurrent correctness requires invariants that are maintained incrementally, not just at quiescent points. Write barriers (GC), transaction journals (databases), and event sourcing (distributed systems) all share this pattern: intercept mutations in-flight to maintain consistency properties without stopping the world.

**Where else this pattern appears:**
- Database MVCC: write barriers (version tracking) maintain snapshot isolation during concurrent transactions
- Distributed consensus (Raft): followers track a "commit pointer" - the tri-color analogy of not advancing state until the leader's writes are fully propagated
- Copy-on-write filesystems (ZFS, Btrfs): block-level marking ensures old blocks are not freed until new tree is fully written

---

### 💡 The Surprising Truth

GC pause times are often irrelevant to application tail latency. A 5ms GC pause sounds negligible, but if safepoint time-to-reach (TTSP) is 50ms - the time for all threads to reach a safepoint before GC begins - then the application experiences a 55ms pause, not 5ms. TTSP dominates many production GC pauses. The root cause: a thread running a long JIT-compiled loop takes time to reach the next safepoint. HotSpot inserts safepoint polls at method returns and loop back-edges, but JIT may eliminate some polls in tight loops. `jvm-opts -XX:+PrintSafepointStatistics` reveals this. ZGC's concurrent relocation nearly eliminates safepoints entirely - but even ZGC cannot help if TTSP is high due to application code. Reducing TTSP often requires code changes (avoid extremely tight loops that suppress JIT safepoint polls), not GC algorithm changes.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** The generational hypothesis says "most objects die young." But for a JVM running a machine learning inference server, every request allocates a large float array for the model output (100KB) that lives for 200ms (the request duration). This object is too large for Eden (Humongous allocation in G1) and too short-lived for Old Gen. How does this allocation pattern break the generational hypothesis, and what GC configuration or code change would fix it?
*Hint:* Research G1GC Humongous object handling (objects > region_size/2 go directly to old gen) and consider what allocation pattern change would make these objects generational.

**Q2 (Scale):** You have a service with 99.9th percentile GC pause of 80ms using G1GC. Switching to ZGC reduces this to 8ms. But application throughput drops 5% (ZGC's write barriers cost more than G1's card table). At 100,000 requests/second, what is the actual business trade-off, and what metric would you use to decide whether the switch is worth it?
*Hint:* Consider what 80ms p99.9 GC pause means for request latency SLAs, and compare against the cost of 5% throughput reduction in terms of additional server capacity needed.

**Q3 (Design Trade-off):** GraalVM Native Image compiles Java to a native binary. Native Image uses a different GC (Serial, or "G1" in GraalVM Enterprise edition). The JVM's GC algorithms assume managed bytecode execution with safepoints. Why cannot HotSpot's ZGC be used directly in a Native Image binary without significant redesign?
*Hint:* Consider what safepoints require (JIT-inserted poll code, known stack layouts), what Native Image's AOT-compiled code structure looks like, and which ZGC components depend on JVM-specific mechanisms like JVMTI or JFR.
