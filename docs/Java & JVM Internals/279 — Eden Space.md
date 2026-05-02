---
layout: default
title: "Eden Space"
parent: "Java & JVM Internals"
nav_order: 279
permalink: /java/eden-space/
number: "0279"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Young Generation, Heap Memory, TLAB, JVM
used_by: Minor GC, Survivor Space, Object Header
related: Young Generation, Survivor Space, TLAB, Minor GC
tags:
  - java
  - jvm
  - gc
  - memory
  - intermediate
---

# 279 — Eden Space

⚡ TL;DR — Eden Space is where every new Java object is born — a fast allocation arena that empties almost entirely at each Minor GC because most objects die without ever leaving it.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0279        │ Category: Java & JVM Internals       │ Difficulty: ★★☆          │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on:  │ Young Generation, Heap Memory,       │                          │
│              │ TLAB, JVM                            │                          │
│ Used by:     │ Minor GC, Survivor Space,            │                          │
│              │ Object Header                        │                          │
│ Related:     │ Young Generation, Survivor Space,    │                          │
│              │ TLAB, Minor GC                       │                          │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Object allocation requires finding free memory on the heap. In a general-purpose heap allocator (like C's `malloc`), finding free space means scanning a free list or using a buddy system, handling fragmentation, and acquiring locks for thread safety. In a multi-threaded Java application with thousands of objects per second, this lock contention and fragmentation management becomes a significant bottleneck.

THE BREAKING POINT:
High-throughput Java servers allocate millions of objects per second across dozens of threads. If each allocation requires a lock and a free-list scan, allocation becomes the bottleneck. The allocation mechanism must be O(1) and lock-free.

THE INVENTION MOMENT:
Eden Space enables pointer-bump allocation: all free space is at the end of the region, and allocating an object simply advances a pointer. Combined with Thread-Local Allocation Buffers (TLABs), this makes allocation lock-free and nearly as fast as stack allocation. This is why Eden Space exists as a dedicated, contiguous allocation region.

### 📘 Textbook Definition

Eden Space is the primary allocation region within the Young Generation where all new Java objects are created (unless they are "humongous" objects exceeding half the Eden size, which bypass to Old Generation or humongous regions). Allocation in Eden uses pointer-bump allocation within a Thread-Local Allocation Buffer (TLAB): each thread has a private slice of Eden, and allocation consists of advancing a pointer within that slice — no locks required. When Eden fills, a Minor GC is triggered. After Minor GC, Eden is emptied (reset to empty) and surviving objects are copied to one of the Survivor spaces.

### ⏱️ Understand It in 30 Seconds

**One line:**
Eden is where all Java objects start their lives — a fast, compact, nearly always empty region after each GC.

**One analogy:**
> Eden is like a dry-erase whiteboard in a classroom. Students (threads) write temporary notes on their designated corner (TLAB). When the board fills, everyone stops (Minor GC), only the important notes are transferred to a notebook (Survivor), and the entire board is erased instantly (Eden reset). New notes start fresh on the clean board.

**One insight:**
Eden's key property is that it is collected by ABANDONMENT, not by scanning dead objects. When Minor GC runs, only live objects are copied out. Eden (and the old Survivor) are then reset by simply moving a pointer — the "dead" objects in Eden are never visited by the GC. This is why Minor GC time is proportional to the number of surviving objects, not the total allocated volume.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. New objects must be allocated extremely fast (nanoseconds per object in hot paths).
2. Most new objects die before the next collection — the GC work for them should be zero.
3. Live survivors must be moved out to enable Eden reset.

DERIVED DESIGN:
Invariant 1 requires contiguous allocation (pointer bump), not free list scanning. TLABs give each thread a private segment, eliminating inter-thread contention during allocation. Invariant 2 justifies "collect by copying survivors": instead of marking dead objects, copy the few live ones and reset the region. Cost is proportional to live objects, not dead ones. Invariant 3 requires the copying mechanism (Survivor spaces) to have capacity for the surviving objects.

THE TRADE-OFFS:
Gain: Near-zero allocation cost per object; GC cost proportional to survivors (not garbage); no fragmentation in Eden.
Cost: Eden must be contiguous memory; the collecting node must stop-the-world to safely enumerate GC roots; TLABs waste some Eden space when threads get refilled (partial TLABs at GC time).

### 🧪 Thought Experiment

SETUP:
100 threads, each allocating 1000 objects per second. Without Eden/TLABs: each allocation acquires a global heap lock, finds a free block via free list, and returns a pointer.

WITHOUT EDEN/TLAB:
100 threads × 1000 alloc/sec = 100,000 allocations per second. Each acquires a lock. 100,000 lock acquisitions per second → lock contention is the bottleneck. At 50ns per lock acquisition: 5ms per second in locking overhead alone. Plus free-list scanning: O(fragments) per allocation.

WITH EDEN/TLAB:
Each of the 100 threads has its own TLAB in Eden (e.g., 256KB each). Within the TLAB, allocation = one pointer-bump instruction. No lock, no scan. 100,000 allocations per second × 2ns per allocation = 0.2ms total overhead. 25× faster than the lock-based approach. TLAB refill (acquire new Eden slice) occurs every ~1000 allocations per thread — rare, briefly requires a global lock.

THE INSIGHT:
TLABs eliminate allocation lock contention by giving each thread a private allocation area within Eden. Most allocations need zero synchronisation, making allocation effectively free in the steady state.

### 🧠 Mental Model / Analogy

> Eden is like the daily intake area of a sorting facility. Trucks (threads) unload packages (objects) at their own unloading bay (TLAB). At end of day (Minor GC), packages not claimed by anyone (unreachable objects) are discarded in bulk, and the bays are instantly reset to empty. A tiny fraction of packages are forwarded to long-term storage (Survivor → Old Gen). The intake area starts fresh every day.

"Unloading bay" → TLAB (thread-local slice of Eden)
"Packages being dumped on the bay" → object allocation via pointer-bump
"End of day bulk discard" → Minor GC absorbs all dead Eden objects
"Forwarded packages" → surviving objects copied to Survivor
"Bay reset" → Eden freed by pointer reset (no per-object cleanup)

Where this analogy breaks down: unlike a physical bay, Eden's "reset" doesn't sweep or clean — it just moves the allocation pointer back to the start. The old data remains in memory until overwritten by new allocations.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your Java program creates an object with `new`, the object starts life in a memory area called Eden Space. Eden is designed specifically for brand-new, short-lived objects — it can be allocated into extremely fast, and when it fills up, most of its contents have already been abandoned by your program and can be instantly reclaimed.

**Level 2 — How to use it (junior developer):**
Monitor Eden via `jstat -gc <pid>`: `EC` = Eden Capacity, `EU` = Eden Used. When `EU/EC` reaches ~95%, Minor GC is triggered. If Minor GC runs too frequently, Eden may be too small — increase with `-XX:NewSize`. If allocation is very high (streams, logging), consider object pooling or reducing transient object creation in hot paths.

**Level 3 — How it works (mid-level engineer):**
TLAB allocation: each thread has a start, end, and top pointer in its private Eden slice. `new Object()` → check `top + objectSize <= end`. If yes: write `top` to new object, advance `top`. If no: request new TLAB from Eden (requires atomic Eden pointer update, rare). When Eden itself fills: Minor GC, all TLABs retired and reset. Eden pointer moved to start. Copy survivors. New TLABs carved from the fresh Eden. Object header includes GC age (starts at 0 in Eden).

**Level 4 — Why it was designed this way (senior/staff):**
TLAB was introduced to solve the "allocation lock" problem: a single atomic CAS on the Eden allocation pointer serialises all threads. TLABs replace a per-allocation CAS with a per-TLAB CAS (one CAS per ~1000 allocations per thread). This is the "lock amortisation" technique: make the expensive operation rare by doing bulk work. The G1GC implementation further evolved this: Eden is no longer one contiguous region but a set of same-sized regions (e.g., 2MB each). When a thread needs a new TLAB region, an unused region is claimed atomically. This enables better NUMA memory placement (TLABs assigned to regions near the CPU's local NUMA node).

### ⚙️ How It Works (Mechanism)

**TLAB Allocation Flow:**

```
┌─────────────────────────────────────────────┐
│          TLAB ALLOCATION MECHANISM          │
├─────────────────────────────────────────────┤
│  Eden Space (contiguous memory)             │
│  ┌──────────────────────────────────────┐   │
│  │ Thread 1 TLAB                        │   │
│  │ [start════top→     end]              │   │
│  ├──────────────────────────────────────┤   │
│  │ Thread 2 TLAB                        │   │
│  │ [start═════════top→  end]            │   │
│  ├──────────────────────────────────────┤   │
│  │ Thread 3 TLAB                        │   │
│  │ [start═top→            end]          │   │
│  ├──────────────────────────────────────┤   │
│  │ [Available Eden: free for next TLAB] │   │
│  └──────────────────────────────────────┘   │
│  Eden top pointer (global; rarely updated)  │
└─────────────────────────────────────────────┘

Allocation in Thread 1:
  1. Check: top + size <= end?
     YES → write header at top, return top, top += size
  2. NO → refill: GC.allocTLAB(Thread1, size)
     → CAS Eden top pointer atomically (+TLAB_SIZE)
     → Thread1.tlab = {start=new, end=new+TLAB_SIZE}
     → Retry step 1 in new TLAB
```

**Eden Size Calculation:**
In ParallelGC:
```
Young Gen = Eden + S0 + S1
SurvivorRatio = Eden / S0 = Eden / S1 (default: 8)
So: Eden = Young * (8/10) = 80% of Young Gen
S0 = S1 = Young * (1/10) = 10% each
```

**Eden Reset After Minor GC:**
```
Before Minor GC:
  Eden: [AAABBBCCCDDDEEE...] (mix of live + dead objects)
  S0 (active):  [FFGGG] (survivors from last GC)
  S1 (empty):   []

After Minor GC:
  Eden: [] (pointer reset to Eden start — no cleanup!)
  S0 (was active): [] (pointer reset) 
  S1 (new active): [BBBFFFGGGAge++] (copied live objects)
  Old Gen: [promoted objects from this GC]
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Application threads allocate objects via 'new'
  → Thread checks TLAB top pointer ← YOU ARE HERE
  → If TLAB has space: pointer bump (2-3 CPU instructions)
  → Object header written, reference returned
  → ...filling Eden gradually...
  → Eden fills (EU ≈ EC)
  → Minor GC triggered: stop-the-world
  → All TLAB pointers reset
  → Live objects from Eden/S0 copied to S1
  → Eden top pointer reset to Eden start
  → Threads resume with fresh TLABs
```

FAILURE PATH:
```
Object too large for TLAB / Eden
  (size > threshold, typically Eden/2)
  → Bypasses Eden entirely
  → Allocated directly in Old Generation
    (or humongous region in G1)
  → Old Gen fills faster
  → Major GC triggered sooner
  → Observable: large objects in Old Gen histogram
```

WHAT CHANGES AT SCALE:
At 1,000 concurrent threads with aggressive allocation, the frequency of TLAB refills increases proportionally. Each refill requires an atomic operation on the Eden allocation pointer. At extreme thread counts (hundreds), refill contention can become measurable. G1GC addresses this with region-level TLAB allocation — each thread gets an entire region (1–32 MB), drastically reducing refill frequency.

### 💻 Code Example

Example 1 — Observe TLAB statistics:
```bash
# Log TLAB allocation events
java -Xlog:gc+tlab=debug -jar myapp.jar \
  2>&1 | grep "TLAB" | head -20
# Output shows per-thread TLAB: size, refills, waste

# Or: jstat shows aggregate Eden allocation rate
jstat -gc <pid> 1000
# Compare EU (Eden Used) changes per second = alloc rate
```

Example 2 — Tune TLAB size:
```bash
# Default TLAB size is adaptive (~1% of Eden / thread)
# For very small objects:
java -XX:TLABSize=64k -jar myapp.jar
# For large batch allocations (fewer refills):
java -XX:TLABSize=512k -jar myapp.jar
# -XX:+PrintTLAB for per-thread TLAB output
```

Example 3 — Avoid bypassing Eden (reduce large object allocations):
```java
// BAD: allocates large array bypassing Eden
byte[] buffer = new byte[10_000_000]; // ~10MB

// GOOD: use existing buffer (pool it)
// BAD pattern repeated in a loop
for (int i = 0; i < n; i++) {
    byte[] buffer = new byte[10_000_000]; // OOM risk!
    process(buffer);
}

// GOOD: reuse buffer (stays in Eden or Old Gen once)
byte[] buffer = new byte[10_000_000];
for (int i = 0; i < n; i++) {
    Arrays.fill(buffer, (byte) 0); // reuse, don't reallocate
    process(buffer);
}
```

Example 4 — Monitor Eden fill rate to size Eden correctly:
```bash
# Compute Eden fill rate:
# Eden fill rate = (EU_after - EU_before) / interval
jstat -gcutil <pid> 1000 | awk '{print $3}' | \
  awk 'NR>1{print $0-prev; prev=$0}1{prev=$0}'
# If Eden fills >100% per second: consider larger Eden

# G1GC: no explicit Eden sizing needed
# Just set MaxGCPauseMillis and let G1 adapt
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -jar myapp.jar
```

### ⚖️ Comparison Table

| Allocation Region | Allocation Speed | Thread Safety | Fragmentation | Contiguous? |
|---|---|---|---|---|
| **Eden (TLAB)** | O(1) pointer bump | Lock-free (per thread) | None | Yes (per TLAB) |
| Old Generation | O(1) region bump (G1) | CAS per region | Managed | No (regions) |
| Off-heap | Depends on allocator | Depends | Possible | Configurable |
| Stack Frame | O(1) pointer bump | None (private) | None | Yes |

How to choose: No choice needed — all `new` allocations go to Eden via TLAB automatically. The choice is whether to reduce allocations (object pooling) or tune TLAB/Eden size for your workload's allocation rate.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Every new object allocation requires a lock" | TLAB allocation is lock-free — just a pointer bump in thread-local memory. Only TLAB refill (rare) requires atomic Eden pointer update. |
| "Dead objects in Eden are actively freed" | Dead objects are never touched — Eden is reset by moving the allocation pointer. The dead objects' memory is simply overwritten by future allocations. |
| "Eden is half the heap" | Eden is typically ~80% of the Young Generation, which itself is 25–33% of the heap. So Eden is about 20–26% of total heap. Exact %s vary by GC and configuration. |
| "Large objects go through Eden" | Objects larger than half the Eden size or TLAB size bypass Eden and go directly to Old Generation (or G1 humongous regions). |

### 🚨 Failure Modes & Diagnosis

**1. Eden Too Small → Excessive Minor GC**

Symptom: `jstat` shows `YGC` count increasing every second; application latency spikes periodically every few hundred milliseconds.

Root Cause: Allocation rate exceeds Eden capacity → Eden fills and triggers Minor GC too frequently.

Diagnostic:
```bash
jstat -gcutil <pid> 500
# If E% (Eden utilization) regularly hits 100%
# in <500ms → Eden too small for allocation rate

# Compute allocation rate
jstat -gc <pid> 1000 | awk '{
  if(NR>1) printf("Alloc %.2fMB/s\n", ($7-prev)/1024)
  prev=$7
}'
```

Prevention: Increase Young Gen size; use G1GC with `MaxGCPauseMillis` for adaptive sizing.

**2. Large Object Allocation Pressure on Old Gen**

Symptom: Old Generation fills faster than expected; heap dump shows large arrays in Old Gen; no corresponding cache growth.

Root Cause: Application allocates large objects (>Eden/2) bypassing Eden — going directly to Old Gen, increasing major GC frequency.

Diagnostic:
```bash
jcmd <pid> GC.class_histogram | grep "\[B\|byte\[\]"
# "\[B" = byte arrays (often the large allocators)
# Large count or total size → excessive large alloc

java -Xlog:gc+humongous=debug -jar myapp.jar
# G1GC log for humongous allocation events
```

Prevention: Reuse large buffers (pool `ByteBuffer`); serialize to pre-allocated streams; avoid large arrays in request processing paths.

**3. TLAB Waste from Thread Exit**

Symptom: Eden utilisation jumps irregularly; `jstat` shows unexpectedly high Eden allocation but low actual object count.

Root Cause: Threads that exit before their TLAB is full leave unused TLAB space as "waste." In high thread churn applications (thread-per-request, unbounded thread pools), this can be significant.

Diagnostic:
```bash
java -Xlog:gc+tlab=debug -jar myapp.jar 2>&1 | \
  grep "tlab retired"
# Output shows per-thread TLAB waste on retirement
```

Prevention: Use thread pools with bounded, long-lived threads; virtual threads (Java 21) use smaller TLABs, reducing waste per virtual thread.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Young Generation` — Eden is the largest subspace of the Young Generation
- `Heap Memory` — Eden is part of the Java heap
- `TLAB` — the per-thread allocation mechanism that makes Eden allocation lock-free

**Builds On This (learn these next):**
- `Survivor Space` — the destination for objects that survive Eden's Minor GC
- `Minor GC` — the collection cycle that processes Eden and resets it
- `Object Header` — written at object creation in Eden; contains initial age (0) and Mark Word

**Alternatives / Comparisons:**
- `Survivor Space` — Eden's sibling in Young Generation; objects "graduate" from Eden to Survivor
- `Old Generation` — bypass destination for large objects that cannot fit in Eden

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Primary allocation area in Young Gen;     │
│              │ where all new Java objects are created    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Object allocation needs to be fast and    │
│ SOLVES       │ lock-free for high-throughput services    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Eden is collected by ABANDONMENT: dead    │
│              │ objects are never touched — Eden reset    │
│              │ by pointer move; GC cost = live objects   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every new object starts here.    │
│              │ Tune size if Minor GC too frequent        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Allocating byte[>Eden/2] — bypasses Eden  │
│              │ and burdens Old Gen directly              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Near-zero allocation cost vs Minor GC     │
│              │ frequency inversely proportional to Eden  │
│              │ size                                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Eden: objects born here; most die before │
│              │ GC even looks at them"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Survivor Space → Minor GC → TLAB          │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** TLAB allocation is "lock-free" within the TLAB, but TLAB refill requires updating the Eden allocation pointer atomically (CAS). At 500 threads each refilling their TLAB every 1 second, there are 500 CAS operations per second on a single hot cache line (the Eden top pointer). On a 100-core NUMA system, all 100 CPUs may contend for this cache line. Explain the hardware cache coherency protocol (MESI) events that occur during this contention, and describe how G1GC's region-based TLAB assignment reduces this specific bottleneck.

**Q2.** When Eden fills and Minor GC begins, all threads must "retire" their current TLABs — the partially-filled remaining space in each active TLAB becomes wasted Eden space. Describe the trade-off between TLAB size and TLAB waste: why doesn't the JVM use the smallest possible TLABs (e.g., 32 bytes per thread) to minimise waste, and what is the actual cost metric that determines the optimal TLAB size for a given workload?

