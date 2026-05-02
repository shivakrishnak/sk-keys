---
layout: default
title: "Write Barrier"
parent: "Java & JVM Internals"
nav_order: 309
permalink: /java/write-barrier/
number: "0309"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Heap Memory
  - Card Table
  - GC Roots
  - JIT Compiler
  - Safepoint
used_by:
  - Card Table
  - Remembered Set
  - G1GC
  - ZGC
  - Shenandoah GC
related:
  - Card Table
  - Remembered Set
  - Read Barrier
  - Memory Barrier
tags:
  - jvm
  - gc
  - memory
  - java-internals
  - deep-dive
---

# 0309 — Write Barrier

⚡ TL;DR — A write barrier is code inserted by the JVM around every object reference store that notifies the GC of the modification, enabling concurrent and incremental GC to maintain heap consistency without full STW pauses.

| #0309 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Heap Memory, Card Table, GC Roots, JIT Compiler, Safepoint | |
| **Used by:** | Card Table, Remembered Set, G1GC, ZGC, Shenandoah GC | |
| **Related:** | Card Table, Remembered Set, Read Barrier, Memory Barrier | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Generational and concurrent GCs need to track which parts of the heap change between GC cycles (for the card table) and which objects are modified during concurrent marking (for snapshot integrity). Without code that intercepts reference stores at the point they happen, the only alternative is a safepoint-based approach: stop all threads, scan the entire heap at once. But "stop everything to check the heap" is exactly what concurrent GCs exist to avoid.

THE BREAKING POINT:
G1GC concurrently marks live objects (no STW) across 1ms–100ms. During concurrent marking, application Thread A modifies a reference: `node.child = null` — pointing a previously-marked-live node's child to null. If G1GC doesn't see this change, it may promote a now-dead object (memory leak) or, worse, miss a live one. Without write barriers intercepting the store, G1GC cannot maintain snapshot consistency for its concurrent marking phase.

THE INVENTION MOMENT:
This is exactly why **Write Barriers** were created — to give the GC a hook at every reference store, allowing it to record metadata (dirty cards, pre/post values) needed for concurrent and incremental operation without requiring full STW pauses.

### 📘 Textbook Definition

A **write barrier** (in the GC context) is a small fragment of code inserted by the JVM/JIT at every reference field store instruction in compiled code. When an application thread stores a reference (`obj.field = value`), the write barrier executes immediately after (or before) the store, recording the store event in GC-specific data structures (card table, remembered set, SATB queue). Different GC algorithms use different barrier designs: **post-write barriers** (G1's card table marking: record after store), **pre-write barriers** (G1's SATB: record the overwritten value before it is lost), and **store barriers** (ZGC: color all references with GC state bits). Write barriers trade per-store overhead (~2–5 ns) for reduced GC pause time.

### ⏱️ Understand It in 30 Seconds

**One line:**
A tiny piece of code that piggybacks on every object reference assignment and quietly tells the GC "hey, this memory just changed."

**One analogy:**
> Imagine postal forwarding. When you move (change a reference), instead of just living at a new address, you also leave a forwarding notice with the post office (write barrier) so that anyone looking for you at the old address gets redirected. The post office (GC) can then find you without searching every possible address in the city.

**One insight:**
The write barrier is a tax on every reference store, paid up-front to avoid a much larger cost later (full STW scan). The critical question is whether the per-store tax is worth it for the GC algorithm using it. For concurrent GCs (G1, ZGC, Shenandoah), the answer is decisively yes: a 2ns per-store overhead avoids multi-hundred-millisecond STW pauses. For Serial GC (no concurrent marking), keeping a card table write barrier adds 1–3% throughput overhead for limited benefit.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. GC algorithms make assumptions about heap state that can be violated by running applications.
2. Every reference store is a potential violation point — the exact moment a GC invariant might be broken.
3. Write barriers intercept violations at their source rather than discovering them retroactively.

DERIVED DESIGN:
Different GC invariants require different barrier types:

**Type 1 — Post-write barrier (card table):**
Used by: all generational GCs.
Purpose: track Old→Young reference creation.
Trigger: after any reference store to an Old Gen object.
Action: mark the corresponding card table entry dirty.

**Type 2 — Pre-write barrier (SATB — Snapshot At The Beginning):**
Used by: G1GC concurrent marking.
Purpose: preserve the "snapshot" of the heap at marking start.
Trigger: before any reference store (capture the overwritten value).
Action: if overwritten value is non-null and GC is marking: enqueue overwritten ref in SATB buffer.

