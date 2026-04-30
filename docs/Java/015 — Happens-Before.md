---
layout: default
title: "Happens-Before"
parent: "Java Fundamentals"
nav_order: 15
permalink: /java/happens-before/
---
⚡ TL;DR — The Java Memory Model's formal guarantee that all actions performed before a synchronisation point are fully visible to all actions after it — the only correct way to reason about visibility in concurrent Java code.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #015         │ Category: JVM Internals              │ Difficulty: ★★★          │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on:  │ Java Memory Model, Memory Barrier,   │                          │
│              │ volatile, synchronized, Thread        │                          │
│ Used by:     │ volatile, synchronized, final,        │                          │
│              │ Thread.start, Thread.join             │                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 📘 Textbook Definition

Happens-Before is a **formal ordering relationship defined by the Java Memory Model (JMM)** that guarantees visibility and ordering between two actions. If action A happens-before action B, then all memory writes performed by A (and everything before A) are guaranteed to be visible to B (and everything after B). It is the JMM's abstraction over memory barriers — giving developers a platform-independent way to reason about concurrent correctness without knowing CPU architecture details.

---

### 🟢 Simple Definition (Easy)

Happens-Before is the JVM's **written promise**: "If A happens-before B, then B will see everything A wrote — no exceptions, no stale reads, no surprises."

---

### 🔵 Simple Definition (Elaborated)

In a multi-threaded program, without any synchronisation, there is zero guarantee that what one thread writes will ever be seen by another thread — or in what order. Happens-Before defines the specific rules under which visibility IS guaranteed. It's not about time (A doesn't have to literally finish before B starts) — it's about visibility. Establish a happens-before relationship between two actions and the JMM guarantees the reader sees the writer's data. Without it, you're in undefined territory regardless of how your code appears to order operations.

---

### 🔩 First Principles Explanation

**The core problem — visibility is not free:**

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          THE VISIBILITY PROBLEM                                                  │
│                                                                                                  │
│  CPU1 (Thread A)              CPU2 (Thread B)                                                    │
│  ───────────────              ───────────────                                                    │
│  write x = 1                  read x → sees 0 ???                                               │
│  write y = 2                  read y → sees 0 ???                                               │
│                                                                                                  │
│  Why? Because:                                                                                   │
│  1. CPU1's writes sit in store buffer — not yet in memory                                        │
│  2. CPU2's reads come from its own L1 cache — stale                                              │
│  3. Compiler reordered the writes entirely                                                       │
│  4. JIT hoisted reads out of loops — cached in register                                          │
│                                                                                                  │
│  There is NO guarantee Thread B ever sees Thread A's writes                                      │
│  without an explicit synchronisation relationship between them                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**The naive solution — "just use time":**

```
"A writes first, then B reads — so B sees A's write, right?"

WRONG.

"Writes before reads" in wall-clock time does NOT guarantee
visibility. The CPU may not have flushed the store buffer.
The JIT may have reordered. The cache may be stale.

Time ordering ≠ visibility guarantee.
```

**The right solution — a formal model:**

> The JMM defines specific RULES under which visibility is guaranteed. These rules together form the happens-before relationship. Follow the rules → visibility guaranteed. Don't follow the rules → visibility undefined, even if it "works" in testing.

```
Happens-Before is a PARTIAL ORDER on program actions:

If A hb→ B:
  • All writes by A visible to B ✅
  • A's writes cannot be reordered past B ✅
  • Transitive: if A hb→ B and B hb→ C then A hb→ C ✅

If NOT (A hb→ B) AND NOT (B hb→ A):
  • Concurrent — no visibility guarantee
  • Data race possible
  • Undefined behaviour per JMM
```

---

### ❓ Why Does This Exist — Why Before What

**Without Happens-Before:**

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     WITHOUT HAPPENS-BEFORE                                                       │
│                                                                                                  │
│  Problem 1: No portable concurrency model                                                        │
│    x86 has strong memory model → code "works"                                                    │
│    ARM has weak memory model  → same code breaks                                                 │
│    Developer has no portable rules to follow                                                     │
│    → write for x86, ship to ARM, random failures                                                 │
│                                                                                                  │
│  Problem 2: No reasoning tool                                                                    │
│    "I wrote x before y" means nothing without HB                                                 │
│    "I used synchronized" — but where? how?                                                       │
│    No formal model → no way to prove code correct                                                │
│                                                                                                  │
│  Problem 3: Compiler optimisations become unsafe                                                 │
│    JIT can't know which reorderings break your code                                              │
│    → either reorder nothing (slow) or reorder everything (broken)                                │
│    HB tells JIT exactly where it cannot reorder                                                  │
│                                                                                                  │
│  Problem 4: Tool vendors have no contract                                                        │
│    Static analysers, race detectors need a formal model                                          │
│    Without HB → can't define what a "data race" even is                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**What breaks without it:**

