---
layout: default
title: "Object Header"
parent: "Java & JVM Internals"
nav_order: 272
permalink: /java/object-header/
number: "0272"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Heap Memory, synchronized, Class Loader
used_by: Escape Analysis, GC Roots, synchronized, Biased Locking
related: GC Roots, synchronized, Escape Analysis, TLAB
tags:
  - java
  - jvm
  - memory
  - internals
  - deep-dive
---

# 272 — Object Header

⚡ TL;DR — Every Java object on the heap begins with a hidden header (8–16 bytes) encoding the object's GC age, lock state, identity hash code, and class pointer.

| #272 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, synchronized, Class Loader | |
| **Used by:** | Escape Analysis, GC Roots, synchronized, Biased Locking | |
| **Related:** | GC Roots, synchronized, Escape Analysis, TLAB | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The JVM needs to know several things about any object at any time, without the programmer explicitly tracking them: Is this object currently locked (for `synchronized`)? How many GC cycles has it survived (for promotion decisions)? What is its identity hash code (for `System.identityHashCode()`)? Which class is it an instance of (for `instanceof` checks and `getClass()`)? Without dedicated per-object storage for this metadata, the JVM would need external lookup tables — one map from object pointer to lock state, another for GC age, another for class type. Every operation involving an object would require a hash table lookup.

**THE BREAKING POINT:**
External lookup tables add synchronisation overhead and memory fragmentation. Object identity operations (`synchronized`, `instanceof`, hash code) are called billions of times per second. They must be O(1) with zero synchronisation cost.

**THE INVENTION MOMENT:**
Prefixing every object with a compact header that encodes all this metadata inline makes every per-object operation an O(1) pointer dereference. This is why every Java object has a header: it is the index card prepended to every object, enabling constant-time metadata access.

---

### 📘 Textbook Definition

The JVM Object Header is a hidden per-object metadata region prepended to every Java heap object before its user-visible fields. In HotSpot JVM, the header consists of two components: (1) the Mark Word (8 bytes on 64-bit JVM) — a multipurpose field whose bits encode the object's identity hash code, GC age (tenuring counter), lock state (unlocked, biased-locked, lightweight-locked, heavyweight-locked), GC forwarding pointer, and other GC flags; (2) the Klass Pointer (4–8 bytes) — a reference to the class's metadata in Metaspace. Together, the header occupies 8–16 bytes per object before any user-declared fields.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every Java object starts with a hidden system header encoding its type, lock status, and garbage collection age.

**One analogy:**
> Every item in a warehouse has a barcode sticker (Object Header) that warehouse workers (the JVM) can scan to find the item's category, storage duration, and access restrictions — without involving the item's owner (your code). You never see the sticker; the warehouse uses it constantly.

**One insight:**
The Object Header's Mark Word is the most reused piece of memory in the JVM — its bits are repurposed for identity hash, lock state, and GC forwarding pointer over the object's lifetime. Understanding the header explains: why `synchronized` on small objects is not "free" (it changes header bits), why identity hash code generation has a one-time cost (hash is stored in the header), and why Java objects have a minimum memory footprint even for empty classes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every object needs type information (what class is it an instance of?).
2. Every object needs synchronisation support (can be used as a monitor).
3. Every object needs GC tracking (how old is it? has it been moved?).
4. All three must be accessible in O(1) without external tables.

**DERIVED DESIGN:**
Invariants 1–4 together mandate per-object storage that is: fixed size (to enable pointer arithmetic to the user fields), present on every object (not optional), and densely packed (to minimise the memory tax on every object). The header must precede the user fields so that object references point to a constant offset from the header start.

**THE TRADE-OFFS:**
**Gain:** O(1) class type check, lock acquisition, hash code retrieval, GC age access — all without external lookup.
**Cost:** 8–16 bytes of memory overhead per object. For applications creating billions of small objects (Integer cache entries, small DTOs), this overhead is significant. The minimum object size on a 64-bit JVM is 16 bytes (8-byte header + 8-byte padding alignment), even for an entirely empty class.

---

### 🧪 Thought Experiment

**SETUP:**
You have a Java application creating 1 billion small objects (e.g., a trading system with 1 billion trade records, each a POJO with two int fields = 8 bytes of user data).

