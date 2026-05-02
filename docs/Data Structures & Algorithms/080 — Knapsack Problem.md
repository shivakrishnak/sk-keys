---
layout: default
title: "Knapsack Problem"
parent: "Data Structures & Algorithms"
nav_order: 80
permalink: /dsa/knapsack-problem/
number: "0080"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Dynamic Programming, Recursion, Backtracking
used_by: Resource Allocation, Bin Packing, Approximation Algorithms
related: Dynamic Programming, Greedy Algorithm, NP-Complete Problems
tags:
  - algorithm
  - advanced
  - deep-dive
  - datastructure
  - pattern
---

# 080 — Knapsack Problem

⚡ TL;DR — The Knapsack Problem selects items with maximum total value without exceeding a weight capacity, solved optimally in O(N×W) with DP despite being NP-complete in general.

| #0080 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Dynamic Programming, Recursion, Backtracking | |
| **Used by:** | Resource Allocation, Bin Packing, Approximation Algorithms | |
| **Related:** | Dynamic Programming, Greedy Algorithm, NP-Complete Problems | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A thief breaks into a museum. The bag holds 50 kg. There are 20 items: a 10 kg painting worth $60,000, a 40 kg sculpture worth $120,000, etc. The thief wants to maximise value taken. Trying all subsets: 2^20 = 1 million combinations. At 100 items: 2^100 ≈ 10^30 combinations — impossible to check in any practical time.

THE BREAKING POINT:
Pure brute-force enumeration is exponential. The observation being wasted: most combinations differ only in whether one specific item is included or not. If you already know the best selection for capacity 49 kg with the first 19 items, you only need one more check to determine the best for 50 kg with all 20 items.

THE INVENTION MOMENT:
Define `dp[i][w]` = maximum value using items 1..i with weight limit w. Either item i is included (add its value, reduce capacity by its weight) or excluded. This produces an O(N×W) table — polynomial in N and W. The **0/1 Knapsack** is technically NP-hard (W can be exponentially large in binary representation), but in practice W is bounded, making DP efficient. This is exactly why **Knapsack Problem** DP is a fundamental technique.

---

### 📘 Textbook Definition

The **0/1 Knapsack Problem** is: given N items each with weight `w[i]` and value `v[i]`, and a knapsack capacity W, select a subset of items to include (each at most once) such that the total weight ≤ W and total value is maximised. The standard dynamic programming solution defines `dp[i][w]` = maximum value achievable using items 1..i with capacity w. Recurrence: `dp[i][w] = max(dp[i-1][w], dp[i-1][w-w[i]] + v[i])` if `w[i] ≤ w`, else `dp[i-1][w]`. Time: O(N×W). Space: O(N×W) or O(W) with rolling array. The **unbounded knapsack** allows unlimited copies of each item; the **fractional knapsack** allows partial items (solvable greedily in O(N log N)).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Fill a bag to maximise value without exceeding weight — try each item: include it or skip it.

**One analogy:**
> Packing a hiking backpack for maximum utility: water bottle (1 kg, essential), sleeping bag (3 kg, important), gourmet food (4 kg, nice-to-have). Your pack holds 5 kg. You can't bring everything — choose water + sleeping bag (4 kg, very useful) over just gourmet food (4 kg, less useful). The DP table is your decision sheet for every sub-capacity.

**One insight:**
The DP's O(N×W) complexity looks polynomial, but W can be encoded in log₂(W) bits, making the problem technically **pseudo-polynomial** (polynomial in the numeric value W, exponential in the bit-length of W). This is why 0/1 Knapsack is NP-complete in the classical sense: if W = 2^N, the DP table has 2^N columns — exponential. In practice, W is always bounded, making DP feasible.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. **Optimal substructure:** The best selection for capacity w using items 1..i contains the best selection for the remaining capacity using items 1..i-1.
2. **Overlapping subproblems:** The subproblem `(i-1, w)` is needed by multiple items i — recomputing it recursively is exponential without memoisation.
3. **Integer weights:** DP with O(N×W) space requires W to be an integer (or discretizable). Fractional weights with continuous capacity cannot use this DP directly.

