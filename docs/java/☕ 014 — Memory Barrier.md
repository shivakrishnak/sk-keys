---
layout: default
title: "Memory Barrier"
parent: "Java Fundamentals"
nav_order: 14
permalink: /java/memory-barrier/
---
âš¡ TL;DR â€” A CPU and compiler instruction that prevents reordering of memory operations across a boundary, ensuring all threads see a consistent view of memory at synchronisation points.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #014         â”‚ Category: JVM Internals              â”‚ Difficulty: â˜…â˜…â˜…          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ [[JVM]] [[Java Memory Model]]        â”‚                          â”‚
â”‚              â”‚ [[volatile]] [[CPU Cache]]            â”‚                          â”‚
â”‚ Used by:     â”‚ [[volatile]] [[synchronized]]         â”‚                          â”‚
â”‚              â”‚ [[happens-before]] [[JIT Compiler]]  â”‚                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ“˜ Textbook Definition

A Memory Barrier (also called a Memory Fence) is a **CPU instruction and compiler directive** that enforces ordering constraints on memory operations. It prevents the CPU's out-of-order execution engine and the compiler's optimiser from reordering read/write instructions across the barrier boundary. In Java, memory barriers are the underlying mechanism that implements `volatile`, `synchronized`, `final` field guarantees, and the Java Memory Model's happens-before relationship.

---

### ðŸŸ¢ Simple Definition (Easy)

A memory barrier is a **hard stop sign for reordering** â€” it tells both the CPU and compiler: "everything before this line must complete and be visible to all threads before anything after this line begins."

---

### ðŸ”µ Simple Definition (Elaborated)

Modern CPUs and compilers aggressively reorder instructions for performance â€” executing them out of order, caching writes locally, deferring flushes to main memory. This is invisible and harmless in single-threaded code. But in multi-threaded code, one thread's writes may never become visible to another thread, or may appear in a different order than written. Memory barriers are the mechanism that stops this reordering at specific points â€” flushing caches, draining write buffers, and establishing the ordering guarantees that safe concurrent code depends on.

---

### ðŸ”© First Principles Explanation

**The hardware reality most Java developers never see:**

Modern CPUs don't execute instructions in the order you write them. They have:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              WHY CPUS REORDER                           â”‚
â”‚                                                         â”‚
â”‚  1. OUT-OF-ORDER EXECUTION                              â”‚
â”‚     CPU executes instructions in whatever order         â”‚
â”‚     maximises pipeline utilisation                      â”‚
â”‚     x = 1; y = 2; â†’ CPU may execute y=2 first          â”‚
â”‚     if it's faster (cache hit vs cache miss)            â”‚
â”‚                                                         â”‚
â”‚  2. STORE BUFFERS                                       â”‚
â”‚     Writes don't go directly to memory                  â”‚
â”‚     They sit in a per-CPU store buffer first            â”‚
â”‚     Other CPUs can't see them yet                       â”‚
â”‚                                                         â”‚
â”‚  3. CACHE HIERARCHY                                     â”‚
â”‚     L1/L2 cache per core â€” not shared                   â”‚
â”‚     L3 shared â€” but coherency has latency               â”‚
â”‚     A write on CPU1 may not be in CPU2's L1 for         â”‚
â”‚     hundreds of nanoseconds                             â”‚
â”‚                                                         â”‚
â”‚  4. COMPILER REORDERING                                 â”‚
â”‚     JIT and javac both reorder instructions             â”‚
â”‚     for performance â€” valid in single thread            â”‚
â”‚     catastrophic in multi-thread without barriers       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**The consequence â€” the classic broken example:**

```java
// Thread 1:
data = 42;        // write data
ready = true;     // signal ready

// Thread 2:
while (!ready);   // wait for signal
print(data);      // read data â€” what prints?
```

Without memory barriers:

```
CPU may reorder Thread 1's writes:
  ready = true;   â† executed first (store buffer)
  data = 42;      â† executed second

Thread 2 sees ready=true but data=0 (default)
Prints: 0  â† wrong answer, no exception, silent bug
```

**The solution â€” memory barriers:**

```
Thread 1:
  data = 42;
  [STORE BARRIER] â† flush all pending writes to memory
  ready = true;

Thread 2:
  while(!ready);
  [LOAD BARRIER]  â† invalidate cache, re-read from memory
  print(data);    â† guaranteed to see data=42
```

---

### â“ Why Does This Exist â€” Why Before What

**Without Memory Barriers:**

```
The CPU and compiler's job: make code run FAST
Their tools: reorder, cache, speculate, batch writes

In single-threaded code:
  Reordering is invisible â€” final result identical
  â†’ Pure performance win, no downside

In multi-threaded code:
  Thread A's reordered writes visible to Thread B
  in wrong order â†’ logical corruption
  Thread A's cached writes NEVER flushed to memory
  â†’ Thread B reads stale values forever
  
Symptoms (all silent, no exceptions):
  â†’ Infinite loops (flag never seen as true)
  â†’ Null pointer on initialised objects
  â†’ Partially constructed objects visible
  â†’ Inconsistent state reads
```

**The fundamental tension:**

```
Performance  â†â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’  Correctness
(reorder     (memory barriers:        (all threads
everything)   "stop here, flush,       see consistent
               coordinate")            memory)
```

**What breaks without them:**

```
1. volatile   â†’ reads always stale, writes not visible
2. synchronized â†’ lock acquisition/release meaningless
3. final fields â†’ partially constructed objects visible
4. Singleton DCL â†’ broken double-checked locking
5. Any flag-based thread communication â†’ unreliable
6. JMM happens-before â†’ has no physical enforcement
```

**With Memory Barriers:**

```
â†’ volatile reads/writes cross-thread visible
â†’ synchronized establishes clear before/after
â†’ final fields safely published
â†’ happens-before has real hardware enforcement
â†’ concurrent code can be reasoned about correctly
```

---

### ðŸ§  Mental Model / Analogy

> Imagine multiple chefs (CPU cores) cooking in a large kitchen, each with their own small prep counter (L1 cache / store buffer).
> 
> Each chef writes notes about what they've prepared on their own counter â€” fast, local, private. Other chefs can't see these notes yet.
> 
> **Without a memory barrier:** Chef A writes "sauce is ready" on their counter. Chef B checks the shared whiteboard â€” doesn't see it yet. Serves unsauced dish.
> 
> **A memory barrier is the head chef shouting "STOP â€” everyone post your notes to the shared whiteboard NOW, and re-read the whiteboard before continuing."**
> 
> All pending private writes get flushed to shared memory. All pending reads get invalidated and re-fetched. Every chef now has a consistent view.
> 
> It's expensive (everyone stops briefly) â€” so you only do it at critical coordination points, not after every knife stroke.

---

### âš™ï¸ How It Works â€” Four Types of Barriers

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  MEMORY BARRIER TYPES                           â”‚
â”‚                                                                 â”‚
â”‚  Operations: Load (read) and Store (write)                      â”‚
â”‚  Barriers prevent reordering ACROSS the barrier                 â”‚
â”‚                                                                 â”‚
â”‚  LoadLoad Barrier                                               â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                                  â”‚
â”‚  Load1                                                          â”‚
â”‚  [LoadLoad]  â† Load1 must complete before Load2                 â”‚
â”‚  Load2                                                          â”‚
â”‚  Use: ensure fresh reads in sequence                            â”‚
â”‚                                                                 â”‚
â”‚  StoreStore Barrier                                             â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                             â”‚
â”‚  Store1                                                         â”‚
â”‚  [StoreStore] â† Store1 visible before Store2                    â”‚
â”‚  Store2                                                         â”‚
â”‚  Use: safe object publication (fields before ref)               â”‚
â”‚                                                                 â”‚
â”‚  LoadStore Barrier                                              â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                              â”‚
â”‚  Load1                                                          â”‚
â”‚  [LoadStore] â† Load1 before Store2                              â”‚
â”‚  Store2                                                         â”‚
â”‚  Use: read-then-write sequences that must stay ordered          â”‚
â”‚                                                                 â”‚
â”‚  StoreLoad Barrier (most expensive â€” "full fence")              â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€            â”‚
â”‚  Store1                                                         â”‚
â”‚  [StoreLoad] â† flush store buffer AND invalidate load cache     â”‚
â”‚  Load2                                                          â”‚
â”‚  Use: volatile write followed by volatile read                  â”‚
â”‚  Cost: forces complete memory synchronisation                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**CPU-level instructions (what JIT actually emits):**

