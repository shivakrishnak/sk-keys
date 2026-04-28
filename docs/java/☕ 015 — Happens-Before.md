---
layout: default
title: "Happens-Before"
parent: "Java Fundamentals"
nav_order: 15
permalink: /java/happens-before/
---
âš¡ TL;DR â€” The Java Memory Model's formal guarantee that all actions performed before a synchronisation point are fully visible to all actions after it â€” the only correct way to reason about visibility in concurrent Java code.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #015         â”‚ Category: JVM Internals              â”‚ Difficulty: â˜…â˜…â˜…          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ Java Memory Model, Memory Barrier,   â”‚                          â”‚
â”‚              â”‚ volatile, synchronized, Thread        â”‚                          â”‚
â”‚ Used by:     â”‚ volatile, synchronized, final,        â”‚                          â”‚
â”‚              â”‚ Thread.start, Thread.join             â”‚                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ“˜ Textbook Definition

Happens-Before is a **formal ordering relationship defined by the Java Memory Model (JMM)** that guarantees visibility and ordering between two actions. If action A happens-before action B, then all memory writes performed by A (and everything before A) are guaranteed to be visible to B (and everything after B). It is the JMM's abstraction over memory barriers â€” giving developers a platform-independent way to reason about concurrent correctness without knowing CPU architecture details.

---

### ðŸŸ¢ Simple Definition (Easy)

Happens-Before is the JVM's **written promise**: "If A happens-before B, then B will see everything A wrote â€” no exceptions, no stale reads, no surprises."

---

### ðŸ”µ Simple Definition (Elaborated)

In a multi-threaded program, without any synchronisation, there is zero guarantee that what one thread writes will ever be seen by another thread â€” or in what order. Happens-Before defines the specific rules under which visibility IS guaranteed. It's not about time (A doesn't have to literally finish before B starts) â€” it's about visibility. Establish a happens-before relationship between two actions and the JMM guarantees the reader sees the writer's data. Without it, you're in undefined territory regardless of how your code appears to order operations.

---

### ðŸ”© First Principles Explanation

**The core problem â€” visibility is not free:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                          THE VISIBILITY PROBLEM                                                  â”‚
â”‚                                                                                                  â”‚
â”‚  CPU1 (Thread A)              CPU2 (Thread B)                                                    â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€              â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                                    â”‚
â”‚  write x = 1                  read x â†’ sees 0 ???                                               â”‚
â”‚  write y = 2                  read y â†’ sees 0 ???                                               â”‚
â”‚                                                                                                  â”‚
â”‚  Why? Because:                                                                                   â”‚
â”‚  1. CPU1's writes sit in store buffer â€” not yet in memory                                        â”‚
â”‚  2. CPU2's reads come from its own L1 cache â€” stale                                              â”‚
â”‚  3. Compiler reordered the writes entirely                                                       â”‚
â”‚  4. JIT hoisted reads out of loops â€” cached in register                                          â”‚
â”‚                                                                                                  â”‚
â”‚  There is NO guarantee Thread B ever sees Thread A's writes                                      â”‚
â”‚  without an explicit synchronisation relationship between them                                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**The naive solution â€” "just use time":**

```
"A writes first, then B reads â€” so B sees A's write, right?"

WRONG.

"Writes before reads" in wall-clock time does NOT guarantee
visibility. The CPU may not have flushed the store buffer.
The JIT may have reordered. The cache may be stale.

Time ordering â‰  visibility guarantee.
```

**The right solution â€” a formal model:**

> The JMM defines specific RULES under which visibility is guaranteed. These rules together form the happens-before relationship. Follow the rules â†’ visibility guaranteed. Don't follow the rules â†’ visibility undefined, even if it "works" in testing.

```
Happens-Before is a PARTIAL ORDER on program actions:

If A hbâ†’ B:
  â€¢ All writes by A visible to B âœ…
  â€¢ A's writes cannot be reordered past B âœ…
  â€¢ Transitive: if A hbâ†’ B and B hbâ†’ C then A hbâ†’ C âœ…

If NOT (A hbâ†’ B) AND NOT (B hbâ†’ A):
  â€¢ Concurrent â€” no visibility guarantee
  â€¢ Data race possible
  â€¢ Undefined behaviour per JMM
```