DERIVED DESIGN:
The recurrence follows from a binary choice for each item:
- **Exclude item i:** `dp[i][w] = dp[i-1][w]` — best without item i.
- **Include item i:** `dp[i][w] = dp[i-1][w - w[i]] + v[i]` — use item i, best for remaining.

Taking the maximum of these two determines the optimal choice. The table fills left-to-right, top-to-bottom in O(N×W) operations.

**Space optimisation:**
Since row i depends only on row i-1, a single 1D array of length W+1 (filled right-to-left) gives O(W) space.

THE TRADE-OFFS:
Gain: Exact optimal solution in O(N×W) — feasible when W is reasonable (up to ~10⁷).
Cost: O(N×W) time and space — infeasible for W > 10⁸. NP-hard for arbitrary W (no known polynomial algorithm in terms of input bit-length). Items must be indivisible (0/1).

---

### 🧪 Thought Experiment

SETUP:
Weights: [2, 3, 4], Values: [3, 4, 5], Capacity: 5.

WHAT HAPPENS WITH BRUTE FORCE (2^3 = 8 subsets):
- {}: value=0. {A}: value=3, weight=2 ✓. {B}: value=4, weight=3 ✓.
- {C}: value=5, weight=4 ✓. {A,B}: value=7, weight=5 ✓. {A,C}: value=8, weight=6 ✗.
- {B,C}: value=9, weight=7 ✗. {A,B,C}: too heavy ✗.
- Best: {A,B} value=7. 8 subsets checked.

WHAT HAPPENS WITH DP:
dp[weight=0..5], 3 items:
After item A(w=2,v=3): dp=[0,0,3,3,3,3].
After item B(w=3,v=4): dp=[0,0,3,4,4,7]. (capacity 5: include B(4)+dp[2]=3 → 7).
After item C(w=4,v=5): dp=[0,0,3,4,5,7]. (capacity 5: include C(5)+dp[1]=0 → 5 < 7; keep 7).
Result: dp[5]=7. Only 18 operations (3×6) instead of checking 8 subsets.

THE INSIGHT:
DP avoids recomputation by storing intermediate results. When computing `dp[C=5]`, the value `dp[B=2]=3` (best for capacity 3 after item A) is already known — no re-exploration. The overlapping subproblems are all the `(capacity, item-prefix)` pairs, each computed exactly once.

---

### 🧠 Mental Model / Analogy

> The DP table is a decision worksheet. Each row is an item; each column is a capacity. Each cell says: "The best I can do with the first i items and exactly j kilograms available." You fill it cell by cell, asking: "Is this item worth including?" — always looking back one row and potentially several columns.

"Item row" → one item's include/exclude decision
"Capacity column" → available weight budget
"Previous row same column" → exclude this item's value
"Previous row, reduced column" → include this item's value
"Cell value" → best total value for this item prefix + capacity

Where this analogy breaks down: The 1D space-optimised version fills right-to-left to avoid using the same item twice in a single pass — this "overwrite order" has no direct physical analogy but is a crucial implementation detail.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The Knapsack Problem asks: given a list of items with weights and values, and a bag with a weight limit, which items should you take to maximise value? It's about making the best subset choice under a constraint.

**Level 2 — How to use it (junior developer):**
Build a 2D `dp[N+1][W+1]` table. Fill row by row: for each item i, for each capacity w, if `w[i-1] ≤ w`, take the max of excluding (`dp[i-1][w]`) or including (`dp[i-1][w-w[i-1]] + v[i-1]`). Otherwise copy the previous row. Answer is `dp[N][W]`. To find which items were selected, backtrack from `dp[N][W]`.

**Level 3 — How it works (mid-level engineer):**
Space optimisation: replace the 2D table with a 1D array `dp[W+1]`. Fill from right to left (capacity W down to `w[i]`) to ensure each item is counted at most once. For unbounded knapsack, fill left to right (item can be used multiple times). Meet-in-the-middle splits items into two halves of size N/2, enumerates all 2^(N/2) subsets of each half (~32,000 for N=30), then binary searches for complementary subsets: O(2^(N/2) × log(2^(N/2))) = O(2^(N/2) × N) — feasible for N ≤ 40.

