---
id: CSF-046
title: Memory Leak Detection and Tooling
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-044, CSF-045
used_by: OBS-015
related: JVM-012, CSF-044
tags: [memory-leak, heap-dump, jvm-tools, mat, memory-profiling]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/csf/memory-leak-detection-and-tooling/
---

⚡ TL;DR - Java memory leaks are objects that are reachable
but no longer needed. Detection: heap dumps analyzed with
Eclipse MAT. Diagnosis: dominator tree reveals what holds
most retained heap. Common causes: static collections,
listener registries, ThreadLocal leaks, unclosed caches.

| #046 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-044 (Memory Management Models), CSF-045 (GC Algorithms) | |
| **Used by:** | OBS-015 (JVM Observability) | |
| **Related:** | JVM-012 (JVM Tuning), CSF-044 (Memory Management) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Java application is deployed on Monday at 10 AM.
By Monday evening, heap usage is at 60%. By Tuesday noon,
GC is running continuously (80% time in GC). By Wednesday,
the application crashes with `OutOfMemoryError: Java heap space`.
Restart. The cycle repeats weekly. The team adds `-Xmx`
(more heap) as a workaround. The leak grows to consume
the new space in two weeks instead of one. Without
the ability to diagnose, the team treats the symptom
(OOM) instead of the cause (the leak).

**THE BREAKING POINT:**

Java's GC prevents dangling pointer bugs but does not
prevent logical retention: objects held in collections,
caches, or registries that the application no longer needs
but that are still reachable. These objects appear LIVE
to the GC. The GC cannot distinguish "I still hold this
reference" from "I still NEED this reference."
Without tooling, you cannot see inside the heap during
the leak. You know the heap is growing; you do not know WHAT
is growing and WHY.

**THE INVENTION MOMENT:**

The heap dump: a snapshot of the entire JVM heap at a
moment in time. Combined with analysis tools (originally
`jhat` in the JDK; now Eclipse Memory Analyzer Tool - MAT),
developers can see exactly which objects are on the heap,
how many, how much memory they retain, and what holds them.
Heap dump analysis became the standard approach for
diagnosing Java memory leaks. Modern profilers (JFR,
async-profiler) can also record allocation hot spots
LIVE without requiring a heap dump.

---

### 📘 Textbook Definition

**Memory leak (Java):** A condition where objects accumulate
on the JVM heap because they remain reachable (via reference
chains from GC roots) even though the application no
longer uses them. GC cannot reclaim them. Over time,
heap usage grows unboundedly.

**Heap dump:** A binary snapshot of all live objects on
the JVM heap, their fields, and the references between
them. Used for offline analysis of memory state.

**Retained heap:** The amount of memory that would be freed
if a particular object were removed from the heap (including
all objects only reachable through this object).

**Dominator tree:** A tree structure derived from the heap
object graph. Each node dominates its children (all paths
to the child pass through the dominator). The dominator
tree reveals WHICH objects hold the most retained heap -
directly identifying leak roots.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Memory leaks in Java = objects reachable but not needed.
Diagnose with heap dumps analyzed by Eclipse MAT:
dominator tree shows what holds the most memory.

**One analogy:**

> A storage unit where you rent space monthly. You put
> boxes in but never take them out. The unit fills.
> The storage company (GC) cannot throw out your boxes -
> you are still the registered owner (reachable reference).
> A heap dump is: open the unit, photograph every box
> and who put it there. The photograph (MAT analysis) shows
> that boxes from January are still there, and they were
> put there by your application's cache that never evicts.

**One insight:**

When Eclipse MAT's "Leak Suspects" report shows that
one object retains 80% of the heap, the problem is usually
solved within 10 minutes of seeing that report. The challenge
is getting there: the application must be caught during
the leak (not before or after OOM), and a heap dump taken.
Automated heap dumps on OOM (`-XX:+HeapDumpOnOutOfMemoryError`)
are essential: they capture the state at the moment of death,
which is usually when the leak is most visible.

---

### 🔩 First Principles Explanation

**JAVA MEMORY LEAK PATTERNS:**