```
x86-64:
  MFENCE  â†’ full barrier (StoreLoad) â€” most used
  SFENCE  â†’ store barrier
  LFENCE  â†’ load barrier
  LOCK prefix on instructions â†’ implicit full barrier

ARM:
  DMB ISH  â†’ data memory barrier, inner shareable
  DSB ISH  â†’ data synchronisation barrier
  ISB      â†’ instruction synchronisation barrier
  (ARM requires MORE explicit barriers than x86)

Note: x86 has a stronger memory model than ARM
x86 guarantees store ordering by default
ARM does not â€” needs explicit barriers for everything
This is why Java code can behave differently on ARM
without proper synchronisation
```

---

### ðŸ”„ How It Connects

```
Java Source Code
      â†“
volatile / synchronized / final
      â†“
Java Memory Model (JMM)
  defines happens-before rules
      â†“
JIT Compiler
  translates JMM rules into
  actual memory barrier instructions
      â†“
CPU executes barriers:
  StoreStore  â†’ prevents write reordering
  LoadLoad    â†’ prevents read reordering
  StoreLoad   â†’ full fence (most expensive)
  LoadStore   â†’ prevents load/store reordering
      â†“
All CPU cores see consistent memory state
at synchronisation points
```

---

### ðŸ’» Code Example

**Example 1 â€” volatile and the barriers it inserts:**

```java
public class VolatileBarrier {

    private volatile boolean ready = false;
    private int data = 0;

    // Thread 1 â€” writer
    public void writer() {
        data = 42;              // ordinary write
                                // [StoreStore barrier inserted here by JIT]
        ready = true;           // volatile write
                                // [StoreLoad barrier inserted here by JIT]
        // After volatile write:
        // ALL previous writes flushed to memory
        // Visible to ALL other threads
    }

    // Thread 2 â€” reader
    public void reader() {
        while (!ready);         // volatile read
                                // [LoadLoad barrier inserted here by JIT]
                                // [LoadStore barrier inserted here by JIT]
        // After volatile read:
        // Cache invalidated â€” fresh read from memory
        System.out.println(data); // guaranteed to print 42
    }
}
```

**What the JIT actually emits (x86 pseudocode):**

```asm
; writer():
MOV [data], 42          ; ordinary store
MOV [ready], 1          ; volatile store
MFENCE                  ; â† JIT inserts full memory fence here
                        ;   flushes store buffer to memory
                        ;   all writes before this are visible

; reader():
LOOP:
  MOV EAX, [ready]      ; volatile load â€” reads from memory
  LFENCE                ; â† ensures load is complete before next
  TEST EAX, EAX
  JZ LOOP
MOV EBX, [data]         ; guaranteed fresh â€” barrier above ensures it
```

**Example 2 â€” Broken without barrier (the classic flag pattern):**

