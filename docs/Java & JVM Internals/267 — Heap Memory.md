---
layout: default
title: "Heap Memory"
parent: "Java & JVM Internals"
nav_order: 267
permalink: /java/heap-memory/
number: "0267"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: JVM, Stack Memory, Memory Management Models
used_by: Young Generation, Old Generation, GC Roots, Minor GC, Major GC
related: Stack Memory, Metaspace, GC Roots, Young Generation
tags:
  - java
  - jvm
  - memory
  - gc
  - intermediate
---

# 267 — Heap Memory

⚡ TL;DR — The JVM heap is the single shared memory region where all Java objects live, managed automatically by the garbage collector.

| #267 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Stack Memory, Memory Management Models | |
| **Used by:** | Young Generation, Old Generation, GC Roots, Minor GC, Major GC | |
| **Related:** | Stack Memory, Metaspace, GC Roots, Young Generation | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
In C, you call `malloc()` to allocate memory and `free()` to release it. Forget to call `free()` and you have a memory leak that slowly grows until the process dies. Call `free()` twice and you corrupt memory, causing crashes that only manifest hours later in an unrelated part of the code. In large C++ codebases, memory bugs are the leading source of security vulnerabilities and production outages — requiring years of expertise to track down.

THE BREAKING POINT:
In 1995, Sun had to make Java accessible to millions of developers who were not memory management experts. Requiring `malloc`/`free` semantics from Java developers would have made Java as error-prone as C. The language needed automatic memory management as a first-class feature.

THE INVENTION MOMENT:
By centralising all object allocation in one managed region — the heap — and appointing the GC as the sole arbiter of memory reclamation, Java eliminated an entire class of memory Safety bugs. This is exactly why the JVM heap was designed: automatic, safe, managed memory for all Java objects.

### 📘 Textbook Definition

The JVM heap is a runtime data area shared among all threads, from which memory is allocated for all object instances and arrays. It is created at JVM startup (sized between `-Xms` and `-Xmx`) and managed by the garbage collector, which periodically identifies and reclaims memory occupied by unreachable objects. The JVM heap is divided into generational regions (Young Generation and Old Generation) in most collectors, based on the empirical observation that most objects die young. Heap exhaustion causes `java.lang.OutOfMemoryError: Java heap space`.

### ⏱️ Understand It in 30 Seconds

**One line:**
The heap is the JVM's memory pool where all objects live, managed automatically so you never call free().

**One analogy:**
> The heap is like a self-cleaning hotel. Guests (objects) check in (allocated via `new`). The hotel manager (GC) periodically checks which rooms are still occupied. Empty rooms (unreachable objects) are automatically cleaned and made available for new guests. You never need to check out manually.

**One insight:**
The heap's performance secret is generational collection: most objects die young (within milliseconds of creation), so the GC focuses most of its effort on a small region (Young Generation). Surviving old objects are promoted to a separate region and collected less frequently — making GC extraordinarily efficient for typical allocation patterns.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Every Java object instance and array lives on the heap — no exceptions.
2. Memory is reclaimed when an object has no live references — not when the last reference goes out of scope.
3. The GC is the sole agent of reclamation — the programmer cannot explicitly free heap memory.

DERIVED DESIGN:
Invariant 1 requires a single shared memory pool. Invariant 2 means reclamation requires tracing reachability from roots — a GC, not reference counting. Invariant 3 means the GC's pause behaviour and tuning parameters directly affect application latency. The generational hypothesis (most objects die young) motivates splitting the heap into regions with different collection frequencies and algorithms.

THE TRADE-OFFS:
Gain: No manual memory management, no use-after-free, no double-free bugs, thread-safe allocation via TLAB.
Cost: GC pauses that increase with heap size; memory overhead for object headers; peak live-set must fit in `-Xmx`.

### 🧪 Thought Experiment

SETUP:
A Java web service handles 1000 requests per second. Each request creates ~100 short-lived objects (request/response DTOs, intermediate computation objects). The service also maintains a cache of 1000 permanent objects.

WHAT HAPPENS WITHOUT GENERATIONAL HEAP:
A single flat heap collects everything together. The GC scans all 1000 cache objects and all 100,000 short-lived request objects on every collection cycle. The cache objects are alive; the request objects are dead. 99% of scan time is spent confirming live objects are live. For 1000 dead request objects and 1000 live cache objects = 50% wasted work.

WHAT HAPPENS WITH GENERATIONAL HEAP:
Short-lived request objects are created in Eden (Young Generation). Minor GC runs every few hundred milliseconds, scanning only Eden (tiny region). It finds 99% of request objects are already dead — reclaims them in <10ms. The 1000 cache objects were promoted to Old Generation long ago and are only scanned during Major GC (rare — perhaps every 10 minutes). The work matches the object lifetime distribution.

