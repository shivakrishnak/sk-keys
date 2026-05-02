---
layout: default
title: "Card Table"
parent: "Java & JVM Internals"
nav_order: 308
permalink: /java/card-table/
number: "0308"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Heap Memory
  - Young Generation
  - Old Generation
  - GC Roots
  - Write Barrier
used_by:
  - Minor GC
  - G1GC
  - Write Barrier
  - Remembered Set
related:
  - Write Barrier
  - Remembered Set
  - GC Roots
  - Minor GC
tags:
  - jvm
  - gc
  - memory
  - java-internals
  - deep-dive
---

# 0308 — Card Table

⚡ TL;DR — The Card Table is a compact bitmap that tracks which chunks of Old Gen memory have been modified, letting Minor GC scan only the tiny dirty fraction instead of scanning all of Old Gen for references into Young Gen.

| #0308 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Heap Memory, Young Generation, Old Generation, GC Roots, Write Barrier | |
| **Used by:** | Minor GC, G1GC, Write Barrier, Remembered Set | |
| **Related:** | Write Barrier, Remembered Set, GC Roots, Minor GC | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Minor GC collects the Young Generation (typically 50–250MB). But objects in Old Gen (typically 1–4GB) may hold references to Young Gen objects. The GC must not incorrectly identify Young Gen objects as unreachable just because the live reference is in Old Gen. Without tracking Old→Young references, Minor GC must either: (A) treat all Old Gen roots as live (scan entire 4GB Old Gen every 100ms) — defeating the purpose of generational GC, or (B) only use thread stack roots — incorrectly collecting Young objects still referenced from Old Gen.

THE BREAKING POINT:
A caching layer holds references to freshly-created cache entries (Young Gen objects). If Minor GC doesn't scan Old Gen for these references, it incorrectly collects the cache entries while they are still referenced from Old Gen. The cache returns stale or null results. This is a correctness failure — incorrect GC causes data corruption.

THE INVENTION MOMENT:
This is exactly why the **Card Table** was created — to track which Old Gen regions contain modified references without requiring a full Old Gen scan on every Minor GC. The card table is a 512-byte-granularity bitmap: each bit covers a 512-byte region of Old Gen. Only "dirty" (modified) cards need scanning.

### 📘 Textbook Definition

A **Card Table** is a write-tracking data structure in the JVM heap management system. The heap is divided into fixed-size **cards** (typically 512 bytes each). Each card has a corresponding 1-byte entry in the card table array. When an object in Old Gen has its reference fields modified (via a **write barrier**), the JVM marks the corresponding card as "dirty" (sets its byte to a nonzero value). During Minor GC, instead of scanning all of Old Gen, the GC scans only dirty cards to find Old→Young references. After scanning, dirty cards are cleaned (reset to zero). This reduces Minor GC root scanning from O(Old Gen size) to O(dirty card count), typically 1–5% of Old Gen.

### ⏱️ Understand It in 30 Seconds

**One line:**
A index card per 512 bytes of memory that gets marked dirty whenever an object in that region is modified — GC only checks the dirty cards.

**One analogy:**
> Imagine a large library where librarians might have moved books to different shelves. Instead of checking every shelf for misplaced books, each shelf has a sticky note that turns red when a librarian touches it. During cleanup (GC), staff only inspect the red-noted shelves. After inspection, the flags are reset to white. Most shelves are white — cleanup is fast.

**One insight:**
The card table converts a global "where are all the Old→Young references?" question into a localized "which 512-byte regions of Old Gen were recently modified?" question. At 512 bytes per card = 1 byte per card, a 4GB Old Gen needs only 8MB of card table memory (1/512 ratio) — this fits in CPU cache, making card scanning fast despite the large Old Gen.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Minor GC needs to find all live references to Young Gen objects — including those from Old Gen.
2. Scanning all of Old Gen on every Minor GC defeats the purpose of generational GC (most objects die young → Minor GC should be cheap).
3. Only modified Old Gen references can create new Old→Young reference paths between Minor GCs.

DERIVED DESIGN:
If we track *modified* Old Gen references (not all Old Gen references), we only need to scan modified regions:
- Before an object in Old Gen's reference field is written, mark that region dirty.
- During Minor GC: iterate only dirty cards, scan all objects within those cards for references to Young Gen.
- After scanning: clean the dirty cards.

