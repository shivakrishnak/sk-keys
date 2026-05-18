---
id: DSA-121
title: "Greedy vs Global Optimization - Universal Principle"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-037, DSA-038
used_by: DSA-122
related: DSA-037, DSA-038, DSA-120
tags:
  - meta
  - greedy
  - dynamic-programming
  - optimization
  - principle
  - problem-solving
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 121
permalink: /technical-mastery/dsa/greedy-vs-global/
---

## TL;DR

Greedy algorithms make locally optimal choices at each
step; global optimization (DP, ILP) finds the globally
optimal solution. Knowing when greedy is provably correct
vs when you must use global optimization is the core skill.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-121 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | greedy, dynamic programming, global optimization, correctness |
| **Prerequisites** | DSA-037, DSA-038 |

---

### The Core Question: When is Greedy Correct?

```
Greedy is PROVABLY CORRECT if both of these hold:

1. Optimal Substructure:
   Optimal solution to problem contains optimal solutions
   to subproblems.
   (Also required for DP - DP uses overlapping subproblems)

2. Greedy Choice Property:
   A globally optimal solution can be reached by making
   locally optimal (greedy) choices at each step.
   Key: you never need to "undo" a greedy choice.

If ONLY property 1 holds (not 2): use Dynamic Programming.
If NEITHER holds: use backtracking/branch-and-bound/heuristics.
```

---

### Classical Examples: Greedy Works vs Fails

```
GREEDY WORKS (Interval Scheduling):
  Problem: given intervals, select maximum non-overlapping set.
  Greedy: always pick interval with EARLIEST END TIME.
  
  Proof: Suppose we pick interval A (earliest end) and
         the optimal solution picks B (not earliest end).
         We can swap B for A: A ends no later than B,
         so the next interval that fits after A also fits
         after B. We never lose intervals by swapping.
         This is the "Exchange Argument" proof technique.
  
  Result: O(n log n) - sort by end time, then greedy scan.

GREEDY FAILS (0/1 Knapsack):
  Problem: maximize value in knapsack capacity W.
           Items cannot be split (0/1).
  Greedy: pick highest value/weight ratio.
  
  Counterexample:
    Items: {value=10, weight=5}, {value=6, weight=3}, {value=6, weight=3}
    Capacity: 6
    Greedy picks {10,5} first (ratio 2.0), then can't fit others -> value=10
    Optimal: pick {6,3} + {6,3} -> value=12
    
  Why greedy fails: picking item A precludes items B+C together
                    Local optimality (ratio) != global optimality.
  Solution: Use Dynamic Programming O(n*W) or fractional
            relaxation + branch-and-bound.
  
GREEDY WORKS ON FRACTIONAL KNAPSACK:
  If items CAN be split, greedy by ratio is optimal!
  Reason: fractional means no "commitment" - you can take
          exactly the right fraction without preclusion.
  This is why greedy choice property matters:
  0/1 commitments break greedy; fractional allows it.
```

---

### Decision Framework: Greedy vs DP vs Heuristic

```
DECISION TREE:

Problem: find optimal solution

Is it a combinatorial optimization (subsets, permutations)?
  YES:
    Does greedy choice property hold?
      YES: Greedy (O(n log n) or O(n))
      NO: Is n small enough for DP? (n <= 10^5 typically)
        YES: Dynamic Programming (O(n^2) or O(n*W))
        NO: NP-Complete? Use approximation algorithm or heuristic
  
  NO (continuous or fractional):
    Usually greedy or linear programming

Proof strategy:
  To prove greedy is correct: Exchange Argument
    "Assume optimal differs from greedy. Show we can swap
     the greedy choice in without making things worse."
  To prove greedy is wrong: find a counterexample
    Small cases (n=3 or 4) often suffice.

Production heuristic when NP-Complete:
  Simulated annealing: accept worse solution with probability
                       e^(-delta/T), cooling temperature T
  Genetic algorithms: evolve population toward fitness
  Both: no correctness guarantee, empirically good for many inputs
```

---

### Dijkstra's Algorithm - Greedy on Graphs

```
Dijkstra: find shortest path in graph with NON-NEGATIVE weights
  Greedy choice: always process unvisited node with minimum
                  current distance estimate
  
Why greedy works here:
  Non-negative weights: once we set distance[v], no later
  path can make it shorter (triangle inequality with positive edges)
  Formally: optimal substructure + greedy choice property hold.

Why greedy FAILS for negative weights:
  Negative edges can create "going around the long way" savings.
  Greedy commits too early. Solution: Bellman-Ford (DP, O(V*E)).
  
Why greedy FAILS for maximizing distance:
  "Longest path" is NP-Complete in general graphs.
  (Dijkstra-style greedy does not have optimal substructure
   for maximization.)

Practical:
  Google Maps: Dijkstra + A* (heuristic for direction bias)
  Waze: Bidirectional Dijkstra for speed
  Negative weights rarely exist in road networks
  (but can appear in financial arbitrage graphs!)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Try greedy first; if it doesn't work, switch to DP" | This is dangerous without proof. Greedy can appear to work on test cases and fail on edge cases. PROVE greedy correctness with exchange argument FIRST, then implement |
| "DP always gives better solutions than greedy" | When greedy is correct, it gives the SAME optimal solution as DP, in O(n log n) vs O(n^2) time. Greedy is not approximate - it's exact when the greedy choice property holds |
| "Greedy algorithms are simple; DP is hard" | The difficulty is proving correctness, not implementing. Interval scheduling greedy is trivial to code but requires a formal proof. The proof is the hard part |

---

### Mastery Checklist

- [ ] Can state greedy choice property and optimal substructure
- [ ] Knows the exchange argument proof technique
- [ ] Can construct a counterexample to show greedy fails for 0/1 knapsack
- [ ] Understands why Dijkstra requires non-negative weights

---

### The Surprising Truth

Dijkstra's algorithm was developed by Edsger Dijkstra in
1956 during a 20-minute coffee shop visit with his
then-fiancee. He later said he designed it without paper
because writing was too tedious, and when he returned home
he was surprised at how clean the algorithm was. The
algorithm was first published in 1959 in a 2-page paper.
The greedy correctness proof - that committing to the
minimum-distance unvisited node is always globally optimal
for non-negative edges - took much longer to formalize
than the algorithm itself. This pattern recurs in computer
science: simple greedy algorithms that are provably correct
are often discovered first, and the formal proof machinery
catches up later.
