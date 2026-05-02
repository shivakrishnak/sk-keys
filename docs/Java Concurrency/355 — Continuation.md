---
layout: default
title: "Continuation"
parent: "Java Concurrency"
nav_order: 355
permalink: /java-concurrency/continuation/
number: "0355"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads (Project Loom), Carrier Thread, ForkJoinPool
used_by: Virtual Threads (Project Loom), Structured Concurrency
related: Virtual Threads (Project Loom), Carrier Thread
tags:
  - java
  - concurrency
  - virtual-threads
  - deep-dive
  - internals
---

# 0355 — Continuation

⚡ TL;DR — A continuation is a snapshot of a thread's call stack and execution state saved to the heap — the internal mechanism enabling virtual thread **unmount**: when a virtual thread blocks, its entire call stack is serialised as a continuation on the heap, freeing the carrier thread to run other work.

| #0355 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Virtual Threads (Project Loom), Carrier Thread, ForkJoinPool | |
| **Used by:** | Virtual Threads (Project Loom), Structured Concurrency | |
| **Related:** | Virtual Threads (Project Loom), Carrier Thread | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A blocking call (e.g., `socket.read()`) blocks the OS thread it runs on — the entire thread context (stack, registers, local variables) is held on the OS thread's stack. To "pause" a thread without blocking the OS thread, the thread's state must be saved somewhere else so the OS thread is free to run other code.

THE INVENTION MOMENT:
**Continuations** solve this by capturing the live execution state (call stack frames + local variables) on the heap, decoupled from any OS thread. When the blocking operation completes, the continuation is restored onto an OS thread to resume execution — as if the blocking call returned normally.

### 📘 Textbook Definition

A **continuation** is the captured execution state of a computation that can be suspended and resumed at a later point. In Java's Project Loom, continuations are implemented via `java.lang.Continuation` (JVM internal, not public API) — a heap-allocated object that stores the virtual thread's call stack as a linked list of `StackChunk` objects. When a virtual thread is unmounted (on blocking), its continuation is saved to heap. When rescheduled, the continuation is "yielded" back onto a carrier thread's stack, restoring all local variables and the exact program counter.

### ⏱️ Understand It in 30 Seconds

**One line:**
A continuation is a "saved game state" for a thread — pause at any point, save to heap, resume later exactly where you left off.

**One analogy:**
> A continuation is a detailed bookmark in a complex choose-your-own-adventure book. Not just the page number, but also every choice you made that got you there (call stack), every character's current status (local variables), and the exact sentence you were reading (program counter). When you close the book (unmount), all context is preserved. When you open it again (remount), you continue from the exact same point.

