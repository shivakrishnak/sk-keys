---

---
---
number: 012 
category: JVM Internals 
difficulty: ★★★ 
depends_on: [[JVM]] [[Heap Memory]] [[Bytecode]] 
used_by: [[GC]] [[Synchronized]] [[JIT Compiler]] [[instanceof]] 
tags: #java, #jvm, #memory, #internals, #concurrency, #deep-dive

---

⚡ TL;DR — The hidden metadata prepended to every heap object containing identity, locking state, GC age, and type pointer — invisible in Java source but costs memory on every single object you create.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #012         │ Category: JVM Internals              │ Difficulty: ★★★          │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on:  │ [[JVM]] [[Heap Memory]] [[Bytecode]] │                          │
│ Used by:     │ [[GC]] [[Synchronized]] [[JIT]]      │                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

#### 📘 Textbook Definition

Every Java object on the heap is prepended with an **Object Header** — a JVM-managed metadata block invisible to Java source code. It consists of two machine-word fields: the **Mark Word** (stores identity hashcode, GC age, locking state, and GC flags) and the **Klass Pointer** (reference to the class metadata in Metaspace). Arrays additionally carry a third field: the **array length**. On a 64-bit JVM with compressed OOPs, the header is typically 12 bytes; without compression, 16 bytes.

---

#### 🟢 Simple Definition (Easy)

Every object you create has a **hidden preamble** attached by the JVM — before your fields even start — that stores bookkeeping information the JVM needs for locking, GC, and type checking. You never see it in Java code, but it's always there.

---

#### 🔵 Simple Definition (Elaborated)

When you write `new Order()`, you think about the fields inside `Order`. But the JVM prepends extra bytes to every object — a header containing: what class this object belongs to, how old it is for GC purposes, what its identity hashcode is, and whether any thread currently holds a lock on it. This header enables `synchronized`, `instanceof`, GC age tracking, and identity hashCode — all without you doing anything. The cost: every object pays this overhead regardless of how small it is.

---

#### 🔩 First Principles Explanation

**The problem:**

The JVM needs to answer four questions about ANY object at runtime, given only a heap pointer:

```
1. What type is this?     → for instanceof, casting, virtual dispatch
2. Is it locked?          → for synchronized blocks
3. How old is it?         → for GC generational promotion
4. What is its identity?  → for default hashCode(), System.identityHashCode()
```

**The constraint:**

Java source code doesn't store any of this. A `Point` class with `x` and `y` has no `type` field, no `lockState` field, no `gcAge` field.

**The solution:**

> Prepend a fixed-size metadata block to every object on the heap — managed entirely by the JVM, invisible to Java code.

```
HEAP MEMORY — what actually exists for 'new Point(3,4)':

┌─────────────────────────────────────┐
│         OBJECT HEADER               │  ← JVM managed, invisible
│  Mark Word      (8 bytes)           │
│  Klass Pointer  (4 bytes compressed)│
├─────────────────────────────────────┤
│         INSTANCE DATA               │  ← your fields
│  int x = 3     (4 bytes)            │
│  int y = 4     (4 bytes)            │
└─────────────────────────────────────┘

Total: 20 bytes for a two-int object
Your fields: 8 bytes
JVM overhead: 12 bytes (60% overhead for small objects!)
```

---

#### ❓ Why Does This Exist — Why Before What

**Without the Object Header:**

```
synchronized(obj) { ... }
→ Where does the JVM store the lock state?
→ No header = nowhere to put it
→ synchronized impossible without external lock table
   (external table = hash map lookup per lock = slow)

obj.hashCode()  (default implementation)
→ Where is the identity hash stored after first call?
→ No header = recompute every time OR external map
→ External map = memory leak + synchronization overhead

GC generational collection
→ How does GC know object's age?
→ No header = no age tracking = no generational GC
→ No generational GC = collect entire heap every time = slow

instanceof / virtual method dispatch
→ How does JVM know what type obj is at runtime?
→ No klass pointer = type check requires scanning
→ Virtual dispatch (polymorphism) becomes O(n) not O(1)
```

