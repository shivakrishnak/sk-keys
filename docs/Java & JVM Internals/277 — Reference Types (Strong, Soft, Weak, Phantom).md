---
layout: default
title: "Reference Types (Strong, Soft, Weak, Phantom)"
parent: "Java & JVM Internals"
nav_order: 277
permalink: /java/reference-types/
number: "0277"
category: Java & JVM Internals
difficulty: ★★★
depends_on: GC Roots, Heap Memory, Class Loader, JVM
used_by: Caching, WeakHashMap, Connection Pooling, Memory Management
related: GC Roots, Heap Memory, WeakHashMap, Metaspace
tags:
  - java
  - jvm
  - memory
  - gc
  - internals
  - deep-dive
---

# 277 — Reference Types (Strong, Soft, Weak, Phantom)

⚡ TL;DR — Java's four reference types let you fine-tune GC behavior: strong keeps forever, soft until memory pressure, weak until next GC, phantom for post-collection cleanup.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0277        │ Category: Java & JVM Internals       │ Difficulty: ★★★          │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on:  │ GC Roots, Heap Memory, Class Loader, │                          │
│              │ JVM                                  │                          │
│ Used by:     │ Caching, WeakHashMap, Connection     │                          │
│              │ Pooling, Memory Management           │                          │
│ Related:     │ GC Roots, Heap Memory, WeakHashMap,  │                          │
│              │ Metaspace                            │                          │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Java only has strong references by default. Every object you reference lives until you explicitly null the reference. Building a cache with Java's default reference model means: if you hold the cache entry strongly, the object never gets evicted (memory leak). If you remove from the cache, you lose data. There's no middle ground: "hold weakly — keep the object when memory is available, but let GC collect it when memory is tight." 

THE BREAKING POINT:
Applications need memory-sensitive caching: "keep these 10,000 parsed Document objects around as long as memory allows, but let the GC collect them under memory pressure rather than causing an OutOfMemoryError." This behaviour is impossible with only strong references, which either keep objects forever or don't keep them at all.

THE INVENTION MOMENT:
Four carefully calibrated reference strengths give applications fine-grained control over GC interaction — letting the GC collect objects selectively based on memory pressure or lifecycle. This is exactly why Java's reference type hierarchy exists.

### 📘 Textbook Definition

Java provides four reference types under `java.lang.ref`, differentiated by how strongly they prevent garbage collection:

1. **Strong Reference** — the default `Object obj = new Object()`. An object is strongly reachable if any GC Root can reach it via a chain of strong references. It will never be collected while strongly reachable.
2. **Soft Reference** (`SoftReference<T>`) — an object only softly reachable (no strong refs) is collected at the GC's discretion — guaranteed to be collected before `OutOfMemoryError`. Used for memory-sensitive caches.
3. **Weak Reference** (`WeakReference<T>`) — only weakly reachable objects are collected at the next GC cycle. Used for canonicalising mappings (`WeakHashMap`), canonical instances, listener registries.
4. **Phantom Reference** (`PhantomReference<T>`) — the weakest. The referent is never accessible through the reference (`.get()` always returns null). Used for post-collection finalization tracking via `ReferenceQueue`.

### ⏱️ Understand It in 30 Seconds

**One line:**
Reference strength is the dial between "keep forever" and "collect immediately" — four positions for different memory management patterns.

