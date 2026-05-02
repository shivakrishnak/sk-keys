---
layout: default
title: "Finalization"
parent: "Java & JVM Internals"
nav_order: 296
permalink: /java/finalization/
number: "296"
category: Java & JVM Internals
difficulty: ★★★
depends_on: GC Roots, Old Generation, Reference Types (Strong, Soft, Weak, Phantom), Heap Memory
used_by: JIT Compiler
tags:
  - java
  - jvm
  - gc
  - memory
  - internals
  - deep-dive
---

# 296 — Finalization

`#java` `#jvm` `#gc` `#memory` `#internals` `#deep-dive`

⚡ TL;DR — A deprecated Java mechanism allowing objects to run cleanup code before GC collection, infamous for delaying memory reclamation and causing resource leaks.

| #296 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | GC Roots, Old Generation, Reference Types (Strong, Soft, Weak, Phantom), Heap Memory | |
| **Used by:** | JIT Compiler | |

---

### 📘 Textbook Definition

**Finalization** is a JVM mechanism enabling objects to execute arbitrary cleanup logic via the `finalize()` method before being reclaimed by the garbage collector. When the GC determines an object is unreachable, if the object overrides `finalize()`, it is placed in a finalizer queue rather than immediately collected. A low-priority finalizer thread invokes `finalize()` on each queued object; after completion, the object becomes eligible for collection on the next GC cycle. Java 9 deprecated `finalize()` and it was removed from active use in Java 18 via `@Deprecated(forRemoval=true)`. The recommended replacement is `java.lang.ref.Cleaner` (Java 9+) or try-with-resources.

### 🟢 Simple Definition (Easy)

Finalization was Java's way of letting an object "say goodbye" before it was garbage collected — running cleanup code before the memory was freed. It was removed because it caused more problems than it solved.

### 🔵 Simple Definition (Elaborated)

When a Java object with a `finalize()` method becomes unreachable, the JVM doesn't free its memory immediately. Instead, it puts the object in a special queue and has a background thread call the object's `finalize()` method first. Only after that can the memory be freed — on the NEXT garbage collection cycle. This means finalizable objects survive at least one extra GC cycle, consume memory longer than necessary, and can even accidentally be "resurrected" if `finalize()` stores a new reference to `this`. It also means resource cleanup (closing file handles, releasing locks) depends on when the GC happens — which is unpredictable.

### 🔩 First Principles Explanation

**The intended purpose:** Close native resources (file descriptors, sockets, native memory) tied to Java objects when those objects become garbage. Without finalization, if a programmer forgets to close a resource, it leaks until the process exits.

**The finalization lifecycle:**

1. Object `O` overrides `finalize()`.
2. GC discovers `O` is unreachable.
3. GC places `O` in the `java.lang.ref.FinalReference` queue.
4. `FinalizerThread` (a low-priority daemon thread) polls the queue and calls `O.finalize()`.
5. `O` is now "finalized" — if no new references to it were created, it becomes eligible for reclamation on the NEXT GC cycle.
6. Memory freed on the next GC run.

**The resurrection problem:**
```java
class Resurrection {
    static Resurrection saved;

    @Override
    protected void finalize() {
        saved = this; // "Resurrect" — creates a strong reference!
        // Now this object won't be collected this cycle
        // If finalize() is called again later (manual null-out):
        // → second time finalize() is NOT called again
    }
}
```

**The problems:**

1. **Two GC cycles minimum:** All finalizable objects survive at least one extra cycle, increasing Old Generation pressure.
2. **Unpredictable timing:** Finalization runs when the GC decides to — could be minutes or hours after the object becomes unreachable.
3. **Priority inversion:** The finalizer thread runs at low priority; under GC pressure it can fall behind, building a backlog of pending finalizations.
4. **Order non-determinism:** No ordering guarantees between multiple finalizers.
5. **Security:** Finalizable objects can be subclassed to perform actions in `finalize()` even after the constructor throws — enabling "finalizer attacks."

### ❓ Why Does This Exist (Why Before What)

WITHOUT Finalization (Java pre-1.0 consideration):

- No automatic cleanup for native resources when Java objects are collected.
- Programmers must manually remember to call `close()` / `dispose()` on every resource.
- Forgotten resource cleanup → leaking file descriptors, native memory, socket connections.

What was supposed to happen with it:
- `finalize()` acts as a safety net: even if you forget `.close()`, the GC eventually calls `finalize()` and cleans up.

What actually breaks with it:
1. Resources held much longer than necessary — GC timing is unpredictable; a file descriptor might not be released for minutes.
2. Finalizer thread backlog under load causes memory to grow until OOM.
3. Test code accidentally triggers resurrection bugs in production.

