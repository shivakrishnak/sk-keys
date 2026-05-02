---
layout: default
title: "OSR (On-Stack Replacement)"
parent: "Java & JVM Internals"
nav_order: 302
permalink: /java/osr-on-stack-replacement/
number: "0302"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JIT Compiler
  - C1 / C2 Compiler
  - Tiered Compilation
  - Deoptimization
  - Stack Frame
used_by:
  - GC Tuning
  - Deoptimization
related:
  - Deoptimization
  - Method Inlining
  - Tiered Compilation
  - Safepoint
tags:
  - jvm
  - jit
  - performance
  - java-internals
  - deep-dive
---

# 0302 — OSR (On-Stack Replacement)

⚡ TL;DR — OSR lets the JVM replace a currently-running method's interpreter frame with compiled native code mid-execution, so long-running loops get JIT benefits without waiting for the next invocation.

| #0302 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JIT Compiler, C1 / C2 Compiler, Tiered Compilation, Deoptimization, Stack Frame | |
| **Used by:** | GC Tuning, Deoptimization | |
| **Related:** | Deoptimization, Method Inlining, Tiered Compilation, Safepoint | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Normal JIT compilation triggers when a method is *invoked* enough times. But what about a method called only once that runs a loop for 60 seconds? The method is only invoked once — it never crosses the invocation count threshold. Without OSR, this loop runs interpreted for its entire lifetime. Real-world examples: a startup-time data loading loop, a background batch processing loop, a long-lived event processing loop.

THE BREAKING POINT:
A data migration job loads 50 million records in a single loop: `for (int i = 0; i < 50_000_000; i++) { process(records[i]); }`. This loop runs for 3 minutes. Without OSR, the loop executes in the interpreter for all 3 minutes — 10x slower than it could be. The job takes 30 minutes instead of 3.

THE INVENTION MOMENT:
This is exactly why **On-Stack Replacement (OSR)** was created — to allow the JVM to JIT-compile a method *while it is currently executing* on the stack and switch execution to the compiled version mid-loop, without waiting for the method to return and be called again.

---

### 📘 Textbook Definition

**On-Stack Replacement (OSR)** is a JIT technique that transfers execution of a currently-active method from the interpreter to compiled native code (or vice versa) without waiting for the method to return. Upon detecting that a loop back-edge counter exceeds the OSR threshold (`Tier4BackEdgeThreshold`, default ~40,000), the JVM compiles the method with the loop body as the entry point, reconstructs the interpreter's state (local variables, operand stack values) into a format compatible with the compiled code, and replaces the interpreter stack frame with a compiled frame — while the method is running. OSR also works in reverse: if compiled code has an uncommon trap inside a loop, execution transfers back to the interpreter via a "reverse OSR" (deoptimization on-stack).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The JVM can swap out your slow-running loop's engine while it's still driving — like changing a car's engine while moving at 60 mph.

**One analogy:**
> Imagine a train running on steam power. The train operator notices the same 50-mile stretch of track is used daily. Without stopping the train, workers upgrade the track section to magnetic levitation. When the train next hits that section, it smoothly transitions from steam to maglev at full speed, and finishes the journey much faster without ever stopping. OSR is this mid-journey engine swap for Java loops.

**One insight:**
OSR closes the gap between "invoked many times" JIT optimization and "long single invocation" scenarios. Without OSR, JIT would be useless for batch processing, startup-time initialization, and any long-running computation that's structured as a single method call. OSR is what makes JIT useful for the full spectrum of Java workloads.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. JIT compilation is triggered by invocation counts — but a method only called once never crosses that threshold.
2. Loops are the primary performance hotspot in long-running single-method executions.
3. The optimizer can only work on code it has already compiled — it cannot optimize interpreter frames in flight.

DERIVED DESIGN:
OSR uses a separate counter: the **backedge counter**, incremented at every loop back-edge (the backward jump at the end of each loop iteration). When this counter crosses `Tier4BackEdgeThreshold`, the JVM triggers OSR compilation.

OSR compilation has a non-obvious challenge: the *entry point* of the compiled method cannot be the method's normal entry. It must be the *middle of the loop* — at the exact back-edge position where OSR is triggered. This means the compiled code must expect the interpreter's live state as input: local variable values, partial computation results.

