---
layout: default
title: "Backtracking"
parent: "Data Structures & Algorithms"
nav_order: 72
permalink: /dsa/backtracking/
number: "0072"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Recursion, DFS, Array
used_by: Dynamic Programming, NP-Complete Problems, Graph Coloring
related: Dynamic Programming, BFS, Greedy Algorithm
tags:
  - algorithm
  - intermediate
  - pattern
  - recursion
  - datastructure
---

# 072 — Backtracking

⚡ TL;DR — Backtracking explores all candidate solutions recursively, abandoning ("pruning") any path the moment it becomes impossible to reach a valid solution.

| #0072 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Recursion, DFS, Array | |
| **Used by:** | Dynamic Programming, NP-Complete Problems, Graph Coloring | |
| **Related:** | Dynamic Programming, BFS, Greedy Algorithm | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Generate all valid sudoku solutions. The naive approach tries all 9^81 ≈ 10^77 complete board configurations, checking validity only at the end. The universe will end before even a single solution is verified.

THE BREAKING POINT:
Pure brute-force enumeration of exponential search spaces is computationally impossible. The key observation being ignored: if placing "7" in row 3, column 4 already violates row/column/box constraints, no completion of that partial board can ever be valid. Those 9^77 completions are wasted work.

THE INVENTION MOMENT:
Check validity as you build. The moment a partial candidate violates a constraint, immediately abandon it and backtrack to the previous decision point. This "pruning" can reduce 10^77 states to thousands of actual checks. This is exactly why **Backtracking** was created.

---

### 📘 Textbook Definition

**Backtracking** is a systematic algorithm for solving constraint satisfaction problems by incrementally building candidates for a solution and abandoning a candidate ("backtracking") as soon as it is determined that the candidate cannot possibly lead to a valid complete solution. It conducts a depth-first search of the implicit search tree of partial solutions, pruning branches that violate constraints. Time complexity in the worst case is exponential O(bᵈ) where b is the branching factor and d is the depth, but pruning typically achieves dramatic practical speedup over exhaustive enumeration.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Try every option; undo your choice immediately when you know it leads nowhere.

**One analogy:**
> Navigating a maze: you move forward until you hit a dead end, then retrace your steps to the last fork and try the other path. You never start over from the entrance — you undo only the last decisions that led to the dead end.

**One insight:**
Backtracking is DFS with a pruning condition. The effectiveness of Backtracking is entirely determined by the quality of the pruning condition — a tight constraint that detects impossible partial states early eliminates exponentially more branches than a loose one that only detects failure at the leaves.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The search explores a **decision tree**: at each node you make one choice from a set of options.
2. Every recursive call represents one decision; each return ("backtrack") undoes exactly that decision.
3. **Pruning** is the key: a constraint check at every node. If a partial state already violates a constraint, terminate this branch immediately.

DERIVED DESIGN:
The template structure follows naturally:

```
backtrack(state, choices):
  if state is complete and valid: record solution, return
  for each choice in valid_choices(state):
    apply choice to state
    backtrack(state, remaining_choices)
    undo choice from state    ← this is the "backtrack"
```

The `undo` step is critical: the state must be perfectly restored after each recursive call. This guarantees each call receives a clean state reflecting only its ancestors' decisions.

**Pruning strategies:**
- **Constraint check:** does the current partial state violate any problem constraint? (e.g., duplicate in sudoku).
- **Bound check:** can the current partial state ever lead to a better solution than the best found so far? (Branch and Bound).
- **Forward checking:** does any remaining variable have zero valid values? (Sudoku: a cell becomes impossible to fill).

THE TRADE-OFFS:
Gain: Finds all valid solutions (or the first/best), explores the search space systematically, is dramatically faster than brute force with good pruning.
Cost: Worst-case exponential time O(bᵈ). Stack depth equals solution depth d — stack overflow possible for deep recursion. Pruning quality determines practical performance; bad pruning is barely better than brute force.

---

### 🧪 Thought Experiment

SETUP:
Generate all valid combinations of 3 numbers chosen from {1, 2, 3, 4} with no repeats.

WHAT HAPPENS WITHOUT BACKTRACKING:
Generate all permutations of {1,2,3,4} of length 3: 4×3×2 = 24. Check each for uniqueness. All 24 are valid. But the generation itself visits every leaf — can't stop early.

WHAT HAPPENS WITH BACKTRACKING (find combinations where sum ≤ 6):
- Choose 1 → [1]. Choose 2 → [1,2]. Choose 3 → [1,2,3]. Sum=6  ✓ record.
- Backtrack to [1,2]. Choose 4 → [1,2,4]. Sum=7 > 6 → PRUNE. Backtrack to [1,2].
- Backtrack to [1]. Choose 3 → [1,3]. Choose 4 → [1,3,4]. Sum=8 > 6 → PRUNE.
- Backtrack to []. Choose 2 → [2]. Choose 3 → [2,3]. Choose 4 → [2,3,4]. Sum=9 → PRUNE.
- Result: only {1,2,3} found. 8 nodes visited instead of all 24 permutations.

