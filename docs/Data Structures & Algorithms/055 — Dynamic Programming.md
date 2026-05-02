---
layout: default
title: "Dynamic Programming"
parent: "Data Structures & Algorithms"
nav_order: 55
permalink: /dsa/dynamic-programming/
number: "0055"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Recursion, Memoization, Tabulation (Bottom-Up DP), Time Complexity / Big-O
used_by: Knapsack Problem, Longest Common Subsequence, Dijkstra, Bellman-Ford
related: Greedy Algorithm, Divide and Conquer, Backtracking
tags:
  - algorithm
  - advanced
  - pattern
  - mental-model
  - deep-dive
  - first-principles
---

# 055 — Dynamic Programming

⚡ TL;DR — Dynamic Programming trades memory for speed by caching overlapping subproblem results, reducing exponential recursion to polynomial time.

| #055 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Recursion, Memoization, Tabulation (Bottom-Up DP), Time Complexity / Big-O | |
| **Used by:** | Knapsack Problem, Longest Common Subsequence, Dijkstra, Bellman-Ford | |
| **Related:** | Greedy Algorithm, Divide and Conquer, Backtracking | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to compute the 40th Fibonacci number. A naive recursive function calls `fib(38)` and `fib(39)`, which each call `fib(37)` and `fib(38)` again. The total calls grow as `2^N` — computing `fib(40)` requires over a billion recursive calls, all repeating work already done. Scale this to the coin change problem (how many ways to make $1.00 from coins?) and the space of recursive calls becomes astronomically large.

**THE BREAKING POINT:**
The fundamental issue is **overlapping subproblems**: the same sub-computation `fib(30)` is triggered from hundreds of distinct call paths. A computer with a wall-clock timer refuses to give an answer before a deadline — the algorithm is technically correct but computationally useless.

**THE INVENTION MOMENT:**
What if instead of recomputing `fib(30)` 800 times, you compute it once and **store** the result? Every future call simply looks up the table. Suddenly `fib(40)` takes exactly 40 additions. This is the core insight of Dynamic Programming: identify subproblems that recur, solve each exactly once, and cache the result. Bellman coined the term in the 1950s to describe this pattern formally. This is exactly why Dynamic Programming was created.

---

### 📘 Textbook Definition

**Dynamic Programming (DP)** is an algorithmic technique for solving optimisation or counting problems by breaking them into overlapping subproblems, solving each subproblem once, and storing solutions in a cache (memoisation table or bottom-up table). DP applies when a problem exhibits two properties: **optimal substructure** (the optimal solution to the full problem can be assembled from optimal solutions to subproblems) and **overlapping subproblems** (the same subproblems recur many times during recursion). DP transforms an exponential brute-force search into a polynomial-time algorithm by eliminating redundant computation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Solve each smaller version of your problem once, cache the answer, never repeat it.

**One analogy:**
> Imagine climbing a staircase. A forgetful climber recounts every step from the ground each time they want to know their height. A smart climber writes the step number on each step — one look gives the answer instantly. DP is writing on the steps.

**One insight:**
The hardest part of DP is not coding the cache — it is *recognising* the recurrence relation: "the answer to problem[N] can be expressed in terms of smaller problem[N-k]." Once you see the recurrence, the implementation is mechanical. The insight separates engineers who "memorise DP problems" from those who can derive solutions to unseen problems on a whiteboard.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The problem contains **overlapping subproblems**: the same sub-instance appears in multiple independent recursion branches.
2. The problem exhibits **optimal substructure**: the optimal answer for any prefix/suffix/subrange is derived from optimal answers to its parts — no "regret" about past choices can improve a globally optimal solution.
3. The state space is **finite and enumerable**: every distinct subproblem maps to a unique key in a table; the table has polynomial size.

