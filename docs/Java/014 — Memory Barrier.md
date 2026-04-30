---
layout: default
title: "Memory Barrier"
parent: "Java & JVM Internals"
nav_order: 14
permalink: /java/memory-barrier/
---
# 014 — Memory Barrier

`#java` `#jvm` `#concurrency` `#internals` `#deep-dive`

⚡ TL;DR — A CPU and compiler instruction that prevents reordering of memory operations across a boundary, ensuring all threads see a consistent view of memory at synchronisation points.

| #014 | Category: JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Java Memory Model, volatile, CPU Cache | |
| **Used by:** | volatile, synchronized, Happens-Before, JIT Compiler | |

---

### 📘 Textbook Definition

A Memory Barrier (also called a Memory Fence) is a **CPU instruction and compiler directive** that enforces ordering constraints on memory operations. It prevents the CPU's out-of-order execution engine and the compiler's optimiser from reordering read/write instructions across the barrier boundary. In Java, memory barriers are the underlying mechanism that implements `volatile`, `synchronized`, `final` field guarantees, and the Java Memory Model's happens-before relationship.

---

### 🟢 Simple Definition (Easy)

A memory barrier is a **hard stop sign for reordering** — it tells both the CPU and compiler: "everything before this line must complete and be visible to all threads before anything after this line begins."

---

### 🔵 Simple Definition (Elaborated)

Modern CPUs and compilers aggressively reorder instructions for performance — executing them out of order, caching writes locally, deferring flushes to main memory. This is invisible and harmless in single-threaded code. But in multi-threaded code, one thread's writes may never become visible to another thread, or may appear in a different order than written. Memory barriers are the mechanism that stops this reordering at specific points — flushing caches, draining write buffers, and establishing the ordering guarantees that safe concurrent code depends on.

---

### 🔩 First Principles Explanation

**The hardware reality most Java developers never see:**

Modern CPUs don't execute instructions in the order you write them. They have:

**The consequence — the classic broken example:**

```java
// Thread 1:
data = 42;        // write data
ready = true;     // signal ready

// Thread 2:
while (!ready);   // wait for signal
print(data);      // read data — what prints?
```

Without memory barriers:

```
CPU may reorder Thread 1's writes:
  ready = true;   ← executed first (store buffer)
  data = 42;      ← executed second

Thread 2 sees ready=true but data=0 (default)
Prints: 0  ← wrong answer, no exception, silent bug
```

**The solution — memory barriers:**

```
Thread 1:
  data = 42;
  [STORE BARRIER] ← flush all pending writes to memory
  ready = true;

Thread 2:
  while(!ready);
  [LOAD BARRIER]  ← invalidate cache, re-read from memory
  print(data);    ← guaranteed to see data=42
```

---

### ❓ Why Does This Exist — Why Before What

**Without Memory Barriers:**

```
The CPU and compiler's job: make code run FAST
Their tools: reorder, cache, speculate, batch writes

In single-threaded code:
  Reordering is invisible — final result identical
  → Pure performance win, no downside

In multi-threaded code:
  Thread A's reordered writes visible to Thread B
  in wrong order → logical corruption
  Thread A's cached writes NEVER flushed to memory
  → Thread B reads stale values forever
  
Symptoms (all silent, no exceptions):
  → Infinite loops (flag never seen as true)
  → Null pointer on initialised objects
  → Partially constructed objects visible
  → Inconsistent state reads
```

**The fundamental tension:**

```
Performance  ←────────────────────→  Correctness
(reorder     (memory barriers:        (all threads
everything)   "stop here, flush,       see consistent
               coordinate")            memory)
```

**What breaks without them:**

```
1. volatile   → reads always stale, writes not visible
2. synchronized → lock acquisition/release meaningless
3. final fields → partially constructed objects visible
4. Singleton DCL → broken double-checked locking
5. Any flag-based thread communication → unreliable
6. JMM happens-before → has no physical enforcement
```

**With Memory Barriers:**

```
→ volatile reads/writes cross-thread visible
→ synchronized establishes clear before/after
→ final fields safely published
→ happens-before has real hardware enforcement
→ concurrent code can be reasoned about correctly
```

---

### 🧠 Mental Model / Analogy

