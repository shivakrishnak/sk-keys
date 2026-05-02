---
layout: default
title: "OSR (On-Stack Replacement)"
parent: "Java & JVM Internals"
nav_order: 302
permalink: /java/osr-on-stack-replacement/
number: "0302"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JIT Compiler, Tiered Compilation, Deoptimization
used_by: GraalVM, Tiered Compilation
related: Deoptimization, Method Inlining, Tiered Compilation
tags:
  - java
  - jvm
  - internals
  - performance
  - deep-dive
---

# 302 — OSR (On-Stack Replacement)

⚡ TL;DR — OSR lets the JVM swap a currently-running interpreted method for its freshly compiled native version mid-execution, without waiting for the method to return.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #302 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JIT Compiler, Tiered Compilation, │ │
│ │ Deoptimization │ │
│ Used by: │ GraalVM, Tiered Compilation │ │
│ Related: │ Deoptimization, Method Inlining, │ │
│ │ Tiered Compilation │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Normal JIT compilation only kicks in when a method is called the next time after
being compiled. But what about a method that's currently running — one that has
been executing for 10 minutes inside a massive loop? Without OSR, you'd have to
wait for the method to exit and be called again before the JIT could provide any
benefit. A long-running computation is stuck in the interpreter for its entire
duration, even if the JIT completed compilation halfway through.

**THE BREAKING POINT:**
A batch job method runs a loop processing 100 million records. It takes 20 minutes.
The JIT hits the compilation threshold after 1 minute of interpreted execution.
Without OSR, the remaining 19 minutes run interpreted at 10% of potential speed.
The batch job could take 3 minutes optimal — instead it takes 20 minutes because
the JIT optimization never arrives.

**THE INVENTION MOMENT:**
This is exactly why **OSR (On-Stack Replacement)** was created: compile the
method while it's running, then hot-swap the interpreter frame for the native
frame at the next loop back-edge, without returning from the method.

---

### 📘 Textbook Definition

On-Stack Replacement (OSR) is a JVM mechanism that transfers execution from an
interpreter-mode stack frame to a JIT-compiled native stack frame (or vice versa)
while the method is actively executing. OSR is triggered at loop back-edges when
the JVM detects that the currently-executing method's back-edge counter crosses
the compilation threshold. The JIT compiles an OSR-specific variant of the method
that begins execution at the detected loop back-edge (not at the method entry),
and the interpreter's frame state is transferred to the new native frame in-place.
Deoptimization is the reverse operation — native frame to interpreter frame.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OSR swaps a running method from "slow" to "fast" mode mid-execution without stopping.

**One analogy:**

> Imagine changing a car's tires while it's driving down the highway. Instead
> of pulling over (returning from the method, waiting for the next call),
> a pit crew runs alongside and swaps tires at 60 mph. The car never stops.
> It accelerates immediately.

**One insight:**
OSR solves the "warm-up gap" for long-running methods. Regular JIT only benefits
the next call. OSR benefits the current call. This is especially critical for
scientific computing, batch processing, and any code with tight long-running loops.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Long-running methods with heavy loops cross the compilation threshold mid-execution.
2. Normal JIT compilation benefits only future calls, not the current running frame.
3. The interpreter and native code have fundamentally different stack frame layouts.
4. A safe state transfer must preserve: local variables, operand stack, program counter.

**DERIVED DESIGN:**
For OSR to work, the JIT must:

