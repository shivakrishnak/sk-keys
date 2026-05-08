---
layout: default
title: "Java Memory Management (Stack vs Heap Practical)"
parent: "Java & JVM Internals"
nav_order: 16
permalink: /java/java-memory-management-stack-heap/
id: JLG-016
category: Java & JVM Internals
difficulty: ★★☆
depends_on: JVM, Garbage Collection (GC), Stack vs Heap
used_by: Java Performance Tuning, Java Profiling
related: OutOfMemoryError, GC Tuning, Memory Leak
tags:
  - java
  - jvm
  - memory
  - gc
  - intermediate
---

# JLG-016 — Java Memory Management (Stack vs Heap Practical)

⚡ **TL;DR —** The JVM divides memory into a per-thread stack for method frames and a shared heap for objects; knowing which region holds what determines how you diagnose and fix every `OutOfMemoryError`.

| | |
|---|---|
| **Depends on** | JVM, Garbage Collection (GC), Stack vs Heap |
| **Used by** | Java Performance Tuning, Java Profiling |
| **Related** | OutOfMemoryError, GC Tuning, Memory Leak |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** If every piece of data — both method-local scratch and long-lived objects — lived in one undifferentiated memory pool, you would need a GC smart enough to track the lifetime of every `int i = 0` loop variable alongside a multi-megabyte `HashMap`. Memory would never be reclaimed promptly; performance would collapse.

**THE BREAKING POINT:** A production service throws `java.lang.OutOfMemoryError: Java heap space` at 3 AM. The on-call engineer has no mental model of where objects live, which GC generation they occupy, or which `-XX` flag controls the limit. They restart the pod — and the OOM returns 45 minutes later.

**THE INVENTION MOMENT:** The JVM separates memory into purpose-built regions: a thread-local stack for cheap, automatic method-frame management, and a GC-managed heap for object lifetimes. Each region has exactly the right lifetime semantics for its occupants — stacks pop on method return; the heap persists until no references remain.

---

### 📘 Textbook Definition

**Java memory management** refers to the JVM's strategy for allocating, organising, and reclaiming memory during program execution. The JVM divides memory into: the **Java Heap** (all object instances, GC-managed, shared across threads), the **Stack** (per-thread, holds method frames containing local variables and operand stacks), the **Metaspace** (class metadata, native memory, replaces PermGen since Java 8), and **Native Memory** (JVM internals, off-heap buffers). The GC reclaims heap memory; stacks are reclaimed automatically on method return.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Stack = fast, per-thread scratch pad; Heap = shared object warehouse managed by GC.

> The stack is a pile of sticky notes on your desk — you use one per task and throw it away when done. The heap is a shared warehouse — things stay until no one needs them anymore.

**One insight:** Most `OutOfMemoryError` variants map to a specific memory region. Knowing which region tells you exactly which flag to tune and which tool to use to diagnose it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Local primitive variables and object references (not the objects themselves) live on the stack.
2. All object instances, regardless of where they are created, live on the heap.
3. A stack frame is created on method entry and destroyed on method return — automatically, no GC needed.
4. The heap is shared; the stack is private to each thread.
5. The JVM can allocate small, non-escaping objects on the stack via **escape analysis** — an optimisation, not a guarantee.

**DERIVED DESIGN:**
- Heap is split into Young Generation (Eden + Survivor spaces) and Old Generation to exploit the *weak generational hypothesis* — most objects die young.
- Thread Local Allocation Buffers (TLAB) allow each thread to allocate into Eden without synchronisation.
- Metaspace (native memory) holds class bytecode, method metadata, and interned strings.
- Off-heap (`ByteBuffer.allocateDirect`) is outside the GC entirely — fast, but requires manual lifecycle management.

**THE TRADE-OFFS:**
**Gain:** Stack allocation is orders of magnitude faster than heap allocation; GC only runs over heap, not stack.
**Cost:** Heap objects have GC overhead — pauses, write barriers, and card tables. Large heaps amplify GC cost.

---

### 🧪 Thought Experiment

**SETUP:** Your service creates a `List<Order>` inside a method, adds 1,000 `Order` objects, processes them, and returns. Do these objects live on the stack or the heap?

**WHAT HAPPENS WITHOUT UNDERSTANDING THIS:** You assume local variables are "on the stack" and think they are cheap. You allocate millions of short-lived objects per second without batching or pooling, triggering constant Minor GCs. Tail latency spikes to 50 ms under load.

