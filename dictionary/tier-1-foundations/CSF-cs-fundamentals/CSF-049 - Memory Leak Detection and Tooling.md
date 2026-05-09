---
id: CSF-049
title: Memory Leak Detection and Tooling
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - deep-dive
  - tradeoff
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /csf/memory-leak-detection-and-tooling/
---

# CSF-049 - Memory Leak Detection and Tooling

⚡ TL;DR - Memory leaks are heap objects that are no longer needed but still referenced, preventing GC collection; detecting them requires heap profiling, leak analysis tools, and understanding object retention graphs.

| CSF-049         | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-023, CSF-050                      |                 |
| **Used by:**    | CSF-059                               |                 |
| **Related:**    | CSF-023, CSF-050, CSF-057, CSF-059    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without memory leak detection, heap memory grows steadily until
the JVM/process OOMs. The growth might be slow (1MB/hour);
the system runs fine for days, then crashes at 2am. No log
entry says "memory is leaking"; you only know when it's too late.

**THE BREAKING POINT:**
A Java web service deployed Friday has 512MB heap. By Sunday
morning, it's at 490MB. By Monday morning, OOM. The heap dump
shows a `Map<String, byte[]>` with 40 million entries — an
in-memory cache with no eviction policy. This is a classic
memory leak: objects held by a reference even though no business
logic needs them.

**THE INVENTION MOMENT:**
Java's `jmap`, `jstack`, and Eclipse MAT (Memory Analyser Tool)
were the first mainstream heap analysis toolchain. They introduced
the concept of _retained heap_ (how much memory would be freed
if this object were collected) and _dominator trees_ (the
path from GC roots to the leaking objects).

**EVOLUTION:**
Modern tooling: Java Flight Recorder, JDK Mission Control, YourKit,
AsyncProfiler, Pyroscope (continuous profiling). eBPF-based
tools enable production profiling with near-zero overhead.
"Continuous profiling" services (Datadog, Pyroscope) sample
memory in production continuously, making leak detection
proactive rather than reactive.

---

### 📘 Textbook Definition

A **memory leak** in GC-managed languages occurs when an object
is reachable (referenced) but no longer _logically needed_.
The GC cannot collect it because it's still in the reference
graph, even though no live code uses it. A **heap dump** is a
snapshot of all live objects in the heap at a point in time.
**Heap analysis tools** traverse the dump to identify objects
with disproportionately large retained heap and trace their
retention path from GC roots.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A memory leak is a reference held longer than needed; heap dump analysis finds what's holding it and why.

**One analogy:**

> A memory leak is like a filing cabinet where you keep
> adding files but never remove old ones. The cabinet is
> full; you need a new one; you add more cabinets. Eventually
> the office is out of space. A heap analyser is an auditor
> who looks through the cabinets, finds the oldest unused
> files, and traces who was responsible for not filing them.

**One insight:**
In GC languages, memory leaks are _always_ reference retention
problems. The GC is not broken; something in your code is
holding a reference it shouldn't. The diagnostic question is
always: "who is holding this reference and why?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. GC collects objects with no GC-root-reachable references.
2. A leak = object reachable but logically dead (no one needs it).
3. GC roots: thread stacks, static fields, JNI references, finalisation queue.
4. Retained heap = memory freed if the object and its exclusive sub-graph are collected.
5. Dominator = object that, if removed, would free the most retained heap.

**DERIVED DESIGN:**

- **jmap -dump**: heap dump to file
- **Eclipse MAT**: dominator tree, leak suspects, OQL queries
- **YourKit / JProfiler**: live profiling + allocation tracking
- **Java Flight Recorder**: low-overhead continuous recording
- **WeakReference / SoftReference**: allow GC to collect referenced objects

**THE TRADE-OFFS:**
**Gain:** Precise root cause identification. Production profiling with JFR.
**Cost:** Heap dump analysis is post-mortem and requires significant memory
for the dump file. Live profiling has overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Object graphs in large systems are complex; retention paths are non-obvious.
**Accidental:** Missing eviction policies, forgotten listeners, ThreadLocal leaks.

---

### 🧪 Thought Experiment

**SETUP:**
Your Spring Boot app processes user sessions. You have a static
`Map<String, UserSession>` as a session cache.

**THE LEAK:**

```java
public class SessionCache {
    // STATIC: lives for the entire JVM lifetime
    private static final Map<String, UserSession>
        sessions = new HashMap<>();

    public void addSession(String id, UserSession s) {
        sessions.put(id, s); // added...
    }
    // But never removed! User logs out: session still in map
    // Map grows unbounded. UserSession holds large objects.
}
```

**DIAGNOSIS:**

```bash
jmap -dump:format=b,file=heap.hprof <pid>
# Open in Eclipse MAT: dominator tree shows
# SessionCache.sessions -> HashMap -> UserSession[]
# Retained: 400MB (all sessions ever created)
```

**FIX:**

```java
// Use Caffeine cache with TTL-based eviction
private static final Cache<String, UserSession> sessions =
    Caffeine.newBuilder().expireAfterAccess(30, TimeUnit.MINUTES).build();
```