**What breaks without it:**

```
1. synchronized         → needs external lock table (slow)
2. Default hashCode()   → recomputed or external map (slow/leaky)
3. Generational GC      → impossible (no age tracking)
4. instanceof           → O(n) scan instead of O(1) pointer check
5. Virtual dispatch     → method lookup becomes linear
6. GC forwarding        → can't store forwarding pointer during GC
```

**With Object Header:**

```
→ O(1) lock acquisition — state in Mark Word
→ O(1) type check — follow Klass Pointer
→ O(1) age check — 4 bits in Mark Word
→ Identity hash stored once in Mark Word
→ GC forwarding pointer stored in Mark Word during collection
→ All of this with zero Java code, zero developer overhead
```

---

#### 🧠 Mental Model / Analogy

> Think of every Java object as a **filed document in a government office**.
> 
> Your document (object fields) contains the actual content — name, address, data.
> 
> But stapled to the front is a **government cover sheet** (object header) containing:
> 
> - Document type/classification (Klass Pointer → what class)
> - Security clearance / lock status (Mark Word → locking)
> - Filing date / age (Mark Word → GC age)
> - Document ID number (Mark Word → identity hashCode)
> 
> You never write the cover sheet — the office (JVM) stamps it automatically. But every document pays the cost of those extra pages, even a one-line memo.

---

#### ⚙️ How It Works — Mark Word Deep Dive

The Mark Word is the most complex part — it's **multipurpose**, meaning the same 64 bits mean different things depending on object state:

```
┌──────────────────────────────────────────────────────────────────┐
│                    MARK WORD (64-bit JVM)                        │
│                    8 bytes — always present                      │
├──────────────────────────────────────────────────────────────────┤
│ State           │ Bit layout (simplified)                        │
├─────────────────┼──────────────────────────────────────────────  │
│ Unlocked        │ [identity hashcode: 31b][unused:25b][age:4b]   │
│                 │ [biased:1b=0][lock:2b=01]                      │
├─────────────────┼────────────────────────────────────────────────│
│ Biased Locked   │ [thread_id:54b][epoch:2b][age:4b]              │
│                 │ [biased:1b=1][lock:2b=01]                      │
├─────────────────┼────────────────────────────────────────────────│
│ Lightweight     │ [ptr_to_lock_record:62b][lock:2b=00]           │
│ Locked          │ (points to stack-allocated lock record)        │
├─────────────────┼────────────────────────────────────────────────│
│ Heavyweight     │ [ptr_to_monitor:62b][lock:2b=10]               │
│ Locked          │ (points to OS mutex — ObjectMonitor)           │
├─────────────────┼────────────────────────────────────────────────│
│ GC Marked       │ [forwarding_ptr:62b][lock:2b=11]               │
│ (during GC)     │ (points to new location during copying GC)     │
└──────────────────────────────────────────────────────────────────┘

Last 2 bits = lock state indicator:
  00 → lightweight locked
  01 → unlocked or biased
  10 → heavyweight locked (inflated)
  11 → GC mark (forwarding pointer)
```

**Klass Pointer:**

```
┌──────────────────────────────────────────────────────────────────┐
│                   KLASS POINTER                                  │
│                                                                  │
│  Points to class metadata in Metaspace                          │
│                                                                  │
│  64-bit JVM, no compression: 8 bytes                            │
│  64-bit JVM, compressed OOPs (-XX:+UseCompressedOops):          │
│    4 bytes (default on heaps ≤ 32GB)                            │
│                                                                  │
│  Used by:                                                        │
│  • instanceof checks → follow klass ptr → check type hierarchy  │
│  • Virtual method dispatch → klass has vtable                   │
│  • GC → klass knows object size for correct copying             │
└──────────────────────────────────────────────────────────────────┘
```

**Array Header — extra field:**

