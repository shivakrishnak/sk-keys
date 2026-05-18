---
id: DSA-022
title: Time Complexity vs Space Complexity
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-004
used_by: DSA-023, DSA-050
related: DSA-004, DSA-023, DSA-071
tags:
  - complexity
  - time-complexity
  - space-complexity
  - trade-offs
  - fundamentals
  - big-o
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/dsa/time-complexity-vs-space-complexity/
---

## TL;DR

Time complexity measures how runtime scales with input size;
space complexity measures memory. Every algorithm trades one
for the other - there is no free optimization.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-022 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | complexity, time-vs-space, trade-offs |
| **Prerequisites** | DSA-004 |

---

### The Problem This Solves

Choosing between algorithms requires understanding what you
are trading: speed vs memory. A cache uses O(n) space to
buy O(1) lookup time. Merge sort uses O(n) space to
guarantee O(n log n) time. Every trade-off has a context
where it is or is not acceptable.

---

### Textbook Definition

**Time complexity:** the number of operations an algorithm
performs as a function of input size n, expressed in Big O
notation (worst, average, or best case).

**Space complexity:** the amount of memory an algorithm
uses as a function of input size n. Includes both auxiliary
space (extra data structures) and input storage.

The space-time trade-off: using more memory (caching,
precomputation, auxiliary data structures) to reduce time.

---

### Understand It in 30 Seconds

Two ways to check if a number is prime:

```
Trial Division: O(sqrt(n)) time, O(1) space
  - Check every number up to sqrt(n)
  - No extra memory

Sieve of Eratosthenes: O(n) time, O(n) space
  - Precompute all primes up to n in a boolean array
  - O(1) lookup per query, but O(n) memory upfront
```

Checking many numbers: sieve wins (time).
Checking one number: trial division wins (space).
Context determines the right choice.

---

### How It Works

**Common space-time trade-offs:**

```java
// O(n²) time, O(1) space - no caching
int fibSlow(int n) {
    if (n <= 1) return n;
    return fibSlow(n-1) + fibSlow(n-2);
}

// O(n) time, O(n) space - memoization
Map<Integer, Integer> memo = new HashMap<>();
int fibFast(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n);
    int result = fibFast(n-1) + fibFast(n-2);
    memo.put(n, result);
    return result;
}

// O(n) time, O(1) space - tabulation (bottom-up)
int fibOptimal(int n) {
    if (n <= 1) return n;
    int prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}
```

**Space categories:**
- Auxiliary space: extra memory allocated by the algorithm
- Stack space: recursive call stack (O(depth) for recursion)
- Input space: the input itself (often not counted)

---

### Comparison Table

| Scenario | Time | Space | When to prefer |
|---------|------|-------|----------------|
| Simple recursion (fib) | O(2^n) | O(n) stack | Never for large n |
| Memoized recursion | O(n) | O(n) | When recursion is natural |
| Bottom-up tabulation | O(n) | O(n) | Most DP problems |
| Optimized DP | O(n) | O(1) | When full table not needed |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Optimize for time first, always" | In memory-constrained environments (embedded, mobile), space is the primary constraint |
| "Space complexity counts only the data structure" | Recursive call stack contributes to space: O(n) depth recursion uses O(n) stack frames |
| "O(n) space is always acceptable" | 10GB dataset with O(n) auxiliary space requires 20GB total - may not fit in RAM |

---

### Quick Reference Card

| Concept | Time cost | Space cost |
|---------|-----------|-----------|
| Caching results | Lower (O(1) lookup) | Higher (O(n) cache) |
| Recursion | Same as iterative | Higher (O(depth) stack) |
| Sort before search | Higher upfront, O(log n) search | O(1) or O(n) |
| Hash map for O(1) lookup | Lower time | O(n) space |

---

### Mastery Checklist

- [ ] Can analyze both time AND space complexity for any
      algorithm implementation
- [ ] Understands recursive stack space contributes to
      space complexity
- [ ] Can articulate the space-time trade-off with a
      concrete example (memoization, caching, indexing)

---

### Interview Deep-Dive

**Q1 (Easy):** What is the space complexity of a recursive
Fibonacci implementation?

> O(n) space due to the recursive call stack. Each call to
> `fib(n)` makes two recursive calls; the maximum call
> stack depth is n (the chain fib(n) → fib(n-1) → ...
> → fib(1)). Even though many frames are active
> simultaneously, the maximum depth at any point is n,
> giving O(n) space. Iterative bottom-up uses O(1) space.

**Q2 (Medium):** When would you choose higher space
complexity to reduce time complexity?

> When time is the bottleneck and memory is available:
> (1) Memoization/DP: trade O(n) or O(n²) space to reduce
> exponential time to polynomial. (2) Hash indexes in
> databases: O(n) space for O(1) lookup instead of O(log n)
> B-tree or O(n) sequential scan. (3) Precomputed lookup
> tables: trade O(k) space for O(1) time for fixed-domain
> computations. Context: a web server with 16GB RAM handling
> 10K req/s should use caching; a microcontroller with
> 64KB RAM should minimize allocation.