**Type 3 — Load/Store barrier with coloring:**
Used by: ZGC, Shenandoah.
Purpose: maintain colored reference invariants for relocating GC.
Trigger: on every reference load AND store.
Action: check/update color bits embedded in reference pointers.

```
┌─────────────────────────────────────────────────┐
│     Write Barrier Types and Their Actions       │
│                                                 │
│  Pre-write (SATB):                              │
│    [save: old_ref = obj.field]                  │
│    [if marking → enqueue(old_ref)]              │
│    obj.field = new_ref                          │
│                                                 │
│  Post-write (card table):                       │
│    obj.field = new_ref                          │
│    [card_table[addr_of(obj.field) >> 9] = dirty]│
│                                                 │
│  Load barrier (ZGC):                            │
│    ref = obj.field                              │
│    [if ref.color != good → fixup(ref)]          │
│    use ref                                      │
└─────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Concurrent/incremental GC possible; shorter STW pauses; O(modified objects) work per GC vs O(heap size).
Cost: 2–5ns overhead per reference store; JIT code size increases for each store (barrier instructions); complex interaction with JIT optimization (stores must not be reordered past barriers).

### 🧪 Thought Experiment

SETUP:
G1GC is concurrently marking the heap. It has already analyzed and determined: object `A` is live, and `A.child = B`. Therefore `B` is also live (reachable from A). Marking completed for this sub-graph.

WITHOUT PRE-WRITE BARRIER (SATB):
Application thread executes: `A.child = null`. G1GC continues marking but never revisits A (already marked). It proceeds with the snapshot from before the store. The snapshot said `A.child = B`, so B was already marked live. No problem yet — actually this is fine because B was already marked before the store.

CORRECT CASE (the real problem):
Object `C` is live (reachable from another root). Thread does: `D.ref = C; A.child = C`. D is not yet marked by G1GC. Now: `A.child = null`. G1GC marks A and finds `A.child = null` — correctly. But C was only reachable via `D.ref`, and D is not yet scanned. If the SATB barrier didn't enqueue the old value of A.child (C) before it was overwritten, and if D.ref is also later overwritten before marking: C gets missed. C is freed despite being live immediately before the store. Dangling reference! Memory corruption.

WITH SATB PRE-WRITE BARRIER:
Before `A.child = null` executes: barrier fires, enqueues the old value (C) into the SATB buffer. G1GC processes the SATB buffer, re-marks C as live regardless of what A.child now says. C is never freed incorrectly.

THE INSIGHT:
SATB's pre-write barrier records the "facts of the old world" before the application destroys them. This is the GC equivalent of a database transaction log — record before you overwrite, so you can reconstruct state if needed.

### 🧠 Mental Model / Analogy

> A write barrier is like a building's change management system. Every time someone moves furniture (modifies a reference), they fill out a short form: "room 42, moved sofa from position A to position B." The facilities manager (GC) can review this log to understand exactly what has changed without walking every room. Different facilities teams keep different logs: "where did new furniture come from?" (SATB) vs "which rooms were recently modified?" (card table) — each serving different maintenance needs.

"Moving furniture" → reference field store.
"Filling out a form" → write barrier code execution.
"Facilities manager reviewing log" → GC processing barrier records.
"Which rooms modified?" → card table tracking for Minor GC.
"Where did furniture come from?" → SATB pre-barrier for concurrent marking.

Where this analogy breaks down: Unlike a paper form system, write barriers are inserted in compiled machine code and execute in 2–5ns — much faster than any paper form could be processed.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every time Java code changes what object a variable points to, a tiny extra piece of code runs automatically and lets the garbage collector know about the change. This tiny code is the write barrier — it's automatic and invisible to the programmer.

**Level 2 — How to use it (junior developer):**
Write barriers are entirely automatic and invisible. You cannot add or remove them directly. Indirectly: reducing the rate of reference stores in Old Gen objects reduces write barrier overhead. Using primitive arrays instead of object arrays, and using immutable objects in long-lived data structures, reduces write barrier frequency.

**Level 3 — How it works (mid-level engineer):**
The JIT inserts write barrier code around every reference store bytecode (`putfield`, `aastore`, etc.). For G1GC, this is:
1. Pre-write: `if (concurrent_marking && old_value != null) enqueue(old_value)`.
2. Actual store: `obj.field = new_value`.
3. Post-write: `if (old_gen_object) card_table[addr >> 9] = dirty`.

The JIT optimizes these barriers: null checks are hoisted; conditions on GC state are converted to hot/cold paths; the barrier code is placed in the "unlikely" path if possible. Modern JITs emit tight barriers of ~3–5 instructions for the common case.

**Level 4 — Why it was designed this way (senior/staff):**
ZGC's load barrier is architecturally different and arguably more elegant: instead of a write barrier (recording every store), ZGC uses a **load barrier** (checking every reference load). This works because ZGC is a fully concurrent relocating GC: objects may move during application execution. When a thread loads a reference, the load barrier checks if the reference is "colored" (pointing to an old location that has been relocated). If so, it fixes up the reference to the new location — transparently, at load time. This converts the "store-time tracking" model to a "load-time healing" model. The advantage: fewer stores happen than loads in reference-heavy code (reads vastly outnumber writes), but ZGC's critical property is that the barrier runs only where needed (on "bad colored" references) — making the average overhead close to zero when relocated objects are rarely accessed.

### ⚙️ How It Works (Mechanism)

**G1GC Write Barrier (JIT generated, x86-64):**
```asm
; obj.field = new_value  (putfield bytecode)