```
┌──────────────────────────────────────────────────────────────────┐
│                    ARRAY OBJECT HEADER                           │
│                                                                  │
│  Mark Word      8 bytes                                          │
│  Klass Pointer  4 bytes (compressed)                            │
│  Array Length   4 bytes  ← EXTRA field for arrays only          │
│  ─────────────────────                                           │
│  Total:        16 bytes                                          │
│                                                                  │
│  Why needed: GC must know array size to copy it correctly        │
│  int[] arr = new int[100]                                        │
│  → header stores length=100                                      │
│  → GC knows: copy 16 + (100 × 4) = 416 bytes                    │
└──────────────────────────────────────────────────────────────────┘
```

---

#### 🔄 How It Connects

```
new Order()
      ↓
Heap allocates: [Mark Word][Klass Ptr][fields...]
                      ↓           ↓
              locking state    points to
              GC age           Order.class
              identity hash    in Metaspace
              GC forward ptr        ↓
                      ↓        vtable for
              synchronized()   virtual dispatch
              reads/writes     instanceof check
              Mark Word        GC size calc
```

---

#### 💻 Code Example

**Measuring object header cost with JOL (Java Object Layout):**

xml

```xml
<!-- Add to pom.xml -->
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.17</version>
</dependency>
```

java

```java
import org.openjdk.jol.info.ClassLayout;
import org.openjdk.jol.vm.VM;

public class HeaderDemo {

    static class Point {
        int x;
        int y;
    }

    static class EmptyObject {
        // no fields at all
    }

    static class SingleBoolean {
        boolean flag;
    }

    public static void main(String[] args) {
        System.out.println(VM.current().details());

        // Point: two ints
        System.out.println(ClassLayout.parseClass(Point.class)
            .toPrintable());

        // Empty object
        System.out.println(ClassLayout.parseClass(EmptyObject.class)
            .toPrintable());

        // Single boolean
        System.out.println(ClassLayout.parseClass(SingleBoolean.class)
            .toPrintable());
    }
}
```

```
Output (64-bit JVM, compressed OOPs enabled):

# Point layout:
OFFSET  SIZE   TYPE
     0     4        (object header - mark word part 1)
     4     4        (object header - mark word part 2)
     8     4        (object header - klass pointer)
    12     4    int x
    16     4    int y
    20     4        (alignment padding)
Instance size: 24 bytes
─────────────────────────────────────────
Header:  12 bytes
Fields:   8 bytes (x + y)
Padding:  4 bytes (alignment to 8-byte boundary)
Total:   24 bytes
Header overhead: 50% of useful data size!

# EmptyObject layout:
OFFSET  SIZE
     0    12   (object header)
    12     4   (alignment padding)
Instance size: 16 bytes
Header overhead: 100% — all overhead, zero data!

# SingleBoolean layout:
OFFSET  SIZE
     0    12   (object header)
    12     1   boolean flag
    13     3   (padding)
Instance size: 16 bytes
Header overhead: 75% of total size for 1 byte of data!
```

**Observing Mark Word changes during locking:**

java

```java
import org.openjdk.jol.info.ClassLayout;

public class LockingDemo {

    public static void main(String[] args) {
        Object obj = new Object();

        // State 1: Unlocked
        System.out.println("UNLOCKED:");
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());

        synchronized (obj) {
            // State 2: Locked — Mark Word changes
            System.out.println("LOCKED:");
            System.out.println(ClassLayout.parseInstance(obj).toPrintable());
        }

        // State 3: Unlocked again — Mark Word reverts
        System.out.println("UNLOCKED AGAIN:");
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());

        // Force identity hashCode — occupies Mark Word bits
        int hash = System.identityHashCode(obj);
        System.out.println("AFTER hashCode() call: hash=" + hash);
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());
        // Mark Word now permanently stores the hash
        // → biased locking now IMPOSSIBLE for this object
        //   (hash and thread_id can't share same bits)
    }
}
```

**Memory cost at scale — why header size matters:**

java