THE INSIGHT:
Matching the memory management strategy to the observed lifetime distribution of objects — most die young, few live long — makes garbage collection practical for real applications.

### 🧠 Mental Model / Analogy

> The heap is like a city's recycling system. New objects are created in a small "intake depot" (Eden). Most objects are discarded quickly (short-lived garbage). The recycling truck (minor GC) clears the depot frequently and cheaply. Objects that survive many clearings get moved to long-term storage (Old Generation). A full city cleanout (major GC) happens rarely and is more disruptive.

"Intake depot" → Eden (Young Generation)
"Objects discarded quickly" → short-lived objects collected in minor GC
"Recycling truck" → garbage collector (minor GC)
"Long-term storage" → Old Generation
"Full city cleanout" → major/full GC cycle

Where this analogy breaks down: the GC doesn't "know" an object is garbage — it discovers it by proving no live reference reaches it. The object isn't flagged for disposal; it simply becomes unreachable.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your Java program creates objects with `new`, they live in a memory area called the heap. The JVM automatically finds and removes objects you no longer use, so you never have to worry about "cleaning up" memory yourself.

**Level 2 — How to use it (junior developer):**
Set heap size with `-Xmx` (maximum) and `-Xms` (initial). If you get `OutOfMemoryError: Java heap space`, your heap is too small or you have a memory leak. Tools: jstat, VisualVM, and heap dumps processed with Eclipse MAT. Don't hold references to large objects longer than needed — this prevents GC from reclaiming them.

**Level 3 — How it works (mid-level engineer):**
The heap is divided into Young Generation (Eden + Survivor S0 and S1) and Old Generation (Tenured). New objects go to Eden. When Eden fills, Minor GC runs: live objects move to a Survivor space; survivors beyond a threshold age are promoted to Old Generation. Old Generation fills slowly and triggers Major or Full GC (more expensive). Thread-Local Allocation Buffers (TLABs) give each thread a private slice of Eden for lock-free allocation.

**Level 4 — Why it was designed this way (senior/staff):**
The generational hypothesis is empirically validated for most programs but not universal (e.g., large in-memory caches skip the young generation entirely and pressure the old generation directly). Modern low-pause collectors (G1GC, ZGC, Shenandoah) reduce but don't eliminate pause times by doing GC work concurrently with the application. ZGC achieves <1ms pauses even for terabyte heaps by using load barriers — every object reference access is intercepted to check if the object needs to be moved. The trade-off is CPU overhead (load barriers) for pause time.

### ⚙️ How It Works (Mechanism)

**Heap Structure (Generational):**

```
┌─────────────────────────────────────────────┐
│              JVM HEAP LAYOUT                │
├─────────────────────────────────────────────┤
│  Young Generation (default ~1/3 of heap)    │
│  ┌─────────────────────────────────────┐    │
│  │ Eden Space                          │    │
│  │ (new objects allocated here via new)│    │
│  ├─────────────────────────────────────┤    │
│  │ Survivor Space S0 (From)            │    │
│  ├─────────────────────────────────────┤    │
│  │ Survivor Space S1 (To)              │    │
│  └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│  Old Generation (Tenured)                   │
│  (promoted objects that survived N GC cycles│
│   in Young Gen — default age threshold: 15) │
└─────────────────────────────────────────────┘
```

**Object Allocation Flow:**
1. `new MyObject()` → JVM checks TLAB (thread-local Eden slice). If space available, allocate lock-free by pointer bump.
2. TLAB full → acquire new TLAB from Eden. If Eden full → trigger Minor GC.
3. Minor GC: copy live objects from Eden + From-Survivor to To-Survivor. Dead objects in Eden just become garbage in place. Swap S0/S1 roles.
4. Objects surviving 15 Minor GCs → promoted to Old Generation.
5. Old Generation full → Major or Full GC (depends on collector).

**Object Header:**
Every JVM object has a header (8–16 bytes before the fields):
- Mark Word: identity hash code, GC age, lock state, biased locking info
- Class Pointer: reference to the class metadata in Metaspace

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Application calls new MyObject()
  → TLAB allocation (fast path) ← YOU ARE HERE
  → Object header written + fields initialised
  → Reference returned to caller (stack / other object)
  → Object used, eventually last reference dropped
  → Minor GC finds no path from GC Roots to object
  → Object's Eden space overwritten by next allocation
  → No explicit free — GC handled it
```

FAILURE PATH:
```
Eden full → Minor GC runs
  → Old Gen full → Major GC runs
  → Major GC cannot reclaim enough
  → OutOfMemoryError: Java heap space
  → Application dies
  → Diagnosis: heap dump → Eclipse MAT
    → find largest retained objects