; --- PRE-WRITE (SATB) ---
; Read old value first:
mov  rax, [rdi + field_offset]    ; old_value = obj.field
; Check if we need to log it:
test rax, rax                     ; old_value != null?
jz   .no_satb_log
cmp  byte ptr [satb_mark_queue_active], 0  ; marking?
jz   .no_satb_log
call satb_log_barrier             ; enqueue old_value
.no_satb_log:

; --- ACTUAL STORE ---
mov  [rdi + field_offset], rsi    ; obj.field = new_value

; --- POST-WRITE (CARD TABLE) ---
; Check if obj is in Old Gen:
mov  rax, rdi
shr  rax, 9                       ; card index
movzx rdx, byte ptr [cardtable + rax]  ; read current card byte
test rdx, rdx                     ; already dirty?
jnz  .card_clean                  ; skip if dirty
mov  byte ptr [cardtable + rax], 0xFF   ; mark dirty
.card_clean:
; Total barrier: ~8 additional instructions for "hot path"
```

**ZGC Store Barrier (conceptual):**
ZGC's barrier is simpler for stores but more complex for loads:
```asm
; Load: value = obj.field
mov  rax, [rdi + field_offset]    ; load reference
test rax, COLOR_BITS_MASK         ; is it "bad" (needs fixup)?
jnz  slow_path_fixup              ; rare: fix and update
; fast path: use rax directly (almost always taken)
```

**Barrier Optimization by JIT:**
```java
// JIT can optimize: "common subexpression" barriers
// If multiple stores to the same object in same region:
// only one card mark needed (JIT deduplicates)
obj.fieldA = x;  // barrier: mark card
obj.fieldB = y;  // barrier: card already dirty, skip
// JIT detects same card, eliminates second dirty mark
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (G1GC):
```
[Application: obj.child = newValue]
    → [Pre-write barrier: enqueue old child ref to SATB]
    → [Actual store: obj.child = newValue]
    → [Post-write barrier: card_table[...] = dirty]  ← YOU ARE HERE
    → [Concurrent refinement: processes dirty card]
    → [Minor/G1 GC: uses pre-cleaned dirty cards + SATB buffer]
    → [Correct liveness: no objects missed, no premature collection]
```

FAILURE PATH (design error — missing barrier):
```
[JNI native code: writes reference directly without JNI APIs]
    → [No write barrier executes]
    → [Card NOT marked dirty, SATB NOT updated]
    → [GC misses the Old→Young or concurrent marking update]
    → [Memory corruption or incorrect liveness decision]
(This is why JNI must use JNI reference APIs, not direct writes)
```

WHAT CHANGES AT SCALE:
At 500 million reference stores per second (write-heavy caching service), write barrier overhead at 3ns/store = 1.5 seconds/second of write barrier CPU — 100% CPU. This drives the design of write-barrier-free algorithms in HPC Java (using primitive arrays, off-heap buffers, or Unsafe). For most services, reference store rates are 10–50 million/second, where 30–150ms/second overhead is 3–15% of CPU — acceptable for the GC benefits provided.

### 💻 Code Example

Example 1 — Measuring write barrier overhead:
```java
// JMH benchmark to measure write barrier cost:
@Benchmark
@BenchmarkMode(Mode.Throughput)
public void referenceStore(BenchmarkState s) {
    // Each iteration: one reference store → one write barrier
    s.holder.ref = s.someObject;
}
// Typical result: 50M–200M stores/sec on modern JVM
// Compare with: primitive store (no barrier):
@Benchmark
public void primitiveStore(BenchmarkState s) {
    s.holder.intField = 42;  // no write barrier
}
// Typically 3–5x faster than reference store
```