THE INSIGHT:
The pruning at [1,2,4] eliminated not just that node but all sub-trees rooted there. In exponential search spaces, early elimination of even a small fraction of branches can reduce total work by orders of magnitude.

---

### 🧠 Mental Model / Analogy

> Backtracking is like packing a suitcase for a maximum weight limit. You place items one by one. The moment the total weight exceeds the limit, you remove the last item and try the next alternative — you don't wait until the suitcase is full and overflowing to decide it won't work.

"Items yet to pack" → remaining choices
"Current suitcase contents" → current partial state
"Check weight after each addition" → constraint check per node
"Remove the last item" → undo last choice (backtrack)
"Suitcase full within limit" → complete valid solution
"Weight already exceeds limit" → prune this branch

Where this analogy breaks down: Real suitcase packing is a knapsack problem (which item to include for maximum value); backtracking generates all valid combinations with pruning. Also, backtracking maintains exact undo state, whereas physically repacking a suitcase is not O(1).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Backtracking is a trial-and-error approach with smart give-up. You try building a solution step by step. If at any point the partial solution clearly won't work, you stop, undo the last step, and try something else — like erasing a wrong answer on a test rather than finishing the entire wrong calculation.

**Level 2 — How to use it (junior developer):**
Identify the decision tree: what choices are made at each step? Implement the recursive template: choose, recurse, unchoose. Add a constraint check at the start of each call to prune early. Classic use cases: N-Queens, Sudoku solver, permutations/combinations, word search on a grid. Always verify that the `undo` step perfectly restores state.

**Level 3 — How it works (mid-level engineer):**
Backtracking's performance depends on prune quality. For N-Queens on an 8×8 board, constraint checking (row, column, diagonal) reduces from 8^8 = 16M to ~92 actual solutions with ~2,000 nodes visited. Two key optimisations: (1) **variable ordering** — pick the variable with the fewest remaining valid values first (MRV heuristic, used in SAT solvers); (2) **constraint propagation** — after placing a queen, immediately eliminate all attacked cells from future considerations, which may trigger further eliminations (arc consistency / forward checking).

**Level 4 — Why it was designed this way (senior/staff):**
Backtracking is the foundation of constraint programming (CP) — a declarative paradigm where you specify constraints and let a CP solver find all solutions. Modern CP solvers like Choco or Google OR-Tools extend backtracking with global constraints (AllDifferent, Circuit, Cumulative) that have specialised propagators with O(N) or O(N log N) pruning rather than O(1) per step. Backtracking is also equivalent to DPLL — the foundational algorithm for SAT solvers. Industrial SAT solvers (MiniSAT, CaDiCaL) extend it with CDCL (Conflict-Driven Clause Learning), replaying backtracking decisions to learn new constraints from failures — making NP-hard problems tractable in practice for millions of variables.

---

### ⚙️ How It Works (Mechanism)

**N-Queens Example (4×4 board):**

```
┌─────────────────────────────────────────────┐
│ N-Queens Decision Tree (partial, 4×4)       │
│                                             │
│ Row 0: try cols 0,1,2,3                     │
│   col=0 → Q at (0,0)                       │
│     Row 1: col=0 CONFLICT (same col)        │
│     Row 1: col=1 CONFLICT (diagonal)        │
│     Row 1: col=2 → Q at (1,2)              │
│       Row 2: col=0 CONFLICT (diagonal /)    │
│       Row 2: col=1 CONFLICT (same col=2)    │
│         ← all cols pruned → BACKTRACK       │
│     Row 1: col=3 → Q at (1,3)              │
│       Row 2: col=1 → Q at (2,1)            │
│         Row 3: all cols pruned              │
│         ← BACKTRACK                        │
│   col=1 → Q at (0,1)                       │
│     ... (continues, finds 2 solutions)     │
└─────────────────────────────────────────────┘
```

**Generic Backtracking Template:**
```java
void backtrack(List<Integer> current,
               boolean[] used, int n) {
    if (current.size() == n) {
        result.add(new ArrayList<>(current));
        return;
    }
    for (int i = 0; i < n; i++) {
        if (used[i]) continue;     // constraint check
        current.add(i);            // choose
        used[i] = true;
        backtrack(current, used, n); // explore
        current.remove(current.size() - 1); // unchoose
        used[i] = false;           // undo state
    }
}
```

The `used[i] = false` line is the "backtrack" — it restores state so the parent call can try the next option.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Problem with exponential candidate space
→ Define decision tree: choices at each node
→ Define constraints: what makes a partial state invalid
→ [BACKTRACKING ← YOU ARE HERE]
  → DFS through decision tree
  → Prune on constraint violation
  → Record complete valid solutions
  → Restore state (undo choice) on return
