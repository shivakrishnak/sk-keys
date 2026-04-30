---
layout: default
title: "CAS (Compare-And-Swap)"
parent: "Java Concurrency"
nav_order: 104
permalink: /java-concurrency/cas-compare-and-swap/
number: "104"
category: Java Concurrency
difficulty: ★★★
depends_on: Atomic Classes, Volatile, Java Memory Model, CPU Hardware
used_by: AtomicInteger, AtomicReference, ConcurrentHashMap, Lock-Free Data Structures
tags: #java, #concurrency, #lock-free, #cas, #atomic, #hardware
---

# 104 — CAS (Compare-And-Swap)

`#java` `#concurrency` `#lock-free` `#cas` `#atomic` `#hardware`

⚡ TL;DR — CAS is a single atomic CPU instruction: "if memory location holds expected value, swap it with new value; otherwise fail" — the hardware primitive that makes lock-free programming possible.

| #104 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Atomic Classes, Volatile, Java Memory Model, CPU Hardware | |
| **Used by:** | AtomicInteger, AtomicReference, ConcurrentHashMap, Lock-Free Data Structures | |

---

### 📘 Textbook Definition

**Compare-And-Swap (CAS)** is an atomic hardware instruction (`CMPXCHG` on x86, `LL/SC` on ARM) that performs: "if the value at address `A` equals `expected`, write `new` to `A` and return true; otherwise, do nothing and return false" — as one uninterruptible operation. In Java, CAS is exposed via `sun.misc.Unsafe` internally and via the `java.util.concurrent.atomic` package (e.g., `AtomicInteger.compareAndSet(expected, update)`). It is the hardware building block for lock-free algorithms.

---

### 🟢 Simple Definition (Easy)

CAS is like a conditional swap with a check: "Only change this value to the new one if it's still what I expect. If someone else changed it first, tell me so I can try again." It happens atomically — the CPU guarantees no other thread can interfere between the check and the swap.

---

### 🔵 Simple Definition (Elaborated)

Traditional locking says "stop everyone else while I change this value." CAS says "let everyone read freely; when I want to update, I verify the value hasn't changed since I read it, then swap in one atomic step." If the swap fails (someone else updated it first), I just re-read and retry — no blocking, no OS involvement. This makes CAS far cheaper than a mutex for low-contention scenarios.

---

### 🔩 First Principles Explanation

**The atomic update problem:**

```
Thread 1: read counter=5, compute 5+1=6
Thread 2: read counter=5, compute 5+1=6  ← both read before either writes
Thread 1: write counter=6
Thread 2: write counter=6               ← LOST UPDATE: should be 7

Fix with CAS:
Thread 1: CAS(addr, expected=5, new=6)  → success → counter=6
Thread 2: CAS(addr, expected=5, new=6)  → FAIL (value is now 6, not 5)
Thread 2: re-read counter=6, retry CAS(addr, expected=6, new=7) → success
Result: counter=7 ✓
```

**The hardware guarantee:**

```
CPU-level (x86):
  LOCK CMPXCHG [mem], reg
  ↑ LOCK prefix: acquires bus lock or uses cache-coherency protocol
    ensuring no other CPU can access [mem] between compare and swap

This is fundamentally different from:
  read(mem)    ← another CPU can write here
  if == expected:
    write(mem) ← race condition!
```

**CAS loop pattern (spin loop):**

```java
// Generic CAS retry loop
do {
    int current = atomicRef.get();       // read current value
    int next = compute(current);         // compute desired new value
} while (!atomicRef.compareAndSet(current, next));  // retry if CAS fails
```

---

### ❓ Why Does This Exist — Why Before What

Without CAS, all concurrent updates require a mutex. A mutex involves a kernel syscall to block/unblock threads, context switches, and scheduler involvement. For simple operations like incrementing a counter, this overhead dominates. CAS stays entirely in user space, typically completing in ~10ns vs ~1µs for a mutex — 100× faster in the uncontended case.

---

### 🧠 Mental Model / Analogy

> CAS is like an **optimistic edit** on a shared Google Doc. You read the document, make your change locally, then say "apply my edit only if the document still looks like it did when I read it (same version number)." If someone else edited it first, you get a conflict notification — you re-read and retry. No one is "locked out" while you're thinking; conflicts are just retried.

---

### ⚙️ How It Works — CAS in Java

```
java.util.concurrent.atomic package uses CAS internally:

AtomicInteger.incrementAndGet():
  internally does:
    do {
      int current = get();          // volatile read
      int next = current + 1;
    } while (!compareAndSet(current, next));  // hardware CAS
    return next;

Under the hood (simplified):
  Unsafe.compareAndSwapInt(object, offset, expected, update)
  → translates to: LOCK CMPXCHG instruction on x86
```

```
CAS outcomes:
  ┌───────────────┬──────────────────────────────────────┐
  │ CAS succeeds  │ Memory = expected → written to new   │
  │               │ Returns true                          │
  ├───────────────┼──────────────────────────────────────┤
  │ CAS fails     │ Memory ≠ expected → no write         │
  │               │ Returns false → caller retries        │
  └───────────────┴──────────────────────────────────────┘
```

---

### 💻 Code Example

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

// 1. AtomicInteger — simplest CAS use
AtomicInteger counter = new AtomicInteger(0);