Better replacement (Java 9+):
→ `java.lang.ref.Cleaner` — phantom-reference-based cleanup, no resurrection risk.
→ `AutoCloseable` + try-with-resources — explicit, deterministic, predictable.

### 🧠 Mental Model / Analogy

> Finalization is like a legal will that says "Before you demolish my house, someone must come and adopt my cat." When the house (object) is condemned (unreachable), instead of immediate demolition, it goes into a waiting queue. A probate lawyer (finalizer thread) eventually processes the will, adopts the cat (runs cleanup), and THEN the house can be demolished — on the next visit of the demolition crew (next GC). The problem: if the will says "find a new owner for 1,000 cats," the process takes forever, the house sits condemned but not demolished, and you run out of demolition slots.

"Condemned house" = unreachable object, "will" = `finalize()`, "probate lawyer" = finalizer thread, "demolition crew" = GC collection pass.

The backlog of condemned-but-not-finalized houses causes the neighbourhood (heap) to run out of space.

### ⚙️ How It Works (Mechanism)

**Finalization Object Graph:**
```
Object O (finalizable, unreachable)
    ↓ GC discovers unreachable
Enqueued in FinalReference queue
    ↓ Finalizer Thread polls
finalize() called on O
    ↓ if no resurrection
O's phantom reference enqueued (GC can now collect)
    ↓ next GC cycle
Memory reclaimed
```

**Finalizer Thread Behavior:**
```bash
# Visualise finalizer thread in heap dump / thread dump:
# Thread name: "Finalizer"
# Stack: java.lang.ref.Finalizer.runFinalizer()
# If this thread is backed up: heap grows, OOM possible

# Check pending finalizers via JMX:
jcmd <pid> VM.finalization_stats
# Or in code:
Runtime.getRuntime().runFinalization(); // force run (unreliable)
```

**Modern Replacement — Cleaner (Java 9+):**

```java
import java.lang.ref.Cleaner;

public class NativeResource implements AutoCloseable {
    private static final Cleaner cleaner =
        Cleaner.create(); // shared cleaner pool

    // Cleanable holds the cleanup action + reference
    private final Cleaner.Cleanable cleanable;
    private final long nativeHandle;

    public NativeResource() {
        this.nativeHandle = allocateNative(); // JNI call
        // Register cleanup: lambda (must NOT capture 'this'!)
        long handle = nativeHandle;
        this.cleanable = cleaner.register(
            this,
            () -> freeNative(handle) // no 'this' reference!
        );
    }

    @Override
    public void close() {
        cleanable.clean(); // explicit deterministic cleanup
    }

    private static native long allocateNative();
    private static native void freeNative(long handle);
}
```

Key difference from `finalize()`: The cleanup action lambda must NOT capture `this` — otherwise a strong reference is created, preventing GC from detecting the object as unreachable, effectively the resurrection problem.

### 🔄 Flow / Lifecycle

```
Object created with finalize() defined
           │
App code holds reference → Normal use
           │
Last strong reference released → Object unreachable
           │
GC finds unreachable finalizable object
           │
Object NOT collected yet → moved to finalization queue
           │
Finalizer thread (low priority) calls finalize()
           │
    ┌──────┴──────────────┐
    │                     │
No resurrection       Resurrection: finalize()
    │                 stores reference to this
    ▼                     │
Object now            Object reachable again
phantom-reachable     (only ONE finalization attempt!)
    │
Next GC cycle → memory reclaimed
```

### 💻 Code Example

Example 1 — Why finalize() is dangerous: unpredictable resource cleanup:

```java
// BAD: relying on finalize() for resource cleanup
class OldStyleResource {
    private FileInputStream fis;

    OldStyleResource(String path) throws IOException {
        this.fis = new FileInputStream(path);
    }

    @Override
    protected void finalize() throws Throwable {
        try {
            if (fis != null) fis.close(); // may run minutes later!
        } finally {
            super.finalize();
        }
    }
}

// GOOD: Use try-with-resources for deterministic cleanup
try (FileInputStream fis = new FileInputStream(path)) {
    // fis.close() called automatically at end of block
}
```

Example 2 — Detecting finalizer backlog in production:

```java
// Check if finalizer thread is backed up
// (available since Java 9 via management API)
public static long getPendingFinalizations() {
    // Approach 1: JMX
    return ManagementFactory
        .getMemoryMXBean()
        .getObjectPendingFinalizationCount();

    // Approach 2: command line
    // jcmd <pid> VM.finalization_stats
}

// Alert if > 1000 objects pending finalization
if (getPendingFinalizations() > 1000) {
    log.warn("Finalizer thread backlog: {} objects",
             getPendingFinalizations());
}
```

Example 3 — Cleaner-based replacement for native resource:

