---
layout: default
title: "VarHandle"
parent: "Java Concurrency"
nav_order: 364
permalink: /java-concurrency/varhandle/
number: "0364"
category: Java Concurrency
difficulty: ★★★
depends_on: Atomic Classes, CAS, Volatile, Java Memory Model, Unsafe
used_by: Lock-Free Data Structures, High-Performance Libraries, Custom Atomics
related: AtomicInteger, Unsafe, Volatile, StampedLock, MemoryOrder
tags:
  - concurrency
  - java
  - varhandle
  - memory-model
  - lock-free
  - advanced
---

# 364 — VarHandle

⚡ TL;DR — VarHandle is a typed, safe replacement for `sun.misc.Unsafe` that provides fine-grained memory access modes (plain, volatile, acquire/release, opaque) and CAS operations on any field or array element with full JVM safety guarantees.

| #0364 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Atomic Classes, CAS, Volatile, Java Memory Model, Unsafe | |
| **Used by:** | Lock-Free Data Structures, High-Performance Libraries, Custom Atomics | |
| **Related:** | AtomicInteger, Unsafe, Volatile, StampedLock, MemoryOrder | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You're implementing a high-performance concurrent queue. You need CAS on the `next` field of a node class, but `AtomicReference` wraps your object in another object (allocation overhead). `AtomicReferenceFieldUpdater` works but requires a `String` field name (not refactoring-safe) and does `AccessController` security checks on every operation. `sun.misc.Unsafe` gives you direct CAS with zero overhead but: (1) it's not a public API, (2) it bypasses all JVM safety guarantees, (3) it will break in future JDK versions.

**THE BREAKING POINT:**
`sun.misc.Unsafe` powers much of `java.util.concurrent` internally but is explicitly "unsafe" and inaccessible to application code in modular Java (JDK 9+ with `--add-opens` workarounds needed). Library authors (Netty, Disruptor, Agrona, Chronicle) have depended on `Unsafe` for a decade, creating a fragile dependency on JDK internals that could break at any JDK update.

**THE INVENTION MOMENT:**
Java 9 introduced `VarHandle` (JEP 193) as the official, safe, typed equivalent of `Unsafe` for variable access. It provides: (1) all CAS and atomic operations `Unsafe` provides; (2) explicit memory ordering modes (plain, opaque, acquire, release, volatile) mirroring the C++11 memory model; (3) full JVM bytecode verification and null/bounds checking; (4) stability as a public API. Library authors can now achieve `Unsafe`-level performance without the stability risk.

---

### 📘 Textbook Definition

**VarHandle** is a typed reference to a variable — a field, array element, or off-heap location — introduced in Java 9 (`java.lang.invoke.VarHandle`). It provides access modes that map directly to the Java Memory Model's ordering guarantees: `plain` (no guarantee beyond Java semantics), `opaque` (bitwise atomicity, no ordering), `acquire` (reads: see all writes before the matching release), `release` (writes: visible to subsequent acquire reads), `volatile` (sequential consistency). CAS operations: `compareAndSet(obj, expected, newVal)`, `compareAndExchange(obj, expected, newVal)` (returns witness), `weakCompareAndSet(obj, expected, newVal)` (may spuriously fail, useful for retry loops). Created via `MethodHandles.lookup().findVarHandle(class, fieldName, fieldType)` — type-checked and security-verified once at creation time, not on every access.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
VarHandle is the safe, official way to do CAS and precise memory-order operations on any field without using `Unsafe`.

**One analogy:**
> VarHandle is like a notarized power of attorney for a specific bank account field. Once notarized (at creation time), you can use it to perform any operation — read, write, CAS — with exactly the memory ordering you specify. The notarization handles all safety checks once; each use is fast. Compare to `Unsafe`: a lockpick that works on any lock but the bank might change the locks on you.

**One insight:**
VarHandle's most underused feature is its memory ordering modes. Most code uses only `volatile` access, but `acquire/release` ordering is sufficient for many lock-free patterns and costs half the memory fence instructions of `volatile`. Getting ordering right requires deep Java Memory Model understanding — but done correctly, it produces faster and more formally correct concurrent code.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. VarHandle is created once via `MethodHandles.lookup()` — type safety verified at creation.
2. Access modes map to JMM ordering guarantees:
   - `plain`: like regular field read/write — compiler/CPU can reorder freely
   - `opaque`: bitwise atomic — no word tearing; no ordering between other operations
   - `acquire` (reads) / `release` (writes): one-sided memory fence (cheaper than volatile)
   - `volatile`: full sequential consistency — strongest, most expensive