```

WHAT CHANGES AT SCALE:
At 10x load, object allocation rate increases 10x, filling Eden faster and triggering more frequent Minor GCs. At 100x, if the Old Generation holds a large cache, major GC pauses become a latency problem. At 1000x (terabyte heaps), only low-pause collectors like ZGC remain viable; traditional stop-the-world GC would pause the application for minutes.

### 💻 Code Example

Example 1 — Configure heap sizes:
```bash
# BAD: Default heap too small for production
java -jar myapp.jar

# GOOD: Set initial and max heap explicitly
java -Xms512m -Xmx2g -XX:+UseG1GC -jar myapp.jar

# BEST (explicit settings for containers):
java -Xms512m -Xmx1g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:+HeapDumpOnOutOfMemoryError \
     -jar myapp.jar
```

Example 2 — Monitor heap usage live:
```bash
# GC statistics every 2 seconds: heap after GC
jstat -gc <pid> 2000
# Columns: S0C S1C S0U S1U EC EU OC OU ...
# EU = Eden Utilization, OC = Old Capacity

# Heap histogram (lightweight - no full dump)
jcmd <pid> GC.class_histogram | head -30
```

Example 3 — Capture and analyse heap dump:
```bash
# Capture heap dump on demand
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Or on OOM automatically:
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/ -jar myapp.jar

# Analyse with Eclipse MAT or JVM heap analyser
# Look for: "Leak Suspects Report"
```

Example 4 — Avoid heap pressure with object pooling:
```java
// BAD: creates a new ByteBuffer per request
// (large objects pressure Old Gen)
public Response handle(Request req) {
    ByteBuffer buf = ByteBuffer.allocate(64 * 1024);
    // ... process ...
    return serialize(buf);
}

// GOOD: use a pool via Apache Commons Pool2
ObjectPool<ByteBuffer> bufPool =
    new GenericObjectPool<>(new ByteBufferFactory());

public Response handle(Request req) throws Exception {
    ByteBuffer buf = bufPool.borrowObject();
    try {
        return serialize(buf);
    } finally {
        buf.clear();
        bufPool.returnObject(buf);
    }
}
```

### ⚖️ Comparison Table

| GC / Heap Config | Pause Time | Throughput | Memory Overhead | Best For |
|---|---|---|---|---|
| Serial GC (-XX:+UseSerialGC) | Long | High | Lowest | Single-CPU, embedded |
| Parallel GC (-XX:+UseParallelGC) | Medium | Highest | Low | Batch jobs, throughput-focused |
| **G1GC (-XX:+UseG1GC)** | Predictable (tunable) | High | Medium | General purpose (Java 9+ default) |
| ZGC (-XX:+UseZGC) | <1ms even at TB heap | Medium | Higher | Low latency, large heaps |
| Shenandoah GC | <10ms | Medium | Higher | Low latency, medium heaps |

How to choose: G1GC is the right default for most production services. Use ZGC when you have terabyte heaps or strict latency SLAs (<1ms GC pause). Use Parallel GC for batch analytics jobs maximising throughput over latency.

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────────┐
│           HEAP OBJECT LIFECYCLE             │
├─────────────────────────────────────────────┤
│  1. new Object() → Eden allocation          │
│     ↓                                       │
│  2. Eden fills → Minor GC                   │
│     ├─ object unreachable → RECLAIMED       │
│     └─ object live → Survivor S1            │
│     ↓                                       │
│  3. Object survives multiple Minor GCs      │
│     (age increments each surviving GC)      │
│     ↓                                       │
│  4. Age ≥ MaxTenuringThreshold (default 15) │
│     → Promoted to Old Generation            │
│     ↓                                       │
│  5. Old Gen fills → Major/Full GC           │
│     ├─ object unreachable → RECLAIMED       │
│     └─ object live → stays in Old Gen       │
└─────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Setting -Xmx higher is always better" | Larger heap → longer GC pause times. Best heap size is the smallest that avoids frequent GC pressure. Profile to find it. |
| "Objects are freed when the last reference goes out of scope" | Objects are freed when GC runs AND the object is unreachable. GC timing is non-deterministic. |
| "The heap is one big flat memory block" | Modern GCs (G1GC, ZGC) divide the heap into many small regions with different roles. The flat Young/Old model is a simplification. |
| "Heap dumps capture everything including stack" | Heap dumps capture objects on the heap only. Stack frames, JIT-compiled code, and class metadata are not in a heap dump. |
| "Full GC always indicates a problem" | Not always — Full GC can be triggered explicitly (System.gc()) or by normal promotion. It's a concern only if it occurs frequently or takes too long. |

### 🚨 Failure Modes & Diagnosis

**1. OutOfMemoryError: Java heap space**

Symptom: `java.lang.OutOfMemoryError: Java heap space`; GC logs show repeated back-to-back GC cycles with no memory freed (>95% of time spent GC'ing means `java.lang.OutOfMemoryError: GC overhead limit exceeded`).

Root Cause: Live object set exceeds `-Xmx`, either from object leak (references held too long) or genuinely insufficient heap for the workload.

Diagnostic:
```bash
# Check GC activity
jstat -gcutil <pid> 1000
# If OU (Old Utilization) is 95%+ and rising → leak