→ Return all (or first, or best) valid solutions
```

FAILURE PATH:
```
Missing undo step → shared mutable state corrupted
→ Wrong solutions generated
→ Debug: after recursive call, assert state == pre-call state
→ Fix: restore every mutation made before the recursive call

Stack overflow → recursion depth exceeds JVM limit
→ java.lang.StackOverflowError
→ Fix: increase stack size (-Xss) or convert to iterative
  with explicit stack
```

WHAT CHANGES AT SCALE:
For large-scale combinatorial problems (NP-hard), backtracking alone is insufficient — professional use requires constraint propagation, good variable ordering (MRV), and value ordering (LCV). SAT problems with 10⁶ variables are solved daily by industrial SAT solvers using CDCL — a backtracking variant that learns clauses from conflicts, enabling backjumping (skipping irrelevant decision levels). Pure backtracking on such scales would never terminate.

---

### 💻 Code Example

**Example 1 — All permutations:**
```java
void permutations(int[] nums,
                  boolean[] used,
                  List<Integer> current,
                  List<List<Integer>> result) {
    if (current.size() == nums.length) {
        result.add(new ArrayList<>(current));
        return;
    }
    for (int i = 0; i < nums.length; i++) {
        if (used[i]) continue;
        current.add(nums[i]);   // choose
        used[i] = true;
        permutations(nums, used, current, result);
        current.remove(current.size() - 1); // unchoose
        used[i] = false;
    }
}
```

**Example 2 — N-Queens:**
```java
boolean isSafe(int[] queens, int row, int col) {
    for (int r = 0; r < row; r++) {
        if (queens[r] == col) return false; // same column
        if (Math.abs(queens[r] - col) ==
            Math.abs(r - row)) return false; // diagonal
    }
    return true;
}

void nQueens(int[] queens, int row,
             int n, List<int[]> result) {
    if (row == n) {
        result.add(queens.clone());
        return;
    }
    for (int col = 0; col < n; col++) {
        if (!isSafe(queens, row, col)) continue; // prune
        queens[row] = col;          // place queen
        nQueens(queens, row + 1, n, result);
        queens[row] = -1;           // remove queen
    }
}
```

**Example 3 — Combination sum (pruning with target):**
```java
void combinationSum(int[] candidates, int target,
                    int start, List<Integer> current,
                    List<List<Integer>> result) {
    if (target == 0) {
        result.add(new ArrayList<>(current));
        return;
    }
    for (int i = start; i < candidates.length; i++) {
        // Prune: remaining candidates too large
        if (candidates[i] > target) break;
        current.add(candidates[i]);
        // Same element can be reused (i, not i+1)
        combinationSum(candidates, target - candidates[i],
                       i, current, result);
        current.remove(current.size() - 1);
    }
}
```

**Example 4 — Sudoku solver:**
```java
boolean solveSudoku(char[][] board) {
    for (int r = 0; r < 9; r++) {
        for (int c = 0; c < 9; c++) {
            if (board[r][c] != '.') continue;
            for (char d = '1'; d <= '9'; d++) {
                if (!isValid(board, r, c, d)) continue;
                board[r][c] = d;             // place digit
                if (solveSudoku(board)) return true;
                board[r][c] = '.';           // undo
            }
            return false; // no digit works → backtrack
        }
    }
    return true; // all cells filled
}
```

---

### ⚖️ Comparison Table

| Approach | Completeness | Time | Space | Best For |
|---|---|---|---|---|
| **Backtracking** | All solutions | O(bᵈ) pruned | O(d) stack | Constraint satisfaction, all solutions |
| Brute Force | All solutions | O(bᵈ) full | O(d) | Reference only — no pruning |
| Greedy | One solution | O(N log N) | O(1) | Optimisation with greedy-choice property |
| Dynamic Programming | Optimal solution | O(N²) to O(N·S) | O(N·S) | Overlapping subproblems, optimal value |
| BFS | Shortest path | O(bᵈ) | O(bᵈ) | Shortest solution, not all solutions |

How to choose: Use Backtracking when you need all valid configurations AND the constraint check can prune early. Use DP when you only need the optimal value and subproblems overlap. Use Greedy for locally optimal choices that lead to globally optimal solutions.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Backtracking is always exponential and impractical | With good pruning (forward checking, constraint propagation), backtracking solves many NP-hard problems in seconds. Sudoku solvers, SAT solvers, and scheduling engines all use it commercially. |
| Backtracking and recursion are the same thing | All backtracking uses recursion, but not all recursion is backtracking. Backtracking requires an explicit UNDO step and a constraint pruning check. |
| You only backtrack on complete invalid solutions | The power comes from backtracking on PARTIAL invalid solutions. Pruning at depth 3 of a depth-10 tree eliminates 10^7 leaves in one step. |
| DFS and Backtracking are identical | DFS explores all reachable nodes; Backtracking prunes branches where no valid solution can exist. Backtracking is DFS + pruning + undo. |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing undo step — state corruption**

Symptom: Solutions contain elements from other branches; solutions repeat or are incomplete.

Root Cause: After the recursive call, the shared state (list, array, boolean flags) still contains the choice made in this call. The sibling and parent calls see corrupted state.

Diagnostic:
```java
// Add assertion before and after recursive call:
int sizeBefore = current.size();
backtrack(...);
assert current.size() == sizeBefore :
    "Undo missing: size went from " + sizeBefore +
    " to " + current.size();