---

### â“ Why Does This Exist â€” Why Before What

**Without Happens-Before:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     WITHOUT HAPPENS-BEFORE                                                       â”‚
â”‚                                                                                                  â”‚
â”‚  Problem 1: No portable concurrency model                                                        â”‚
â”‚    x86 has strong memory model â†’ code "works"                                                    â”‚
â”‚    ARM has weak memory model  â†’ same code breaks                                                 â”‚
â”‚    Developer has no portable rules to follow                                                     â”‚
â”‚    â†’ write for x86, ship to ARM, random failures                                                 â”‚
â”‚                                                                                                  â”‚
â”‚  Problem 2: No reasoning tool                                                                    â”‚
â”‚    "I wrote x before y" means nothing without HB                                                 â”‚
â”‚    "I used synchronized" â€” but where? how?                                                       â”‚
â”‚    No formal model â†’ no way to prove code correct                                                â”‚
â”‚                                                                                                  â”‚
â”‚  Problem 3: Compiler optimisations become unsafe                                                 â”‚
â”‚    JIT can't know which reorderings break your code                                              â”‚
â”‚    â†’ either reorder nothing (slow) or reorder everything (broken)                                â”‚
â”‚    HB tells JIT exactly where it cannot reorder                                                  â”‚
â”‚                                                                                                  â”‚
â”‚  Problem 4: Tool vendors have no contract                                                        â”‚
â”‚    Static analysers, race detectors need a formal model                                          â”‚
â”‚    Without HB â†’ can't define what a "data race" even is                                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**What breaks without it:**

```
1. volatile      â†’ no formal definition of what it guarantees
2. synchronized  â†’ no formal definition of what it establishes
3. Thread.start  â†’ no guarantee of what the new thread sees
4. Race detectorsâ†’ no formal definition of a data race
5. JIT compiler  â†’ no contract on what it can/cannot reorder
6. Your code     â†’ no way to prove concurrent correctness
```

**With Happens-Before:**

```
â†’ Platform-independent visibility rules
â†’ Clear contract: follow these rules = correct concurrent code
â†’ JIT knows exactly what it cannot reorder
â†’ Race detectors have a formal definition to enforce
â†’ You can PROVE your code is correct, not just hope it works
â†’ Same rules work on x86, ARM, RISC-V, any CPU
```

---

### ðŸ§  Mental Model / Analogy

> Imagine a large organisation where employees (threads) work in separate offices (CPU cores) and pass documents (memory writes) through an internal mail system.
> 
> **Without happens-before:** Each office has its own inbox and outbox. Nobody knows when documents are delivered. You might send a memo and your colleague might read it in an hour, tomorrow, or never.
> 
> **Happens-Before is a CERTIFIED DELIVERY STAMP.**
> 
> When you stamp a document with happens-before, you're saying: "I guarantee that by the time the recipient opens this, they will also have received ALL documents I sent before this one â€” and all documents my predecessors sent to me."
> 
> The stamp doesn't mean instant delivery â€” it means **completeness guarantee**. Everything before the stamp is visible after the stamp.
> 
> Specific stamps: `volatile` write, `synchronized` exit, `Thread.start()`, `Thread.join()` â€” each is a happens-before certified delivery point.

---

### âš™ï¸ How It Works â€” The Eight HB Rules