**DERIVED DESIGN:**
Given these invariants, any correct implementation must: (1) define a **state** — a tuple of parameters that uniquely identifies a subproblem; (2) define a **transition** — a recurrence showing how `dp[state]` is computed from `dp[smaller states]`; (3) define a **base case** — the smallest subproblems whose answers are known directly; (4) **fill or recurse** the table in an order where dependencies are resolved before they are needed.

**Top-down (Memoisation):** Use recursion exactly as you would naively, but intercept each call — if the answer is cached, return it; otherwise compute and cache before returning.

**Bottom-up (Tabulation):** Identify a topological order over subproblems (usually iterating a dimension from smallest to largest), fill the table iteratively without recursion stack overhead. This is typically faster in practice due to no function-call overhead and better cache locality.

**Why DP beats brute-force when valid:**
Naive recursion explores `O(2^N)` nodes in the decision tree. DP collapses all nodes with identical state into one, reducing the tree to a DAG with `O(states)` nodes and `O(states × branching)` edges. For the 0/1 knapsack with N items and capacity W, this reduces `O(2^N)` to `O(N × W)`.

**THE TRADE-OFFS:**
**Gain:** Polynomial time (often `O(N²)` or `O(N×W)`) from exponential brute force.
**Cost:** Memory proportional to the state space — `O(N²)` or `O(N×W)` space, which is prohibitive for very large inputs. Also, recognising the correct state definition requires significant problem-solving skill.

---

### 🧪 Thought Experiment

**SETUP:**
Count the number of ways to climb `N = 5` stairs, taking 1 or 2 steps at a time. This is a classic DP counting problem.

**WHAT HAPPENS WITHOUT DYNAMIC PROGRAMMING:**
Call `ways(5)`. It calls `ways(4)` and `ways(3)`. `ways(4)` calls `ways(3)` and `ways(2)`. `ways(3)` is now computed **twice** — once from `ways(5)→ways(3)` and once from `ways(5)→ways(4)→ways(3)`. At `N=30`, `ways(3)` is recomputed millions of times. Total calls grow as Fibonacci(N) ≈ 1.618^N.

**WHAT HAPPENS WITH DYNAMIC PROGRAMMING:**
Allocate `dp[0..5]`. Set `dp[0]=1, dp[1]=1`. Iterate: `dp[i] = dp[i-1] + dp[i-2]`. Each subproblem is computed exactly once in left-to-right order. `dp[5] = 8` — computed in exactly 5 additions, never repeating.

**THE INSIGHT:**
The exponential blowup in naive recursion comes entirely from recomputing identical subproblems. DP's cache converts the recursion tree into a DAG — instead of `O(2^N)` nodes, it has `O(N)` nodes. The algorithm is not fundamentally smarter; it simply refuses to repeat work.

---

### 🧠 Mental Model / Analogy

> Dynamic Programming is like filling out a tax form. You don't know your final tax until you compute boxes A, B, and C first. Each box is a subproblem — you fill it once, write the number, and every later box that needs it just reads from the form. You never recompute a box.

- "Fill each box once" → solve each subproblem once
- "Write the number on the form" → store result in the DP table
- "Later boxes read from the form" → transition reads from `dp[smaller state]`
- "The final tax amount" → `dp[N]` — the answer to the full problem

Where this analogy breaks down: Tax forms have a fixed structure dictated externally. In DP, *you* must discover the subproblem decomposition from the problem structure. The hardest work in DP is designing the form, not filling it in.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of solving the same mini-problem a thousand times, solve it once, write the answer down, and look it up whenever you need it again. This turns a very slow computer problem into a fast one.

**Level 2 — How to use it (junior developer):**
Recognise the recurrence: "dp[i] = dp[i-1] + dp[i-2]" (stairs), "dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])" (knapsack). Choose top-down (add a `Map<State, Result>` cache to your recursive function) or bottom-up (iterate a table in increasing order). Always verify base cases. Check for off-by-one in table indexing.

