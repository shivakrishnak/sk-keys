---
id: DSA-023
title: Big O Notation Fundamentals
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-004, DSA-022
used_by: DSA-028, DSA-072
related: DSA-004, DSA-022
tags:
  - complexity
  - big-o
  - asymptotic-analysis
  - fundamentals
  - performance
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/dsa/big-o-notation-fundamentals/
---

## TL;DR

Big O notation describes how algorithm runtime or memory
scales as input grows - the single most important tool for
comparing algorithm performance without running code.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-023 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | complexity, big-o, asymptotic analysis |
| **Prerequisites** | DSA-004, DSA-022 |

---

### The Problem This Solves

Two algorithms both sort a list. Algorithm A takes 0.1s for
100 elements; Algorithm B takes 0.05s. Which scales better
to 1,000,000 elements? Without Big O, you cannot answer this
without running both at scale. Big O lets you reason about
scaling without benchmarking.

---

### Textbook Definition

Big O notation O(f(n)) describes an upper bound on algorithm
growth rate. f(n) is the tightest function that bounds the
algorithm's operation count as n → ∞. Constants and
lower-order terms are dropped because they become irrelevant
at scale. Big O measures the worst case unless otherwise stated.

Related notations: Omega (Ω) = lower bound (best case),
Theta (Θ) = tight bound (average case matches worst case).

---

### Understand It in 30 Seconds

```
n=10:
  O(1):      1 op
  O(log n):  3 ops
  O(n):      10 ops
  O(n log n): 33 ops
  O(n²):     100 ops
  O(2^n):    1,024 ops

n=1,000,000:
  O(1):      1 op
  O(log n):  20 ops
  O(n):      1,000,000 ops
  O(n log n): 20,000,000 ops
  O(n²):     1,000,000,000,000 ops (10^12)
  O(2^n):    impossible
```

The difference between O(n) and O(n²) at scale:
O(n) = 1s → O(n²) = ~278 hours for the same input size.

---

### How It Works

**Big O class hierarchy (best to worst):**

```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) < O(n!)
```

**Simplification rules:**

```java
// Rule 1: Drop constants
// O(2n) → O(n)
for (int i = 0; i < n; i++) { }      // 2n ops
for (int i = 0; i < n; i++) { }      // simplified: O(n)

// Rule 2: Drop lower-order terms
// O(n² + n) → O(n²)
for (int i = 0; i < n; i++)          // n²
  for (int j = 0; j < n; j++) { }
for (int k = 0; k < n; k++) { }      // n (dropped)

// Rule 3: Different inputs → different variables
void fn(int[] a, int[] b) {
    for (int x : a) { }   // O(a.length)
    for (int y : b) { }   // O(b.length)
}
// Total: O(a + b), NOT O(n)

// Rule 4: Nested loops MULTIPLY, sequential ADD
for (int i = 0; i < n; i++)
  for (int j = 0; j < n; j++) { }  // O(n²), multiply
// ---
for (int i = 0; i < n; i++) { }    // O(n)
for (int j = 0; j < n; j++) { }    // O(n)
// Total: O(n + n) = O(2n) = O(n), add
```

**Recognizing common patterns:**

| Code pattern | Complexity |
|-------------|-----------|
| Single loop 0 to n | O(n) |
| Nested loop, both 0 to n | O(n²) |
| Loop halving (i /= 2) | O(log n) |
| Recursion splitting into 2 (merge sort) | O(n log n) |
| Recursion with 2 calls each full n | O(2^n) |
| Sorting + loop | O(n log n) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "O(1) means exactly one operation" | O(1) means CONSTANT time - could be 1,000 operations as long as it does not grow with n |
| "Lower Big O is always faster in practice" | O(n²) with n=100 beats O(n log n) with large constant. At small n, constants dominate |
| "Average case is what matters" | Depends on context; for worst-case-sensitive systems (real-time), worst case matters; use Θ for average |
| "Two O(n) algorithms perform the same" | O(n) just means linear; constants and hidden work vary; profile to be sure |

---

### Failure Modes & Diagnosis

**Failure: Misjudging complexity of library calls**
- Example: `List.contains()` on ArrayList is O(n),
  not O(1) like a HashMap - nested in a loop = O(n²)
- Diagnosis: Look up time complexity of every library
  method in the Java docs
- Fix: Replace `ArrayList.contains()` in hot paths with
  `HashSet.contains()` (O(1))

---

### Quick Reference Card

| Class | Example algorithm | Practical n limit |
|-------|------------------|-------------------|
| O(1) | HashMap.get | Any |
| O(log n) | Binary search | Any |
| O(n) | Linear scan | ~10^8 |
| O(n log n) | Merge sort | ~10^7 |
| O(n²) | Bubble sort | ~10^4 |
| O(2^n) | Power set | ~20 |
| O(n!) | Permutations | ~12 |

---

### Mastery Checklist

- [ ] Can calculate Big O for any code snippet including
      nested loops, recursion, and library calls
- [ ] Knows when to drop constants vs treat them seriously
      (large n vs small n)
- [ ] Recognizes O(n²) anti-patterns in code review

---

### Interview Deep-Dive

**Q1 (Easy):** What is the Big O of nested loops where
the inner loop goes from `i` to `n`?

> O(n²/2) = O(n²). The outer loop runs n times; the
> inner loop runs n, n-1, n-2, ..., 1 times. Total = n(n+1)/2.
> Drop the constant 1/2 → O(n²). This pattern appears in
> bubble sort and selection sort.

**Q2 (Medium):** What is the time complexity of this code?
```java
for (int i = 1; i < n; i *= 2)
  for (int j = 0; j < i; j++)
    System.out.println(j);
```

> O(n). The outer loop runs log(n) times (doubling: 1,2,4,...,n).
> The inner loop runs 1, 2, 4, ..., n/2 times respectively.
> Total inner iterations = 1 + 2 + 4 + ... + n/2 = n-1 = O(n).
> This is a geometric series sum pattern.