Card size trade-off: smaller cards → more precise, less false scanning, but larger card table (more memory, slower to iterate). Larger cards → smaller table, but more per-card false positives (scan more objects per dirty card). 512 bytes is the empirically chosen balance point in HotSpot.

```
┌─────────────────────────────────────────────────┐
│            Card Table Layout                     │
│                                                 │
│  Old Gen heap (4GB):                            │
│  [card0][card1][card2]...[cardN]                │
│   512B    512B   512B       512B                │
│                                                 │
│  Card Table (8MB, 1 byte per card):             │
│  [idx0][idx1][idx2]...[idxN]                    │
│   0=clean  !0=dirty                             │
│                                                 │
│  Write to Old Gen object's ref field:           │
│    → Write Barrier fires                        │
│    → card_table[addr >> 9] = dirty (0xFF)       │
│       (>> 9 = divide by 512)                    │
│                                                 │
│  Minor GC root scanning:                        │
│    for each dirty card: scan 512 bytes          │
│    for refs to Young Gen                        │
│    card_table[i] = clean (0x00)                 │
└─────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Minor GC scans only dirty cards (1–5% of Old Gen typically) → fast Minor GC.
Cost: Write barrier overhead on every reference store (1-2 extra instructions); card table memory (Old Gen / 512 bytes); false positives (dirty card scanned but no Young Gen reference found).

### 🧪 Thought Experiment

SETUP:
Old Gen = 2GB, containing 10 million objects. Between two Minor GCs, 50,000 Old Gen objects had their reference fields updated.

WITHOUT CARD TABLE:
Minor GC scans all 2GB of Old Gen = 10 million objects to find all Old→Young references. Each object: ~5ns to scan headers + fields. Total: 50ms of Old Gen scanning on every Minor GC. Minor GC frequency: every 500ms. Old Gen scanning dominates Minor GC time.

WITH CARD TABLE:
50,000 updated objects → ~50,000 objects × 512B/object (rough) → ~12,500 distinct cards dirty. GC scans 12,500 × 512B = 6.4MB of Old Gen in each Minor GC instead of 2GB. Speedup: 2GB / 6.4MB = 312x. Minor GC now takes 160µs for Old Gen scanning instead of 50ms.

THE INSIGHT:
The card table converts Old Gen scanning from proportional to Old Gen size to proportional to modification rate. In a typical workload where only 0.5% of Old Gen is modified between GCs, the speedup is 200x. This is why generational GC is effective: Minor GC is cheap, and the card table is what makes it cheap.

### 🧠 Mental Model / Analogy

> The card table is like a hotel's "do not disturb / please clean" door sign system applied to memory. Each room (512-byte card) has a sign. When something changes in a room (object reference modified), the housekeeping management system flips the sign to "needs attention." Daily cleanup (Minor GC) walks only the hallway checking signs — goes into only "needs attention" rooms. After cleaning, resets to "do not disturb." The next day, only rooms actually changed since yesterday need new cleaning.

"Room" → 512-byte card.
"Sign flip" → write barrier marking card dirty.
"Hallway walking" → scanning card table array (8MB, fits in cache).
"Entering the room" → scanning the 512-byte card for Young Gen refs.
"Resetting sign" → clearing card table entry after GC scan.

Where this analogy breaks down: Unlike hotel rooms, card table false positives exist — a card may appear dirty because an unrelated write touched the same 512-byte region, causing the GC to scan that card even though the actual reference in it hasn't changed.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Old memory can hold references to new memory. The JVM keeps a notepad (the card table) where it marks pages of old memory that have been touched recently. When collecting new memory, it only re-checks the marked pages — not all old memory.

**Level 2 — How to use it (junior developer):**
Card table is automatic and internal. You do not interact with it. Indirectly, you can affect it: patterns that heavily mutate Old Gen objects (large mutable caches, frequently-updated data structures in long-lived objects) will produce many dirty cards and increase Minor GC root scanning time. Use immutable data patterns for Old Gen objects when possible.

**Level 3 — How it works (mid-level engineer):**
The card table byte array is located at a fixed offset from the start of the heap. Computing the card table index for a heap address `addr` is a single right-shift: `card_idx = (addr - heap_base) >> LOG_CARD_SHIFT` (512 = 2^9, so shift by 9). The corresponding byte is set to 0 (clean) or 0xFF (dirty). Write barrier for reference stores: after writing `obj.field = value`, additionally execute: `card_table[(&obj.field - heap_base) >> 9] = dirty`. This is 1-3 extra instructions per reference store.

**Level 4 — Why it was designed this way (senior/staff):**
The card table's 512-byte granularity was chosen after empirical analysis: smaller granularity (e.g., 64 bytes per card) would be more precise but require 8x more card table memory — not fitting in L2 cache for large heaps. Larger granularity (e.g., 4KB per card) would reduce memory but scan too much on each dirty card. 512 bytes fits the card table for a 4GB Old Gen into 8MB — exactly fitting in L3 cache on most machines. The card table's 1-byte-per-card design (vs 1-bit-per-card) serves an additional purpose: G1GC uses the card table byte to store not just "dirty/clean" but also generation and processing state — reducing the number of data structures needed per card.

### ⚙️ How It Works (Mechanism)

**Write Barrier (HotSpot generated assembly):**
```asm
; Object field store: obj.field = newref
; Generated JIT code:
mov [rdi + field_offset], rsi    ; actual store

