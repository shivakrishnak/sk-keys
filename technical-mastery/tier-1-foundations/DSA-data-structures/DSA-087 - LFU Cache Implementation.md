---
id: DSA-087
title: LFU Cache Implementation
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-086, DSA-028
used_by: DSA-077
related: DSA-086, DSA-028, DSA-014
tags:
  - data-structures
  - lfu-cache
  - cache-eviction
  - frequency
  - o-1
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 87
permalink: /technical-mastery/dsa/lfu-cache/
---

## TL;DR

LFU Cache evicts the least-frequently-used item (ties broken
by LRU order), implemented with three HashMaps for O(1)
get and put - better than LRU for skewed access patterns
with stable hot items.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-087 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, LFU-cache, eviction-policy |
| **Prerequisites** | DSA-086, DSA-028 |

---

### The Problem This Solves

LRU evicts items based on recency. But if a hot item hasn't
been accessed in 5 seconds (e.g., off-peak), LRU evicts
it when a burst of one-time access patterns fill the cache.
LFU keeps items proportional to their long-term access
frequency - better for stable "hot items" like popular
product pages or frequently accessed configs.

---

### The Three-HashMap Design

```
keyToVal:   key → value           (O(1) lookup by key)
keyToFreq:  key → current freq    (O(1) frequency lookup)
freqToKeys: freq → LinkedHashSet  (O(1) evict min-freq item)

Also track: minFreq (current minimum frequency)
```

**Full O(1) implementation:**

```java
class LFUCache {
    private final int capacity;
    private int minFreq;
    private final Map<Integer, Integer> keyToVal;
    private final Map<Integer, Integer> keyToFreq;
    // freqToKeys: LinkedHashSet preserves insertion order
    // (for LRU tie-breaking among same-frequency items)
    private final Map<Integer, LinkedHashSet<Integer>> freqToKeys;

    LFUCache(int capacity) {
        this.capacity = capacity;
        this.minFreq = 0;
        this.keyToVal = new HashMap<>();
        this.keyToFreq = new HashMap<>();
        this.freqToKeys = new HashMap<>();
    }

    // Get: O(1)
    int get(int key) {
        if (!keyToVal.containsKey(key)) return -1;
        incrementFreq(key);
        return keyToVal.get(key);
    }

    // Put: O(1)
    void put(int key, int val) {
        if (capacity <= 0) return;
        if (keyToVal.containsKey(key)) {
            keyToVal.put(key, val);
            incrementFreq(key);
            return;
        }
        if (keyToVal.size() >= capacity) evictLFU();
        keyToVal.put(key, val);
        keyToFreq.put(key, 1);
        freqToKeys.computeIfAbsent(1,
            k -> new LinkedHashSet<>()).add(key);
        minFreq = 1; // new key always starts at freq 1
    }

    private void incrementFreq(int key) {
        int freq = keyToFreq.get(key);
        keyToFreq.put(key, freq + 1);
        // Remove from old freq bucket
        freqToKeys.get(freq).remove(key);
        if (freqToKeys.get(freq).isEmpty()) {
            freqToKeys.remove(freq);
            if (minFreq == freq) minFreq++; // update minFreq
        }
        // Add to new freq bucket
        freqToKeys.computeIfAbsent(freq + 1,
            k -> new LinkedHashSet<>()).add(key);
    }

    private void evictLFU() {
        LinkedHashSet<Integer> minFreqKeys = freqToKeys.get(minFreq);
        int evictKey = minFreqKeys.iterator().next(); // LRU among min-freq
        minFreqKeys.remove(evictKey);
        if (minFreqKeys.isEmpty()) freqToKeys.remove(minFreq);
        keyToVal.remove(evictKey);
        keyToFreq.remove(evictKey);
    }
}
```

---

### Comparison Table

| Property | LRU | LFU |
|---------|-----|-----|
| Eviction basis | Least-recently-used | Least-frequently-used |
| Tie-breaking | N/A (pure recency) | LRU among same frequency |
| Implementation | HashMap + DLL | 3 HashMaps |
| Scan resistance | Poor (large scans evict hot items) | Good (hot items protected by frequency) |
| Cold-start | Good | Poor (all items start at freq=1) |
| Access pattern | Temporal locality | Long-term frequency |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LFU is always better than LRU" | LFU has poor cache pollution resistance for newly relevant items (stuck at low frequency); LRU adapts faster to changing access patterns |
| "LFU requires a heap for O(log n) eviction" | The three-HashMap design achieves O(1) eviction by tracking minFreq explicitly |

---

### Failure Modes & Diagnosis

**Failure: New popular item immediately evicted from LFU cache**
- Cause: Cold-start problem: new items start at frequency 1;
  old items with high accumulated frequency are protected
  even if they were popular 6 months ago but not now
- Fix: Add frequency decay (halve all frequencies
  periodically); or use Window-TinyLFU (used by Caffeine
  Java cache) which combines recency and frequency

---

### Quick Reference Card

| Operation | LFU Cache |
|-----------|----------|
| Get | O(1) |
| Put | O(1) |
| Eviction policy | Least-frequently-used |
| Tie-breaking | LRU order |
| Java cache lib | Caffeine (uses W-TinyLFU) |

---

### The Surprising Truth

Caffeine (the most popular Java caching library, used by
Spring Boot's default cache) doesn't use pure LRU or LFU.
It uses Window-TinyLFU (W-TinyLFU): a combination of a
small recent-access window (LRU) plus a frequency-based
main cache. Items from the recent window compete with
frequency-protected items for admission. This adaptive
approach outperforms both pure LRU and pure LFU on
real-world access patterns by 10-40% hit rate improvement
measured against Facebook, Wikipedia, and YouTube traces.

---

### Mastery Checklist

- [ ] Implements LFU with three HashMaps for O(1) ops
- [ ] Understands the minFreq tracking trick
- [ ] Knows Caffeine uses W-TinyLFU (not pure LFU)

---

### Interview Deep-Dive

**Q1 (Hard - LeetCode 460):** Design LFU cache with O(1)
get and put.

> Three maps:
> keyToVal: key→value for O(1) get
> keyToFreq: key→frequency for increment
> freqToKeys: freq→LinkedHashSet<key> for LRU tie-breaking
> minFreq: track current minimum for O(1) eviction
> 
> Get: look up value, call incrementFreq.
> Put: if present, update value + incrementFreq.
>   If at capacity, evict first element of freqToKeys[minFreq].
>   New key: add to all three maps, set minFreq=1.
> incrementFreq: move key from freq bucket to freq+1 bucket;
>   update minFreq if old bucket was minFreq and now empty.
> All operations: O(1). Space: O(capacity).
> 
> Interview insight: LinkedHashSet provides O(1) add,
> O(1) remove, and O(1) peek-first (insertion order) -
> exactly what's needed for LRU tie-breaking.