```
┌──────────────────────────────────────────────────┐
│         OSR State Transfer                        │
│                                                  │
│  Interpreter frame during loop iteration:        │
│  [local0=obj] [local1=idx] [local2=sum]          │
│  bytecode_pc = 237 (back-edge)                   │
│                                                  │
│  OSR Buffer created:                             │
│  locals[] = {obj, 42000, 1234567}                │
│  bytecode_pc = 237 → compiled_entry_point        │
│                                                  │
│  Compiled frame installed:                       │
│  register EBX = 42000  (local1)                  │
│  register ECX = 1234567 (local2)                │
│  Jump to compiled loop body                      │
└──────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Long-running loops benefit from JIT compilation even when the method is only called once; startup tasks and batch jobs run at near-native speed.
Cost: OSR-compiled code is typically slightly less optimized than normally-compiled code (special entry point constraints limit some optimizations, particularly around variables live across the back-edge); OSR transitions have a one-time overhead for state transfer; method must be re-profiled on next normal invocation.

---

### 🧪 Thought Experiment

SETUP:
A Java main method loads a 100GB dataset: the entire computation is in a single `for` loop iterating 1 billion times. The method is called exactly once in the program's lifetime.

WITHOUT OSR:
Backedge counter hits 40,000 iterations — OSR threshold reached. But there is no OSR. The loop continues interpreted for the remaining 999,960,000 iterations. Each iteration: ~200ns (interpreted). Total: ~200 seconds.

WITH OSR:
At iteration 40,000 (backedge count threshold), the JVM submits the loop for OSR compilation on a background thread. Compilation takes 200ms. Meanwhile, iterations 40,000–80,000 run interpreted. At iteration ~80,000: compiled OSR code is ready. JVM pauses at the next back-edge to perform state transfer (20µs). Loop continues in compiled code. Each compiled iteration: ~10ns. Remaining 999,920,000 iterations: ~10 seconds. Total including warmup: ~11 seconds vs ~200 seconds.

THE INSIGHT:
OSR's 200ms compilation and 20µs transfer overhead is invisible against the 189 seconds of savings. Even with marginal overhead at the OSR entry point vs. normally-compiled code, the benefit is enormous for long-running loops.

---

### 🧠 Mental Model / Analogy

> imagine a factory assembly line running in manual mode (workers doing each step by hand). A factory manager observes that a certain section of the line is used intensely. While the line keeps running, the manager installs automated machines alongside the manual workers. At the right moment, the manager taps the next worker on the shoulder, tells them to stand aside, and the automated machine seamlessly takes over their station — the product never stops moving on the conveyor belt.

"Manual workers" → interpreter executing bytecode.
"Factory manager observing" → JVM backedge counter monitoring.
"Installing automated machines" → JIT compiling the loop in background.
"Tapping on the shoulder" → OSR state transfer at a back-edge.
"Automated machine takes over" → compiled code resumes the loop.

Where this analogy breaks down: Unlike the factory where the product is physical, the JVM must precisely reconstruct the exact processor state from the interpreter frame into the compiled frame's expected format — a precision requirement the factory analogy doesn't capture.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a loop is running for a long time in slow mode, the JVM can switch it to fast mode in the middle of running — without restarting the loop or losing any progress. It's like upgrading your computer's processor while it's still computing.

**Level 2 — How to use it (junior developer):**
OSR is automatic. You benefit from it in scenarios with long-running initialization loops, batch-processing loops, or single-method data transformation jobs. Be aware: if you write JMH benchmarks with very short warmup iteration counts, your first few iterations may include an OSR transition — use adequate `@Warmup(iterations=5)` to let OSR settle before measuring.

**Level 3 — How it works (mid-level engineer):**
The interpreter increments `BackedgeCounter` at every loop back-edge. When it exceeds `Tier4BackEdgeThreshold` (default 40,000), the JVM triggers OSR compilation for this specific loop. Compilation produces a method with a special **OSR entry point** at the back-edge. An **OSR nmethod** is created alongside (not replacing) the normal method entry. When compilation completes, the next time the interpreter hits that back-edge, it calls `uncommon_trap` which initiates the OSR state transfer, creates the compiled frame, and resumes in compiled code.

**Level 4 — Why it was designed this way (senior/staff):**
The OSR entry point constraint creates a subtle limitation: variables that are live across the OSR entry point cannot be as aggressively optimized as variables that are first created inside the compiled code. Specifically, objects that were allocated by the interpreter before OSR transition are "already escaping" from the optimizer's perspective — they exist on the heap already, so the optimizer cannot fold them to the stack even if their scope is local. This is why OSR-compiled code is sometimes measurably slower than the same code compiled normally (from method entry). For extreme performance, rewrite the problematic loop as a separate method called many times rather than one long-running method — this enables normal compilation instead of OSR.

---

### ⚙️ How It Works (Mechanism)

**Backedge Counter:**
The interpreter maintains per-method counters. At every loop back-edge (backward `goto` bytecode), the interpreter:
1. Increments `BackedgeCounter`.
2. Periodically checks if `BackedgeCounter + InvocationCounter > CompileThreshold`.
3. If threshold met, calls `CompilationPolicy::method_back_edge_event()`.

**OSR Compilation Request:**
A special compilation request is submitted: "compile method X with OSR entry at bytecode offset Y". The background JIT thread compiles a variant of the method where the loop's back-edge is the entry point. The compiled code accepts the interpreter's live state as initial parameters.

**State Transfer at Back-Edge:**
```
[Interpreter running iteration 40000]
    → [Back-edge reached: compiled OSR code ready?]
    → [YES: generate OSR buffer from live locals]
    → [Bundle: locals[], bytecode_pc, klass_id]
    → [Call into osr_migration_end stub]
    → [Stub: construct compiled frame from buffer]
    → [Resume execution at OSR compiled entry point]
    → [Compiled code takes over the loop]
