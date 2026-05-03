---
layout: default
title: "VarHandle"
parent: "Java Concurrency"
nav_order: 364
permalink: /java-concurrency/varhandle/
number: "0364"
category: Java Concurrency
difficulty: ★★★
depends_on: Atomic Classes, CAS (Compare-And-Swap), Memory Ordering, Java Memory Model
used_by: Lock-Free Data Structures, Low-Level Concurrency Libraries
related: Atomic Classes, Unsafe (sun.misc), StampedLock
tags:
  - java
  - concurrency
  - deep-dive
  - lock-free
  - memory-model
  - advanced
---

# 0364 — VarHandle

⚡ TL;DR — `VarHandle` (Java 9+) is a type-safe, JDK-sanctioned replacement for `sun.misc.Unsafe` that provides CAS and fine-grained memory ordering operations on specific fields and array elements — enabling lock-free data structures with precise control over memory visibility without the undefined behaviour risks of `Unsafe`.

| #0364 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Atomic Classes, CAS (Compare-And-Swap), Memory Ordering, Java Memory Model | |
| **Used by:** | Lock-Free Data Structures, Low-Level Concurrency Libraries | |
| **Related:** | Atomic Classes, Unsafe (sun.misc), StampedLock | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`AtomicReference` is great for making an entire field atomic. But it wraps the field in an object — you can't make an arbitrary existing field atomic without redesigning the class. Meanwhile, `sun.misc.Unsafe` lets you do CAS on any field at a specific memory offset — but it's an internal, undocumented, unsupported API. JVM vendors are free to change it, break it, or remove it. Calling `Unsafe.objectFieldOffset()` with the wrong class or field name crashes at runtime, not compile time. Using `Unsafe` in production code is a ticking time bomb for JVM upgrades.

**THE BREAKING POINT:**
The JDK itself (java.util.concurrent internals — `ConcurrentHashMap`, `AbstractQueuedSynchronizer`, `ForkJoinPool`) relied heavily on `sun.misc.Unsafe` for performance. But for library authors and application developers, `Unsafe` was accessible but explicitly unsupported. Java 9's module system started restricting `Unsafe` access. The ecosystem needed a supported, type-safe API for the same capabilities.

**THE INVENTION MOMENT:**
`VarHandle` was introduced in Java 9 (JEP 193) to provide a sanctioned, type-safe, access-checked API for: CAS and other atomic operations on specific object fields and array elements; fine-grained memory ordering (plain, opaque, acquire/release, volatile) — more precise than Java's binary volatile/non-volatile distinction.

---

### 📘 Textbook Definition

**VarHandle:** A dynamically-typed reference (`java.lang.invoke.VarHandle`) to a variable — either an instance field, a static field, or an array element. It provides: (1) access modes that mirror the C++11 memory model (plain, opaque, acquire, release, volatile); (2) atomic compare-and-set/exchange/add operations; (3) type checking enforced by the JVM at lookup time, not at use time. Created via `MethodHandles.lookup().findVarHandle(Class, "fieldName", Class)`.

**Access modes:** The memory ordering guarantee applied to a VarHandle operation:
- `PLAIN` — no ordering guarantees (like a regular field access)
- `OPAQUE` — single-variable atomicity, no cross-variable ordering
- `ACQUIRE` — subsequent reads/writes see all operations prior to the release
- `RELEASE` — pairs with acquire on another thread
- `VOLATILE` — full sequential consistency (same as Java `volatile`)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
VarHandle is the safe, official version of `sun.misc.Unsafe` — it gives you CAS and memory-ordering control on any field, with type safety and JVM support.

**One analogy:**
> `sun.misc.Unsafe` is a master key that opens any lock in the building — powerful but dangerous; if used wrong, you corrupt the entire building. `VarHandle` is a properly-issued per-room key — you still get access to the specific room (field) you need, but the key is checked against the room's lock type at creation time. If the key doesn't match, it fails at key-issuance time, not when you're halfway through the door.

**One insight:**
The critical addition over `AtomicReference`/`AtomicInteger` is the **access mode spectrum**. Java's `volatile` gives you full sequential consistency — the strongest (and most expensive) memory ordering. Most lock-free algorithms only need weaker guarantees (e.g., acquire/release — as used in C++ mutexes and Java's `ReentrantLock` internally). Using full volatile ordering where acquire/release suffices wastes memory fence instructions. `VarHandle` exposes the complete spectrum, letting you match the ordering cost to what your algorithm actually requires.

---

### 🔩 First Principles Explanation

