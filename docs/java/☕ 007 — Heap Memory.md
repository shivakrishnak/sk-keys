---
layout: default
title: "007 — Heap Memory"
parent: "Java Fundamentals"
nav_order: 7
permalink: /java/007-heap-memory/
---
# â˜• Heap Memory

ðŸ·ï¸ Tags â€” #java #jvm #memory #gc #internals #intermediate

âš¡ TL;DR â€” The JVM's shared memory region where all objects live, managed automatically by the Garbage Collector across generational spaces. 

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #007  â”‚ Category: JVM Memory     â”‚ Difficulty: â˜…â˜…â˜†   â”‚
â”‚ Depends on: JVM, GC, Stack Memory â”‚ Used by: Every   â”‚
â”‚ object allocation, GC, Spring,    â”‚ Hibernate        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

The Java Heap is a **shared, runtime memory region** managed by the JVM where all object instances and arrays are allocated. It is divided into generational spaces â€” Young Generation (Eden + Survivor spaces) and Old Generation â€” based on object lifetime. Memory is reclaimed automatically by the Garbage Collector when objects become unreachable.

---

#### ðŸŸ¢ Simple Definition (Easy)

The heap is **where all your objects live**. Every time you write `new Something()`, that object goes on the heap. The JVM's Garbage Collector periodically cleans up objects that are no longer needed.

---

#### ðŸ”µ Simple Definition (Elaborated)

