---
layout: default
title: "Reference Types (Strong, Soft, Weak, Phantom)"
parent: "Java & JVM Internals"
nav_order: 17
permalink: /java/reference-types/
number: "017"
category: JVM Internals
difficulty: ★★★
depends_on: JVM, Heap Memory, GC Roots, Object Header, Young Generation
used_by: GC, G1GC, ZGC, Parallel GC, Memory Leak Diagnosis
tags: #java, #jvm, #memory, #gc, #internals, #deep-dive
---

# 017 — Reference Types (Strong, Soft, Weak, Phantom)

`#java` `#jvm` `#memory` `#gc` `#internals` `#deep-dive`

⚡ TL;DR — Four reference strengths that give developers control over how aggressively the GC can collect an object — from "never collect" to "collect immediately" to "notify me after collection."

| #017 | Category: JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, GC Roots, Object Header, Young Generation | |
| **Used by:** | GC, G1GC, ZGC, Parallel GC, Memory Leak Diagnosis | |

---

### 📘 Textbook Definition

Java defines four reference strengths that control GC eligibility: **Strong Reference** (normal reference — object never collected while reachable), **Soft Reference** (`SoftReference<T>` — collected only under memory pressure), **Weak Reference** (`WeakReference<T>` — collected at next GC regardless of memory), and **Phantom Reference** (`PhantomReference<T>` — collected after finalization, used for cleanup notification). All non-strong references are managed via `java.lang.ref` package and work with `ReferenceQueue` for post-collection callbacks.

---

### 🟢 Simple Definition (Easy)

Java gives you four levels of "how much do you want to hold onto this object" — from "keep it forever" (strong) to "let go when memory is tight" (soft) to "let go at next GC" (weak) to "just tell me after it's gone" (phantom).

---

### 🔵 Simple Definition (Elaborated)

By default, every Java reference is strong — the GC will never collect an object you can reach. But sometimes you want a cache that automatically shrinks under memory pressure, or a map that doesn't prevent its keys from being collected, or a callback when an object is cleaned up. The four reference types let you express these intentions to the GC — it then makes collection decisions based on both reachability AND reference strength.

---

### 🔩 First Principles Explanation

**The problem — strong references are all-or-nothing:**

```
Strong reference model:
  Either you hold a ref → object lives forever
  Or you null the ref   → object dies next GC

No middle ground:
  "Keep if memory is available, drop if tight"  → impossible
  "Don't prevent collection but use if alive"   → impossible
  "Notify me when object is collected"          → impossible
```

**The insight:**

> "Let the developer express the STRENGTH of their
>  interest in an object. GC honours that strength
>  relative to memory pressure and collection cycles."

**The four levels of GC contract:**

```
Strong  → "I need this — never collect"
Soft    → "Keep if you can — collect if OOM approaching"
Weak    → "I'll use it if it's there — collect freely"
Phantom → "I don't need it — just tell me when it's gone"
```

---

### ❓ Why Does This Exist — Why Before What

**Without reference types:**

```
Problem 1: Cache implementation impossible
  Strong refs → cache grows until OOM
  Null refs   → cache always empty, defeats purpose
  Need: "keep while memory available" → SoftReference

Problem 2: Canonical maps leak
  WeakHashMap needs WeakReference on keys
  Without it: map holds strong ref to key
  Key never GC'd even if no other ref exists
  → Every entry added to map = permanent memory

Problem 3: Resource cleanup unreliable
  No way to hook into GC collection event
  finalize() is broken (ordering, resurrection)
  Need: "notify me after collection" → PhantomReference
  Used by: Cleaner API, DirectByteBuffer cleanup

Problem 4: Observer pattern leaks
  Listener registered with strong ref
  Subject keeps listener alive even after
  listener's owner is gone
  Need: "listen but don't prevent collection"
  → WeakReference on listener
```

**What breaks without them:**
```
1. Memory-sensitive caches → OOM or always empty
2. Canonical maps          → memory leaks on key insertion
3. Native resource cleanup → leaks file handles, sockets
4. Observer/listener maps  → retain dead listeners forever
5. Off-heap memory mgmt    → DirectByteBuffer can't clean up
```

---

### 🧠 Mental Model / Analogy

> Think of your relationship with a borrowed library book:
>
> **Strong Reference** — You OWN the book. Library cannot take it back. Ever.
>
> **Soft Reference** — You're BORROWING it indefinitely. Library lets you keep it until they desperately need shelf space (memory pressure). Then they ask for it back.
>
> **Weak Reference** — You've made a NOTE of where the book is. You can read it IF it's still on the shelf. But the library can shelve/remove it any time — they don't check with you.
>
> **Phantom Reference** — The book is already gone. You just want the library to **notify you** once they've fully processed its removal (cleaned up) so you can update your records.

---

