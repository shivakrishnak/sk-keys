---
layout: default
title: "Tabulation (Bottom-Up DP)"
parent: "Data Structures & Algorithms"
nav_order: 52
permalink: /dsa/tabulation-bottom-up-dp/
number: "0052"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Memoization, Array, Dynamic Programming
used_by: Dynamic Programming, Longest Common Subsequence, Knapsack Problem
related: Memoization, Dynamic Programming, Space Complexity
tags:
  - algorithm
  - intermediate
  - performance
  - pattern
---

# 052 — Tabulation (Bottom-Up DP)

⚡ TL;DR — Tabulation fills a DP table iteratively from base cases upward, avoiding recursion overhead and call stack limits while matching memoization's time complexity.

| #052 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Memoization, Array, Dynamic Programming | |
| **Used by:** | Dynamic Programming, Longest Common Subsequence, Knapsack Problem | |
| **Related:** | Memoization, Dynamic Programming, Space Complexity | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Memoized Fibonacci works for N up to ~5,000. Beyond that, the recursion depth causes `StackOverflowError`. You cannot increase stack size indefinitely (each thread stack consumes RAM). For large N=1,000,000, you simply cannot use top-down recursion.

**THE BREAKING POINT:**
Memoization is limited by call stack depth. Even with caching, N recursive frames are opened on the call stack for the first full traversal. For large N, this is fatal. You need the efficiency of memoization without the stack depth risk.

**THE INVENTION MOMENT:**
Instead of computing from the top (large N) down to the base cases, compute from the bottom (base cases) up to the target. No recursion. No call stack. Just a loop filling an array in dependency order: compute `dp[i]` only after all values it depends on are already filled. This is exactly why Tabulation was created.

---

### 📘 Textbook Definition

**Tabulation** (bottom-up dynamic programming) constructs a table of DP values starting from base cases and iteratively filling in higher values in dependency order, until the target value is computed. Unlike memoization (which is recursive/top-down), tabulation uses iterative loops — eliminating call stack overhead and StackOverflowError risk. Time and space complexity match memoization, but tabulation often achieves better cache performance due to sequential array access patterns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Fill the answer table from small to big — base cases first, target last.

**One analogy:**
> Building a staircase: you cannot place step 10 before step 9. Tabulation is laying step 1, then 2, then 3 — always in order, always on solid ground. Memoization is someone jumping from step 10 down to step 1 to build what's needed — works, but risks falling if the staircase is too tall.

**One insight:**
Tabulation and memoization compute the exact same set of subproblems. The difference is *direction* and *execution model*. Tabulation is often more space-efficient (can discard rows once calculated) and always safe from stack overflow, at the cost of computing subproblems you may not need.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Compute subproblems in topological order (no subproblem is computed before its dependencies).
2. Each subproblem is computed exactly once (fill the cell once; never recompute).
3. The result is the value of the final cell (the target subproblem).

**DERIVED DESIGN:**
For 1D DP (fib, coin change):
- `dp[0]` = base case; `dp[1]` = base case; compute `dp[i]` from `dp[i-1]`, `dp[i-2]`.
- Sequential left-to-right loop ensures all dependencies are available.

For 2D DP (LCS, edit distance):
- `dp[0][*]` and `dp[*][0]` = base cases; compute `dp[i][j]` from `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]`.
- Row-by-row left-to-right ensures all dependencies are available.

Space optimisation: if `dp[i]` only depends on `dp[i-1]` (not earlier), keep only one row. Many 2D DP problems drop from O(N²) to O(N) space.