```
┌──────────────────────────────────────────────────────┐
│ PATTERN 1: Static Collection without Eviction        │
│   static Map<String, Session> sessions = new HashMap<>();│
│   sessions.put(sessionId, session); // never removed │
│   // Sessions accumulate forever (GC can't reclaim)  │
│                                                      │
│ PATTERN 2: Event Listener not Deregistered           │
│   button.addActionListener(listener); // strong ref  │
│   // button holds listener alive even after window   │
│   // is closed                                       │
│                                                      │
│ PATTERN 3: ThreadLocal not Removed                   │
│   static ThreadLocal<UserContext> ctx = new ThreadLocal<>();│
│   ctx.set(userContext); // in thread pool thread     │
│   // Thread is reused; ctx.set() again for next req  │
│   // Old UserContext? Still alive if ctx.remove()    │
│   // was never called. N threads * N contexts = leak │
│                                                      │
│ PATTERN 4: Inner Class Holds Outer Reference         │
│   class Outer {                                      │
│     class Inner implements Runnable { // holds Outer }│
│     // Submitting Inner to executor: Outer stays alive│
│     // even after Outer is "done"                    │
│   }                                                  │
│                                                      │
│ PATTERN 5: Cache Without Eviction Policy             │
│   Map<CacheKey, Value> cache = new HashMap<>();      │
│   cache.put(key, value); // never expired/evicted    │
│   // Cache grows to contain every key ever seen      │
└──────────────────────────────────────────────────────┘
```

**DETECTION WORKFLOW:**

```
┌──────────────────────────────────────────────────────┐
│ 1. OBSERVE: heap usage grows monotonically            │
│    jstat -gcutil <pid> 5000                          │
│    O column: Old Gen usage grows and never drops     │
│                                                      │
│ 2. CAPTURE: heap dump (live or on OOM)               │
│    jmap -dump:format=b,file=heap.hprof <pid>         │
│    # or auto on OOM:                                 │
│    # -XX:+HeapDumpOnOutOfMemoryError                 │
│    # -XX:HeapDumpPath=/var/log/heapdumps/            │
│                                                      │
│ 3. ANALYZE: Eclipse MAT (Memory Analyzer Tool)       │
│    Run "Leak Suspects" report                        │
│    View Dominator Tree                               │
│    Find object with largest retained heap            │
│    Expand: what holds the reference chain?           │
│                                                      │
│ 4. FIX: remove retention, add eviction, close resource│
│                                                      │
│ 5. VERIFY: repeat load test; heap stabilizes         │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THREAD LOCAL LEAK IN SPRING:**

A Spring Boot application uses a thread pool (embedded
Tomcat: default 200 threads). Each request handler sets
a `ThreadLocal<UserContext>` for downstream logging:

```java
static final ThreadLocal<UserContext> CTX = new ThreadLocal<>();

