---
layout: default
title: "Eden Space"
parent: "Java & JVM Internals"
nav_order: 19
permalink: /java/eden-space/
number: "019"
category: JVM Internals
difficulty: ★★☆
depends_on: JVM, Young Generation, GC Roots, Object Allocation, TLAB
used_by: GC, Minor GC, Object Aging, Young Generation
tags: #java, #jvm, #memory, #gc, #internals, #intermediate
---

# 019 — Eden Space

`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`

⚡ TL;DR — The allocation-fast birth region within Young Generation where every new object is created via TLAB pointer bumping — wiped completely clean on every Minor GC.

| #019 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, GC Roots, Object Allocation, TLAB | |
| **Used by:** | GC, Minor GC, Object Aging, Young Generation | |

---

### 📘 Textbook Definition

Eden Space is the **primary allocation region within the Young Generation** where all new objects are initially created. Allocation uses Thread Local Allocation Buffers (TLABs) — pre-assigned chunks of Eden per thread — allowing lock-free allocation via simple pointer bumping. When Eden is full, a Minor GC is triggered. Live objects are evacuated to a Survivor space. Dead objects require no per-object work — the entire Eden space is reclaimed in bulk.

---

### 🟢 Simple Definition (Easy)

Eden is where **every new object is born** — allocation is extremely fast (just move a pointer), and cleanup wipes the entire region at once rather than cleaning up individual objects.

---

### 🔵 Simple Definition (Elaborated)

Eden's design is optimised for the two most common operations: fast allocation and fast collection. Allocation is nearly free — each thread has a private chunk of Eden (TLAB) and just bumps a pointer forward for each new object. Collection is also fast — since most objects in Eden are already dead by the time GC runs, the GC doesn't clean them individually. It copies the few survivors out and then marks the entire Eden region as empty in one operation. This asymmetry (expensive allocation avoided, cheap bulk reclaim) is what makes Java allocation surprisingly fast.

---

### 🔩 First Principles Explanation

**The allocation problem:**

```
Naive heap allocation:
  1. Acquire heap lock
  2. Find free block (free list or bitmap scan)
  3. Mark block as used
  4. Release heap lock
  Cost: 100-1000 cycles per allocation
  Contention: all threads compete for heap lock
```

**The Eden insight — bump pointer allocation:**

```
Eden is one contiguous region:
  [used | used | used | FREE ...]
                       ↑
                   next_free ptr

Allocating new object (size N):
  1. ptr_old = next_free
  2. next_free += N
  3. return ptr_old
  Cost: ~2 CPU instructions, ~1-2 cycles
  No lock, no search, no fragmentation

This works because:
  Eden is never randomly freed (no holes)
  Objects always die together (bulk wipe)
  → Contiguous allocation always valid
```

**The TLAB extension:**

```
Problem: Even bump pointer needs atomic operation
         if multiple threads share next_free ptr

Solution: Give each thread its own Eden chunk (TLAB)
  Thread gets: tlab_start to tlab_end (e.g. 512KB)
  Allocation within TLAB: pure local pointer bump
  Zero synchronisation, zero contention
  Thread fills TLAB → requests new TLAB from Eden
  (only this step needs synchronisation)
```

---

### ❓ Why Does This Exist — Why Before What

**Without Eden Space:**

```
Without segregated allocation region:
  Objects scattered throughout heap
  → Allocation requires free-list search
  → Fragmentation builds up
  → GC must trace every object individually
  → No bulk reclaim possible

Without TLAB in Eden:
  All threads compete for heap lock
  → Contention on every 'new' keyword
  → Scalability cliff on multi-core systems
  → 10 threads × 1M allocs/sec = 10M lock acquisitions/sec

Without bulk wipe (Eden's key property):
  GC must individually identify and free dead objects
  Since 98% of Eden is dead → 98% overhead for dead objects
  → Collection time = proportional to garbage (expensive)
  → Eden's design: collection time = proportional to survivors
    (much cheaper)
```