; Card table update (write barrier):
mov rax, rdi
shr rax, 9                        ; divide by 512
add rax, [card_table_base]        ; add card table base
mov byte ptr [rax], 0xFF          ; mark card dirty

; Cost: ~3 extra instructions per reference store
```

**Minor GC Root Scanning with Card Table:**
```
1. Iterate the card table array (8MB for 4GB Old Gen)
2. For each byte != 0 (dirty card):
   a. Compute heap address = card_index * 512 + heap_base
   b. Scan 512 bytes of Old Gen objects starting at address
   c. For each reference field found:
      - If points to Young Gen: add to GC roots
      - Else: skip
   d. Set card byte = 0 (clean card)
3. Continue Minor GC with collected roots
```

**Card Table Memory Layout:**
```
┌────────────────────────────────────────────────┐
│  Heap Address                Card Table Index  │
├────────────────────────────────────────────────┤
│  0x0000_0000 – 0x0000_01FF    0                │
│  0x0000_0200 – 0x0000_03FF    1                │
│  ...                                           │
│  0xFFFF_FE00 – 0xFFFF_FFFF  8,388,607 (8MB)   │
│                                                │
│  4GB heap → 8MB card table                     │
│  (1/512 ratio)                                 │
└────────────────────────────────────────────────┘
```

**G1GC Card Table Extension:**
G1GC extends the card table concept into per-region **Remembered Sets** (RSet): each region maintains a summary of cards from OTHER regions that point into it. This makes G1GC's incremental collection work: to collect a region, the GC only scans that region's RSet to find cross-region references, not the entire heap.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Object in Old Gen: obj.cacheRef = newYoungObject]
    → [Write Barrier fires]  ← YOU ARE HERE
    → [card_table[obj_addr >> 9] = 0xFF]
    → [card marked dirty]

[Minor GC triggered]
    → [Scan GC roots (thread stacks)]
    → [Scan dirty cards in card table]  ← YOU ARE HERE
    → [For each dirty card: scan 512B for Young refs]
    → [Found: obj.cacheRef → Young Gen object]
    → [Young Gen object marked live, not collected]
    → [Dirty cards cleared after scan]
```

FAILURE PATH:
```
[Write barrier missed (JNI native code writes ref)]
    → [Card NOT marked dirty]
    → [Minor GC doesn't find Old→Young reference]
    → [Young Gen object incorrectly collected]
    → [Stale reference in Old Gen]
    → [Next access: NullPointerException or worse]
(This is exactly why JNI code must use JNI APIs,
not raw memory writes for reference fields)
```

WHAT CHANGES AT SCALE:
With a 64GB heap and frequent writes (write-heavy cache workload), 128MB of card table must be scanned on each Minor GC. At 10 Minor GCs/second, this is 1.28GB/sec of card table reading — realistic on server hardware, but at scale with hundreds of dirty cards per GC, the card scanning phase can become a bottleneck. G1GC's refined card scanning (processes dirty cards concurrently in the background) addresses this.

### 💻 Code Example