---

### 🧠 Mental Model / Analogy

> Think of the heap as a city connected by roads (references).
> The GC is the demolition crew: they can only demolish buildings
> (objects) with no roads leading to them. A memory leak is a
> road network that keeps an entire neighbourhood connected to
> the city centre, even though everyone has moved out.
> Heap analysis is the urban planner who draws the road map,
> finds the last road keeping the neighbourhood alive,
> and identifies who built it.

**Element mapping:**

- Buildings = heap objects
- Roads = references
- City centre = GC roots (stacks, statics)
- Demolition crew = garbage collector
- Road map = object reference graph
- Urban planner = heap analysis tool (MAT, YourKit)

Where this analogy breaks down: the GC can find and demolish
multiple isolated neighbourhoods at once (cyclic garbage with no root).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A memory leak is when a program keeps holding onto things it
no longer needs. Like a computer program that downloads files
but never deletes them — eventually the disk fills up.
Memory leak tools find what's being kept and why.

**Level 2 - How to use it (junior developer):**
When heap grows without bound: (1) take heap dump with `jmap`;
(2) open in Eclipse MAT; (3) click "Leak Suspects";
(4) find the dominator with the most retained heap;
(5) click to see the reference chain from GC root to the leaking object.

**Level 3 - How it works (mid-level engineer):**
Eclipse MAT builds a _dominator tree_: for each object, the
dominator is the object whose removal would free the largest
sub-graph. Objects with unexpectedly large retained heap are
leak suspects. OQL (Object Query Language) lets you query the
heap like a database: `SELECT * FROM java.util.HashMap WHERE size > 100000`.

**Level 4 - Why it was designed this way (senior/staff):**
Java Flight Recorder is designed for production use: it samples
only 1-2% overhead. It uses a circular buffer (ring buffer)
for continuous recording. This enables "always-on" leak
detection: when a leak is suspected, dump the last N minutes
of recording without requiring a heap dump (which pauses the JVM
for seconds to minutes for large heaps).

**Expert Thinking Cues:**

- Heap growing without OOM: is the old gen growing steadily? Schedule a heap dump at peak.
- GC overhead >25%: is the live set too large for the heap? Or is there a leak?
- `jstat -gcutil <pid>`: live data on GC frequency and old gen usage over time.

---

### ⚙️ How It Works (Mechanism)

**Heap dump capture:**

```bash
# Trigger heap dump (JVM pauses)
jmap -dump:format=b,file=/tmp/heap.hprof <pid>

# Trigger on OOM automatically
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/heap.hprof ...
```

**Eclipse MAT analysis:**

```
1. Open heap.hprof in MAT
2. View: Dominator Tree -> sort by Retained Heap
3. Top suspect: SessionCache.sessions -> HashMap
4. Right-click -> Path to GC Roots -> shortest path
5. Shows: SessionCache (static field) -> HashMap -> entries
6. Fix: add eviction policy (TTL, max size)
```

**jstat live monitoring:**

```bash
# Print GC stats every second
jstat -gcutil <pid> 1000
# S0  S1  E  O  M  CCS  YGC  YGCT  FGC  FGCT  GCT
# 0   50  90 40 95  90  3500 12.4  3    1.2   13.6
# Old (O) growing: 40% -> check every few minutes
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Monitoring alert: heap >80% for 30 min  ← YOU ARE HERE
  |-> jstat -gcutil: Old gen growing 1%/hr
  |-> jmap -dump: heap.hprof (1.2GB, JVM paused 15s)
  |-> MAT: leak suspects -> SessionCache.sessions
  |-> Dominator: HashMap retains 800MB
  |-> Path to GC root: static field SessionCache.sessions
  |-> Fix: add Caffeine TTL eviction
  |-> Deploy: Old gen growth stops
  |-> Alert: cleared
```

**FAILURE PATH:**

- Heap dump causes long JVM pause (minutes for 8GB heap)
- OOM before dump captured: use `-XX:+HeapDumpOnOutOfMemoryError`
- Dump file too large: copy to separate machine for analysis

---

### ⚖️ Comparison Table

| Tool                 | Use Case                    | Overhead   | Production Safe?   |
| -------------------- | --------------------------- | ---------- | ------------------ |
| `jmap -dump`         | Post-mortem heap capture    | Pauses JVM | Only for diagnosis |
| Eclipse MAT          | Offline heap analysis       | N/A        | Offline only       |
| Java Flight Recorder | Continuous monitoring       | ~1-2%      | Yes                |
| YourKit / JProfiler  | Live profiling + allocation | 10-30%     | No                 |
| AsyncProfiler        | CPU + memory sampling       | <5%        | Yes (sampling)     |
| Pyroscope            | Continuous profiling        | <5%        | Yes                |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                            |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| "GC languages don't have memory leaks"         | GC can't collect reachable objects; any held reference leaks                       |
| "Heap dump is only for debugging"              | JFR enables continuous heap analysis in production with low overhead               |
| "OOM means the heap is too small"              | Often means the live set is growing due to a leak; increasing heap just delays OOM |
| "WeakReference prevents all leaks"             | Weak/soft references allow GC to collect but aren't appropriate for all caches     |
| "Memory leak = infinite loop consuming memory" | Leaks are usually slow (MB/hour); they only manifest as OOM after long running     |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Static Collection Leak**
**Symptom:** Heap grows monotonically; static field dominates.
**Diagnostic:**