Unlike stack memory which is per-thread and self-cleaning, the heap is a **single shared pool** across all threads â€” every object created by any thread lands here. Because objects have unpredictable lifetimes (you can't know at method-exit time if an object is still referenced elsewhere), the JVM needs a dedicated system â€” the Garbage Collector â€” to find and reclaim unreachable objects. The heap is structured into regions based on how long objects typically live, which makes GC dramatically more efficient.

---

#### ðŸ”© First Principles Explanation

**The problem:**

Stack memory cleans itself â€” method exits, frame gone. But objects can outlive the method that created them:

java

```java
public List<String> createList() {
    List<String> list = new ArrayList<>(); // created here
    list.add("item");
    return list; // but LIVES BEYOND this method
}
// method exits â†’ stack frame gone
// but list object must survive â†’ can't be on stack
```

**The deeper problem:**

Objects have **unpredictable lifetimes**. Some die immediately, some live for the entire application lifetime. You can't know at compile time when to free them.

**The insight â€” two observations about object lifetimes:**

> **The Generational Hypothesis:** "Most objects die young."

Empirically proven across programs â€” the vast majority of objects become unreachable within milliseconds of creation (think temporary loop variables, builder objects, DTOs).

**The solution:**

Divide heap into generations. Collect the young generation frequently and cheaply. Promote survivors to older generations. Collect old generation rarely.

```
ALLOCATION RATE vs SURVIVAL RATE
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Objects allocated: â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  (high)
Objects surviving: â–ˆâ–ˆ                    (very low)

â†’ Most GC work happens in a small space (Young Gen)
â†’ Old Gen collects rarely â†’ less Stop-The-World pauses
```

---

#### ðŸ§  Mental Model / Analogy

> Think of the heap as a **city with two districts**:
> 
> **Young district (Eden + Survivor areas)** â€” a fast-moving neighbourhood. New residents (objects) arrive constantly. Most leave quickly. Cleanup crews (Minor GC) sweep through frequently but it's fast because the area is small.
> 
> **Old district (Old Gen / Tenured)** â€” established residents who've proven they're staying long-term. Cleanup here (Major GC) is rare but takes longer because the district is large.
> 
> **Metaspace** â€” the city's zoning office. Stores blueprints (class definitions), not residents (objects).

---

#### âš™ï¸ How It Works â€” Heap Structure

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        JVM HEAP                             â”‚
â”‚                                                             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚                  YOUNG GENERATION                    â”‚   â”‚
â”‚  â”‚                                                      â”‚   â”‚
â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚   â”‚
â”‚  â”‚  â”‚      EDEN       â”‚  â”‚Survivor 0â”‚  â”‚Survivor 1â”‚    â”‚   â”‚
â”‚  â”‚  â”‚                 â”‚  â”‚  (From)  â”‚  â”‚   (To)   â”‚    â”‚   â”‚
â”‚  â”‚  â”‚ new objects     â”‚  â”‚          â”‚  â”‚          â”‚    â”‚   â”‚
â”‚  â”‚  â”‚ allocated here  â”‚  â”‚ age 1-N  â”‚  â”‚ (empty)  â”‚    â”‚   â”‚
â”‚  â”‚  â”‚                 â”‚  â”‚ objects  â”‚  â”‚          â”‚    â”‚   â”‚
â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚   â”‚
â”‚  â”‚         ~80%               ~10%          ~10%        â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                           â†“ promotion                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚                  OLD GENERATION                      â”‚   â”‚
â”‚  â”‚              (Tenured Space)                         â”‚   â”‚
â”‚  â”‚                                                      â”‚   â”‚
â”‚  â”‚  Long-lived objects promoted from Young Gen          â”‚   â”‚
â”‚  â”‚  Large objects allocated directly here               â”‚   â”‚
â”‚  â”‚  Collected by Major GC / Full GC                     â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

SEPARATE (not heap):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  METASPACE (off-heap, native memory)                     â”‚
â”‚  Class metadata, method bytecode, static variables       â”‚
â”‚  (replaced PermGen in Java 8)                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš™ï¸ Object Allocation Flow â€” What Happens on `new`

```
new Order(42)
      â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Step 1: TLAB Check                                     â”‚
â”‚  Each thread has a Thread Local Allocation Buffer        â”‚
â”‚  (a private chunk of Eden)                              â”‚
â”‚  â†’ Allocate from TLAB â€” no synchronization needed       â”‚
â”‚  â†’ Just bump a pointer: ptr += objectSize               â”‚
â”‚  â†’ Extremely fast (~nanoseconds)                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“ (TLAB full?)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Step 2: New TLAB from Eden                             â”‚
â”‚  Request fresh TLAB chunk from Eden space               â”‚
â”‚  (synchronized but infrequent)                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“ (Eden full?)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Step 3: Minor GC triggered                             â”‚
â”‚  â€¢ Scan Young Gen for live objects                      â”‚
â”‚  â€¢ Dead objects â†’ reclaimed immediately                 â”‚
â”‚  â€¢ Live objects â†’ copied to Survivor space              â”‚
â”‚  â€¢ Age incremented per GC survived                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“ (object age > threshold, default 15?)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Step 4: Promotion to Old Gen                           â”‚
â”‚  Object copied to Old Generation                        â”‚
â”‚  Will only be collected by Major/Full GC now            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“ (object too large for Young Gen?)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Step 5: Direct Old Gen allocation                      â”‚
â”‚  Large objects (arrays, large strings) bypass           â”‚
â”‚  Young Gen entirely â†’ go straight to Old Gen            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ”„ How It Connects

```
new Object()
     â†“
[Heap Memory â€” Eden Space]   â† object born here
     â†“ survives Minor GC
[Survivor Space]             â† object ages here
     â†“ age > threshold
[Old Generation]             â† long-lived objects here
     â†“ no more references
[GC â€” reclaims memory]       â† object dies here
     â†‘
  [Stack Memory]             â† holds reference to heap object
  [Metaspace]                â† holds class definition of object
```

---

#### ðŸ’» Code Example

**Visualizing allocation and GC:**

java

```java
public class HeapDemo {
    public static void main(String[] args) throws Exception {

        // These die immediately â€” Eden allocated, Minor GC reclaims
        for (int i = 0; i < 1_000_000; i++) {
            String s = "temp-" + i;  // allocated in Eden
            // s goes out of scope â†’ unreachable â†’ GC candidate
        }

        // This survives â€” promoted to Old Gen
        List<String> longLived = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            longLived.add("item-" + i);
        }
        // longLived reference kept â†’ objects survive GC cycles
        // â†’ promoted to Old Gen after enough Minor GCs

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
# [GC (Allocation Failure)         â† Eden full
#   [PSYoungGen: 65536Kâ†’8192K]     â† Young Gen beforeâ†’after
#   65536Kâ†’16384K                  â† Total heap beforeâ†’after
#   0.0045 secs]                   â† pause duration
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
                // Allocate 1MB chunks, hold reference â†’ can't GC
                leak.add(new byte[1024 * 1024]);
            }
        } catch (OutOfMemoryError e) {
            System.out.println("OOM after: " + leak.size() + " MB");
            // GC cannot help â€” objects ARE reachable (leak holds them)
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
# â†’ find which objects are consuming most memory
# â†’ trace GC roots holding them alive
```

**Escape Analysis â€” JVM can put objects ON stack:**

java

```java
// JVM detects this object never escapes the method
// May allocate on STACK instead of heap â†’ zero GC pressure
public int compute() {
    Point p = new Point(3, 4);    // JVM may stack-allocate this
    return p.x + p.y;             // p never escapes this method
}
// -XX:+DoEscapeAnalysis (on by default Java 8+)

// Contrast â€” object ESCAPES â†’ must be heap allocated
public Point createPoint() {
    Point p = new Point(3, 4);
    return p;                      // escapes â†’ heap allocated
}
```

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Heap is slow, stack is fast"|New object allocation via TLAB is ~nanoseconds; heap isn't inherently slow|
|"GC runs on a schedule"|GC is triggered by **allocation pressure** â€” when spaces fill up|
|"`System.gc()` forces GC"|It's a **hint** â€” JVM may ignore it|
|"Old Gen objects are permanent"|They're collected by Major/Full GC â€” just less frequently|
|"Metaspace is part of heap"|Metaspace is **off-heap** (native memory) â€” not subject to `-Xmx`|
|"More heap = better performance"|Too much heap â†’ longer GC pause times when it does collect|

---

#### ðŸ”¥ Pitfalls in Production

**1. Memory leak â€” references held unintentionally**

java

```java
// Classic leak â€” static collection grows forever
public class SessionCache {
    // static = lives as long as class = application lifetime
    private static Map<String, UserSession> cache = new HashMap<>();

    public void addSession(String id, UserSession session) {
        cache.put(id, session); // â† added but never removed
        // sessions accumulate â†’ Old Gen fills â†’ Full GC â†’ OOM
    }
}

// Fix: use WeakHashMap or explicit eviction
private static Map<String, UserSession> cache =
    Collections.synchronizedMap(new WeakHashMap<>());
// WeakHashMap: entries GC'd when key has no strong references
```

**2. Heap sizing â€” the right balance**

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

**3. Large object allocation â€” bypasses Young Gen**

java

```java
// This goes straight to Old Gen
byte[] buffer = new byte[10 * 1024 * 1024]; // 10MB

// Old Gen fills â†’ Major GC â†’ Stop-The-World pause
// Fix: reuse large buffers via pooling
// Or: use off-heap ByteBuffer (DirectByteBuffer)
ByteBuffer offHeap = ByteBuffer.allocateDirect(10 * 1024 * 1024);
// Off-heap: not subject to GC, manual lifecycle management
```

**4. Premature promotion â€” survivor space too small**

bash

```bash
# If objects promoted to Old Gen too quickly:
# Old Gen fills â†’ frequent Major GC

# Tune survivor space ratio:
-XX:SurvivorRatio=8      # Eden:Survivor = 8:1:1
-XX:MaxTenuringThreshold=15  # survive 15 Minor GCs before promotion

# Diagnosis: check if objects are aging properly
-XX:+PrintTenuringDistribution
```

---

#### ðŸ”— Related Keywords

- `Stack Memory` â€” holds references to heap objects
- `GC (Garbage Collector)` â€” reclaims unreachable heap objects
- `Minor GC` â€” collects Young Generation
- `Major GC / Full GC` â€” collects Old Generation
- `Metaspace` â€” class metadata (off-heap, not heap)
- `TLAB` â€” per-thread allocation buffer in Eden
- `Escape Analysis` â€” JVM optimization; may avoid heap allocation
- `OutOfMemoryError` â€” heap exhausted
- `WeakReference` â€” heap object eligible for GC despite reference
- `G1GC / ZGC` â€” modern GC algorithms for large heaps
- `jmap / MAT` â€” tools to analyse heap contents

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Shared memory region for all objects,     â”‚
â”‚              â”‚ generationally structured for GC          â”‚
â”‚              â”‚ efficiency                                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Always â€” every object lives here          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Avoid heap for large buffers in           â”‚
â”‚              â”‚ latency-critical paths â€” use off-heap     â”‚
â”‚              â”‚ DirectByteBuffer instead                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Heap = shared object city; GC = the      â”‚
â”‚              â”‚  cleanup crew; generations = the          â”‚
â”‚              â”‚  efficiency trick"                        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ GC Roots â†’ Minor GC â†’ Major GC â†’          â”‚
â”‚              â”‚ G1GC â†’ ZGC â†’ Metaspace â†’ TLAB             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

**Entry 007 complete.**

#### ðŸ§  Think About This Before We Continue

**Q1.** You have a Spring Boot app with a memory leak. Heap usage climbs steadily over 6 hours then OOM. You take a heap dump. Walk me through â€” step by step â€” how you would diagnose which objects are leaking and what's holding them alive.

**Q2.** Escape Analysis allows the JVM to allocate objects on the stack instead of the heap. What are the conditions an object must meet for this optimization to apply â€” and why can't the JVM always do this?

Next up: **008 â€” Metaspace** â€” the off-heap region that replaced PermGen, what lives there, why it matters for long-running apps, and how class loading connects to native memory.