```
1. volatile      → no formal definition of what it guarantees
2. synchronized  → no formal definition of what it establishes
3. Thread.start  → no guarantee of what the new thread sees
4. Race detectors→ no formal definition of a data race
5. JIT compiler  → no contract on what it can/cannot reorder
6. Your code     → no way to prove concurrent correctness
```

**With Happens-Before:**

```
→ Platform-independent visibility rules
→ Clear contract: follow these rules = correct concurrent code
→ JIT knows exactly what it cannot reorder
→ Race detectors have a formal definition to enforce
→ You can PROVE your code is correct, not just hope it works
→ Same rules work on x86, ARM, RISC-V, any CPU
```

---

### 🧠 Mental Model / Analogy

> Imagine a large organisation where employees (threads) work in separate offices (CPU cores) and pass documents (memory writes) through an internal mail system.
> 
> **Without happens-before:** Each office has its own inbox and outbox. Nobody knows when documents are delivered. You might send a memo and your colleague might read it in an hour, tomorrow, or never.
> 
> **Happens-Before is a CERTIFIED DELIVERY STAMP.**
> 
> When you stamp a document with happens-before, you're saying: "I guarantee that by the time the recipient opens this, they will also have received ALL documents I sent before this one — and all documents my predecessors sent to me."
> 
> The stamp doesn't mean instant delivery — it means **completeness guarantee**. Everything before the stamp is visible after the stamp.
> 
> Specific stamps: `volatile` write, `synchronized` exit, `Thread.start()`, `Thread.join()` — each is a happens-before certified delivery point.

---

### ⚙️ How It Works — The Eight HB Rules

The JMM defines exactly **eight rules** that establish happens-before. These are the ONLY ways to establish HB in Java:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE EIGHT HAPPENS-BEFORE RULES                                            │
│                                                                                                  │
│  RULE 1: PROGRAM ORDER                                                                           │
│  Within a single thread, every action happens-before                                             │
│  every subsequent action in that thread                                                          │
│  a = 1; hb→ b = 2; (within same thread)                                                         │
│  Note: only within ONE thread — no cross-thread guarantee                                        │
│                                                                                                  │
│  RULE 2: MONITOR LOCK (synchronized)                                                             │
│  Unlocking a monitor happens-before every subsequent                                             │
│  lock of that SAME monitor                                                                       │
│  synchronized exit hb→ synchronized entry (same lock)                                           │
│  Everything written before unlock visible after next lock                                        │
│                                                                                                  │
│  RULE 3: VOLATILE VARIABLE                                                                       │
│  A write to a volatile field happens-before every                                                │
│  subsequent read of that SAME volatile field                                                     │
│  volatile write hb→ volatile read (same variable)                                               │
│  Everything written before volatile write visible                                                │
│  after volatile read                                                                             │
│                                                                                                  │
│  RULE 4: THREAD START                                                                            │
│  Thread.start() on a thread T happens-before any                                                 │
│  action in thread T                                                                              │
│  Everything written before start() visible to new thread                                         │
│                                                                                                  │
│  RULE 5: THREAD TERMINATION (join)                                                               │
│  All actions in thread T happen-before Thread.join(T)                                            │
│  returns                                                                                         │
│  Everything T wrote is visible to thread that called join                                        │
│                                                                                                  │
│  RULE 6: THREAD INTERRUPTION                                                                     │
│  A call to interrupt(T) happens-before thread T                                                  │
│  detects the interrupt (via InterruptedException or                                              │
│  isInterrupted())                                                                                │
│                                                                                                  │
│  RULE 7: FINALIZER                                                                               │
│  Completion of constructor happens-before start                                                  │
│  of finalizer for that object                                                                    │
│                                                                                                  │
│  RULE 8: TRANSITIVITY                                                                            │
│  If A hb→ B and B hb→ C then A hb→ C                                                            │
│  This is what makes HB chains work across multiple                                               │
│  synchronisation points                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects

```
Java Memory Model defines HB rules
            ↓
Developer uses: volatile / synchronized /
                Thread.start / Thread.join
            ↓
HB relationship established between actions
            ↓
JIT Compiler reads HB constraints
  → inserts Memory Barriers at HB boundaries
  → cannot reorder across HB points
            ↓
CPU executes with barriers:
  StoreStore / LoadLoad / StoreLoad
            ↓
Cross-thread visibility guaranteed
at HB synchronisation points
```