The JMM defines exactly **eight rules** that establish happens-before. These are the ONLY ways to establish HB in Java:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        THE EIGHT HAPPENS-BEFORE RULES                                            â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 1: PROGRAM ORDER                                                                           â”‚
â”‚  Within a single thread, every action happens-before                                             â”‚
â”‚  every subsequent action in that thread                                                          â”‚
â”‚  a = 1; hbâ†’ b = 2; (within same thread)                                                         â”‚
â”‚  Note: only within ONE thread â€” no cross-thread guarantee                                        â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 2: MONITOR LOCK (synchronized)                                                             â”‚
â”‚  Unlocking a monitor happens-before every subsequent                                             â”‚
â”‚  lock of that SAME monitor                                                                       â”‚
â”‚  synchronized exit hbâ†’ synchronized entry (same lock)                                           â”‚
â”‚  Everything written before unlock visible after next lock                                        â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 3: VOLATILE VARIABLE                                                                       â”‚
â”‚  A write to a volatile field happens-before every                                                â”‚
â”‚  subsequent read of that SAME volatile field                                                     â”‚
â”‚  volatile write hbâ†’ volatile read (same variable)                                               â”‚
â”‚  Everything written before volatile write visible                                                â”‚
â”‚  after volatile read                                                                             â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 4: THREAD START                                                                            â”‚
â”‚  Thread.start() on a thread T happens-before any                                                 â”‚
â”‚  action in thread T                                                                              â”‚
â”‚  Everything written before start() visible to new thread                                         â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 5: THREAD TERMINATION (join)                                                               â”‚
â”‚  All actions in thread T happen-before Thread.join(T)                                            â”‚
â”‚  returns                                                                                         â”‚
â”‚  Everything T wrote is visible to thread that called join                                        â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 6: THREAD INTERRUPTION                                                                     â”‚
â”‚  A call to interrupt(T) happens-before thread T                                                  â”‚
â”‚  detects the interrupt (via InterruptedException or                                              â”‚
â”‚  isInterrupted())                                                                                â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 7: FINALIZER                                                                               â”‚
â”‚  Completion of constructor happens-before start                                                  â”‚
â”‚  of finalizer for that object                                                                    â”‚
â”‚                                                                                                  â”‚
â”‚  RULE 8: TRANSITIVITY                                                                            â”‚
â”‚  If A hbâ†’ B and B hbâ†’ C then A hbâ†’ C                                                            â”‚
â”‚  This is what makes HB chains work across multiple                                               â”‚
â”‚  synchronisation points                                                                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ”„ How It Connects

```
Java Memory Model defines HB rules
            â†“
Developer uses: volatile / synchronized /
                Thread.start / Thread.join
            â†“
HB relationship established between actions
            â†“
JIT Compiler reads HB constraints
  â†’ inserts Memory Barriers at HB boundaries
  â†’ cannot reorder across HB points
            â†“
CPU executes with barriers:
  StoreStore / LoadLoad / StoreLoad
            â†“
Cross-thread visibility guaranteed
at HB synchronisation points
```

---

### ðŸ’» Code Example

**Example 1 â€” Establishing HB via volatile (Rule 3):**

```java
public class HappensBeforeVolatile {

    private int data = 0;
    private volatile boolean ready = false;

    // Thread A â€” writer
    public void writer() {
        data = 42;          // ordinary write
                            // Rule 1: data=42 hbâ†’ ready=true (same thread)
        ready = true;       // volatile write
                            // Rule 3: ready=true hbâ†’ any subsequent read of ready
    }

    // Thread B â€” reader
    public void reader() {
        if (ready) {        // volatile read â€” establishes HB
                            // Rule 3: write of ready hbâ†’ this read
                            // Rule 8 (transitivity):
                            //   data=42 hbâ†’ ready=true hbâ†’ read of ready
                            //   THEREFORE: data=42 hbâ†’ read of data below
            System.out.println(data); // GUARANTEED to print 42
        }
    }
}
```