**Level 3 — How it works (mid-level engineer):**
DP works on DAGs of subproblems. The state tuple must capture all information that distinguishes one subproblem from another — miss a dimension and different subproblems collide in the table, giving wrong answers. State compression (bitmasking for small sets) reduces memory from `O(2^N × N)` to `O(N)` for certain graph problems. Rolling array optimisation reduces space from `O(N²)` to `O(N)` when transition only depends on the previous row.

**Level 4 — Why it was designed this way (senior/staff):**
DP is the algorithmically correct response to problems with **matroid complement structure** where greedy fails. Bellman's principle of optimality formalises it: *a globally optimal policy has the property that, regardless of initial state and decision, the remaining decisions constitute an optimal policy with regard to the state resulting from the first decision.* This is optimal substructure stated precisely. DP fails when this principle does not hold — e.g., shortest path in graphs with negative cycles (no finite substructure exists). In competitive programming and interview contexts, recognising DP problems requires pattern matching across problem classes: interval DP, bitmask DP, tree DP, digit DP, profile DP.

---

### ⚙️ How It Works (Mechanism)

**Step 1 — Define the state.**
The state is the complete set of variables that uniquely identify a subproblem. For stair climbing: a single integer `i` (step index). For 0/1 knapsack: a pair `(i, remaining_capacity)`. For LCS: a pair `(i, j)` (position in each string). If your state is missing a variable, two distinct subproblems will share the same key and produce wrong answers.

**Step 2 — Write the recurrence.**
The recurrence expresses `dp[state]` in terms of `dp[smaller states]`:
```
Stair climbing:    dp[i] = dp[i-1] + dp[i-2]
0/1 Knapsack:      dp[i][w] = max(dp[i-1][w],
                     dp[i-1][w-wt[i]] + val[i])
LCS:               dp[i][j] = dp[i-1][j-1]+1
                     if s[i]==t[j]
                   else max(dp[i-1][j], dp[i][j-1])
```

**Step 3 — Identify base cases.**
Base cases are the smallest subproblems solvable without further decomposition. Incorrect base cases silently corrupt every dependent result — they are the most dangerous bugs in DP code.

**Step 4 — Choose top-down or bottom-up.**

```
┌──────────────────────────────────────────┐
│ TOP-DOWN (Memoisation)                   │
│                                          │
│  fib(N)                                  │
│    ↓                                     │
│  cache hit? → return immediately         │
│    ↓ miss                                │
│  compute fib(N-1) + fib(N-2)            │
│    ↓                                     │
│  store in cache → return                 │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ BOTTOM-UP (Tabulation)                   │
│                                          │
│  dp[0]=1, dp[1]=1                        │
│  for i in 2..N:                          │
│    dp[i] = dp[i-1] + dp[i-2]            │
│  return dp[N]                            │
└──────────────────────────────────────────┘
```

**Step 5 — Optimise memory if needed.**
If transition only reads from the previous row/column, replace the full 2D table with two 1D arrays (or one array updated in place). This reduces space from `O(N²)` to `O(N)` while keeping time complexity unchanged.

**Complexity analysis:**
- Time: `O(states × transitions per state)`
- Space: `O(states)` for naive table; reducible with rolling arrays

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Problem with exponential search space
→ Identify optimal substructure
→ Define state (tuple of parameters)
→ Write recurrence relation
→ [DYNAMIC PROGRAMMING ← YOU ARE HERE]
→ Fill dp table (bottom-up) or recurse+cache (top-down)
→ Read dp[final state] = answer
```

**FAILURE PATH:**
```
Wrong state definition (missing a parameter)
→ Two distinct subproblems share same key
→ Incorrect cached value returned
→ Wrong final answer with no runtime error
→ Debug: add assertions on state uniqueness,
  compare against brute-force on small inputs