**WHAT HAPPENS WITHOUT OBJECT HEADER:**
The object occupies only 8 bytes (two ints). An external `HashMap<Object, Integer>` maps each object pointer to its GC age. When `synchronized(trade)` is called, the JVM looks up the lock state in another external hash table. For 1 billion objects: the external tables themselves consume gigabytes of memory. Cache miss rates for each object operation are high — the lock table and GC table are cold in CPU cache.

**WHAT HAPPENS WITH OBJECT HEADER:**
Each object occupies 16 bytes (8-byte header + 8 bytes user data). GC age, lock state, and hash code are in the header — a single pointer dereference away. For 1 billion objects: memory overhead is an extra 8 GB for headers. But every object operation is a single cache line access. The trade-off: predictable, local, fast access at the cost of fixed per-object overhead.

**THE INSIGHT:**
Per-object overhead is justified when operations on those objects are frequent. The object header trades memory for constant-time metadata access — a fundamental engineering trade-off between space and time.

---

### 🧠 Mental Model / Analogy

> The Object Header is like a UPC barcode on every product on a grocery store shelf. The barcode contains the product's category (class pointer), the item's shelf expiry counter (GC age), and a security tag status (lock state). The store's self-checkout (JVM) scans the barcode for everything it needs to know. The shopper (programmer) never handles the barcode directly.

- "UPC barcode" → the Object Header (Mark Word + Klass Pointer)
- "Product category (aisle code)" → Klass Pointer → class metadata in Metaspace
- "Shelf expiry counter" → GC age bits (tenuring threshold)
- "Security tag" → lock bits in Mark Word
- "Self-checkout scanner" → JVM runtime operations

Where this analogy breaks down: unlike a barcode, the header bits change during object lifetime — lock bits flip when synchronized; GC bits flip during collection; hash code is generated lazily on first request and then permanently stored.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every Java object secretly has a small label attached to the front of it that the Java runtime reads and writes for its own bookkeeping. You as a programmer never see or touch this label, but it enables Java to track what type of object this is, whether it's currently locked by a thread, and how old it is for garbage collection purposes.

**Level 2 — How to use it (junior developer):**
You don't interact with the Object Header directly. It matters to you when: (1) you notice that even an empty Java object consumes 16 bytes (not 0) — the header accounts for 8–16 bytes; (2) `System.identityHashCode(obj)` has a small one-time cost — because it generates and caches the hash in the header; (3) `synchronized(obj)` has a small overhead — it transitions the Mark Word through lock state changes.

**Level 3 — How it works (mid-level engineer):**
The Mark Word (8 bytes on 64-bit) uses bit encoding to multiplex multiple states. The encoding changes meaning based on the low-order bits:
- `01` = unlocked (bits encode identity hash + GC age)
- `01` + biased = biased-locked (bits encode thread ID + epoch + GC age)
- `00` = lightweight-locked (bits are a pointer to a lock record on the stack)
- `10` = heavyweight-locked (bits are a pointer to an inflated Monitor object)
- `11` = marked for GC (bits are a forwarding pointer during GC copy)

**Level 4 — Why it was designed this way (senior/staff):**
The Mark Word's bit-multiplexing design reflects a decades-long optimisation battle. Biased locking (deprecated in Java 15, removed in Java 18) assumed that a monitor was usually locked by the same thread — the thread ID was encoded in the header to avoid CAS operations for repeated locking. When wrong (multiple threads contesting), the deoptimisation cost was high. The decision to remove it in Java 18 reflected the observation that modern workloads with virtual threads and structured concurrency no longer match the "one thread dominates" assumption. This is a case where an optimisation's premise became invalid as the ecosystem evolved.

---

### ⚙️ How It Works (Mechanism)

**Mark Word States (HotSpot 64-bit):**

```
┌─────────────────────────────────────────────────────────┐
│                MARK WORD (8 bytes) LAYOUT               │
├────────────────────────────────────────┬────────────────┤
│  State                                 │  Low-order bits │
├────────────────────────────────────────┼────────────────┤
│  Unlocked (identity hash + age)        │  ...hash..age 01│
│  Biased-locked (thread + epoch + age)  │  ...tid..epoch 01│
│                                        │  (+ 1 bias bit) │
│  Lightweight-locked (stack lock ptr)   │  ptr..........00│
│  Heavyweight-locked (Monitor ptr)      │  ptr..........10│
│  Marked for GC / Forwarding ptr        │  ptr..........11│
└────────────────────────────────────────┴────────────────┘
```