Example 1 — Observing card table activity in GC logs:
```bash
java -Xlog:gc+remset=debug \
     -Xlog:gc+heap*=debug MyApp 2>&1 | grep -i "card"

# Sample G1GC output:
# [gc,remset] GC(4) Processed dirty cards: 12,345 of 512 bytes each
# [gc,heap] Before GC Used: 1.5GB, Eden: 512MB, Old: 1.0GB
```

Example 2 — Code pattern that generates many dirty cards (avoid for latency):
```java
// BAD: Mutating old gen objects at high frequency
// This creates many dirty cards → longer Minor GC scanning
@Component
public class HeavyCache {
    private final Map<String, Object> cache = new HashMap<>();

    // If cache has been promoted to Old Gen:
    // every put() marks a card dirty
    public void update(String key, Object value) {
        cache.put(key, value);  // write barrier → dirty card
    }
}

// With 100,000 puts/second → 100,000 dirty cards/second
// Each Minor GC (every 500ms): 50,000 dirty cards to scan
```

Example 3 — Immutable patterns reduce card table pressure:
```java
// GOOD: Immutable data reduces write barrier frequency
// Replace the mutable cache with a copy-on-write pattern:
private volatile Map<String, Object> cache = Map.of();

public void update(String key, Object value) {
    Map<String, Object> newCache = new HashMap<>(cache);
    newCache.put(key, value);
    cache = Collections.unmodifiableMap(newCache);
    // One write barrier (cache = newCache) vs N for mutation
}
```

Example 4 — Checking card table size for your heap:
```bash
# Card table size = heap size / 512
# For a 4GB heap: 4GB / 512 = 8MB card table
# For a 64GB heap: 64GB / 512 = 128MB card table

# Observe dirty card scanning time in G1GC:
java -XX:+UseG1GC \
     -Xlog:gc+phases*=debug MyApp 2>&1 | \
  grep "Update RS\|Scan RS"

# Output:
# [gc,phases] GC(5) Update RS (ms):  2.5
# [gc,phases] GC(5) Scan RS (ms):    1.2
# These are the card table and remembered set phases
```

### ⚖️ Comparison Table

| Structure | Granularity | Memory Cost | Precision | GC Usage |
|---|---|---|---|---|
| **Card Table (HotSpot)** | 512 bytes/card | Heap / 512 | Per-512-byte region | Minor GC (Serial, Parallel, G1) |
| Remembered Set (G1) | Per card per region | Variable | Per-card per region pair | G1 incremental collection |
| Snapshot At Beginning (SATB) | Per object | ~1 bit/object | Per-object | G1/ZGC concurrent marking |
| Mod Union Table | 512 bytes | Heap / 512 | Per-card (generational filter) | Full GC in some collectors |

How to choose: These are GC-internal structures; you don't choose between them. Understanding them helps diagnose GC phase timings in GC logs.

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────────────┐
│         Card Table Lifecycle per GC Cycle       │
├─────────────────────────────────────────────────┤
│  [Mutator phase (application running)]          │
│    obj.field = youngRef                         │
│      → write barrier → card[addr>>9] = dirty    │
│    (every reference write to Old Gen)           │
│                                                 │
│  [Minor GC triggered]                           │
│    Iterate card table                           │
│    For dirty card[i]:                           │
│      scan Old Gen[i*512 .. (i+1)*512]           │
│      find refs to Young Gen                     │
│      add to GC root set                         │
│      card[i] = clean                            │
│    Complete Minor GC with full root set         │
│                                                 │
│  [Back to mutator phase]                        │
│    Card table fully clean after GC              │
│    Mutations re-dirty cards                     │
└─────────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Card table only handles Old→Young references | Card table tracks all modifications to Old Gen memory, not just new Old→Young references. The scanning phase then filters for Young Gen references |
| The write barrier causes significant performance overhead | 1-3 extra instructions per reference store. For most workloads: 1–3% throughput overhead. Only in write-intensive microbenchmarks (millions of reference stores/second) does it become measurable |
| All dirty cards are scanned during every Minor GC | G1GC optimizes this: it uses refined card scanning (processes dirty cards concurrently during the mutator phase, before Minor GC) so fewer dirty cards remain to scan during Minor GC pauses |
| Card table is per-heap | There is one card table per JVM heap. In a standard JVM process with one heap, one card table. Some advanced setups (NUMA-aware JVMs) may have per-NUMA-node tables |
| Clearing dirty cards happens during Minor GC, causing longer pauses | G1GC's concurrent refinement threads process dirty cards in the background during application execution, clearing most cards before Minor GC starts |
| Card table is only used in generational GC | ZGC and Shenandoah don't use a card table for generational tracking in their default configurations (though newer GraalVM versions introduce generational ZGC that does) |