**What breaks without it:**
```
1. Allocation speed    → 100-1000× slower (lock + search)
2. Concurrency         → lock contention at every 'new'
3. GC collection speed → proportional to garbage not survivors
4. Memory locality     → objects fragmented, cache cold
5. Throughput          → falls off cliff under high alloc rate
```

---

### 🧠 Mental Model / Analogy

> Think of Eden as a **long roll of receipt paper** at a checkout counter.
>
> Every new object = tearing off the next piece of paper. Fast — just grab and advance.
>
> Each cashier (thread) has their own receipt roll (TLAB) — no waiting, no coordination between cashiers.
>
> When the roll runs out (Eden full) → Minor GC: tear off and keep only the receipts you still need (live objects, copied to Survivor). Then throw the entire used roll away at once — no sorting through individual receipts to find the trash.
>
> The **bulk discard** is what makes it fast. You're not examining 1000 receipts one by one — you're discarding 980 of them as a block and keeping 20.

---

### ⚙️ How It Works — TLAB + Eden Allocation

| #019 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, GC Roots, Object Allocation, TLAB | |
| **Used by:** | GC, Minor GC, Object Aging, Young Generation | |

**What happens during Minor GC:**

```
EDEN BEFORE GC:
  [obj_A(dead)][obj_B(live)][obj_C(dead)]
  [obj_D(dead)][obj_E(live)][obj_F(dead)]
  ... 80% dead, 20% live (typical)

MINOR GC:
  1. Trace from GC roots
  2. Mark obj_B, obj_E as live (reachable)
  3. COPY obj_B → Survivor space (age=1)
     COPY obj_E → Survivor space (age=1)
  4. Eden reclaimed IN BULK
     next_free = eden_start  ← single pointer reset!
     ALL dead objects gone in one operation
     No per-object cleanup needed

EDEN AFTER GC:
  [                                                ]
   ← completely empty, ready for allocation
```

---

### 🔄 How It Connects

```
new Object() called
      ↓
Thread checks TLAB free space
      ↓
TLAB has space?
  YES → bump tlab_top pointer
        return object address
        ~2 CPU cycles ✅
      ↓
TLAB full → request new TLAB from Eden
  Eden has space?
    YES → assign new TLAB chunk to thread
    NO  → trigger Minor GC
      ↓
Minor GC:
  Copy live objects → Survivor Space
  Reset Eden → empty
  Assign new TLAB to thread
      ↓
Object created → lives in TLAB/Eden
      ↓
Survives Minor GC → moves to Survivor
Survives threshold GCs → Old Gen
```

---

### 💻 Code Example

**Observing TLAB behaviour:**
```bash
# Print TLAB statistics
java -XX:+PrintTLAB MyApp

# Output per GC:
# TLAB: gc thread: 0x... [id: 1]
#   desired_size: 512KB
#   slow allocs: 12     ← times TLAB was refilled
#   refill waste: 2048  ← bytes wasted at TLAB end
#   alloc: 0.98         ← fraction allocated via TLAB
#   gc waste: 4096      ← wasted space at GC time

# alloc: 0.98 = 98% of allocations via fast TLAB path ✅
# If alloc < 0.9: TLAB too small, increase with:
java -XX:TLABSize=1m MyApp      # fixed TLAB size
java -XX:TLABWasteTargetPercent=1 MyApp  # tuning hint
```

**Allocation rate benchmarking:**
```java
import org.openjdk.jmh.annotations.*;

@BenchmarkMode(Mode.Throughput)
@Warmup(iterations = 5)
@Measurement(iterations = 10)
public class AllocationBenchmark {

    // This allocation is FREE via TLAB bump pointer
    // (assuming escape analysis doesn't eliminate it)
    @Benchmark
    public Object allocateTLAB() {
        return new Object();  // TLAB bump: ~1-2 cycles
    }

    // Force heap allocation outside TLAB
    // (large object bypasses TLAB)
    @Benchmark
    public byte[] allocateLarge() {
        return new byte[512 * 1024]; // 512KB: may bypass TLAB
    }
}
```

