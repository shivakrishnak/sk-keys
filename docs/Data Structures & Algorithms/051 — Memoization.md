---
layout: default
title: "Memoization"
parent: "Data Structures & Algorithms"
nav_order: 51
permalink: /dsa/memoization/
number: "0051"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Recursion, HashMap
used_by: Dynamic Programming, Tabulation (Bottom-Up DP)
related: Tabulation (Bottom-Up DP), Dynamic Programming, LRU Cache
tags:
  - algorithm
  - intermediate
  - performance
  - pattern
---

# 051 — Memoization

⚡ TL;DR — Memoization caches the results of recursive calls so each unique subproblem is computed only once, converting exponential recursion into polynomial time.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #051         │ Category: Data Structures & Algorithms │ Difficulty: ★★☆        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Recursion, HashMap                     │                        │
│ Used by:     │ Dynamic Programming, Tabulation        │                        │
│ Related:     │ Tabulation, Dynamic Programming, Cache │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Computing Fibonacci(40) with naïve recursion calls `fib(39)` and `fib(38)`. Each of those calls the same function again, and `fib(38)` is computed twice independently — each call spawning its own entire subtree. `fib(2)` is computed 1,134,903,170 times for fib(45). The total calls grow as O(2^N) — exponential.

THE BREAKING POINT:
Recursive algorithms naturally express problems in terms of subproblems. But when the same subproblem is solved repeatedly from scratch each time it's needed, the work explodes exponentially. The algorithm is correct but catastrophically inefficient.

THE INVENTION MOMENT:
Before returning a recursive result, store it in a cache (typically a HashMap). On the next call with the same arguments, return the cached result immediately. Each unique subproblem is now solved exactly once. The exponential O(2^N) becomes polynomial O(N) because the number of *unique* subproblems is O(N). This is exactly why Memoization was created.

### 📘 Textbook Definition

**Memoization** is a top-down dynamic programming technique where recursive calls cache their results so that each unique subproblem is computed at most once. A cache maps function arguments to return values. When a function is called with arguments previously computed, the cached result is returned in O(1). This converts recursive algorithms with overlapping subproblems from exponential time to polynomial time matching the number of unique subproblem combinations.

### ⏱️ Understand It in 30 Seconds

**One line:**
Remember what you've already computed so you never solve the same subproblem twice.

**One analogy:**
> A math student solving a long calculation writes each intermediate result in the margin. When the same intermediate answer is needed again later, they look it up instead of recalculating. This is memoization — a personal lookup table built while working.

**One insight:**
Memoization requires two conditions: **overlapping subproblems** (the same subproblem is encountered multiple times) and **optimal substructure** (the solution to a problem can be built from solutions to subproblems). When both are present, memoization converts any correct-but-slow recursive solution to an efficient one automatically.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A function's result is uniquely determined by its arguments (it must be *pure* — no side effects, no global state).
2. The same unique (argument combination) can appear multiple times in the recursion tree.
3. Once a result is cached, all future calls with the same arguments can reuse it in O(1).

DERIVED DESIGN:
The cache maps `args → result`. For single-integer argument (like fib), this is a `HashMap<Integer, Long>` or a simple array. For compound arguments (like DP on (i, j) indices), use a `HashMap<String, Long>` with a key like `"i,j"`, or a 2D array `dp[i][j]`.

**Time complexity with memoization:**
Without: O(branches ^ depth). With: O(unique subproblems × work per subproblem).
For fib(N): unique subproblems = N+1 (fib(0) through fib(N)). Work per subproblem = O(1). Total: O(N).

**Space complexity:**
O(N) for the cache + O(N) for the call stack depth (N recursive calls still open before fib(0) is reached the first time).

Can we remove the call stack? Yes — convert to iterative bottom-up (tabulation). But memoization is often easier to write first.

THE TRADE-OFFS:
Gain: Converts exponential to polynomial automatically, easy to implement on any correct recursive solution.
Cost: O(N) call stack depth (risk of StackOverflowError), O(N) cache memory, HashMap overhead per call.

### 🧪 Thought Experiment

SETUP:
`fib(5)` without memoization:

```
fib(5)
├── fib(4)
│   ├── fib(3)
│   │   ├── fib(2) ← computed here
│   │   └── fib(1)
│   └── fib(2)     ← computed AGAIN (redundant)
└── fib(3)         ← computed AGAIN (redundant)
    ├── fib(2)     ← computed AGAIN
    └── fib(1)
```

Total calls: 15 for fib(5). For fib(45): ~1.1 billion calls.

WHAT HAPPENS WITH MEMOIZATION:
```
fib(5):
  fib(4):  fib(3): fib(2): fib(1)+fib(0)=1 (cache fib(2)=1)
                   fib(1): return 1
                   → fib(3)=2 (cached)
           fib(2): cache hit → 1
           → fib(4)=3 (cached)
  fib(3): cache hit → 2
  → fib(5)=5
```
Total unique calls: 6 (fib(0)–fib(5)). Each computed once.