**The transitivity chain â€” this is the key insight:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     TRANSITIVITY IN ACTION                                                       â”‚
â”‚                                                                                                  â”‚
â”‚  Thread A:                          Thread B:                                                    â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€                          â”€â”€â”€â”€â”€â”€â”€â”€â”€                                                    â”‚
â”‚  data = 42   â”€â”€(Rule 1)â”€â”€â†’  ready=true â”€â”€(Rule 3)â”€â”€â†’  read ready â”€â”€(Rule 1)â”€â”€â†’  read data       â”‚
â”‚                                                                                                  â”‚
â”‚  Full chain:                                                                                     â”‚
â”‚  data=42  hbâ†’  ready=true  hbâ†’  read(ready)  hbâ†’  read(data)                                    â”‚
â”‚                                                                                                  â”‚
â”‚  By Rule 8 (transitivity):                                                                       â”‚
â”‚  data=42  hbâ†’  read(data)                                                                        â”‚
â”‚                                                                                                  â”‚
â”‚  Conclusion: Thread B's read of data MUST see 42                                                 â”‚
â”‚  This is NOT about timing â€” it's about the HB chain                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Example 2 â€” HB via synchronized (Rule 2):**

```java
public class HappensBeforeSynchronized {

    private int counter = 0;
    private final Object lock = new Object();

    // Thread A
    public void increment() {
        synchronized (lock) {
            counter++;
        }   // â† monitor UNLOCK here
            // Rule 2: this unlock hbâ†’ next lock of 'lock'
    }

    // Thread B
    public int read() {
        synchronized (lock) {   // â† monitor LOCK here
                                // sees everything written before unlock
            return counter;     // guaranteed to see latest value
        }
    }
}
```

**Example 3 â€” HB via Thread.start (Rule 4):**

```java
public class HappensBeforeThreadStart {

    private int config = 0;

    public void setup() {
        config = 42;            // write before start

        Thread t = new Thread(() -> {
            // Rule 4: Thread.start() hbâ†’ every action in this thread
            // config=42 hbâ†’ Thread.start() hbâ†’ this print
            System.out.println(config); // GUARANTEED to print 42
        });

        t.start();              // â† HB boundary: Rule 4
                                // everything before start()
                                // visible to new thread
    }
}
```

**Example 4 â€” HB via Thread.join (Rule 5):**

```java
public class HappensBeforeJoin {

    private int result = 0;

    public void compute() throws InterruptedException {
        Thread worker = new Thread(() -> {
            result = expensiveComputation(); // write in worker thread
        });                                  // Rule 5: all actions in
                                            // worker hbâ†’ join() returns

        worker.start();
        worker.join();          // â† HB boundary: Rule 5
                                // blocks until worker finishes
                                // worker's writes visible after join

        System.out.println(result); // GUARANTEED to see computed value
    }
}
```

**Example 5 â€” Data race â€” NO HB established:**

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
    // (0, 0) â†’ Thread B ran before Thread A
    // (1, 1) â†’ Thread B ran after Thread A
    // (0, 1) â†’ Thread B partially interleaved
    // (1, 0) â†’ ALSO POSSIBLE â€” CPU/compiler reordering!
    //          y=1 executed before x=1 in Thread A
    //          Thread B sees y=1 but x=0
    //          This is a DATA RACE â€” undefined by JMM
}
```

**Example 6 â€” Common mistake: HB doesn't mean atomicity:**

```java
public class HBNotAtomicity {
    private volatile int counter = 0;