**THE TRADE-OFFS:**
**Gain:** O(1) call stack, better cache locality (sequential array access), space optimisation possible.
**Cost:** Computes ALL subproblems even if only a few are needed (vs memoization's lazy evaluation), harder to reason about for non-linear dependency orders.

---

### 🧪 Thought Experiment

**SETUP:**
Coin change: given denominations [1, 5, 10] and amount 12, find minimum coins.

MEMOIZATION approach: recurse from 12, branching to 11, 7, 2. Each subproblem recurses further.

TABULATION approach:
```
dp[0]=0, dp[1]=1(1), dp[2]=2(1+1), dp[3]=3,
dp[4]=4, dp[5]=1(5), dp[6]=2(5+1), dp[7]=3,
dp[8]=4, dp[9]=5, dp[10]=1(10), dp[11]=2,
dp[12]=3(10+1+1)
```
No recursion, no stack. Each cell filled exactly once. Answer at dp[12]=3.

**THE INSIGHT:**
The order matters: compute dp[5] before dp[10] before dp[12]. Tabulation enforces this order explicitly by looping from 0 to 12. Memoization enforces it implicitly through the call stack. Both produce the same dp[12]=3.

---

### 🧠 Mental Model / Analogy

> Tabulation is filling a tax form from the top line down: line 1 is given (income), line 2 depends on line 1, line 3 depends on lines 1 and 2, and so on until the final total. You fill each line once, in order. No backtracking, no uncertainty — every required value is available before you need it.

- "Tax form lines" → DP table cells
- "Fill in order" → compute base cases to target
- "Each line depends on earlier lines" → DP dependency structure
- "Final total" → target subproblem answer

Where this analogy breaks down: Tax forms are filled once; DP tables for different inputs require refilling from scratch. Also, tax forms are 1D; many DP tables are 2D or more.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Start with the easy cases (base cases), then use them to solve slightly harder cases, keep going until you've solved the target problem. Always build from previously solved answers.

**Level 2 — How to use it (junior developer):**
1. Define what `dp[i]` means. 2. Identify base cases. 3. Write the recurrence: `dp[i] = f(dp[i-1], dp[i-2], ...)`. 4. Loop from base cases to target. 5. Return `dp[N]`. Always validate: "is dp[i-1] computed before dp[i] is accessed?" For 2D: always fill base rows/columns first.

**Level 3 — How it works (mid-level engineer):**
Loop order determines correctness. For LCS `dp[i][j] = max(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]+1)`: outer loop on i (top to bottom), inner on j (left to right) — ensures all three predecessors are available. Reversing the loop order for different recurrences (e.g., when `dp[i]` depends on `dp[i+1]`) requires iterating right to left.

**Level 4 — Why it was designed this way (senior/staff):**
The term "dynamic programming" was coined by Richard Bellman in the 1950s. "Dynamic" was chosen partly to avoid military funding oversight (a clever naming choice). Tabulation maps directly to matrix operations — edit distance, LCS, and optimal subsequences are naturally expressed as matrix fills. Hardware prefetching strongly favours sequential array access (tabulation's pattern) over HashMap-scattered access (memoization's pattern). For problems computed billions of times (sequence alignment in bioinformatics), the cache-efficiency of tabulation vs memoization causes 10–50× performance differences in practice.

---

### ⚙️ How It Works (Mechanism)

**Fibonacci — tabulation:**
```java
long[] dp = new long[N + 1];
dp[0] = 0;
dp[1] = 1;
for (int i = 2; i <= N; i++) {
    dp[i] = dp[i-1] + dp[i-2];
}
return dp[N];
// Space: O(N) — optimisable to O(1)
```

**Fibonacci — O(1) space tabulation (rolling variables):**
```java
long prev2 = 0, prev1 = 1;
for (int i = 2; i <= N; i++) {
    long curr = prev1 + prev2;
    prev2 = prev1; prev1 = curr;
}
return prev1; // Space: O(1)
```

**Coin Change — 1D tabulation:**
```java
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1); // "infinity" sentinel
dp[0] = 0;
for (int i = 1; i <= amount; i++) {
    for (int coin : coins) {
        if (coin <= i)
            dp[i] = Math.min(dp[i], dp[i - coin] + 1);
    }
}
return dp[amount] > amount ? -1 : dp[amount];
```

**LCS — 2D tabulation:**
```java
int[][] dp = new int[m+1][n+1]; // base cases = 0

for (int i = 1; i <= m; i++) {
    for (int j = 1; j <= n; j++) {
        if (s1.charAt(i-1) == s2.charAt(j-1))
            dp[i][j] = dp[i-1][j-1] + 1;
        else
            dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
    }
}
return dp[m][n];
```

┌──────────────────────────────────────────────┐
│  LCS tabulation fill order                   │
│                                              │
│       "" A B C                              │
│  ""  [ 0  0  0  0 ]  ← base row             │
│  A   [ 0  1  1  1 ]  ← fill left to right   │
│  C   [ 0  1  1  2 ]                          │
│  B   [ 0  1  2  2 ]                          │
│                                              │
│  dp[3][3] = 2 → LCS length of "AC","ABC"=2  │
└──────────────────────────────────────────────┘

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Problem decomposed into subproblems
→ dp[] table allocated
→ Base cases filled
→ Loop: fill dp[i] from previously-filled dp[j<i]
→ [TABULATION ← YOU ARE HERE]
→ Target dp[N] returned
→ Optional: space-optimise with rolling variables
```

**FAILURE PATH:**
```
Wrong loop order (dp[i] reads dp[i+1] which isn't filled)
→ dp[i] computed from zero/invalid value
→ Wrong answer silently (no error thrown)
→ Fix: trace the recurrence, verify loop direction
```

**WHAT CHANGES AT SCALE:**
For N=1,000,000, a 1D tabulation uses 8 MB (long[]) — comfortable. For 2D with N=1,000,000: N² = 1 trillion cells — impossible. In bioinformatics, sequence alignment with 100M-character strings uses banded DP (only the diagonal ±B cells), Hirschberg's algorithm (O(N) space with traceback), or divide-and-conquer DP.

---

### 💻 Code Example

**Example 1 — Edit Distance (Levenshtein) — classic 2D tabulation:**
```java
int editDistance(String s1, String s2) {
    int m = s1.length(), n = s2.length();
    int[][] dp = new int[m+1][n+1];

    // Base cases: empty string transformations
    for (int i = 0; i <= m; i++) dp[i][0] = i;
    for (int j = 0; j <= n; j++) dp[0][j] = j;

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (s1.charAt(i-1) == s2.charAt(j-1))
                dp[i][j] = dp[i-1][j-1];
            else
                dp[i][j] = 1 + Math.min(dp[i-1][j-1],
                    Math.min(dp[i-1][j], dp[i][j-1]));
        }
    }
    return dp[m][n];
}
```

**Example 2 — Space-optimised edit distance (O(N) space):**
```java
int editDistSpaceOpt(String s1, String s2) {
    int m = s1.length(), n = s2.length();
    int[] prev = new int[n + 1], curr = new int[n + 1];
    for (int j = 0; j <= n; j++) prev[j] = j;

    for (int i = 1; i <= m; i++) {
        curr[0] = i;
        for (int j = 1; j <= n; j++) {
            if (s1.charAt(i-1) == s2.charAt(j-1))
                curr[j] = prev[j-1];
            else
                curr[j] = 1 + Math.min(prev[j-1],
                    Math.min(prev[j], curr[j-1]));
        }
        int[] tmp = prev; prev = curr; curr = tmp;
    }
    return prev[n];
}
```

---

### ⚖️ Comparison Table

| Aspect | Tabulation | Memoization |
|---|---|---|
| Direction | Bottom-up | Top-down |
| Stack | O(1) (iterative) | O(depth) (recursive) |
| Subproblems computed | All | Only reachable ones |
| Cache pattern | Sequential array | Random HashMap access |
| Space optimisable | ✓ (rolling vars) | ✗ (cache must retain all) |
| Easier to write | Sometimes | Usually |

How to choose: Start with memoization for clarity. Convert to tabulation when N is large (SO risk) or when profiling shows HashMap overhead or cache misses dominate.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Tabulation requires more space than memoization | Both use O(unique subproblems) for storage; tabulation can often be space-optimised further |
| Tabulation always computes more work than memoization | For fully-connected DP problems, they compute the same subproblems; for sparse problems, memoization may compute fewer |
| The order of loops doesn't matter | Loop order is critical — `dp[i][j]` must be filled after all its dependencies; wrong order gives silently wrong answers |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong loop direction causes incorrect results**

**Symptom:** Answer is wrong; some DP states are 0 or the default value when they shouldn't be.

**Root Cause:** Loop processes `dp[i]` before `dp[i-1]` is filled; reads a 0-initialised cell.

**Diagnostic:**
```java
// Print dp table after filling:
for (int i = 0; i <= m; i++)
    System.out.println(Arrays.toString(dp[i]));