### ⚙️ How It Works — Collection Behaviour

| #017 | Category: JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, GC Roots, Object Header, Young Generation | |
| **Used by:** | GC, G1GC, ZGC, Parallel GC, Memory Leak Diagnosis | |

---

### 🔄 How It Connects

```
Object created → strong ref held
      ↓
Strong ref nulled / goes out of scope
      ↓
Only SoftReference remains?
  → Survives until memory pressure
  → Cleared before OOM

Only WeakReference remains?
  → Eligible immediately
  → Cleared at next GC

Only PhantomReference remains?
  → Already dead to GC
  → Enqueued in ReferenceQueue
  → Your cleanup code runs

ReferenceQueue
  → poll() returns cleared reference
  → trigger cleanup: close file,
    free native memory, log, etc.
```

---

### 💻 Code Example

**Strong Reference — default, nothing special:**
```java
// Every normal Java variable is a strong reference
Object obj = new Object();  // strong ref
// GC will NEVER collect obj while this variable lives
obj = null; // strong ref removed → eligible for GC
```

**SoftReference — memory-sensitive cache:**
```java
import java.lang.ref.SoftReference;

public class ImageCache {
    // Values are SoftReferences — GC clears under pressure
    private final Map<String, SoftReference<BufferedImage>>
        cache = new HashMap<>();

    public void put(String key, BufferedImage img) {
        cache.put(key, new SoftReference<>(img));
    }

    public BufferedImage get(String key) {
        SoftReference<BufferedImage> ref = cache.get(key);
        if (ref == null) return null;

        BufferedImage img = ref.get(); // returns null if GC cleared it
        if (img == null) {
            cache.remove(key); // clean up dead entry
        }
        return img; // may be null — caller must handle cache miss
    }
}
// Under memory pressure: JVM clears SoftReferences
// → images evicted → app reloads them
// → no OOM, automatic cache sizing
```

**WeakReference — WeakHashMap canonical map:**
```java
import java.lang.ref.WeakReference;

public class WeakRefDemo {

    public static void main(String[] args) throws Exception {
        Object obj = new Object();
        WeakReference<Object> weakRef = new WeakReference<>(obj);

        System.out.println(weakRef.get()); // not null — obj alive

        obj = null;  // remove strong reference
        System.gc(); // suggest GC (not guaranteed but likely in demo)

        Thread.sleep(100);

        System.out.println(weakRef.get()); // null — obj collected
        // WeakReference.get() returns null once GC collected obj
    }
}

// WeakHashMap: keys are WeakReferences
// When key has no strong ref outside the map
// → key collected by GC → entry auto-removed from map
Map<Object, String> map = new WeakHashMap<>();
Object key = new Object();
map.put(key, "value");
System.out.println(map.size()); // 1

key = null;
System.gc();
Thread.sleep(100);
System.out.println(map.size()); // 0 — entry auto-removed
```

**PhantomReference — post-collection cleanup:**
```java
import java.lang.ref.*;

public class PhantomCleanup {

    static ReferenceQueue<Object> queue =
        new ReferenceQueue<>();

    // Track what to clean up when object is collected
    static class CleanupPhantom extends PhantomReference<Object> {
        private final String resourceName;

        CleanupPhantom(Object ref, String resourceName) {
            super(ref, queue);
            this.resourceName = resourceName;
        }

        void cleanup() {
            System.out.println("Cleaning up: " + resourceName);
            // close file handles, free native memory, etc.
        }
    }

    public static void main(String[] args) throws Exception {
        Object obj = new Object();
        CleanupPhantom phantom =
            new CleanupPhantom(obj, "native-resource-42");

        // PhantomReference.get() ALWAYS returns null
        System.out.println(phantom.get()); // null

        obj = null; // remove strong ref
        System.gc();
        Thread.sleep(100);

        // Poll queue for collected objects
        CleanupPhantom ref = (CleanupPhantom) queue.poll();
        if (ref != null) {
            ref.cleanup(); // "Cleaning up: native-resource-42"
        }
    }
}
// This is how Java.lang.ref.Cleaner works (Java 9+)
// Used by DirectByteBuffer to free off-heap memory
```

