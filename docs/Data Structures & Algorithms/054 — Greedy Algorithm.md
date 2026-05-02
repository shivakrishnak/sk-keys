---
layout: default
title: "Greedy Algorithm"
parent: "Data Structures & Algorithms"
nav_order: 54
permalink: /dsa/greedy-algorithm/
number: "0054"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Time Complexity / Big-O, Priority Queue
used_by: Dijkstra, Huffman Coding, Kruskal / Prim
related: Dynamic Programming, Divide and Conquer, Backtracking
tags:
  - algorithm
  - intermediate
  - pattern
  - mental-model
---

# 054 — Greedy Algorithm

⚡ TL;DR — A Greedy Algorithm makes the locally optimal choice at each step, never revising it — correct when the greedy choice property holds, faster than DP or exhaustive search.

| #054 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Time Complexity / Big-O, Priority Queue | |
| **Used by:** | Dijkstra, Huffman Coding, Kruskal / Prim | |
| **Related:** | Dynamic Programming, Divide and Conquer, Backtracking | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to make change for $0.86 using the fewest coins possible (denominations: 25¢, 10¢, 5¢, 1¢). Trying all combinations: there are billions of possibilities. Dynamic programming: O(amount × denominations) — polynomial but requires a table. Is there a faster approach?

**THE BREAKING POINT:**
For large combinatorial problems, exhaustive search is exponential. Dynamic programming is polynomial but requires O(amount) space per denomination. Some problems have a simpler structure that allows a correct short-cut — but identifying when that shortcut is valid is the challenge.

**THE INVENTION MOMENT:**
For this specific coin system, always picking the largest coin that fits (25¢, then 10¢, etc.) always produces the optimal answer. The "greedy choice" at each step is locally optimal, and remarkably, locally optimal choices compose into a globally optimal solution. This is the **Greedy Choice Property** — when it holds, a greedy algorithm beats DP in both time and simplicity. This is exactly why Greedy Algorithms were created.

---

### 📘 Textbook Definition

A **Greedy Algorithm** solves an optimisation problem by making a series of choices, each the locally optimal choice at that step, without revisiting previous choices. For a greedy algorithm to produce the globally optimal solution, the problem must satisfy two properties: the **Greedy Choice Property** (a globally optimal solution can be assembled from locally optimal choices) and **Optimal Substructure** (the optimum for the whole contains optima for subproblems). When these hold, greedy algorithms are typically O(N log N) or O(N) — faster than O(N² or exponential) DP or backtracking.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
At each step, pick the best available option and never look back.

**One analogy:**
> A hiker climbing a mountain by always taking the steepest step upward. This finds the local summit quickly but may miss a higher nearby peak. Greedy works when the mountain has only one summit — or when the structure of the problem guarantees the local summit IS the global one.

**One insight:**
The hardest part of using greedy is *proving* the Greedy Choice Property — that "always take the best now" never sacrifices "the best total." This proof is problem-specific. Without proof, greedy is just a heuristic — it may find a good solution, but not necessarily the optimal one.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. At each step, make the best locally available choice.
2. Never reconsider a choice once made.
3. Prove (or rely on known proof) that local optimality implies global optimality for this specific problem.

**DERIVED DESIGN:**
**Standard greedy framework:**
1. Define a selection criterion (which option is "best" at each step).
2. Prove the Greedy Choice Property for this criterion.
3. Prove Optimal Substructure (removing the greedy choice leaves a subproblem with the same structure).
4. Implement: sort by criterion if needed, then iterate selecting greedily.

**Why does greedy beat DP when valid?**
DP explores all possible choices at each step and caches results. Greedy makes one choice per step. For the same asymptotic complexity in the subproblem exploration, greedy eliminates the branching factor — one path through the decision tree instead of all paths.

**When greedy fails:**
Coin problem with denominations [1, 3, 4]: change for 6.
Greedy: 4+1+1 = 3 coins. Optimal: 3+3 = 2 coins. Greedy picks 4 first but this is suboptimal.
The standard USD/EU coin systems satisfy the greedy choice property; non-standard denominations may not.

**THE TRADE-OFFS:**
**Gain:** Often O(N log N) or O(N), simple implementation, no need for state table.
**Cost:** Correctness hard to verify; fails silently if greedy choice property doesn't hold; not universally applicable.

---

### 🧪 Thought Experiment