```java
// GOOD: Java 9+ Cleaner — no resurrection risk, explicit control
public class DirectBuffer implements AutoCloseable {
    private static final Cleaner cleaner = Cleaner.create();

    private final long address;
    private final Cleaner.Cleanable cleanable;

    public DirectBuffer(int size) {
        this.address = unsafe.allocateMemory(size);
        long addr = address; // capture primitive, not 'this'
        this.cleanable = cleaner.register(
            this,
            () -> unsafe.freeMemory(addr)
        );
    }

    @Override
    public void close() {
        cleanable.clean(); // immediate + idempotent
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| finalize() is called immediately when an object becomes garbage | finalize() is called by a low-priority background thread on an unpredictable schedule — potentially much later than when the object became unreachable. |
| finalize() is always called before process exit | The JVM does not guarantee finalize() will be called at all — objects pending finalization at JVM shutdown may never be finalised. |
| finalize() is safe as a fallback for close() | Finalizable objects survive extra GC cycles, consuming heap longer; under load, finalizer backlogs cause OOM. |
| An object can be finalized multiple times | finalize() is called at most once per object, even if the object is resurrected and becomes unreachable again. |
| Cleaner is just a renamed finalize() | Cleaner uses phantom references — no resurrection possible, no "survive-extra-cycle" cost, no priority problems. It's fundamentally safer. |
| super.finalize() is called automatically | Unlike constructors, the JVM does NOT automatically call super.finalize(). You must explicitly call it in a finally block. |
| finalize() was removed in Java 9 | finalize() was @Deprecated in Java 9, @Deprecated(forRemoval=true) in Java 18, and the method still exists but should never be used. |

### 🔥 Pitfalls in Production

**1. Finalizer Thread Backlog Causing OOM**

```java
// BAD: Creating millions of finalizable objects in a hot path
class LegacyEvent {
    protected void finalize() { cleanup(); }
}
// Under load: millions of LegacyEvent objects enqueued
// Finalizer thread can't keep pace → heap fills → OOM

// DIAGNOSIS:
// jcmd <pid> VM.finalization_stats
// or: Runtime.getRuntime().runFinalization() to flush (unreliable)

// FIX: Remove finalize() or replace with Cleaner
```

**2. Resurrection Causing Subtle Memory Leaks**

```java
// BAD: finalize() accidentally captures an outer reference
class Cache {
    static Cache instance; // static field = GC root

    protected void finalize() {
        // This "resurrects" the object!
        Cache.instance = this;
        // Object will NEVER be collected again
        // (finalize() is only called once)
    }
}
// FIX: Never store 'this' in finalize()
```

**3. Native Resources Leaking Due to GC Pressure Dependencies**

```bash
# Symptom: "too many open files" OS error despite Java code
# looking correct — file descriptors piling up because
# finalize() hasn't run yet on closed FileInputStream wrappers

# DIAGNOSIS:
lsof -p <pid> | wc -l  # count open file descriptors

# FIX: Explicitly close resources with try-with-resources
# and run the finalizer queue immediately in tests:
System.gc(); System.runFinalization(); // for test validation only
```

### 🔗 Related Keywords

- `Reference Types (Strong, Soft, Weak, Phantom)` — Phantom references are the safe basis for Cleaner-based cleanup.
- `GC Roots` — finalizable objects are tracked via special reference queues during GC.
- `Old Generation` — finalizable objects often promoted to Old Gen before finalization.
- `Cleaner` — java.lang.ref.Cleaner is the safe, modern replacement.
- `AutoCloseable` — the preferred pattern for deterministic resource cleanup.
- `try-with-resources` — the language-level mechanism ensuring deterministic close().

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ finalize() delays GC by ≥1 cycle, runs   │
│              │ unpredictably, enables resurrection.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Never — use try-with-resources or         │
│              │ java.lang.ref.Cleaner instead.            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Always — deprecated and being removed.    │
│              │ Existing finalize() → migrate to Cleaner. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "finalize() is a time bomb in your heap:  │
│              │ unpredictable, unreliable, dangerous."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reference Types → Cleaner → JIT Compiler  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A legacy Java 8 codebase wraps JNI-allocated native memory buffers in Java objects with `finalize()` for cleanup. The service runs fine at low load but crashes with OOM every 3 hours under peak load. The heap peaks at 92% utilisation, but a heap dump shows 80% is live data — not garbage. Explain the exact mechanism by which `finalize()` causes this pattern, and design a zero-downtime migration path to `java.lang.ref.Cleaner`.

**Q2.** The Cleaner API requires that the cleanup Runnable passed to `Cleaner.register()` must NEVER capture a strong reference to the object being registered. Explain precisely why capturing `this` in the cleanup lambda would prevent the object from ever being garbage collected at all — tracing the reference chain from the Cleaner's internal data structure to the object.

