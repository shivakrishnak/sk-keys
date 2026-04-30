---
layout: default
title: "Heap Memory"
parent: "Java & JVM Internals"
nav_order: 7
permalink: /java/heap-memory/
---
# 007 — Heap Memory

`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`

⚡ TL;DR — The JVM's shared memory region where all objects live, managed automatically by the Garbage Collector across generational spaces.

| #007 | Category: JVM Memory | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Stack Memory | |
| **Used by:** | Every object allocation, GC, Spring, Hibernate | |

---

### 📘 Textbook Definition

The Java Heap is a **shared, runtime memory region** managed by the JVM where all object instances and arrays are allocated. It is divided into generational spaces — Young Generation (Eden + Survivor spaces) and Old Generation — based on object lifetime. Memory is reclaimed automatically by the Garbage Collector when objects become unreachable.

---

### 🟢 Simple Definition (Easy)

The heap is **where all your objects live**. Every time you write `new Something()`, that object goes on the heap. The JVM's Garbage Collector periodically cleans up objects that are no longer needed.

---

### 🔵 Simple Definition (Elaborated)

Unlike stack memory which is per-thread and self-cleaning, the heap is a **single shared pool** across all threads — every object created by any thread lands here. Because objects have unpredictable lifetimes (you can't know at method-exit time if an object is still referenced elsewhere), the JVM needs a dedicated system — the Garbage Collector — to find and reclaim unreachable objects. The heap is structured into regions based on how long objects typically live, which makes GC dramatically more efficient.

---

### 🔩 First Principles Explanation

**The problem:**

Stack memory cleans itself — method exits, frame gone. But objects can outlive the method that created them:

java

```java
public List<String> createList() {
    List<String> list = new ArrayList<>(); // created here
    list.add("item");
    return list; // but LIVES BEYOND this method
}
// method exits → stack frame gone
// but list object must survive → can't be on stack
```

**The deeper problem:**

Objects have **unpredictable lifetimes**. Some die immediately, some live for the entire application lifetime. You can't know at compile time when to free them.

**The insight — two observations about object lifetimes:**

> **The Generational Hypothesis:** "Most objects die young."

Empirically proven across programs — the vast majority of objects become unreachable within milliseconds of creation (think temporary loop variables, builder objects, DTOs).

**The solution:**

Divide heap into generations. Collect the young generation frequently and cheaply. Promote survivors to older generations. Collect old generation rarely.

```
ALLOCATION RATE vs SURVIVAL RATE
─────────────────────────────────────────────────────
Objects allocated: ████████████████████  (high)
Objects surviving: ██                    (very low)

→ Most GC work happens in a small space (Young Gen)
→ Old Gen collects rarely → less Stop-The-World pauses
```

---

### 🧠 Mental Model / Analogy

> Think of the heap as a **city with two districts**:
> 
> **Young district (Eden + Survivor areas)** — a fast-moving neighbourhood. New residents (objects) arrive constantly. Most leave quickly. Cleanup crews (Minor GC) sweep through frequently but it's fast because the area is small.
> 
> **Old district (Old Gen / Tenured)** — established residents who've proven they're staying long-term. Cleanup here (Major GC) is rare but takes longer because the district is large.
> 
> **Metaspace** — the city's zoning office. Stores blueprints (class definitions), not residents (objects).

---

### ⚙️ How It Works — Heap Structure

---

### ⚙️ Object Allocation Flow — What Happens on `new`

```
new Order(42)
      ↓
┌─────────────────────────────────────────────────────────┐
│  Step 1: TLAB Check                                     │
│  Each thread has a Thread Local Allocation Buffer        │
│  (a private chunk of Eden)                              │
│  → Allocate from TLAB — no synchronization needed       │
│  → Just bump a pointer: ptr += objectSize               │
│  → Extremely fast (~nanoseconds)                        │
└─────────────────────────────────────────────────────────┘
      ↓ (TLAB full?)
┌─────────────────────────────────────────────────────────┐
│  Step 2: New TLAB from Eden                             │
│  Request fresh TLAB chunk from Eden space               │
│  (synchronized but infrequent)                          │
└─────────────────────────────────────────────────────────┘
      ↓ (Eden full?)
┌─────────────────────────────────────────────────────────┐
│  Step 3: Minor GC triggered                             │
│  • Scan Young Gen for live objects                      │
│  • Dead objects → reclaimed immediately                 │
│  • Live objects → copied to Survivor space              │
│  • Age incremented per GC survived                      │
└─────────────────────────────────────────────────────────┘
      ↓ (object age > threshold, default 15?)
┌─────────────────────────────────────────────────────────┐
│  Step 4: Promotion to Old Gen                           │
│  Object copied to Old Generation                        │
│  Will only be collected by Major/Full GC now            │
└─────────────────────────────────────────────────────────┘
      ↓ (object too large for Young Gen?)
┌─────────────────────────────────────────────────────────┐
│  Step 5: Direct Old Gen allocation                      │
│  Large objects (arrays, large strings) bypass           │
│  Young Gen entirely → go straight to Old Gen            │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects

```
new Object()
     ↓
[Heap Memory — Eden Space]   ← object born here
     ↓ survives Minor GC
[Survivor Space]             ← object ages here
     ↓ age > threshold
[Old Generation]             ← long-lived objects here
     ↓ no more references
[GC — reclaims memory]       ← object dies here
     ↑
  [Stack Memory]             ← holds reference to heap object
  [Metaspace]                ← holds class definition of object
```

---

### 💻 Code Example

**Visualizing allocation and GC:**

java

```java
public class HeapDemo {
    public static void main(String[] args) throws Exception {

        // These die immediately — Eden allocated, Minor GC reclaims
        for (int i = 0; i < 1_000_000; i++) {
            String s = "temp-" + i;  // allocated in Eden
            // s goes out of scope → unreachable → GC candidate
        }

        // This survives — promoted to Old Gen
        List<String> longLived = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            longLived.add("item-" + i);
        }
        // longLived reference kept → objects survive GC cycles
        // → promoted to Old Gen after enough Minor GCs

        System.out.println("Long lived: " + longLived.size());
    }
}
```

bash

```bash
# Run with GC logging to see heap in action
java -Xms256m -Xmx512m \
     -XX:+PrintGCDetails \
     -XX:+PrintGCDateStamps \
     -Xlog:gc*:file=gc.log \
     HeapDemo