```

**WHAT CHANGES AT SCALE:**
For large state spaces (e.g., N=10⁶ items, W=10⁶ capacity), the `O(N×W)` table requires 10¹² entries — physically impossible. This forces problem reformulation: use greedy if applicable, heuristics, or segment-tree-optimised DP (for convex hull trick, divide-and-conquer DP optimisation), which reduces `O(N²)` transitions to `O(N log N)` for problems with the quadrangle inequality property.

---

### 💻 Code Example

**Example 1 — Fibonacci (naive vs memoised vs bottom-up):**
```java
// BAD: exponential O(2^N) — recomputes every subproblem
int fibNaive(int n) {
    if (n <= 1) return n;
    return fibNaive(n-1) + fibNaive(n-2);
}

// GOOD top-down: O(N) time, O(N) space
Map<Integer,Long> memo = new HashMap<>();
long fibMemo(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n);
    long result = fibMemo(n-1) + fibMemo(n-2);
    memo.put(n, result);
    return result;
}

// GOOD bottom-up: O(N) time, O(1) space (rolling)
long fibDP(int n) {
    if (n <= 1) return n;
    long prev2 = 0, prev1 = 1;
    for (int i = 2; i <= n; i++) {
        long cur = prev1 + prev2;
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}
```

**Example 2 — 0/1 Knapsack (production pattern):**
```java
// items[i] = {weight, value}, capacity = W
int knapsack(int[] weights, int[] values,
             int n, int W) {
    // dp[i][w] = max value using first i items,
    // weight limit w
    int[][] dp = new int[n+1][W+1];
    for (int i = 1; i <= n; i++) {
        int wt = weights[i-1];
        int val = values[i-1];
        for (int w = 0; w <= W; w++) {
            // don't take item i
            dp[i][w] = dp[i-1][w];
            // take item i if it fits
            if (w >= wt) {
                dp[i][w] = Math.max(dp[i][w],
                    dp[i-1][w-wt] + val);
            }
        }
    }
    return dp[n][W];
}
// Time: O(N*W), Space: O(N*W) → reduce to O(W)
// by iterating w in reverse with a 1D array
```

**Example 3 — Space-optimised knapsack:**
```java
int knapsack1D(int[] weights, int[] values,
               int n, int W) {
    int[] dp = new int[W+1];
    for (int i = 0; i < n; i++) {
        // MUST iterate right-to-left for 0/1 knapsack
        // to avoid using item i twice
        for (int w = W; w >= weights[i]; w--) {
            dp[w] = Math.max(dp[w],
                dp[w - weights[i]] + values[i]);
        }
    }
    return dp[W];
}
// Space: O(W) — critical insight: reverse iteration
// prevents item from being chosen multiple times
```

**Example 4 — Longest Common Subsequence (diagnostic):**
```java
int lcs(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m+1][n+1];
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (a.charAt(i-1) == b.charAt(j-1))
                dp[i][j] = dp[i-1][j-1] + 1;
            else
                dp[i][j] = Math.max(
                    dp[i-1][j], dp[i][j-1]);
        }
    }
    return dp[m][n];
}
// To trace back the actual subsequence, walk
// dp table backwards from dp[m][n] to dp[0][0]
```

---

### ⚖️ Comparison Table

| Paradigm | Time | Space | Globally Optimal | When to Use |
|---|---|---|---|---|
| **Dynamic Programming** | O(N²) typical | O(states) | Yes (with opt. substructure) | Overlapping subproblems, optimisation/counting |
| Greedy | O(N log N) | O(1) | Only if GCP holds | Scheduling, MST, fractional knapsack |
| Divide & Conquer | O(N log N) | O(log N) | Yes (non-overlapping) | Merge sort, binary search |
| Backtracking | O(2^N) | O(N) | Yes (exhaustive) | Constraint satisfaction, all solutions |
| Brute Force | O(N!) or O(2^N) | O(1) | Yes | Only for very small N |

How to choose: Use DP when subproblems overlap and you need the global optimum. Use greedy when you can prove the greedy choice property. Use divide-and-conquer when subproblems are independent.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DP is always faster than recursion | DP is only faster when subproblems overlap; for non-overlapping problems (merge sort), memoisation adds overhead with no benefit |
| Memoisation and DP are the same thing | Memoisation is top-down DP; bottom-up tabulation is also DP. Both are forms of DP, but have different space/constant-factor tradeoffs |
| DP always requires a 2D table | Many DP problems require only a 1D array, or even two variables (Fibonacci space-optimised). State dimension equals the number of independent parameters, not the size of the problem |
| DP guarantees optimal solution for any problem | DP only guarantees optimal solutions when optimal substructure holds. Problems with non-optimal substructure (e.g., longest path in a graph with cycles) cannot be solved with standard DP |
| Once you see the recurrence, DP is easy | Finding the recurrence is the hard part. The coding is mechanical once the state and transition are correctly defined |
| DP is only for competitive programming | DP is used in production: route planning (Bellman-Ford), NLP (Viterbi algorithm), resource scheduling, diff algorithms (Myers diff uses LCS) |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong state definition — missing a parameter**

**Symptom:** DP produces wrong answers on certain inputs but correct answers on others; results differ from brute-force reference.

**Root Cause:** The state tuple does not uniquely identify a subproblem. Two distinct situations (different "histories") map to the same key, so the cached result from one is incorrectly reused for the other.

**Diagnostic:**
```java
// Compare DP vs brute force on all small inputs:
for (int n = 0; n <= 15; n++) {
    assert dpSolve(n) == bruteForceSolve(n)
      : "Mismatch at n=" + n;
}
```

**Fix:** Add the missing dimension to the state. If item already-selected matters, track which items are used. If direction matters in grid problems, track direction.

**Prevention:** Before coding, enumerate all parameters that affect the answer. Each must be a state dimension.

---

**2. Off-by-one in base cases or table indexing**

**Symptom:** Final answer is off by 1, or `ArrayIndexOutOfBoundsException` at runtime.

**Root Cause:** `dp` indexed at `0..N` but array allocated as `new int[N]` (size N, indices 0..N-1). Or base case set to `dp[1]=0` when it should be `dp[1]=1`.

**Diagnostic:**
```java
// Print first 5 dp values vs hand-computed values:
for (int i = 0; i <= 5; i++)
    System.out.println("dp["+i+"]="+dp[i]);
