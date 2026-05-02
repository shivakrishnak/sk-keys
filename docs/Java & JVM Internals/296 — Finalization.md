---
layout: default
title: "Finalization"
parent: "Java & JVM Internals"
nav_order: 296
permalink: /java/finalization/
number: "0296"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - GC Roots
  - Heap Memory
  - Reference Types (Strong, Soft, Weak, Phantom)
  - Minor GC
  - Full GC
used_by:
  - GC Tuning
  - GC Pause
related:
  - Reference Types (Strong, Soft, Weak, Phantom)
  - GC Roots
  - Stop-The-World (STW)
  - Phantom References
tags:
  - jvm
  - gc
  - memory
  - java-internals
  - deep-dive
---

# 0296 — Finalization

⚡ TL;DR — Java's `finalize()` mechanism lets objects run cleanup code before GC reclaims them, but it is unreliable, unpredictable, and deprecated — use try-with-resources or `Cleaner` instead.

| #0296 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | GC Roots, Heap Memory, Reference Types, Minor GC, Full GC | |
| **Used by:** | GC Tuning, GC Pause | |
| **Related:** | Reference Types, GC Roots, Stop-The-World, Phantom References | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine your Java object holds a native resource — an open file handle, a socket, a database connection, or off-heap memory allocated via JNI. When the object becomes unreachable and GC reclaims it, that native resource silently leaks. GC manages Java heap memory, but it knows nothing about OS resources outside the heap.

**THE BREAKING POINT:**
A server runs for three hours. Every request creates a `FileInputStream`. Callers forget to call `close()`. GC eventually collects the objects, but the OS file descriptors are never released. After 60,000 open requests, the OS reports "Too many open files" and the server crashes.

**THE INVENTION MOMENT:**
This is exactly why **Finalization** was created — to give objects a last-chance callback before their memory is reclaimed, so they can release non-heap resources even if the developer forgot to call a cleanup method. The intention was good. The execution was fatally flawed.

---

### 📘 Textbook Definition

**Finalization** is a JVM mechanism that invokes an object's `finalize()` method (inherited from `java.lang.Object`) before the GC reclaims its heap memory. Objects with a non-trivial `finalize()` override are called *finalizable objects* and require at least two GC cycles to collect: one to detect unreachability and enqueue them on the finalizer queue, and one to actually reclaim their memory after the finalizer runs. As of Java 9, `finalize()` is deprecated; as of Java 18 it is deprecated-for-removal.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A "last rites" callback the JVM calls on an object just before erasing it from memory.

**One analogy:**
> Imagine a hotel room checkout. When you leave without telling the front desk, the hotel eventually sends housekeeping to clean up. But housekeeping might arrive hours later, or the hotel might run out of rooms before they get there. Finalization is that unreliable housekeeping — it eventually runs, but you cannot count on it being prompt or guaranteed.

**One insight:**
The deep problem with finalization is that it turns a one-cycle reclamation into a two-cycle reclamation. The object that should die in GC cycle N is kept alive until its `finalize()` runs, then potentially promoted to old-gen and only freed in GC cycle N+1 or later — creating GC pressure from the very mechanism meant to help with cleanup.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. GC manages heap memory. It has no knowledge of OS resources (file handles, sockets, native memory).
2. An object's `finalize()` must run before its memory is reclaimed — so the object must stay alive until finalization completes.
3. The JVM cannot guarantee *when* `finalize()` runs, only that it runs *at some point before* the object is definitively reclaimed (or never, if the JVM exits first).

**DERIVED DESIGN:**
Given invariant 2, the JVM introduces a **Finalizer Queue** (a `ReferenceQueue` internally). When a finalizable object becomes otherwise unreachable:
1. GC detects it is unreachable but sees it has a non-trivial `finalize()` — it cannot collect it yet.
2. GC adds it to the Finalizer Queue (a `java.lang.ref.FinalReference`).
3. The single daemon **Finalizer thread** dequeues it and calls `finalize()`.
4. The object is now considered "finalized" — next GC cycle can actually collect it.

This creates a mandatory two-generation survival, often promoting objects to old-gen just because they have `finalize()`.

**THE TRADE-OFFS:**
**Gain:** Non-heap resources leak less often if callers forget to call `close()`.
**Cost:**
- Two GC cycles per finalizable object.
- Single-threaded Finalizer thread is a bottleneck.
- If `finalize()` throws, the exception is silently swallowed.
- Objects can "resurrect" themselves in `finalize()` by storing `this` in a global reference — causing memory corruption-style bugs.
- JVM exit can skip `finalize()` entirely.

---

### 🧪 Thought Experiment

