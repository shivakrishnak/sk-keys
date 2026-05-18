---
id: DSA-066
title: Memoization vs Tabulation
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-065
used_by: DSA-077
related: DSA-065, DSA-026, DSA-040
tags:
  - algorithms
  - memoization
  - tabulation
  - dynamic-programming
  - top-down
  - bottom-up
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/dsa/memoization-vs-tabulation/
---

## TL;DR

Memoization (top-down) adds a cache to recursion - natural
to write but has stack overhead. Tabulation (bottom-up) fills
a table iteratively - better performance and no stack overflow.
Same time complexity, different constants and trade-offs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-066 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, memoization, tabulation, DP |
| **Prerequisites** | DSA-065 |

---

### The Problem This Solves

Two correct implementations of the same DP problem behave
differently under large inputs, deep recursion, or memory
pressure. Choosing the wrong one causes StackOverflowError
(memoization with n=100,000) or wastes computation on
unused subproblems (tabulation when most subproblems are
irrelevant).

---

### Textbook Definition

**Memoization (top-down DP):** Recursive solution with a
cache (HashMap or array) that stores previously computed
subproblem results. Compute only what is needed.

**Tabulation (bottom-up DP):** Iterative solution that
fills a table from smallest subproblems to the answer.
Computes all subproblems up to the required size.

Both achieve the same asymptotic time complexity. The
difference is in constants, recursion depth, and which
subproblems are computed.

---

### How It Works

**Same problem - two implementations:**

Fibonacci n=6:

**Memoization (top-down):**
```java
// BAD: no memoization (exponential)
int fibNaive(int n) {
    if (n <= 1) return n;
    return fibNaive(n-1) + fibNaive(n-2);
}

// GOOD: memoized
Map<Integer, Long> memo = new HashMap<>();
long fib(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n);
    long result = fib(n-1) + fib(n-2);
    memo.put(n, result);
    return result;
}
// Pros: Natural from recursive formulation
//       Only computes needed subproblems
//       Easy to implement incrementally
// Cons: Stack frame per call → StackOverflow for large n
//       HashMap overhead if using non-int keys
```

**Tabulation (bottom-up):**
```java
long fibTab(int n) {
    if (n <= 1) return n;
    long[] dp = new long[n+1];
    dp[0] = 0; dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}
// Pros: No recursion → no StackOverflow
//       Better cache performance (sequential array access)
//       Easier to optimize space (rolling variables)
// Cons: Must compute all subproblems dp[0..n]
//       Less intuitive for some 2D problems
```

**Space-optimized tabulation (when only last 2 needed):**
```java
long fibO1(int n) {
    if (n <= 1) return n;
    long prev2 = 0, prev1 = 1;
    for (int i = 2; i <= n; i++) {
        long curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}
// O(1) space - only possible with tabulation
```

---

### Comparison Table

| Property | Memoization (top-down) | Tabulation (bottom-up) |
|---------|----------------------|----------------------|
| Implementation | Recursive + cache | Iterative + array |
| Subproblems computed | Only needed ones | All from 0 to n |
| Stack depth risk | Yes (StackOverflow) | No |
| Cache performance | Random access | Sequential (better) |
| Space optimization | Hard | Easy (rolling array) |
| Intuition | Follows recursion | Requires recurrence |
| When to prefer | Complex state, sparse | Large n, dense |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Memoization is always O(n) like tabulation" | Both are O(n) asymptotically, but memoization has HashMap overhead and O(n) stack depth; for n=100,000 in Java (default 512KB stack), memoization can stack overflow while tabulation runs fine |
| "Tabulation is always more efficient" | If only a few subproblems are needed (sparse DP), memoization skips the rest; tabulation wastes work |

---

### Failure Modes & Diagnosis

**Failure: StackOverflowError in memoized DP**
- Cause: Large n exceeds Java's call stack depth
  (~6,000-10,000 frames in default JVM settings)
- Fix: Switch to tabulation OR increase stack size:
  `-Xss4m`. Tabulation preferred for large n

---

### Quick Reference Card

| Situation | Recommendation |
|-----------|---------------|
| Small n, complex state | Memoization (easier to write) |
| Large n (n > 10,000) | Tabulation (no stack risk) |
| Sparse subproblems | Memoization (skips unused) |
| Space optimization needed | Tabulation (rolling array) |
| All subproblems needed | Tabulation (better cache perf) |

---

### The Surprising Truth

Java's JVM has a default thread stack of 512KB on 64-bit
systems. With 3-5 local variables per frame at 8 bytes each,
each frame uses ~40-100 bytes. This means roughly 5,000-
13,000 recursive calls before StackOverflowError. Recursive
memoized DP with n=50,000 will crash in Java without
explicit `-Xss` tuning. Tabulation simply never has this
problem. This is why production Java code almost always
uses tabulation for DP.

---

### Mastery Checklist

- [ ] Can implement both approaches for the same problem
- [ ] Knows when tabulation is safer (large n)
- [ ] Can space-optimize tabulation to O(1) when applicable

---

### Interview Deep-Dive

**Q1 (Medium):** For Longest Common Subsequence of two
strings length m and n, which DP approach is better?

> Both O(m*n) time. Tabulation preferred because:
> 1. State space is 2D (dp[i][j]), requiring all m*n cells
>    in the worst case - no sparsity benefit for memoization
> 2. Tabulation fills row by row: cache-friendly sequential
>    access vs memoization's random HashMap lookups
> 3. Stack depth is min(m,n) levels in memoization - safe
>    for typical string lengths
> Bottom-up tabulation: O(m*n) time, O(m*n) space.
> Space-optimized: O(min(m,n)) with 2-row rolling array.
> Memoization cannot be space-optimized below O(m*n).
