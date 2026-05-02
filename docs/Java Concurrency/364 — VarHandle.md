---
layout: default
title: "VarHandle"
parent: "Java Concurrency"
nav_order: 364
permalink: /java-concurrency/varhandle/
number: "364"
category: Java Concurrency
difficulty: ★★★
depends_on: CAS (Compare-And-Swap), Atomic Variables, Java Memory Model (JMM), Memory Barrier, Happens-Before
used_by: Lock-Free Data Structures, Atomic Variables
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
---

# 364 — VarHandle

`#java` `#concurrency` `#advanced` `#deep-dive`

⚡ TL;DR — A typed, bound reference to a variable (field, array element, or off-heap memory) that provides atomic operations and memory-ordering guarantees without `sun.misc.Unsafe`.

| #364 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAS (Compare-And-Swap), Atomic Variables, Java Memory Model (JMM), Memory Barrier, Happens-Before | |
| **Used by:** | Lock-Free Data Structures, Atomic Variables | |

---

### 📘 Textbook Definition

`java.lang.invoke.VarHandle` (Java 9+) is an abstraction providing typed references to Java variables — fields, array elements, and off-heap memory — with access modes that specify atomic operations and memory-ordering constraints. Access modes range from plain (no ordering) through `getVolatile`/`setVolatile` (full sequential consistency), `getAcquire`/`setRelease` (acquire-release ordering), `getOpaque`/`setOpaque` (visibility with no ordering), to atomic CAS (`compareAndSet`), numeric atomic updates (`getAndAdd`), and bitwise atomic operations. `VarHandle` replaces `sun.misc.Unsafe` for low-level concurrency in the standard JDK as of Java 9.

### 🟢 Simple Definition (Easy)

VarHandle is a safe, official way to do directly-on-a-field atomic operations — like `AtomicInteger` but for any field without wrapping objects.

### 🔵 Simple Definition (Elaborated)

Before Java 9, library authors who needed atomic operations on individual object fields (for lock-free data structures) had to use `sun.misc.Unsafe` — an internal, unsafe API that could crash the JVM. `VarHandle` is the official, safe replacement. You create a `VarHandle` once that points to a specific field (e.g., `next` pointer in a linked list node) and then use it to do atomic get, set, CAS, and add operations on that field in any object. It also provides fine-grained memory-ordering modes (acquire/release/plain/opaque) that are cheaper than full `volatile` semantics when you don't need sequential consistency.

### 🔩 First Principles Explanation

**The pre-Java 9 problem:**

`java.util.concurrent.atomic.AtomicInteger` is convenient but requires wrapping every field in an `Atomic*` object — adding object allocation and indirection overhead. `AtomicIntegerFieldUpdater` existed but was slow due to reflection and required all fields to be `volatile`. The only fast alternative was `sun.misc.Unsafe.compareAndSwapInt()`, but `Unsafe` is a JDK-internal class, not part of the public API.

**VarHandle design:**

1. **One VarHandle per field type:** Created once via `MethodHandles.lookup().findVarHandle()`.
2. **Fully typed:** The VarHandle knows the field type at creation time; operations are type-safe.
3. **Intrinsified by JIT:** The JIT compiles VarHandle operations to direct hardware atomic instructions (e.g., `LOCK CMPXCHG` on x86) — same performance as Unsafe.
4. **Access modes:**
   - `get/set` — plain (no memory ordering; like regular field access).
   - `getOpaque/setOpaque` — coherent (visible to same thread and some ordering).
   - `getAcquire/setRelease` — acquire-release semantics (used for lock-free protocols).
   - `getVolatile/setVolatile` — sequential consistency (same as `volatile` field).
   - `compareAndSet` — atomic CAS.
   - `getAndAdd`, `getAndSet`, etc. — atomic read-modify-write.

**Acquire-Release ordering:** Weaker than `volatile` but stronger than plain. `getAcquire` ensures all subsequent reads/writes are visible after the acquire. `setRelease` ensures all prior reads/writes are visible before the release. This matches the semantics needed for lock-free lock implementations (acquire on lock, release on unlock) — without the full cost of sequential consistency.

### ❓ Why Does This Exist (Why Before What)

WITHOUT VarHandle:

- Library authors needed `sun.misc.Unsafe` for field-level atomic operations.
- `Unsafe` is not portable, not supported between JDK versions, and can segfault the JVM.
- `AtomicIntegerFieldUpdater` was slow and required fields to be `volatile` unnecessarily.
- No way to specify memory ordering weaker than `volatile` for performance-critical lock-free code.

