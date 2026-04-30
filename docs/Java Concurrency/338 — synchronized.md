---
layout: default
title: "synchronized"
parent: "Java Concurrency"
nav_order: 338
permalink: /java-concurrency/synchronized/
---
# 338 — synchronized

`#java` `#concurrency` `#threading` `#locks` `#monitor`

⚡ TL;DR — `synchronized` is Java's built-in mutual exclusion mechanism — it ensures only one thread at a time executes a block of code by acquiring an object's monitor lock, establishing both atomicity and happens-before visibility.

| #338 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, Thread Lifecycle, Java Memory Model, Monitor | |
| **Used by:** | Deadlock, Race Condition, ReentrantLock, volatile | |

---

### 📘 Textbook Definition

`synchronized` is a keyword that locks an object's **monitor** before executing a block or method. While one thread holds a monitor, any other thread attempting to acquire the same monitor enters the BLOCKED state. Upon exit (normally or via exception), the monitor is released. `synchronized` provides: **mutual exclusion** (only one thread in the block at a time) and **visibility** (all writes by the exiting thread are visible to the next thread that acquires the same monitor — happens-before guarantee).

---

### 🟢 Simple Definition (Easy)

`synchronized` is a "do not disturb" sign on a door. Only one thread can be inside at a time. Other threads wait (BLOCKED) outside. When the first thread leaves, the next one can enter. This prevents two threads from interfering with each other when reading and writing shared data.

---

### 🔵 Simple Definition (Elaborated)

Every Java object has an internal lock called a **monitor**. `synchronized` on a method or block acquires (locks) that monitor before executing. If another thread already holds the monitor, the newcomer blocks. Three key benefits: (1) mutual exclusion — no two threads can be in the same synchronized region simultaneously; (2) visibility — changes made inside a synchronized block are guaranteed visible to the next thread that acquires the same lock; (3) reentrance — a thread that already holds a lock can re-enter synchronized blocks using the same lock without deadlocking itself.

---

### 🔩 First Principles Explanation

**The race condition problem:**

```
Thread A and Thread B both run: counter++
counter++ compiles to three steps:
   1. READ:  load counter from memory
   2. ADD:   compute counter + 1
   3. WRITE: store back to memory

Interleaved execution can break things:
   T-A: READ  counter = 0
   T-B: READ  counter = 0   (sees old value!)
   T-A: ADD   result = 1
   T-B: ADD   result = 1
   T-A: WRITE counter = 1
   T-B: WRITE counter = 1   (overwrites T-A's result!)
   Final counter = 1  (expected 2! One increment lost)
```

**The solution — mutual exclusion:**

```
synchronized keyword acquires monitor BEFORE execution:

   synchronized(this) {
       counter++;   // only one thread executes this at a time
   }

   T-A: ACQUIRE lock  ← T-B must WAIT here
   T-A: READ counter = 0
   T-A: ADD  result = 1
   T-A: WRITE counter = 1
   T-A: RELEASE lock  ← T-B can now enter
   T-B: ACQUIRE lock
   T-B: READ counter = 1   (sees T-A's write!)
   T-B: WRITE counter = 2
   T-B: RELEASE lock
   Final counter = 2  ✓ correct!
```

---

### ❓ Why Does This Exist — Why Before What

```
Without synchronized:
  ✗ Counter increments lost (race conditions)
  ✗ Visibility: CPU caches may hold stale values
  ✗ Reordering: JVM/CPU reorders instructions; other threads see nonsensical states

With synchronized:
  ✅ Mutual exclusion: one thread at a time in critical section
  ✅ Happens-before: all writes before lock release visible after lock acquire
  ✅ Reentrance: same thread can acquire same lock multiple times
  ✅ Built-in: no external libraries needed
```

---

### 🧠 Mental Model / Analogy

> `synchronized` is a **single-key bathroom**. There's one lock, one key. The person inside (thread) holds the key. Anyone else who tries to enter waits at the door (BLOCKED). When the person leaves, they hang the key back, and the next person grabs it. The key also guarantees: when you walk in, everything the previous person left (wrote) is exactly as they left it — nothing is hidden in their pockets.

---

### ⚙️ How It Works

```
Two forms:

1. Synchronized method — locks 'this' (for instance methods)
                       — locks the Class object (for static methods)
   public synchronized void increment() { counter++; }

2. Synchronized block — explicit lock object
   private final Object lock = new Object();
   synchronized (lock) { counter++; }

   // Prefer blocks: finer granularity, explicit lock object

Monitor internals:
   Every Java object has a mark word in its header
   When locked: mark word encodes the owning thread
   Uncontended lock: biased/thin lock (cheap — no OS involvement)
   Contended lock: inflated to heavyweight mutex (OS involvement)
   → Biased/thin → fair contention → heavyweight
```

---

### 🔄 How It Connects