Example 2 — Reducing write barrier overhead with primitive arrays:
```java
// BAD: Array of objects → barriers for every element set
Object[] refArray = new Object[1_000_000];
for (int i = 0; i < 1_000_000; i++) {
    refArray[i] = createObject(i);  // 1M write barriers
}

// GOOD: Use primitive arrays where possible (no barriers):
int[] primitiveArray = new int[1_000_000];
for (int i = 0; i < 1_000_000; i++) {
    primitiveArray[i] = computeValue(i);  // 0 write barriers
}
// Or use ByteBuffer / off-heap for reference-heavy data:
// ArrowBuffer, Chronicle Map, etc.
```

Example 3 — G1GC vs ZGC barrier overhead comparison:
```bash
# Measure write barrier overhead difference:
# G1GC (pre+post write barriers):
java -XX:+UseG1GC -jar barrier-bench.jar ReferenceStoreBenchmark

# ZGC (load barriers only):
java -XX:+UseZGC -jar barrier-bench.jar ReferenceStoreBenchmark

# Expected: ZGC stores ~5-15% faster (fewer write barrier ops)
# but ZGC loads may be 5-10% slower (load barriers)
```

Example 4 — JFR monitoring write barrier activity:
```bash
java -XX:StartFlightRecording=duration=60s,\
  filename=barriers.jfr,settings=profile MyApp

# In JMC: Memory → G1 Card Table Events
# Shows: dirty card creation rate, SATB buffer usage
# High SATB buffer rate → lots of pre-write barrier activity
```

### ⚖️ Comparison Table

| GC Algorithm | Write Barrier Type | Barrier Cost | Purpose |
|---|---|---|---|
| **Serial / Parallel GC** | Post (card table only) | ~1-2 instructions | Generational ref tracking |
| **G1GC** | Pre (SATB) + Post (card) | ~5-8 instructions | Concurrent marking + generational |
| **ZGC** | None (uses load barrier) | Store: minimal | Load-time relocation fixup |
| **Shenandoah** | Pre (SATB) + fwd pointer | ~4-6 instructions | Concurrent marking + compaction |
| **Epsilon GC** | Post (card only) | ~1-2 instructions | No actual collection |