// Compare with pen-and-paper calculation
```

**Fix:** Always allocate `new int[N+1]` for 0-indexed DP over [0..N]. Write base cases explicitly on paper before coding.

**Prevention:** Test on N=0, N=1, N=2 before testing N=100. Base case bugs appear immediately.

---

**3. Using item twice in 0/1 knapsack**

**Symptom:** Knapsack returns a value higher than achievable by selecting each item at most once.

**Root Cause:** 1D bottom-up knapsack iterates `w` from left-to-right (small W to large W). When computing `dp[w]`, `dp[w - weight[i]]` has already been updated in this same iteration, meaning item `i` can be added multiple times.

**Diagnostic:**
```java
// Test: single item of weight 1, value 10,
// capacity 5. Answer should be 10, not 50.
assert knapsack(new int[]{1}, new int[]{10},
                1, 5) == 10;
```

**Fix:**
```java
// BAD: left-to-right allows reusing items
for (int w = weights[i]; w <= W; w++)
    dp[w] = Math.max(dp[w],
              dp[w-weights[i]] + values[i]);

// GOOD: right-to-left prevents reuse
for (int w = W; w >= weights[i]; w--)
    dp[w] = Math.max(dp[w],
              dp[w-weights[i]] + values[i]);
```

**Prevention:** Comment every 1D knapsack loop direction with its rationale.

---

**4. Stack overflow in top-down DP on large N**

**Symptom:** `StackOverflowError` on inputs with N > ~10,000.

**Root Cause:** Top-down DP uses call stack proportional to recursion depth. For `fib(100000)`, the recursion depth is 100,000 frames — exceeding default JVM stack size (~512 calls/frame).

**Diagnostic:**
```bash
# Check stack depth at failure:
java -Xss8m -jar app.jar  # Increase stack size
# Or switch to bottom-up to eliminate recursion
```

**Fix:** Convert to bottom-up tabulation for large N, or use iterative memoisation with an explicit stack.

**Prevention:** Use bottom-up DP when N > 10,000.

---

**5. Negative space usage on interval DP problems**

**Symptom:** Out-of-memory or TLE (time limit exceeded) on interval DP problems where N=5000 produces an O(N³) algorithm.

**Root Cause:** Interval DP on `dp[i][j]` for all pairs `(i,j)` has O(N²) states and O(N) transitions — cubic total. For N=5000, this is 125 billion operations.

**Diagnostic:**
```bash
# Profile with async-profiler on JVM:
java -agentpath:/async-profiler/libasyncProfiler.so
     =start,event=cpu,file=profile.html App