**WHAT HAPPENS WITH UNDERSTANDING THIS:** You know `List` and `Order` instances live on the heap. You recognise they are short-lived (die before next GC cycle) and will be collected in Eden. You instrument with `jstat -gcutil` to verify Eden fill rate, and if needed, pre-size the list with `new ArrayList<>(1024)` to avoid internal array reallocations.

**THE INSIGHT:** "Local variable" does not mean "on the stack." Only primitive types and object references (4–8 bytes each) are on the stack. The objects they point to are always on the heap.

---

### 🧠 Mental Model / Analogy

> The stack is a whiteboard next to your desk — erased after each meeting (method call). The heap is a shared storage room — items persist until explicitly no longer needed by anyone in the office.

- **Whiteboard (stack)** → per-thread method frames, local variables
- **Storage room (heap)** → all object instances
- **Item tag with no owner** → unreachable object, eligible for GC
- **Facility manager (GC)** → periodically visits storage room, discards untagged items
- **Storage room overflow** → `OutOfMemoryError: Java heap space`

Where this analogy breaks down: unlike a real storage room, the heap has generational structure (Eden/Survivor/Old) and the GC does not always visit the entire heap at once.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your Java program runs, variables used inside a method live in a fast scratch area (stack). Objects you create with `new` live in a big shared area (heap). When no one uses an object anymore, the garbage collector cleans it up.

**Level 2 — How to use it (junior developer):**
Tune heap size with `-Xms` (initial) and `-Xmx` (max). Set stack size with `-Xss`. Check GC activity with `jstat -gcutil <pid> 1000`. If you see `FGCT` growing, you have too many long-lived objects or a memory leak. Use `jmap -heap <pid>` to see generation fill levels.

**Level 3 — How it works (mid-level engineer):**
Eden fills as objects are allocated via TLAB. A Minor GC copies surviving objects to a Survivor space, incrementing their age counter. Objects reaching tenure threshold (`-XX:MaxTenuringThreshold`, default 15 for G1) are promoted to Old Gen. A Full GC (or G1 Mixed GC) reclaims Old Gen — this is where GC pause time spikes. Metaspace grows as classes are loaded; class leaks (common with dynamic classloaders) exhaust it.

**Level 4 — Why it was designed this way (senior/staff):**
The generational hypothesis drives the heap layout: empirically, 80–95% of objects die in the first Minor GC cycle. By keeping Eden small (100–500 MB) and evacuating survivors frequently, most garbage is collected cheaply in Minor GC without touching Old Gen. G1 further improves this by dividing the heap into equal-sized regions and selecting the most garbage-dense ones for collection — maximising reclaimed bytes per pause millisecond. ZGC and Shenandoah push further: they reclaim memory concurrently, keeping pause times under 1 ms regardless of heap size.

---

### ⚙️ How It Works (Mechanism)

```
  Thread 1              Thread 2
  ┌──────────┐          ┌──────────┐
  │  Stack   │          │  Stack   │
  │  Frame N │          │  Frame N │
  │  Frame 1 │          │  Frame 1 │
  └────┬─────┘          └────┬─────┘
       │  references         │  references
       ▼                     ▼
  ┌─────────────────────────────────┐
  │           HEAP                  │
  │  ┌───────────────────────────┐  │
  │  │  Young Generation         │  │
  │  │  [Eden][S0][S1]           │  │
  │  └───────────────────────────┘  │
  │  ┌───────────────────────────┐  │
  │  │  Old (Tenured) Generation │  │
  │  └───────────────────────────┘  │
  └─────────────────────────────────┘
  ┌─────────────────────────────────┐
  │  Metaspace (native memory)      │
  │  [Class metadata][Interned str] │
  └─────────────────────────────────┘
```

New objects go to Eden (via TLAB). Minor GC copies survivors to S0/S1. Old enough survivors are promoted to Old Gen. GC reclaims unreachable objects.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
  new Order()  called by Thread-1
    │
    ▼  Thread-1 TLAB has space
  Object allocated in Eden        ← YOU ARE HERE
    │
    ▼  Order used, method returns
  Order reference goes out of scope
    │
    ▼  Eden fills → Minor GC triggered
  Live objects copied to Survivor-0
  Order (unreachable) is collected
    │
    ▼  Objects surviving N GCs
  Promoted to Old Generation
    │
    ▼  Old Gen fills → G1 Mixed GC
  Old Gen regions collected