**SETUP:**
Activity Selection: given N activities with start and end times, select maximum number of non-overlapping activities.

BRUTE FORCE: Try all 2^N subsets, check each for compatibility. O(2^N).

GREEDY: Sort by end time. Always pick the activity that ends earliest and doesn't overlap the previous selection.

WHY GREEDY WORKS HERE:
Activity ending earliest leaves the most remaining time for future activities. Choosing any other activity instead of the earliest-ending one cannot enable more future activities — it can only enable fewer (because it ends later, reducing the remaining window).

PROOF SKETCH (exchange argument):
Suppose an optimal solution O doesn't include the earliest-ending activity A. Swap the first activity in O with A. A ends earlier or at the same time, so it's still compatible with everything O was compatible with. The result is at least as good as O and includes A. So there's always an optimal solution that includes the greedy choice.

**THE INSIGHT:**
The "exchange argument" is the standard proof technique for greedy: show that any optimal solution can be transformed to include the greedy choice without getting worse. If this holds for every step, greedy is globally optimal.

---

### 🧠 Mental Model / Analogy

> Greedy is like a packing strategy for a suitcase: always pack the densest item first (most value per cm³). This fills the suitcase with maximum value per space. But if items are discrete and indivisible, the densest-first approach may leave wasted space that a different combination would fill better. Greedy works for the "fractional knapsack" (items divisible) but not the "0/1 knapsack" (items whole).

- "Densest item first" → greedy selection criterion
- "Fractional knapsack" → greedy works (items are divisible)
- "0/1 knapsack" → greedy fails (items are indivisible)
- "Wasted space from indivisibility" → greedy choice property violated

Where this analogy breaks down: "Densest" is a well-defined ordering; greedy selection criteria are problem-specific and may be non-obvious (e.g., Huffman encoding's criterion is character frequency).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
At every decision point, pick the best-looking option right now without worrying about future consequences. Works when the "best right now" always leads to the "best overall."

**Level 2 — How to use it (junior developer):**
Recognise when a problem has a natural ordering (smallest, cheapest, highest value-to-weight) and test if always picking first works. Common greedy applications: activity selection (sort by end time), fractional knapsack (sort by value/weight), Huffman encoding (always merge two smallest frequencies), Dijkstra (always process nearest unvisited node), Prim/Kruskal MST.

**Level 3 — How it works (mid-level engineer):**
Most greedy algorithms: (1) sort by the relevant criterion O(N log N), (2) iterate O(N) making greedy choices → total O(N log N). Some use priority queues for dynamic ordering (Dijkstra: O((V+E) log V)). Proof techniques: exchange argument (show swapping greedy for non-greedy choice doesn't improve), or "greedy stays ahead" (show greedy's solution is lexicographically ≥ optimal at each step).

**Level 4 — Why it was designed this way (senior/staff):**
Greedy algorithms are not about simplicity — they are about exploiting matroid structure. A **matroid** is an abstract mathematical structure where greedy algorithms always find optimal solutions (independent set systems with the exchange property). Huffman encoding works because the character frequencies form a matroid-like structure. Minimum spanning trees work because graphic matroids satisfy the exchange property. When you prove greedy is correct, you're implicitly proving the problem's solution space forms a matroid (or similar). Recognising when a problem has matroid structure is an advanced skill separating candidates who "know" greedy from those who understand it.

---

### ⚙️ How It Works (Mechanism)

**Activity Selection — greedy implementation:**
```java
List<int[]> activitySelection(int[][] activities) {
    // Sort by end time — greedy criterion
    Arrays.sort(activities, Comparator.comparingInt(a -> a[1]));

    List<int[]> result = new ArrayList<>();
    int lastEnd = -1;

    for (int[] act : activities) {
        if (act[0] >= lastEnd) { // doesn't overlap
            result.add(act);
            lastEnd = act[1];
        }
    }
    return result;
}
// Time: O(N log N) for sort + O(N) for scan = O(N log N)
```

**Fractional Knapsack — greedy by value/weight ratio:**
```java
double fractionalKnapsack(Item[] items, int capacity) {
    // Sort by value-per-weight descending — greedy criterion
    Arrays.sort(items, (a, b) ->
        Double.compare(b.value/b.weight, a.value/a.weight));

    double totalValue = 0;
    for (Item item : items) {
        if (capacity >= item.weight) {
            totalValue += item.value;
            capacity -= item.weight;
        } else {
            totalValue += (double)capacity / item.weight * item.value;
            break; // knapsack is full
        }
    }
    return totalValue;
}
```

**Why fractional knapsack is greedy-correct but 0/1 is not:**
```
Items: [(value=3, weight=3), (value=4, weight=4), (value=5, weight=5)]
Capacity: 7

Fractional greedy (value/weight all = 1):
  Take all of item 3 (weight 3): value=3, remaining=4
  Take all of item 2 (weight 4): value=4, remaining=0
  Total: 7 (optimal for fractional)

0/1 greedy (same criterion):
  Take item 3 (w=3): value=3, remaining=4
  Take item 2 (w=4): value=4, remaining=0
  Total: 7 — OK here, but consider:

Items: [(v=6, w=4), (v=5, w=3), (v=5, w=3)], capacity=6
Greedy picks v/w: 6/4=1.5 → take (6,4), remaining=2 → NO more fit
Result: 6
Optimal: take (5,3)+(5,3) = 10
Greedy FAILS for 0/1 knapsack.
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Problem requires selecting items/choices optimally
→ Identify greedy criterion (what "best at each step" means)
→ Prove Greedy Choice Property (exchange argument)
→ [GREEDY ALGORITHM ← YOU ARE HERE]
→ Sort + iterate O(N log N)
→ Globally optimal solution
```

**FAILURE PATH:**
```
Apply greedy without proof of correctness
→ Produces a feasible but suboptimal solution
→ No error thrown — silently wrong
→ Fix: verify against DP solution on test cases
→ Use DP if greedy fails even one counterexample
```

**WHAT CHANGES AT SCALE:**
Greedy's O(N log N) is excellent at scale: 1 billion elements in ~30 log(10^9) ≈ 30 billion comparisons. The sort step dominates; the greedy scan is O(N). For streaming data (can't sort), greedy must be adapted with priority queues (Dijkstra: O((V+E) log V)). At distributed scale, greedy algorithms solve the local problem on each shard; global optimality requires careful aggregation.