```

**PrintCompilation Output (OSR marker `%`):**
```
185  47 %  4 com.example.Loader::loadData @ 237 (120 bytes)
           ^                                  ^-- bytecode offset
           % = OSR compilation
```

The `%` marker in `-XX:+PrintCompilation` output identifies OSR compilations.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Method called once] → [Interpreter starts]
    → [Loop begins looping]
    → [BackedgeCounter++] (each iteration)
    → [Counter > Tier4BackEdgeThreshold = 40K]
    → [OSR compile request submitted] ← YOU ARE HERE
    → [Background JIT compiles loop with OSR entry]
    → [At next back-edge: state transfer]
    → [Compiled loop body executes]
    → [Remaining 999,960,000 iterations: fast]
```

FAILURE PATH:
```
[Compiled OSR code has uncommon trap inside loop]
    → [Trap fires mid-loop-execution]
    → [Reverse OSR (deoptimization OSR)]
    → [Reconstructs interpreter frame from compiled]
    → [Interpreter continues loop at same iteration]
    → [Performance penalty for that iteration]
    → [Re-profiling and re-compilation if frequent]
```

WHAT CHANGES AT SCALE:
In containerized batch jobs, OSR transitions can race with JVM process startup — if the container has a CPU limit of 0.5 cores, the JIT compilation (running in background) may stall, delaying OSR transition well beyond the 40,000-iteration mark. Monitor: OSR compilation delay (method stays flagged for compilation for many thousands of iterations) as a containerized performance issue distinct from bare-metal behavior.

---

### 💻 Code Example

Example 1 — Observing OSR in PrintCompilation:
```bash
java -XX:+PrintCompilation MyApp 2>&1 | grep "%"

# Output:
# 342   56 %   4  com.example.DataLoader::loadAllRecords
#                  @ 187 (245 bytes)
# The "@187" means OSR entry is at bytecode offset 187
# (the back-edge of the loop)
```

Example 2 — Code pattern that triggers OSR:
```java
// This loop triggers OSR — called once, runs long:
public void loadAllRecords() {
    for (int i = 0; i < 50_000_000; i++) {
        records[i] = repository.load(ids[i]); // hot callsite
    }
    // Method only called ONCE — normal JIT never triggers
    // BackedgeCounter hits 40K → OSR compiles loop entry
}
```

