---
layout: default
title: "GC Roots"
parent: "Java & JVM Internals"
nav_order: 276
permalink: /java/gc-roots/
number: "0276"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Heap Memory, Class Loader, Stack Memory, Thread
used_by: Minor GC, Major GC, Reference Types, Stop-The-World
related: Heap Memory, Reference Types, Young Generation, GC Pause
tags:
  - java
  - jvm
  - gc
  - memory
  - internals
  - deep-dive
---

# 276 — GC Roots

⚡ TL;DR — GC Roots are the entry points from which the garbage collector traces object reachability — any object not reachable from a GC root is eligible for collection.

| #276 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, Class Loader, Stack Memory, Thread | |
| **Used by:** | Minor GC, Major GC, Reference Types, Stop-The-World | |
| **Related:** | Heap Memory, Reference Types, Young Generation, GC Pause | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
To reclaim unreachable objects, the GC must distinguish live objects from dead ones. The naive approach — reference counting — tracks how many pointers point to each object. When the count drops to 0, the object is dead. But reference counting fails with circular references: Object A holds a reference to Object B, Object B holds a reference to Object A, both have a reference count of 1, but neither is reachable from your program. Circular references cause permanent memory leaks in pure reference-counting systems (Python 2's GC spent enormous effort on cycle detection for this reason).

**THE BREAKING POINT:**
Java programs frequently create circular structures: doubly linked lists, bidirectional object graphs, parent-child relationships. A reference counting GC would require explicit cycle detection for all of these, adding complexity and overhead to every allocation and pointer update.

**THE INVENTION MOMENT:**
Tracing GC from a set of known live starting points — GC Roots — eliminates the circular reference problem entirely. If an object cannot be reached by following any chain of references starting from a GC Root, it is dead — regardless of how many other objects point to it. This is exactly why GC Roots exist: they define the set of definitively-alive objects that everything else must be connected to.

---

### 📘 Textbook Definition

GC Roots are the initial set of object references that the JVM's garbage collector uses as starting points for the reachability analysis that determines which heap objects are live. An object is "live" (not collectible) if and only if there exists a path of references from at least one GC Root to the object. The primary categories of GC Roots in HotSpot JVM are: local variables and method parameters on active thread stacks, static fields of loaded classes (stored in Metaspace), active Java threads themselves (thread objects are roots), references held by JNI (Java Native Interface) code, and synchronisation monitor objects.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GC Roots are the "live anchors" — any object attached to one survives; everything else is garbage.

**One analogy:**
> A city power grid has substations (GC Roots) that feed electricity to buildings (heap objects) via wires (references). Any building connected through any chain of wires to a substation has power. Any building completely disconnected from all substations is dark and unused. The city decommissions disconnected buildings. The GC does the same to disconnected objects.

**One insight:**
The real-world impact of GC Roots is memory leaks. The most common Java memory leak is NOT a reference counting problem — it is an object that IS reachable from a GC Root but shouldn't be. A forgotten entry in a static `Map`, an event listener never removed, a ThreadLocal not cleaned up — all these keep objects "alive" via GC Root connectivity even when the programmer considers them "unused." Memory leaks in Java = unintended GC Root connectivity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Reachability from a known live root defines liveness — transitively.
2. GC Roots are objects definitively live because the JVM needs them: thread stacks, static state, native references.
3. Any object not transitively reachable from at least one GC Root is definitively dead.

**DERIVED DESIGN:**
Invariant 1 enables tracing GC algorithms (mark-sweep, mark-compact, copy). Invariant 2 defines the root set: stack frames (active methods need their locals), class metadata with statics (always needed while the class is loaded), active threads (thread objects are live while running), and JNI references (native code holds live references). Invariant 3 is the correctness guarantee — no reachable object is ever collected.

**THE TRADE-OFFS:**
**Gain:** Handles circular references correctly; no per-object reference count overhead on pointer updates; simple correctness argument.
**Cost:** Requires global heap tracing (touching all live objects) — pause time proportional to live object set; requires "stop the world" at some phase (or sophisticated concurrent tracing with write barriers).

---

### 🧪 Thought Experiment

**SETUP:**
Three objects: Node A (held in a local variable), Node B (referenced by A), Node C (referenced by B and also by A). All form a triangle. Then the local variable is set to null.

**WHAT HAPPENS WITH REFERENCE COUNTING:**
Before null: A=1 ref (local), B=1 ref (from A), C=2 refs (from A and B). Set local = null. A→0 refs. A is collected. A's reference to B removed: B→0 refs. B collected. B's reference to C removed: C→1 ref (from A, but A was already collected). But wait — C still has 1 ref from the already-freed A? In practice, when A was collected, A's ref to C was decremented: C→0 refs → collected. Works! But: CIRCULAR: if A also had `A.self = A`, A's ref count would be 1 even after the local = null — never collected. Memory leak.

**WHAT HAPPENS WITH GC ROOTS TRACING:**
Before null: GC Root → local variable → A → {B, C} → C. All reachable. Set local = null. No GC Roots → A. GC traces from all roots, cannot reach A. Cannot reach B (only via A). C: check if reachable from any root — if only via A and B (both unreachable), C is also unreachable. All three collected, even if A had `A.self = A` — circular reference irrelevant, none reachable.

**THE INSIGHT:**
Root-based tracing means circular references are never a memory leak problem in tracing GC systems. Liveness is defined absolutely by root connectivity, not by relative reference counts.

---

### 🧠 Mental Model / Analogy

> GC Roots are like anchor points on a cave wall. Climbers (heap objects) are roped together (references). Any climber attached by an unbroken rope chain to an anchor point is safe (alive). Climbers with no rope path to any anchor, no matter how many other climbers they're tied to, are dangling in free fall (unreachable = collectable).

- "Anchor points in cave wall" → GC Roots (stack locals, static fields, JNI refs)
- "Climbers roped together" → heap objects with references between them
- "Unbroken rope to anchor" → reference chain from object to a GC Root
- "Dangling in free fall" → unreachable objects, eligible for GC
- "Rescue team" → GC collector reclaiming dangling climbers

Where this analogy breaks down: Unlike climbers, Java objects don't know they're unreachable — the GC determines this through the full traversal. Also, unlike climbers, "dangling" objects may have active reference counts > 0 (circular refs) but still be unreachable.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java's garbage collector periodically scans the heap to find and recycle unused objects. To know what's "unused," it starts from a small set of definitely-needed objects (GC Roots) — like variables your running code is holding — and follows all the references from there. Any object it can't reach is considered unused and gets recycled.

**Level 2 — How to use it (junior developer):**
Understanding GC Roots helps debug memory leaks. If heap usage grows unboundedly, it means objects are being kept alive (connected to GC Roots) unintentionally. Common causes: static collections (`static Map<> cache` that never removes entries), event listeners never deregistered, `ThreadLocal` values not cleaned up on thread return to pool. Solution: break the unintended GC Root connection.

**Level 3 — How it works (mid-level engineer):**
During GC's Mark phase, the collector begins with the GC Root set: all object references from thread stacks, JVM internal references, static fields in Metaspace, JNI global/local refs. It uses a work queue (grey objects) and marks objects as it traverses. When the queue is empty, all unmarked objects are garbage. For concurrent collectors (G1, ZGC), write barriers intercept pointer modifications during marking to ensure no concurrent modifications create missed reachable objects.

**Level 4 — Why it was designed this way (senior/staff):**
The GC Root enumeration is the most disruptive phase of GC because it requires knowing all stack variables across all threads — which requires either stopping all threads (stop-the-world) or using precise pointer tracking (OopMaps) tied to JIT-compiled code safepoints. OopMaps record, for every instruction in JIT-compiled code, which registers and stack slots contain object references (as opposed to integers). At a safepoint, the GC consults OopMaps to enumerate roots precisely. This tight coupling between the JIT and GC is one reason embedding a GC in a JIT-compiled system is extraordinarily complex — it drives much of the JVM's implementation complexity.

---

### ⚙️ How It Works (Mechanism)

**GC Root Categories:**

```
┌─────────────────────────────────────────────┐
│               GC ROOT TYPES                 │
├─────────────────────────────────────────────┤
│  1. Stack Locals (per thread)               │
│     - Local variables in active frames      │
│     - Method parameters in active frames    │
│     - Example: any method currently on the  │
│       call stack that holds an object ref   │
├─────────────────────────────────────────────┤
│  2. Static Fields (class statics)           │
│     - All static fields of all loaded       │
│       classes (stored in Metaspace)         │
│     - Persist as long as the class is loaded│
│     - Example: Logger.INSTANCE, Enum values │
├─────────────────────────────────────────────┤
│  3. Active Threads                          │
│     - Thread objects themselves are roots   │
│     - While thread is alive, its object     │
│       reference is a root                   │
├─────────────────────────────────────────────┤
│  4. JNI References                          │
│     - Global JNI refs from native code      │
│     - Local JNI refs in active JNI frames   │
│     - Used by C/C++ code calling Java       │
├─────────────────────────────────────────────┤
│  5. Synchronisation Monitors               │
│     - Objects being monitored (locked)      │
│     - Held as roots while locked           │
└─────────────────────────────────────────────┘
```

**Mark Phase (Tracing from Roots):**

```
┌─────────────────────────────────────────────┐
│       GC MARK PHASE (BFS traversal)         │
├─────────────────────────────────────────────┤
│  1. Add all GC Roots to work queue (grey)   │
│     ↓                                       │
│  2. Pop object from queue                   │
│     ↓                                       │
│  3. Mark object as LIVE (black)             │
│     ↓                                       │
│  4. For each reference field in object:     │
│     → if referent not yet marked: add       │
│       to work queue (grey)                  │
│     ↓                                       │
│  5. Repeat 2–4 until queue empty           │
│     ↓                                       │
│  6. All UNMARKED objects = GARBAGE          │
│     → collect in Sweep/Compact phase        │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Minor GC (Young Gen) triggered
  → All threads reach safepoint
  → GC enumerates GC Roots ← YOU ARE HERE
    (stack locals, statics, JNI refs, active threads)
  → Marks all objects reachable from roots in Young Gen
    (using card table for cross-generation refs)
  → Unmarked Eden/Survivor objects = garbage
  → Live objects copied to Survivor / promoted to Old Gen
  → Threads resume
```

**FAILURE PATH:**
```
StaticMap.cache grows indefinitely
  → Every new object added to static Map
  → Static field of loaded class = GC Root
  → All Map entries transitively reachable from root
  → GC cannot collect them (correctly!)
  → Heap grows → OOM
  → Diagnosis: heap dump → Dominator Tree
    → largest LiveSet is the static Map entries
```

**WHAT CHANGES AT SCALE:**
At terabyte heap scales, the live object set is enormous. Even though GC Roots are typically small (stack vars, statics), the live object graph can contain billions of objects. The mark phase must visit every live object — making it O(live set size). This is why terabyte-heap collectors (ZGC, Shenandoah) perform concurrent marking (mark while application runs), intersecting with write barriers to handle concurrent modification of the reference graph.

---

### 💻 Code Example

Example 1 — Identify GC Root categories with heap dump analysis:
```bash
# Capture heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Analyse with Eclipse MAT
# Tools → Leak Suspects Report
# Shows: Root causes: "Class static field X holds live reference to..."
# This reveals unintended GC Root connections
```

Example 2 — Static field as GC Root causing leak:
```java
// BAD: static Map = GC Root → everything put in it
// is permanently alive until removed
class SessionManager {
    // Static field makes this a GC Root!
    private static final Map<String, UserSession> sessions
        = new HashMap<>();

    static void addSession(String id, UserSession s) {
        sessions.put(id, s); // never removed = leak
    }
}

// GOOD: bounded cache with eviction (explicitly manages roots)
class SessionManager {
    private static final Cache<String, UserSession> sessions =
        Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterAccess(30, TimeUnit.MINUTES)
            .build();
}
```

Example 3 — ThreadLocal as unexpected GC Root:
```java
// BAD: ThreadLocal not removed from thread pool threads
// Thread pool threads live for the JVM lifetime
// → ThreadLocal values are GC Roots via thread → threadLocalMap
class RequestContext {
    private static final ThreadLocal<Request> context
        = new ThreadLocal<>();

    static void set(Request req) {
        context.set(req);
        // If remove() is never called, and this thread
        // is a pool thread (long-lived), req is FOREVER
        // reachable via: Thread.threadLocals → context → req
    }
}

// GOOD: always remove ThreadLocal on scope exit
static void processRequest(Request req) {
    context.set(req);
    try {
        // ... process ...
    } finally {
        context.remove(); // BREAK THE GC ROOT CONNECTION
    }
}
```

Example 4 — Analyse GC roots with jcmd:
```bash
# List GC roots in running JVM (diagnostic)
jcmd <pid> GC.roots

# Find what's keeping an object alive:
# In Eclipse MAT: right-click object →
# "Path to GC Roots" → shows the reference chain
# from a GC Root to your object
```

---

### ⚖️ Comparison Table

| GC Strategy | Handles Cycles | Overhead Per Write | Mark Cost | Best For |
|---|---|---|---|---|
| **Tracing (GC Roots)** | Yes | None | O(live set) | JVM, .NET, Go |
| Reference Counting | No (needs cycle detection) | Per pointer update | O(0) for live, O(collected set) for dead | Python, Swift, Rust Arc |
| Ref Counting + Cycle Detection | Yes | Per pointer + cycle scan | O(connected component) | Python (CPython) |
| Region-based (Rust lifetime) | Yes | Zero (compile-time) | Zero (no GC needed) | Systems programming |

How to choose: Java uses tracing from GC Roots — elegant for correctness, requires periodic stop/scan. For deterministic latency without GC, use Rust's ownership system or manual memory management.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Java has no memory leaks because of GC" | Java has memory leaks — they just look different. An object accumulating in a static collection is a GC leak: GC correctly preserves it because it IS reachable from a root, just unintentionally connected. |
| "Objects with reference count zero are automatically garbage" | Java's GC is not reference counting. An object is garbage if and only if not reachable from GC Roots — not when its count drops to zero. |
| "Setting an object to null immediately frees memory" | Setting to null removes one reference. The object is only collectable if this was the LAST reference chain to a GC Root. The GC still runs on its own schedule. |
| "GC Roots are only local variables" | GC Roots include static fields, active threads, JNI references — not just local variables. Static fields are a major source of unintended object retention. |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory Leak via Static Collection (Most Common)**

**Symptom:** Heap grows monotonically over hours/days; restart fixes temporarily; OOM eventually.

**Root Cause:** A static field (GC Root) holds a growing collection of objects. The objects are "live" from the GC's perspective but logically dead from the application's perspective.

**Diagnostic:**
```bash
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# Eclipse MAT → "Leak Suspects Report"
# OR: Dominator Tree → find object with largest
# retained heap
# "Path to GC Roots" → reveals the static field anchor
```

**Prevention:** Use bounded caches (Caffeine, Guava) instead of raw `HashMap` for application caches; review all `static final Map/List/Set` fields for proper eviction/bounds.

**2. ThreadLocal Memory Leak (Thread Pool)**

**Symptom:** Heap grows with each processed request; heap dump shows many `ThreadLocalMap.Entry` objects referencing request objects from old requests.

**Root Cause:** Thread pool threads are long-lived GC Roots. `ThreadLocal` values set on those threads without `remove()` stay alive forever.

**Diagnostic:**
```bash
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# Eclipse MAT → find "Thread" objects in OQL:
# SELECT * FROM java.lang.Thread
# For each Thread → threadLocals → check Entry values
```

**Prevention:** Always call `ThreadLocal.remove()` in a `finally` block; use request-scoped frameworks (Spring @RequestScope) that handle cleanup automatically.

**3. JNI Global Reference Leak**

**Symptom:** Native memory grows; `jcmd VM.native_memory` shows growing JNI reference count; native code that calls back into Java retains old Java object references indefinitely.

**Root Cause:** JNI code creates `NewGlobalRef` to a Java object but never calls `DeleteGlobalRef`. JNI Global References are GC Roots — they keep Java objects alive until explicitly deleted.

**Diagnostic:**
```bash
jcmd <pid> VM.native_memory summary | grep JNI
# Growing "JNI" section indicates ref leak
```

**Prevention:** Always pair `NewGlobalRef` with `DeleteGlobalRef` in native code; document ownership of all JNI global references.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — the runtime that performs GC using GC Root tracing
- `Heap Memory` — the region that GC Root tracing operates on
- `Class Loader` — loaded classes and their static fields are GC Roots as long as the ClassLoader is alive
- `Stack Memory` — all active thread stack frames contribute local variables as GC Roots

**Builds On This (learn these next):**
- `Minor GC` — the frequent collection that traces GC Roots across the Young Generation
- `Reference Types` — Soft, Weak, and Phantom references modify the normal GC Root reachability rules
- `Stop-The-World` — the phase where all threads are paused to safely enumerate GC Roots
- `GC Pause` — the observable latency impact of GC Root enumeration at safepoints

**Alternatives / Comparisons:**
- `Reference Counting` — alternative GC strategy (Python, Swift) that does not require GC Roots but fails with cycles
- `Safepoints` — the JVM mechanism that ensures all threads are in a consistent state for GC Root enumeration

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Starting anchors for GC's reachability    │
│              │ traversal: stack locals, statics, JNI refs│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ GC needs to know definitively which       │
│ SOLVES       │ objects are live without being fooled     │
│              │ by circular references                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Java memory leaks = objects reachable     │
│              │ from GC Roots that shouldn't be.          │
│              │ Break the root chain to fix the leak.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnose memory leaks: trace root chain   │
│              │ in Eclipse MAT "Path to GC Roots"         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never hold long-lived references in static│
│              │ collections without explicit eviction     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correct circular ref handling vs O(live   │
│              │ set) tracing cost at GC time              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Anything not anchored to a GC Root is    │
│              │ invisible to the JVM — and will be        │
│              │ swept away"                               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reference Types → Minor GC → G1GC         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `WeakHashMap<K, V>` uses weak references as keys. When the key object has no other strong references, the key becomes weakly reachable and the entry is removed on the next GC. However, the VALUE in the entry is a strong reference. Describe the exact GC root chain that keeps the value alive BEFORE the key is collected, and trace what happens to the value AFTER the key is collected — specifically, why doesn't the value immediately become garbage when the key's strong references disappear?

**Q2.** In a concurrent GC (like G1GC with concurrent marking), the GC is tracing objects from GC Roots while the application is simultaneously mutating the reference graph. Object A is being scanned; it references Bs. Application thread X concurrently removes B from A and adds B to Object C (which hasn't been scanned yet). Without a write barrier, the GC would miss B entirely. Describe the write barrier mechanism that ensures the concurrent GC sees all live objects — and why this mechanism must intercept write operations rather than read operations.