**SETUP:**
You have a `NativeBuffer` object wrapping a C `malloc` allocation. The class overrides `finalize()` to call a JNI `free()` method. A tight loop creates 10,000 `NativeBuffer` objects per second. GC runs minor collections every 500ms.

**WHAT HAPPENS WITHOUT FINALIZATION:**
Every `NativeBuffer` that becomes unreachable leaks its native allocation. After 5 seconds, 50,000 native allocations are stranded. The OS process runs out of virtual memory and crashes with `OutOfMemoryError: native memory`.

**WHAT HAPPENS WITH FINALIZATION:**
Each unreachable `NativeBuffer` is enqueued. The Finalizer thread processes them sequentially, calling `free()`. But the Finalizer thread can only process ~5,000/second. The queue grows. Native memory still leaks — just more slowly. Eventually the Finalizer thread falls so far behind that the OOM still occurs, just 20 seconds later instead of 5.

**THE INSIGHT:**
Finalization does not solve resource leaks — it only delays them unless the production rate of finalizable objects is slower than the Finalizer thread can process. The correct solution is always explicit cleanup via `AutoCloseable` and `try-with-resources`.

---

### 🧠 Mental Model / Analogy

> Think of finalization as a **dead-letter office**. When a letter has no valid address (the object is unreachable), instead of burning it immediately, the post office holds it in a special bin and sends one more notification to the sender. The sender (the `finalize()` method) can do some last-minute cleanup when notified. But the dead-letter office has a single employee, the bin can overflow, and the notification may never come if the office closes (JVM shuts down) before the employee processes it.

- "Dead letter" → unreachable object with a `finalize()` override.
- "Special bin" → Finalizer Queue (internal `ReferenceQueue`).
- "Single employee" → the JVM Finalizer daemon thread.
- "Notification" → invocation of `finalize()`.
- "Office closing" → JVM shutdown without running finalizers.

Where this analogy breaks down: Unlike a dead-letter office, the sender (object) can in theory refuse to die by re-inserting itself into live references inside `finalize()` — a "resurrection" the postal analogy does not capture.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When Java objects are thrown away by the garbage collector, the JVM gives each object a chance to say goodbye and clean up its mess first — like telling your plumber to turn off the water before leaving. This goodbye callback is called finalization.

**Level 2 — How to use it (junior developer):**
Override `finalize()` in your class to release non-Java resources. But in modern Java you should use `try-with-resources` and implement `AutoCloseable` instead. Only consider `java.lang.ref.Cleaner` (Java 9+) for truly necessary resource cleanup in objects you cannot make `AutoCloseable`.

**Level 3 — How it works (mid-level engineer):**
When GC marks an object unreachable, it checks whether the object overrides `finalize()`. If yes, instead of immediately reclaiming memory, the JVM creates a `FinalReference` wrapper and adds it to a pending-reference list. The JVM's Finalizer thread (a daemon thread at max priority minus 2) polls this list, calls `finalize()` on each object, and then releases it for the next GC cycle. This causes the object to survive at least one GC cycle, potentially being promoted to old-gen, increasing GC pressure.

**Level 4 — Why it was designed this way (senior/staff):**
Java 1.0 designers wanted C++ destructor semantics without the dangers of manual memory management. They chose lazy, GC-driven finalization over reference counting. The fundamental flaw is that GC is not designed for resource management — its goal is memory efficiency, not timeliness. The Finalizer thread is a single-threaded design that cannot scale, and there is no backpressure mechanism. Java 9 introduced `java.lang.ref.Cleaner` as the approved replacement: it uses phantom references (not strong re-reachability), runs in its own configurable thread, and avoids object resurrection. Java 18 deprecated `finalize()` for removal (JEP 421).

---

### ⚙️ How It Works (Mechanism)

**Step 1 — Finalizable object detection:**
During GC mark phase, when an object `O` is found unreachable, the JVM inspects whether its class overrides `finalize()` with a non-trivial implementation (the JVM tracks this via a class-level flag set at class loading time when `finalize()` is resolved to a non-Object implementation).

**Step 2 — FinalReference enqueue:**
Rather than marking `O` for collection, GC wraps it in a `java.lang.ref.FinalReference` (a package-private subclass of `Reference`) and adds it to the JVM's pending-reference list. The object `O` is now *softly reachable* through the `FinalReference` — it cannot be collected yet.