    // Thread A and Thread B both call this
    public void increment() {
        counter++;  // looks atomic â€” IS NOT
        // expands to:
        // int temp = counter;  // volatile READ  â†’ HB established
        // temp = temp + 1;     // arithmetic
        // counter = temp;      // volatile WRITE â†’ HB established
        //
        // But READ and WRITE are TWO separate operations
        // Another thread can interleave between them
        // â†’ lost updates possible
        //
        // HB guarantees VISIBILITY not ATOMICITY
        // Fix: use AtomicInteger.incrementAndGet() â†’ CAS operation
    }
}
```

---

### ðŸ” HB Relationship Map â€” All Establishes

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    WHAT ESTABLISHES HAPPENS-BEFORE                                               â”‚
â”‚                                                                                                  â”‚
â”‚  Action                          â†’  Happens-Before  â†’  Action                                   â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                              â”‚
â”‚  Any action in thread            â†’                  â†’  Next action in same thread                â”‚
â”‚                                                                                                  â”‚
â”‚  volatile WRITE of field X       â†’                  â†’  volatile READ of field X                 â”‚
â”‚                                                                                                  â”‚
â”‚  synchronized UNLOCK of M        â†’                  â†’  synchronized LOCK of M                   â”‚
â”‚                                                                                                  â”‚
â”‚  Thread.start() call             â†’                  â†’  First action in new thread                â”‚
â”‚                                                                                                  â”‚
â”‚  Last action in thread T         â†’                  â†’  Thread.join(T) return                    â”‚
â”‚                                                                                                  â”‚
â”‚  Static initializer completes    â†’                  â†’  Any thread accessing the class            â”‚
â”‚                                                                                                  â”‚
â”‚  Constructor completes           â†’                  â†’  Finalizer starts                          â”‚
â”‚                                                                                                  â”‚
â”‚  Writing to final field          â†’                  â†’  Any read after constructor exit           â”‚
â”‚  in constructor                                                                                  â”‚
â”‚                                                                                                  â”‚
â”‚  Future.get() return             â†’                  â†’  Caller of get()                           â”‚
â”‚                                                                                                  â”‚
â”‚  CountDownLatch.countDown()      â†’                  â†’  CountDownLatch.await() return             â”‚
â”‚                                                                                                  â”‚
â”‚  CyclicBarrier.await() complete  â†’                  â†’  Actions after barrier in all threads      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"HB means A executes before B in time"|HB means **visibility** â€” B sees A's writes; timing is separate|
|"volatile guarantees atomicity"|volatile guarantees **visibility + ordering**; NOT atomicity|
|"synchronized is only about mutual exclusion"|synchronized ALSO establishes **HB** â€” visibility guarantee on entry/exit|
|"if A writes before B reads in wall time, B sees A's write"|FALSE â€” wall clock time means nothing without HB relationship|
|"HB is transitive automatically across all actions"|Only transitive **within an established chain** â€” gaps break it|
|"final fields need no synchronisation"|final fields have special JMM rule â€” HB from constructor to first read|

---

### ðŸ”¥ Pitfalls in Production

**1. Partial synchronisation â€” HB chain broken**

```java
// BROKEN â€” HB chain has a gap
public class BrokenChain {
    private int data = 0;
    private volatile boolean ready = false;

    public void writer() {
        data = 42;
        ready = true;   // volatile write â€” establishes HB âœ…
    }

    public void reader() {
        if (ready) {
            // data read is in HB chain âœ…
            System.out.println(data);
        }
    }

    // BUT:
    public void brokenReader() {
        boolean localReady = ready; // volatile read â†’ HB established
        // ... 50 lines of unrelated code ...
        // ... HB chain still holds â€” transitivity âœ…

        // BROKEN: reading ready again as non-volatile copy
        if (localReady) {
            System.out.println(data); // still safe â€” localReady
        }                             // captured from volatile read

        // ACTUALLY BROKEN PATTERN:
        boolean nonVolatileReady = ready; // volatile read âœ…
        // someone passes nonVolatileReady to another method
        // that method doesn't know about the HB chain
        // and reads data without any HB â†’ data race âŒ
    }
}
```

**2. HB and thread pools â€” invisible gaps**

```java
// DANGEROUS: submitting tasks to ExecutorService
ExecutorService pool = Executors.newFixedThreadPool(4);

int sharedData = 0;
sharedData = 42;            // write BEFORE submit