```java
public class HeaderCost {
    public static void main(String[] args) {
        int objectCount = 10_000_000; // 10 million objects

        // Each Point: 24 bytes total, 12 bytes header
        // 10M Points = 240MB total
        // Header alone = 120MB — HALF the memory is overhead

        // Real world: microservice with 10M cached DTOs
        // Switching from many small objects to fewer large ones
        // or using primitive arrays instead of object arrays
        // can cut memory 40-60%

        long headerOverhead = (long) objectCount * 12; // bytes
        System.out.println("Header overhead: "
            + headerOverhead / 1024 / 1024 + " MB");
        // Output: Header overhead: 114 MB
    }
}
```

**Compressed OOPs — why heap > 32GB breaks it:**

bash

```bash
# Default: compressed OOPs ON (heap ≤ 32GB)
java -Xmx31g -XX:+UseCompressedOops myapp
# Klass Pointer: 4 bytes
# Object header: 12 bytes total

# Heap > 32GB: compressed OOPs automatically disabled
java -Xmx33g myapp
# Klass Pointer: 8 bytes
# Object header: 16 bytes total
# 10M objects × 4 extra bytes = 40MB MORE just from header growth

# The 32GB cliff: going from 31GB to 33GB heap
# actually INCREASES memory usage per object
# Counter-intuitive but real production gotcha
```

---

#### 🔁 Locking State Transitions via Mark Word

```
Object created
      ↓
[UNLOCKED] mark word: hashcode | age | 01
      ↓
First synchronized(obj) — same thread repeatedly
      ↓
[BIASED LOCKED] mark word: thread_id | epoch | age | 01
  → No CAS operation needed for same thread
  → Fastest path
      ↓
Different thread tries to lock
      ↓
Bias revoked → [LIGHTWEIGHT LOCKED]
  mark word: ptr_to_stack_lock_record | 00
  → Uses CAS (Compare-And-Swap)
  → No OS involvement yet
      ↓
Contention — thread must wait
      ↓
[HEAVYWEIGHT LOCKED / INFLATED]
  mark word: ptr_to_ObjectMonitor | 10
  → OS mutex involved
  → Thread parked by OS scheduler
  → Most expensive path
      ↓
Lock released
      ↓
[UNLOCKED] again
```

> Note: Biased locking was **deprecated in Java 15** and **removed in Java 21** — modern JVMs start at lightweight locking. The progression is now: Unlocked → Lightweight → Heavyweight.

---

#### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Object size = sum of field sizes"|Always add **12-16 bytes** for header + alignment padding|
|"Empty objects have zero overhead"|Empty object = **16 bytes** — all header, zero data|
|"synchronized is always expensive"|Uncontended lightweight lock = **CAS only**, very fast|
|"hashCode() is computed every time"|Computed **once**, stored in Mark Word, cached forever|
|"Klass Pointer is always 8 bytes"|**4 bytes** with compressed OOPs (default on heaps ≤ 32GB)|
|"Header is part of your class"|Header is **JVM-managed** — invisible to Java reflection|
|"Biased locking is still used"|**Removed in Java 21** — don't rely on biased lock behaviour|

#### 🔥 Pitfalls in Production

**1. The 32GB heap cliff**

bash

```bash
# Team decides to increase heap from 28GB to 36GB
# Expecting linear memory improvement
# Result: performance WORSE, memory usage UP

# Why:
# ≤32GB: compressed OOPs → 4-byte klass ptr → 12-byte header
# >32GB: no compressed OOPs → 8-byte klass ptr → 16-byte header
# 10M objects × 4 bytes extra = 40MB more just from headers
# + all object references grow: 4 bytes → 8 bytes
# → cache lines hold fewer pointers → more cache misses

# Fix: stay under 32GB OR jump to significantly larger heap
# (the overhead amortises at very large heap sizes)
# Sweet spot: 28-30GB for compressed OOPs benefit
java -Xmx30g -XX:+UseCompressedOops myapp   # ✅
java -Xmx33g myapp                           # ❌ loses compression
```

**2. Identity hashCode poisoning biased locks**

java