Example 3 — Re-writing to favor normal JIT over OSR:
```java
// Re-written as two methods — inner loop called many times:
public void loadAllRecords() {
    loadChunk(records, ids, 0, ids.length);
}

// BETTER: called via loop in caller — crosses invocation threshold
// JIT compiles normally (not OSR) for potentially better optimization
private void loadChunk(Record[] records, long[] ids,
                        int from, int to) {
    for (int i = from; i < to; i++) {
        records[i] = repository.load(ids[i]);
    }
}
// If the outer driver calls loadChunk in a batched loop:
// 50x calls of 1M records each → loadChunk gets normal JIT
```

Example 4 — Lowering OSR threshold for faster switching:
```bash
# Lower the backedge threshold for faster OSR triggering:
java -XX:Tier4BackEdgeThreshold=10000 MyApp

# Useful for:
# - Short-running batch jobs where default 40K is too slow
# - Benchmarks that need to confirm OSR is not affecting results

# WARNING: more aggressive compilation = more CPU during warmup
```

---

### ⚖️ Comparison Table

| Scenario | Normal JIT | OSR | Best Strategy |
|---|---|---|---|
| Method called 100K times | Normal JIT at ~10K invocations | N/A (not needed) | Normal JIT (default) |
| **Long loop, method called once** | Never — stays interpreted | OSR at 40K iterations | OSR (automatic) |
| Benchmark micro-loop | May OSR — skews results | OSR mid-benchmark | Separate batched calls |
| Startup loader method | Once — interpreter until OSR | OSR triggers loop JIT | OSR + readiness probe |
| AOT (GraalVM) | No JIT | No OSR needed | Native compilation |

How to choose: OSR is automatic and typically correct. For maximum JIT optimization of long loops, refactor them so the loop body is a short separate method called many times — normal JIT produces better code than OSR for such cases.

---

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────────────┐
│         OSR State Machine                        │
│                                                 │
│  [Method entry: Interpreter]                    │
│         │                                       │
│         ▼ (loop starts)                         │
│  [BackedgeCounter++]                            │
│         │ counter < threshold                   │
│         │ continue looping                      │
│         │ counter > threshold                   │
│         ▼                                       │
│  [Submit OSR compile request]                   │
│         │ (loop continues interpreted)           │
│         ▼ (compilation done)                    │
│  [At next back-edge: state transfer]            │
│         │                                       │
│         ▼                                       │
│  [Compiled loop running]                        │
│         │                                       │
│         │ uncommon trap? → reverse OSR          │
│         │ (back to interpreter)                 │
│         ▼ (loop end)                            │
│  [Normal return from compiled code]             │
└─────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OSR is just normal JIT triggered by loops | OSR is fundamentally different — it requires a special compiled entry point at the loop's back-edge, not the method entry. Normal JIT and OSR produce different code for the same method |
| OSR-compiled code is as fast as normally-compiled code | OSR code is often slightly slower because variables live across the OSR entry cannot be as deeply optimized (they escaped before OSR took over). Refactoring to normal JIT invocation can be faster |
| OSR is only triggered for `for` loops | OSR triggers for any looping construct that creates back-edges: `while`, `do-while`, and `for` loops all increment the backedge counter |
| The `%` marker in PrintCompilation means OSR is complete | The `%` marks when OSR compilation was submitted/completed — not when the transition actually happens. The transition occurs at the next back-edge after compilation is done |
| Lowering OSR threshold always helps performance | A lower threshold means less profiling data before compilation. C2 makes worse decisions with fewer backedge iterations of profiling data, potentially producing suboptimal OSR-compiled code |
| OSR is not needed in Java 21+ virtual threads | Virtual threads do not change the JIT model. A virtual thread running a long loop still benefits from (and relies on) OSR |

---

### 🚨 Failure Modes & Diagnosis

**OSR Compilation Not Triggered Despite Long Loop**

Symptom:
A batch job runs 10x slower than expected. Profiling shows time in interpreter. The single long loop has millions of iterations but no OSR compilation.

Root Cause:
CPU quota in container prevents JIT background threads from running. The OSR compile request is submitted but the JIT thread is starved, delaying compilation by minutes.

Diagnostic Command / Tool:
```bash
java -XX:+PrintCompilation 2>&1 | grep "%"
# If no % lines for the expected method, OSR didn't fire

# Check if JIT thread is running:
top -H -p <pid>
# Look for "C2 CompilerThread" — is it using CPU?
# If CPU throttled, the thread may not run
```