```

Fix: Every `add/set/mark` before the recursive call must have a corresponding `remove/reset/unmark` after it.

Prevention: Write choose → recurse → unchoose in a single block; never separate them.

---

**2. Stack overflow for deep recursion**

Symptom: `java.lang.StackOverflowError` for large inputs (e.g., word search on a 20×20 grid).

Root Cause: Default JVM stack depth is ~10,000 frames. Backtracking depth equals solution depth × branching factor of path.

Diagnostic:
```bash
java -Xss10m -jar myapp.jar   # increase stack size
# Or check recursion depth:
jstack <pid> | grep "backtrack"
```

Fix: Increase stack size with `-Xss`, or convert to iterative backtracking with an explicit stack.

Prevention: Estimate maximum recursion depth before deployment: `max_depth × avg_frame_size_bytes < Xss`.

---

**3. Duplicate solutions when input has duplicates**

Symptom: `[1,1,2]` produces `[[1,1,2],[1,1,2]]` instead of `[[1,1,2]]`.

Root Cause: Without deduplication, both occurrences of "1" at index 0 and 1 are each used as a separate start — producing identical combinations.

Diagnostic:
```java
// Sort input first, then skip duplicate choices:
if (i > start && candidates[i] == candidates[i-1])
    continue; // skip duplicate at same level
```

Fix: Sort the input array; skip candidates equal to the previous candidate at the same recursion level.

Prevention: Always sort input and add duplicate-skip logic when input may contain repeats.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` — Backtracking is implemented via recursion; understanding call stack frames and base cases is essential.
- `DFS` — Backtracking is DFS with pruning; understanding depth-first traversal explains the exploration order.
- `Array` — Most backtracking problems involve arrays as candidate pools or board representations.

**Builds On This (learn these next):**
- `Dynamic Programming` — When backtracking reveals overlapping subproblems (same state reached via different paths), DP memoises results to avoid recomputation.
- `Graph Coloring` — A classic constraint satisfaction problem solved by backtracking; extends the N-Queens structure to graphs.
- `NP-Complete Problems` — Most NP-complete problems are solved in practice using backtracking with heavy pruning (SAT, TSP, knapsack exact).

**Alternatives / Comparisons:**
- `Greedy Algorithm` — Makes irrevocable locally optimal choices; faster (O(N log N)) but doesn't guarantee globally optimal solution and doesn't find all solutions.
- `Dynamic Programming` — Optimal for counting or optimising over overlapping subproblems; doesn't enumerate all solutions explicitly.
- `BFS` — Explores level by level; finds shortest solution path but stores exponential frontier in memory.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ DFS + pruning + undo on implicit          │
│              │ decision tree of partial solutions        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Exponential brute force can't explore     │
│ SOLVES       │ constraint-satisfaction spaces in time    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pruning partial states eliminates entire  │
│              │ sub-trees — more powerful than leaf-check │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need all valid solutions to a constraint  │
│              │ satisfaction problem; pruning is possible │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only optimal value needed (use DP);       │
│              │ problem has greedy-choice property        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete but exponential worst case vs    │
│              │ polynomial DP (only optimal value)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Try, check, undo — never finish a dead   │
│              │  end"                                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ N-Queens → Sudoku Solver → SAT/CDCL       │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** In the N-Queens backtracking, when a queen is placed at row `r`, column `c`, you mark three sets as invalid: the column, and the two diagonals. Compare two pruning strategies: (A) recompute `isSafe` by scanning all placed queens each time O(r) per check; (B) maintain three Boolean sets for columns and diagonals O(1) per check. How does the choice of pruning data structure affect the total number of nodes visited vs. the work per node, and what is the optimal trade-off for N=25?

**Q2.** Backtracking and Dynamic Programming both explore a state space. DP memoises states to avoid recomputation; Backtracking prunes states to avoid exploration. For the Longest Common Subsequence problem, draw the recursive call tree. Which calls represent the same state (overlapping subproblems)? Why does Backtracking without memoisation become O(2^N) while DP solves it in O(N×M)? Under what constraint would Backtracking be necessary even if DP would solve it faster?