---

### 💻 Code Example

**Example 1 — Establishing HB via volatile (Rule 3):**

```java
public class HappensBeforeVolatile {

    private int data = 0;
    private volatile boolean ready = false;

    // Thread A — writer
    public void writer() {
        data = 42;          // ordinary write
                            // Rule 1: data=42 hb→ ready=true (same thread)
        ready = true;       // volatile write
                            // Rule 3: ready=true hb→ any subsequent read of ready
    }

    // Thread B — reader
    public void reader() {
        if (ready) {        // volatile read — establishes HB
                            // Rule 3: write of ready hb→ this read
                            // Rule 8 (transitivity):
                            //   data=42 hb→ ready=true hb→ read of ready
                            //   THEREFORE: data=42 hb→ read of data below
            System.out.println(data); // GUARANTEED to print 42
        }
    }
}
```

**The transitivity chain — this is the key insight:**

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     TRANSITIVITY IN ACTION                                                       │
│                                                                                                  │
│  Thread A:                          Thread B:                                                    │
│  ─────────                          ─────────                                                    │
│  data = 42   ──(Rule 1)──→  ready=true ──(Rule 3)──→  read ready ──(Rule 1)──→  read data       │
│                                                                                                  │
│  Full chain:                                                                                     │
│  data=42  hb→  ready=true  hb→  read(ready)  hb→  read(data)                                    │
│                                                                                                  │
│  By Rule 8 (transitivity):                                                                       │
│  data=42  hb→  read(data)                                                                        │
│                                                                                                  │
│  Conclusion: Thread B's read of data MUST see 42                                                 │
│  This is NOT about timing — it's about the HB chain                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Example 2 — HB via synchronized (Rule 2):**

```java
public class HappensBeforeSynchronized {

    private int counter = 0;
    private final Object lock = new Object();

    // Thread A
    public void increment() {
        synchronized (lock) {
            counter++;
        }   // ← monitor UNLOCK here
            // Rule 2: this unlock hb→ next lock of 'lock'
    }

    // Thread B
    public int read() {
        synchronized (lock) {   // ← monitor LOCK here
                                // sees everything written before unlock
            return counter;     // guaranteed to see latest value
        }
    }
}
```

**Example 3 — HB via Thread.start (Rule 4):**

```java
public class HappensBeforeThreadStart {

    private int config = 0;

    public void setup() {
        config = 42;            // write before start

        Thread t = new Thread(() -> {
            // Rule 4: Thread.start() hb→ every action in this thread
            // config=42 hb→ Thread.start() hb→ this print
            System.out.println(config); // GUARANTEED to print 42
        });

        t.start();              // ← HB boundary: Rule 4
                                // everything before start()
                                // visible to new thread
    }
}
```

**Example 4 — HB via Thread.join (Rule 5):**

```java
public class HappensBeforeJoin {

    private int result = 0;

    public void compute() throws InterruptedException {
        Thread worker = new Thread(() -> {
            result = expensiveComputation(); // write in worker thread
        });                                  // Rule 5: all actions in
                                            // worker hb→ join() returns

        worker.start();
        worker.join();          // ← HB boundary: Rule 5
                                // blocks until worker finishes
                                // worker's writes visible after join

        System.out.println(result); // GUARANTEED to see computed value
    }
}
```

**Example 5 — Data race — NO HB established:**

```java
public class DataRace {
    private int x = 0;
    private int y = 0;

    // Thread A                    // Thread B
    public void threadA() {        public void threadB() {
        x = 1;                         int r1 = y;
        y = 1;                         int r2 = x;
    }                              }

    // No volatile, no synchronized, no HB between threads
    // POSSIBLE OUTCOMES for (r1, r2):
    // (0, 0) → Thread B ran before Thread A
    // (1, 1) → Thread B ran after Thread A
    // (0, 1) → Thread B partially interleaved
    // (1, 0) → ALSO POSSIBLE — CPU/compiler reordering!
    //          y=1 executed before x=1 in Thread A
    //          Thread B sees y=1 but x=0
    //          This is a DATA RACE — undefined by JMM
}
```

**Example 6 — Common mistake: HB doesn't mean atomicity:**

