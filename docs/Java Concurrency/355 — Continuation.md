---
layout: default
title: "Continuation"
parent: "Java Concurrency"
nav_order: 355
permalink: /java-concurrency/continuation/
number: "355"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads (Project Loom), Carrier Thread, Thread (Java), Stack Frame
used_by: Structured Concurrency, Carrier Thread
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
---

# 355 — Continuation

`#java` `#concurrency` `#advanced` `#deep-dive`

⚡ TL;DR — The saved execution state (call stack + local variables) of a suspended virtual thread, stored on the heap until it is ready to resume on a carrier thread.

| #355 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Virtual Threads (Project Loom), Carrier Thread, Thread (Java), Stack Frame | |
| **Used by:** | Structured Concurrency, Carrier Thread | |

---

### 📘 Textbook Definition

A **Continuation** in the context of Project Loom is an object representing the suspended execution state of a virtual thread — comprising its call stack frames, local variables, and program counter — serialised as a heap-allocated data structure. When a virtual thread is unmounted from its carrier thread (due to a blocking operation), its continuation is created and stored on the Java heap. When the blocking condition resolves, the continuation is re-mounted onto an available carrier thread and execution resumes from exactly where it left off. `jdk.internal.vm.Continuation` is the low-level API; application code never interacts with continuations directly.

### 🟢 Simple Definition (Easy)

A continuation is a bookmark for an entire program's in-progress execution — saving exactly where it was so it can be resumed later, even on a different thread.

### 🔵 Simple Definition (Elaborated)