pool.submit(() -> {
    // Is sharedData=42 visible here?
    // YES â€” ExecutorService.submit() establishes HB âœ…
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
System.out.println(result[0]); // BROKEN â€” no HB from task completion
                                // to this read
                                // Fix: Future.get() establishes HB
Future<Integer> f = pool.submit(() -> compute());
System.out.println(f.get()); // âœ… Future.get() hbâ†’ caller
```

**3. Volatile on wrong variable â€” HB not established**

```java
// BROKEN â€” volatile on wrong field
public class WrongVolatile {
    private volatile int version = 0;  // volatile
    private int data = 0;              // NOT volatile

    public void update(int newData) {
        version++;      // volatile write â†’ HB established
        data = newData; // BUT: this write is AFTER volatile write
                        // HB only covers writes BEFORE volatile write
                        // data=newData is NOT in the HB chain âŒ
    }

    public int read() {
        int v = version; // volatile read
        return data;     // data write was AFTER volatile write
                         // not covered by HB â†’ may be stale âŒ
    }

    // FIX: write data BEFORE volatile write
    public void fixedUpdate(int newData) {
        data = newData; // write data first
        version++;      // volatile write AFTER â†’ data is in HB chain âœ…
    }
}
```

**4. Safe publication patterns**

```java
// BROKEN â€” unsafe publication (no HB from constructor to reader)
public class UnsafePublication {
    public int x;
    public int y;

    public UnsafePublication() {
        x = 1;
        y = 2;
    }
}

// Another thread may see partially constructed object:
// x=1, y=0 (default) â€” constructor not fully visible

// FIX 1: final fields (Rule: constructor hbâ†’ any read after)
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
// volatile write of reference â†’ HB established
// reader sees fully constructed object

// FIX 3: synchronized publication
synchronized (lock) {
    instance = new SafePublication();
}
// synchronized exit â†’ HB â†’ synchronized entry in reader
```

---

### ðŸ”— Related Keywords

- `Java Memory Model` â€” the specification that defines happens-before rules
- `Memory Barrier` â€” the physical CPU instruction that enforces HB
- `volatile` â€” establishes HB between write and subsequent read
- `synchronized` â€” establishes HB between unlock and subsequent lock
- `Thread.start` â€” establishes HB from pre-start code to new thread
- `Thread.join` â€” establishes HB from joined thread to caller
- `Data Race` â€” what happens when two accesses have no HB between them
- `Atomicity` â€” separate concept from HB; volatile gives visibility not atomicity
- `final` â€” special JMM rule: constructor completion hbâ†’ any field read
- `VarHandle` â€” fine-grained HB control with acquire/release semantics
- `CompletableFuture` â€” establishes HB between completion and thenApply()

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Formal JMM rule: if A hbâ†’ B, everything          â”‚
â”‚              â”‚ A wrote is guaranteed visible to B â€”             â”‚
â”‚              â”‚ the only safe foundation for concurrent code     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Reasoning about any cross-thread visibility:      â”‚
â”‚              â”‚ flags, shared state, object publication,         â”‚
â”‚              â”‚ result passing between threads                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't assume wall-clock ordering establishes      â”‚
â”‚              â”‚ HB â€” it doesn't. Don't confuse HB with           â”‚
â”‚              â”‚ atomicity â€” volatile is not enough for           â”‚
â”‚              â”‚ compound operations like counter++               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Happens-Before is Java's contract:              â”‚
â”‚              â”‚  establish the relationship and I guarantee      â”‚
â”‚              â”‚  visibility; skip it and you're on your own"     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Java Memory Model â†’ volatile â†’ synchronized â†’    â”‚
â”‚              â”‚ Data Race â†’ VarHandle â†’ AtomicInteger â†’          â”‚
â”‚              â”‚ CompletableFuture HB chain                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

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

Spring initialises beans single-threaded at startup, then serves requests on multiple threads. Is there a happens-before relationship between `@PostConstruct` completing and the first request thread calling `get()`? What guarantees this â€” or what could break it?

**Q2.** You have a producer-consumer system where the producer writes 10 fields to a shared object and then sets a `volatile boolean done = true`. The consumer spins on `done` and reads all 10 fields when it becomes true. This works correctly. Now your team refactors â€” they extract the 10 fields into a nested object and the producer sets `volatileDone = true` after constructing it. The consumer reads the nested object's fields after seeing `done = true`. Draw the complete happens-before chain and identify if the guarantee still holds â€” or where it breaks.

---

Next up: **016 â€” GC Roots** â€” the starting points of the garbage collector's reachability graph, what qualifies as a root, and why understanding them is essential for diagnosing memory leaks.

Shall I continue?