**One analogy:**
> Think of reference types as library book holds: Strong Reference = personally checked out (library can't take it back). Soft Reference = put on reserve (library can recall it if space runs out). Weak Reference = browsing copy on open shelves (collected at next tidy-up). Phantom Reference = a notification slip left when the book is returned (only useful for knowing the book is gone).

**One insight:**
Phantom references fundamentally changed the post-collection cleanup story: `finalize()` is called by the JVM before collection (causing resurrection risk and GC unpredictability), while Phantom references are enqueued AFTER collection (safe, predictable, no resurrection possible). The `Cleaner` API (Java 9+) is built on Phantom references.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Strong reachability always keeps an object alive — this is the base case.
2. Softer references allow GC to override program "ownership" when resources are scarce.
3. Reference strength is a one-way ratchet: stronger → weaker → dead (objects never become more strongly reachable via the reference itself).
4. `ReferenceQueue` provides a notification mechanism when soft/weak/phantom references are cleared.

DERIVED DESIGN:
Invariant 2 enables memory-sensitive caching — memory pressure triggers collection of soft references automatically. Invariant 3 ensures consistency: you cannot accidentally "resurrect" an object by holding a soft ref after a strong ref is removed. Invariant 4 enables the notification-on-collect pattern used for cleanup actions that must run after collection.

THE TRADE-OFFS:
Gain: Fine-grained control over GC interaction; enables memory-sensitive caches; enables post-collection cleanup without finalizers.
Cost: Complexity; incorrect use (e.g., using WeakReference where SoftReference is needed) causes premature collection; ReferenceQueue requires active polling or background thread.

### 🧪 Thought Experiment

SETUP:
A document parser caches 1000 parsed DOM trees. DOM trees are expensive to recompute (50ms each). Total DOM trees in memory = 500 MB. Available heap = 600 MB.

WITH STRONG REFERENCES:
All 1000 DOM trees stay in memory indefinitely (strongly reachable from the cache). When a new parse adds tree 1001 and requires the final 50 MB: OutOfMemoryError. Cache is full but no eviction policy. Application crashes.

WITH SOFT REFERENCES:
All 1000 DOM trees held by `SoftReference`. Available heap = 600 MB, used = 500 MB for trees. New parse request needs 50 MB more. GC detects imminent OOM situation. Clears soft references (some or all 1000 DOM trees freed). The 50 MB becomes available. New parse succeeds. If the cached tree is requested later: `ref.get()` returns null → reparse. Performance degradation (one reparse) vs application crash.

THE INSIGHT:
Soft references trade computation (reparse on eviction) for memory safety (no OOM). This is a principled decision about resource management that is impossible to express with only strong references.

### 🧠 Mental Model / Analogy

> Reference types are like storage options for a collector's library. Strong = items in a locked vault (never touched by the cleaner). Soft = items in a display case (cleaner can bag them up if the building runs out of fire-escape capacity). Weak = items on open shelves (cleaner picks them up at next tidying round). Phantom = a tag left behind when an item is removed (tells the collector it's gone, but the item is already gone).

"Locked vault" → Strong Reference (GC cannot collect)
"Display case cleared before capacity crisis" → SoftReference (cleared before OOM)
"Open shelf items cleared at tidying" → WeakReference (cleared at next GC)
"Tag left behind" → PhantomReference (notified after collection, `.get()` = null)

Where this analogy breaks down: unlike a physical library, Java's GC makes the collection decision algorithmically, not based on physical space. "Memory pressure" is measured by heap utilisation metrics, not human perception.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
By default in Java, if your code holds a reference to an object, that object lives forever (until you set the reference to null). Java offers gentler holds: a "soft hold" that the GC can break if memory runs out, a "weak hold" that the GC breaks at the next cleanup, and a "phantom hold" that only tells you when the object is gone. These let you build smart caches that auto-evict when memory is tight.

**Level 2 — How to use it (junior developer):**
Use `SoftReference<T>` for memory-sensitive caches. Use `WeakReference<T>` for canonical mappings (`WeakHashMap`) and listener registries. Never use `PhantomReference` in application code — use `java.lang.ref.Cleaner` (Java 9+) instead, which wraps it. Always check `.get() != null` before using a soft/weak reference, as it may have been cleared.

**Level 3 — How it works (mid-level engineer):**
The JVM processes reference types during GC in a specific order: strong → soft → weak → phantom. During the mark phase, objects reachable only via soft refs are provisionally marked as "conditionally alive." After marking completes, the GC decides based on current heap pressure whether to clear soft refs (if memory is critically low) or keep them (if plenty of heap remains). Objects cleared from soft/weak refs are added to `ReferenceQueue` if one was provided at Reference construction time. Phantom referents are enqueued AFTER the object is finalized (if it has a finalizer) or immediately after collection if not.

**Level 4 — Why it was designed this way (senior/staff):**
The four-level reference hierarchy was introduced in Java 1.2 as part of a systematic overhaul of Java's GC interaction model. The critical design insight: `finalize()` (already in Java 1.0) was the only pre-Java1.2 cleanup mechanism, but it was disastrously flawed — calling finalize() before collection required keeping the object alive until finalizer runs, delaying collection by at least one GC cycle per finalizable object, and allowing resurrection. Phantom references, by providing a `ReferenceQueue` notification AFTER collection with a permanently cleared referent, eliminate resurrection risk entirely. The `Cleaner` API (Java 9) built on top of Phantom references is the modern replacement for all finalize()-based cleanup.

### ⚙️ How It Works (Mechanism)

**Reference Processing Order During GC:**