When a virtual thread blocks (waits for I/O, sleeps, or acquires a lock), the JVM needs to free up its carrier OS thread immediately so it can run other work. But the virtual thread isn't done — it just needs to pause temporarily. The JVM saves the virtual thread's entire execution state — all its pending method calls, local variables, the exact line it was on — into a compact object called a continuation. This object is stored on the heap (not tied to any thread's stack). When the blocking condition resolves, the JVM finds an available carrier thread, reconstructs the execution from the saved continuation, and the virtual thread continues as if it never stopped.

### 🔩 First Principles Explanation

**The call stack problem:**

Platform threads each have a fixed OS-allocated stack (typically 512 KB to 1 MB). When a thread blocks, the OS keeps the entire stack resident in memory. Continuations solve this by moving stack data off the thread and into the heap.

**What a continuation contains:**
1. **Stack frames:** each pending method invocation with its local variables and operand stack state.
2. **Program counter:** the exact bytecode offset where execution should resume.
3. **Object references:** all object references on the stack (GC roots).

**Continuation vs. coroutine vs. fiber:**
- **Coroutine:** language-level construct for cooperative multitasking (Python/Kotlin `async/await`, `yield`).
- **Fiber:** OS-level or library-level lightweight thread.
- **Continuation:** the fundamental mechanism underlying both — the save/restore of execution state.

**Stack copying implementation:**

When a virtual thread unmounts, the JVM performs a "stack freeze":
1. Walk the call stack frames from the current frame up to the continuation entry point.
2. Copy each frame's data into a heap-allocated `StackChunk` object.
3. The virtual thread's continuation now points to this chain of `StackChunk` objects.

When remounted:
1. The `StackChunk` chain is "thawed" back onto the carrier thread's stack.
2. Execution resumes at the saved program counter.

**Stack depth impact:** Very deep call stacks mean larger continuations. For deeply nested code, each blocking call serialises a large stack snapshot. This is why shallow call stacks (typical in modern Java) make virtual threads efficient.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Continuations:

- Virtual threads can't be unmounted without losing their execution state.
- The only alternative for non-blocking code is async/reactive programming (callbacks, CompletableFuture chains) — which inverts the program structure drastically.
- Blocking = tying up an OS thread = limited scalability.

What breaks without it:
1. Millions of concurrent virtual threads impossible — each needs its own OS thread without continuations.
2. Blocking I/O at scale requires rewriting code into callback chains — high complexity, poor debuggability.

WITH Continuations:
→ Virtual threads can block in straight-line code — no callbacks needed.
→ Stack migrates from OS-allocated thread stack to GC-managed Java heap.
→ Millions of suspended continuations on heap cost only the actual stack data (often 1–10 KB each) vs. 512 KB+ OS thread stacks.

### 🧠 Mental Model / Analogy

> Continuation is like a save-game slot in a video game. When you quit mid-game (virtual thread blocks), the game engine saves everything: your exact position, inventory, health, active quests (call stack, local variables, program counter). The console (OS thread / carrier) is freed to play another game. When you want to continue, you load the save slot on any compatible console (carrier thread), and resume exactly where you left off — not from the beginning.

"Save-game slot" = continuation object on heap, "game engine" = JVM, "console" = carrier thread, "loading save on any console" = remounting on any available carrier.

The magic: multiple players (virtual threads) can have saved games (continuations) simultaneously; consoles (carriers) are always busy playing something.

### ⚙️ How It Works (Mechanism)

**Continuation lifecycle:**
```
Virtual Thread RUNNING (mounted on carrier)
       │
       │ blocking op (I/O / sleep / park)
       ▼
Stack Freeze: copy frames to heap (StackChunk)
       │
Continuation FROZEN (on heap)
       │
Carrier thread freed → runs other VT
       │
Blocking op completes (I/O done / timer fired)
       │
Continuation THAWED: frames restored to carrier stack
       │
Virtual Thread RUNNING again (may be different carrier)
```

**Memory cost estimate:**
```
Typical virtual thread continuation:
  - 5 stack frames, 10 local vars each = ~400 bytes
  - Object header + metadata = ~64 bytes
  - Total: ~500 bytes per suspended virtual thread

vs. OS thread stack:
  - 512 KB default minimum

1,000,000 suspended continuations = ~500 MB
1,000,000 OS threads = ~500 GB

That's a 1000× memory reduction.
```

**Accessing continuations (low-level API — rarely needed):**
```java
// jdk.internal.vm.Continuation is a restricted API
// Use it only for framework-level code (never application code)
// Standard API: just create virtual threads and block normally
var vt = Thread.ofVirtual().start(() -> {
    doWork();         // JVM manages continuations transparently
    blockOnIO();      // freeze/thaw happens here automatically
    doMoreWork();     // resumes from continuation
});
```

### 🔄 How It Connects (Mini-Map)

```
Virtual Thread executing
       ↓ blocking
Stack Freeze → Continuation on heap ← you are here
       ↓ I/O complete
Stack Thaw → Virtual Thread resumes
       ↓ running on
Carrier Thread
       ↓
ForkJoinPool (carrier pool)
```

### 💻 Code Example

Example 1 — Continuation-based scaling (developer sees none of it):

```java
// 1 million virtual threads, each blocking 1 second
// Continuations handle all state saves transparently
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1_000_000; i++) {
        exec.submit(() -> {
            // Virtual thread blocks here
            // JVM: freeze call stack into continuation
            Thread.sleep(Duration.ofSeconds(1));
            // JVM: thaw continuation on available carrier
            return "done";
        });
    }
} // all 1M complete; ~500 MB heap for continuations
  // vs. ~500 GB if OS threads were used
```

Example 2 — Thread-local state survives continuation freeze/thaw:

```java
// ThreadLocal values are part of the virtual thread's state
// They survive unmount/remount correctly
ThreadLocal<String> ctx = new ThreadLocal<>();

Thread.ofVirtual().start(() -> {
    ctx.set("request-123");
    doBlockingIO(); // unmount/remount happens here
    // After remount, ctx.get() still returns "request-123"
    String value = ctx.get(); // "request-123" ✓
    System.out.println(value);
});
```

Example 3 — Diagnosing deep stacks and large continuations:

```bash
# Large continuations occur when virtual threads have deep stacks
# Monitor with JFR:
jcmd <pid> JFR.start settings=default duration=30s \
  filename=vt_diag.jfr
jfr print --events jdk.VirtualThreadEnd,jdk.VirtualThreadStart \
  vt_diag.jfr

# For deep stack profiling:
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintVMOptions \
     -jar app.jar
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Continuations are visible to Java application developers | Continuations are an internal JVM mechanism; the public API is just virtual threads. Application code creates virtual threads, not continuations directly. |
| Continuation freeze/thaw is expensive | For typical shallow call stacks (5–20 frames), freeze/thaw takes microseconds. Deep recursive stacks are more expensive. |
| Continuations require special-purpose code | Standard blocking Java code (sleep, socket I/O, Lock.lock()) automatically benefits from continuation-based unmounting when running on virtual threads. |
| A continuation is tied to a specific carrier thread | A continuation can be resumed on any available carrier thread — not necessarily the one it was running on before. ThreadLocals bound to the virtual thread survive; carrier-thread-specific state does not. |
| Virtual thread memory use is approximately zero | Each continuation uses heap proportional to its call stack depth. Shallow stacks: ~1 KB. Very deep stacks: tens of KB. |

### 🔥 Pitfalls in Production

**1. Unbounded Thread-Local State Leaking via Continuations**

```java
// BAD: Large objects in ThreadLocal survive unmount/remount
// and accumulate if virtual threads aren't terminated
ThreadLocal<byte[]> bigBuffer =
    ThreadLocal.withInitial(() -> new byte[1024 * 1024]); // 1 MB!

Thread.ofVirtual().start(() -> {
    bigBuffer.get(); // attaches 1 MB to this virtual thread
    // If this virtual thread is reused or pooled → 1 MB leaked
});

// GOOD: Use ScopedValue for request-scoped context
// Or: remove() ThreadLocal after use
bigBuffer.remove(); // always clean up
```

**2. Using Virtual Thread Pools Defeats Continuation Benefits**

```java
// BAD: Pooling virtual threads reuses thread-local state
// Virtual thread pools are explicitly discouraged by JEP 444
ExecutorService = Executors.newFixedThreadPool(1000,
    Thread.ofVirtual().factory()); // DON'T do this

// GOOD: One virtual thread per task —
// JVM creates/terminates them cheaply
ExecutorService =
    Executors.newVirtualThreadPerTaskExecutor();
```

**3. Very Deep Recursive Stacks Bloating Continuations**

```java
// BAD: 10,000-frame deep recursion on virtual thread
// = large continuation snapshot = heap pressure
void deepRecurse(int n) {
    if (n == 0) { blockOnIO(); return; }
    deepRecurse(n - 1); // 10,000 frames!
    // Each frame included in frozen continuation
}

// GOOD: Trampoline or iterative approach reduces stack depth
```

### 🔗 Related Keywords

- `Virtual Threads (Project Loom)` — the user-facing abstraction continuations enable.
- `Carrier Thread` — the OS thread that continuations are mounted onto/unmounted from.
- `Stack Frame` — the per-method data captured in a continuation snapshot.
- `Structured Concurrency` — the API built on top of virtual threads and continuations.
- `Heap Memory` — where frozen continuations reside between mount/unmount cycles.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Heap-stored snapshot of a virtual         │
│              │ thread's call stack; enables unmounting.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding virtual thread performance  │
│              │ and memory trade-offs; diagnosing heap    │
│              │ pressure from suspended VTs.              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Directly: never — it's an internal API.  │
│              │ Indirectly: avoid deep stacks on VTs.    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Continuation: the saved game that lets   │
│              │ a million players pause simultaneously."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Carrier Thread → Structured Concurrency   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A virtual thread executes a chain of 3 async-looking blocking calls, each nested 15 stack frames deep through middleware, filters, and interceptors before reaching an I/O call. Each blocking I/O completes in 10ms but unmount/remount happens 3 times per request. Estimate the total continuation size per request and explain whether the continuation overhead is significant compared to the I/O time — and at what stack depth it would become significant.

**Q2.** Continuations allow a virtual thread to resume on a different carrier thread than it ran on before. This creates an interesting problem for code that assumes thread identity is stable. Identify two specific real-world scenarios in Java libraries or frameworks where this "carrier thread switching" between unmount and remount cycles could cause correctness issues, even if no explicit carrier-thread-specific state is used.