---

### 💻 Code Example

**Example 1 — Huffman Encoding (greedy frequency merging):**
```java
// Build Huffman tree: always merge two lowest-frequency nodes
int minCost(int[] frequencies) {
    PriorityQueue<Integer> pq =
        new PriorityQueue<>();
    for (int f : frequencies) pq.offer(f);

    int totalCost = 0;
    while (pq.size() > 1) {
        int left  = pq.poll(); // smallest
        int right = pq.poll(); // second smallest
        int merged = left + right;
        totalCost += merged;
        pq.offer(merged);
    }
    return totalCost; // minimum encoding cost
}
// Greedy: always merge two cheapest → optimal Huffman tree
```

**Example 2 — Jump Game (can you reach the end?):**
```java
// Greedy: track furthest reach at each step
boolean canJump(int[] nums) {
    int maxReach = 0;
    for (int i = 0; i <= maxReach; i++) {
        maxReach = Math.max(maxReach, i + nums[i]);
        if (maxReach >= nums.length - 1) return true;
    }
    return false;
}
// Always extend reach greedily — O(N), no DP needed
```

---

### ⚖️ Comparison Table

| Paradigm | Choice per step | Can backtrack | Globally optimal | Time |
|---|---|---|---|---|
| **Greedy** | 1 (no revisit) | No | Only if GCP proves | O(N log N) |
| Dynamic Programming | All, cached | Via table | Yes (for OPT struct) | O(N²) typical |
| Backtracking | All, with undo | Yes | Yes (exhaustive) | O(2^N) typical |
| Brute Force | All | Not needed | Yes | O(N!) or O(2^N) |

How to choose: Use greedy when you can prove the greedy choice property. Use DP when subproblems overlap and greedy fails. Use backtracking for constraint satisfaction where you need to explore all solutions.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Greedy always finds the optimal solution | Greedy is only correct when the greedy choice property holds; for 0/1 knapsack and TSP, greedy is suboptimal |
| Greedy and DP are equivalent | Greedy avoids a DP table by making one choice per step — faster, but narrower applicability |
| Coin change is always greedy | Standard USD/EU denominations work greedily; non-canonical denominations (e.g., [1,3,4]) require DP |
| "Pick the largest first" is the universal greedy criterion | The criterion is problem-specific: end time for scheduling, frequency for Huffman, edge weight for MST |

---