### 🚨 Failure Modes & Diagnosis

**High Minor GC Pause from Excessive Dirty Cards**

Symptom:
Minor GC `Scan RS` or `Update RS` phase takes 10–30ms. Application modifies large mutable Old Gen data structures frequently.

Root Cause:
High write rate to Old Gen objects → many dirty cards per GC interval → Minor GC must scan large portions of Old Gen despite it being "Minor" GC.

Diagnostic Command / Tool:
```bash
java -XX:+UseG1GC \
     -Xlog:gc+phases=debug MyApp 2>&1 | \
  grep "Scan RS\|Update RS\|Dirty Cards"

# High "Update RS" time = many dirty cards being refined
# High "Scan RS" time = many dirty cards at GC time
```

Fix:
Reduce mutation rate of Old Gen objects:
- Use immutable data structures for long-lived caches.
- Batch mutation operations to reduce write barrier frequency.
- Consider CopyOnWrite patterns for frequently-read-rarely-written structures.

Prevention:
Profile write barrier frequency in load testing using JFR's `jdk.ObjectWrite` events.

---

**G1GC Concurrent Card Table Refinement Causing CPU Spikes**

Symptom:
Background CPU spikes during high-write-rate periods. G1GC concurrent refinement threads consuming unexpected CPU.

Root Cause:
G1GC's concurrent refinement threads process dirty cards in the background to prevent Minor GC pause spikes. Very high write rates overwhelm the refinement threads.

Diagnostic Command / Tool:
```bash
java -Xlog:gc+refine=debug MyApp 2>&1 | grep "Refine"
# Shows refinement thread activity and dirty card counts
```

Fix:
Increase refinement thread count:
```bash
java -XX:G1ConcRefinementThreads=8 MyApp
# (Default is based on ParallelGCThreads)
```

Prevention:
Monitor G1 refinement thread CPU and dirty card queue depth in Prometheus.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Young Generation` — the card table exists to track references FROM Old Gen TO Young Gen; understanding Young Gen is prerequisite
- `Old Generation` — the card table tracks modifications in Old Gen; understanding Old Gen's role is essential
- `Write Barrier` — every card table dirty mark is created by a write barrier; the mechanism that feeds the card table

**Builds On This (learn these next):**
- `Remembered Set` — G1GC's Remembered Set is built on top of the card table concept, adding per-region cross-region tracking
- `Minor GC` — Minor GC uses the dirty cards as additional roots; understanding Minor GC shows how the card table integrates

**Alternatives / Comparisons:**
- `Remembered Set` — per-region refinement of the card table concept used by G1GC
- `Write Barrier` — the mechanism that CREATES dirty card entries; card table and write barrier are two sides of the same mechanism

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 512-byte-granularity bitmap tracking      │
│              │ modified Old Gen regions                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without it, Minor GC must scan all of     │
│ SOLVES       │ Old Gen for Old→Young references          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Old Gen / 512 = card table size (8MB for  │
│              │ 4GB heap) — fits in CPU cache for fast    │
│              │ dirty card iteration                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (automatic, internal to JVM)       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cannot avoid; reduce dirty rate via       │
│              │ immutable Old Gen objects                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write barrier overhead vs fast Minor GC   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Dirty laundry list for memory — only     │
│              │  wash the pages that were actually used"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Write Barrier → Remembered Set → G1GC     │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** G1GC's concurrent card table refinement processes dirty cards in the background during application execution. Describe the precise race condition that can occur if a refinement thread clears a dirty card while the application thread simultaneously writes a new reference to the same 512-byte region — and explain the JVM mechanism (either memory barrier or synchronization protocol) that prevents this from producing a silent correctness failure in the GC.

**Q2.** The card table's 512-byte granularity was an empirical choice balancing precision vs memory. If JVM heap sizes grow from today's typical 4–64GB to 1TB (as DRAM costs fall), what happens to the card table size (calculate it), why does the original design assumption (card table fits in L3 cache) break down, and what alternative tracking data structure designs would scale better to 1TB heaps while maintaining acceptable write barrier overhead?