**Level 4 — Why it was designed this way (senior/staff):**
0/1 Knapsack is in NP (solutions verifiable in polynomial time) and NP-hard (3-Partition, Subset Sum reduce to it). The O(N×W) DP is pseudo-polynomial — it becomes polynomial when W is polynomial in N. The FPTAS (Fully Polynomial-Time Approximation Scheme) rounds item values to reduce effective W, trading a (1+ε) approximation factor for O(N²/ε) time — guaranteeing a solution within (1+ε) of optimal in polynomial time. This makes Knapsack one of the most studied NP-hard problems: it has the best known approximation guarantees of any NP-hard problem.

---

### ⚙️ How It Works (Mechanism)

**2D DP table (3 items, capacity 5):**

```
┌──────────────────────────────────────────────┐
│ Items: A(w=2,v=3), B(w=3,v=4), C(w=4,v=5)  │
│ Capacity 0..5                                │
│                                              │
│      cap: 0  1  2  3  4  5                  │
│ init:     0  0  0  0  0  0                  │
│ +A(2,3):  0  0  3  3  3  3                  │
│ +B(3,4):  0  0  3  4  4  7  ← A+B at cap 5 │
│ +C(4,5):  0  0  3  4  5  7  ← A+B still best│
│                                              │
│ Answer: dp[3][5] = 7                         │
└──────────────────────────────────────────────┘
```

**1D Space-Optimised (fill right-to-left):**

```
┌──────────────────────────────────────────────┐
│ dp = [0,0,0,0,0,0] (capacity 0..5)           │
│                                              │
│ Item A (w=2,v=3): fill from cap=5 down to 2  │
│   dp[5]=max(dp[5],dp[3]+3)=max(0,3)=3        │
│   dp[4]=max(dp[4],dp[2]+3)=3                 │
│   dp[3]=max(dp[3],dp[1]+3)=3                 │
│   dp[2]=max(dp[2],dp[0]+3)=3                 │
│   → dp=[0,0,3,3,3,3]                         │
│                                              │
│ (right-to-left prevents using A twice)       │
└──────────────────────────────────────────────┘
```

**Backtracking to find selected items:**
Start from `dp[N][W]`. For each item i from N to 1: if `dp[i][w] != dp[i-1][w]`, item i was included. Subtract `w[i]` from w.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
N items with (weight, value) pairs + capacity W
→ Validate: W is bounded integer
→ [KNAPSACK DP ← YOU ARE HERE]
  → Fill dp[N][W] table in O(N×W)
  → dp[N][W] = maximum value
  → Backtrack to find selected items
→ Apply: cargo loading, investment selection,
  feature flag packing, test suite selection
```

FAILURE PATH:
```
W too large → OOM or TLE
→ System: heap overflow on dp array allocation
→ Fix: use approximation (FPTAS, greedy with ratio sort)
→ Diagnostic: estimate N × W × 4 bytes;
  if > JVM heap: switch to FPTAS ε=0.01