> Imagine multiple chefs (CPU cores) cooking in a large kitchen, each with their own small prep counter (L1 cache / store buffer).
> 
> Each chef writes notes about what they've prepared on their own counter — fast, local, private. Other chefs can't see these notes yet.
> 
> **Without a memory barrier:** Chef A writes "sauce is ready" on their counter. Chef B checks the shared whiteboard — doesn't see it yet. Serves unsauced dish.
> 
> **A memory barrier is the head chef shouting "STOP — everyone post your notes to the shared whiteboard NOW, and re-read the whiteboard before continuing."**
> 
> All pending private writes get flushed to shared memory. All pending reads get invalidated and re-fetched. Every chef now has a consistent view.
> 
> It's expensive (everyone stops briefly) — so you only do it at critical coordination points, not after every knife stroke.

---

### ⚙️ How It Works — Four Types of Barriers

**CPU-level instructions (what JIT actually emits):**

```
x86-64:
  MFENCE  → full barrier (StoreLoad) — most used
  SFENCE  → store barrier
  LFENCE  → load barrier
  LOCK prefix on instructions → implicit full barrier

ARM:
  DMB ISH  → data memory barrier, inner shareable
  DSB ISH  → data synchronisation barrier
  ISB      → instruction synchronisation barrier
  (ARM requires MORE explicit barriers than x86)

Note: x86 has a stronger memory model than ARM
x86 guarantees store ordering by default
ARM does not — needs explicit barriers for everything
This is why Java code can behave differently on ARM
without proper synchronisation
```

---

### 🔄 How It Connects

```
Java Source Code
      ↓
volatile / synchronized / final
      ↓
Java Memory Model (JMM)
  defines happens-before rules
      ↓
JIT Compiler
  translates JMM rules into
  actual memory barrier instructions
      ↓
CPU executes barriers:
  StoreStore  → prevents write reordering
  LoadLoad    → prevents read reordering
  StoreLoad   → full fence (most expensive)
  LoadStore   → prevents load/store reordering
      ↓
All CPU cores see consistent memory state
at synchronisation points
```

---

### 💻 Code Example

**Example 1 — volatile and the barriers it inserts:**

```java
public class VolatileBarrier {

    private volatile boolean ready = false;
    private int data = 0;

    // Thread 1 — writer
    public void writer() {
        data = 42;              // ordinary write
                                // [StoreStore barrier inserted here by JIT]
        ready = true;           // volatile write
                                // [StoreLoad barrier inserted here by JIT]
        // After volatile write:
        // ALL previous writes flushed to memory
        // Visible to ALL other threads
    }

    // Thread 2 — reader
    public void reader() {
        while (!ready);         // volatile read
                                // [LoadLoad barrier inserted here by JIT]
                                // [LoadStore barrier inserted here by JIT]
        // After volatile read:
        // Cache invalidated — fresh read from memory
        System.out.println(data); // guaranteed to print 42
    }
}
```

**What the JIT actually emits (x86 pseudocode):**

```asm
; writer():
MOV [data], 42          ; ordinary store
MOV [ready], 1          ; volatile store
MFENCE                  ; ← JIT inserts full memory fence here
                        ;   flushes store buffer to memory
                        ;   all writes before this are visible

; reader():
LOOP:
  MOV EAX, [ready]      ; volatile load — reads from memory
  LFENCE                ; ← ensures load is complete before next
  TEST EAX, EAX
  JZ LOOP
MOV EBX, [data]         ; guaranteed fresh — barrier above ensures it
```

**Example 2 — Broken without barrier (the classic flag pattern):**

```java
// BROKEN — no volatile, no barrier
public class BrokenFlag {
    private boolean stop = false;  // not volatile!

    public void runWorker() {
        while (!stop) {            // JIT may cache 'stop' in register
            doWork();              // never re-reads from memory
        }
        // Thread may NEVER stop — infinite loop
        // stop=true written by other thread but:
        // → sits in that thread's store buffer
        // → OR cached in this thread's register
        // → this thread never sees it
    }

    public void requestStop() {
        stop = true;               // write goes to store buffer
                                   // no barrier → may never flush
    }
}

// FIXED — volatile ensures barrier
public class FixedFlag {
    private volatile boolean stop = false;  // volatile!

    public void runWorker() {
        while (!stop) {            // volatile read = fresh from memory
            doWork();              // LoadLoad barrier after each read
        }
    }

    public void requestStop() {
        stop = true;               // StoreLoad barrier after volatile write
                                   // flushes to memory immediately
    }
}
```

**Example 3 — Double-Checked Locking (DCL) — classic barrier story:**