```java
// BROKEN â€” no volatile, no barrier
public class BrokenFlag {
    private boolean stop = false;  // not volatile!

    public void runWorker() {
        while (!stop) {            // JIT may cache 'stop' in register
            doWork();              // never re-reads from memory
        }
        // Thread may NEVER stop â€” infinite loop
        // stop=true written by other thread but:
        // â†’ sits in that thread's store buffer
        // â†’ OR cached in this thread's register
        // â†’ this thread never sees it
    }

    public void requestStop() {
        stop = true;               // write goes to store buffer
                                   // no barrier â†’ may never flush
    }
}

// FIXED â€” volatile ensures barrier
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

**Example 3 â€” Double-Checked Locking (DCL) â€” classic barrier story:**

```java
// BROKEN in Java < 5 â€” no barrier on instance
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
                    // 3. assign reference to instance â† reordered!
                    // 2. write fields (constructor)
                    //
                    // Another thread sees non-null instance
                    // but constructor hasn't run yet!
                    // â†’ NullPointerException on field access
                }
            }
        }
        return instance;
    }
}

// FIXED â€” volatile inserts StoreStore barrier
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

**Example 4 â€” VarHandle for fine-grained barriers (Java 9+):**

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

    // Weaker â€” only StoreStore (no StoreLoad)
    // Cheaper than full volatile write
    public void setRelease(int v) {
        VALUE.setRelease(this, v);     // StoreStore barrier only
    }

    // Weaker â€” only LoadLoad (no StoreLoad)
    public int getAcquire() {
        return (int) VALUE.getAcquire(this); // LoadLoad barrier only
    }

    // No barrier â€” plain read/write
    public int getPlain() {
        return (int) VALUE.get(this);  // no barrier
    }
}
```

> `setRelease` + `getAcquire` together form an **acquire-release** pair â€” cheaper than full volatile but still safe for producer-consumer patterns. Only the full `StoreLoad` barrier (volatile write) is truly expensive.

---

### ðŸ” Barrier Costs â€” Performance Reality

```
BARRIER COST HIERARCHY (approximate, x86):

No barrier (plain read/write)
  Cost: ~1 cycle
  Use: single-threaded code, EA-eliminated objects

LoadLoad / StoreStore / LoadStore
  Cost: ~5-10 cycles
  Use: publication patterns, ordered writes

StoreLoad (MFENCE on x86) â€” full fence
  Cost: ~100-200 cycles
  Use: volatile write, synchronized exit

Compare to:
  L1 cache hit:    ~4 cycles
  L2 cache hit:    ~12 cycles
  L3 cache hit:    ~40 cycles
  Main memory:     ~200 cycles

StoreLoad â‰ˆ main memory access cost
â†’ This is why volatile writes are expensive
â†’ This is why lock-free code needs careful design
â†’ This is why false sharing kills performance
   (forces unnecessary barrier + cache invalidation)
```

---

### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"volatile means stored in RAM not cache"|volatile means **barriers are inserted** â€” it's about ordering, not storage location|
|"synchronized is just a mutex"|synchronized also inserts **full memory barriers** on entry and exit|
|"memory barriers are Java-specific"|They are **CPU instructions** â€” Java exposes them through JMM abstractions|
|"x86 doesn't need barriers"|x86 is strong but still needs **StoreLoad** barrier for volatile semantics|
|"barriers are slow"|LoadLoad/StoreStore are cheap (~5 cycles); only **StoreLoad is expensive** (~200 cycles)|
|"final fields need no barriers"|JMM inserts **StoreStore barrier** after constructor to safely publish final fields|

---

### ðŸ”¥ Pitfalls in Production

**1. Missing volatile on flags â€” silent infinite loops**

```java
// This bug is invisible in testing (single-core CI machines)
// Manifests only on multi-core production servers
// JIT compiles the loop â†’ hoists the read â†’ never re-checks

private boolean running = true; // missing volatile!

// JIT optimises to (conceptually):
// boolean cached_running = running; // read once
// while (cached_running) { doWork(); } // never re-reads