```java
public class HBNotAtomicity {
    private volatile int counter = 0;

    // Thread A and Thread B both call this
    public void increment() {
        counter++;  // looks atomic — IS NOT
        // expands to:
        // int temp = counter;  // volatile READ  → HB established
        // temp = temp + 1;     // arithmetic
        // counter = temp;      // volatile WRITE → HB established
        //
        // But READ and WRITE are TWO separate operations
        // Another thread can interleave between them
        // → lost updates possible
        //
        // HB guarantees VISIBILITY not ATOMICITY
        // Fix: use AtomicInteger.incrementAndGet() → CAS operation
    }
}
```

---

### 🔁 HB Relationship Map — All Establishes

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    WHAT ESTABLISHES HAPPENS-BEFORE                                               │
│                                                                                                  │
│  Action                          →  Happens-Before  →  Action                                   │
│  ──────────────────────────────────────────────────────────────────                              │
│  Any action in thread            →                  →  Next action in same thread                │
│                                                                                                  │
│  volatile WRITE of field X       →                  →  volatile READ of field X                 │
│                                                                                                  │
│  synchronized UNLOCK of M        →                  →  synchronized LOCK of M                   │
│                                                                                                  │
│  Thread.start() call             →                  →  First action in new thread                │
│                                                                                                  │
│  Last action in thread T         →                  →  Thread.join(T) return                    │
│                                                                                                  │
│  Static initializer completes    →                  →  Any thread accessing the class            │
│                                                                                                  │
│  Constructor completes           →                  →  Finalizer starts                          │
│                                                                                                  │
│  Writing to final field          →                  →  Any read after constructor exit           │
│  in constructor                                                                                  │
│                                                                                                  │
│  Future.get() return             →                  →  Caller of get()                           │
│                                                                                                  │
│  CountDownLatch.countDown()      →                  →  CountDownLatch.await() return             │
│                                                                                                  │
│  CyclicBarrier.await() complete  →                  →  Actions after barrier in all threads      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"HB means A executes before B in time"|HB means **visibility** — B sees A's writes; timing is separate|
|"volatile guarantees atomicity"|volatile guarantees **visibility + ordering**; NOT atomicity|
|"synchronized is only about mutual exclusion"|synchronized ALSO establishes **HB** — visibility guarantee on entry/exit|
|"if A writes before B reads in wall time, B sees A's write"|FALSE — wall clock time means nothing without HB relationship|
|"HB is transitive automatically across all actions"|Only transitive **within an established chain** — gaps break it|
|"final fields need no synchronisation"|final fields have special JMM rule — HB from constructor to first read|

---

### 🔥 Pitfalls in Production

**1. Partial synchronisation — HB chain broken**

```java
// BROKEN — HB chain has a gap
public class BrokenChain {
    private int data = 0;
    private volatile boolean ready = false;

    public void writer() {
        data = 42;
        ready = true;   // volatile write — establishes HB ✅
    }

    public void reader() {
        if (ready) {
            // data read is in HB chain ✅
            System.out.println(data);
        }
    }

    // BUT:
    public void brokenReader() {
        boolean localReady = ready; // volatile read → HB established
        // ... 50 lines of unrelated code ...
        // ... HB chain still holds — transitivity ✅

        // BROKEN: reading ready again as non-volatile copy
        if (localReady) {
            System.out.println(data); // still safe — localReady
        }                             // captured from volatile read

        // ACTUALLY BROKEN PATTERN:
        boolean nonVolatileReady = ready; // volatile read ✅
        // someone passes nonVolatileReady to another method
        // that method doesn't know about the HB chain
        // and reads data without any HB → data race ❌
    }
}
```

**2. HB and thread pools — invisible gaps**

```java
// DANGEROUS: submitting tasks to ExecutorService
ExecutorService pool = Executors.newFixedThreadPool(4);

int sharedData = 0;
sharedData = 42;            // write BEFORE submit

pool.submit(() -> {
    // Is sharedData=42 visible here?
    // YES — ExecutorService.submit() establishes HB ✅
    // Java docs: "Actions in a thread prior to the submission
    // of a Runnable to an Executor happen-before its execution"
    System.out.println(sharedData); // safe: 42
});

// BUT:
int[] result = new int[1];
pool.submit(() -> {
    result[0] = compute();  // write in pool thread
});
// ... no join, no Future.get() ...
System.out.println(result[0]); // BROKEN — no HB from task completion
                                // to this read
                                // Fix: Future.get() establishes HB
Future<Integer> f = pool.submit(() -> compute());
System.out.println(f.get()); // ✅ Future.get() hb→ caller
```

**3. Volatile on wrong variable — HB not established**