### 🚨 Failure Modes & Diagnosis

**1. Greedy produces suboptimal solution (silently)**

**Symptom:** Algorithm output is feasible but not optimal; noticed when comparing with DP solution.

**Root Cause:** Greedy choice property doesn't hold for the specific problem or input.

**Diagnostic:**
```java
// Compare greedy vs DP on identical inputs:
assert greedySolve(input) == dpSolve(input)
    : "Greedy failed on: " + Arrays.toString(input);
```

**Fix:** Use DP if even one counterexample fails. Alternatively, find a different greedy criterion (rare but sometimes possible).

**Prevention:** Never claim greedy correctness without a formal proof or known theoretical result.

---

**2. Wrong sort criterion produces incorrect greedy**

**Symptom:** Greedy returns wrong answers on certain inputs; other inputs are correct.

**Root Cause:** The ordering criterion is subtly wrong (e.g., sorting by start time for activity selection instead of end time).

**Diagnostic:**
```java
// Test with hand-crafted cases:
// Activities: [(1,10),(2,3),(4,5)] — sorted by end time
// Expected: [(2,3),(4,5)] = 2 activities
// If sort by start: [(1,10)] = 1 activity (wrong)
assert activitySelection(acts).size() == 2;
```

**Fix:** Ensure sort key matches the greedy choice property. For activity selection: end time, not start time.

**Prevention:** Trace greedy on 3–4 hand-crafted examples before coding; include a degenerate case (early-starting but late-ending activity should be rejected).

---

**3. Off-by-one in greedy scan**

**Symptom:** Greedy produces one too few or one too many selections.

**Root Cause:** Boundary condition in greedy comparison (`>=` vs `>`, off-by-one in end time).

**Diagnostic:**
```java
// Use exact boundary input: two activities with same end time
// Activities: [(1,5),(3,5)] — both end at 5
// Expected: only one selected (they overlap at end = start)
```

**Fix:** Verify the overlap condition (strictly overlapping: `start < lastEnd`, or non-overlapping: `start >= lastEnd`).

**Prevention:** Define "compatible" precisely: "activity starts at or after last selected activity ends" → `act.start >= lastEnd`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Time Complexity / Big-O` — greedy complexity analysis requires understanding sorting and iteration.
- `Priority Queue` — many greedy algorithms use a priority queue to always select the minimum/maximum efficiently.

**Builds On This (learn these next):**
- `Dijkstra` — shortest-path algorithm using greedy: always process the nearest unvisited node.
- `Kruskal / Prim` — minimum spanning tree algorithms using greedy edge selection.
- `Huffman Coding` — greedy tree construction based on character frequencies.

**Alternatives / Comparisons:**
- `Dynamic Programming` — when greedy fails (no greedy choice property), use DP.
- `Backtracking` — exhaustive correct-by-construction search when neither greedy nor DP applies.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Algorithm making locally-optimal choices  │
│              │ at each step; globally optimal when GCP   │
│              │ holds                                     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ DP and backtracking are too slow for      │
│ SOLVES       │ problems where local optima compose       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Correctness is NOT obvious — must prove   │
│              │ the Greedy Choice Property per problem    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Scheduling (end time), MST, Huffman,      │
│              │ fractional knapsack, coin change (canon.) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ 0/1 knapsack, TSP, non-canonical coin     │
│              │ systems — use DP or backtracking          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N log N) speed vs only works for        │
│              │ specific problem structures               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Take the best now, never look back —     │
│              │  but prove it's safe to do so first"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dynamic Programming → Dijkstra → Huffman  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The activity selection problem with identical end times: suppose you have N activities all ending at time 10, with start times 1, 2, 3, ..., N. Which activities can be selected? How many? What does this reveal about the activity selection greedy algorithm's behavior at the boundary, and does the greedy choice property still hold (does "earliest end time first" still produce the optimal count)? How would you handle ties in the greedy criterion to ensure deterministic and correct behavior?

**Q2.** Dijkstra's algorithm is a greedy algorithm that always processes the nearest unvisited node. It fails (produces wrong results) on graphs with negative edge weights. Explain precisely why the Greedy Choice Property fails for Dijkstra on negative edges: construct a minimal counterexample (graph with 3 nodes, one negative edge) and trace why relaxing a node via the greedy "minimum distance" choice locks in a suboptimal path. How does Bellman-Ford's non-greedy approach avoid this failure?