3. CAS operations: `compareAndSet`, `compareAndExchange`, `weakCompareAndSet`.
4. No allocation overhead — VarHandle operates directly on the target field.

**DERIVED DESIGN:**

```
VARHANDLE CREATION (once, during class initialization):
private static final VarHandle NEXT;
static {
    try {
        NEXT = MethodHandles.lookup()
            .findVarHandle(Node.class, "next", Node.class);
        // Type checked: "next" is Node type ✓
        // Security checked: caller can access Node.next ✓
    } catch (Exception e) { throw new Error(e); }
}

USAGE (zero overhead after creation):
// Plain write (no ordering):
NEXT.set(node, newNext);

// Volatile write (sequential consistency):
NEXT.setVolatile(node, newNext);

// Release write (pairs with acquire read on other thread):
NEXT.setRelease(node, newNext);

// CAS (if node.next == expected, set to newNext):
boolean ok = NEXT.compareAndSet(node, expected, newNext);

// CAS returning witness value:
Node witness = (Node) NEXT.compareAndExchange(node, expected, newNext);
// witness == expected → CAS succeeded; witness != expected → failed
```

```
MEMORY ORDERING MODES vs COST:
┌────────────────┬──────────┬───────────────────────────────┐
│ Mode           │ Fence    │ Guarantee                     │
├────────────────┼──────────┼───────────────────────────────┤
│ plain          │ None     │ Just Java program order       │
│ opaque         │ None     │ Bitwise atomic (no tearing)   │
│ getAcquire     │ Load     │ All prior writes visible      │
│ setRelease     │ Store    │ All prior writes flushed      │
│ getVolatile    │ Full     │ Sequential consistency        │
│ setVolatile    │ Full     │ Sequential consistency        │
│ compareAndSet  │ Full     │ CAS + sequential consistency  │
└────────────────┴──────────┴───────────────────────────────┘
```

**THE TRADE-OFFS:**
- **Gain:** Official API; zero overhead vs Unsafe on modern JVMs; explicit memory ordering; works in module system.
- **Cost:** Verbose creation; requires `MethodHandles.lookup()` (module access rules apply); requires deep JMM knowledge to use correctly; harder to use than `AtomicInteger` for simple cases.

---

### 🧪 Thought Experiment

**SETUP:**
You're implementing a lock-free, single-producer/single-consumer (SPSC) ring buffer. The producer writes to slot `[writeIndex]` and advances `writeIndex`. The consumer reads from slot `[readIndex]` and advances `readIndex`. No synchronization needed for the data slots themselves — only the index updates must be visible across threads.

**WITHOUT VarHandle (using volatile fields):**
Both `writeIndex` and `readIndex` are `volatile`. Every write and read of these indices incurs a full memory fence. On modern x86, a full store fence (`MFENCE`) costs ~40-100 CPU cycles. At 100M ops/sec, fences alone cost 4–10 CPU seconds per second — all overhead.

**WITH VarHandle + acquire/release:**
- Producer: writes to slot (plain), then `writeIndex.setRelease(newIndex)` — one store fence.
- Consumer: `readIndex.getAcquire()` — one load fence — then reads slot (plain).
- The acquire/release pair is sufficient: consumer's acquire read sees everything before producer's release write.
- Cost: one directional fence instead of two full fences per operation. Up to 2x throughput improvement.

**THE INSIGHT:**
acquire/release is sufficient for producer-consumer patterns. `volatile` (sequential consistency) is only needed when you need total ordering across ALL threads — not just between one producer and one consumer. Using the weakest sufficient ordering mode is the key to efficient lock-free code.

---

### 🧠 Mental Model / Analogy

> VarHandle memory ordering modes are like progressively stricter security checkpoints at an airport. **Plain**: walk right through, no check. **Opaque**: just verify you have a boarding pass (atomic access). **Acquire/Release**: standard security lane — "everything packed before this point is in your checked bag." **Volatile**: full TSA screening with shoe removal — nothing gets through until the person in front is completely clear. Each level costs more time; choose the minimum level that your protocol requires for correctness.