# Capture heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# Open with Eclipse MAT → Leak Suspects Report
```

Prevention: Enable `-XX:+HeapDumpOnOutOfMemoryError` in all production deployments. Review large `Map` and `List` objects held as static or long-lived fields.

**2. Long GC Pause Causing Latency Spikes**

Symptom: Request latencies spike periodically (e.g., 99th percentile spikes to 5+ seconds); GC logs show stop-the-world pauses correlating with latency spikes.

Root Cause: Full GC triggered by Old Generation filling up, pausing all application threads.

Diagnostic:
```bash
# Enable GC logging (Java 17+)
java -Xlog:gc*:file=/var/log/gc.log:time,level,tags \
     -jar myapp.jar

# Analyse GC pause times
grep "Pause Full" /var/log/gc.log
grep "Pause Young" /var/log/gc.log
```

Fix:
```bash
# Switch from Parallel GC to G1GC/ZGC
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -jar myapp.jar
# Or for <1ms target:
java -XX:+UseZGC -jar myapp.jar
```

Prevention: Profile object allocation rates with async-profiler; size the heap appropriately to avoid frequent Old Gen collections.

**3. Heap Memory Leak (Retention via Collections)**

Symptom: Memory usage grows unbounded over hours/days; heap dump shows one large `HashMap` or `ArrayList` holding millions of entries.

Root Cause: Objects added to a collection but never removed; common patterns: unbounded caches, event listeners not deregistered, session maps without expiry.

Diagnostic:
```bash
# Heap histogram - find the large collection
jcmd <pid> GC.class_histogram | grep -E \
  "HashMap|ArrayList|ConcurrentHashMap" | head -10

# Heap dump → Eclipse MAT → "Dominator Tree"
# shows which objects retain the most memory
```

Prevention: Use bounded caches (Caffeine, Guava Cache with `maximumSize`); use `WeakReference` for event listeners; monitor heap growth trend with Prometheus/Micrometer.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — the runtime that creates and manages the heap
- `Stack Memory` — the complementary per-thread memory region; understanding the contrast clarifies heap's role
- `Memory Management Models` — contrast with C's manual malloc/free; the heap is Java's answer to automatic management

**Builds On This (learn these next):**
- `Young Generation` — the heap sub-region for newly created objects; deeply connected to Minor GC
- `GC Roots` — the starting points from which the GC determines heap object reachability
- `Minor GC` — the frequent collection of the Young Generation portion of the heap
- `G1GC` — the default GC algorithm managing heap regions in modern Java (Java 9+)

**Alternatives / Comparisons:**
- `Stack Memory` — per-thread, no GC, faster, but limited to scope-bounded data
- `Metaspace` — stores class metadata; native memory, not part of the Java heap
- `Off-heap` — explicit memory outside the JVM heap, used for large datasets avoiding GC (e.g., Netty, Ehcache)

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared JVM memory region for all objects, │
│              │ managed by the garbage collector          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual malloc/free leads to leaks and     │
│ SOLVES       │ corruption; heap + GC eliminates both     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Generational collection (most objects die │
│              │ young) makes GC practical — Minor GC is   │
│              │ fast because most of Eden is garbage      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every Java program — all objects live     │
│              │ on the heap automatically                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data too large for GC (use off-heap       │
│              │ ByteBuffer / direct memory instead)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No manual memory management vs GC pauses  │
│              │ that increase with heap size              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The heap is a self-cleaning hotel —      │
│              │ check in freely, the manager handles      │
│              │ checkout automatically"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Young Generation → GC Roots → G1GC        │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A Java microservice processes financial transactions and keeps a `HashMap<String, Transaction>` as an in-memory cache. Over 24 hours, heap usage grows from 200 MB to 1.8 GB and triggers OOM. The cache has no size limit. Trace step by step: which generation does this HashMap occupy, why doesn't Minor GC reclaim it, and what specific changes to the code would prevent the memory leak?

**Q2.** At 10 million live heap objects and `-Xmx8g`, Major GC takes 4 seconds (stop-the-world). The SLA requires 99th percentile latency under 200ms. Migrating from G1GC to ZGC claims to reduce max pause to <1ms at the cost of 10% CPU overhead. Given your heap size and object count, explain WHAT ZGC does differently from G1GC during the pause phase, and why the 10% CPU overhead is a worthwhile trade-off for latency-sensitive services.

