---
id: DSA-068
title: Backtracking
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-026
used_by: DSA-077
related: DSA-026, DSA-065, DSA-067
tags:
  - algorithms
  - backtracking
  - constraint-satisfaction
  - pruning
  - brute-force
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/dsa/backtracking/
---

## TL;DR

Backtracking is systematic brute force with pruning - it
explores all possibilities via recursion, but abandons
branches that cannot lead to a valid solution, making it
practical for constraint satisfaction problems.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-068 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, backtracking, constraint-satisfaction |
| **Prerequisites** | DSA-026 |

---

### The Problem This Solves

"Place 8 queens on a chess board so no two threaten each
other." Pure brute force: 64^8 = 281 trillion options.
Backtracking: place queens column by column, abandon
any column placement that causes a conflict immediately.
This pruning reduces the search space to thousands of
configurations, not trillions.

---

### Textbook Definition

Backtracking is a general algorithm for finding solutions
to constraint satisfaction problems. It incrementally
builds candidates and abandons ("backtracks") each candidate
as soon as it determines the candidate cannot lead to a
valid solution. Implemented via DFS recursion with
undo operations.

Template:
```
backtrack(state):
  if goal_reached: add state to results; return
  for each choice:
    if choice is valid:
      make the choice (modify state)
      backtrack(new state)
      undo the choice (restore state)  ← KEY STEP
```

---

### How It Works

**N-Queens implementation:**

```java
List<List<String>> solveNQueens(int n) {
    List<List<String>> result = new ArrayList<>();
    int[] queens = new int[n]; // queens[row] = col
    Arrays.fill(queens, -1);

    Set<Integer> cols = new HashSet<>();
    Set<Integer> diag1 = new HashSet<>(); // row - col
    Set<Integer> diag2 = new HashSet<>(); // row + col

    backtrack(0, n, queens, cols, diag1, diag2, result);
    return result;
}

void backtrack(int row, int n, int[] queens,
               Set<Integer> cols, Set<Integer> diag1,
               Set<Integer> diag2,
               List<List<String>> result) {
    if (row == n) {
        result.add(buildBoard(queens, n));
        return;
    }

    for (int col = 0; col < n; col++) {
        // Pruning: skip if column or diagonal is attacked
        if (cols.contains(col) ||
            diag1.contains(row - col) ||
            diag2.contains(row + col)) continue;

        // Make choice
        queens[row] = col;
        cols.add(col);
        diag1.add(row - col);
        diag2.add(row + col);

        backtrack(row + 1, n, queens, cols,
                  diag1, diag2, result);

        // UNDO choice (backtrack)
        queens[row] = -1;
        cols.remove(col);
        diag1.remove(row - col);
        diag2.remove(row + col);
    }
}
```

**The undo step is critical:**

```java
// BAD: missing undo - state accumulates, wrong results
cols.add(col);
backtrack(row + 1, ...);
// cols still has col for next sibling iteration!

// GOOD: with undo
cols.add(col);
backtrack(row + 1, ...);
cols.remove(col); // restore for next sibling
```

---

### Comparison Table

| Approach | N-Queens | Subset Sum | Sudoku |
|---------|----------|-----------|--------|
| Backtracking | Yes (practical) | Yes (with pruning) | Yes (standard) |
| DP | No (combinatorial) | Pseudo-polynomial | No |
| Greedy | No (no greedy property) | No | No |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Backtracking is brute force" | It's structured brute force with pruning; effective pruning can reduce exponential to polynomial in practice |
| "Backtracking always generates all solutions" | It can be used to find just the FIRST valid solution (stop after first result) or count solutions without storing them |

---

### Failure Modes & Diagnosis

**Failure: Missing undo step causes wrong results**
- Symptom: Solutions contain duplicate elements, or
  constraints appear violated in later iterations
- Cause: State modification not reversed after recursive call
- Fix: Every state change before recursion must have
  a corresponding undo after recursion returns

---

### Quick Reference Card

| Property | Backtracking |
|---------|-------------|
| Time | Exponential worst case |
| Pruning | Practical speedup (often huge) |
| Space | O(depth) for call stack |
| Key pattern | make-choice + recurse + undo-choice |
| Common problems | N-Queens, Sudoku, permutations, subsets |

---

### The Surprising Truth

Sudoku solvers used in newspapers and apps run backtracking.
The constraint propagation step (constraint satisfaction
before backtracking) is what makes them fast: filling in
cells that only have one possible value first, then
backtracking only when ambiguity remains. A typical 9x9
Sudoku puzzle is solved by backtracking in microseconds
with good pruning. Without pruning, it's 9^81 = 10^77
operations - impossible. Backtracking with pruning is
one of the most practically impactful algorithm techniques.

---

### Mastery Checklist

- [ ] Implements N-Queens with backtracking
- [ ] Never forgets the undo step in state restoration
- [ ] Can identify when backtracking is the right approach

---

### Interview Deep-Dive

**Q1 (Medium):** Generate all permutations of n unique
elements.

> Backtracking approach:
> State: current permutation (partial or complete).
> Choice: at each position, try all remaining unused elements.
> Prune: no pruning needed (all permutations are valid).
> Undo: remove the element from "used" set after recursion.
> 
> Time: O(n * n!) - n! permutations, O(n) to build each.
> Swap-in-place optimization: avoid used set, swap current
> position with each subsequent position, recurse, then
> swap back.
> 
> Key learning: even without pruning, backtracking is the
> correct pattern for generating combinatorial structures
> (permutations, subsets, combinations).