- "Walk right through" → plain read/write, no ordering
- "Standard security lane" → acquire/release ordering (directional fence)
- "Full TSA screening" → volatile (full sequential consistency)
- "Security checkpoint" → memory fence instruction inserted by JIT
- "Person in front must clear completely" → happens-before relationship

Where this analogy breaks down: unlike airport security, acquire/release ordering is asymmetric — the "acquire" is on the reader and the "release" is on the writer. They must be paired correctly to create a happens-before relationship; using acquire on both or release on both is a bug.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
VarHandle is a handle that lets you read, write, or atomically update a specific field in an object, with control over how visible those changes are to other threads. Most developers don't use VarHandle directly — it powers the internals of `AtomicInteger` and similar classes.

**Level 2 — How to use it (junior developer):**
You likely won't use VarHandle directly in application code. But if you're building a library and need CAS on a field without `AtomicReference` allocation overhead, create the VarHandle in a static block: `MethodHandles.lookup().findVarHandle(MyClass.class, "myField", long.class)`. Use `compareAndSet(object, expected, newVal)` instead of `AtomicLong.compareAndSet`. The field must be declared (but not necessarily `volatile` — the access mode controls ordering).

**Level 3 — How it works (mid-level engineer):**
VarHandle operations are polymorphic inline methods — the JIT compiler can fully inline them into machine code. A `VarHandle.compareAndSet()` compiles to a single `LOCK CMPXCHG` instruction on x86, with no method dispatch overhead. The memory ordering modes map to specific CPU instructions: `volatile` → `MFENCE`; `setRelease` → store with `sfence`; `getAcquire` → `lfence` (implicit on x86 due to strong TSO model, but necessary on ARM). The `MethodHandles.lookup()` at creation time performs access control checks — module access, field visibility — once, not per call. This is the "price paid once" design.

**Level 4 — Why it was designed this way (senior/staff):**
VarHandle's design is directly inspired by the C++11 `std::atomic` memory model, which itself was formalized by the C++ Standards Committee based on hardware memory consistency research. The Java Memory Model predates C++11 and lacked the explicit acquire/release distinction. JEP 193 retrofitted these semantics into Java via VarHandle without changing the core JMM. The "poly-morphic method" invocation design (similar to `MethodHandle`) allows the JIT to produce optimal machine code for each access mode while maintaining a uniform API. The key insight: correctness guarantees should be paid for once (at VarHandle creation) and the per-access overhead should be zero beyond what the memory ordering semantically requires — exactly the principle behind C++ zero-overhead abstractions.

---

### ⚙️ How It Works (Mechanism)