THE INSIGHT:
Memoization prunes the recursion tree by collapsing all duplicate subproblems into single nodes. The tree becomes a DAG (Directed Acyclic Graph) where each node is computed exactly once.

### 🧠 Mental Model / Analogy

> Memoization is like a lookup table at the entrance to a maze. Before entering a room, check if you've solved it before and what the answer was. If yes, leave immediately with the cached answer. If no, solve it and post the answer at the room's entrance for next time.

"Room" → unique subproblem (unique argument combination)
"Answer posted at entrance" → cache entry
"Entering and solving" → recursive computation
"Leaving with cached answer" → returning cached result in O(1)

Where this analogy breaks down: A maze has a specific topology; memoization works on any pure function with any argument structure — not just tree/graph traversals.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Save your work. Before computing something, check if you already did it. If yes, use the saved answer.

**Level 2 — How to use it (junior developer):**
Add a `Map<Arguments, Result>` to your recursive function. At the top: `if (memo.containsKey(args)) return memo.get(args)`. At the bottom: `memo.put(args, result)`. For integer keys, a simple array (`int[] dp = new int[N+1]`) is faster than a HashMap. Initialize with a sentinel value (e.g., -1 for uncomputed).

**Level 3 — How it works (mid-level engineer):**
Memoization transforms the recursion call graph from a tree (re-computing subtrees) to a DAG (each node computed once). The cache size equals the number of distinct argument combinations = the number of unique subproblems. For `fib(N)`: N+1 subproblems. For `LCS(s1, s2)`: |s1| × |s2| subproblems. For coin change with denominations d and target T: d × T+1 subproblems. In Java, `HashMap.computeIfAbsent(key, Function)` is idiomatic for memoization.

**Level 4 — Why it was designed this way (senior/staff):**
Memoization is the top-down view of dynamic programming; tabulation is the bottom-up view. Both compute the same set of subproblems, but memoization only computes subproblems actually needed (lazy), while tabulation computes all subproblems in dependency order (eager). Memoization's lazy evaluation means that for problems where only a fraction of all subproblems are reachable, memoization wins. For problems requiring all subproblems (e.g., matrix chain multiplication), tabulation is typically faster due to better cache locality (iterating arrays vs HashMap lookups). Haskell and other purely functional languages build memoization into the language via lazy evaluation — each thunk is evaluated at most once, effectively memoizing all expressions automatically.

### ⚙️ How It Works (Mechanism)

**Pattern 1 — HashMap memo:**
```java
Map<Integer, Long> memo = new HashMap<>();

long fib(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n); // cache hit
    long result = fib(n - 1) + fib(n - 2);
    memo.put(n, result);                          // cache store
    return result;
}
```

**Pattern 2 — Array memo (faster for integer keys):**
```java
long[] dp = new long[N + 1];
Arrays.fill(dp, -1);

long fib(int n) {
    if (n <= 1) return n;
    if (dp[n] != -1) return dp[n]; // cache hit
    dp[n] = fib(n - 1) + fib(n - 2);
    return dp[n];
}
```

**Pattern 3 — computeIfAbsent idiom:**
```java
Map<String, Integer> memo = new HashMap<>();

int lcs(String s1, String s2, int i, int j) {
    if (i == 0 || j == 0) return 0;
    String key = i + "," + j;
    return memo.computeIfAbsent(key, k -> {
        if (s1.charAt(i-1) == s2.charAt(j-1))
            return 1 + lcs(s1, s2, i-1, j-1);
        return Math.max(lcs(s1, s2, i-1, j),
                        lcs(s1, s2, i, j-1));
    });
}
```

**Without vs with memoization — call counts:**
```
fib(10):
  Without memo: 177 calls
  With memo:     19 calls (10+1 unique fib values × ~2 calls each)

fib(40):
  Without memo: ~2.7 billion calls
  With memo:     79 calls
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Recursive call arrives with arguments A
→ Check memo[A]
→ [MEMOIZATION ← YOU ARE HERE]
→ Cache hit: return memo[A] in O(1)
→ Cache miss: compute, store in memo[A], return
→ All subsequent calls to A return instantly
```

FAILURE PATH:
```
Deep recursion before any cache hit (first call to fib(N))
→ N recursive frames on call stack simultaneously
→ For N > ~5,000: StackOverflowError
→ Fix: use iterative tabulation for large N
```

WHAT CHANGES AT SCALE:
For N > 10,000, the O(N) call stack depth overflows the JVM. Use tabulation (iterative DP) instead. For multi-dimensional memo tables (e.g., `dp[i][j][k]` for 3D DP), memory grows as N³ — quickly unmanageable. Use tabulation with rolling dimensions to reduce space.

### 💻 Code Example

**Example 1 — Without vs with memoization (Fibonacci):**
```java
// BAD: O(2^N) time
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
// fib(45) makes ~2.7 billion calls

// GOOD: O(N) time with memoization
Map<Integer, Long> memo = new HashMap<>();
long fibMemo(int n) {
    if (n <= 1) return n;
    return memo.computeIfAbsent(n,
        k -> fibMemo(k-1) + fibMemo(k-2));
}
// fibMemo(45) makes 46 unique calls
```