```
┌─────────────────────────────────────────────┐
│    REFERENCE PROCESSING PIPELINE (GC)       │
├─────────────────────────────────────────────┤
│  1. Normal mark phase                        │
│     - Mark all strongly reachable objects   │
│     ↓                                       │
│  2. Soft reference processing               │
│     - Objects only softly reachable found   │
│     - Memory tight? → clear + enqueue       │
│     - Memory OK? → keep (treat as strong)   │
│     ↓                                       │
│  3. Weak reference processing               │
│     - Objects only weakly reachable found   │
│     - Always cleared + enqueued (if queue)  │
│     ↓                                       │
│  4. Finalization queue processing           │
│     - Objects with finalizers scheduled     │
│     - Reference to f-queue keeps object     │
│       alive until finalizer runs            │
│     ↓                                       │
│  5. Phantom reference processing            │
│     - Objects whose referents are being     │
│       collected → enqueued to ReferenceQueue│
│     - .get() always returns null            │
└─────────────────────────────────────────────┘
```

**API Overview:**

```java
// Strong Reference (implicit)
Object obj = new Object();  // default strong ref

// Soft Reference
SoftReference<HeavyObject> soft =
    new SoftReference<>(new HeavyObject());
HeavyObject o = soft.get(); // may be null if GC cleared

// Weak Reference
WeakReference<Object> weak =
    new WeakReference<>(new Object());
Object ref = weak.get(); // null if next GC ran

// Soft/Weak with ReferenceQueue notification
ReferenceQueue<HeavyObject> queue = new ReferenceQueue<>();
SoftReference<HeavyObject> tracked =
    new SoftReference<>(new HeavyObject(), queue);
// After GC clears it:
Reference<?> cleared = queue.poll(); // returns 'tracked'

// Phantom Reference
PhantomReference<Object> phantom =
    new PhantomReference<>(new Object(), queue);
Object alwaysNull = phantom.get(); // ALWAYS null
// After collection: queue.poll() returns 'phantom'
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Application uses SoftReference-based cache
  → Request for cached item
  → ref.get() returns non-null ← YOU ARE HERE
  → (item still alive: memory pressure low)
  → Application uses item
  
  [memory pressure increases]
  → GC runs, finds only soft refs to items
  → clears soft refs, adds to ReferenceQueue
  → ref.get() returns null
  → Application repopulates cache (cache miss)
  → ReferenceQueue used for cleanup/metrics
```

FAILURE PATH:
```
Weak reference used where soft reference needed:
  → Every Minor GC clears all weak refs
  → Cache hit rate drops to 0% (cleared constantly)
  → Application repopulates cache after every GC
  → Performance degradation, excessive computation
  → Fix: use SoftReference for memory-sensitive cache
    use WeakReference only for canonicalization
```

WHAT CHANGES AT SCALE:
At scale, large SoftReference-based caches (e.g., a 10 GB parsed-object cache) interact with GC pressure in subtle ways. The JVM makes soft reference clearing decisions based on heap free space and a "soft reference LRU seconds-per-mb" heuristic (`-XX:SoftRefLRUPolicyMSPerMB=1000`). Tuning this flag controls how aggressively soft refs are cleared under pressure. At extreme scale (100 GB heap), tracking thousands of ReferenceQueue entries becomes itself a performance consideration.

### 💻 Code Example

Example 1 — Memory-sensitive cache with SoftReference:
```java
import java.lang.ref.SoftReference;
import java.util.HashMap;
import java.util.Map;

public class SoftCache<K, V> {
    private final Map<K, SoftReference<V>> cache =
        new HashMap<>();

    public void put(K key, V value) {
        cache.put(key, new SoftReference<>(value));
    }

    public V get(K key) {
        SoftReference<V> ref = cache.get(key);
        if (ref == null) return null;
        V value = ref.get();
        if (value == null) {
            // GC cleared it — remove stale entry
            cache.remove(key);
        }
        return value; // may be null (cache miss)
    }
}
// Better: use Caffeine cache which manages this internally
```

Example 2 — WeakHashMap for canonicalising:
```java
import java.util.WeakHashMap;

// Canonical instance registry: share instances by content
// When no code holds a strong ref to the key,
// the entry is automatically removed by GC
Map<String, Connection> connectionCache =
    new WeakHashMap<>();

// Note: the VALUE is strongly held by the entry!
// Only the KEY being weak-reachable triggers removal
// If the key has no other strong refs, entry is removed
String host = "db.example.com";
connectionCache.put(host, connect(host));
// When 'host' local var goes out of scope:
// key is only weakly reachable → entry removed from map
```