@GetMapping("/order")
ResponseEntity<?> getOrder(...) {
    CTX.set(new UserContext(userId, tenantId)); // set
    try {
        return ok(orderService.get(orderId));
    } finally {
        // MISSING: CTX.remove()
    }
}
```

Each of the 200 threads holds a `UserContext` for the LAST
request it served. The thread is reused; `CTX.set()` overwrites
the old value. But if `CTX.remove()` is never called and
the thread dies or is replaced (in some pool implementations),
the old `UserContext` is never freed. Worse: in frameworks
like Netty (which reuse threads very long-term), the
`ThreadLocal` grows: each request adds a new mapping in
the internal `ThreadLocalMap` of the thread.

**THE FIX:**
`try { CTX.set(ctx); doWork(); } finally { CTX.remove(); }`
Always remove `ThreadLocal` values in a `finally` block.

---

### 🎯 Mental Model / Analogy

**HEAP DUMP AS FORENSIC AUTOPSY:**

A heap dump is an autopsy report for a sick Java application.
It shows exactly what is in the body (heap) at a moment in time.
Eclipse MAT is the forensic pathologist: it identifies
the cause of death (leak root) by tracing which objects
hold which other objects in the reference chain (the pathology).

Eclipse MAT's dominator tree: an object A is the dominator
of B if all paths from GC roots to B pass through A.
If removing A would free B, A dominates B. The dominator
tree shows A at the top - it is the leak root.
Removing A from the heap would free the most memory.

**MEMORY HOOK:**

"Leak = reachable but not needed.
Detect: heap grows monotonically (Old Gen never drops).
Tool: jmap -dump + Eclipse MAT.
Dominator tree: who retains the most memory.
Common leaks: static collections, listeners, ThreadLocal
not removed, inner classes, caches without eviction.
JVM flag: -XX:+HeapDumpOnOutOfMemoryError"

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Imagine your backpack fills with rocks and you cannot take
any out. Memory leak: the program collects "rocks" (objects)
and never throws them away, even when it does not need them.
Eventually the backpack (heap) is so full you cannot add more.

**Level 2 - Student:**
Heap grows -> GC runs more frequently -> application slows down
-> eventually OOM. Diagnose: take a heap dump when the heap
is mostly full. Open in Eclipse MAT. Find which objects
take the most memory. Find what holds them.

**Level 3 - Professional:**
Key MAT operations:
- "Leak Suspects" report: auto-identifies probable leak roots
- "Dominator Tree": objects sorted by retained heap size
- "Path to GC Roots": for a suspect object, shows the full
  reference chain from GC root to the object (shows what
  keeps it alive)
- "OQL" (Object Query Language): SQL-like queries against
  the heap (`SELECT * FROM java.lang.String s WHERE s.count > 1000`)

**Level 4 - Senior Engineer:**
Allocation profiling (live, without heap dump): async-profiler
with allocation events: `./profiler.sh -e alloc -d 60 -f alloc.html <pid>`.
Shows where in the code objects are being created (the
allocation hot spots). Useful when the leak is growing
slowly and heap dumps cannot be taken on production.
JFR (Java Flight Recorder): `jcmd <pid> JFR.start duration=60s filename=recording.jfr`.
Records GC events, allocation hot spots, thread states. Analyze with JMC (Java Mission Control).

**Level 5 - Expert:**
Shallow vs retained heap distinction. Shallow heap: the
memory of the object itself (header + fields). Retained heap:
shallow heap of the object PLUS shallow heaps of all objects
that would be freed if this object were removed.
Example: a `HashMap` with 1M entries. Shallow heap: ~48 bytes
(the HashMap object itself: a few fields). Retained heap:
potentially GBs (the entries, their keys and values). MAT
shows RETAINED heap in the dominator tree, which is what
matters for leak analysis.

---

### ⚙️ How It Works (Formal Basis)

**REFERENCE TYPES IN JAVA:**

```
┌──────────────────────────────────────────────────────┐
│ Strong Reference (normal): Object o = new Object();  │
│   -> GC will NOT collect. Object is fully alive.     │
│                                                      │
│ SoftReference: SoftReference<T> sr = new SoftRef(v); │
│   -> GC collects when memory is LOW (before OOM).    │
│   -> Used for memory-sensitive caches.               │
│                                                      │
│ WeakReference: WeakReference<T> wr = new WeakRef(v); │
│   -> GC collects at NEXT GC (if no strong refs).     │
│   -> Used for canonical maps, listeners.             │
│   -> WeakHashMap: keys are weak refs.                │
│                                                      │
│ PhantomReference: for cleanup after object collected │
│   -> Used with Cleaner (Java 9+) for resource cleanup│
│                                                      │
│ Memory leak prevention strategy:                     │
│   Cache with strong refs -> SoftReference cache      │
│   Listener registry     -> WeakReference<Listener>   │
│   ThreadLocal           -> always call remove()      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Cache Memory Leak**

```java
// BAD: unbounded cache - classic memory leak
class ProductCache {
    private static final Map<String, Product> cache = new HashMap<>();

    static Product get(String id) {
        return cache.computeIfAbsent(id, ProductCache::load);
    }
    // cache grows forever: every product ever requested stays in memory
}

// GOOD option 1: Caffeine cache with eviction policy
class ProductCache {
    private static final Cache<String, Product> cache = Caffeine
        .newBuilder()
        .maximumSize(10_000)         // LRU eviction
        .expireAfterWrite(30, MINUTES)
        .recordStats()               // enable monitoring
        .build();

    static Product get(String id) {
        return cache.get(id, ProductCache::load);
    }
}

// GOOD option 2: WeakHashMap (GC-friendly; but eviction unpredictable)
class ProductCache {
    // Keys are weak refs: GC can collect key objects even if in map
    private final Map<String, Product> cache = new WeakHashMap<>();

    synchronized Product get(String id) {
        return cache.computeIfAbsent(id, this::load);
    }
}
```

**Example 2 - ThreadLocal Leak Pattern and Fix**