Fix:
Increase container CPU quota during initialization, or use multiple methods with invocation-based JIT.

Prevention:
Set appropriate CPU requests (not just limits) in Kubernetes Pod spec to ensure JIT threads can run.

---

**OSR Entry Prevents Escape Analysis Optimization**

Symptom:
A long-running loop creates objects inside it. Profiling shows heavy minor GC activity even though objects appear to be short-lived.

Root Cause:
Objects created by the interpreter before the OSR transition already exist on the heap. After OSR takes over, the compiled code cannot prove these pre-existing objects are local — they have already "escaped" to the heap, preventing stack allocation.

Diagnostic Command / Tool:
```bash
# See if escape analysis is working post-OSR:
java -XX:+PrintEscapeAnalysis \
     -XX:+DoEscapeAnalysis MyApp 2>&1 | \
  grep "escape\|osr"
```

Fix:
Refactor the loop to create fresh objects only within the compiled portion. Or structure as multiple small methods to use normal JIT (not OSR) compilation.

Prevention:
Benchmark-compare OSR vs batched-invocation approaches for GC-sensitive long-loop code.

---

**Reverse OSR Loop (Deoptimization Inside OSR Loop)**

Symptom:
Long batch loop starts fast (OSR compiled), then suddenly spikes to slow midway through.

Root Cause:
An uncommon trap fires inside the OSR-compiled loop. The JVM performs reverse OSR (deoptimization back to interpreter) for the remainder of the loop. In rare cases, the loop never re-optimizes if the trap condition is triggered repeatedly.

Diagnostic Command / Tool:
```bash
java -XX:+TraceDeoptimization 2>&1 | grep "osr"
# Shows OSR-specific deoptimization events
```

Fix:
Find the rarely-hit type/condition within the batch loop and either handle it before the loop or extract it into a separate non-OSR path.

Prevention:
Test batch jobs with data that includes edge-case records to expose OSR-invalidating types before production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JIT Compiler` — OSR is a JIT technique; understanding fundamental JIT operation is prerequisite
- `Deoptimization` — reverse OSR is deoptimization on-stack; the two are deeply related
- `Stack Frame` — OSR transfers a stack frame from interpreter format to compiled format; understanding frame structure is essential

**Builds On This (learn these next):**
- `Safepoint` — OSR state transfer happens at a safepoint (the back-edge is a safe polling point); understanding safepoints explains when OSR transitions can occur

**Alternatives / Comparisons:**
- `Method Inlining` — the complementary JIT optimization for hot code; together OSR and inlining cover the full case: frequently-invoked methods (inlining) and long single-invocation methods (OSR)
- `Tiered Compilation` — the framework in which OSR operates; OSR can occur at any tier transition, not just Tier 0→4

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mid-execution swap of interpreter frame   │
│              │ to compiled native code for hot loops     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Long loops called only once never cross   │
│ SOLVES       │ the invocation count JIT threshold        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ OSR entry point is at the loop back-edge  │
│              │ — not method entry — meaning compiler     │
│              │ inherits pre-existing interpreter state   │
│              │ with limited optimization scope           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic for long loops; tune threshold  │
│              │ for batch jobs needing fast warmup        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Max performance needed: refactor long     │
│              │ loops into batched method invocations     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Automatic JIT for long loops vs slightly  │
│              │ suboptimal code vs normal compilation     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The engine swap you don't feel while     │
│              │  the train keeps moving"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Safepoint → AOT → GraalVM                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data science team writes Java code that processes a NumPy-equivalent dataset in a single loop over 200 million rows, called exactly once. When they convert this to use virtual threads instead of the main thread for parallelism across 8 threads, each processing 25 million rows, does OSR still apply? If yes, describe how OSR interacts with the virtual thread model — specifically what happens to the OSR state transfer when a virtual thread is unmounted and remounted on different carrier threads during the loop execution.

**Q2.** OSR-compiled code has a special entry point at the loop back-edge, and variables live across that entry inherit the interpreter's representation. Design a concrete microbenchmark test that would quantitatively measure the performance difference between an OSR-compiled loop and an equivalent normally-compiled loop (the same loop body in a method called 1 million times). What would the benchmark measure, what JVM flags would you need, and what result would you expect in terms of throughput difference and GC pressure?