// Look for unexpected 0s at positions that should be non-zero
```

**Fix:** Trace the recurrence `dp[i] = f(dp[i-1])` → loop must go `i = base → target`.

**Prevention:** Always trace the recurrence for ONE example by hand before coding the loop.

---

**2. Wrong answer from wrong sentinel value**

**Symptom:** Algorithm returns "impossible" for a case that IS possible, or returns an incorrect minimum.

**Root Cause:** Initial fill value conflicts with valid DP values. E.g., `Arrays.fill(dp, 0)` for a minimum-count problem where 0 is a valid intermediate result.

**Fix:** Use a sentinel clearly outside the valid range: `Integer.MAX_VALUE/2` or `amount+1` for "infinity" in minimisation problems. Avoid `Integer.MAX_VALUE` directly: `Integer.MAX_VALUE + 1` overflows.

**Prevention:** Document the invariant: "dp[i] = minimum coins, or INFTY = amount+1 if impossible."

---

**3. ArrayIndexOutOfBoundsException from wrong table size**

**Symptom:** AIOOBE on `dp[amount]` or `dp[m][n]`.

**Root Cause:** Table allocated as `new int[N]` but accessed at index `N`: needs `new int[N+1]`.

**Diagnostic:** Always check: what is the maximum index accessed? If `dp[amount]` is the answer, need `new int[amount+1]`.

**Prevention:** Table size = (max index) + 1. Write this as `new int[amount + 1]`, not `new int[amount]`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Memoization` — top-down counterpart; understanding both clarifies the trade-offs.
- `Array` — the DP table; sequential access pattern determines cache efficiency.
- `Dynamic Programming` — the general concept of which tabulation is the bottom-up implementation.

