---
layout: default
title: "LFU Cache"
parent: "Data Structures & Algorithms"
nav_order: 47
permalink: /dsa/lfu-cache/
number: "0047"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: LRU Cache, HashMap, Heap (Min/Max)
used_by: CDN Caching, Browser Cache
related: LRU Cache, TinyLFU, MFU Cache
tags:
  - datastructure
  - advanced
  - algorithm
  - caching
  - deep-dive
---

# 047 — LFU Cache

⚡ TL;DR — An LFU Cache evicts the least *frequently* accessed item when full, outperforming LRU on skewed workloads — achieved in O(1) via a frequency-bucketed doubly linked list design.

| #047 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | LRU Cache, HashMap, Heap (Min/Max) | |
| **Used by:** | CDN Caching, Browser Cache | |
| **Related:** | LRU Cache, TinyLFU, MFU Cache | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A media streaming CDN caches popular videos. A few blockbuster titles (100 videos) account for 95% of traffic; millions of niche titles each serve a handful of viewers. An LRU cache fills with the most recently watched niche titles after any browsing session, evicting the blockbusters. The next viewer who wants a blockbuster gets a cache miss — even though blockbusters are clearly more valuable to cache.

THE BREAKING POINT:
LRU evicts based on *recency*, not *importance*. One scan through mostly-unique niche content "poisons" the LRU cache, displacing frequently watched content. Recency alone is a poor proxy for future utility in frequency-skewed workloads.

THE INVENTION MOMENT:
Track how many times each entry has been accessed. When eviction is needed, evict the entry with the lowest access count. Items accessed frequently stay in cache regardless of when they were last accessed. For ties in frequency, use LRU among the least-frequent group. This is exactly why the LFU Cache was created.

### 📘 Textbook Definition

An **LFU (Least Frequently Used) Cache** maintains access counts per entry and evicts the entry with the minimum access count when the cache is full. Among entries with equal minimum counts, the *least recently used* within that frequency group is evicted. An O(1) implementation uses three HashMaps: `{key→value}`, `{key→freq}`, `{freq→LRU-ordered-set-of-keys}`, plus a `minFreq` variable tracking the current minimum frequency bucket.

### ⏱️ Understand It in 30 Seconds

**One line:**
A cache that keeps the most-used items, evicting the least-accessed one when full.

**One analogy:**
> A library with limited shelf space. A bestseller borrowed 200 times stays on the shelf. A niche textbook borrowed once goes back to the archive even if it was borrowed yesterday. Usage count, not recency, determines shelf placement.

**One insight:**
LFU's critical implementation challenge is: when you access an entry, its frequency increases — and it must move from one frequency bucket to the next *in O(1)*. The "bucket-per-frequency" design with doubly linked lists inside each bucket achieves this by making bucket transitions O(1) pointer operations.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Every access to a key increments its frequency count.
2. The eviction candidate is always the key in the minimum-frequency bucket.
3. Among keys with the same minimum frequency, the LRU (oldest access) is evicted.

DERIVED DESIGN:
Naive O(log N) approach: use a min-heap keyed by (frequency, access_time). `get`: update heap entry — O(log N). `put`: heap insert — O(log N). Too slow for L1/L2 cache-level latency requirements.

O(1) approach (Ding & Lin, 2010):
```
keyToVal  = HashMap<K, V>
keyToFreq = HashMap<K, Integer>
freqToLRU = HashMap<Integer, LinkedHashSet<K>>
             (each bucket is insertion-ordered set = LRU)
minFreq   = integer (current minimum frequency)
```

`get(key)`:
1. Look up val: O(1)
2. `freq = keyToFreq[key]`; increment → `newFreq = freq+1`
3. Remove key from `freqToLRU[freq]`; if empty, remove bucket; if `freq == minFreq` and bucket now empty → `minFreq++`
4. Add key to `freqToLRU[newFreq]`
5. `keyToFreq[key] = newFreq`

`put(key, value)`:
- If exists: update value + call get-like increment
- If new: if at capacity, evict first entry from `freqToLRU[minFreq]`; add new entry to `freqToLRU[1]`; reset `minFreq = 1`

All steps are O(1) HashMap operations plus O(1) LinkedHashSet operations.

THE TRADE-OFFS:
Gain: Better hit rates than LRU for frequency-skewed workloads (Zipf distribution).
Cost: Higher implementation complexity, 3 HashMaps, "frequency recency bias" — a newly inserted item may never overcome an old item's head start in access counts.