# GC log output (simplified):
# [GC (Allocation Failure)         ← Eden full
#   [PSYoungGen: 65536K→8192K]     ← Young Gen before→after
#   65536K→16384K                  ← Total heap before→after
#   0.0045 secs]                   ← pause duration
```

**Heap inspection at runtime:**

java

```java
public class HeapInspect {
    public static void main(String[] args) {
        Runtime rt = Runtime.getRuntime();

        // Force GC to get accurate reading
        System.gc();

        long max   = rt.maxMemory();     // -Xmx value
        long total = rt.totalMemory();   // currently allocated from OS
        long free  = rt.freeMemory();    // free within allocated
        long used  = total - free;       // actually used

        System.out.printf("Max:   %d MB%n", max   / 1024 / 1024);
        System.out.printf("Used:  %d MB%n", used  / 1024 / 1024);
        System.out.printf("Free:  %d MB%n", free  / 1024 / 1024);
    }
}
```

**Triggering and observing OutOfMemoryError:**

java

```java
public class OOMDemo {
    public static void main(String[] args) {
        List<byte[]> leak = new ArrayList<>();
        try {
            while (true) {
                // Allocate 1MB chunks, hold reference → can't GC
                leak.add(new byte[1024 * 1024]);
            }
        } catch (OutOfMemoryError e) {
            System.out.println("OOM after: " + leak.size() + " MB");
            // GC cannot help — objects ARE reachable (leak holds them)
        }
    }
}
```

bash

```bash
# Capture heap dump automatically on OOM:
java -Xmx256m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/heap.hprof \
     OOMDemo

# Analyse dump:
# Eclipse MAT, VisualVM, or IntelliJ Profiler
# → find which objects are consuming most memory
# → trace GC roots holding them alive
```

**Escape Analysis — JVM can put objects ON stack:**

java

```java
// JVM detects this object never escapes the method
// May allocate on STACK instead of heap → zero GC pressure
public int compute() {
    Point p = new Point(3, 4);    // JVM may stack-allocate this
    return p.x + p.y;             // p never escapes this method
}
// -XX:+DoEscapeAnalysis (on by default Java 8+)