```java
// BROKEN in Java < 5 — no barrier on instance
public class BrokenSingleton {
    private static BrokenSingleton instance;

    public static BrokenSingleton getInstance() {
        if (instance == null) {              // check 1
            synchronized (BrokenSingleton.class) {
                if (instance == null) {      // check 2
                    instance = new BrokenSingleton();
                    // new BrokenSingleton() compiles to:
                    // 1. allocate memory
                    // 2. write fields (constructor)
                    // 3. assign reference to instance
                    //
                    // CPU may REORDER to:
                    // 1. allocate memory
                    // 3. assign reference to instance ← reordered!
                    // 2. write fields (constructor)
                    //
                    // Another thread sees non-null instance
                    // but constructor hasn't run yet!
                    // → NullPointerException on field access
                }
            }
        }
        return instance;
    }
}

// FIXED — volatile inserts StoreStore barrier
// prevents reordering of constructor writes
// and reference assignment
public class FixedSingleton {
    private static volatile FixedSingleton instance; // volatile!

    public static FixedSingleton getInstance() {
        if (instance == null) {
            synchronized (FixedSingleton.class) {
                if (instance == null) {
                    instance = new FixedSingleton();
                    // volatile write = StoreStore barrier
                    // GUARANTEES: all constructor writes complete
                    // BEFORE reference becomes visible to other threads
                }
            }
        }
        return instance;
    }
}
```

**Example 4 — VarHandle for fine-grained barriers (Java 9+):**

```java
import java.lang.invoke.*;

public class VarHandleBarrier {
    private int value = 0;

    private static final VarHandle VALUE;
    static {
        try {
            VALUE = MethodHandles.lookup()
                .findVarHandle(VarHandleBarrier.class,
                               "value", int.class);
        } catch (Exception e) { throw new Error(e); }
    }

    // Full volatile semantics
    public void setVolatile(int v) {
        VALUE.setVolatile(this, v);    // StoreLoad barrier
    }

    // Weaker — only StoreStore (no StoreLoad)
    // Cheaper than full volatile write
    public void setRelease(int v) {
        VALUE.setRelease(this, v);     // StoreStore barrier only
    }

    // Weaker — only LoadLoad (no StoreLoad)
    public int getAcquire() {
        return (int) VALUE.getAcquire(this); // LoadLoad barrier only
    }

    // No barrier — plain read/write
    public int getPlain() {
        return (int) VALUE.get(this);  // no barrier
    }
}
```

> `setRelease` + `getAcquire` together form an **acquire-release** pair — cheaper than full volatile but still safe for producer-consumer patterns. Only the full `StoreLoad` barrier (volatile write) is truly expensive.

---

### 🔁 Barrier Costs — Performance Reality

```
BARRIER COST HIERARCHY (approximate, x86):

No barrier (plain read/write)
  Cost: ~1 cycle
  Use: single-threaded code, EA-eliminated objects

LoadLoad / StoreStore / LoadStore
  Cost: ~5-10 cycles
  Use: publication patterns, ordered writes

StoreLoad (MFENCE on x86) — full fence
  Cost: ~100-200 cycles
  Use: volatile write, synchronized exit

Compare to:
  L1 cache hit:    ~4 cycles
  L2 cache hit:    ~12 cycles
  L3 cache hit:    ~40 cycles
  Main memory:     ~200 cycles

StoreLoad ≈ main memory access cost
→ This is why volatile writes are expensive
→ This is why lock-free code needs careful design
→ This is why false sharing kills performance
   (forces unnecessary barrier + cache invalidation)
```

---

### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"volatile means stored in RAM not cache"|volatile means **barriers are inserted** — it's about ordering, not storage location|
|"synchronized is just a mutex"|synchronized also inserts **full memory barriers** on entry and exit|
|"memory barriers are Java-specific"|They are **CPU instructions** — Java exposes them through JMM abstractions|
|"x86 doesn't need barriers"|x86 is strong but still needs **StoreLoad** barrier for volatile semantics|
|"barriers are slow"|LoadLoad/StoreStore are cheap (~5 cycles); only **StoreLoad is expensive** (~200 cycles)|
|"final fields need no barriers"|JMM inserts **StoreStore barrier** after constructor to safely publish final fields|

---

### 🔥 Pitfalls in Production

**1. Missing volatile on flags — silent infinite loops**