```
┌─────────────────────────────────────────────────┐
│        Finalization Object Lifecycle             │
│                                                 │
│  [Object unreachable]                           │
│         │                                       │
│         ▼                                       │
│  [GC: has non-trivial finalize()?]              │
│         │ YES                                   │
│         ▼                                       │
│  [Add to pending-reference list]                │
│         │                                       │
│         ▼                                       │
│  [Finalizer thread calls finalize()]            │
│         │                                       │
│         ▼                                       │
│  [Object becomes truly unreachable again]       │
│         │                                       │
│         ▼                                       │
│  [Next GC cycle: reclaim memory]                │
└─────────────────────────────────────────────────┘
```

**Step 3 — Finalizer thread processing:**
The JVM starts a daemon thread named "Finalizer" that continuously polls the queue. When an entry appears, it strong-references the object (preventing collection), calls `finalize()`, swallows any thrown exception, then releases the strong reference. The object is now finalizable only once — the JVM marks it "finalized" so `finalize()` is never called twice, even if the object resurrects itself.

**Step 4 — Second collection:**
On the next GC cycle after finalization, if the object is genuinely unreachable (not resurrected), its memory is reclaimed normally.

**Step 5 — Object resurrection:**
Inside `finalize()`, code can do `Resurrection.instance = this;` — assigning `this` to a reachable static field. The object is now reachable again. GC cannot collect it. If the reference is later nulled, GC can reclaim it — but `finalize()` will NOT be called again (invoked at most once).

**Finalizer thread priority:**
The Finalizer thread runs at `Thread.MAX_PRIORITY - 2` (priority 8). On a heavily loaded system, it may still starve if GC produces finalizable objects faster than the single thread can process them.

**Java 9+ Cleaner API:**
`java.lang.ref.Cleaner` avoids all these problems by using `PhantomReference` (which the referent cannot be resurrected through), supports multiple threads, and the `Cleanable` action is a plain `Runnable` that does not hold a reference to the cleaned object.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Object created in Eden]
    → [Object becomes unreachable]
    → [Minor GC runs]
    → [GC detects non-trivial finalize()] ← YOU ARE HERE
    → [FinalReference added to pending list]
    → [Finalizer thread calls finalize()]
    → [Object now collectible]
    → [Next GC: memory reclaimed]
```

**FAILURE PATH:**
```
[finalize() throws exception]
    → [Exception silently swallowed]
    → [Non-heap resource NOT released]
    → [Leak accumulates]

[Finalizer thread falls behind]
    → [Queue grows unboundedly]
    → [Heap fills with uncollected finalizable objects]
    → [OutOfMemoryError]
```

**WHAT CHANGES AT SCALE:**
At high object creation rates (>10,000 finalizable objects/sec), the single-threaded Finalizer becomes a bottleneck. Objects pile up in old-gen waiting for finalization, triggering premature Full GCs. At 100x scale, the Finalizer queue can grow to millions of entries, consuming gigabytes of heap and causing multi-second STW pauses. This is why frameworks like Netty explicitly avoid finalizers on hot-path objects.

---

### 💻 Code Example

Example 1 — Anti-pattern: Overriding finalize() for resource cleanup:
```java
// BAD: Unreliable, causes GC overhead, deprecated
public class NativeBuffer {
    private long nativePtr;

    public NativeBuffer(int size) {
        this.nativePtr = allocateNative(size); // JNI call
    }

    @Override
    @Deprecated
    protected void finalize() throws Throwable {
        try {
            if (nativePtr != 0) {
                freeNative(nativePtr);  // JNI call
                nativePtr = 0;
            }
        } finally {
            super.finalize();
        }
    }
}
```

Example 2 — Correct: AutoCloseable + try-with-resources:
```java
// GOOD: Explicit, deterministic, fast
public class NativeBuffer implements AutoCloseable {
    private long nativePtr;
    private volatile boolean closed = false;

    public NativeBuffer(int size) {
        this.nativePtr = allocateNative(size);
    }

    @Override
    public void close() {
        if (!closed) {
            closed = true;
            freeNative(nativePtr);
            nativePtr = 0;
        }
    }
}

// Caller:
try (NativeBuffer buf = new NativeBuffer(1024)) {
    buf.use();
} // close() called automatically here
```

Example 3 — Java 9+ Cleaner: safety net without finalize() downsides:
```java
// BEST for objects that cannot implement AutoCloseable
import java.lang.ref.Cleaner;

public class NativeBuffer {
    private static final Cleaner CLEANER = Cleaner.create();

    private final long nativePtr;
    private final Cleaner.Cleanable cleanable;

    // Action must NOT hold reference to NativeBuffer —
    // or the cleaner can never detect unreachability
    private static class CleanAction implements Runnable {
        private long ptr;
        CleanAction(long ptr) { this.ptr = ptr; }

        @Override
        public void run() {
            if (ptr != 0) {
                freeNative(ptr);
                ptr = 0;
            }
        }
    }

