---
layout: default
title: "GC Roots"
parent: "Java & JVM Internals"
nav_order: 276
permalink: /java/gc-roots/
---
# 276 — GC Roots

`#java` `#jvm` `#memory` `#gc` `#internals` `#deep-dive`

⚡ TL;DR — The fixed set of starting points the Garbage Collector uses to determine which objects are reachable — anything not reachable from a GC root is dead and eligible for collection.

| #276 | category: Java & JVM Internals
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, Garbage Collector, Class Loader | |
| **Used by:** | GC, Memory Leak Diagnosis, jmap, Eclipse MAT | |

---

### 📘 Textbook Definition

GC Roots are a **fixed set of reference sources that the Garbage Collector treats as unconditionally live**. The GC performs a reachability traversal starting from these roots — any object reachable (directly or transitively) from a GC root is considered live and will not be collected. Any object NOT reachable from any GC root is considered dead and eligible for reclamation.

---

### 🟢 Simple Definition (Easy)

GC Roots are the **anchor points of the object graph** — the GC starts here and follows every reference chain. If it can reach your object from a root, your object survives. If nothing connects it to any root, it dies.

---

### 🔵 Simple Definition (Elaborated)

The GC doesn't guess which objects are alive — it traces. Starting from a known set of always-live references (GC roots), it follows every object reference recursively, marking everything it can reach as live. When the traversal ends, anything not marked is unreachable — no path from any root leads to it. Those objects are dead. This simple reachability model is what makes automatic memory management correct — and understanding GC roots is what makes memory leak diagnosis possible.

---

### 🔩 First Principles Explanation

**The fundamental question GC must answer:**

```
"Is this object on the heap still needed
 by any running code?"
```

**The problem — you can't ask objects:**

Objects can't self-report whether they're needed.
References form a complex graph with cycles.
Reference counting fails on circular references.

**The solution — reachability from known live points:**

> "Define a fixed set of things we KNOW are alive
>  (the roots). Everything reachable from them
>  is alive. Everything else is garbage."

```
GC ROOT REACHABILITY:

GC Root ──→ Object A ──→ Object B
                 └──→ Object C ──→ Object D

Object E ──→ Object F
(no root leads here)

Live:    A, B, C, D  (reachable from root)
Dead:    E, F        (unreachable — collect)
```

**Why this works for cycles:**

```
Object X ──→ Object Y
Object Y ──→ Object X
(circular reference — neither reachable from root)

Both X and Y are DEAD — correctly identified
Reference counting would fail here (count = 1 each)
Reachability from roots handles cycles perfectly
```

---

### ❓ Why Does This Exist — Why Before What

**Without GC Roots:**

```
Without a defined set of live anchors:

Problem 1: Reference counting
  Object X → Y → X (cycle)
  Both have ref count = 1
  Neither collected → memory leak
  C++ shared_ptr suffers this problem

Problem 2: No starting point for traversal
  GC can't traverse the heap without
  knowing where to start
  → Can't determine live vs dead objects

Problem 3: Conservative collection
  Without precise roots → GC must treat
  any bit pattern that looks like a pointer
  as a live reference → many objects
  incorrectly kept alive → memory waste

Problem 4: Memory leak diagnosis impossible
  Without knowing roots → can't answer:
  "What is holding this object alive?"
  → No path from root to object = no leak
  → Path exists = follow it to find the holder
```

**What breaks without it:**
```
1. GC correctness  → can't determine live objects
2. Cycle handling  → circular refs never collected
3. Leak diagnosis  → no path to trace
4. GC performance  → no starting point for traversal
5. Precise GC      → impossible without knowing roots
```

**With GC Roots:**
```
→ Precise reachability — no false survivors
→ Cycle handling — unreachable cycles collected
→ Leak diagnosis — follow root path to find holder
→ Correct GC — objects kept alive iff reachable
→ Foundation for all modern GC algorithms
```

---

### 🧠 Mental Model / Analogy