```java
// BROKEN — volatile on wrong field
public class WrongVolatile {
    private volatile int version = 0;  // volatile
    private int data = 0;              // NOT volatile

    public void update(int newData) {
        version++;      // volatile write → HB established
        data = newData; // BUT: this write is AFTER volatile write
                        // HB only covers writes BEFORE volatile write
                        // data=newData is NOT in the HB chain ❌
    }

    public int read() {
        int v = version; // volatile read
        return data;     // data write was AFTER volatile write
                         // not covered by HB → may be stale ❌
    }

    // FIX: write data BEFORE volatile write
    public void fixedUpdate(int newData) {
        data = newData; // write data first
        version++;      // volatile write AFTER → data is in HB chain ✅
    }
}
```

**4. Safe publication patterns**

```java
// BROKEN — unsafe publication (no HB from constructor to reader)
public class UnsafePublication {
    public int x;
    public int y;

    public UnsafePublication() {
        x = 1;
        y = 2;
    }
}

// Another thread may see partially constructed object:
// x=1, y=0 (default) — constructor not fully visible

// FIX 1: final fields (Rule: constructor hb→ any read after)
public class SafeWithFinal {
    public final int x;
    public final int y;
    public SafeWithFinal() { x = 1; y = 2; }
    // final fields: JMM guarantees constructor completes
    // before any thread can read x or y
}

// FIX 2: volatile reference
public volatile SafePublication instance;
instance = new SafePublication();
// volatile write of reference → HB established
// reader sees fully constructed object

// FIX 3: synchronized publication
synchronized (lock) {
    instance = new SafePublication();
}
// synchronized exit → HB → synchronized entry in reader
```

---

### 🔗 Related Keywords

- `Java Memory Model` — the specification that defines happens-before rules
- `Memory Barrier` — the physical CPU instruction that enforces HB
- `volatile` — establishes HB between write and subsequent read
- `synchronized` — establishes HB between unlock and subsequent lock
- `Thread.start` — establishes HB from pre-start code to new thread
- `Thread.join` — establishes HB from joined thread to caller
- `Data Race` — what happens when two accesses have no HB between them
- `Atomicity` — separate concept from HB; volatile gives visibility not atomicity
- `final` — special JMM rule: constructor completion hb→ any field read
- `VarHandle` — fine-grained HB control with acquire/release semantics
- `CompletableFuture` — establishes HB between completion and thenApply()

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Formal JMM rule: if A hb→ B, everything          │
│              │ A wrote is guaranteed visible to B —             │
│              │ the only safe foundation for concurrent code     │
├──────────────┼───────────────────────────────────────────────────┤
│ USE WHEN     │ Reasoning about any cross-thread visibility:      │
│              │ flags, shared state, object publication,         │
│              │ result passing between threads                   │
├──────────────┼───────────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't assume wall-clock ordering establishes      │
│              │ HB — it doesn't. Don't confuse HB with           │
│              │ atomicity — volatile is not enough for           │
│              │ compound operations like counter++               │
├──────────────┼───────────────────────────────────────────────────┤
│ ONE-LINER    │ "Happens-Before is Java's contract:              │
│              │  establish the relationship and I guarantee      │
│              │  visibility; skip it and you're on your own"     │
├──────────────┼───────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Java Memory Model → volatile → synchronized →    │
│              │ Data Race → VarHandle → AtomicInteger →          │
│              │ CompletableFuture HB chain                       │
└──────────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Consider this common pattern in Spring Boot:

```java
@Component
public class ConfigService {
    private Map<String, String> config;

    @PostConstruct
    public void init() {
        config = loadFromDatabase(); // expensive load at startup
    }

    public String get(String key) {
        return config.get(key); // called by many threads
    }
}
```

Spring initialises beans single-threaded at startup, then serves requests on multiple threads. Is there a happens-before relationship between `@PostConstruct` completing and the first request thread calling `get()`? What guarantees this — or what could break it?

**Q2.** You have a producer-consumer system where the producer writes 10 fields to a shared object and then sets a `volatile boolean done = true`. The consumer spins on `done` and reads all 10 fields when it becomes true. This works correctly. Now your team refactors — they extract the 10 fields into a nested object and the producer sets `volatileDone = true` after constructing it. The consumer reads the nested object's fields after seeing `done = true`. Draw the complete happens-before chain and identify if the guarantee still holds — or where it breaks.

---

Next up: **016 — GC Roots** — the starting points of the garbage collector's reachability graph, what qualifies as a root, and why understanding them is essential for diagnosing memory leaks.