```

WHAT CHANGES AT SCALE:
In cloud resource optimisation (selecting VM types to minimise cost for given CPU/memory requirements), W can represent millions of memory increments — O(N×W) DP is infeasible. Production systems use:
1. Greedy by value/weight ratio (fractional knapsack: optimal; 0/1: 2-approximation).
2. LP relaxation + branch-and-bound for near-optimal with pruning.
3. FPTAS for guaranteed (1+ε)-optimal in O(N²/ε) time.

---

### 💻 Code Example

**Example 1 — 0/1 Knapsack (2D DP):**
```java
int knapsack(int[] w, int[] v, int W) {
    int n = w.length;
    int[][] dp = new int[n+1][W+1];
    for (int i = 1; i <= n; i++) {
        for (int cap = 0; cap <= W; cap++) {
            dp[i][cap] = dp[i-1][cap]; // exclude
            if (w[i-1] <= cap)
                dp[i][cap] = Math.max(dp[i][cap],
                    dp[i-1][cap - w[i-1]] + v[i-1]);
        }
    }
    return dp[n][W];
}
```

**Example 2 — Space-optimised (1D DP):**
```java
int knapsack1D(int[] w, int[] v, int W) {
    int[] dp = new int[W+1];
    for (int i = 0; i < w.length; i++) {
        // Right-to-left to avoid using item twice
        for (int cap = W; cap >= w[i]; cap--) {
            dp[cap] = Math.max(dp[cap],
                dp[cap - w[i]] + v[i]);
        }
    }
    return dp[W];
}
```

**Example 3 — Unbounded knapsack (left-to-right):**
```java
int unboundedKnapsack(int[] w, int[] v, int W) {
    int[] dp = new int[W+1];
    for (int cap = 1; cap <= W; cap++) {
        for (int i = 0; i < w.length; i++) {
            if (w[i] <= cap)
                dp[cap] = Math.max(dp[cap],
                    dp[cap - w[i]] + v[i]);
            // Left-to-right allows reusing items
        }
    }
    return dp[W];
}
```

**Example 4 — Fractional knapsack (greedy, optimal):**
```java
double fractionalKnapsack(int[] w, int[] v, int W) {
    // Sort by value/weight ratio descending
    Integer[] idx = IntStream.range(0,w.length)
        .boxed().toArray(Integer[]::new);
    Arrays.sort(idx, (a,b) ->
        Double.compare((double)v[b]/w[b],
                       (double)v[a]/w[a]));
    double total = 0;
    int remaining = W;
    for (int i : idx) {
        if (remaining <= 0) break;
        int take = Math.min(w[i], remaining);
        total += (double) take / w[i] * v[i];
        remaining -= take;
    }
    return total;
}
```

---

### ⚖️ Comparison Table

| Variant | Algorithm | Time | Optimal | Use Case |
|---|---|---|---|---|
| **0/1 Knapsack** | DP | O(N×W) | Yes | Items cannot be split |
| Unbounded Knapsack | DP (L→R) | O(N×W) | Yes | Unlimited copies per item |
| Fractional Knapsack | Greedy (ratio sort) | O(N log N) | Yes | Items can be divided |
| Bounded Knapsack | Binary split + DP | O(N×W×log M) | Yes | At most M copies per item |
| Multi-Dimensional | DP | O(N×W₁×W₂) | Yes | Multiple constraints |

How to choose: Use fractional knapsack when items are divisible (O(N log N), optimal by greedy). Use 0/1 DP when items are indivisible and W is manageable. Use FPTAS when W is too large for exact DP but approximation suffices.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Greedy (sort by value/weight ratio) solves 0/1 Knapsack optimally | Greedy is optimal ONLY for fractional knapsack. For 0/1: items={w=2,v=3; w=3,v=4; w=3,v=4}, W=6. Greedy by ratio picks w=2 (ratio 1.5) → then runs out of space optimally, but DP picks {w=3,v=4;w=3,v=4}=8 > 3+4=7. |
| The O(N×W) DP solution proves 0/1 Knapsack is polynomial | Pseudo-polynomial. W can be exponentially large in its binary representation. If W=2^N, the table has 2^N columns — exponential time. The problem is NP-hard in terms of input bit length. |
| The 1D DP fills left-to-right | 0/1 Knapsack requires right-to-left fill to prevent using the same item twice. Left-to-right solves unbounded knapsack (unlimited copies). Using L→R for 0/1 produces wrong results. |
| Items not selected don't affect the DP | The order items are processed doesn't affect the final answer for 0/1 knapsack (unlike the 1D fill direction). Any permutation of items produces the same dp[N][W]. |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong fill direction in 1D DP (double-counting)**

Symptom: 0/1 knapsack returns higher value than possible; items appear selected multiple times.

Root Cause: Left-to-right fill allows updating `dp[cap]` using an already-updated `dp[cap - w[i]]` in the same pass — item i counted twice.

Diagnostic:
```java
// Test: weights=[2], values=[3], capacity=4
// 0/1: best value = 3 (select item once)
// If result = 6: double-counting bug (fills left-to-right)
assert knapsack1D(new int[]{2}, new int[]{3}, 4) == 3;
```

Fix: Fill from `W` down to `w[i]` (right-to-left) for 0/1 knapsack.

Prevention: Comment fill direction; add unit test for single-item inputs.

---

**2. Array index out of bounds for large W**

Symptom: `OutOfMemoryError` or `NegativeArraySizeException` when W > Integer.MAX_VALUE / 4.

Root Cause: `new int[W+1]` allocation fails for W = 10^8 (400 MB for int array alone).

Diagnostic:
```java
long estimatedBytes = (long)(n + 1) * (W + 1) * 4;
System.out.println("Estimated: " + estimatedBytes/1e6 + " MB");
```

Fix: Use FPTAS or meet-in-the-middle when W > 10^7. For 1D DP: `new int[W+1]` only requires W+1 ints ≈ 4 × W bytes.

Prevention: Validate W before allocation; document max supported W in API.

---

**3. Forgetting to guard `cap - w[i] >= 0`**

Symptom: `ArrayIndexOutOfBoundsException` for items with weight > some capacity values.

Root Cause: Without checking `w[i-1] <= cap`, accessing `dp[i-1][cap - w[i-1]]` with `cap < w[i-1]` gives a negative index.

Diagnostic:
```java
// Check: item weight 5 with capacity 3 → cap - w = -2
// Guard: if (w[i-1] <= cap) dp[i][cap] = max(...)
```

Fix: Always guard `if (w[i-1] <= cap)` or in 1D: loop from `W` down to `w[i]` (loop condition prevents negative index).

Prevention: The 1D right-to-left loop bound `for (cap = W; cap >= w[i]; cap--)` naturally prevents this.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dynamic Programming` — Knapsack is a canonical DP problem; optimal substructure and overlapping subproblems must be understood.
- `Recursion` — The top-down recursive formulation with memoisation is the mental model for the recurrence.
- `Backtracking` — Exact enumeration via backtracking is the exponential alternative; DP avoids its redundancy.