```java
// CREATING VARHANDLES (class initialization, done once)
import java.lang.invoke.*;

class LockFreeStack<T> {
    private volatile Node<T> top;

    // VarHandle for the 'top' field
    private static final VarHandle TOP;
    static {
        try {
            TOP = MethodHandles.lookup()
                .findVarHandle(LockFreeStack.class,
                               "top", Node.class);
            // verified once: type safety, access rights
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // Lock-free push using VarHandle CAS
    void push(T item) {
        Node<T> newNode = new Node<>(item);
        Node<T> current;
        do {
            current = (Node<T>) TOP.getAcquire(this); // acquire read
            newNode.next = current;
        } while (!TOP.compareAndSet(this, current, newNode));
        // CAS: if top == current, set top = newNode
        // If CAS fails: another thread pushed first, retry
    }

    // Lock-free pop
    T pop() {
        Node<T> current;
        Node<T> next;
        do {
            current = (Node<T>) TOP.getAcquire(this);
            if (current == null) return null; // empty
            next = current.next;
        } while (!TOP.compareAndSet(this, current, next));
        return current.item;
    }
}

// MEMORY ORDERING EXAMPLE: SPSC producer-consumer
class SPSCBuffer {
    private final Object[] buffer = new Object[1024];
    private long writeIndex = 0;
    private long readIndex = 0;

    private static final VarHandle WRITE_IDX;
    private static final VarHandle READ_IDX;
    static {
        try {
            WRITE_IDX = MethodHandles.lookup()
                .findVarHandle(SPSCBuffer.class,
                               "writeIndex", long.class);
            READ_IDX  = MethodHandles.lookup()
                .findVarHandle(SPSCBuffer.class,
                               "readIndex", long.class);
        } catch (Exception e) { throw new Error(e); }
    }

    // Producer: write data, then RELEASE writeIndex
    void produce(Object item) {
        long wi = (long) WRITE_IDX.getOpaque(this);
        buffer[(int)(wi & 1023)] = item;      // plain write to slot
        WRITE_IDX.setRelease(this, wi + 1);   // release: data visible
    }

    // Consumer: ACQUIRE readIndex, then read data
    Object consume() {
        long ri = (long) READ_IDX.getOpaque(this);
        long wi = (long) WRITE_IDX.getAcquire(this); // acquire
        if (ri == wi) return null; // empty
        Object item = buffer[(int)(ri & 1023)]; // plain read
        READ_IDX.setRelease(this, ri + 1);    // release
        return item;
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (VarHandle CAS in lock-free stack push):
Thread creates new Node
→ Reads current top via getAcquire (acquire fence)
→ Sets node.next = current
→ [VarHandle.compareAndSet ← YOU ARE HERE]
→ CAS: if top == current → set top = newNode (success)
→ Or: CAS fails (concurrent push) → retry loop
→ Stack updated atomically with correct ordering

FAILURE PATH:
Incorrect memory ordering (using setVolatile where setRelease needed)
→ No incorrect behaviour on x86 (TSO model: stores don't reorder)
→ Incorrect behaviour on ARM/RISC-V (weaker memory model)
→ Consumer reads slot data BEFORE producer's release write is visible
→ Observable: data corruption in consumer; only on non-x86 hardware
→ Fix: use setRelease in producer, getAcquire in consumer

WHAT CHANGES AT SCALE:
On NUMA systems, VarHandle operations touching fields of objects
allocated on remote NUMA nodes have higher latency due to
cross-NUMA memory access. LMAX Disruptor addresses this by
padding cache lines (preventing false sharing) and ensuring
producer/consumer objects are NUMA-local. VarHandle's access
modes are still correct but raw latency is higher — the
ordering primitives are cheap, the actual memory access is not.
```

---

### 💻 Code Example

```java
// Example: FieldUpdater migration to VarHandle
// Old way: AtomicReferenceFieldUpdater (reflection string name)
AtomicReferenceFieldUpdater<Node, Node> nextUpdater =
    AtomicReferenceFieldUpdater.newUpdater(
        Node.class, Node.class, "next"  // string name — fragile!
    );
nextUpdater.compareAndSet(node, expected, newNext);

// New way: VarHandle (type-safe, refactoring-safe)
private static final VarHandle NEXT =
    MethodHandles.lookup().findVarHandle(
        Node.class, "next", Node.class  // IDEs can rename this
    );
NEXT.compareAndSet(node, expected, newNext);

// Example: compareAndExchange (returns witness value)
// Useful when you need the current value on failure without re-read:
Node witness = (Node) NEXT.compareAndExchange(node, expected, newNext);
if (witness == expected) {
    // CAS succeeded
} else {
    // CAS failed; witness is the actual current value
    // No need to do another read — we already have it
}

// Example: weakCompareAndSet (may spuriously fail — for retry loops)
// Cheaper than compareAndSet on some architectures (ARM LL/SC)
while (!NEXT.weakCompareAndSetPlain(node, expected, newNext)) {
    expected = (Node) NEXT.getOpaque(node); // re-read
}
```

---

### ⚖️ Comparison Table

| API | Safety | Overhead | Access Modes | Best For |
|---|---|---|---|---|
| `volatile` field | JVM safe | Full fence | Volatile only | Simple shared flags |
| `AtomicInteger/Long` | JVM safe | One extra object | Volatile | Simple counters/refs |
| `AtomicXxxFieldUpdater` | JVM safe | String-name risk | Volatile | Legacy field CAS |
| **VarHandle** | JVM safe | None (inlined) | All (plain to volatile) | Library internals, performance |
| `sun.misc.Unsafe` | Not safe | None (inlined) | All | JDK internals only |