# Look for hot DP transition loop
```

**Fix:** Apply divide-and-conquer DP optimisation or the convex hull trick if the problem satisfies the quadrangle inequality (`dp[i][j] + dp[i'][j'] ≤ dp[i][j'] + dp[i'][j]`). Reduces O(N³) to O(N² log N) or O(N²).

**Prevention:** Analyse DP complexity with state count × transition count before coding. n=1000 is fine for O(N²); n=5000 requires O(N² log N) or better.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` — DP top-down is recursion with caching; you must understand the call stack before adding memoisation.
- `Memoization` — the top-down form of DP; understand cache lookup/store pattern first.
- `Tabulation (Bottom-Up DP)` — the iterative form of DP; understanding table-fill order is core to correctness.
- `Time Complexity / Big-O` — DP's value is converting O(2^N) to O(N²); you must quantify this improvement.

**Builds On This (learn these next):**
- `Knapsack Problem` — the canonical DP problem class; mastering it unlocks all DP variants.
- `Longest Common Subsequence` — interval DP with string comparison; a stepping stone to edit distance and other text algorithms.
- `Bellman-Ford` — shortest-path via DP on edges; DP on graphs.
- `Dijkstra` — greedy shortest-path that emerges from DP relaxation insight.

**Alternatives / Comparisons:**
- `Greedy Algorithm` — faster (O(N log N)) but only correct when greedy choice property holds; DP is the fallback when greedy fails.
- `Divide and Conquer` — similar decomposition but subproblems do not overlap; merge sort uses D&C, not DP.
- `Backtracking` — exhaustive search that can explore all solutions; DP prunes the space when optimal substructure guarantees you never need suboptimal sub-solutions.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cache-driven optimisation: solve each     │
│              │ subproblem once, reuse the result         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Exponential brute force from overlapping  │
│ SOLVES       │ recursive subproblems                     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Optimal substructure + overlapping        │
│              │ subproblems = DP applies. Both required.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Optimisation/counting, subproblems recur, │
│              │ globally optimal answer required          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Subproblems are independent (D&C),        │
│              │ or greedy choice property holds           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N²) time vs O(2^N) brute force;        │
│              │ costs O(states) memory                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fill the table once; never recompute"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Knapsack Problem → LCS → Bellman-Ford     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The coin change problem with denominations `[1, 5, 6, 9]` and target `T = 11` yields different results from greedy (which picks 9+1+1 = 3 coins) vs DP (which finds 6+5 = 2 coins). Trace the DP table for `dp[0..11]` using the recurrence `dp[t] = 1 + min(dp[t - c] for c in coins)`. At which value of `t` does DP first diverge from the greedy choice, and what does this reveal about the relationship between overlapping subproblems and the coin denominations structure?

**Q2.** A grid-path DP problem computes the number of paths from top-left to bottom-right of an M×N grid moving only right or down. The standard solution runs in O(M×N) time and O(M×N) space. Propose a space optimisation that reduces space to O(min(M,N)). Then consider: if the grid contains obstacle cells that block passage, what additional state would be needed if you also needed to track the number of paths that pass through exactly one specific "checkpoint" cell? How does adding this constraint change the state definition?