```java
// BAD: ThreadLocal used in thread pool without remove()
class RequestContextHolder {
    static final ThreadLocal<RequestContext> CTX = new ThreadLocal<>();

    // Called at start of request
    static void set(RequestContext ctx) { CTX.set(ctx); }
    // MISSING: clear() method or remove() in finally block
}

// In Servlet filter:
class ContextFilter implements Filter {
    public void doFilter(request, response, chain) throws Exception {
        RequestContextHolder.set(new RequestContext(request)); // set
        chain.doFilter(request, response);
        // BUG: no remove() - if exception propagates, context not cleared
        // Thread goes back to pool with old context in ThreadLocal
    }
}

// GOOD: always remove in finally
class ContextFilter implements Filter {
    public void doFilter(request, response, chain) throws Exception {
        RequestContextHolder.set(new RequestContext(request));
        try {
            chain.doFilter(request, response);
        } finally {
            RequestContextHolder.CTX.remove(); // ALWAYS clean up
        }
    }
}
```

---

### ⚖️ Comparison Table

| Tool | Type | Overhead | Use Case |
|---|---|---|---|
| `jmap -dump` | Heap dump (offline) | Pauses JVM during dump | Diagnosing OOM, large leak |
| `-XX:+HeapDumpOnOutOfMemoryError` | Auto heap dump on OOM | None until OOM | Production safety net |
| Eclipse MAT | Heap dump analysis (offline) | None (offline) | Analyzing heap dumps |
| `jstat -gcutil` | Live GC metrics | Minimal | Trend monitoring |
| Java Flight Recorder (JFR) | Live low-overhead profiling | ~1% overhead | Allocation profiling in prod |
| async-profiler (`-e alloc`) | Live allocation profiling | Low-medium | Finding allocation hot spots |
| VisualVM | GUI profiling | Medium-high | Dev/staging profiling |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "WeakHashMap prevents all memory leaks" | `WeakHashMap` holds keys as weak references. If the KEY object has no other strong reference, the GC can collect the key, and the WeakHashMap entry disappears. BUT: if the VALUE holds a strong reference back to the key (or any other strong reference keeps the key alive), the key is never collected. `WeakHashMap` works only when the key's lifecycle is external to the cache. Misused, it can be just as leaky as HashMap. |
| "Increasing heap size fixes memory leaks" | Increasing heap delays OOM but does not fix the leak. The leak continues to grow; it just takes longer to fill the larger heap. Increasing heap is a short-term mitigation; the leak must be found and fixed. |
| "Finalize prevents resource leaks" | `Object.finalize()` was deprecated in Java 9 and removed (for scheduling purposes) in Java 18. It was unreliable: GC does not guarantee WHEN or WHETHER finalize runs. Programs that depend on finalize for resource cleanup are incorrect. Use `try-with-resources` for deterministic cleanup and `Cleaner` (Java 9+) for post-GC cleanup of native resources. |
| "jmap -dump safely captures heap in production" | `jmap -dump` causes the JVM to pause completely during the dump (full STW). For a 4GB heap, this pause is measured in SECONDS (proportional to heap size). Do NOT use `jmap -dump` on a production service without warning: it will cause a service outage for the duration of the dump. Use `-XX:+HeapDumpOnOutOfMemoryError` for production (fires only on OOM), or use JFR (low overhead, no STW dump). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: OutOfMemoryError: Metaspace**

**Symptom:** `OutOfMemoryError: Metaspace` (not `Java heap space`).
Heap usage is normal; Metaspace grows without bound.

**Root Cause:** Class loading without unloading. Metaspace
stores class metadata. If classes are repeatedly loaded
(by a classloader that creates a new classloader for each
operation, e.g., some scripting/plugin frameworks, or
hot-deploy without proper unloading), the old classloaders
are not GC'd and Metaspace grows.

**Diagnosis:**
```bash
jstat -gcmetacapacity <pid> 5000
# MC (Metaspace committed) grows without bound

jcmd <pid> VM.native_memory summary
# Shows Metaspace usage
```

**Fix:** Fix the classloader leak (ensure classloaders
are released after use). Or set `-XX:MaxMetaspaceSize=256m`
to get OOM early (to diagnose the leak rate) rather than
consuming all available memory.

**Failure Mode 2: Direct Memory (Off-Heap) Leak**

**Symptom:** `OutOfMemoryError: Direct buffer memory`.
Java heap is fine; process RSS grows beyond `-Xmx + metaspace + native`.

**Root Cause:** `ByteBuffer.allocateDirect()` allocations
not being cleaned up. The ByteBuffer object on the JVM
heap is tiny; the off-heap allocation is large. If ByteBuffer
objects are not GC'd promptly (heap not under pressure),
the associated Cleaners don't run, and off-heap accumulates.