    public NativeBuffer(int size) {
        this.nativePtr = allocateNative(size);
        // Register: when THIS object is phantom-reachable,
        // run CleanAction
        this.cleanable = CLEANER.register(
            this, new CleanAction(nativePtr)
        );
    }

    public void close() {
        cleanable.clean(); // explicit close OR cleaner fires later
    }
}
```

Example 4 — Diagnosing finalizer queue buildup:
```bash
# Check finalizer queue length via JMX/JConsole
# Or use jcmd:
jcmd <pid> GC.run_finalization

# Check how many finalizable objects exist:
jmap -histo:live <pid> | grep Finalizer

# Verbose GC log showing finalization overhead:
java -Xlog:gc*,ref*=debug MyApp 2>&1 | grep -i final
```

---

### ⚖️ Comparison Table

| Cleanup Mechanism | Timeliness | Thread-safe | GC Overhead | Resurrection Risk | Best For |
|---|---|---|---|---|---|
| `finalize()` | Never guaranteed | Single thread | High (2 cycles) | Yes | Nothing new |
| `AutoCloseable` | Immediate/explicit | Caller-controlled | None | No | All explicit resources |
| `Cleaner` (Java 9+) | Phantom-reachable | Configurable thread | Low | No | Safety-net for non-closeable objects |
| `PhantomReference` | Phantom-reachable | Manual | Low | No | Custom cleanup frameworks |
| `WeakReference` callbacks | GC-driven | Manual | Low | Possible | Caches, listeners |

How to choose: Always prefer `AutoCloseable` + `try-with-resources` for explicit resource management. Use `Cleaner` only as a safety net for objects that are used via external APIs where callers cannot be trusted to call `close()`.

---

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────────────┐
│         Finalizable Object State Machine         │
├─────────────────────────────────────────────────┤
│  CREATED → [strong reachable]                   │
│     │                                           │
│     ▼ (all strong refs gone)                    │
│  UNREACHABLE [but FinalReference holds it]      │
│     │                                           │
│     ▼ (Finalizer thread dequeues)               │
│  FINALIZING [finalize() executing]              │
│     │                      │                    │
│     │ (stores self         │ (no resurrection)  │
│     │  in live ref)        │                    │
│     ▼                      ▼                    │
│  RESURRECTED          FINALIZED                 │
│  [reachable again]    [collectible]             │
│     │                      │                    │
│     ▼ (ref nulled)         ▼ (next GC)          │
│  UNREACHABLE again    RECLAIMED                 │
│  [NOT finalized again]                          │
└─────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `finalize()` is called when the object goes out of scope | `finalize()` is called only when the GC decides to collect the object, which may be seconds, minutes, or never during the JVM's lifetime |
| `finalize()` guarantees resource cleanup | The JVM can exit without calling any finalizers — use `Runtime.addShutdownHook` + `AutoCloseable` for shutdown cleanup |
| `finalize()` exceptions cause visible errors | All exceptions thrown from `finalize()` are silently swallowed — there is no stack trace, no log, nothing |
| Calling `System.gc()` triggers finalizers immediately | `System.gc()` is a hint; even if GC runs, finalizers run asynchronously in the Finalizer thread — call `System.runFinalization()` to process the queue, but this is still not guaranteed |
| Objects with `finalize()` are just slightly slower to collect | They require two full GC cycles, often get promoted to old-gen, and a slow Finalizer thread can cause the entire heap to fill with uncollected finalizable objects |
| `super.finalize()` is automatically called | Unlike constructors, `super.finalize()` is NOT automatically chained — you must call it explicitly in a `finally` block |

---

### 🚨 Failure Modes & Diagnosis

**Finalizer Queue Backlog (OOM)**

**Symptom:**
`OutOfMemoryError: Java heap space` on a server with high object creation rate. `jmap -histo` shows thousands of instances of your class or `java.lang.ref.Finalizer`.

**Root Cause:**
The single Finalizer thread cannot process enqueued objects faster than the application creates new ones. The pending finalization queue is backed by strong references, so GC cannot reclaim objects until the Finalizer thread processes them.

**Diagnostic Command / Tool:**
```bash
jcmd <pid> VM.native_memory
jmap -histo:live <pid> | head -30
# Look for large counts of your finalizable class
# Also check:
jstack <pid> | grep -A20 "Finalizer"
```

**Fix:**
Remove `finalize()` overrides. Replace with `AutoCloseable`. For legacy code, wrap the object in a class that uses `Cleaner`.

**Prevention:**
Never add `finalize()` to objects created at high frequency. Enforce via ArchUnit rule: `noClasses().should().haveMethod("finalize")`.

---

**Silent Resource Leak**

**Symptom:**
Native memory or file descriptors leak. `lsof -p <pid>` shows growing file descriptor count. Eventually "Too many open files" error or native OOM.

**Root Cause:**
`finalize()` was relied upon for cleanup. GC never runs (abundant heap), or queue backs up, leaving resources unreleased.

**Diagnostic Command / Tool:**
```bash
lsof -p <pid> | wc -l   # File descriptor count
cat /proc/<pid>/status | grep VmRSS  # Native memory footprint
```

**Fix:**
Implement `AutoCloseable`, add `close()` call, wrap in `try-with-resources`.

**Prevention:**
Design all resource-holding objects with explicit `close()` from day one.

---

**Object Resurrection Bug**

**Symptom:**
Object reappears after it was believed to be garbage-collected. Data corruption occurs because finalized (partially cleaned) state is re-used.

**Root Cause:**
`finalize()` stores `this` in a static/global reference. The object is resurrected but with partially-cleaned state (the `finalize()` method may have already released some resources). Subsequent use of the resurrected object hits null pointers or already-freed native memory.

**Diagnostic Command / Tool:**
```bash
# Enable verbose GC logging to observe unexpected survivals:
java -Xlog:gc+ref=debug MyApp 2>&1 | grep resurrection
# Review all finalize() implementations for assignments of 'this'
```

**Fix:**
Remove resurrection logic. If a re-pooling pattern is needed, use a proper object pool class instead.

**Prevention:**
Code review rule: `finalize()` must never assign `this` to any variable.

---

**JVM Exit Without Finalization**

**Symptom:**
On JVM shutdown, native resources (temp files, sockets) are not cleaned up. Temp files accumulate on disk.

**Root Cause:**
JVM exit does not guarantee running finalizers. By default, `Runtime.halt()` and SIGKILL skip all finalizers.

**Diagnostic Command / Tool:**
```bash
# Check what shutdown hooks are registered:
jcmd <pid> VM.flags | grep ShutdownHook
# Observe temp files after JVM restart
ls /tmp | grep myapp
```

**Fix:**
Register a `Runtime.addShutdownHook(Thread)` that explicitly closes resources. Do not rely on `finalize()` for shutdown cleanup.

**Prevention:**
Add a JVM shutdown hook that iterates a `ConcurrentHashMap` of open resources and closes each one.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `GC Roots` — understanding what makes an object reachable is prerequisite to understanding when finalization triggers
- `Reference Types (Strong, Soft, Weak, Phantom)` — `FinalReference` is a special internal reference type; `Cleaner` uses `PhantomReference`
- `Minor GC` — finalizable objects frequently survive to old-gen because they outlast the minor GC that first marks them unreachable

**Builds On This (learn these next):**
- `GC Tuning` — overuse of `finalize()` shows up directly in GC metrics and requires specific tuning strategies
- `GC Pause` — a backed-up Finalizer queue causes premature Full GCs and longer STW pauses

**Alternatives / Comparisons:**
- `java.lang.ref.Cleaner` — Java 9+ replacement that uses phantom references, avoids all finalization pitfalls
- `AutoCloseable` — the preferred deterministic resource cleanup mechanism via `try-with-resources`
- `PhantomReference` — lower-level mechanism that `Cleaner` is built on; allows cleanup without the resurrection risk of `finalize()`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A JVM callback invoked before GC reclaims │
│              │ an object's memory                        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Non-heap resources (file handles,         │
│ SOLVES       │ native memory) leak when forgotten        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Finalization forces 2 GC cycles per       │
│              │ object; the queue is single-threaded and  │
│              │ can back up, causing heap OOM             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Never — deprecated for removal (Java 18+) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Any new code; any high-frequency object   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Leak safety vs GC overhead + reliability  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The last rites no one shows up for"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cleaner → AutoCloseable → PhantomReference│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are reviewing a legacy codebase where every DAO object overrides `finalize()` to close its JDBC connection. The system handles 5,000 requests/second and has recently started experiencing random `OutOfMemoryError` bursts every few hours. Walk through the exact causal chain from finalize() overrides to the OOM — what role does the minor GC promotion heuristic play, and how would you diagnose and fix this without rewriting all DAOs at once?

**Q2.** Java's `Cleaner` API (Java 9+) solves the resurrection problem by using `PhantomReference` instead of finalizer invocation. Given that a `PhantomReference`'s referent is by definition not accessible from the cleanup action, what specifically prevents object resurrection, and how does this design trade-off affect use cases where cleanup code genuinely needs to inspect the object's state (like reading its native pointer) to perform cleanup?