**MEMORY ORDERING SPECTRUM (weakest → strongest):**

```
PLAIN        No ordering. Like a regular Java field access.
             May be reordered freely. No memory barrier.
             Use: single-threaded accesses, under lock.

OPAQUE       Bit-atomic. Not torn. Not reordered with itself.
             No cross-variable ordering.
             Use: progress monitoring, statistics.

ACQUIRE/     Pairs form a happens-before relationship.
RELEASE      Load-acquire: sees everything before the paired store-release.
             Store-release: all prior writes visible to load-acquire.
             Use: lock-free data structures, hand-off patterns.

VOLATILE     Full sequential consistency. Most expensive.
             Same as Java volatile.
             Use: when ordering with ALL threads is required.
```

**CREATING A VarHandle:**

```java
import java.lang.invoke.*;

public class Node {
    int value;
    Node next;                    // the field we want VarHandle for

    // Declare VarHandle as a static final field (lookup once, use many)
    private static final VarHandle NEXT;
    static {
        try {
            NEXT = MethodHandles.lookup()
                .findVarHandle(Node.class, "next", Node.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }
}
```

**KEY OPERATIONS:**

```java
// Volatile access (same as AtomicReference):
Node current = (Node) NEXT.getVolatile(node);
NEXT.setVolatile(node, newNode);

// CAS (volatile strength):
boolean success = NEXT.compareAndSet(node, expectedNext, newNext);

// CAS with acquire/release (weaker, often sufficient, less overhead):
boolean success = NEXT.compareAndExchangeAcquire(node, expectedNext, newNext);

// Plain access (no ordering — use under lock or single-threaded):
Node n = (Node) NEXT.get(node);

// Acquire/Release pattern:
// Writer: NEXT.setRelease(node, value)  ← store-release
// Reader: Node n = (Node) NEXT.getAcquire(node)  ← load-acquire
// Reader is guaranteed to see everything done before setRelease
```

**ARRAY ELEMENTS:**

```java
// VarHandle for array elements
VarHandle ARRAY = MethodHandles.arrayElementVarHandle(int[].class);
int[] arr = new int[10];
ARRAY.compareAndSet(arr, 3, 0, 42); // CAS arr[3] from 0 to 42
```

---

### 🧪 Thought Experiment

**SETUP:**
Implement a lock-free SPSC (Single-Producer Single-Consumer) queue. Producer writes items and advances the write index. Consumer reads items and advances the read index. They never contend on the same index. But they need visibility of each other's writes.

**WITH `volatile` for BOTH indices:**
```
volatile int writeIndex; // full sequential consistency
volatile int readIndex;  // full sequential consistency
// Correct, but uses full memory fence on every increment.
// Overkill: producer only needs to PUBLISH writeIndex (store-release)
//           consumer only needs to SEE writeIndex (load-acquire)
// Full volatile forces all threads to see all stores globally — not needed for 2 threads.
```

**WITH VarHandle acquire/release:**
```java
// Producer:
WRITE_INDEX.setRelease(this, writeIdx); // lighter than volatile
// All prior writes (to items[]) are visible to anyone who does a load-acquire

// Consumer:
int w = (int) WRITE_INDEX.getAcquire(this); // load-acquire
// Sees all writes done before the producer's setRelease
// items[] reads after this line see the producer's writes
```

**THE INSIGHT:**
Acquire/release semantics are precisely the right tool for producer-consumer handoff: exactly the ordering needed, nothing more. Full volatile ordering would also work but costs extra memory fence instructions on every access. At 100M operations/second, the difference is measurable.

---

### 🧠 Mental Model / Analogy

> Memory ordering is like a rule about when you're allowed to "publish" your work so others can see it. PLAIN = post on internal notes nobody reads. OPAQUE = post on your own board (visible to yourself). ACQUIRE/RELEASE = hand over a completed folder to a colleague — they see everything you put in before handing it over. VOLATILE = broadcast on the company-wide intercom — everyone hears simultaneously, in order.

Explicit mapping:
- "post on internal notes" → PLAIN (no visibility guarantees)
- "post on your own board" → OPAQUE (stable for single variable)
- "hand over a folder" → store-RELEASE; "colleague receives" → load-ACQUIRE
- "company-wide broadcast" → VOLATILE
- VarHandle = the specific publishing mechanism for a specific field