// Fix: always volatile for cross-thread flags
private volatile boolean running = true;
```

**2. Volatile array reference vs volatile array elements**

```java
// volatile on REFERENCE â€” not on elements!
private volatile int[] array = new int[10];

// Thread 1:
array[0] = 42;        // NOT volatile â€” no barrier
                      // other threads may not see this

// Thread 2:
int val = array[0];   // may read stale value
                      // volatile only on array reference,
                      // not on individual element writes

// Fix: use AtomicIntegerArray
private AtomicIntegerArray array = new AtomicIntegerArray(10);
array.set(0, 42);     // full barrier per element
```

**3. False sharing â€” invisible barrier storm**

```java
// Two fields on the same cache line (64 bytes)
// Thread A writes field1 â†’ invalidates cache line
// Thread B reads field2 â†’ must re-fetch whole cache line
// â†’ As expensive as if they shared a variable
// â†’ Barrier-level cost without any barrier in code

public class FalseSharing {
    // BAD: both fields likely on same 64-byte cache line
    volatile long field1 = 0;  // offset 0
    volatile long field2 = 0;  // offset 8 â€” same cache line!
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
//   Works perfectly â€” x86 provides many guarantees implicitly

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

### ðŸ”— Related Keywords

- `volatile` â€” inserts LoadLoad + LoadStore after reads, StoreStore + StoreLoad after writes
- `synchronized` â€” full barriers on monitor enter and exit
- `happens-before` â€” the JMM abstraction that memory barriers enforce
- `Java Memory Model (JMM)` â€” the spec that defines when barriers are required
- `VarHandle` â€” Java 9+ API for fine-grained barrier control
- `False Sharing` â€” cache line invalidation that mimics barrier cost
- `CPU Cache` â€” what barriers flush and invalidate
- `JIT Compiler` â€” emits the actual barrier instructions
- `Atomic classes` â€” built on CAS + implicit barriers
- `@Contended` â€” annotation to prevent false sharing via padding
- `StoreLoad` â€” most expensive barrier type; used by volatile write

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ CPU + compiler instruction that prevents  â”‚
â”‚              â”‚ reordering across a boundary â€” the        â”‚
â”‚              â”‚ physical enforcement of happens-before    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Cross-thread communication, flag-based    â”‚
â”‚              â”‚ coordination, safe publication of objects â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't insert barriers on every operation  â”‚
â”‚              â”‚ â€” use them at coordination points only;   â”‚
â”‚              â”‚ prefer acquire-release over full fences   â”‚
â”‚              â”‚ where possible                            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "A memory barrier is the JVM telling the  â”‚
â”‚              â”‚  CPU: stop speculating, flush everything, â”‚
â”‚              â”‚  let everyone catch up"                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ volatile â†’ Java Memory Model â†’            â”‚
â”‚              â”‚ happens-before â†’ synchronized internals â†’ â”‚
â”‚              â”‚ VarHandle â†’ False Sharing â†’ @Contended    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** The `StoreLoad` barrier is the most expensive â€” approximately 200 CPU cycles, equivalent to a main memory access. Every `volatile` write emits one. Now consider a high-throughput counter incremented by multiple threads using `volatile`. At 10 million increments/second across 8 threads, what is the approximate CPU cycle cost just from barriers â€” and what would you use instead, and why?

**Q2.** Consider this code running on a multi-core ARM server (not x86):

```java
int a = 0, b = 0; // shared, non-volatile

// Thread 1:        // Thread 2:
a = 1;             int r1 = b;
b = 1;             int r2 = a;
```

Is it possible for Thread 2 to observe `r1 = 1` and `r2 = 0` simultaneously? Would this be possible on x86? What does your answer reveal about the difference between x86 and ARM memory models â€” and why does Java's JMM abstract this away?

---

Next up: **015 â€” Happens-Before** â€” the Java Memory Model's formal guarantee of visibility and ordering between operations, how it's established, and why it's the only safe way to reason about concurrent Java code.

Shall I continue?