**Builds On This (learn these next):**
- `Longest Common Subsequence` — classic 2D tabulation application.
- `Knapsack Problem` — classic 2D tabulation with space optimisation.

**Alternatives / Comparisons:**
- `Memoization` — top-down, recursive, easier to write, O(depth) stack.
- `Space-Time Trade-off` — tabulation's rolling-row optimisation is a direct application.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Iterative DP: fill table from base cases  │
│              │ upward; no recursion, no stack risk       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Memoization fails on large N due to       │
│ SOLVES       │ StackOverflowError; tabulation never does │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Same subproblems as memoization, computed  │
│              │ in topological (dependency) order         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Large N (risk of SO); performance-critical│
│              │ (cache-friendly sequential iteration)     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only a fraction of subproblems needed     │
│              │ (memoization is lazier and uses less RAM) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No stack risk + cache-friendly vs computes│
│              │ ALL subproblems (memoization is lazier)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Lay each stair before stepping on it —   │
│              │  never jump before the ground is built"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dynamic Programming → Memoization → LCS   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Longest Common Subsequence with tabulation uses a 2D table of M×N. For sequences of length 1,000, this is 1,000,000 cells. A rolling-row optimisation reduces this to 2×N cells. However, if you need to also reconstruct the actual LCS sequence (not just its length), the rolling-row optimisation fails — you need the full table to trace back. Explain precisely why reconstruction requires the full table, and describe one alternative algorithm (Hirschberg's) that achieves O(N) space while still enabling reconstruction.

**Q2.** The subset-sum problem (can we select elements from an array summing to target T?) uses tabulation with a boolean dp[N+1][T+1] table. Both dimensions depend on input: N items and target T. For N=40, T=10^18 (representing realistic large integer inputs), this table is impossibly large. Explain why the tabulation approach fails for this input range while a different technique (meet-in-the-middle) succeeds, and what asymptotic complexity MitM achieves for this problem.