**Measuring Eden fill rate in production:**
```bash
# jstat: shows Eden usage live
jstat -gcnew <pid> 1000
# Output every 1000ms:
#  S0C    S1C    S0U    S1U   TT MTT  DSS   EC     EU     YGC  YGCT
# 10752  10752   0.0  5632.0  7  15 5376  83968  67543    12  0.135
# EC=Eden Capacity, EU=Eden Used
# EU grows over time → Eden filling
# At ~83MB Eden, filling ~67MB between GCs

# Allocation rate ≈ Eden_size / time_between_minor_gc
# 83MB / 2 seconds = ~41MB/sec allocation rate
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Eden allocation requires a lock" | TLAB allocation is **lock-free** — only TLAB refill needs brief sync |
| "Eden is cleaned object by object" | Eden is **bulk-wiped** — pointer reset; per-object work only for survivors |
| "Larger Eden = better" | Larger Eden = less frequent GC but **longer pause** when it does run |
| "All objects go to Eden" | Large objects (humongous) go **directly to Old Gen** bypassing Eden |
| "TLAB size is fixed" | JVM **dynamically sizes** TLABs based on allocation patterns |
| "Eden GC time = proportional to Eden size" | No — **proportional to live objects** (survivors) not total Eden size |

---

### 🔥 Pitfalls in Production

**1. High allocation rate saturating Eden**
```bash
# Symptom: Minor GC every 100-500ms
# Application spending 2-5% time in GC

# Diagnosis:
jstat -gcnew <pid> 500  # check every 500ms
# If YGC increments every check → Eden filling too fast

# Causes in Spring Boot apps:
#  • JSON serialisation creating many temporary strings
#  • Hibernate loading large result sets as objects
#  • Stream operations with many intermediate collections
#  • Logging frameworks creating String objects

# Fix 1: Increase Eden (less frequent GC):
java -XX:NewSize=1g MyApp

# Fix 2: Reduce allocation rate (better fix):
# Use StringBuilder instead of String concatenation in loops
# Use primitive arrays instead of boxed collections
# Use streaming/pagination instead of loading full datasets
```

**2. TLAB waste — large objects in small TLABs**
```java
// Thread has TLAB with 10KB free
// Allocates 12KB object
// → Object doesn't fit in TLAB
// → Thread requests new TLAB (old 10KB wasted)
// → OR object allocated directly in Eden (slow path)

// High TLAB waste = many wasted KB at TLAB boundaries

// Diagnosis:
-XX:+PrintTLAB | grep "refill waste"
# Large refill waste → many large objects

// Fix: tune TLAB size to match typical object sizes
-XX:TLABSize=256k    # smaller TLABs if mostly small objects
-XX:TLABSize=2m      # larger TLABs if many medium objects
```

---

### 🔗 Related Keywords

- `Young Generation` — Eden is the primary region within it
- `TLAB` — per-thread allocation buffer within Eden
- `Minor GC` — triggered when Eden fills, wipes it clean
- `Survivor Space` — destination for Eden survivors after GC
- `Object Header` — prepended to every Eden-allocated object
- `Escape Analysis` — may eliminate Eden allocation entirely
- `Bump Pointer` — allocation technique used in Eden
- `Humongous Objects` — too large for Eden, go directly to Old Gen
- `G1GC` — implements Eden differently as region-based allocation
- `Allocation Rate` — speed at which Eden fills (MB/sec)

---

### 📌 Quick Reference Card

| #019 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, GC Roots, Object Allocation, TLAB | |
| **Used by:** | GC, Minor GC, Object Aging, Young Generation | |

---
### 🧠 Think About This Before We Continue

**Q1.** Eden uses bump-pointer allocation within TLABs — essentially zero-cost allocation. Yet allocation-heavy microservices still suffer GC pressure. If allocation itself is nearly free, what exactly is the performance cost — and at what point in the allocation → Eden fill → Minor GC → Survivor copy cycle does the real cost appear?

**Q2.** G1GC doesn't have a single contiguous Eden region. Instead it designates multiple non-contiguous heap regions as "Eden regions." What is the advantage of this approach when the GC needs to meet a pause time target of 200ms — and what new problem does it introduce that the classic contiguous Eden doesn't have?

---