**One insight:**
Continuations make Java virtual threads fundamentally different from async/await (C#, JavaScript). In async/await, the developer manually "segments" code at `await` points. In Java, continuations make ANY synchronous blocking code "continuable" — the programmer writes blocking code and the JVM handles the save/restore transparently.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A continuation captures the ENTIRE call stack — not just a callback, but all nested method frames.
2. Continuations are heap objects — they can be GC'd like any other object when no longer needed.
3. Continuation yielding is controlled by the `Continuation.scope` — only the virtual thread scheduler yields continuations (not arbitrary user code).

**Internal structure:**
```
StackChunk (heap object):
  - size: bytes of stack data
  - parent: pointer to next chunk (linked list)
  - data: actual stack frame bytes (local vars, return addresses)

VirtualThread.continuation:
  - stack: linked list of StackChunks
  - stackPointer: where to resume
  - instructionPointer: program counter at yield point
```

**Continuation lifecycle:**
```
Platform stack (carrier):
  [virtual_thread_run()]
    → [userCode.processOrder()]
      → [socket.read()] ← yield point
```

On unmount: JVM copies platform stack frames from `virtual_thread_run` to `socket.read()` into heap-allocated StackChunks. Linked list is stored in `VirtualThread.continuation`.

On remount: JVM copies continuation back onto carrier's platform stack. Instruction pointer restores to `socket.read()` return site. All local variables in all frames are restored.

THE TRADE-OFFS:
Gain: Transparent blocking code; no callback/async rewriting; natural sequential code style; efficient heap storage for inactive VTs.
Cost: Shallow vs deep stack matters — very deep call stacks mean larger continuation objects; StackChunk copying has overhead; native frames cannot be captured (causes pinning); debugging continuation stack traces requires tools support.

### 🧪 Thought Experiment

SETUP: What does a 5-frame continuation look like?

```java
// Call stack when socket.read() blocks:
main()
  → handleRequest()
    → OrderService.process()
      → UserRepository.findById()
        → DatabaseConnection.execute()
          → socket.read() ← BLOCKS HERE
```

WITHOUT CONTINUATIONS:
The OS thread's stack (6 frames) is frozen. The OS thread cannot run other code. 10,000 requests = 10,000 frozen OS threads.

WITH CONTINUATIONS:
The 6 stack frames are copied to heap-allocated StackChunks (each ~a few KB). The OS carrier thread's stack is freed — it can now run VT "order-2"'s stack. When socket.read() completes: 6 frames are copied back from heap to carrier stack. Execution resumes at `execute()` return, unwinds normally through all frames.

THE INSIGHT:
The continuation copy cost is ~1-2μs (typically much less). The benefit is freeing an OS thread worth of stack (~1MB) and context-switching cost. For 10,000 concurrent I/O-bound operations, the tradeoff is enormously positive.

### 🧠 Mental Model / Analogy

> A continuation is like a detailed pause state in a video game's quick-save slot. Not just level + health, but exact position, all inventory, every NPC's state at this exact second, cursor position. When you resume (load), everything is exactly as you left it — no information lost. The game can run other saves (other VTs) while yours is paused.

"Pause state in quick-save slot" → continuation on heap.
"Running other saves" → carrier mounting other VTs.
"Loading and resuming" → remounting continuation.

Where this analogy breaks down: Video game saves capture everything statically. Continuations capture stack frames which can contain object references into shared heap state — those objects may change while the continuation is suspended (correct concurrency semantics still apply when resumed).

### 📶 Gradual Depth — Four Levels

**Level 1:** A continuation is "pause a thread completely, save it, resume later" — letting the OS thread go do other work.

**Level 2:** Developers don't interact with continuations directly. They are the internal mechanism for virtual thread unmount/mount. Understanding continuations helps explain why: (1) deeply recursive code creates larger continuations; (2) native methods pin (can't be serialised to heap); (3) virtual threads can't cross native frame boundaries.

**Level 3:** The JVM uses `StackChunk` objects linked in a chain. When a virtual thread is unmounted, the interpreter walks the stack frames from the carrier's current execution point back to the virtual thread's entry frame, copying all interpreter frames into `StackChunk` objects. Compiled (JIT) frames require deoptimisation first — the JIT output is discarded and interpreted frames are saved. This is one reason blocking in hot loops (JIT-compiled code) has slightly higher overhead for the first unmount.

**Level 4:** Continuations in Java Loom are **delimited continuations**: only the frames from the virtual thread's run frame to the yield point are saved — not the entire call stack of the carrier thread (which may include other completely unrelated work). This is why native frames pin: the JVM can't save native stack frames into a Java heap object — they contain C/C++ ABI frame layouts that the JVM cannot portably serialize.

### ⚙️ How It Works (Mechanism)

**Observing continuations via JFR:**
```bash
# JFR captures virtual thread lifecycle events:
jcmd <pid> JFR.start name=vt_trace duration=60s \
  settings=default filename=vt_trace.jfr

jfr print --events jdk.VirtualThreadStart,\
    jdk.VirtualThreadEnd,jdk.VirtualThreadPinned,\
    jdk.VirtualThreadSubmitFailed \
    vt_trace.jfr | head -100
```

**Stack depth affects continuation size:**
```java
// Shallow call stack = small continuation:
void shallow() { socket.read(); } // 2 frames saved

// Deep call stack = larger continuation:
void level1() { level2(); }
void level2() { level3(); }
// ... 
void level100() { socket.read(); } // 101 frames saved
// Larger continuation = more heap, more copy cost
// Not a problem in practice (<1MB per continuation typically)
```

**Why native methods pin:**
```java
// Native frame cannot be saved to heap:
native void nativeOperation(); // C code, Java can't serialize frames

void callerFromJava() {
    nativeOperation(); // can this carry on a VT? No.
    // If nativeOperation() blocks: carrier PINNED
}

// Detection:
// java -Djdk.tracePinnedThreads=full MyApp
// Will show: "pinned at nativeOperation (native method)"
```

### 🔄 The Complete Picture — End-to-End Flow