> Think of heap objects as **islands in an ocean**, connected by bridges (references).
>
> GC Roots are the **mainland** — guaranteed solid ground. Islands connected to the mainland (directly or via chains of other islands) are safe — inhabited, reachable, kept.
>
> Islands with NO path back to the mainland are **abandoned** — the GC demolishes them and reclaims the land.
>
> A memory leak is an island you think is abandoned but actually has a hidden bridge (reference) back to the mainland you forgot about — the GC correctly keeps it alive, but you didn't intend that.

---

### ⚙️ How It Works — What Qualifies as a GC Root

| #276 | category: Java & JVM Internals
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, Garbage Collector, Class Loader | |
| **Used by:** | GC, Memory Leak Diagnosis, jmap, Eclipse MAT | |

---

### 🔄 How It Connects

```
GC triggered (allocation pressure)
      ↓
GC identifies ALL roots:
  thread stacks + static fields +
  JNI refs + monitors + system classes
      ↓
Mark phase: traverse from every root
  follow every reference recursively
  mark each reached object as LIVE
      ↓
Sweep/Compact phase:
  unmarked objects → reclaim memory
  marked objects → survive this GC
      ↓
Young Gen survivors → age incremented
Age > threshold → promote to Old Gen
      ↓
Static field holding ref → object
never marked dead → never collected
→ This is a MEMORY LEAK
```

---

### 💻 Code Example

**Identifying GC roots with Eclipse MAT:**
```bash
# Step 1: capture heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Step 2: open in Eclipse MAT
# → Dominator Tree shows what's keeping most memory alive
# → Path to GC Roots shows WHY an object is alive

# Step 3: find leak suspects
# MAT query: "List objects with GC root path"
# Shows the exact reference chain from root to object
```

**Common memory leak — static collection as root:**
```java
public class LeakDemo {

    // STATIC FIELD = GC Root
    // Everything reachable from here lives forever
    private static final Map<String, byte[]> cache =
        new HashMap<>();

    public void processRequest(String key) {
        // Added but never removed
        // GC root → cache → byte[] arrays
        // All byte[] arrays stay alive forever
        cache.put(key, new byte[1024 * 1024]); // 1MB each
    }
}

// After 1000 requests: 1GB stuck in memory
// GC cannot collect — reachable from static root
// Heap dump + MAT: shows path →
//   GC Root (static field LeakDemo.cache)
//     → HashMap
//       → HashMap$Entry[]
//         → byte[1048576]  ← your leak
```

**Visualising the object graph:**
```java
public class RootDemo {

    // ROOT 1: static field
    static List<String> globalList = new ArrayList<>();

    public static void main(String[] args) {

        // ROOT 2: local variable in main's stack frame
        Object localObj = new Object();

        // ROOT 3: thread itself
        Thread t = new Thread(() -> {
            // ROOT 4: local var in thread's stack frame
            Object threadLocal = new Object();
            // threadLocal reachable from thread's stack root
            // survives as long as thread is running
        });
        t.start();

        // These are NOT roots — just heap objects
        Object a = new Object(); // referenced by localObj? No
        // a is only reachable if localObj references it
        // localObj doesn't → a is a GC candidate immediately
    }
}
```

**Finding GC root path programmatically:**
```java
// Using JVM TI or diagnostic tools to trace root paths
// In production: use jcmd + MAT instead

// Simulating root analysis logic:
public class ReachabilityDemo {

    static Object staticRoot = new Object();  // ROOT

    public static void main(String[] args) {
        Object a = new Object();   // root: stack frame
        Object b = new Object();   // root: stack frame

        // Create reference: a → c
        // c is reachable via root(a) → c
        Object c = new Object();

        // Now remove stack reference to c
        // but keep it reachable via a
        // (conceptual — in real code a would hold ref to c)

        // d has NO reference from any root
        Object d = new Object();
        d = null;  // only reference gone → d is GC eligible
                   // root: stack frame had d, now null
                   // d is UNREACHABLE → eligible for collection
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Setting reference to null frees memory" | It removes ONE reference — object freed only if NO other root path exists |
| "Local variables are always GC roots" | Only local vars in **active stack frames** — completed methods' vars are gone |
| "Static fields are only roots if used" | Static fields are roots **always** — as long as class is loaded |
| "Circular references cause memory leaks" | NOT in Java — GC uses reachability, not ref counting; unreachable cycles collected |
| "GC roots are in the heap" | Roots are **outside the heap** — stack, static storage, JNI; they POINT INTO heap |
| "More roots = slower GC" | More REACHABLE objects = slower GC; root count itself is small |

---

### 🔥 Pitfalls in Production

**1. Static collections — silent heap growth**
```java
// Classic leak pattern in every codebase
public class UserSessionManager {
    // Static = GC Root = never collected
    private static Map<String, UserSession> sessions
        = new ConcurrentHashMap<>();

