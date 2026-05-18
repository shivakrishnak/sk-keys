---
id: DSA-065
title: Dynamic Programming (DP)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-026
used_by: DSA-066, DSA-077
related: DSA-026, DSA-066, DSA-067, DSA-068
tags:
  - algorithms
  - dynamic-programming
  - dp
  - optimization
  - overlapping-subproblems
  - optimal-substructure
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/dsa/dynamic-programming/
---

## TL;DR

Dynamic Programming transforms exponential recursion into
polynomial solutions by storing solutions to subproblems -
applicable when the problem has optimal substructure and
overlapping subproblems.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-065 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, DP, optimization, subproblems |
| **Prerequisites** | DSA-026 |

---

### The Problem This Solves

Fibonacci(40) via naive recursion: 2^40 calls. With DP:
40 unique subproblems, each solved once = O(n).
DP transforms exponential brute force into polynomial
solutions by identifying and caching overlapping
subproblems.

---

### Textbook Definition

Dynamic Programming is an algorithm design technique for
optimization and counting problems with two properties:
1. Optimal substructure: optimal solution contains
   optimal solutions to subproblems
2. Overlapping subproblems: same subproblems are
   solved multiple times in naive recursion

DP stores subproblem solutions (memoization = top-down,
tabulation = bottom-up) to avoid recomputation.
See DSA-066 for the memoization vs tabulation comparison.

---

### Understand It in 30 Seconds

```
Fibonacci naive: fib(5) = fib(4) + fib(3)
                         = (fib(3)+fib(2)) + (fib(2)+fib(1))
fib(3) computed TWICE, fib(2) THREE TIMES.

DP: compute once, store result.
  fib[0]=0, fib[1]=1, fib[2]=1, ...
  Each fib[i] = fib[i-1] + fib[i-2]
  O(n) time, O(n) space (or O(1) with 2 variables)
```

---

### How It Works

**Five steps to solve any DP problem:**

```
1. IDENTIFY: Is this optimization or counting?
             Does it have optimal substructure?
             Do subproblems overlap?

2. STATE: Define what dp[i] (or dp[i][j]) represents.
          "dp[i] = max profit using first i items"

3. TRANSITION: How is dp[i] computed from smaller states?
               "dp[i] = max(dp[i-1], dp[i-w]+val)"

4. BASE CASE: What are the trivially-known values?
              "dp[0] = 0 (no items, no profit)"

5. ANSWER: Which state holds the final answer?
           "dp[n] = max profit with all n items"
```

**Classic example: 0/1 Knapsack**

```java
// Items: weights[] and values[], capacity W
// dp[i][w] = max value using first i items, capacity w
int knapsack(int[] weights, int[] values, int W) {
    int n = weights.length;
    int[][] dp = new int[n+1][W+1];

    for (int i = 1; i <= n; i++) {
        for (int w = 0; w <= W; w++) {
            // Don't take item i
            dp[i][w] = dp[i-1][w];
            // Take item i (if it fits)
            if (weights[i-1] <= w) {
                dp[i][w] = Math.max(dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                );
            }
        }
    }
    return dp[n][W];
}
// Time: O(n*W), Space: O(n*W)
// Space-optimized to O(W) by using 1D dp array
```

---

### Comparison Table

| Problem | Approach | DP pattern |
|---------|----------|-----------|
| Fibonacci | Linear | dp[i] = dp[i-1]+dp[i-2] |
| Knapsack 0/1 | 2D grid | dp[i][w] |
| Longest Common Subsequence | 2D grid | dp[i][j] |
| Coin change (min coins) | Linear | dp[i] = min coins for i |
| Longest increasing subseq | Linear | dp[i] = LIS ending at i |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "DP is just recursion with caching" | Memoization (top-down DP) is that. But tabulation (bottom-up DP) avoids recursion entirely, has better cache performance, and no stack overflow risk |
| "DP always requires a 2D array" | Many DP problems need only O(n) or O(1) space with rolling arrays |

---

### Failure Modes & Diagnosis

**Failure: DP gives wrong answer**
- Cause 1: Wrong state definition (dp[i] means something
  inconsistent across transitions)
- Cause 2: Wrong base case (not covering all edge cases)
- Cause 3: Wrong transition (not considering all choices)
- Fix: Write out the recurrence on paper with a small
  example before coding; verify each dp[i] by hand

---

### Quick Reference Card

| Property | DP |
|---------|-----|
| Requirement 1 | Optimal substructure |
| Requirement 2 | Overlapping subproblems |
| Top-down | Memoization (recursive + cache) |
| Bottom-up | Tabulation (iterative) |
| Common patterns | Linear, 2D grid, interval, tree DP |

---

### The Surprising Truth

The word "programming" in "Dynamic Programming" has nothing
to do with computer programming. Richard Bellman coined it
in the 1950s to mean "planning" or "scheduling" (as in
"linear programming" = linear optimization). Bellman used
the term specifically to avoid government scrutiny of his
mathematics research - the Secretary of Defense at the
time disliked mathematical research, so Bellman chose a
name that sounded like practical planning. The word
"dynamic" was chosen because he wanted something that
"no one could object to."

---

### Mastery Checklist

- [ ] Can apply the 5-step DP framework to any new problem
- [ ] Implements knapsack, LCS, and coin-change from memory
- [ ] Knows when to apply memoization vs tabulation

---

### Interview Deep-Dive

**Q1 (Medium):** Given coins of different denominations,
find the minimum number of coins to make amount n.

> DP: dp[i] = min coins to make exactly i cents.
> Base: dp[0] = 0.
> Transition: for each coin c, dp[i] = min(dp[i], dp[i-c]+1).
> Answer: dp[amount] (-1 if unreachable).
>
> Why greedy fails: coins {1, 3, 4}, amount = 6.
> Greedy picks 4, then 1+1 = 3 coins.
> DP finds 3+3 = 2 coins. Optimal substructure holds but
> greedy picks locally optimal choice that's globally wrong.
> DP explores all choices: O(amount * num_coins).