Example 3 — Phantom Reference for resource cleanup (modern: Cleaner):
```java
import java.lang.ref.Cleaner;

// MODERN APPROACH: Cleaner (Java 9+) wraps PhantomRef
public class NativeResource implements AutoCloseable {
    private static final Cleaner CLEANER =
        Cleaner.create();

    private final long nativeHandle; // native resource ID
    private final Cleaner.Cleanable cleanable;

    public NativeResource(long handle) {
        this.nativeHandle = handle;
        // Register cleanup: runs when THIS object is collected
        // The cleanup action must NOT hold a strong ref to 'this'
        // (would prevent collection → memory leak!)
        long h = handle; // capture primitive, not 'this'
        this.cleanable = CLEANER.register(
            this, () -> freeNative(h)
        );
    }

    @Override
    public void close() {
        cleanable.clean(); // explicit early cleanup
    }

    private static void freeNative(long handle) {
        // Release native resource
    }
}
```

Example 4 — Diagnose reference clearing:
```bash
# Monitor soft reference clearing in GC logs
java -Xlog:gc*:file=/tmp/gc.log:time \
     -XX:SoftRefLRUPolicyMSPerMB=100 \
     -jar myapp.jar
# -XX:SoftRefLRUPolicyMSPerMB: lower = more aggressive
# soft ref clearing (default 1000ms per MB free heap)

# JMH benchmark to measure soft vs hard reference cache hit rate
```

### ⚖️ Comparison Table

| Reference Type | When Cleared | `.get()` After Clear | Use Case |
|---|---|---|---|
| **Strong** | Never (by GC) | N/A — not a Reference class | All normal variables |
| `SoftReference` | Before OOM / under memory pressure | Returns `null` | Memory-sensitive caches |
| `WeakReference` | At next GC cycle if only weakly reachable | Returns `null` | Canonical maps, listener lists |
| `PhantomReference` | After finalization | Always `null` (even before) | Post-collection cleanup via Cleaner |