**Klass Pointer:**
- On 64-bit JVM with compressed oops (`-XX:+UseCompressedOops`, default): 4 bytes
- Without compressed oops (very large heaps >32GB): 8 bytes
- Points to the class's metadata structure in Metaspace

**Object Layout in Memory:**

```
┌─────────────────────────────────────────────┐
│  JAVA OBJECT MEMORY LAYOUT (64-bit JVM)     │
├─────────────────────────────────────────────┤
│  Offset 0: Mark Word (8 bytes)              │
│  Offset 8: Klass Pointer (4 or 8 bytes)     │
│  Offset 12 or 16: First user field          │
│  ...                                        │
│  (padding to 8-byte alignment at end)       │
└─────────────────────────────────────────────┘

Example: class Point { int x; int y; }
  Mark Word:    8 bytes
  Klass Ptr:    4 bytes (compressed oops)
  int x:        4 bytes
  int y:        4 bytes
  padding:      4 bytes (align to 8-byte boundary)
  Total:       24 bytes (not 8! header adds 16 bytes)
```

**Object Size Impact:**

```
┌─────────────────────────────────────────────┐
│  OBJECT SIZES (64-bit, compressed oops)     │
├────────────────────────┬────────────────────┤
│  Class declaration     │  Heap size          │
├────────────────────────┼────────────────────┤
│  class Empty {}        │  16 bytes           │
│  class OneInt {int x;} │  16 bytes           │
│  class TwoInts         │  24 bytes           │
│  class OneRef {A a;}   │  16 bytes           │
│  class OneLong {long l}│  24 bytes           │
└────────────────────────┴────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
new MyObject() called
  → Heap allocates: header(8+4=12 bytes) + fields + padding
    ← YOU ARE HERE (header initialised: Mark Word = unlocked,
                    Klass Ptr → MyObject class in Metaspace)
  → Reference returned to caller
  → synchronized(obj) called
    → JVM reads Mark Word low bits
    → transitions Mark Word to locked state
  → Minor GC: object survives
    → GC increments age bits in Mark Word
    → if age ≥ 15 → promoted to Old Gen
  → Full GC: copying collector moves object
    → Mark Word temporarily = forwarding ptr (11 bits)
    → After move: new Mark Word at new address
```

**FAILURE PATH:**
```
Mark Word corruption (rare, often JNI bug)
  → Incorrect lock state → incorrect synchronisation
  → JVM crash with hs_err_pid crash file
  → Native code bypassing JVM safety checks
```

**WHAT CHANGES AT SCALE:**
At very large JVM heaps (>32 GB), compressed oops (`-XX:+UseCompressedOops`) cannot be used — the Klass Pointer expands to 8 bytes, increasing every object's header to 16 bytes. For applications with billions of small objects, this doubles header memory overhead. ZGC and Shenandoah handle large heaps without requiring this trade-off by using coloured pointers in the reference bits themselves.

---

### 💻 Code Example

Example 1 — Measure real object sizes with JOL (Java Object Layout):
```xml
<!-- Add JOL to pom.xml -->
<dependency>
  <groupId>org.openjdk.jol</groupId>
  <artifactId>jol-core</artifactId>
  <version>0.17</version>
</dependency>
```
```java
import org.openjdk.jol.info.ClassLayout;

public class HeaderDemo {
    static class Point {
        int x;
        int y;
    }

    public static void main(String[] args) {
        System.out.println(
            ClassLayout.parseClass(Point.class)
                       .toPrintable()
        );
        // Output:
        // OFFSET  SIZE  TYPE DESCRIPTION
        //      0     4       (object header: mark)
        //      4     4       (object header: mark - cont)
        //      8     4       (object header: class)
        //     12     4   int Point.x
        //     16     4   int Point.y
        //     20     4       (alignment/padding gap)
        // Instance size: 24 bytes
    }
}
```