### 🧪 Thought Experiment

SETUP:
LFU cache capacity 3. Sequence: put(A), put(B), put(C), get(A)×5, get(B)×3, get(C)×1, put(D).

LFU state before put(D):
- A: freq=5, B: freq=3, C: freq=1. minFreq=1.

LFU eviction: evict C (freq 1). Cache = {A, B, D}.

LRU would evict: C was last accessed after B, so LRU evicts... C too in this case. But try:
put(A), put(B), put(C), get(B)×5, get(C)×3, get(A)×1, then put(D):

LFU evicts A (freq 1, minimum).
LRU evicts A too (oldest access).

But now: put(A), put(B), put(C), get(B)×5, get(A)×3, get(C)×2, get(A) again... then a scan: put(D), put(E), put(F)...

LFU: D, E, F each get freq 1. Each displaces the min-freq entry — but A (freq 4) and B (freq 5) survive the scan. LRU: D, E, F are most recent; C (freq 3) and maybe A get evicted.

THE INSIGHT:
LFU resists scan pollution because frequently accessed items accumulate high counts that cannot be evicted just because a scan of unique items happened. LRU has no such defence — recency is vulnerable to bulkscans.

### 🧠 Mental Model / Analogy

> An LFU cache is like a music chart based on total streams. Songs are ranked by total listens. A new viral hit climbs the chart over weeks by accumulating streams. Legacy hits with massive total streams stay at the top even if they weren't played today. When the chart needs to cut entries, the least-streamed track goes first.

"Total streams" → frequency count
"Least-streamed track" → minimum frequency entry for eviction
"New viral hit" → newly inserted entry (starts with freq=1)
"Legacy hit" → old entry with high accumulated frequency

Where this analogy breaks down: Real charts don't have a fixed capacity that forces eviction; they can add entries. Also, real charts often weight recent streams more heavily — that's TinyLFU's approach, not pure LFU.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A smart cache that counts how often each item is used. The item used the least times gets removed first when space runs out.

**Level 2 — How to use it (junior developer):**
Use Caffeine (`Caffeine.newBuilder().maximumSize(N).build()`) — it implements W-TinyLFU which outperforms pure LFU. For implementing from scratch: three HashMaps + minFreq variable. Initialise minFreq=0; set it to 1 on each new insertion. Remember to remove empty frequency buckets immediately to keep minFreq accurate.

**Level 3 — How it works (mid-level engineer):**
The `freqToLRU` map uses `LinkedHashSet<K>` per frequency bucket — insertion-ordered, so the first element is the LRU within that frequency. Eviction: `freqToLRU.get(minFreq).iterator().next()` — O(1). Incrementing frequency: remove from old bucket, add to new bucket — O(1). The `minFreq` variable: only needs to be updated when the current `minFreq` bucket becomes empty AND the access was a `get` (not a `put`). On `put`, always reset `minFreq=1` because the new entry starts at freq=1.

**Level 4 — Why it was designed this way (senior/staff):**
The O(1) LFU algorithm published by Ding & Lin (2010) was a breakthrough — previously, best known was O(log N). The key insight: frequency buckets, not a global sorted structure, avoids re-sorting. The `LinkedHashSet` inside each bucket provides both O(1) removal-by-key and LRU ordering for tie-breaking. Caffeine's W-TinyLFU improves on pure LFU by using a frequency sketch (Count-Min Sketch) that forgets old accesses — preventing "frequency aging" where old entries with high counts block new hot entries forever. This aging is the core weakness of pure LFU.

### ⚙️ How It Works (Mechanism)

**LFU State representation:**
```
capacity=3, size=3

keyToVal:  {A→"a", B→"b", C→"c"}
keyToFreq: {A→3, B→2, C→1}
freqToLRU: {1→[C], 2→[B], 3→[A]}
minFreq:   1
```

**get(C):**
```
1. val = keyToVal[C] = "c"
2. freq = keyToFreq[C] = 1
3. Remove C from freqToLRU[1] → freqToLRU[1] = []
   freqToLRU[1] now empty AND freq==minFreq → minFreq++ = 2
4. Add C to freqToLRU[2] → freqToLRU[2] = [B, C] (C added last)
5. keyToFreq[C] = 2

State after:
freqToLRU: {2→[B,C], 3→[A]}
minFreq: 2
```

