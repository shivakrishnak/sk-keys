---
layout: default
title: "volatile"
parent: "Java Concurrency"
nav_order: 70
permalink: /java-concurrency/volatile/
---
# 070 — volatile

`#java` `#concurrency` `#memory-model` `#visibility`

⚡ TL;DR — `volatile` guarantees that writes to a field are immediately visible to all other threads (no CPU cache staleness), and establishes a happens-before relationship — but it does NOT provide atomicity for compound operations like `i++`.

| #070 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, Java Memory Model, CPU Caches, Happens-Before | |
| **Used by:** | synchronized, Atomic Variables, Race Condition, Double-Checked Locking | |

---

### 📘 Textbook Definition

The `volatile` keyword on a field instructs the JVM to: (1) always read the field directly from main memory, never from a thread-local CPU cache; (2) always write the field back to main memory immediately; (3) establish a **happens-before** relationship — a write to a volatile field happens-before every subsequent read of that field. It prevents instruction reordering around the volatile access but does NOT provide mutual exclusion or atomicity for compound read-modify-write operations.

---

### 🟢 Simple Definition (Easy)

Without `volatile`, each thread may work from its own cached copy of a variable — like two people working from different photocopies of a document. `volatile` says: "There's only ONE copy. Every read goes to the source. Every write goes straight back." No stale cached values.

---

### 🔵 Simple Definition (Elaborated)

Modern CPUs have multiple levels of cache (L1, L2, L3). When a thread writes a variable, it may stay in the CPU cache for a while before being flushed to main memory. Other threads reading the same variable may see the stale cached version. `volatile` bypasses this by forcing all reads and writes directly through main memory, and inserting memory barriers that prevent the compiler and CPU from reordering instructions around the access. The limitation: it only guarantees single-field visibility, not multi-step atomicity — `volatile int i; i++` is still a race condition because read-increment-write are three steps.

---

### 🔩 First Principles Explanation

**Why CPU caches cause visibility problems:**

```
Multi-core CPU layout:

Core 1                    Core 2
┌──────────┐              ┌──────────┐
│ L1 Cache │              │ L1 Cache │
│ flag = 0 │  (stale!)    │ flag = 1 │  (written by Core 2)
└────┬─────┘              └────┬─────┘
     │                         │
     └──────────┬──────────────┘
                │
         Main Memory
         flag = 1  (Core 2 wrote here)

Thread on Core 1 reads flag → gets 0 from L1 cache
Thread on Core 2 wrote flag = 1 → sits in L2, not yet visible to Core 1

Result: Thread 1 never sees the update → infinite loop / wrong logic
```

**What volatile does:**

```
volatile boolean flag;

Write (Core 2):
  flag = true;
  → Memory barrier inserted
  → Value flushed to main memory immediately
  → All caches invalidated for this address

Read (Core 1):
  while (!flag) { ... }
  → Memory barrier before read
  → Must load from main memory (bypasses stale cache)
  → Sees: flag = true → exits loop ✓
```

**What volatile does NOT do:**

```
volatile int counter = 0;

Thread A: counter++    expands to:
  1. READ  counter from memory (= 0)
  2. ADD   0 + 1 = 1   ← no barrier here, not atomic
  3. WRITE 1 to memory

Thread B: counter++
  1. READ  counter from memory (also = 0, before A's write)
  2. ADD   0 + 1 = 1
  3. WRITE 1 to memory

Result: counter = 1, not 2 — same race condition as without volatile
For atomicity use: AtomicInteger.incrementAndGet()
```

---

### ❓ Why Does This Exist — Why Before What

```
Without volatile (on modern JVMs with JIT + CPU reordering):
  ✗ Thread reads stale cached value forever
  ✗ JIT may hoist loop variable out of loop (optimises away re-read)
  ✗ Instructions may be reordered across thread boundaries
  ✗ Singleton double-checked locking breaks (partially constructed object)

With volatile:
  ✅ Guaranteed fresh read from main memory
  ✅ Prevents compiler/CPU reordering around the access
  ✅ Happens-before: writer's actions visible to reader after volatile read
  ✅ Lightweight — no mutex, no blocking, no OS involvement
  ✅ Sufficient when: one writer, many readers, no compound operations
```

---

### 🧠 Mental Model / Analogy

> `volatile` is like a **whiteboard in a shared office** vs sheets of paper on individual desks. Without volatile: each thread has its own scrap paper — they may not notice when someone else changes the value on their paper. With volatile: everyone looks at the same whiteboard — when someone writes, everyone sees it immediately. But the whiteboard doesn't prevent two people writing at the same time (for that, you still need a turn-taking rule — i.e., synchronization).

---

### ⚙️ How It Works

```
JVM memory model guarantees for volatile:

1. VISIBILITY:
   Write to volatile → flush to main memory immediately
   Read of volatile  → load from main memory (not cache)

2. HAPPENS-BEFORE:
   All actions before volatile write
   happens-before volatile write
   happens-before volatile read
   happens-before all actions after volatile read

3. ORDERING (memory barriers):
   StoreStore barrier before volatile write
   StoreLoad  barrier after  volatile write
   LoadLoad   barrier before volatile read
   LoadStore  barrier after  volatile read
   → Prevents JIT/CPU from reordering around the access

What volatile does NOT provide:
   ✗ Atomicity for compound ops (i++, check-then-act)
   ✗ Mutual exclusion (multiple threads can be in same code simultaneously)
   ✗ Protection for multi-variable invariants
```

---

### 🔄 How It Connects