Example 2 — Identity hash code stored in header:
```java
Object obj = new Object();

// First call: generates hash, stores in Mark Word
int hash1 = System.identityHashCode(obj);

// Subsequent calls: reads from Mark Word (O(1))
int hash2 = System.identityHashCode(obj);

// Once identity hash is set:
// → object CANNOT be biased-locked
// → because biased lock would overwrite hash bits
// → synchronized(obj) after identityHashCode
//    uses lightweight-lock or heavyweight-lock only
System.out.println(hash1 == hash2); // always true
```

Example 3 — Observe object header with jcmd:
```bash
# Print heap info for a running JVM
jcmd <pid> GC.heap_info

# For detailed object layout analysis:
# Use JVM with -XX:+PrintCompressedOopsMode
java -XX:+PrintCompressedOopsMode -jar myapp.jar
# Shows: HeapBaseMinAddress / Narrow oop / shift info

# Check if compressed oops are enabled
jcmd <pid> VM.flags | grep CompressedOops
```

Example 4 — Memory footprint of arrays vs objects:
```java
// Array objects also have a header + length field
// int[100] layout:
// Mark Word(8) + Klass(4) + length(4) + data(400)
//  = 416 bytes

// vs 100 Integer objects:
// 100 × 16 bytes (boxed Integer) = 1600 bytes
// → prefer int[] for large numeric data

// Verify with JOL:
System.out.println(
    ClassLayout.parseInstance(new int[10]).toPrintable()
);
```

---

### ⚖️ Comparison Table

| Object Layout | Header Size | User Fields Offset | Compressed Oops | Heap Limit |
|---|---|---|---|---|
| **64-bit + CompressedOops** | 12 bytes | offset 12 | Yes (4-byte Klass) | Up to ~32 GB |
| 64-bit, no CompressedOops | 16 bytes | offset 16 | No (8-byte Klass) | > 32 GB heaps |
| 32-bit JVM | 8 bytes | offset 8 | N/A | Up to 4 GB |
| Project Lilliput (JEP 450) | 4-8 bytes (future) | Reduced | Enhanced | Experimental |

How to choose: Always use `-XX:+UseCompressedOops` (default for heaps < 32 GB) to save 4 bytes per object in the Klass Pointer. For heaps > 32 GB, accept the full 16-byte header or split into multiple JVM instances.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "An empty Java object has 0 bytes overhead" | An empty class instance occupies 16 bytes (header=12 + padding=4), never less. |
| "synchronized(obj) is always expensive" | For lightly contended locks, biased-locked objects (Java 8–14) or lightweight-locked objects require only a Mark Word CAS — nanosecond-level overhead. |
| "Garbage collection (GC) doesn't modify objects" | GC does modify the Mark Word — it temporarily overwrites it with a forwarding pointer during object copying, then restores/updates it at the new address. |
| "Identity hash code is random every call" | It is random on FIRST call, then permanently stored in the Mark Word. After the first call, it is always the same value for the same object. |
| "Smaller classes use less memory" | Minimum object size is 16 bytes (headers + padding), regardless of how few fields the class declares. |

---

### 🚨 Failure Modes & Diagnosis

**1. Excessive Heap from Many Small Objects**

**Symptom:** Heap dump shows millions/billions of small objects consuming far more memory than a multiply-by-field count suggests.

**Root Cause:** Object header overhead (12–16 bytes) plus alignment padding inflate small objects significantly. `new Integer(1)` is 16 bytes, not 4.

**Diagnostic:**
```bash
# Heap histogram
jcmd <pid> GC.class_histogram | head -30
# Shows: instances × instance-size for each class

# JOL to see exact layout per class
java -jar jol-cli.jar internals com.example.MyClass
```

**Fix:**
```java
// BAD: many boxed Integer objects
List<Integer> ids = new ArrayList<>();
for (int i = 0; i < 1_000_000; i++) ids.add(i);

// GOOD: primitive array (no object header per element)
int[] ids = new int[1_000_000];
// Or: use IntStream, int[], Eclipse Collections Primitive
```

**Prevention:** Prefer primitives over boxed types for large collections; profile heap with class histogram before scaling.

**2. Lock Inflation Causing Unexpected Contention**