**put(D) (cache full):**
```
1. Evict: freqToLRU[minFreq=2] → first entry = B
   Remove B from all maps; size--
2. Add D: keyToVal[D]="d", keyToFreq[D]=1
   freqToLRU[1] = [D]; size++
3. Reset minFreq = 1

State after:
freqToLRU: {1→[D], 2→[C], 3→[A]}
minFreq: 1
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Request for key K arrives
→ get(K): found → increment freq, return value
→ [LFU CACHE ← YOU ARE HERE]
→ Miss: compute/fetch value
→ put(K, v): if full, evict minFreq entry; insert at freq=1
→ Reset minFreq=1
```

FAILURE PATH:
```
Workload: millions of unique items, each accessed once
→ All items have freq=1; minFreq=1 forever
→ LFU degenerates to LRU (same behavior, more overhead)
→ For purely uniform random access: LRU is simpler and equally effective
```

WHAT CHANGES AT SCALE:
At millions of entries, the three-HashMap approach uses O(N) memory per entry — more than LRU's two structures. The `freqToLRU` map can have millions of frequency buckets for long-running caches where items accumulate high counts. Caffeine avoids this by periodically halving all frequency counts ("aging") or using a probabilistic Count-Min Sketch that naturally forgets old accesses.

### 💻 Code Example

**Full O(1) LFU implementation:**
```java
class LFUCache {
    Map<Integer, Integer> keyToVal = new HashMap<>();
    Map<Integer, Integer> keyToFreq = new HashMap<>();
    Map<Integer, LinkedHashSet<Integer>> freqToKeys =
        new HashMap<>();
    int capacity, minFreq;

    LFUCache(int capacity) { this.capacity = capacity; }

    public int get(int key) {
        if (!keyToVal.containsKey(key)) return -1;
        incrFreq(key);
        return keyToVal.get(key);
    }

    public void put(int key, int value) {
        if (capacity <= 0) return;
        if (keyToVal.containsKey(key)) {
            keyToVal.put(key, value);
            incrFreq(key);
            return;
        }
        if (keyToVal.size() >= capacity) removeMinFreq();
        keyToVal.put(key, value);
        keyToFreq.put(key, 1);
        freqToKeys.computeIfAbsent(1,
            k -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }

    private void incrFreq(int key) {
        int f = keyToFreq.get(key);
        keyToFreq.put(key, f + 1);
        freqToKeys.get(f).remove(key);
        if (freqToKeys.get(f).isEmpty()) {
            freqToKeys.remove(f);
            if (minFreq == f) minFreq++;
        }
        freqToKeys.computeIfAbsent(f + 1,
            k -> new LinkedHashSet<>()).add(key);
    }

    private void removeMinFreq() {
        LinkedHashSet<Integer> keys =
            freqToKeys.get(minFreq);
        int evict = keys.iterator().next();
        keys.remove(evict);
        if (keys.isEmpty()) freqToKeys.remove(minFreq);
        keyToVal.remove(evict);
        keyToFreq.remove(evict);
    }
}
```

### ⚖️ Comparison Table

| Policy | Scan Resistant | Freq Aware | Recency Aware | Best For |
|---|---|---|---|---|
| **LFU** | ✓ | ✓ | ✗ (LRU for ties) | Stable-frequency workloads |
| LRU | ✗ | ✗ | ✓ | General temporal locality |
| TinyLFU/W-TinyLFU | ✓ | ✓ | ✓ | Production (overall best) |
| CLOCK | Partial | ✗ | ✓ | OS page replacement |
| ARC | ✓ | Partial | ✓ | Dynamic workload adaptation |

How to choose: In practice, use Caffeine (W-TinyLFU) for all new Java caches — it outperforms both pure LRU and pure LFU. Implement pure LFU for interview problems and learning. Use LRU in simple cases where implementation simplicity matters.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LFU always outperforms LRU | On uniform random access patterns, LFU offers no advantage over LRU; frequency ties produce identical behavior |
| LFU is just LRU with a counter | LFU requires fundamentally different data structures to achieve O(1); adding a counter to LRU still gives O(log N) |
| LFU is immune to all cache pollution | Very long-running items can accumulate counts so high that new hot entries can never displace them |
| LFU tracks how recently an item was accessed | Pure LFU only tracks count; recency is only used as a tie-breaker within the minimum-frequency bucket |

