---
id: DSA-084
title: Count-Min Sketch
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-083, DSA-014
used_by: DSA-105
related: DSA-083, DSA-085
tags:
  - data-structures
  - count-min-sketch
  - probabilistic
  - frequency
  - streaming
  - approximate
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 84
permalink: /technical-mastery/dsa/count-min-sketch/
---

## TL;DR

Count-Min Sketch estimates frequency of items in a stream
with configurable error bounds, using O(1/epsilon * log(1/delta))
space - orders of magnitude less than storing all exact
counts, and the data structure behind Twitter's trending topics.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-084 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, count-min-sketch, frequency-estimation |
| **Prerequisites** | DSA-083, DSA-014 |

---

### The Problem This Solves

"How many times has user X appeared in the last 1 billion
requests?" Exact counting needs 1B * 8 bytes = 8GB for
all users. Count-Min Sketch answers with configurable
accuracy (e.g., ±1000 in 1B events, 99% confidence)
using just kilobytes of memory.

---

### Textbook Definition

Count-Min Sketch is a probabilistic frequency estimation
structure using a 2D array (d rows x w columns). For d
independent hash functions, each element is counted in
one cell per row. Query returns the minimum across all d
rows. Error bound: with probability 1-delta, estimated
count <= actual count + epsilon * N where N = total items
seen, epsilon = e/w, delta = e^(-d). Only over-counts,
never under-counts.

---

### How It Works

**Implementation:**

```java
class CountMinSketch {
    private final int width;  // w = ceil(e/epsilon)
    private final int depth;  // d = ceil(ln(1/delta))
    private final int[][] sketch;
    private final int[] seeds; // hash function seeds

    CountMinSketch(double epsilon, double delta) {
        this.width  = (int) Math.ceil(Math.E / epsilon);
        this.depth  = (int) Math.ceil(Math.log(1.0 / delta));
        this.sketch = new int[depth][width];
        this.seeds  = new int[depth];
        Random rnd = new Random(42);
        for (int i = 0; i < depth; i++) seeds[i] = rnd.nextInt();
    }

    private int hash(String item, int seed) {
        int h = seed;
        for (char c : item.toCharArray())
            h = h * 31 + c;
        return Math.abs(h % width);
    }

    // Count: O(d)
    void add(String item) {
        for (int i = 0; i < depth; i++)
            sketch[i][hash(item, seeds[i])]++;
    }

    // Estimate: O(d) - returns minimum across all rows
    int estimate(String item) {
        int min = Integer.MAX_VALUE;
        for (int i = 0; i < depth; i++)
            min = Math.min(min, sketch[i][hash(item, seeds[i])]);
        return min; // guaranteed: estimate >= actual count
    }
}

// Example: 1% error, 1% failure probability
// width = ceil(e/0.01) = 272 cells per row
// depth = ceil(ln(100)) = 5 rows
// Total: 272 * 5 * 4 bytes = 5.4KB (vs millions for exact count!)
CountMinSketch cms = new CountMinSketch(0.01, 0.01);
```

**Twitter trending topics pattern:**

```
1 billion tweets/day with #hashtags.
Exact count: HashMap of all hashtags → GBs
Count-Min Sketch at 1% error: ~10KB

For each tweet: cms.add(hashtag)
Every minute: find top-k hashtags by estimate
  → Use min-heap of size K, checking candidate hashtags
  
Result: trending topics with ±1% count error, 10KB RAM
```

---

### Comparison Table

| Property | HashMap | Count-Min Sketch |
|---------|---------|-----------------|
| Exact counts | Yes | No (over-counts) |
| Under-count | Never | Never |
| Over-count | Never | Yes (bounded by epsilon*N) |
| Space | O(unique items) | O(1/epsilon * log(1/delta)) |
| 1M items | ~64MB | ~10KB at 1% error |
| Merge sketches | No | Yes (add cell-wise) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Count-Min Sketch can under-count" | Never. Collisions cause over-counts only. The minimum over d rows minimizes this |
| "All items have equal error" | High-frequency items have lower relative error; low-frequency items may have high relative error |

---

### Failure Modes & Diagnosis

**Failure: All estimates much higher than actual counts**
- Cause: Total event volume N too high relative to sketch
  size; error = epsilon * N blows up
- Fix: Periodically reset sketch (for sliding window);
  OR increase width (reduce epsilon)

---

### Quick Reference Card

| Property | Count-Min Sketch |
|---------|-----------------|
| Add | O(d) |
| Query | O(d) |
| Error guarantee | estimate ≤ actual + epsilon*N |
| Failure probability | delta |
| Space | O(1/epsilon * log(1/delta)) |
| Merge | Yes (add matrices cell-wise) |

---

### The Surprising Truth

Apache Flink, Apache Kafka Streams, and Twitter's Algebird
library (used in Twitter's real-time analytics) implement
Count-Min Sketch as a first-class streaming primitive.
Algebird's HeavyHitters (top-k frequency) is built on
Count-Min Sketch. The entire "Trending on Twitter" feature
that processes billions of tweets per day uses ~KB of
memory for frequency tracking, not GB - made possible by
Count-Min Sketch's fixed-size guarantees.

---

### Mastery Checklist

- [ ] Understands that CMS over-counts but never under-counts
- [ ] Can configure epsilon and delta for a given use case
- [ ] Knows CMS can be merged (useful for distributed systems)

---

### Interview Deep-Dive

**Q1 (Hard):** Design a system to find the top-10 most
visited URLs from 1 billion requests per hour using
limited memory.

> Two-structure approach:
> 1. Count-Min Sketch for frequency estimation
>    epsilon=0.001, delta=0.001 → ~2KB
>    For each request: cms.add(url)
> 2. Min-heap of size 10 for top-K tracking
>    Periodically: for candidate URLs, query CMS
>    Keep top-10 by estimated frequency in heap
> 
> Memory: CMS ~2KB + heap ~10 URLs (negligible).
> Error: estimated counts off by ±epsilon*N =
>   0.001 * 10^9 = ±1M requests. Acceptable for trending.
> 
> Alternative: Count sketch + heavy hitter algorithm
> for provably correct top-K (Misra-Gries), at
> cost of 2x memory.
> Production: Apache Kafka Streams + Algebird HeavyHitters.