1. Detect the OSR trigger: back-edge counter in the currently-executing method reaches threshold.
2. Compile an OSR-entry variant of the method that starts execution inside the loop body,
   not at method entry (since we're already past method entry).
3. Build an OSR entry point with the correct register/stack layout to receive
   the state transferred from the interpreter frame.
4. At the next loop back-edge, the interpreter checks whether an OSR entry exists:
   if yes, transfer state → jump to compiled loop body.

**The key challenge**: the interpreter frame layout (a software stack of slot values)
must be accurately translated to the native frame layout (registers + native stack).
The JIT must produce both a "normal entry" (for future calls) and an "OSR entry"
(for the current in-progress execution).

**THE TRADE-OFFS:**

- Gain: long-running methods get JIT benefits mid-execution, not just on next call.
- Cost: OSR entrypoints are more complex to generate (start mid-method; unusual).
- Cost: OSR-compiled code is sometimes less optimized than a fully JIT-compiled entry
  because the JIT starts with less context about the loop's starting state.
- Gain: eliminates the "cold loop" problem that makes JIT ineffective for batch workloads.

---

### 🧪 Thought Experiment

**SETUP:**
A method `void processBatch(int[] data)` iterates over an array of 50 million
elements. Each iteration does a small calculation. The method is called once.
The compilation threshold is 10,000.

**WHAT HAPPENS WITHOUT OSR:**
After 10,000 iterations, the JIT notices the back-edge counter is high and compiles
the method. But the method is currently running. Normal JIT waits for the method
to return — then uses the compiled version for the next call. But this method
is called once. It processes all 50 million elements in the interpreter.
JIT compilation was wasted effort.

**WHAT HAPPENS WITH OSR:**
After 10,000 iterations, the JIT detects the back-edge threshold and triggers
OSR compilation. While the interpreter handles calls 10,001–15,000, C2 compiles
an OSR entry point for the loop. At iteration 15,001, the interpreter checks:
"OSR entry available?" Yes. Transfer: local variable `data` (array ref), loop index
`i = 15001`, any other locals → transferred to native frame. Execution resumes
in native code at iteration 15,001. Remaining 49,985,000 iterations run at full
native speed.

**THE INSIGHT:**
OSR closes the gap between "JIT compiled" and "JIT effective." The optimization
benefit doesn't require a future call — it arrives in the middle of the current one.

---

### 🧠 Mental Model / Analogy

> OSR is like upgrading your web browser while a video is streaming. Instead
> of stopping the video, downloading the update, then restarting — the browser
> hot-patches itself while the video plays. At the next "safe frame boundary"
> (loop back-edge), the new code takes over seamlessly.

- "Video streaming" → long-running method executing in interpreter
- "Browser update downloading" → JIT compiling the method in background
- "Safe frame boundary" → loop back-edge (a natural checkpoint)
- "Hot-patch takes over" → interpreter frame replaced with native frame
- "Seamless continuation" → execution resumes without returning from method

**Where this analogy breaks down:** A browser update usually improves the same
behavior. OSR changes the execution engine (interpreter → JIT) which can sometimes
cause subtle differences in behavior on edge cases — though the JVM guarantees
correctness at all times.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
If Java code is currently running in a long loop, OSR lets the faster compiled
version kick in while the loop is still going — no need to wait for the
method to finish and restart.

**Level 2 — How to use it (junior developer):**
OSR is automatic. You'll see it in `-XX:+PrintCompilation` output as methods
marked with `%` — the percent sign indicates an OSR compilation. OSR is triggered
by back-edge counts (loop iterations), not method call counts. No configuration
needed; OSR fires whenever a loop crosses the back-edge threshold.

**Level 3 — How it works (mid-level engineer):**
The interpreter executes a special back-edge counter bump at every loop iteration.
When this counter + invocation counter exceeds the OSR threshold
(`OnStackReplacePercentage` × `CompileThreshold`, default ~14,000), the interpreter
calls into the JVM runtime to request an OSR compilation. The C1/C2 compiler
generates an OSR-specific entry point — a variant that begins execution in the
middle of the method, initializing the native frame from the passed-in interpreter
state. At the next back-edge check, if the OSR entry is ready, the interpreter
copies its state into a buffer and jumps to the OSR entry.

**Level 4 — Why it was designed this way (senior/staff):**
OSR compilation is architecturally different from normal JIT compilation: the
OSR entry point must accept state from the interpreter's slot model (every local
is a tagged value at a known slot index) and map it to whatever register allocation
the native code uses. This is the "impossible problem" — the native code has
allocated local variables to registers optimally, but the interpreter state
hands values by index. OSR must bridge this semantic gap. As a result, OSR-compiled
code is sometimes less optimized than normal JIT code: the compiler cannot make
certain optimizations that require knowing the values at loop entry. This is an
acceptable trade-off — OSR code is still 5–10× faster than interpreter, just not
the theoretical maximum.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│         OSR — ON-STACK REPLACEMENT FLOW                 │
├─────────────────────────────────────────────────────────┤
│  Method starts running in interpreter                   │
│                    ↓                                    │
│  Loop iteration N: back_edge_counter++                  │
│  if (counter > OSR_threshold) {                         │
│      Request OSR compilation (async)                    │
│  }                                                      │
│                    ↓                                    │
│  JIT compiles OSR entry in background                   │
│  (while interpreter continues running)                  │
│                    ↓                                    │
│  At next back-edge: is OSR entry ready?                 │
│  YES:                                                   │
│    1. Pack interpreter state into OSR buffer:           │
│       - All local variables (by slot index)             │
│       - Operand stack contents                          │
│       - Lock set (held monitors)                        │
│    2. Call OSR entry with buffer                        │
│    3. Native code unpacks buffer → registers            │
│    4. Execution resumes in native code at loop body     │
│                    ↓                                    │
│  Method continues in native code until return          │
│  Future calls use normal JIT entry (not OSR entry)     │
│                                                         │
│  % mark in PrintCompilation = OSR compilation          │
└─────────────────────────────────────────────────────────┘
```

The `%` marker in compilation output:

```
  892   47 %  com.Batch::process @ 42 (150 bytes)
              ^                    ^
              OSR marker           bytecode offset of loop back-edge
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌───────────────────────────────────────────────────────────┐
│         OSR IN THE TIERED COMPILATION PICTURE             │
├───────────────────────────────────────────────────────────┤
│  [Method enters] → [Interpreter runs]                     │
│       ↓ back-edge counter crosses threshold               │
│  [OSR compilation requested]                              │
│  ← YOU ARE HERE (compilation in background)               │
│       ↓ compilation complete                              │
│  [State transfer at next back-edge]                       │
│  ← YOU ARE HERE (hot-swap happens)                        │
│       ↓                                                   │
│  [Native OSR code runs rest of method]                    │
│       ↓ method returns                                    │
│  [Normal JIT entry exists for future calls]               │
└───────────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
OSR compilation fails → method stays in interpreter for entire duration →
`PrintCompilation` shows no `%` entries for the method → batch job runs slow →
observable via `jcmd <pid> Compiler.queue` showing method repeatedly queuing.