What breaks without it:
1. Lock-free data structures (e.g., `ConcurrentLinkedQueue`'s next pointer) require unsafe atomics.
2. JDK 9+ module system restricts access to `sun.misc.Unsafe`, breaking existing usage.

WITH VarHandle:
→ Standard API for field-level atomics — no Unsafe needed.
→ Fine-grained memory ordering (plain, opaque, acquire/release, volatile) enables micro-optimisations.
→ Safe across JDK versions and accessible from all modules.

### 🧠 Mental Model / Analogy

> VarHandle is like a typed TV remote that's permanently paired with one specific TV (the field). The remote has multiple buttons: `getVolatile` (full scan of all channels — expensive), `getAcquire` (half-scan — medium cost), `get` (instant, no scan — cheapest). The same remote can also do special tricks: atomically flip the channel if it's still on the same one as when you last checked (`compareAndSet`). The key: *the remote is bound to a specific TV* — it can't control a different model without creating a new remote.

"TV remote" = VarHandle, "TV" = specific field instance, "scan level" = memory ordering mode, "channel flip" = CAS operation.

The hierarchy from expensive to cheap: `volatile` (full sequential scan) → acquire/release (half scan) → opaque (quick peek) → plain (no scan).

### ⚙️ How It Works (Mechanism)

**Creating a VarHandle:**

```java
// Obtain a VarHandle for the "next" field of Node class
// MethodHandles.lookup() must be called from within the class
// that owns the field for full access rights
private static final VarHandle NEXT;
static {
    try {
        NEXT = MethodHandles.lookup()
            .findVarHandle(Node.class, "next", Node.class);
    } catch (ReflectiveOperationException e) {
        throw new ExceptionInInitializerError(e);
    }
}
```

**Access mode comparison:**

```
Access Mode       Ordering              Cost
──────────────────────────────────────────────────
plain             None (register-like)  ~1 ns
getOpaque         Coherence only        ~2 ns
getAcquire        Acquire fence         ~5 ns
getVolatile       Full SC fence         ~10 ns
compareAndSet     Full SC + hardware CAS ~10-20 ns
```

**Lock-free increment using VarHandle:**

```java
// Instead of AtomicInteger, use VarHandle on an int field
class Counter {
    private volatile int count = 0;
    private static final VarHandle COUNT;
    static {
        try { COUNT = MethodHandles.lookup()
            .findVarHandle(Counter.class, "count", int.class);
        } catch (Exception e) { throw new Error(e); }
    }

    // Atomic increment using VarHandle
    public int getAndIncrement() {
        return (int) COUNT.getAndAdd(this, 1);
    }

    // CAS with VarHandle
    public boolean compareAndSet(int expected, int update) {
        return COUNT.compareAndSet(this, expected, update);
    }
}
```

### 🔄 How It Connects (Mini-Map)

```
sun.misc.Unsafe (internal, deprecated path)
           ↓ replaced by
VarHandle (Java 9+) ← you are here
           ↑ used by
AtomicInteger / AtomicReference
           ↑ higher-level
AtomicIntegerFieldUpdater (legacy, slower)
           ↓ enables
Lock-Free Data Structures
```

### 💻 Code Example

Example 1 — Lock-free linked list node using VarHandle:

```java
public class LockFreeStack<T> {
    private static class Node<T> {
        final T value;
        volatile Node<T> next; // must be volatile for VarHandle

        Node(T val) { this.value = val; }
    }

    private volatile Node<T> head = null;

    private static final VarHandle HEAD;
    static {
        try {
            HEAD = MethodHandles.lookup()
                .findVarHandle(
                    LockFreeStack.class, "head",
                    Node.class);
        } catch (Exception e) { throw new Error(e); }
    }

    public void push(T value) {
        Node<T> newHead = new Node<>(value);
        Node<T> oldHead;
        do {
            oldHead = (Node<T>) HEAD.getVolatile(this);
            newHead.next = oldHead;
        } while (!HEAD.compareAndSet(this, oldHead, newHead));
        // CAS: only update head if it's still oldHead
    }

    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = (Node<T>) HEAD.getVolatile(this);
            if (oldHead == null) return null;
            newHead = oldHead.next;
        } while (!HEAD.compareAndSet(this, oldHead, newHead));
        return oldHead.value;
    }
}
```

Example 2 — Acquire-release ordering for a simple spinlock:

```java
public class SpinLock {
    private volatile int locked = 0;
    private static final VarHandle LOCKED;
    static {
        try { LOCKED = MethodHandles.lookup()
            .findVarHandle(SpinLock.class, "locked", int.class);
        } catch (Exception e) { throw new Error(e); }
    }

    public void lock() {
        // Spin until CAS succeeds: 0→1
        while (!LOCKED.compareAndSet(this, 0, 1)) {
            Thread.onSpinWait(); // hint CPU to relax
        }
        // Implicit acquire fence after successful CAS
    }

    public void unlock() {
        // setRelease: all prior writes visible before release
        LOCKED.setRelease(this, 0);
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| VarHandle is only useful for library authors | Any code needing field-level atomics without Atomic* wrapper allocation benefits from VarHandle. |
| getVolatile is always the safest choice | getVolatile adds a full memory fence; for lock-free protocols, getAcquire/setRelease provides all necessary ordering at lower cost. |
| VarHandle works on non-volatile fields | For atomic modes (CAS, getAndAdd), the field doesn't need to be volatile — VarHandle adds the ordering itself. Plain access modes on non-volatile fields have no ordering guarantee. |
| VarHandle is slower than AtomicInteger | VarHandle + int field compiles to identical machine code as AtomicInteger internally — both use the same hardware CAS instructions. |
| You need one VarHandle per instance | VarHandle is created once per field — it's shared and used with different object instances via the `instance` parameter in each operation. |

### 🔥 Pitfalls in Production

**1. Creating VarHandle Per Method Call — Expensive Reflection**

```java
// BAD: Creating VarHandle on every call
public void update(MyObj obj) {
    try {
        VarHandle vh = MethodHandles.lookup()
            .findVarHandle(MyObj.class, "field", int.class);
        vh.compareAndSet(obj, 0, 1); // expensive creation!
    } catch (Exception e) { throw new Error(e); }
}

// GOOD: Create once in static initialiser
private static final VarHandle FIELD;
static {
    try { FIELD = MethodHandles.lookup()
        .findVarHandle(MyObj.class, "field", int.class);
    } catch (Exception e) { throw new Error(e); }
}
```

**2. Accessing Field as Wrong Type in VarHandle**

```java
// BAD: VarHandle for int field, but using long operations
VarHandle vh = MethodHandles.lookup()
    .findVarHandle(MyObj.class, "value", int.class);
long result = (long) vh.getAndAdd(obj, 1L); // WrongMethodTypeException!

// GOOD: Match types exactly
int result = (int) vh.getAndAdd(obj, 1); // int increments by int
```

**3. Forgetting volatile Annotation for Ordered Accesses**

```java
// You don't NEED volatile for VarHandle CAS:
private int counter = 0; // plain int is fine for VarHandle CAS

// But for regular field access TO BE ORDERED,
// either use VarHandle.getVolatile() or declare volatile:
private volatile int counter = 0;
// If mixing direct field reads with VarHandle CAS,
// declare volatile to ensure visibility
```

### 🔗 Related Keywords

- `CAS (Compare-And-Swap)` — the hardware primitive VarHandle `compareAndSet` uses.
- `Atomic Variables` — higher-level wrappers that use VarHandle internally since Java 9.
- `Java Memory Model (JMM)` — VarHandle access modes are defined relative to JMM ordering.
- `Memory Barrier` — VarHandle's ordering modes map directly to hardware memory fence instructions.
- `Lock-Free Data Structures` — the primary use case for VarHandle in library development.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Safe, typed field-level atomic operations │
│              │ with tunable memory ordering. Unsafe      │
│              │ replacement for lock-free code.           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lock-free data structures; eliminating    │
│              │ Atomic* wrapper allocation overhead;      │
│              │ acquire-release lock protocols.           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple counters/flags — use AtomicInteger;│
│              │ high-level sync — use Lock/synchronized.  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "VarHandle: field-level atomics without  │
│              │ needing Unsafe or wrapper objects."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lock-Free DS → Memory Barrier → JMM       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A high-performance ring buffer uses `VarHandle.setRelease()` for the producer to write a value and `VarHandle.getAcquire()` for the consumer to read it. Explain why `setRelease`/`getAcquire` is the correct ordering pair for this producer-consumer pattern — specifically, what acquire-release ordering guarantees about the visibility of non-VarHandle writes that preceded the `setRelease` call.

**Q2.** VarHandle's `compareAndSet(obj, expected, witness)` is documented as providing sequential consistency. For a lock-free stack implementation, you use CAS on the `head` pointer. Under the Java Memory Model, what property does sequential consistency on this single CAS operation provide that an acquire-release CAS would NOT provide, and in what specific scenario would using acquire-release CAS on the head pointer lead to an observable correctness bug?

