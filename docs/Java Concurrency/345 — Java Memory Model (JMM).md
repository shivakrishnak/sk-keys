---
layout: default
title: "Java Memory Model"
parent: "Java Concurrency"
nav_order: 345
permalink: /java-concurrency/java-memory-model/
number: "345"
category: Java Concurrency
difficulty: ★★★
depends_on: volatile, synchronized, Happens-Before, Memory Barrier
used_by: All Concurrency Features, JIT Compiler, CPU Reordering
tags: #java, #concurrency, #jmm, #memory-model, #advanced
---

# 345 — Java Memory Model (JMM)

`#java` `#concurrency` `#jmm` `#memory-model` `#advanced`

⚡ TL;DR — The Java Memory Model defines the rules under which one thread's writes are visible to another thread's reads — it specifies happens-before relationships established by synchronized, volatile, final, and thread start/join.

| #345 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | volatile, synchronized, Happens-Before, Memory Barrier | |
| **Used by:** | All Concurrency Features, JIT Compiler, CPU Reordering | |

---

### 📘 Textbook Definition

The **Java Memory Model** (JMM), specified in §17 of the Java Language Specification, defines a formal memory consistency model for Java programs. It allows compilers and CPUs to reorder instructions and cache values — optimisations that improve single-threaded performance. To constrain these optimisations, the JMM establishes **happens-before** (hb) relationships: if action A happens-before action B, then all effects of A are visible to B. Key hb sources: monitor unlock→next lock, volatile write→next volatile read, thread.start()→first action in new thread, thread action→thread.join() return.

---

### 🟢 Simple Definition (Easy)

Modern CPUs and JIT compilers reorder operations and cache values to go faster. This is great for single-threaded code but dangerous for multithreaded code. The JMM is a contract: "Here are the specific cases where I (JVM) GUARANTEE that what one thread wrote IS visible to another thread." If you follow these rules, your concurrent code is correct anywhere Java runs.

---

### 🔵 Simple Definition (Elaborated)

The JMM doesn't describe hardware cache behaviour directly — it describes guarantees that hold regardless of the underlying CPU architecture. A Java program using `volatile`, `synchronized`, or `final` correctly gets strong visibility guarantees. A program that doesn't use synchronization correctly has **data races** — and the JMM permits arbitrary behaviour for racy programs (like C/C++ undefined behaviour). Understanding JMM is what separates "code that works on my machine" from "code that works on all JVMs."

---

### 🔩 First Principles Explanation

```
Why we need JMM:

CPU optimisations that break naive concurrent code:
  1. Store buffers: CPU writes to local buffer before main memory
     → Another CPU reads stale value from memory
  2. Instruction reordering: CPU/JIT reorders independent instructions
     → Thread A sees instructions happen in different order
  3. Register caching: JIT hoists variable into register for inner loop
     → Thread A's loop never re-reads variable from memory

Without JMM guarantees → program outcomes are non-deterministic

The JMM solution: happens-before relationships

    if A happens-before B:
      ALL actions of A are guaranteed visible to B
      B cannot be moved before A in observed ordering

Happens-before is TRANSITIVE:
  A hb B  AND  B hb C  →  A hb C
```

**Complete happens-before rules (JMM):**

```
1. Program order:      Within single thread, each action hb next action
2. Monitor lock:       UNLOCK of monitor hb LOCK of same monitor
3. volatile:           WRITE to volatile hb READ of same volatile
4. Thread start:       thread.start() hb first action in started thread
5. Thread join:        last action in thread hb thread.join() return
6. Object init:        write to final fields in constructor hb reader of object
                       (safe publication of immutable objects)
7. Transitivity:       A hb B AND B hb C → A hb C
```

---

### 🧠 Mental Model / Analogy

> The JMM is the **contract between developer and JVM**. The developer says: "I will use synchronized/volatile/final correctly." The JVM says: "I will ensure your visibility guarantees hold, even though I'm reordering and caching aggressively for performance." Without this contract, you'd need to know x86 vs ARM vs SPARC memory models — the JMM abstracts all of that into Java-level guarantees.

---

### ⚙️ How It Works

```
Data race (JMM violation):
  Two threads access the same variable without hapens-before relationship
  At least one is a write
  Result: undefined behaviour — JMM allows any outcome

Data race free (DRF):
  All shared variable accesses ordered by happens-before
  Result: sequentially consistent behaviour (programs behave as if
          operations happened in a single global order)

Safe publication:
  Object created in Thread A, used in Thread B
  Without synchronization: B may see partially constructed object
  
  Safe publication mechanisms:
  1. Static initialiser (class loader)
  2. volatile field
  3. synchronized block on same monitor
  4. final fields (JMM final field semantics)
  5. AtomicReference.set()

  Unsafe publication:
  Object reference = new Object();   // Thread A assigns
  // Thread B reads reference → may see uninitialized object fields!
  // Object field writes may not be visible (no happens-before)
```