```
[VT "order-5" calls socket.read() — blocking op]
    → [JVM: detect blocking → initiate yield]     ← YOU ARE HERE
    → [Continuation: copy stack frames to StackChunks on heap]
    → [VT "order-5" continuation stored in heap]
    → [Carrier FJWorker-2: UNMOUNTED "order-5", now IDLE]
    → [FJPool: schedule VT "order-6" on FJWorker-2]
    → [NIO: data arrives for "order-5"]
    → [JVM: schedule VT "order-5" on FJPool]
    → [FJWorker-2: when free, MOUNT "order-5"]
    → [Continuation: copy StackChunks back to carrier stack]
    → [socket.read() returns data — VT continues]
```

### 💻 Code Example

```java
// Public Continuation API (preview/internal — not production use):
// In application code, you use virtual threads; continuations are internal

// Creating a virtual thread that uses continuations under the hood:
Runnable task = () -> {
    // Stack frame 1: task lambda
    doLevel1Work();
};

Thread vt = Thread.ofVirtual().start(task);
// JVM manages continuation internally when vt blocks

// The developer's code looks exactly like blocking:
void doLevel1Work() {
    // Stack frame 2
    String data = fetchFromDatabase(); // blocks → continuation saved
    process(data); // resumes after continuation restored
}
```

### ⚖️ Comparison Table

| Concurrency Model | Stack Storage | Developer Code | Blocking | Language |
|---|---|---|---|---|
| Platform threads | OS stack (1MB per) | Blocking OK | Blocks OS thread | Java (pre-21) |
| **Continuations (VT)** | Heap (dynamic size) | Blocking OK | Unmounts carrier | Java 21+ |
| Async/await | No full stack | Must use async | Callbacks | C#, JS |
| Coroutines | Coroutine stack (heap) | `suspend fun` required | Suspending | Kotlin |
| Green threads | Heap | Blocking OK | JVM-managed | Early Java, Go |

How to choose: Virtual threads (continuations) give Java the simplicity of synchronous code with coroutine-level scalability — no async/await syntax needed.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Continuations are a public Java API | `java.lang.Continuation` is JVM-internal and not public API (as of Java 21). Developers use virtual threads which use continuations under the hood. A limited experiment API may be available in future previews |
| Continuations incur full OS context-switch cost | Continuations use heap copies + ForkJoinPool scheduling (~1-5μs). OS context switches include register saving, TLB flush, kernel/user mode transition (~10-20μs). Continuations are faster |
| Every virtual thread always uses a continuation | A continuation is created only when a virtual thread actually blocks. VTs that complete without blocking never create a continuation |
| Deep call stacks break virtual threads | Deep stacks create larger continuations but don't break correctness. The JVM handles stack expansion transparently. Very deep recursion still causes StackOverflow (but the limit is higher for VTs — configurable) |

### 🚨 Failure Modes & Diagnosis

**Native frame pinning (continuation cannot be created):**
```bash
# -Djdk.tracePinnedThreads=full output:
# Thread[#45,ForkJoinPool-1-worker-2,5,CarrierThreads]
#  at com.example.NativeWrapper.callNative (NativeWrapper.java:20)
#  <== pinned (native frame)
```
Fix: Move native calls outside of VT I/O paths where possible.

**Large continuation memory pressure:**
Symptom: Heap grows despite JVM GC activity. Millions of VTs with deep call stacks.

Diagnostic:
```bash
jmap -dump:live,format=b,file=heap.hprof <pid>
# Eclipse MAT: search for StackChunk objects
# StackChunk[] with large aggregate size = deep VT stacks in use
```

Fix: Reduce call stack depth for VT-heavy paths. Avoid deeply nested framework calls in high-VT-concurrency code.

### 🔗 Related Keywords

**Prerequisites:** `Virtual Threads (Project Loom)`, `Carrier Thread`, `ForkJoinPool`
**Builds on:** `Structured Concurrency` (uses VTs + continuations)
**Related:** `Carrier Thread`, `Virtual Threads (Project Loom)`

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Heap-stored call stack snapshot — the     │
│              │ mechanism enabling VT unmount/remount     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Native frames cannot be saved → pin.      │
│              │ Deep stacks = larger heap continuation.   │
│              │ Not a public API — internal VT mechanism  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Thread's call stack saved to heap so the │
│              │  OS thread can go do other work"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Structured Concurrency → Scoped Values    │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** When a virtual thread's continuation is stored on the heap and the VT is unmounted, the continuation holds references to all local variables in all stack frames — including object references. Explain why a virtual thread that holds a database `Connection` object in a local variable while waiting for a query result (another I/O) means the `Connection` is kept alive on the heap (through the continuation) during the wait, why this is not a memory leak but correct expected behaviour, and what specific scenario WOULD be a memory leak involving continuations and object references.