How to choose: Default to strong. Use `SoftReference` for caches where eviction under pressure > OOM. Use `WeakReference` for identity maps (key should not prevent GC) and listener deregistration. Use `Cleaner` (wraps PhantomReference) for native resource cleanup instead of `finalize()`.

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────────┐
│        REFERENCE LIFECYCLE                  │
├─────────────────────────────────────────────┤
│  1. Object created, strongly reachable      │
│     ↓ strong ref removed                   │
│  2a. SoftReference only → "softly reachable"│
│      GC: keep if memory OK, clear if tight  │
│     ↓ cleared                               │
│  2b. WeakReference only → "weakly reachable"│
│      GC: always clear at next collection    │
│     ↓ cleared / 3. Finalization scheduling  │
│  4. Object finalizable (has finalizer)      │
│     → finalize() queued + called            │
│     → object may be resurrected (BAD)       │
│     → if not resurrected: collected         │
│  5. PhantomReference enqueued               │
│     → Cleaner.Cleanable.clean() called      │
│     → resource freed safely                 │
└─────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "WeakReference keeps the object alive until the next GC" | Correct for Minor GC. But WeakRef objects may survive multiple Minor GCs if promoted to Old Gen before the weak ref is cleared (only cleared by the corresponding collection of the generation it's in). |
| "SoftReference is lazily cleared on each GC" | SoftReferences are NOT cleared on every GC — they survive until the JVM determines memory pressure is high enough. The clearing policy is implementation-dependent. |
| "PhantomReference.get() returns the object before collection" | NEVER. `PhantomReference.get()` always returns `null` — even before the object is collected. This is by design to prevent resurrection. |
| "Using SoftReference prevents OOM" | Not guaranteed. If you create new strongly reachable objects faster than soft refs can be cleared, OOM can still occur. Soft refs help but don't replace proper memory management. |
| "finalize() runs before PhantomReference is enqueued" | Correct. Finalizable objects go through the finalization queue before phantom refs are cleared. This means phantom-based cleanup runs after (not instead of) finalization, if both are involved. |

### 🚨 Failure Modes & Diagnosis

**1. Cache with Stale Null Soft References**

Symptom: Cache map grows unboundedly even though GC has cleared the referenced objects — map has millions of entries with cleared (`null`) SoftReferences.

Root Cause: After GC clears a SoftReference, the entry remains in the map with a dead `SoftReference` wrapper. The map itself is strongly held — the wrapper stays forever.

Diagnostic:
```bash
jcmd <pid> GC.class_histogram | grep SoftReference
# Millions of SoftReference instances with null referents
```

Fix:
```java
// BAD: never clean stale entries
map.computeIfAbsent(key, k -> new SoftReference<>(compute(k)));

// GOOD: clean stale entries on access (or use ReferenceQueue)
public V get(K key) {
    SoftReference<V> ref = map.get(key);
    if (ref == null) return null;
    V value = ref.get();
    if (value == null) map.remove(key); // CLEAN STALE
    return value;
}
// BEST: use Caffeine cache with weakValues() / softValues()
```

Prevention: Use production-ready caching libraries (Caffeine) instead of hand-rolled SoftReference maps — they handle entry eviction correctly.

**2. WeakReference Unexpectedly Null (Premature Collection)**

Symptom: `weakRef.get()` returns `null` immediately after creation; object was collected before expected use.

Root Cause: The object was only held by the WeakReference and no strong references. Without a strong reference path, GC collected it immediately.

Diagnostic:
```java
// BAD: no strong reference keeps object alive
WeakReference<MyObj> ref = new WeakReference<>(new MyObj());
// GC may collect MyObj() immediately — no strong refs!
MyObj obj = ref.get(); // NULL!

// GOOD: ensure a strong reference path exists
// while the weak reference should be live
MyObj strongRef = new MyObj();
WeakReference<MyObj> ref = new WeakReference<>(strongRef);
// strongRef keeps it alive; weak ref for other purposes
```

**3. finalize() Delays Collection Two GC Cycles**

Symptom: Objects with `finalize()` methods survive longer than expected; GC pressure from long-lived finalizable objects; heap grows between finalization cycles.

Root Cause: Finalizable objects require two GC cycles: one to detect and queue for finalization, one (after finalizer runs) to actually collect.

Diagnostic:
```bash
jcmd <pid> GC.class_histogram | grep "Finalizable\|finalize"
# Large count of objects awaiting finalization = bottleneck
```

Prevention: Remove `finalize()` from all classes; use `AutoCloseable` + try-with-resources or `Cleaner` API for cleanup. Mark all legacy `finalize()` usages for migration.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `GC Roots` — defines what "strongly reachable" means; reference types modify this reachability
- `Heap Memory` — the region where objects under different reference types reside
- `JVM` — the runtime that implements the reference processing pipeline during GC

**Builds On This (learn these next):**
- `WeakHashMap` — Java's standard map implementation using WeakReference for keys; a direct application of WeakReference semantics
- `Caching` — memory-sensitive caches (Caffeine's `softValues()`, `weakValues()`) use these reference types as eviction strategies
- `Finalization` — the pre-collection cleanup mechanism that PhantomReference replaces

**Alternatives / Comparisons:**
- `Finalization` — the deprecated Java 1.0 object lifecycle hook; PhantomReference is the correct modern alternative
- `AutoCloseable` — manual resource management that doesn't rely on GC timing; preferred over any GC-coupled cleanup
- `Off-heap` — memory entirely outside the GC; completely different approach to GC-independent object management

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Four reference strengths: strong, soft,   │
│              │ weak, phantom — controlling GC interaction│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Strong refs keep objects forever;          │
│ SOLVES       │ need memory-sensitive eviction and        │
│              │ post-collection cleanup hooks             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Phantom refs are the RIGHT way to do      │
│              │ post-collection cleanup — they cannot      │
│              │ resurrect the object, unlike finalize()   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Soft: memory-sensitive caches. Weak:      │
│              │ canonicalization maps. Phantom/Cleaner:   │
│              │ native resource cleanup.                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid Phantom refs directly — use Cleaner │
│              │ API. Never use finalize(). SoftRef not    │
│              │ suitable for strict eviction policies     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ GC-driven cache eviction vs unpredictable │
│              │ GC timing for cache hit rates            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reference types are a dial from          │
│              │ 'keep it forever' to 'tell me when        │
│              │ it's gone'"                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WeakHashMap → Caching → Finalization      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Caffeine cache (the standard Java caching library) offers both `weakValues()` and `softValues()` eviction modes. A web application uses a Caffeine cache with `softValues()` to cache parsed HTML templates. Under normal load, hit rate is 95%. During a traffic spike, GC pressure increases and soft references are cleared, dropping hit rate to 30% — causing a CPU spike as templates are reparsed. Would switching to `weakValues()` improve or worsen the situation, and why? What alternative cache eviction strategy would provide more predictable hit rates under load?

**Q2.** `java.lang.Cleaner` (Java 9+) uses PhantomReference internally. One critical constraint: the cleanup action registered with `Cleaner.register(Object, Runnable)` must NOT hold a strong reference to the object being registered. Why does this constraint exist — and what would happen if the cleanup lambda accidentally captured `this` (the object being registered for cleanup)? Trace the exact sequence of events showing why this would prevent collection permanently.

