---
id: OSY-032
title: "Page Replacement Algorithms (LRU, LFU, FIFO, Clock)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-031
used_by: OSY-054
related: OSY-031, OSY-054, OSY-090
tags:
  - page-replacement
  - LRU
  - LFU
  - FIFO
  - clock-algorithm
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/osy/page-replacement-algorithms/
---

## TL;DR

When physical RAM is full and a new page is needed, the
OS must evict one. FIFO is simple but suffers Belady's
anomaly. OPT is optimal but impossible. LRU is near-
optimal but expensive to implement. The Clock Algorithm
(CLOCK) is LRU's practical approximation used in real
OSes. Linux uses a two-list (active/inactive) LRU variant.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-032 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | page replacement, LRU, LFU, FIFO, clock, swap |
| **Prerequisites** | OSY-031 |

---

### The Problem

Physical memory has N frames. Process requests M pages
(M > N). When a new page is needed but all frames are
occupied, the OS must evict (replace) an existing page.
Wrong choice = "thrashing" (constant swapping, useless
CPU cycles).

---

### Algorithm Comparisons

**FIFO (First In, First Out)**

```
Replace the page that has been in memory the longest.

Reference string: 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2
Frames = 3:

7: [7 - -]  FAULT
0: [7 0 -]  FAULT
1: [7 0 1]  FAULT
2: [2 0 1]  FAULT (evict 7, oldest)
0: [2 0 1]  HIT
3: [2 3 1]  FAULT (evict 0, oldest)
...

Problems:
  1. Belady's Anomaly: MORE frames can cause MORE page faults!
     (FIFO with 4 frames may fault more than with 3 frames)
  2. May evict frequently-used pages
  
Advantage: O(1) with queue data structure
```

**OPT (Optimal) - Theoretical only**

```
Replace the page that won't be used for the longest time.

Requires knowing FUTURE reference string -> impossible in practice
Used as benchmark to measure how close real algorithms are.
```

**LRU (Least Recently Used)**

```
Replace the page not used for the longest TIME.
  
Key insight: recent past predicts near future
  (temporal locality)

Exact LRU implementation requires:
  Counter: timestamp every page access, evict lowest
  Stack: on access move to top, evict bottom
  Both are O(N) per access or require expensive hardware support

Approximation used in practice: Clock Algorithm
```

**Clock Algorithm (Second-Chance)**

```
Approximates LRU without exact timestamp tracking.

Data structure: circular queue of frames, pointer (hand)
Each frame has: page + reference bit (0 or 1)

On page access: set reference bit = 1 (hardware does this)

On page fault (need to evict):
  Advance hand clockwise
  If reference bit = 1: clear to 0, advance (second chance)
  If reference bit = 0: EVICT this page, place new page here

Example (4 frames, initial: [A*, B*, C*, D*] hand at A):
  * = reference bit = 1
  
  Request E (fault, all frames full):
    A: bit=1, clear to 0, advance
    B: bit=1, clear to 0, advance
    C: bit=1, clear to 0, advance
    D: bit=1, clear to 0, advance
    A: bit=0, EVICT A, place E here
```

---

### Linux Page Replacement (Two-List LRU)

```
Linux uses two LRU lists, not a single LRU queue:

Active list:   recently accessed pages (protected from eviction)
Inactive list: pages eligible for eviction

Page lifecycle:
  New page -> inactive list tail
  Accessed again while in inactive -> move to active list head
  Active list grows too big -> move tail of active to inactive head
  Memory pressure -> evict from inactive list tail
  
  Why two lists?
  Single LRU: a large file read (streaming) evicts all working set
  Two-list: streaming pages enter inactive, working set stays active
  This is "scan-resistant" LRU (protects from I/O cache pollution)
  
Observe in /proc:
  cat /proc/meminfo | grep -E "Active|Inactive"
  Active(anon):   working set anonymous pages (JVM heap)
  Inactive(anon): candidate for swap
  Active(file):   hot page cache entries
  Inactive(file): candidate for eviction from page cache
```

---

### Comparison Table

| Algorithm | Fault Rate | Belady's Anomaly | Impl. Cost | Used In |
|-----------|-----------|-----------------|------------|---------|
| FIFO | High | YES | O(1) | Simple systems |
| OPT | Minimal | No | Impossible | Benchmark only |
| LRU (exact) | Near-optimal | No | O(N) per access | Theory |
| Clock | Near-LRU | No | O(1) amortized | BSD Unix |
| Two-list LRU | Near-optimal | No | O(1) amortized | Linux |

---

### Java Relevance

```java
// Java caches often implement LRU
// LinkedHashMap with access order = LRU cache

// BAD: No eviction, unbounded memory growth
private final Map<String, byte[]> cache = new HashMap<>();
public byte[] get(String key) {
    return cache.computeIfAbsent(key, this::loadFromDB);
}
// OutOfMemoryError after enough unique keys

// GOOD: LRU cache with max size
private final Map<String, byte[]> cache = Collections.synchronizedMap(
    new LinkedHashMap<String, byte[]>(1000, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(
                Map.Entry<String, byte[]> eldest) {
            return size() > 1000;  // evict when > 1000 entries
        }
    }
);
// access-order=true: recently accessed entries move to tail
// removeEldestEntry: LRU eviction when capacity reached
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "More RAM = fewer page faults always" | Belady's anomaly proves that FIFO with MORE frames can have MORE page faults than with fewer. This is why FIFO is not used in practice |
| "LRU is used directly in Linux" | Linux uses a two-list LRU approximation (active/inactive lists). Pure LRU requires tracking exact access times for all pages - too expensive for millions of pages |

---

### Quick Reference Card

| Algorithm | Eviction Policy | Key Issue |
|-----------|----------------|-----------|
| FIFO | Oldest in memory | Belady's anomaly; may evict hot pages |
| OPT | Furthest future use | Optimal but requires future knowledge |
| LRU | Least recently used | Expensive exact tracking |
| Clock | LRU approximation | O(1), practical, used in real OSes |
| Linux Two-list | LRU with scan protection | Scan-resistant for large file I/O |