// Contrast — object ESCAPES → must be heap allocated
public Point createPoint() {
    Point p = new Point(3, 4);
    return p;                      // escapes → heap allocated
}
```

---

### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Heap is slow, stack is fast"|New object allocation via TLAB is ~nanoseconds; heap isn't inherently slow|
|"GC runs on a schedule"|GC is triggered by **allocation pressure** — when spaces fill up|
|"`System.gc()` forces GC"|It's a **hint** — JVM may ignore it|
|"Old Gen objects are permanent"|They're collected by Major/Full GC — just less frequently|
|"Metaspace is part of heap"|Metaspace is **off-heap** (native memory) — not subject to `-Xmx`|
|"More heap = better performance"|Too much heap → longer GC pause times when it does collect|

---

### 🔥 Pitfalls in Production

**1. Memory leak — references held unintentionally**

java

```java
// Classic leak — static collection grows forever
public class SessionCache {
    // static = lives as long as class = application lifetime
    private static Map<String, UserSession> cache = new HashMap<>();

    public void addSession(String id, UserSession session) {
        cache.put(id, session); // ← added but never removed
        // sessions accumulate → Old Gen fills → Full GC → OOM
    }
}

// Fix: use WeakHashMap or explicit eviction
private static Map<String, UserSession> cache =
    Collections.synchronizedMap(new WeakHashMap<>());
// WeakHashMap: entries GC'd when key has no strong references
```

**2. Heap sizing — the right balance**

bash

```bash
# Too small: frequent GC pauses, possible OOM
java -Xmx256m myapp    # GC runs constantly

# Too large: rare but very long GC pauses
java -Xmx32g myapp     # Full GC = tens of seconds pause

# Sweet spot for latency-sensitive apps:
# -Xmx no larger than needed
# Use G1GC or ZGC for large heaps (ZGC: sub-millisecond pauses)
java -Xmx4g -XX:+UseZGC myapp

# Same min/max to prevent resize GC:
java -Xms2g -Xmx2g myapp
```

**3. Large object allocation — bypasses Young Gen**

java

```java
// This goes straight to Old Gen
byte[] buffer = new byte[10 * 1024 * 1024]; // 10MB

// Old Gen fills → Major GC → Stop-The-World pause
// Fix: reuse large buffers via pooling
// Or: use off-heap ByteBuffer (DirectByteBuffer)
ByteBuffer offHeap = ByteBuffer.allocateDirect(10 * 1024 * 1024);
// Off-heap: not subject to GC, manual lifecycle management
```

**4. Premature promotion — survivor space too small**

bash

```bash
# If objects promoted to Old Gen too quickly:
# Old Gen fills → frequent Major GC

# Tune survivor space ratio:
-XX:SurvivorRatio=8      # Eden:Survivor = 8:1:1
-XX:MaxTenuringThreshold=15  # survive 15 Minor GCs before promotion

# Diagnosis: check if objects are aging properly
-XX:+PrintTenuringDistribution
```

---

### 🔗 Related Keywords

- `Stack Memory` — holds references to heap objects
- `GC (Garbage Collector)` — reclaims unreachable heap objects
- `Minor GC` — collects Young Generation
- `Major GC / Full GC` — collects Old Generation
- `Metaspace` — class metadata (off-heap, not heap)
- `TLAB` — per-thread allocation buffer in Eden
- `Escape Analysis` — JVM optimization; may avoid heap allocation
- `OutOfMemoryError` — heap exhausted
- `WeakReference` — heap object eligible for GC despite reference
- `G1GC / ZGC` — modern GC algorithms for large heaps
- `jmap / MAT` — tools to analyse heap contents

---

### 📌 Quick Reference Card

---

**Entry 007 complete.**

### 🧠 Think About This Before We Continue

**Q1.** You have a Spring Boot app with a memory leak. Heap usage climbs steadily over 6 hours then OOM. You take a heap dump. Walk me through — step by step — how you would diagnose which objects are leaking and what's holding them alive.

**Q2.** Escape Analysis allows the JVM to allocate objects on the stack instead of the heap. What are the conditions an object must meet for this optimization to apply — and why can't the JVM always do this?

Next up: **008 — Metaspace** — the off-heap region that replaced PermGen, what lives there, why it matters for long-running apps, and how class loading connects to native memory.