```bash
jmap -dump:format=b,file=h.hprof <pid>
# MAT: dominator tree -> static field -> collection
```

**Fix:** Replace `HashMap` with bounded Caffeine/Guava cache.

**Mode 2: Event Listener Leak (Java/Android)**
**Symptom:** UI components or domain objects not collected after destroy.
**Root Cause:** Event listener registered but never removed.
**Fix:**

```java
// BAD: listener holds reference to Activity
EventBus.register(this); // never unregistered!

// GOOD: unregister in lifecycle method
@Override protected void onDestroy() {
    EventBus.unregister(this);
}
```

**Mode 3: ThreadLocal Leak (App Servers)**
**Symptom:** Memory grows per request in thread-pool servers.
**Root Cause:** `ThreadLocal` set but never removed; thread pool reuses threads.
**Fix:** Always call `threadLocal.remove()` in finally block.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-023 - Stack vs Heap Memory]]
- [[CSF-050 - Garbage Collection Algorithms Overview]]

**Builds On This (learn these next):**

- [[CSF-059 - GC Pause Analysis and Production Impact]]

**Alternatives / Comparisons:**

- Memory sanitizers (ASan, Valgrind) for C/C++/Rust
- Python `tracemalloc` for Python heap tracking

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Objects held longer than needed;      │
│                 tooling finds retention paths         │
│ PROBLEM         Slow heap growth → OOM crash at 2am   │
│ IT SOLVES       without root cause visibility         │
│ KEY INSIGHT     Leak = reference retained, not GC     │
│                 failure; always a retention path      │
│ USE WHEN        Old gen growing, GC overhead >25%     │
│ AVOID WHEN      (No avoidance: monitor proactively)   │
│ TRADE-OFF       Heap dump: precise but pauses JVM;    │
│                 JFR: continuous but less detailed     │
│ ONE-LINER       Find the reference that's holding     │
│                 more than it should                  │
│ NEXT EXPLORE    CSF-059, Eclipse MAT, JFR             │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Memory leaks in GC languages are always reference retention problems, not GC failures.
2. Diagnosis: `jmap -dump` + Eclipse MAT dominator tree finds what's holding the most retained heap.
3. Prevention: avoid unbounded collections, always remove event listeners, always clean ThreadLocals.

**Interview one-liner:**
"Memory leaks in GC languages occur when objects are reachable but logically dead; diagnosis requires heap dump analysis (jmap + Eclipse MAT) to find the dominator object and trace its retention path from GC roots."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every collection that grows without a size limit or eviction
policy is a potential memory leak. The rule: every bounded
resource (heap, disk, connections) must have an explicit
eviction or expiry strategy. Unbounded growth is a design
flaw, not a configuration issue.

**Where else this pattern appears:**

- **Connection pool leaks** — connections acquired but never returned; pool exhausted
- **Log file growth** — logs without rotation; disk fills up
- **Redis without TTL** — cache grows without eviction; memory fills up

---

### 💡 The Surprising Truth

The most common source of Java memory leaks in enterprise
software is not application code — it's framework and library
configuration. Hibernate's second-level cache, Spring's
application context cache, and log framework buffer caches
can all grow without bound if not configured with size or TTL
limits. Many "application memory leaks" are actually
misconfigured framework caches. The fix is not in application
code; it's in a single configuration property: `maximumSize=1000`
or `expireAfterWrite=30m`.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A Java service has `ThreadLocal<UserContext>`
that is set per request. The service uses a thread pool with
50 threads. After 10,000 requests, memory has grown by 500MB.
Why, and how does the thread pool interact with ThreadLocal retention?

_Hint:_ ThreadLocal stores a value per _thread_. Thread pools
reuse threads. If the ThreadLocal is never removed (`threadLocal.remove()`),
the value accumulates. How many values are kept alive?

**Q2 (Scale):** Your application runs on 50 JVMs each with
an 8GB heap. A slow memory leak grows at 1MB/hour. How would
you detect this before OOM, and what alerting strategy minimises
false positives while catching leaks early?

_Hint:_ Consider monitoring the _rate of change_ of Old Gen usage
between Full GCs. A steady positive slope indicates a leak.
What is the threshold? Research the GC overhead limit as a
lagging indicator.

**Q3 (Design Trade-off):** Some engineers use `WeakHashMap`
to implement caches that don't prevent GC. What are the
semantics of `WeakHashMap` and when does it fail as a cache
implementation? What are the production gotchas?

_Hint:_ Research what `WeakHashMap` does when the GC collects
a key. What happens to the corresponding value? What if the
value references the key?