### 🚨 Failure Modes & Diagnosis

**1. Frequency aging stale items block new hot entries**

Symptom: After long uptime, same old items always in cache regardless of recent access patterns; new hot content evicted immediately.

Root Cause: Old items accumulated frequency counts so high (e.g., 10,000) that new items (freq=1) are immediately evicted. "Hot at startup" ≠ "hot now."

Diagnostic:
```java
// Print max frequency in cache:
keyToFreq.values().stream()
    .mapToInt(Integer::intValue).max()
    .ifPresent(max -> System.out.println("Max freq: " + max));
// If max >> minFreq, aging problem exists
```

Fix: Use TinyLFU (Caffeine) which uses Count-Min Sketch with frequency halving (aging) to forget old access patterns. Or implement periodic frequency halving.

Prevention: Never use pure LFU for long-running caches; use Caffeine with its built-in aging.

---

**2. minFreq not reset on new insertion**

Symptom: After inserting new item (freq=1), evictions remove a higher-frequency item instead of the new one.

Root Cause: Forgot to set `minFreq = 1` after each new `put()`. The cached `minFreq` points to an old minimum.

Diagnostic:
```java
// Test: put 4 items in capacity-3 cache; 5th should evict most recent
// new item (freq=1), not an older high-freq item
lfuCache.put(1, 1); lfuCache.put(2, 2); lfuCache.put(3, 3);
lfuCache.get(1); lfuCache.get(1); // freq[1]=2
lfuCache.put(4, 4); // should evict item 2 or 3 (freq=1)
assert lfuCache.get(2) == -1 || lfuCache.get(3) == -1;
```

Fix: Always `minFreq = 1` at end of every new `put()`.

Prevention: Add unit tests for post-insertion eviction order.

---

**3. Memory leak from non-empty frequency buckets accumulating**

Symptom: `freqToKeys` map grows without bound; memory increases over time.

Root Cause: Frequency buckets are created but not removed when empty (missed `if (isEmpty()) remove(freq)` check).

Diagnostic:
```bash
# Monitor freqToKeys.size() over time
System.out.println("Freq buckets: " + freqToKeys.size());
# Should not grow monotonically
```

Fix: Remove the frequency bucket from `freqToKeys` immediately when it becomes empty.

Prevention: Every time you remove a key from a bucket, always check and remove the bucket if empty.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `LRU Cache` — LFU builds on LRU concepts; understanding O(1) LRU is prerequisite.
- `HashMap` — three HashMaps are the core of the O(1) LFU design.
- `Heap (Min/Max)` — naive O(log N) LFU uses a min-heap; O(1) design avoids this.

**Builds On This (learn these next):**
- `TinyLFU / W-TinyLFU` — Caffeine's improved LFU with frequency aging and scan resistance.

**Alternatives / Comparisons:**
- `LRU Cache` — simpler implementation; better for recent-biased workloads.
- `Caffeine W-TinyLFU` — outperforms both LRU and LFU in practice.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fixed cache evicting least-accessed item; │
│              │ O(1) via 3 HashMaps + minFreq tracker     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ LRU evicts popular items after scans;     │
│ SOLVES       │ frequency should determine staying power  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Frequency buckets (not global sort) make  │
│              │ O(1) possible — only minFreq matters      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Stable frequency distributions (Zipf);   │
│              │ CDN; video streaming; search results      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-running cache without aging; or      │
│              │ uniform random access (use LRU instead)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Better hit rate for skewed workloads vs   │
│              │ implementation complexity + no aging      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A music chart: the most-played track     │
│              │  stays, the least-played is cut"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LRU Cache → Caffeine TinyLFU → Count-Min  │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Pure LFU has the "cold start" problem: a newly popular item (freq=1) is immediately evicted when the cache is full of items with high historical frequencies. Caffeine's W-TinyLFU uses a "window" LRU for recently inserted items and an LFU "main" cache. Explain how this window design solves the cold start problem, and why simply periodically halving all frequencies (aging) is not sufficient on its own.

**Q2.** You are designing a cache for a news aggregator where articles become hot during a news cycle (24 hours) and then are rarely accessed. Pure LFU would retain articles from yesterday's top stories over today's breaking news. Design a modification to the LFU eviction policy that incorporates time decay without using a heap (maintaining O(1) operations), and describe the data structure changes required.