**Builds On This (learn these next):**
- `NP-Complete Problems` — 0/1 Knapsack is NP-complete; understanding complexity classes explains why O(N×W) doesn't contradict this.
- `Approximation Algorithms` — FPTAS for knapsack is one of the best approximation results for an NP-hard problem.
- `Resource Allocation` — Bin packing, scheduling, and portfolio optimisation all generalise the knapsack model.

**Alternatives / Comparisons:**
- `Greedy Algorithm` — Optimal for fractional knapsack; suboptimal (but fast) for 0/1 knapsack.
- `Branch and Bound` — Exact algorithm for NP-hard combinatorial problems; better than DP in practice for large W.
- `Integer Linear Programming` — General framework subsuming knapsack; solved by ILP solvers (CPLEX, Gurobi).

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Select items for max value under weight   │
│              │ constraint; each item 0/1 (include/skip)  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ 2^N brute-force subset enumeration →      │
│ SOLVES       │ O(N×W) pseudo-polynomial DP               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Each cell = best choice for (items 1..i,  │
│              │ capacity w); each item: include or exclude │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Items indivisible; W bounded (≤ 10^7);    │
│              │ exact optimum required                    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ W > 10^8 (use FPTAS); items divisible     │
│              │ (use fractional knapsack greedy O(N log N))│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Exact optimum O(N×W) vs pseudo-polynomial │
│              │ — NP-hard for W exponential in N          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pack the best subset without overflow"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ FPTAS → Branch & Bound → ILP Solvers      │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The 0/1 Knapsack DP runs in O(N×W). Yet the problem is NP-complete. The apparent contradiction is resolved by noting O(N×W) is pseudo-polynomial — exponential in the *bit-length* of W. Construct an explicit example where W = 2^N, showing that the DP table has 2^N columns and thus O(N × 2^N) time — exponential in N. Now explain why the FPTAS achieves (1+ε)-optimal in O(N²/ε) time by "scaling and rounding" item values: what exactly is rounded, why does this make W polynomial in N, and what is the worst-case error guarantee?

**Q2.** Cloud providers offer 50 VM types with different CPU, memory, and cost profiles. You need to select VM instances to run 200 microservices, each with CPU and memory requirements, minimising total cost. This is a 2-dimensional (multi-constraint) knapsack: one constraint for CPU, one for memory. Why does the standard 1D DP not apply directly? What is the complexity of the 2D DP extension, and at what point (number of constraints K) does the DP become impractical compared to LP relaxation with rounding?