```java
// This bug is invisible in testing (single-core CI machines)
// Manifests only on multi-core production servers
// JIT compiles the loop → hoists the read → never re-checks

private boolean running = true; // missing volatile!

// JIT optimises to (conceptually):
// boolean cached_running = running; // read once
// while (cached_running) { doWork(); } // never re-reads

// Fix: always volatile for cross-thread flags
private volatile boolean running = true;
```

**2. Volatile array reference vs volatile array elements**

```java
// volatile on REFERENCE — not on elements!
private volatile int[] array = new int[10];

// Thread 1:
array[0] = 42;        // NOT volatile — no barrier
                      // other threads may not see this

// Thread 2:
int val = array[0];   // may read stale value
                      // volatile only on array reference,
                      // not on individual element writes

// Fix: use AtomicIntegerArray
private AtomicIntegerArray array = new AtomicIntegerArray(10);
array.set(0, 42);     // full barrier per element
```

**3. False sharing — invisible barrier storm**

```java
// Two fields on the same cache line (64 bytes)
// Thread A writes field1 → invalidates cache line
// Thread B reads field2 → must re-fetch whole cache line
// → As expensive as if they shared a variable
// → Barrier-level cost without any barrier in code

public class FalseSharing {
    // BAD: both fields likely on same 64-byte cache line
    volatile long field1 = 0;  // offset 0
    volatile long field2 = 0;  // offset 8 — same cache line!
}

// FIX: pad to separate cache lines
public class NoFalseSharing {
    volatile long field1 = 0;
    long p1, p2, p3, p4, p5, p6, p7; // 56 bytes padding
    volatile long field2 = 0;         // different cache line
}

// Or use @Contended (Java 8+):
@jdk.internal.vm.annotation.Contended
volatile long field1 = 0;
@jdk.internal.vm.annotation.Contended
volatile long field2 = 0;
// JVM adds padding automatically
// Requires: -XX:-RestrictContended
```

**4. Assuming ARM behaves like x86**

```java
// Code tested on x86 (strong memory model):
//   Works perfectly — x86 provides many guarantees implicitly

// Deployed on ARM (weak memory model):
//   Missing barriers become real problems
//   ARM requires explicit barriers for orderings
//   x86 provides implicitly

// Concrete: Java code without volatile running on ARM
// may exhibit broken behaviour that NEVER appeared on x86

// Fix: always use proper Java synchronisation primitives
// Never rely on x86-specific behaviour
// volatile/synchronized work correctly on ALL platforms
// because JIT emits platform-appropriate barriers
```

---

### 🔗 Related Keywords

- `volatile` — inserts LoadLoad + LoadStore after reads, StoreStore + StoreLoad after writes
- `synchronized` — full barriers on monitor enter and exit
- `happens-before` — the JMM abstraction that memory barriers enforce
- `Java Memory Model (JMM)` — the spec that defines when barriers are required
- `VarHandle` — Java 9+ API for fine-grained barrier control
- `False Sharing` — cache line invalidation that mimics barrier cost
- `CPU Cache` — what barriers flush and invalidate
- `JIT Compiler` — emits the actual barrier instructions
- `Atomic classes` — built on CAS + implicit barriers
- `@Contended` — annotation to prevent false sharing via padding
- `StoreLoad` — most expensive barrier type; used by volatile write

---

### 📌 Quick Reference Card

---

### 🧠 Think About This Before We Continue

**Q1.** The `StoreLoad` barrier is the most expensive — approximately 200 CPU cycles, equivalent to a main memory access. Every `volatile` write emits one. Now consider a high-throughput counter incremented by multiple threads using `volatile`. At 10 million increments/second across 8 threads, what is the approximate CPU cycle cost just from barriers — and what would you use instead, and why?

**Q2.** Consider this code running on a multi-core ARM server (not x86):

```java
int a = 0, b = 0; // shared, non-volatile

// Thread 1:        // Thread 2:
a = 1;             int r1 = b;
b = 1;             int r2 = a;
```

Is it possible for Thread 2 to observe `r1 = 1` and `r2 = 0` simultaneously? Would this be possible on x86? What does your answer reveal about the difference between x86 and ARM memory models — and why does Java's JMM abstract this away?

---

Next up: **015 — Happens-Before** — the Java Memory Model's formal guarantee of visibility and ordering between operations, how it's established, and why it's the only safe way to reason about concurrent Java code.

Shall I continue?