**Symptom:** Thread dumps show many threads blocked on `synchronized`; lock inflation to heavyweight Monitor not expected by the developer.

**Root Cause:** Multiple threads contesting the same object's lock causes Mark Word transition from biased/lightweight to heavyweight (inflated Monitor), which involves kernel synchronisation.

**Diagnostic:**
```bash
# Thread dump shows contention
jcmd <pid> Thread.print | grep "BLOCKED"
# Find the object address and which threads compete for it
```

**Fix:**
```java
// BAD: coarse-grained lock causing contention
synchronized(this) { /* all operations */ }

// GOOD: fine-grained locks, or lock-free structures
private final ReentrantReadWriteLock lock =
    new ReentrantReadWriteLock();
lock.readLock().lock();
try { /* read operations */ }
finally { lock.readLock().unlock(); }
```

**Prevention:** Design for minimal lock contention; use `ReentrantLock` or `java.util.concurrent` classes that are better tuned for contention than `synchronized`.

**3. Compressed OOPs Disabled for Unexpectedly Large Heap**

**Symptom:** Every object consumes 4 bytes more than expected after heap size increases past 32 GB.

**Root Cause:** `-XX:+UseCompressedOops` is disabled when `-Xmx` exceeds ~32 GB, expanding the Klass Pointer from 4 to 8 bytes per object.

**Diagnostic:**
```bash
jcmd <pid> VM.flags | grep CompressedOops
# -XX:+UseCompressedOops → enabled (heap ≤ 32GB)
# -XX:-UseCompressedOops → disabled (heap > 32GB)
```

**Prevention:** Keep heap <= 32 GB per JVM instance to enable compressed oops; or use multiple JVM instances horizontally rather than one very large heap.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — the runtime environment that creates and interprets object headers
- `Heap Memory` — the region where all Java objects (and their headers) are allocated
- `synchronized` — keyword that transitions the Mark Word through lock states

**Builds On This (learn these next):**
- `Escape Analysis` — can stack-allocate objects when they don't escape, avoiding header overhead on heap
- `GC Roots` — GC uses Mark Word fields (forwarding pointers, GC age bits) during garbage collection
- `Biased Locking` — the historical Mark Word optimisation that assumed single-thread lock dominance

**Alternatives / Comparisons:**
- `Project Lilliput (JEP 450)` — experimental JVM project to shrink the Object Header from 12–16 bytes to 8 bytes, reducing per-object overhead
- `Off-heap` — native memory storage that has no Java object header overhead

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hidden 8–16 byte metadata prefix on every │
│              │ heap object: Mark Word + Klass Pointer    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ JVM needs O(1) access to type, lock, and  │
│ SOLVES       │ GC metadata per object without external   │
│              │ lookup tables                             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The Mark Word is multipurposed: same 8    │
│              │ bytes encode hash / lock / GC forwarding  │
│              │ depending on the object's current state   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — automatic on every object.       │
│              │ Tune with JOL to understand memory layout │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Creating billions of tiny objects —       │
│              │ use primitive arrays or off-heap to avoid │
│              │ 16-byte minimum per object                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) metadata access vs 8–16 bytes per    │
│              │ object overhead (significant at scale)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every Java object carries a 16-byte      │
│              │ invisible passport encoding its type,     │
│              │ lock status, and GC age"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Escape Analysis → synchronized →          │
│              │ GC Roots                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An application creates 100 million `Point` objects (two int fields). With default 64-bit JVM settings and compressed oops, each Point is 24 bytes (8 mark word + 4 klass ptr + 4 x + 4 y + 4 padding). Disabling compressed oops (heap > 32 GB) makes each Point 32 bytes. Calculate the total memory increase for 100 million objects, and explain why increasing heap size past 32 GB can paradoxically INCREASE live memory usage (not just overhead) — creating a reinforcing cycle.

**Q2.** The Mark Word in an unlocked object encodes the object's identity hash code. If `synchronized(obj)` transitions the Mark Word to lightweight-locked state (overwriting the hash code bits with a stack pointer), what happens to the previously computed identity hash code? How does the JVM ensure that `System.identityHashCode(obj)` continues to return the original value even while the object is locked? Trace the JVM's precise mechanism for preserving hash code across lock state transitions.