```java
// Calling System.identityHashCode() on an object
// BEFORE synchronizing on it prevents biased locking
// (hash and thread_id can't share the same Mark Word bits)

// Bad pattern (pre Java 21):
Map<Object, Data> map = new HashMap<>();
map.put(lock, data);           // triggers hashCode computation
                               // → Mark Word now stores hash
                               // → biased locking impossible
synchronized(lock) { ... }    // falls back to lightweight immediately

// In Java 21+ this doesn't matter — biased locking removed
// But understanding Mark Word bit contention still relevant
// for custom lock implementations and JVM internals
```

**3. Small object proliferation — hidden memory cost**

java

```java
// Anti-pattern: many tiny objects
// Common in event-driven / streaming systems

// Each event wrapper:
class EventWrapper {
    String type;     // reference: 4 bytes
    long timestamp;  // 8 bytes
    // Header: 12 bytes
    // Total: 24 bytes — 50% is header
}

// 1M events/sec × 24 bytes = 24MB/sec allocation rate
// GC pressure explodes

// Fix 1: use primitive arrays or ByteBuffer (off-heap)
// Fix 2: object pooling (reuse wrappers)
// Fix 3: value types (Project Valhalla — future Java)
//        → eliminates header for small value objects
//        → 'int x, y' in a value type = 8 bytes, no header
```

**4. Arrays of objects vs arrays of primitives**

java

```java
// Array of objects — each element is a REFERENCE
// Each referenced object has its OWN header

int[] primitives = new int[1000];
// Array header: 16 bytes
// Data: 1000 × 4 = 4000 bytes
// Total: 4016 bytes ✅

Integer[] boxed = new Integer[1000];
// Array header: 16 bytes
// References: 1000 × 4 = 4000 bytes
// Each Integer object: 16 bytes (header 12 + int 4)
// Total: 16 + 4000 + (1000 × 16) = 20016 bytes ❌
// 5× more memory for same data!
```

---

#### 🔗 Related Keywords

- `Heap Memory` — where object headers live
- `Mark Word` — first field of header; locking + GC + hash
- `Klass Pointer` — second field; points to class in Metaspace
- `Metaspace` — where Klass Pointer points to
- `synchronized` — reads/writes Mark Word for lock state
- `GC` — uses Mark Word for age tracking and forwarding pointers
- `Compressed OOPs` — shrinks Klass Pointer from 8 to 4 bytes
- `System.identityHashCode()` — stored in Mark Word after first call
- `JOL (Java Object Layout)` — tool to inspect object memory layout
- `Project Valhalla` — future JVM feature to eliminate headers for value types
- `Object Padding` — alignment bytes added after fields to reach 8-byte boundary

---

#### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Hidden 12-16 byte JVM metadata block on   │
│              │ every heap object — enables locking, GC,  │
│              │ type checking, identity hash              │
├──────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always present — understand it to reason  │
│              │ about memory costs, locking behaviour,    │
│              │ and GC efficiency                         │
├──────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid many tiny objects in               │
│              │ memory-sensitive paths — header overhead  │
│              │ dominates small objects                   │
├──────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Every object pays a 12-byte JVM tax —   │
│              │  the smaller the object, the heavier      │
│              │  the tax"                                 │
├──────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Mark Word → Compressed OOPs →             │
│              │ synchronized internals → GC Forwarding →  │
│              │ Project Valhalla → JOL                    │
└──────────────────────────────────────────────────────────┘
```

---

#### 🧠 Think About This Before We Continue

**Q1.** A `Boolean` object (wrapping a single `true`/`false` bit) takes **16 bytes** on the heap — 12 bytes header, 1 byte field, 3 bytes padding. Yet a `boolean` primitive takes 1 byte. Now consider a `List<Boolean>` with 1 million entries vs a `boolean[]` with 1 million entries. Calculate the exact memory difference — and what does this tell you about the real cost of autoboxing in high-throughput systems?

**Q2.** During GC, the collector needs to **move objects** to defragment the heap (copying GC). It writes the new address into the old location so any thread still holding a reference can be redirected. Where exactly does it store this forwarding pointer — and why does this work without corrupting the object's data?

---

Next up: **013 — Escape Analysis** — the JVM optimisation that determines whether an object can be allocated on the stack instead of the heap, how it eliminates GC pressure, and why it silently makes your code faster without you doing anything.