---

### 🔄 How It Connects

```
Java Memory Model
  │
  ├─ Defines rules for ──→ volatile, synchronized, final, thread ops
  ├─ Permits            ──→ instruction reordering (within hb bounds)
  ├─ Foundation for     ──→ all java.util.concurrent correctness proofs
  ├─ Prevents data races → if all accesses have hb chain
  └─ Specified in       ──→ JLS §17 (formal axioms)
```

---

### 💻 Code Example

```java
// JMM violation: unsynchronized access — data race
class Race {
    int x = 0;
    boolean ready = false;

    void writer() {
        x = 42;
        ready = true;        // no volatile, no sync — may be reordered!
    }
    void reader() {
        while (!ready) {}    // may spin forever (JIT hoists ready into register)
        System.out.println(x); // may print 0! (x write not visible)
    }
}
```

```java
// JMM fixed: volatile establishes happens-before
class Fixed {
    int x = 0;
    volatile boolean ready = false;

    void writer() {
        x = 42;
        ready = true;        // volatile write: hb the volatile read
    }
    void reader() {
        while (!ready) {}    // volatile read: sees ready=true eventually
        System.out.println(x); // x=42 guaranteed visible (hb from volatile)
    }
    // Reason: x=42 write (program order) hb volatile write (program order)
    //         volatile write hb volatile read (JMM volatile rule)
    //         ∴ x=42 is visible after volatile read
}
```

```java
// Safe publication: final fields
class ImmutablePoint {
    final int x;
    final int y;
    ImmutablePoint(int x, int y) { this.x = x; this.y = y; }
}
// Reading final fields: JMM guarantees constructor writes visible
// to any reader — even without synchronization
// (provided reference is safely published)
ImmutablePoint p = new ImmutablePoint(3, 4); // safe if 'p' published safely
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| JMM is only relevant for low-level code | JMM affects any class with shared mutable fields — even ordinary field reads |
| Volatile guarantees atomicity for compound ops | Only visibility + ordering — `volatile int i; i++` is still a race condition |
| `synchronized` makes the whole program sequential | Only synchronizes actions on the SAME monitor — different monitors are unordered |
| `final` fields are immutable forever | `final` prevents reassignment; the object the final field points to CAN be mutable |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Double-checked locking without volatile**

```java
// Without volatile: JIT may publish partially constructed object
private static Singleton instance;   // ❌ missing volatile
if (instance == null) {
    synchronized (Singleton.class) {
        if (instance == null) instance = new Singleton(); // may be visible before constructor finishes
    }
}
// Fix: volatile instance ensures constructor completes before reference is visible
private static volatile Singleton instance;  // ✅
```

**Pitfall 2: Relying on thread creation time as synchronization**

```java
int x = 0;
Thread t = new Thread(() -> System.out.println(x)); // reads x
x = 42;  // written BEFORE t.start()
t.start(); // t.start() hb first action in t
// x = 42 IS visible — thread.start() establishes hb
// BUT if x=42 were written AFTER t.start(): NOT guaranteed visible!
```

---

### 🔗 Related Keywords

- **[Happens-Before](../Java/015 — Happens-Before.md)** — the core ordering relation
- **[volatile](./070 — volatile.md)** — establishes hb between write and read
- **[synchronized](./069 — synchronized.md)** — unlock establishes hb with next lock
- **[Memory Barrier](../Java/014 — Memory Barrier.md)** — hardware mechanism JMM relies on
- **[Race Condition](./072 — Race Condition.md)** — result of JMM violations (data races)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Formal rules for inter-thread visibility;     │
│              │ happens-before pairs define safe sharing      │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Understanding WHY volatile/sync work; proving │
│              │ your concurrent code is correct              │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Never write concurrent code WITHOUT hb chain  │
│              │ between shared accesses — that's a data race  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Without a happens-before chain, writes       │
│              │  are invisible — anything goes"              │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Happens-Before → Memory Barrier → volatile →  │
│              │ Safe Publication → final fields              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Thread A writes `data = 42` and then starts Thread B via `t.start()`. Thread B reads `data`. Is this safe without volatile or synchronized? Identify the precise happens-before chain that makes this correct.

**Q2.** Can happens-before be violated by the JIT compiler optimising away a loop variable check? Give a concrete example where JIT hoisting causes a visibility bug in the absence of volatile.

**Q3.** The JMM allows "relaxed" writes and reads that can be reordered. Why is this performance-critical? What would the performance cost be if every write had to be immediately visible to every other CPU?

