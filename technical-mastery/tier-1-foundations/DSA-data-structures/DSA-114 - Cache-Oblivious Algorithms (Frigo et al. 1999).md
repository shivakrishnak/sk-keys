---
id: DSA-114
title: Cache-Oblivious Algorithms (Frigo et al. 1999)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-071, DSA-070
used_by: DSA-122
related: DSA-071, DSA-112
tags:
  - theory
  - cache-oblivious
  - memory-hierarchy
  - frigo
  - cache-efficiency
  - performance
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 114
permalink: /technical-mastery/dsa/cache-oblivious-algorithms/
---

## TL;DR

Cache-oblivious algorithms achieve optimal cache
performance at ALL cache hierarchy levels (L1, L2, L3,
disk) without knowing cache sizes - using recursive
divide-and-conquer that naturally creates cache-friendly
access patterns.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-114 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | cache-oblivious, memory hierarchy, performance |
| **Prerequisites** | DSA-071, DSA-070 |

---

### The Problem This Solves

Classic algorithms are designed for RAM model (uniform
access time). Real computers have 5-level memory
hierarchy: L1 (0.5ns), L2 (5ns), L3 (40ns), RAM (100ns),
Disk (10ms). Cache-aware algorithms tune for a specific
cache size. Cache-oblivious algorithms automatically
perform well at every level without any tuning.

---

### Cache-Oblivious Principle

```
Key insight: A recursive divide-and-conquer algorithm that
divides the problem until subproblems fit in cache will
naturally use each cache level efficiently.

WHY: When a subproblem shrinks to fit in L1 cache,
     it executes from L1 (fastest).
     Before that, from L2. Before that, from L3.
     The recursion naturally exploits each cache level
     without knowing any cache size.

Cache-aware alternative: tune block size B = cache line size.
  Problem: what B do you use? L1 has B=64 bytes,
           L2 has B=256 bytes, disk has B=4KB.
           A cache-aware algorithm must pick one B
           and is sub-optimal at other levels.

Cache-oblivious: no B parameter. Works at ALL levels.
```

---

### Cache-Oblivious Matrix Multiplication

```java
// Cache-aware: process in blocks of size B
// Problem: need to choose B, only optimal for one cache level

// Cache-oblivious: recursive divide-and-conquer
void multiply(double[][] C, double[][] A, double[][] B,
              int rowA, int colA, int rowB, int colB,
              int rowC, int colC, int n) {
    if (n <= BASE_CASE) { // fits in L1 cache
        // Naive O(n^3) multiplication for tiny n
        for (int i = 0; i < n; i++)
            for (int k = 0; k < n; k++)
                for (int j = 0; j < n; j++)
                    C[rowC+i][colC+j] +=
                        A[rowA+i][colA+k] * B[rowB+k][colB+j];
        return;
    }
    int half = n / 2;
    // Split each matrix into 4 quadrants
    // 8 recursive calls, each on n/2 submatrix
    multiply(C,A,B, rowA,colA, rowB,colB, rowC,colC, half);
    multiply(C,A,B, rowA,colA, rowB,colB+half, rowC,colC+half, half);
    multiply(C,A,B, rowA,colA+half, rowB+half,colB, rowC,colC, half);
    // ... (all 8 quadrant combinations)
}
// This naturally becomes cache-friendly at every level:
// When n/2^k submatrix fits in L1: executes from L1
// When fits in L2: from L2. When fits in L3: from L3.
// No explicit cache blocking needed.
```

---

### Practical Relevance

```
Libraries using cache-oblivious design:
  FFTW (Fast Fourier Transform): adapts to cache via
        recursive decomposition. World's fastest FFT library.
  Intel MKL: matrix operations use cache-oblivious techniques.
  Java Arrays.parallelSort(): uses fork-join divide-and-conquer
        that achieves cache-oblivious properties.
  B-epsilon tree: used in databases (TokuDB, PerconaFT)
        providing O(log_B n) cache-oblivious performance.

When it matters:
  Large matrix operations (> 1MB matrix: cache pressure real)
  Database scans (disk I/O equivalent of cache miss)
  Scientific computing (petaflop simulations)
  In-JVM: rarely matters for typical application code
          unless processing arrays > 100K elements repeatedly
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Cache-oblivious = cache-friendly" | Cache-oblivious is a specific theoretical framework. All cache-oblivious algorithms are cache-friendly, but not all cache-friendly code is cache-oblivious (e.g., simple sequential scan is cache-friendly but not cache-oblivious in the theoretical sense) |

---

### Mastery Checklist

- [ ] Can explain why recursive divide-and-conquer is cache-oblivious
- [ ] Knows FFTW uses cache-oblivious design
- [ ] Understands when to apply this in JVM vs systems programming

---

### The Surprising Truth

Matteo Frigo (lead author of the 1999 cache-oblivious
paper) also wrote FFTW, the world's fastest FFT library.
FFTW is so fast it's used in virtually every scientific
computing application: from gravitational wave detection
(LIGO) to medical imaging (MRI reconstruction). The
theoretical insight - that algorithms can be made cache-
optimal without knowing the cache size - translates
directly to FFTW's "planner" that finds the optimal
recursive decomposition at runtime.