**Fix:** Pool `DirectByteBuffer` objects (allocate once,
reuse). Set `-XX:MaxDirectMemorySize=2g` to limit off-heap.
Enable `-Xlog:gc*` to monitor GC frequency.

---

**Security Note:**

Heap dumps contain ALL live objects on the JVM heap at
the time of capture, including: passwords stored in `char[]`,
session tokens in `String` fields, API keys in memory,
decrypted secrets, user PII. A heap dump file is
a SECURITY ARTIFACT. Storage and access controls:
- Store heap dumps in encrypted, access-controlled directories
- Treat heap dump files with the same sensitivity as production databases
- Never share heap dumps publicly or with third parties
without scrubbing
- Use `-XX:HeapDumpPath` to direct dumps to a restricted directory
- Delete heap dumps after analysis
- Automated retention policies for heap dump directories

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Memory Management Models` (CSF-044) - leaks are a failure
  mode of GC memory management; understanding GC is prerequisite
- `GC Algorithms` (CSF-045) - understanding what GC collects
  (reachable objects NOT collected) is core to understanding leaks

**Builds On This (learn these next):**
- `JVM Tuning` (JVM-012) - full JVM memory configuration
  and tuning including GC and heap settings
- `GC Pause Analysis` (CSF-075) - deeper analysis of GC
  behavior in production including pause impact

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ DETECT       │ jstat -gcutil <pid> 5000               │
│              │ O column grows, never drops = leak      │
├──────────────┼─────────────────────────────────────────┤
│ CAPTURE      │ jmap -dump:format=b,file=heap.hprof<pid>│
│              │ -XX:+HeapDumpOnOutOfMemoryError (always)│
│              │ -XX:HeapDumpPath=/var/log/heapdumps     │
├──────────────┼─────────────────────────────────────────┤
│ ANALYZE      │ Eclipse MAT: "Leak Suspects" report     │
│              │ Dominator Tree: largest retained heap   │
│              │ "Path to GC Roots": why alive?          │
├──────────────┼─────────────────────────────────────────┤
│ COMMON LEAKS │ Static Map/List without eviction        │
│              │ Event listener not removed              │
│              │ ThreadLocal without remove() in finally │
│              │ Non-static inner class in executor      │
│              │ Cache without size/time eviction        │
├──────────────┼─────────────────────────────────────────┤
│ FIX PATTERNS │ Add eviction (Caffeine, max size/TTL)   │
│              │ WeakReference for optional listeners    │
│              │ ThreadLocal.remove() in finally ALWAYS  │
│              │ try-with-resources for all Closeable    │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ JVM-012 (JVM Tuning), CSF-075 (GC Pause)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Java memory leaks are LOGICAL, not pointer bugs: objects
   remain reachable (strong reference chain from GC root)
   but are no longer needed. GC cannot help. The programmer
   must remove the reference (evict from cache, deregister
   listener, remove from ThreadLocal). Always add `-XX:+HeapDumpOnOutOfMemoryError
   -XX:HeapDumpPath=/var/log/heapdumps/` to production JVM flags.
2. Eclipse MAT's dominator tree is the primary diagnostic tool.
   The object that retains the most heap and is not supposed
   to is the leak root. "Path to GC Roots" shows the reference
   chain keeping it alive. Fix: break the chain.
3. Three always-fix patterns: (1) caches need eviction
   (Caffeine `maximumSize` + `expireAfterWrite`). (2) ThreadLocal
   values must be removed in a `finally` block. (3) listeners/
   observers must be explicitly deregistered. Each of these
   is a class of bug that causes memory leaks in Spring Boot
   applications.

**Interview one-liner:**
"Java memory leaks are reachable objects that the application
no longer needs. GC cannot collect them because they have
a strong reference chain from a GC root. Detection: heap
usage grows monotonically in `jstat`. Diagnosis: Eclipse
MAT dominator tree on a heap dump shows what retains the
most memory. Common causes: static collections without
eviction, unremoved listeners, ThreadLocal without remove().
Fix: add eviction policies, deregister listeners, always
call ThreadLocal.remove() in finally."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Memory leaks embody the "who is responsible for cleanup?"
question that appears everywhere in software. In GC languages,
we offload MEMORY cleanup to the GC but keep LOGICAL cleanup
as a programmer responsibility. The same tension applies
to: database connections (who closes the connection?),
file handles (who closes the file?), lock acquisition
(who releases the lock?), message acknowledgement (who
acks the message?). In every case, the question is:
"who owns this resource and is responsible for releasing
it?" Java's try-with-resources encodes the answer: the
code that allocates is responsible for cleanup, and the
`try` block lifetime defines the resource lifetime. Memory
leaks are bugs where the question "who releases this object
reference?" has no answer - no code ever removes the object
from the collection it was placed in.

**Where else this pattern appears:**

- **Kubernetes resource limits** - In Kubernetes, if a pod
  has no memory limit, it can consume all node memory.
  Other pods are OOM-killed. The "Kubernetes memory leak"
  analog: a pod's memory usage grows until the node is
  exhausted. Detection: `kubectl top pod` shows growing RSS.
  Fix: set `resources.limits.memory`. Analysis: kubectl
  describe node shows memory pressure events. The same
  "limit resources to detect and diagnose growth" principle
  applies to both JVM heap and Kubernetes pod memory.
- **Redis memory without eviction** - Redis without an
  eviction policy (`maxmemory-policy noeviction`) fills
  its memory limit and starts returning errors. This is
  the Redis equivalent of Java's OOM. Detection: `redis-cli info memory`
  shows `used_memory` approaching `maxmemory`. Fix: set
  an eviction policy (`allkeys-lru`, `volatile-lru`) and
  a `maxmemory` limit. Same principle: unbounded growth
  in a bounded resource requires eviction.
- **Event sourcing command log retention** - An event store
  without retention limits grows indefinitely. Each event
  is "reachable" (it may be needed for replay). The log
  compaction equivalent: remove events superseded by later
  snapshots. Without compaction, the event store is a
  memory leak analog: everything is retained even when
  no longer needed for active processing.

---

### 💡 The Surprising Truth

The JVM's `-XX:+HeapDumpOnOutOfMemoryError` flag has been
available since Java 1.4.2 (2004) but was not enabled by
default in most application servers and Spring Boot applications
until relatively recently. Many teams discovered their
application's memory leak only AFTER OOM - and without
a heap dump, they could not diagnose it. The application
was restarted, the leak started again, and the cycle
continued. The irony: the 5 minutes spent adding
`-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/heap/`
to the JVM startup flags would have captured the evidence
needed to fix the leak on the first OOM. Instead, teams
spent weeks adding memory, restarting, and hoping. Modern
Spring Boot documentation and production checklists include
these flags as standard. Always add them. The heap dump
file (potentially GBs) is the cost; the ability to diagnose
a production OOM is the benefit. It is always worth it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[CONFIGURE]** Add the necessary JVM flags to a Spring
   Boot application's startup command to: (1) auto-dump
   on OOM, (2) save dumps to a specific directory,
   (3) enable GC logging for trend analysis. Justify each flag.

2. **[DIAGNOSE]** Given a heap dump from a Java application
   with 3GB retained in 2M objects, use Eclipse MAT to:
   run Leak Suspects, identify the dominator (the one object
   that retains the most memory), show its path to GC roots,
   and identify which code created and is holding the object.

3. **[FIX]** Review this code for memory leaks:
   ```java
   class EventBus {
     private static final List<EventHandler> handlers = new ArrayList<>();
     public static void register(EventHandler h) { handlers.add(h); }
   }
   ```
   Fix using WeakReference with automatic cleanup of stale entries.

4. **[IMPLEMENT]** Implement a production-safe caching layer
   for a product service using Caffeine: maximum 50,000 entries,
   30-minute TTL after write, stats recording, and a
   `CacheLoader` that loads from the database. Justify the
   eviction parameters for a product catalog of ~500K products
   accessed with a power-law distribution.

5. **[EXPLAIN]** Explain the difference between shallow heap
   and retained heap in Eclipse MAT. Why does a `HashMap`
   with 1M entries show tiny shallow heap but large retained heap?

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application uses Spring's `@Cacheable`
annotation with an in-memory cache (default: `ConcurrentMapCacheManager`).
The application is deployed on Monday; by Friday, the heap
is 90% full. Why? What is the correct fix?

*Hint: Spring's default `ConcurrentMapCacheManager` uses
`ConcurrentHashMap` internally with NO eviction policy.
Every unique cache key (and its value) ever stored in
the cache is retained indefinitely. If the cache key
includes parameters that have high cardinality (user IDs,
product IDs, timestamps), the cache grows unboundedly.
By Friday, every user, every product, every combination
of parameters ever seen is in the cache.
Fix: Replace the default cache manager with Caffeine:
```java
@Bean
CacheManager cacheManager() {
    CaffeineCacheManager mgr = new CaffeineCacheManager("products");
    mgr.setCaffeine(Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(30, MINUTES));
    return mgr;
}
```
Always configure maximum size AND expiry time for any Spring cache.*

**Q2.** You run `jmap -dump:format=b,file=heap.hprof <pid>` on
a production Spring Boot service with a 4GB heap and 5,000
requests/second. The dump takes 45 seconds. What happens
to the application during those 45 seconds? Is there an
alternative?

*Hint: During `jmap -dump`, the JVM is fully paused (STW).
ALL application threads are suspended for the entire
45 seconds. From the perspective of clients: every request
that arrived during those 45 seconds times out (assuming
a 30-second timeout). Load balancer may remove the instance
from rotation. Users see errors. This is effectively a
45-second service outage.
Alternatives:
(1) `-XX:+HeapDumpOnOutOfMemoryError`: fires only on OOM,
not on demand. No STW outside the OOM event.
(2) Java Flight Recorder: `jcmd <pid> JFR.start duration=60s filename=recording.jfr`
records allocation and GC data continuously with ~1% overhead.
(3) Use jmap on a non-production replica (canary, staging)
during a load test that reproduces the leak.
(4) NMT (Native Memory Tracking): `jcmd <pid> VM.native_memory summary`
for off-heap without a full STW dump.*

---

### 🎯 Interview Deep-Dive

**Q1: "How would you diagnose a memory leak in a Java production application?"**

*Why they ask:* Common production experience question.
Tests real-world diagnostic skills.

*Strong answer includes:*
1. Detect: monitor Old Gen usage via `jstat -gcutil <pid> 5000`.
   Old Gen (`O` column) grows and never drops after GC.
   Or: Datadog/Prometheus `jvm.memory.used{area=heap}` metric trends up.
2. Confirm: track growth rate. If Old Gen grows linearly,
   it is a leak, not a burst.
3. Capture: use heap dump already configured:
   `-XX:+HeapDumpOnOutOfMemoryError` (auto), or:
   `jmap -dump:format=b,file=heap.hprof <pid>` (manual, but PAUSES JVM).
4. Analyze: Eclipse MAT -> Leak Suspects report -> dominator tree.
5. Identify: largest retained heap object -> path to GC roots.
6. Fix: break the reference chain (eviction, remove, deregister).
7. Verify: run load test after fix; confirm Old Gen stabilizes.

**Q2: "What are common Java memory leak patterns? How do you fix each?"**

*Why they ask:* Tests specific pattern knowledge and fix strategies.

*Strong answer includes:*
- Static collection without eviction: `static Map<K,V> cache`.
  Fix: use Caffeine with `maximumSize` and `expireAfterWrite`.
- Event listener not deregistered: publisher holds strong ref.
  Fix: `WeakReference<Listener>` in publisher, or explicit deregister.
- ThreadLocal without `remove()`: in thread pool, ThreadLocal
  values accumulate per thread. Fix: always call `remove()` in `finally`.
- Non-static inner class submitted to executor: inner class holds
  reference to outer. Fix: use static inner class or lambda
  that captures only needed values (not `this`).
- Off-heap `DirectByteBuffer` accumulation: Fix: pool and reuse buffers.

**Q3: "What is the difference between shallow and retained heap in Eclipse MAT?"**

*Why they ask:* Tests depth of MAT knowledge. Separates users who understand it vs who just run it.

*Strong answer:*
- Shallow heap: the memory occupied by the object itself
  (header ~8-16 bytes + field values). For a `HashMap`: a few
  reference fields (table array ref, size, threshold, etc.).
  Shallow heap of the HashMap object might be 48 bytes.
- Retained heap: shallow heap of the object + shallow heap of ALL
  objects that are only reachable through this object (and would
  be freed if this object were freed). For a `HashMap` with
  1M entries, retained heap includes the table array, all
  Map.Entry objects, all keys and values that are only referenced
  by this map. Retained heap might be GBs.
- Why it matters: sorting the dominator tree by RETAINED heap
  shows which objects, if removed, would free the most memory.
  That is the leak root. Sorting by shallow heap shows the
  most numerous individual objects but not which would help most if freed.
