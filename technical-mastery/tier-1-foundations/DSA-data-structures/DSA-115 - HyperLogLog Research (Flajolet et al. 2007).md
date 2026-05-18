---
id: DSA-115
title: HyperLogLog Research (Flajolet et al. 2007)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-085, DSA-012
used_by: DSA-122
related: DSA-083, DSA-084, DSA-085
tags:
  - theory
  - hyperloglog
  - flajolet
  - cardinality-estimation
  - probabilistic
  - research
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 115
permalink: /technical-mastery/dsa/hyperloglog-research/
---

## TL;DR

Philippe Flajolet's 2007 HyperLogLog paper solved the
cardinality estimation problem with 1.5% accuracy using
only 12KB for any cardinality - enabling Redis to count
billions of distinct items in near-zero memory.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-115 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | HyperLogLog, Flajolet, cardinality estimation, probabilistic |
| **Prerequisites** | DSA-085, DSA-012 |

---

### The Research Timeline

```
1984: Flajolet and Martin - "Probabilistic Counting Algorithms"
      First probabilistic cardinality estimation using single
      hash function + bit position trick. Error: O(1/sqrt(m))

1985-2000: LogLog variants
      Using k hash functions to reduce variance
      "SuperLogLog" (2000): improved constant

2007: HyperLogLog - Flajolet, Fusy, Gandouet, Meunier
      Key innovation: harmonic mean (not arithmetic mean)
      of MaxRun estimates across m=2^b registers
      Error: 1.04/sqrt(m), e.g. m=4096 -> 1.6% error
      Memory: m * 6 bits (4096*6=3KB to 16KB typical)

2013: HyperLogLog++ - Heule, Nunkesser, Hall (Google)
      Practical improvements: 64-bit hash, better constants,
      hybrid representation (sparse for small cardinalities).
      Used in Google BigQuery, implemented in Redis 2.8.9+
```

---

### The Mathematical Insight

```
Hash elements to [0,1] uniformly. For n elements:
  Expected number of elements with hash < 1/n: ~1
  Expected maximum run of leading zeros in binary hash: log2(n)

Simple estimator: 2^(max leading zeros) estimates n
  Problem: high variance (one unlucky element skews result)

HyperLogLog solution:
  Use m registers, each tracking max leading zeros for
  elements hashed to that register (first b bits determine register)
  Estimate: use harmonic mean of 2^MaxRun[j] across all m registers
  Harmonic mean is robust to outliers (unlike arithmetic mean)

The harmonic mean magic:
  Arithmetic mean of {1, 100}: 50.5 (skewed by 100)
  Harmonic mean of {1, 100}: 1/(1/2) = 1.98 (robust to outlier)
  For cardinality estimation, outlier registers (large MaxRun)
  from hash collisions are dampened by harmonic mean
```

---

### Why Redis Uses HyperLogLog

```
Problem: count distinct users per day
  100M users * 8 bytes (Long) = 800MB per day
  365 days = 292GB per year (exact Set approach)

HyperLogLog solution:
  12KB per day (HLL with m=4096 registers)
  365 days = 4.4MB per year
  Error: ~1.6%
  For analytics dashboards: 1.6% error acceptable

Redis implementation:
  PFADD key elem1 elem2 ...  # add elements
  PFCOUNT key                # estimate cardinality (1.6% error)
  PFMERGE dest key1 key2 ... # merge HLLs (union cardinality)

Merge property (key for distributed systems):
  HLL(A) merged with HLL(B) = HLL(A union B)
  This is bitwise OR of registers
  Allows: daily HLL -> weekly HLL -> monthly HLL
  Without re-processing all raw data
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "HyperLogLog only works for counting integers" | HLL works for any hashable element. Redis PFADD accepts strings. The hash function maps any element to a uniform bit string |
| "More memory always means better HLL accuracy" | Accuracy improves as sqrt(m) where m=registers. Doubling accuracy requires 4x memory. There are diminishing returns past ~12KB |

---

### Mastery Checklist

- [ ] Understands the leading zeros trick (bit position = log2(n))
- [ ] Knows why harmonic mean is used (outlier robustness)
- [ ] Can merge HLLs for distributed cardinality estimation

---

### The Surprising Truth

Philippe Flajolet, one of the founders of analytic
combinatorics, died in 2011 at age 62 - before HyperLogLog
became ubiquitous in production systems. His algorithms
now count distinct visitors at Facebook, Twitter, Google,
and every Redis deployment worldwide. The PFADD/PFCOUNT
Redis command names use "PF" as a tribute to Flajolet.
He had a characteristic style: his papers were always
mathematically rigorous and included whimsical examples,
calling his probabilistic counting algorithms "approximate
magic." His 2007 HyperLogLog paper ended with: "This
algorithm constitutes the first algorithm for cardinality
estimation to require but O(log log n) bits to represent."