    public void addSession(String id, UserSession s) {
        sessions.put(id, s); // grows forever
    }
    // Missing: removeSession() called on logout/expiry

    // Fix: use expiring cache
    private static Cache<String, UserSession> sessions =
        Caffeine.newBuilder()
            .expireAfterAccess(30, TimeUnit.MINUTES)
            .build();
}
```

**2. Listener/callback registration leaks**
```java
// Registering listener without deregistering
public class EventService {
    // Static list = GC root
    private static List<EventListener> listeners
        = new ArrayList<>();

    public void register(EventListener l) {
        listeners.add(l);   // object now reachable from root
    }
    // No unregister() → listeners accumulate
    // All objects reachable FROM listeners also stuck

    // Fix: WeakReference allows GC when listener
    // has no other strong references
    private static List<WeakReference<EventListener>>
        listeners = new ArrayList<>();
}
```

**3. ThreadLocal leaks in thread pools**
```java
// ThreadLocal values are GC roots
// (reachable from Thread object → ThreadLocalMap)
// Thread pool threads NEVER die
// → ThreadLocal values NEVER collected

static ThreadLocal<LargeObject> tl = new ThreadLocal<>();

// In request handler:
tl.set(new LargeObject()); // stored in thread's root
// ... handle request ...
// MISSING: tl.remove()
// Thread returns to pool — ThreadLocal still set
// LargeObject reachable from thread root → never GC'd
// Next request gets WRONG LargeObject value too

// Fix: always remove in finally block
try {
    tl.set(new LargeObject());
    handleRequest();
} finally {
    tl.remove(); // breaks root reference → GC eligible
}
```

---

### 🔗 Related Keywords

- `Heap Memory` — where GC root reachability analysis operates
- `Garbage Collector` — uses roots to determine live objects
- `Minor GC / Major GC` — both start reachability from roots
- `Mark Phase` — the traversal from roots that marks live objects
- `Memory Leak` — unintended root path keeping object alive
- `Static Fields` — most common root type causing leaks
- `ThreadLocal` — root path through Thread object
- `WeakReference` — reference that does NOT count as root path
- `Eclipse MAT` — tool that shows path from object to GC root
- `jmap` — captures heap dump for root analysis

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Fixed live anchors the GC traces from —  │
│              │ reachable = live, unreachable = garbage   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing memory leaks — always ask:     │
│              │ "What root path is keeping this alive?"   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never store long-lived objects in static  │
│              │ collections without expiry — static       │
│              │ fields are permanent GC roots             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "If the GC can walk from any root to      │
│              │  your object — it lives. If not —         │
│              │  it dies. Memory leaks are surprise       │
│              │  root paths you forgot about"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mark Phase → Weak References →            │
│              │ Minor GC → Major GC → Eclipse MAT →       │
│              │ Memory Leak Patterns                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring singleton bean holds a reference to a request-scoped object that was injected into it. The request is long gone. Why is the request-scoped object still alive — what is the root path keeping it in memory — and how does Spring's scoped proxy pattern solve this?

**Q2.** You use a `ThreadLocal<Connection>` to store database connections in a thread pool of 50 threads. Each connection object holds a reference to a large metadata cache. The pool threads never die. Draw the complete root path from GC root to the metadata cache — and explain why this is a leak even if you think you're "done" with the connection.

---