**WHAT CHANGES AT SCALE:**
At scale, OSR is less critical — server applications hit methods via many short
calls (OSR not needed). OSR matters most for: batch jobs, scientific computing,
test runners, and any scenario with long single-threaded computation in tight loops.

---

### 💻 Code Example

```java
// Example 1 — Observe OSR activation
// Run: java -XX:+PrintCompilation LongLoop
public class LongLoop {
    public static long sum(int n) {
        long s = 0;
        for (int i = 0; i < n; i++) {
            s += i; // back-edge triggers OSR
        }
        return s;
    }
    public static void main(String[] args) {
        // Single call — relies on OSR for JIT benefit
        System.out.println(sum(100_000_000));
    }
}
// PrintCompilation output:
//  234   42 %  LongLoop::sum @ 8 (25 bytes)
// The % = OSR; 8 = bytecode offset of back-edge
```

```java
// Example 2 — OSR vs normal JIT comparison
// Normal JIT: called many times → JIT kicks in on future calls
for (int call = 0; call < 100_000; call++) {
    shortMethod(call);  // after 10k calls, future calls are JIT
}

// OSR: called once with large loop → JIT kicks in mid-execution
longLoopMethod(1_000_000);  // OSR triggers inside the loop
```

```java
// Example 3 — OSR timing observation
public static void main(String[] args) throws Exception {
    long start = System.nanoTime();
    long result = 0;
    for (int i = 0; i < 100_000_000; i++) {
        result += i;
        // Observe: speed changes WITHIN this loop
        // First 15k iterations: ~10ns each (interpreter)
        // After OSR: ~0.5ns each (native)
        // You can measure by sampling nanoTime inside loop
        if (i % 1_000_000 == 0) {
            long now = System.nanoTime();
            System.out.printf(
                "i=%,d elapsed=%dms%n",
                i, (now-start)/1_000_000
            );
        }
    }
}
// Look for sudden throughput increase in the output
// corresponding to OSR activation
```

---

### ⚖️ Comparison Table

| Mechanism         | When Activated           | Direction            | Scope                    | Best For                         |
| ----------------- | ------------------------ | -------------------- | ------------------------ | -------------------------------- |
| **OSR**           | Loop back-edge threshold | Interpreter → Native | Current method mid-run   | Long single-call methods         |
| Normal JIT        | Method call threshold    | Interpreter → Native | Next method call         | Short, frequently-called methods |
| Deoptimization    | Guard failure            | Native → Interpreter | Current method mid-run   | Correcting wrong speculation     |
| Class loading JIT | New class loaded         | Triggers recompile   | Methods using that class | Stable class hierarchy           |