How to choose: GC algorithm determines write barrier type. If write-heavy workload is the throughput bottleneck, ZGC's store-barrier-free approach may improve throughput. Test with JMH under realistic load.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Write barriers are the same as `volatile` memory barriers | GC write barriers are code inserted by the JVM/JIT to notify the GC; `volatile` memory barriers enforce CPU instruction ordering. They are completely different concepts that happen to share the word "barrier" |
| Write barriers only matter for GC | Write barriers are a GC concept. However, "read barriers" and "store barriers" in the concurrent memory model (CPU/JMM context) are a different concept — hardware memory ordering instructions |
| Disabling write barriers would speed up Java by 3-5% | While true in theory, disabling write barriers would break concurrent GC algorithms. Serial GC (which doesn't need SATB) still needs card table barriers for generational correctness. Only fully conservative GC or ref-counting could work without them |
| Write barriers are inserted only for field stores | Barriers are inserted for all reference stores: object field stores (`putfield`), array element stores (`aastore`), and `putStatic`. Each is handled |
| JIT can eliminate all write barriers in JIT-optimized hot paths | JIT can eliminate redundant barriers (e.g., same card already dirty) but cannot eliminate barriers entirely from reference stores to Old Gen objects. The barrier is a correctness requirement, not optional |
| ZGC's load barrier is more expensive than G1's write barrier | For stores: ZGC has no write barrier. For loads: ZGC's load barrier is ~2-3 instructions on the "good" fast path — comparable to G1's write barrier cost. ZGC trades write overhead for load overhead |

### 🚨 Failure Modes & Diagnosis

**GC Pause Spike from SATB Buffer Overflow**

Symptom:
G1GC concurrent marking phase occasionally causes long pauses that don't match expected GC patterns. GC logs show "SATB queue overflow" warnings.

Root Cause:
Application writes references at a rate exceeding the SATB buffer's capacity. Buffers overflow → GC must process them during STW rather than concurrently.

Diagnostic Command / Tool:
```bash
java -Xlog:gc+marking=debug MyApp 2>&1 | grep "SATB"
# Look for "SATB buffer overflow" or high SATB queue counts
```

Fix:
```bash
# Increase SATB buffer size:
java -XX:G1SATBBufferEnqueueingThresholdPercent=90 \
     -XX:G1SATBBufferSize=4096 MyApp
# Or reduce write frequency in hot paths
```

Prevention:
Load test with write-heavy scenarios. Monitor SATB buffer utilization via JFR.

---

**Write Barrier Missing in JNI Code (Correctness Bug)**

Symptom:
Intermittent NullPointerExceptions, object corruption, or SIGSEGV in JNI-heavy applications. Problem disappears on Serial GC but appears with G1 or concurrent GC.

Root Cause:
JNI native code modifies Java object reference fields directly via `env->SetObjectField()` using pointer arithmetic instead of proper JNI APIs. No write barrier is executed. Card table not marked, SATB not updated.

Diagnostic Command / Tool:
```bash
# Enable strict JNI checking:
java -Xcheck:jni MyApp
# Flags improper JNI field access patterns
```

Fix:
All JNI reference field writes MUST use `env->SetObjectField()`, `env->SetObjectArrayElement()`, etc. — never raw pointer writes to Java heap memory.

Prevention:
Code review all JNI code for direct heap pointer manipulation. Run all JNI code with `-Xcheck:jni` in CI.

---

**High Write Barrier CPU Overhead in Write-Intensive Service**

Symptom:
CPU profiling shows 15–20% of CPU time in GC write barrier stubs. Service processes reference-store-heavy workloads (e.g., building object graphs at high rate).

Root Cause:
Very high reference store rate (>500M/sec) → write barrier overhead becomes significant CPU fraction.

Diagnostic Command / Tool:
```bash
# Async-profiler CPU profile:
./profiler.sh -e cpu -d 30 -f output.html <pid>
# Look for "BarrierStub", "G1WriteBarrier", or "ZGC store barrier"
# in the flame graph hot section
```

Fix:
Options by priority:
1. Replace object arrays with primitive arrays where possible.
2. Use off-heap memory (ByteBuffer, Arena allocator) for hot-path data structures.
3. Switch to ZGC (no write barriers on stores).
4. Use Unsafe for read-only graphs that never update references after construction.

Prevention:
Performance test write-intensive code paths with realistic allocation patterns. Profile barrier overhead explicitly.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Card Table` — the primary data structure that post-write barriers update; understanding card table is prerequisite to understanding the write barrier's purpose
- `GC Roots` — write barriers complement GC root tracking; both provide the GC its view of live objects
- `JIT Compiler` — write barriers are inserted by the JIT into compiled code; understanding JIT shows where barriers live in the execution pipeline

**Builds On This (learn these next):**
- `Remembered Set` — G1GC's Remembered Set uses write barriers to track cross-region references; RSet is the next level of write barrier application
- `G1GC` — the GC algorithm that uses both pre and post write barriers most prominently
- `ZGC` — uses load barriers (not write barriers) for relocation; important contrast to understand barrier design trade-offs

**Alternatives / Comparisons:**
- `Memory Barrier` — hardware instruction for CPU memory ordering; completely different from GC write barriers despite the name
- `Card Table` — the data structure the write barrier updates; the two are inseparable

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Code inserted at every reference store    │
│              │ that notifies the GC of heap changes      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Concurrent GC cannot track heap changes   │
│ SOLVES       │ without intercepting reference stores     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Two types exist: pre-write (SATB: save     │
│              │ old value before overwrite) and post-write│
│              │ (card table: mark region as modified).    │
│              │ ZGC uses load barriers (no write barrier) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic — inserted by JIT for all GCs   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cannot avoid; reduce stores to primitive  │
│              │ arrays / off-heap to reduce barrier rate  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ ~3ns per reference store vs concurrent GC │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A mandatory change-log entry for every   │
│              │  reference move the GC might need to see" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Remembered Set → G1GC → ZGC               │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** ZGC replaces write barriers with load barriers for its relocation-based design. Shenandoah uses both a write barrier (for SATB concurrent marking) AND a "forwarding pointer" mechanism (for concurrent compaction). Explain the architectural reason Shenandoah needs two separate barrier types while ZGC achieves single-barrier design — and what specific property of ZGC's region layout eliminates the need for a write barrier during concurrent compaction.

**Q2.** A Java service processes financial transactions where each transaction creates a directed acyclic graph of 50 immutable `TransactionNode` objects. Once created, the graph is never modified — nodes are read but no reference fields are written. Given this usage pattern, analyze: How many write barriers execute per transaction graph? What percentage of the write barrier overhead comes from construction vs. post-construction? And propose a concrete memory layout optimization that would eliminate post-construction write barriers for these graphs while maintaining full GC safety.