```
volatile
  │
  ├─ Provides ──→ Visibility + happens-before (not atomicity)
  ├─ vs       ──→ synchronized (visibility + atomicity + mutex)
  ├─ vs       ──→ AtomicInteger (visibility + CAS atomicity, lock-free)
  │
  ├─ USE CASE: flag variables (shutdown signals, state changes)
  ├─ USE CASE: double-checked locking singleton (Java 5+)
  └─ MISUSE  ──→ volatile counter++ is still a race condition
```

---

### 💻 Code Example

```java
// Classic use: shutdown flag
public class Worker implements Runnable {
    private volatile boolean running = true;  // volatile: thread sees update

    @Override
    public void run() {
        while (running) {  // reads fresh value on every iteration
            doWork();
        }
        System.out.println("Worker stopped cleanly");
    }

    public void stop() {
        running = false;  // write visible to worker thread immediately
    }
}
// Without volatile: JIT might optimise while(running) to while(true)
// because it never sees running change from within the thread
```

```java
// Double-checked locking singleton (requires volatile — Java 5+)
public class Singleton {
    private static volatile Singleton instance;  // volatile is REQUIRED

    public static Singleton getInstance() {
        if (instance == null) {                  // first check (no lock)
            synchronized (Singleton.class) {
                if (instance == null) {          // second check (with lock)
                    instance = new Singleton();  // volatile prevents partial construction
                }
            }
        }
        return instance;
    }
}
// Without volatile: another thread may see partially constructed Singleton
// (constructor not finished, but reference already assigned — reordering!)
// volatile prevents: assignment being visible before constructor completes
```

```java
// Demonstrating what volatile does NOT fix: counter++ race
public class VolatileCounter {
    private volatile int count = 0;

    public void increment() {
        count++;   // ❌ NOT atomic: read-increment-write = 3 steps
    }

    // Fix 1: synchronized
    public synchronized void safeIncrement() { count++; }

    // Fix 2: AtomicInteger (lock-free, preferred)
    private AtomicInteger atomicCount = new AtomicInteger(0);
    public void atomicIncrement() { atomicCount.incrementAndGet(); }
}
```

```java
// Volatile for status flag in producer/consumer
public class DataProcessor {
    private volatile boolean dataReady = false;
    private int data;  // written before volatile write → visible after volatile read

    public void produce(int value) {
        this.data = value;         // happens-before the volatile write
        this.dataReady = true;     // volatile write — flushes data too
    }

    public void consume() {
        while (!dataReady) { }     // volatile read — establishes happens-before
        process(this.data);        // safely visible due to happens-before chain
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `volatile` makes operations atomic | Only single read/write is atomic; `i++` is still three non-atomic steps |
| Without `volatile`, JVM always reads from main memory | JVM spec permits (and JIT exploits) caching — `volatile` forces main memory |
| `volatile` is the same as `synchronized` | `synchronized` also provides mutual exclusion; `volatile` does not |
| `volatile` is only needed for multi-core systems | JIT optimizations (loop hoisting, reordering) affect even single-core scenarios |
| Any `final` field is automatically volatile | `final` prevents reassignment; it doesn't provide happens-before for mutable state inside the referenced object |

---

### 🔥 Pitfalls in Production

**Pitfall 1: volatile counter (false safety)**

```java
private volatile int requests = 0;

// Multiple threads call this:
public void handleRequest() {
    requests++;   // ❌ read-modify-write is NOT atomic
}
// Fix: AtomicInteger or synchronized
private final AtomicInteger requests = new AtomicInteger(0);
public void handleRequest() { requests.incrementAndGet(); }
```

**Pitfall 2: Volatile on multi-variable invariant**

```java
private volatile int min = 0;
private volatile int max = 100;

// Thread A: set new range
min = 50;    // write 1
max = 200;   // write 2

// Thread B: read range (may see min=50, max=100 between the two writes!)
if (value >= min && value <= max) { ... }
// volatile doesn't atomically update both fields
// Fix: synchronized block to update both together
```

**Pitfall 3: Missing volatile in double-checked locking**

```java
// Without volatile — broken on Java 5+ JIT:
private static Singleton instance;  // ❌ missing volatile

// Thread may see non-null reference but uninitialized object fields
// because JIT can reorder: allocate → assign reference → run constructor
// Fix: always use volatile for DCL pattern
private static volatile Singleton instance;  // ✅
```

---

### 🔗 Related Keywords

- **[synchronized](./069 — synchronized.md)** — provides visibility + atomicity + mutex
- **[Happens-Before](../Java/015 — Happens-Before.md)** — the formal memory ordering guarantee
- **[Atomic Variables](./077 — Atomic Variables.md)** — volatile + CAS for lock-free compound ops
- **[Race Condition](./072 — Race Condition.md)** — what volatile alone cannot fully prevent
- **[Memory Barrier](../Java/014 — Memory Barrier.md)** — the hardware mechanism volatile uses

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Force read/write through main memory;         │
│              │ happens-before guarantee; no atomicity        │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ One writer, many readers; simple flag/state;  │
│              │ double-checked locking singleton              │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Compound operations (i++, check-then-act,     │
│              │ multi-variable invariants) — use synchronized │
│              │ or AtomicInteger instead                      │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "volatile = everyone sees the same whiteboard;│
│              │  but two people can still write at once"      │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Happens-Before → Memory Barrier →             │
│              │ Atomic Variables → synchronized → JMM         │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have `volatile boolean ready` and a non-volatile `int data`. Thread A writes `data = 42` then `ready = true`. Thread B reads `ready` then reads `data`. Is `data = 42` guaranteed visible to Thread B? Why? What happens-before chain makes this safe?

**Q2.** Can `volatile` replace `synchronized` for a simple flag that is only ever written by ONE thread and read by many? What are the trade-offs?

**Q3.** Why does double-checked locking require `volatile` even though the second check is inside `synchronized`? What specific reordering is prevented by the `volatile` declaration?