// Increment atomically using CAS internally
int newVal = counter.incrementAndGet();  // thread-safe, no lock

// Manual CAS — only update if still 5
boolean succeeded = counter.compareAndSet(5, 6);
System.out.println("CAS succeeded: " + succeeded);

// 2. Implement your own lock-free stack using CAS
public class LockFreeStack<T> {
    private final AtomicReference<Node<T>> top = new AtomicReference<>();

    public void push(T value) {
        Node<T> newNode = new Node<>(value);
        Node<T> current;
        do {
            current = top.get();        // read current top
            newNode.next = current;     // new node points to current top
        } while (!top.compareAndSet(current, newNode));  // retry if top changed
    }

    public T pop() {
        Node<T> current;
        do {
            current = top.get();
            if (current == null) return null;  // empty stack
        } while (!top.compareAndSet(current, current.next));  // retry if top changed
        return current.value;
    }

    private static class Node<T> { T value; Node<T> next; Node(T v) { value = v; } }
}
```

```java
// 3. ABA Problem demo and fix
AtomicReference<String> ref = new AtomicReference<>("A");

// Thread 1 reads "A", plans to swap to "C"
String snapshot = ref.get(); // = "A"

// Thread 2 changes A → B → A (ABA)
ref.set("B");
ref.set("A");

// Thread 1: CAS succeeds even though the world changed!
ref.compareAndSet(snapshot, "C"); // ← succeeds (value is "A"), but is this right?

// Fix: use AtomicStampedReference (adds a version counter)
AtomicStampedReference<String> stamped = new AtomicStampedReference<>("A", 0);
int[] stampHolder = new int[1];
String current = stamped.get(stampHolder);     // reads value AND stamp
int currentStamp = stampHolder[0];
// Only succeeds if BOTH value AND stamp match — ABA detected by stamp change
stamped.compareAndSet(current, "C", currentStamp, currentStamp + 1);
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CAS never fails | CAS fails whenever the value was changed by another thread; must retry |
| CAS is free under contention | High contention causes CAS spin loops → CPU waste (worse than mutex) |
| CAS prevents ABA | CAS only checks value equality; ABA requires `AtomicStampedReference` |
| CAS = lock-free = no synchronization cost | CAS still implies a memory barrier; cache coherency traffic still exists |
| Only atomic primitives use CAS | ConcurrentHashMap, CopyOnWriteArrayList, and most java.util.concurrent internals use CAS |

---

### 🔥 Pitfalls in Production

**Pitfall 1: High contention — CAS spin becomes CPU-bound**

```java
// Bad: 100 threads all incrementing one AtomicLong  
// Under extreme contention, CAS retries dominate — 
// threads spin burning CPU but making slow progress

// Fix: LongAdder splits the counter into multiple cells
// Each thread updates its own cell → no contention → merge at read
LongAdder adder = new LongAdder();  // preferred for high-write counters
adder.increment();
long total = adder.sum();           // not linearizable but much faster
```

**Pitfall 2: ABA problem in pointer-based structures**

```java
// Stack: top = A → B
// Thread 1: reads top=A, plans to pop
// Thread 2: pops A and B, pushes new A (different object, same value)
// Thread 1: CAS(top, A, B) succeeds — but B was already freed!
// Result: ABA causes use-after-free equivalent

// Fix: AtomicStampedReference or AtomicMarkableReference
```

**Pitfall 3: Infinite retry loop with no backoff**

```java
// Under contention, tight CAS loops starve other threads
while (!cas.compareAndSet(old, newVal)) {
    old = cas.get();  // no backoff — hammers memory bus
}

// Better: exponential backoff or use higher-level abstractions
```

---

### 🔗 Related Keywords

- **[Atomic Variables](./363 — Atomic Variables.md)** — Java's CAS-backed atomic types
- **[Lock-Free Data Structures](./347b — Lock-Free Data Structures.md)** — algorithms built on CAS
- **[volatile](./339 — volatile.md)** — visibility guarantee that CAS builds on
- **[Java Memory Model (JMM)](./345 — Java Memory Model (JMM).md)** — memory ordering guarantees
- **[VarHandle](./364 — VarHandle.md)** — modern API for CAS on arbitrary fields

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Atomic conditional swap — hardware primitive  │
│              │ enabling lock-free algorithms                  │
├──────────────┼───────────────────────────────────────────────┤
│ JAVA API     │ AtomicInteger.compareAndSet(expected, update) │
├──────────────┼───────────────────────────────────────────────┤
│ PATTERN      │ do { read } while (!CAS(read, compute))       │
├──────────────┼───────────────────────────────────────────────┤
│ ABA PROBLEM  │ A→B→A fools value-only CAS; use stamped ref   │
├──────────────┼───────────────────────────────────────────────┤
│ WHEN FAST    │ Low contention; fast critical sections        │
├──────────────┼───────────────────────────────────────────────┤
│ WHEN SLOW    │ High contention; use LongAdder or mutex       │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Explain the ABA problem with a concrete stack example. Why does CAS fail to detect it?

**Q2.** When would you prefer a mutex over CAS-based atomics? What makes CAS worse under high contention?

**Q3.** `LongAdder` outperforms `AtomicLong` for counters under contention. What architectural trick does it use, and why does it trade consistency for throughput?