```
synchronized
  │
  ├─ Provides ──→ Mutual exclusion + happens-before visibility
  ├─ Causes   ──→ BLOCKED state in waiting threads
  ├─ Enables  ──→ wait() / notify() (must own monitor to call)
  ├─ vs       ──→ volatile (visibility only, no mutex)
  ├─ vs       ──→ ReentrantLock (same semantics + tryLock/fairness)
  ├─ vs       ──→ Atomic variables (lock-free, single ops only)
  └─ Misuse   ──→ Deadlock (two threads each holding one lock, waiting for the other)
```

---

### 💻 Code Example

```java
// Thread-safe counter using synchronized method
public class Counter {
    private int count = 0;

    public synchronized void increment() { count++; } // locks 'this'
    public synchronized void decrement() { count--; }
    public synchronized int  get()       { return count; }
}
```

```java
// Synchronized block — finer granularity, explicit lock object
public class BankAccount {
    private final Object balanceLock = new Object();
    private double balance;

    public void deposit(double amount) {
        synchronized (balanceLock) { // only locks for balance operations
            balance += amount;
        }
        // other methods can run concurrently if they don't touch balance
    }

    public void withdraw(double amount) {
        synchronized (balanceLock) {
            if (balance >= amount) balance -= amount;
            else throw new IllegalStateException("Insufficient funds");
        }
    }
}
```

```java
// Static synchronized method — locks Class object, not instance
public class IdGenerator {
    private static long nextId = 0;

    public static synchronized long generate() { // locks IdGenerator.class
        return ++nextId;
    }
}
// Warning: static lock prevents ALL instances from running concurrently
```

```java
// Reentrancy — same thread can acquire same lock multiple times
public class ReentrantExample {
    public synchronized void outer() {
        System.out.println("outer");
        inner(); // calls synchronized method on same 'this' — NOT deadlock!
    }

    public synchronized void inner() {
        System.out.println("inner"); // same thread re-enters its own lock
    }
}
// Java monitors are reentrant — lock count tracked per thread
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| synchronized on different objects provides mutual exclusion | Only threads locking the *same* object are mutually exclusive |
| synchronized protects the variable, not the code | It protects the *code block* — any field access inside must consistently use same lock |
| volatile + synchronized are interchangeable | volatile: visibility only; synchronized: visibility + atomicity |
| synchronized methods lock the class | Instance methods lock `this`; only `static synchronized` locks the class object |
| Try/catch inside synchronized is safe | Exception still exits the block and releases the lock — no deadlock |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Locking on different objects — no mutual exclusion**

```java
// Bug: two instances → two different locks → no protection
public class BadCounter {
    public synchronized void increment() { count++; } // locks THIS instance
}
BadCounter a = new BadCounter();
BadCounter b = new BadCounter();
// a.increment() and b.increment() run concurrently — different locks!

// Fix: use a shared lock object, or use a single shared instance
```

**Pitfall 2: Holding lock too long — reduces concurrency**

```java
// Bad: entire method synchronized — holds lock during slow I/O
public synchronized String fetchAndProcess(String url) {
    String data = httpClient.get(url);  // holds lock for 200ms!
    return process(data);
}

// Fix: minimize lock scope
public String fetchAndProcess(String url) {
    String data = httpClient.get(url);  // runs without lock
    synchronized (this) {
        return process(data);           // only critical section locked
    }
}
```

**Pitfall 3: Not using consistent lock across all access points**

```java
// Bug: read is unsynchronized — can see stale/partial data
private int count = 0;
public synchronized void increment() { count++; }
public int get() { return count; }  // ❌ not synchronized — stale read

// Fix: synchronize both reads and writes on same lock
public synchronized int get() { return count; }
```

---

### 🔗 Related Keywords

- **[Thread Lifecycle](./068 — Thread Lifecycle.md)** — synchronized causes BLOCKED state
- **[Deadlock](./071 — Deadlock.md)** — two synchronized blocks waiting for each other
- **[volatile](./070 — volatile.md)** — visibility without mutual exclusion
- **[ReentrantLock](./076 — ReentrantLock.md)** — explicit lock with same semantics + tryLock
- **[Race Condition](./072 — Race Condition.md)** — what synchronized prevents
- **Java Memory Model** — happens-before guarantee from synchronized

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Acquire object monitor → mutual exclusion +   │
│              │ happens-before visibility; reentrant by design│
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Multiple threads read/write shared mutable    │
│              │ state; compound check-then-act operations     │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Read-only data (no sync needed); single-field │
│              │ visibility only (use volatile); performance-  │
│              │ critical paths (use Atomic or StampedLock)    │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "One thread in, everyone else blocks —        │
│              │  and what the last thread wrote, you'll see"  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ volatile → ReentrantLock → Deadlock →         │
│              │ Atomic Variables → Java Memory Model          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Thread A holds lock on object X and is waiting to acquire lock on object Y. Thread B holds lock on object Y and is waiting to acquire lock on object X. What state are both threads in, and what is this called? How would you detect this from a thread dump?

**Q2.** Inside a `synchronized` instance method, you call `Thread.sleep(5000)`. Does this release the lock while the thread sleeps? What about calling `obj.wait(5000)`?

**Q3.** What is the difference between using `synchronized(this)` and `synchronized(SomeClass.class)` in an instance method? When would each be appropriate?