```

**FAILURE PATH:**
- Eden allocation fails (TLAB exhausted, no space) → Minor GC triggered.
- Minor GC cannot free enough space → objects promoted to Old Gen.
- Old Gen fills → Full GC / G1 Mixed GC triggered.
- GC cannot reclaim enough → `OutOfMemoryError: Java heap space`.

**WHAT CHANGES AT SCALE:**
At high allocation rates (>1 GB/s), Eden fills in milliseconds. GC frequency increases, competing with application threads for CPU. Each GC pause adds tail latency. At scale, tune `-Xmx`, GC algorithm, and Eden size (`-XX:NewRatio`), and audit for allocation hotspots with async-profiler.

---

### 💻 Code Example

```java
// BAD — unbounded heap growth via static collection
public class MetricCache {
    // Static = lives for JVM lifetime
    private static final Map<String, List<Double>>
        metrics = new HashMap<>();

    public void record(String key, double val) {
        metrics.computeIfAbsent(
            key, k -> new ArrayList<>()).add(val);
        // LIST GROWS FOREVER — memory leak
    }
}
```

```java
// GOOD — bounded cache with eviction policy
public class MetricCache {
    private final Map<String, Double> metrics;

    public MetricCache(int maxEntries) {
        // LinkedHashMap with access-order eviction
        this.metrics = Collections.synchronizedMap(
            new LinkedHashMap<>(maxEntries, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(
                        Map.Entry<String, Double> e) {
                    return size() > maxEntries;
                }
            });
    }

    public void record(String key, double val) {
        metrics.put(key, val);
    }
}
```

```java
// Diagnosing heap usage at runtime
// Print GC stats every second
// $ jstat -gcutil <pid> 1000
//
// Heap regions: S0    S1    E     O     M
//               0.00  25.4  68.2  41.3  97.1
// E (Eden) near 100 → frequent Minor GC
// O (Old)  near 100 → risk of Full GC

// Force heap histogram (safe on live JVM)
// $ jcmd <pid> GC.heap_info
// $ jmap -histo:live <pid> | head -30
```

---

### ⚖️ Comparison Table

| Memory Region | Lifetime | Thread-Safety | Managed By | OOM Error Type |
|---|---|---|---|---|
| Stack | Method scope | Per-thread; no sharing | JVM (auto-pop) | `StackOverflowError` |
| Heap (Young) | Until GC | Shared; GC write barriers | GC (Minor GC) | `heap space` |
| Heap (Old) | Until GC | Shared | GC (Major/Mixed GC) | `heap space` |
| Metaspace | Class lifetime | Shared | JVM/GC (class unload) | `Metaspace` |
| Off-heap | Manual | Manual | Application code | Native OOM |

---

### 🔁 Flow / Lifecycle

```
  [Object created in Eden]
      │
      ▼  Eden fills
  [Minor GC — copy-collect]
      │ live? ──no──▶ [Collected — freed]
      │ yes
      ▼
  [Survivor space, age++]
      │
      ▼  age >= threshold
  [Promoted to Old Gen]
      │
      ▼  Old Gen fills
  [G1 Mixed GC / Full GC]
      │ reachable? ──no──▶ [Collected]
      │ yes
      ▼
  [Object lives in Old Gen]
      │
      ▼  no remaining references
  [Collected on next GC cycle]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Local variables are on the stack" | Primitive local variables are on the stack. Object *references* are on the stack. The *objects* they point to are always on the heap (unless escape analysis allocates on stack). |
| "Setting a variable to null frees memory immediately" | Setting to `null` removes a reference; memory is freed only at the next GC cycle that reclaims the object. |
| "A bigger heap means faster performance" | Bigger heaps delay Full GC but make each Full GC pause longer. Over-provisioning can worsen tail latency. |
| "PermGen and Metaspace are the same" | PermGen was fixed-size heap memory (Java ≤7), causing `OutOfMemoryError: PermGen`. Metaspace (Java 8+) is native memory and grows dynamically — but can still OOM if capped with `-XX:MaxMetaspaceSize`. |
| "Off-heap avoids all memory problems" | Off-heap bypasses GC overhead but requires manual deallocation. Failure to call `Cleaner` or `release()` leaks native memory — harder to diagnose than heap leaks. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `OutOfMemoryError: Java heap space`**
**Symptom:** JVM crashes with heap OOM; GC log shows back-to-back Full GCs reclaiming near-zero bytes.
**Root Cause:** Either heap is undersized, or there is a memory leak (unreleased references, growing static collections, cache without eviction).
**Diagnostic:**
```bash
# Capture heap dump on OOM (add to JVM flags)
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/heap.hprof

# Analyse immediately after crash
jmap -histo:live <pid> | head -40
# Look for unexpectedly large instance counts
```
**Fix:** If legitimate growth: increase `-Xmx`. If leak: find the retaining reference chain in the heap dump (use Eclipse MAT or IntelliJ heap analyser).
**Prevention:** Set `-XX:+HeapDumpOnOutOfMemoryError` in all production JVMs. Monitor Old Gen fill with Prometheus JMX exporter.