**How to choose:** These operate automatically. OSR matters when you have
computationally-intensive single-call methods. Benchmark before assuming
OSR is a bottleneck — for server apps, normal JIT handles most heat.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                             |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| OSR and normal JIT produce identical code           | OSR-compiled code starts mid-loop; the compiler has less context at loop entry — output is slightly less optimized  |
| The `%` in PrintCompilation means a problem         | `%` is a normal, expected marker indicating an OSR compilation; it's a positive sign that JIT is helping long loops |
| OSR requires the method to be called multiple times | OSR is triggered by back-edge (loop iteration) counts, not call counts — it activates even for single-call methods  |
| OSR is only relevant for micro-benchmarks           | OSR is critical for batch processing, ETL jobs, and any server code with large per-request loops                    |
| After OSR, the method is permanently native         | OSR code runs for the current method activation; if the method is later deoptimized, the OS version reverts too     |

---

### 🚨 Failure Modes & Diagnosis

**OSR Not Triggering for Long Loops**

Symptom:
Batch job runs at consistently low throughput. PrintCompilation shows no `%`
entries for the main processing loop. CPU is spent in interpreter overhead.

Root Cause:
Loop counter arithmetic may overflow or be reset, preventing threshold crossing.
Or the threshold `OnStackReplacePercentage` × `CompileThreshold` is too high.

Diagnostic Command / Tool:

```bash
java -XX:+PrintCompilation -XX:+TraceOSR LongBatch 2>&1 \
  | grep -E "[%]|OSR"
# No % entries = OSR not triggering
# Check effective threshold:
java -XX:+PrintFlagsFinal -version | grep -E \
  "(OnStackReplace|CompileThreshold)"
```

Fix:

```bash
# Lower OSR threshold (default: CompileThreshold * 1.4)
-XX:OnStackReplacePercentage=140  # reduce to trigger sooner
# Or lower overall threshold:
-XX:CompileThreshold=5000
```

Prevention:
Profile batch jobs specifically for OSR activity, not just method-call-based JIT.

---

**OSR Code Less Optimized Than Expected**

Symptom:
A method is OSR-compiled (`%` appears in PrintCompilation), but throughput
is only 3× interpreter speed instead of the expected 10×.

Root Cause:
OSR entry at a loop back-edge prevents the compiler from knowing initial
values of loop variables — constant folding and invariant hoisting are blocked.

Diagnostic Command / Tool:

```bash
# Compare OSR vs normal JIT performance:
# 1. Run with single call (OSR): time vs
# 2. Run with many small calls (normal JIT):
#    wrap loop in outer for-loop, call inner method
java -XX:+PrintCompilation -XX:+PrintInlining App 2>&1 \
  | grep -E "(% |inline)" | head -20
```

Fix:
Refactor: extract the loop body into a separately-called method. Now the
outer loop triggers normal JIT (via back-edge), and the inner method gets
full optimization with clean entry state.

Prevention:
For performance-critical batch code, benchmark both OSR and
refactored-to-multiple-calls patterns.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JIT Compiler` — OSR is a JIT mechanism; requires understanding JIT basics
- `Tiered Compilation` — OSR is part of the tiered execution system
- `Deoptimization` — the inverse operation to OSR (native → interpreter)

**Builds On This (learn these next):**

- `Safepoint` — OSR state transfer happens at safepoints (loop back-edges are safepoints)
- `GraalVM` — GraalVM implements its own OSR mechanism

**Alternatives / Comparisons:**

- `Deoptimization` — OSR and deoptimization are exact inverses; deopt is native→interpreter, OSR is interpreter→native
- `Method Inlining` — peer JIT optimization; inlining is about call sites, OSR is about loop execution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mid-execution swap: interpreter → native   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Long-running methods get no JIT benefit    │
│ SOLVES       │ without needing the method to return first │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ OSR triggers on loop back-edges, not       │
│              │ method calls — activated by loop iteration │
│              │ count, not call count                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic — critical for batch jobs and    │
│              │ compute-heavy single-call methods          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — automatic; observe with %PrintComp. │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ OSR code slightly less optimal than normal │
│              │ JIT but far better than interpreter        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JIT for the race already in progress"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Safepoint → Deoptimization → GraalVM       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data pipeline method processes 1 billion rows in a single call.
Due to OSR limitations, the JIT cannot fully optimize the loop entry state.
You refactor the method to call a small inner method for each row instead.
Normal JIT now applies fully. Walk through the exact trade-offs: What do you
gain in optimization quality? What do you lose in method call overhead?
At what row count does the refactoring become a net win?

**Q2.** OSR and Deoptimization are described as inverse operations — one
promotes (interpreter → native), one demotes (native → interpreter).
Both operate at safepoints. Given that they share safepoint infrastructure,
could a method theoretically oscillate between the two states repeatedly?
Under what production conditions would you observe this, and what would
the performance signature look like on a latency histogram?