Where this analogy breaks down: "ACQUIRE/RELEASE" doesn't mean the value is immediately visible to ALL threads — just to the thread that performs the paired acquire read. For global visibility (all threads see the same ordering), VOLATILE is required.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
VarHandle is a way to do CAS (atomic compare-and-swap) on a specific field of an object, officially and safely. Think of it as `AtomicReference` but for any field you choose, without wrapping the field in a separate object. It's used internally by the JDK and by library authors building lock-free data structures.

**Level 2 — How to use it (junior developer):**
Declare a `static final VarHandle` field in your class. Look it up in a `static {}` block using `MethodHandles.lookup().findVarHandle(...)`. Then use it like `HANDLE.compareAndSet(object, expectedValue, newValue)` for CAS, or `HANDLE.getVolatile(object)` / `HANDLE.setVolatile(object, value)` for volatile access. This is equivalent to making the field `volatile` and wrapping it in `AtomicReference` — but without the wrapper object overhead.

**Level 3 — How it works (mid-level engineer):**
`VarHandle` is a JVM-level construct that compiles to the same hardware instructions as `Unsafe` and `AtomicReference` — but the JVM verifies the type signature at lookup time, not at call time. The access modes compile to specific instruction sequences: `getVolatile` → load with memory fence; `setRelease` → store with release fence (lighter than full volatile); `compareAndSet` → CAS instruction. On x86, `setRelease` compiles to a plain store (x86's TSO memory model makes all stores already release-ordered), making it free vs. volatile. On ARM, it compiles to `stlr` (store-release) instead of `dmb` + `str` (full fence + store) — a meaningful difference.

**Level 4 — Why it was designed this way (senior/staff):**
VarHandle was designed as part of a broader JVM access-control reform (Java 9 module system). The JDK itself needed to migrate away from `sun.misc.Unsafe` for its own internal use (ConcurrentHashMap, AQS, etc.) while also providing the capability to external library authors. The `MethodHandles.Lookup` system provides access control: you can only create a `VarHandle` for a field that your lookup context has access to (same package, same module, etc.). This prevents a hostile class from creating a VarHandle for a private field of an unrelated class — unlike `Unsafe.objectFieldOffset()` which has no such restriction. The memory ordering spectrum (Plain/Opaque/Acquire/Release/Volatile) directly maps the C++11 memory model to Java, allowing library authors (Disruptor, Chronicle Map, LMAX) to write portable, JVM-correct code without depending on architecture-specific fence knowledge.

---

### ⚙️ How It Works (Mechanism)

```
VarHandle LOOKUP (once at class load):
  MethodHandles.Lookup lookup = MethodHandles.lookup();
  VarHandle VH = lookup.findVarHandle(MyClass.class, "field", int.class);
  // JVM verifies: does lookup context have access to MyClass.field?
  // Type encoded: VH knows this is an int field on MyClass objects
  // Offset computed: VH stores the exact memory offset of 'field' in MyClass

VarHandle USE (millions of times):
  VH.compareAndSet(myObj, expected, newVal)
    → JVM: load address of myObj + field_offset
    → hardware CMPXCHG at that address (x86)
    → NO object creation, NO indirection
    → Same speed as Unsafe.compareAndSwapInt()
    → But type-safe (JVM verifies myObj is MyClass, expected/newVal are int)

ACCESS MODE COMPILATION (JVM intrinsics):
  getVolatile   → MFENCE (or equivalent) + LOAD (on x86)
  setVolatile   → LOCK XCHG or MFENCE + STORE
  getAcquire    → LOAD (on x86, all loads are acquire — free)
  setRelease    → STORE (on x86, all stores are release — free)
  getOpaque     → LOAD (no reordering with self)
  setOpaque     → STORE (no reordering with self)
  get/set PLAIN → Regular field access (may be register-cached)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Class definition:
  class Node {
    int value;
    volatile Node next;   ← OLD APPROACH: field itself is volatile

    // OR: NEW VarHandle APPROACH
    Node next;            ← plain field (not volatile)
    static final VarHandle NEXT; // handle for CAS + memory ordering
    static { NEXT = MethodHandles.lookup().findVarHandle(...); }
  }

Lock-free linked list insert:
  Node newNode = new Node(value);
  for (;;) {
    Node tail = (Node) TAIL.getAcquire(list);  // load-acquire
    Node tailNext = (Node) NEXT.getAcquire(tail); // load-acquire
    if (tail == TAIL.getAcquire(list)) {
      if (tailNext == null) {
        if (NEXT.compareAndSet(tail, null, newNode)) { // CAS
          TAIL.compareAndSet(list, tail, newNode);     // CAS (best-effort)
          return;
        }
      } else {
        TAIL.compareAndSet(list, tail, tailNext); // help advance tail
      }
    }
  }
```

---

### 💻 Code Example

**Example 1 — VarHandle for CAS on instance field:**
```java
import java.lang.invoke.*;

public class LockFreeCounter {
    private int value;

    private static final VarHandle VALUE;
    static {
        try {
            VALUE = MethodHandles.lookup()
                .findVarHandle(LockFreeCounter.class, "value", int.class);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // Lock-free increment with retry loop
    public int incrementAndGet() {
        int current, next;
        do {
            current = (int) VALUE.getAcquire(this);   // load-acquire
            next = current + 1;
        } while (!VALUE.compareAndSet(this, current, next)); // CAS
        return next;
    }

    // Volatile read (exact equivalent of 'volatile int value')
    public int get() {
        return (int) VALUE.getVolatile(this);
    }

    // Store-release (lighter than volatile store)
    public void setRelease(int newValue) {
        VALUE.setRelease(this, newValue);
    }
}
```

**Example 2 — Acquire/Release handoff pattern:**
```java
// Single-producer, single-consumer flag
public class Handoff {
    private Object data;
    private int ready; // 0 = not ready, 1 = ready

    private static final VarHandle READY;
    static {
        try {
            READY = MethodHandles.lookup()
                .findVarHandle(Handoff.class, "ready", int.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // Producer: write data, then signal ready
    public void produce(Object item) {
        this.data = item;                 // plain write (before release)
        READY.setRelease(this, 1);        // STORE-RELEASE: establishes happens-before
        // Consumer's getAcquire will see all writes before this setRelease
    }

    // Consumer: poll for ready, then read data
    public Object consume() {
        while ((int) READY.getAcquire(this) == 0) { // LOAD-ACQUIRE
            Thread.onSpinWait(); // hint to JVM: spin-wait loop
        }
        return data; // safe: happens-after the producer's setRelease
    }
}
```

**Example 3 — Array element CAS:**
```java
// CAS on array element (e.g., ConcurrentHashMap-style table)
VarHandle TABLE = MethodHandles.arrayElementVarHandle(Object[].class);
Object[] table = new Object[1024];

// CAS table[index] from null to newNode:
boolean inserted = TABLE.compareAndSet(table, index, null, newNode);
if (!inserted) {
    // Another thread inserted at this index first — handle collision
}

// Volatile read of table[index]:
Object existing = TABLE.getVolatile(table, index);
```

---

### ⚖️ Comparison Table

| API | Type-safe | Supported | Memory ordering control | Access scope |
|---|---|---|---|---|
| **VarHandle** | Yes | Yes (Java 9+) | Full spectrum (Plain/Opaque/Acquire-Release/Volatile) | Any accessible field |
| AtomicInteger/Long/Ref | Yes | Yes | Volatile only | Dedicated wrapper object |
| sun.misc.Unsafe | No | No (internal) | Platform-specific | Any field (bypasses access) |
| volatile field | Yes | Yes | Volatile only | Specific field (static) |
| synchronized | Yes | Yes | Happens-before | Entire block |

How to choose: use `AtomicInteger`/`AtomicLong`/`AtomicReference` for most application code. Use `VarHandle` when: (a) you cannot use wrapper objects (embedded field in existing class), (b) you need acquire/release instead of full volatile, or (c) you're writing a library/framework replacing `sun.misc.Unsafe` usage.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "VarHandle replaces AtomicInteger for everyday code" | No. AtomicInteger and AtomicLong are the right choice for >95% of cases. VarHandle is for library authors and performance-critical code needing fine-grained control. |
| "getAcquire/setRelease are always faster than getVolatile/setVolatile" | On x86, they compile to the same instructions (x86's TSO memory model makes all loads acquire and all stores release). The benefit appears on ARM/POWER architectures. |
| "VarHandle requires unsafe or privileged code" | VarHandle respects Java access control. You can only get a VarHandle for fields your code would normally be able to access (same module, same package, or public). |
| "VarHandle operations are type-checked at each call" | Type checking happens AT LOOKUP TIME (when the VarHandle is created). Each individual `compareAndSet()` call checks only the signature, not full type — it's fast. |

---

### 🚨 Failure Modes & Diagnosis

**1. ClassCastException / WrongMethodTypeException at Call Site**

**Symptom:** `java.lang.ClassCastException` or `WrongMethodTypeException` at the `VarHandle.compareAndSet()` call. Runtime crash, not compile-time error.

**Root Cause:** The argument types passed to the VarHandle operation don't match the types declared at lookup time.

**Example:**
```java
// Looked up as: findVarHandle(Node.class, "value", int.class)
// Call site: VH.compareAndSet(node, (long) 5, (long) 10) ← wrong: long vs int
// Throws: WrongMethodTypeException at runtime
```

**Fix:** Ensure argument types at every call site exactly match the field type declared at lookup. Cast explicitly if needed. Write a unit test for every VarHandle call site.

**Prevention:** Declare VarHandle as `static final` and perform the lookup in a `static {}` block with a `try/catch ExceptionInInitializerError` wrapper — you'll catch lookup errors at class load time. Test every access pattern in unit tests.

---

**2. Incorrect Happens-Before with Acquire/Release Mismatch**

**Symptom:** Intermittent visibility bugs. Thread B reads a stale value even though Thread A wrote it. Very hard to reproduce.

**Root Cause:** Using `setRelease` on writer but `get` (plain) instead of `getAcquire` on reader. The happens-before chain is broken — acquire/release must be paired to establish ordering.

**Diagnostic:**
```java
// BROKEN (no happens-before):
READY.setRelease(this, 1);   // writer: store-release
int r = (int) READY.get(this); // reader: PLAIN read — no acquire!
// No ordering guarantee between writer's prior writes and reader's subsequent reads

// CORRECT:
READY.setRelease(this, 1);         // writer: store-release
int r = (int) READY.getAcquire(this); // reader: LOAD-ACQUIRE — paired!
// Happens-before established between writer's prior writes and reader's subsequent reads
```

**Prevention:** Document every acquire/release pair explicitly. When in doubt, use full volatile — the performance difference is only relevant on non-x86 architectures. For correctness-first code, full volatile is safer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Atomic Classes` — the higher-level, simpler API; understand before VarHandle
- `CAS (Compare-And-Swap)` — the hardware mechanism VarHandle exposes
- `Memory Ordering` — the memory model concepts VarHandle access modes implement
- `Java Memory Model` — the specification that defines what volatile, acquire/release mean

**Builds On This (learn these next):**
- `Lock-Free Data Structures` — what VarHandle enables: stacks, queues, skip lists
- `Low-Level Concurrency Libraries` — Disruptor, Chronicle Map use VarHandle internally
- `Unsafe (sun.misc)` — understand to appreciate why VarHandle was introduced

**Alternatives / Comparisons:**
- `Atomic Classes` — recommended for most use cases; simpler, safer
- `Unsafe (sun.misc)` — predecessor; unsupported, dangerous; avoid in new code
- `StampedLock` — different approach: optimistic read locking at field group level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Type-safe CAS + memory-ordering API for   │
│              │ any field; official replacement for Unsafe│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ sun.misc.Unsafe: unsafe, unsupported;     │
│ SOLVES       │ AtomicRef: wrapper object overhead        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Access modes (plain/opaque/acq-rel/vol):  │
│              │ match ordering cost to algorithm need     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Library/framework code; replacing Unsafe; │
│              │ need acq/rel ordering; CAS on plain fields│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Application code (use AtomicInteger/Ref); │
│              │ team unfamiliar with memory models        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fine-grained performance control vs.      │
│              │ complex API; easy to get ordering wrong   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Unsafe with type-checking and official   │
│              │  JVM support: CAS on any field, safely."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lock-Free Data Structures → Java Memory   │
│              │ Model                                     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The JDK's `ConcurrentHashMap` (Java 17) uses `VarHandle` for its `ABASE` (array base offset) and per-bucket CAS. Specifically, when inserting into an empty bucket, it uses `tabAt()` (load-acquire on the table slot) and `casTabAt()` (CAS volatile on the slot). Explain why `getAcquire` is sufficient for reading the bucket head (rather than `getVolatile`), and why the CAS to insert must be `volatile`-strength (not acquire-release). What ordering invariant must be maintained when a reader traverses the node chain within a bucket?

**Q2.** You are implementing a lock-free ring buffer for a SPSC (single-producer, single-consumer) queue. The producer writes to `buffer[writeIndex % N]` and advances `writeIndex`. The consumer reads from `buffer[readIndex % N]` and advances `readIndex`. Using VarHandle access modes, specify exactly which access mode should be used for: (a) producer writing buffer element, (b) producer advancing writeIndex, (c) consumer reading writeIndex, (d) consumer reading buffer element, (e) consumer advancing readIndex. Justify each choice in terms of the happens-before relationship that must be established.