**Mode 2: `OutOfMemoryError: Metaspace`**
**Symptom:** OOM specifically for Metaspace; class count keeps growing over hours.
**Root Cause:** Dynamic classloading (Groovy scripts, JDBC drivers re-registered, hot-reload frameworks) leaks classloaders. Each leaked classloader holds a reference to all its loaded classes.
**Diagnostic:**
```bash
jcmd <pid> VM.classloader_stats | grep "classes"
# Growing class count over time = classloader leak

jstat -gcmetacapacity <pid> 5000
# Watch MCMX (max) vs MC (current)
```
**Fix:** Find the retained `ClassLoader` reference in a heap dump. Common culprits: thread-local variables, static fields in web apps.
**Prevention:** Set `-XX:MaxMetaspaceSize=256m` to get a fast OOM instead of slow native memory exhaustion.

**Mode 3: `StackOverflowError`**
**Symptom:** `StackOverflowError` with a stacktrace showing thousands of repeated frames.
**Root Cause:** Unbounded recursion — missing or incorrect base case, circular object graph traversal.
**Diagnostic:**
```bash
jstack <pid> | head -100
# Count repeated frame depth to estimate stack depth
# Default stack size: 512k (client) / 1MB (server)
```
**Fix:** Convert recursion to iteration, or increase stack size with `-Xss2m` (verify recursion is truly intentional first).
**Prevention:** Unit-test recursive algorithms with depth limits. Add a `depth` parameter to recursive methods and throw early.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- JVM — the overall runtime architecture
- Garbage Collection (GC) — how the heap is reclaimed
- Stack vs Heap — fundamental memory model concepts

**Builds On This (learn these next):**
- Java Performance Tuning — applying memory knowledge to reduce latency
- Java Profiling (YourKit, JFR) — tools to observe memory behaviour at runtime
- GC Tuning — deep-diving GC algorithm selection and knobs

**Alternatives / Comparisons:**
- Off-heap (`ByteBuffer.allocateDirect`) — manual lifecycle, GC-free, for high-throughput I/O
- GraalVM Native Image — AOT compilation, no JVM heap warmup, fixed native memory layout
- Project Panama (Java 22+) — structured foreign memory API replacing `sun.misc.Unsafe`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    JVM memory split: stack & heap     │
│ PROBLEM SOLVED Lifetime-matched storage regions  │
│ KEY INSIGHT   Objects are ALWAYS on the heap     │
│ USE WHEN      Diagnosing OOM or GC pressure      │
│ AVOID WHEN    — (foundational knowledge)         │
│ TRADE-OFF     Heap GC overhead vs stack speed    │
│ ONE-LINER     Stack = frames; Heap = objects     │
│ NEXT EXPLORE  GC Tuning, Java Profiling, JFR     │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(B — Scale)** At 500k object allocations per second, Eden fills in roughly 200 ms (assuming 256 MB Eden and 500-byte average object). How does increasing `-Xmx` without increasing Eden size affect Minor GC frequency, and what flag controls the Eden-to-Old ratio?

2. **(D — Root Cause)** A service runs for 4 hours without OOM, then crashes with `OutOfMemoryError: Java heap space`. The heap dump shows 2.8 GB of `byte[]` instances held by a `ThreadLocal<byte[]>` field. What object lifecycle event failed to occur, and how would you prevent it in a thread-pool-based server?

3. **(C — Design Trade-off)** Off-heap (`ByteBuffer.allocateDirect`) bypasses GC entirely, making it attractive for large caches. What are the two primary risks of off-heap allocation that do NOT exist with on-heap objects, and under what production conditions do those risks outweigh the GC-avoidance benefit?