**Example 2 — 2D memoization (Unique Paths grid):**
```java
// Count unique paths in M×N grid (down or right only)
int[][] dp = new int[m][n];

int paths(int i, int j) {
    if (i == 0 || j == 0) return 1;
    if (dp[i][j] != 0) return dp[i][j]; // -1,0 sentinel
    dp[i][j] = paths(i - 1, j) + paths(i, j - 1);
    return dp[i][j];
}
// Time: O(M*N), Space: O(M*N) + O(M+N) call stack
```

### ⚖️ Comparison Table

| Technique | Direction | Space | Call Stack | Best For |
|---|---|---|---|---|
| **Memoization** | Top-down | O(subproblems) | O(depth) | Easy-to-write; sparse subproblems |
| Tabulation | Bottom-up | O(subproblems) | O(1) | Large N; dense subproblems |
| Naïve Recursion | Top-down | O(depth) | O(depth) | No overlapping subproblems |

How to choose: Start with memoization (easiest to code). If N is large (risk of SO) or performance needs to be maximised, convert to tabulation.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Memoization = caching = always good | Memoization helps only when subproblems overlap; for problems with all-unique subproblems (like divide-and-conquer without overlap), it adds overhead with no benefit |
| Memoization uses less memory than tabulation | Both use O(unique subproblems) for cache; memoization also uses O(depth) stack space |
| computeIfAbsent is thread-safe | `HashMap.computeIfAbsent` is NOT thread-safe; use `ConcurrentHashMap.computeIfAbsent` for multi-threaded code |
| Memoization always converts O(2^N) to O(N) | Only for problems with O(N) unique subproblems; for permutations, unique subproblems = N! → no polynomial speedup |

### 🚨 Failure Modes & Diagnosis

**1. StackOverflowError on large N**

Symptom: `java.lang.StackOverflowError` for large inputs (N > 5,000).

Root Cause: Memoized recursion still maintains the call stack; the first call to fib(N) opens N stack frames before any cache hits.

Fix: Convert to bottom-up tabulation (iterative DP) or use `trampoline` pattern for tail-recursive languages.

Prevention: For N > 1,000, prefer tabulation over memoization.

---

**2. Wrong results from impure function memoization**

Symptom: Memoized function returns stale results; behavior depends on external state.

Root Cause: Memoized function reads global/mutable state — the same arguments can produce different results at different times.

Fix: Ensure the memoized function is pure: output depends only on inputs, no side effects, no global reads.

Prevention: Never memoize functions that read mutable external state (`System.currentTimeMillis()`, DB calls, etc.).

---

**3. Memory leak from memo Map never cleared**

Symptom: Service memory grows unboundedly; heap dump shows large `HashMap` in the memoization cache.

Root Cause: Class-level static memo HashMap accumulates entries from all calls, never evicted.

Fix: Use a bounded cache (LRU) or clear the cache after each top-level computation completes.

Prevention: Never make a memoization cache a long-lived class field; either pass it as a parameter or clear it after use.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` — memoization only applies to recursive algorithms with repeated calls.
- `HashMap` — the standard cache backing store.

**Builds On This (learn these next):**
- `Tabulation (Bottom-Up DP)` — the iterative counterpart; avoids call stack issues.
- `Dynamic Programming` — the general technique; memoization is the top-down approach.

**Alternatives / Comparisons:**
- `Tabulation` — same asymptotic complexity, O(1) stack, better cache locality.
- `LRU Cache` — bounded memoization that evicts old entries to control memory.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cache for recursive calls: compute each   │
│              │ unique argument combination exactly once  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Exponential recursion from recomputing    │
│ SOLVES       │ the same subproblems repeatedly           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Works only when subproblems overlap; for  │
│              │ all-unique subproblems it adds overhead   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Recursive solution is obvious but slow;  │
│              │ subproblems repeat (DP, combinatorics)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N > ~5,000 (use tabulation); function     │
│              │ has side effects (not pure)               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Easy to write vs O(depth) call stack      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check the margin before recalculating —  │
│              │  you may have already solved this"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tabulation → Dynamic Programming          │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A memoized solution to the 0/1 Knapsack problem uses a `HashMap<String, Integer>` with keys `"i,w"`. An alternative uses a 2D `int[][]` array `dp[i][w]`. For N=100 items, capacity W=10,000, the 2D array uses 100 × 10,000 × 4 bytes = ~4 MB. The HashMap's memory usage depends on which subproblems are actually visited. Under what input conditions would the memoized HashMap use *less* memory than the full 2D array, and when would it use more? How would you decide which to use?

**Q2.** In languages like Haskell, every function is automatically memoized by the lazy evaluation strategy — a value is computed at most once, then shared. In Java, you must explicitly implement memoization with a HashMap. What fundamental property of Haskell's type system and evaluation model makes automatic memoization safe, and why would automatically memoizing every Java method call be dangerous without explicit programmer opt-in?