**How to choose:** Use `AtomicInteger`/`AtomicLong` for application-level atomic operations — simpler API, no boilerplate. Use `VarHandle` when building libraries that need CAS on existing class fields without allocation overhead, or when you need weaker-than-volatile access modes for performance.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| VarHandle is just a nicer Unsafe API | VarHandle adds JVM type safety, bounds checking, module system compatibility, and correctness guarantees that Unsafe never provided. It's not "nicer Unsafe" — it's the first truly safe low-level JVM variable access API |
| acquire/release is weaker so it's less safe | Correctness is about using the minimum ordering that your protocol requires. acquire/release is correct for producer-consumer; using volatile for it is paying extra for unneeded guarantees — wasteful but not unsafe |
| VarHandle operations on x86 are equivalent to volatile | On x86's TSO (Total Store Order) model, loads have acquire semantics and stores have release semantics by default — so acquire/release and volatile produce the same machine code on x86. But on ARM or RISC-V, they produce different instructions. Write for the JMM, not for x86 |
| You need VarHandle for all concurrent field access | You only need VarHandle for CAS operations or weaker-than-volatile memory ordering. Normal shared fields should just be `volatile` or protected by standard synchronization |

---

### 🚨 Failure Modes & Diagnosis

**Wrong Memory Ordering Causes Visibility Bug on non-x86**

**Symptom:** Lock-free algorithm works correctly on x86 (development machines) but fails intermittently on ARM-based production servers (AWS Graviton, Apple M-series, Android devices).

**Root Cause:** Using `plain` or `opaque` access modes when `acquire/release` is required for correctness. x86's TSO model masks the bug; ARM's weaker memory model exposes it.

**Diagnostic Command:**
```bash
# Run stress test on ARM:
# Use jcstress (JVM Concurrency Stress Tests) — the only
# reliable way to detect memory ordering bugs:
java -jar jcstress.jar -t MyOrderingTest

# Or use LLVM Memory Model Litmus Tests tooling
```

**Fix:** Audit VarHandle access modes against the JMM happens-before requirements. Use `setRelease`/`getAcquire` for producer-consumer; `volatile` for any-to-any ordering.

**Prevention:** Test concurrent algorithms with jcstress on multiple architectures. Never assume x86 test results cover ARM behaviour.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Atomic Classes` — VarHandle is what atomic classes use internally; know atomic first
- `Volatile` — VarHandle's volatile mode is the same as `volatile` field declarations
- `Java Memory Model` — required to correctly choose access modes (acquire/release vs volatile)
- `CAS` — the core operation VarHandle provides at field level

**Builds On This (learn these next):**
- `Lock-Free Data Structures` — VarHandle is the primitive used to build them
- `Memory Ordering (C++ analogy)` — C++ std::atomic memory_order provides the same abstraction
- `Project Loom / Structured Concurrency` — future Java concurrency building on VarHandle primitives

**Alternatives / Comparisons:**
- `AtomicInteger/Long` — higher-level, easier API; VarHandle for fields without allocation overhead
- `sun.misc.Unsafe` — same power, no safety; avoid in application code
- `AtomicReferenceFieldUpdater` — older field-CAS API; VarHandle is strictly superior

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Typed, safe, zero-overhead field accessor │
│              │ with explicit memory ordering modes       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Library-level CAS on fields without       │
│ SOLVES       │ Unsafe, allocation overhead, or fragility │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ acquire/release is sufficient for P/C     │
│              │ patterns; volatile is overkill (and slow) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building concurrent libraries; need CAS   │
│              │ on existing fields; need weaker ordering  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Application code — use AtomicInteger etc; │
│              │ when you don't understand JMM ordering    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Maximum performance + correctness vs      │
│              │ complexity and deep JMM knowledge needed  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A notarized power of attorney: checked   │
│              │  once at creation, zero cost per use"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lock-Free Data Structures → JMM →         │
│              │ Disruptor Pattern                         │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** VarHandle's `compareAndExchange` returns the witness value — the actual value at the time of the CAS attempt. Compare this to `compareAndSet` which returns a boolean. Describe a concrete lock-free algorithm (e.g., a Treiber stack variant) where using `compareAndExchange` instead of `compareAndSet` measurably reduces retry loop iterations under contention, and explain the precise mathematical reason why the witness value eliminates one read operation per failed attempt.

**Q2.** On x86, `setRelease` and `setVolatile` produce almost identical machine code because x86's TSO memory model already provides release semantics for stores. But on ARM, `setRelease` uses `STLR` (store-release) while `setVolatile` uses `STLR` + `DMB ISH` (full barrier). If a Java library correctly uses VarHandle acquire/release semantics and is tested only on x86, what is the precise JMM rule that guarantees the same correctness on ARM without any code changes — and why does the JIT compiler rather than the developer bear responsibility for inserting the correct instructions?