**Java 9+ Cleaner — PhantomReference made easy:**
```java
import java.lang.ref.Cleaner;

public class NativeResource implements AutoCloseable {
    private static final Cleaner cleaner =
        Cleaner.create();

    private final long nativeHandle;
    private final Cleaner.Cleanable cleanable;

    public NativeResource(long handle) {
        this.nativeHandle = handle;
        // Register cleanup action — runs when this object
        // becomes phantom reachable
        // IMPORTANT: action must NOT hold ref to outer class
        // (would prevent collection!)
        long h = handle;
        this.cleanable = cleaner.register(this,
            () -> freeNative(h));
    }

    @Override
    public void close() {
        cleanable.clean(); // explicit cleanup — best path
    }

    private static void freeNative(long handle) {
        System.out.println("Freeing native handle: " + handle);
        // actual native cleanup
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "WeakReference = SoftReference" | Weak collected at **next GC**; Soft collected only under **memory pressure** |
| "PhantomReference.get() returns the object" | Always returns **null** — object is already dead |
| "SoftReference is reliable for caching" | JVM decides WHEN to clear — not guaranteed to survive specific duration |
| "WeakHashMap prevents all leaks" | Only if keys have **no other strong references** outside the map |
| "finalize() is better than PhantomReference" | finalize() is **deprecated** — unpredictable order, can resurrect objects, Cleaner is the replacement |
| "Setting ref = null clears SoftReference" | Only if that was the **last strong reference** — other strong refs keep object alive |

---

### 🔥 Pitfalls in Production

**1. SoftReference eviction order is JVM-specific**
```java
// JVM may clear SoftReferences in any order
// HotSpot clears least-recently-used first
// BUT: this is not guaranteed by spec

// Don't build systems that depend on WHICH
// SoftReferences are cleared first
// Use Caffeine/Guava Cache instead of manual
// SoftReference caches — they have defined eviction policies
Cache<String, Image> cache = Caffeine.newBuilder()
    .maximumSize(1000)
    .expireAfterAccess(10, TimeUnit.MINUTES)
    .build();
```

**2. PhantomReference cleanup thread blocking**
```java
// ReferenceQueue polling must happen on a dedicated thread
// If you block on cleanup → GC can't enqueue new refs
// → Phantom refs pile up → native memory not freed

// BAD: polling in request thread
Reference<?> ref = queue.remove(); // blocks!
cleanup(ref);

// GOOD: dedicated daemon cleanup thread
Thread cleanupThread = new Thread(() -> {
    while (true) {
        try {
            Reference<?> ref = queue.remove(1000); // timeout
            if (ref instanceof CleanupPhantom cp) {
                cp.cleanup();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
});
cleanupThread.setDaemon(true);
cleanupThread.start();
```

**3. WeakHashMap value holding key**
```java
// Classic subtle leak:
WeakHashMap<Key, Value> map = new WeakHashMap<>();

class Value {
    Key key; // Value holds reference back to Key!
}

Key k = new Key();
Value v = new Value();
v.key = k;         // Value → Key (strong ref!)
map.put(k, v);

k = null;
// Expected: entry removed (key weakly reachable)
// Actual: entry STAYS
// Why: map → Value (strong) → Key (strong via v.key)
//      Key is strongly reachable via Value!
//      WeakHashMap entry never removed → LEAK

// Fix: never store key reference inside value
```

---

### 🔗 Related Keywords

- `GC Roots` — strong references from roots prevent collection
- `Garbage Collector` — honours reference strength during collection
- `ReferenceQueue` — notification mechanism for collected references
- `WeakHashMap` — uses WeakReference on keys for auto-cleanup
- `Cleaner` — Java 9+ PhantomReference-based cleanup API
- `SoftReference` — memory-sensitive caching building block
- `finalize()` — deprecated predecessor to PhantomReference
- `DirectByteBuffer` — uses PhantomReference to free off-heap memory
- `Caffeine` — production cache built on top of reference semantics
- `Memory Leak` — often caused by unintended strong references

---

### 📌 Quick Reference Card


```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Four GC collection strengths: Strong      │
│              │ (never), Soft (memory pressure), Weak     │
│              │ (next GC), Phantom (after collection)     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Soft: memory-sensitive cache              │
│              │ Weak: canonical maps, observers           │
│              │ Phantom: native resource cleanup          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use SoftReference as primary cache  │
│              │ strategy — use Caffeine with defined      │
│              │ eviction policy instead                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reference types let you say how much you │
│              │  care — GC respects that and collects     │
│              │  when your interest level allows it"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ReferenceQueue → Cleaner API →            │
│              │ WeakHashMap → Caffeine Cache →            │
│              │ DirectByteBuffer cleanup                  │
└──────────────────────────────────────────────────────────┘
```
---
### 🧠 Think About This Before We Continue

**Q1.** You're building an event bus where listeners register to receive events. You use a `List<WeakReference<EventListener>>` to store listeners. A developer complains that their listener stops receiving events even though their code is still running. What is happening — and what does this reveal about the relationship between WeakReference and object lifecycle management?

**Q2.** `DirectByteBuffer` allocates memory off-heap (outside JVM heap). The JVM heap holds only the `DirectByteBuffer` object itself — a tiny wrapper. When the wrapper is collected, the off-heap memory must also be freed. There is no Java destructor. Walk through exactly how Java uses PhantomReference and ReferenceQueue to solve this — and what happens if the cleanup thread is slow?

---