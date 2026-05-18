---
id: DSA-067
title: Greedy Algorithm
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-065
used_by: DSA-077
related: DSA-064, DSA-065, DSA-068
tags:
  - algorithms
  - greedy
  - optimization
  - locally-optimal
  - activity-selection
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/dsa/greedy-algorithm/
---

## TL;DR

Greedy algorithms always pick the locally optimal choice
at each step - faster than DP but only correct when the
greedy choice property holds and the problem has optimal
substructure without future regret.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-067 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, greedy, optimization, local-choice |
| **Prerequisites** | DSA-065 |

---

### The Problem This Solves

DP explores all possibilities: O(n^2) or worse. Greedy
makes one irrevocable choice per step: O(n log n) or
O(n). When provably correct, greedy gives the optimal
solution with orders-of-magnitude better performance.
The challenge: proving greedy is correct for a specific
problem.

---

### Textbook Definition

A greedy algorithm builds a solution by always choosing
the locally optimal option at each decision point without
reconsidering previous choices. Correct greedy algorithms
satisfy two properties:
1. Greedy choice property: a globally optimal solution
   can be built by making locally optimal choices
2. Optimal substructure: the optimal solution contains
   optimal solutions to subproblems

Greedy differs from DP: it makes one choice per step
(no reconsidering), DP explores all choices.

---

### How It Works

**Activity selection (canonical greedy problem):**

```java
// Find max number of non-overlapping activities
// each activity is {start, end}
int activitySelection(int[][] activities) {
    // GREEDY CHOICE: always pick the activity
    // that finishes earliest (leaves most room)
    Arrays.sort(activities, Comparator.comparingInt(a -> a[1]));

    int count = 1;
    int lastEnd = activities[0][1];

    for (int i = 1; i < activities.length; i++) {
        if (activities[i][0] >= lastEnd) { // non-overlapping
            count++;
            lastEnd = activities[i][1];
        }
    }
    return count;
}
// O(n log n) for sort, O(n) for scan
// Why correct: picking earliest-finishing activity
// NEVER prevents more activities than any other choice.
// Proof by exchange argument.
```

**When greedy FAILS - the coin change counter-example:**

```java
// coins = {1, 3, 4}, amount = 6
// WRONG: Greedy (largest coin first)
//   Pick 4 → remaining: 2
//   Pick 1 → remaining: 1
//   Pick 1 → remaining: 0
//   Result: 3 coins {4, 1, 1}
//
// CORRECT: DP
//   3+3=6 → 2 coins {3, 3}
//
// Why greedy fails: picking 4 prevents the optimal {3,3}
// The "greedy choice property" does NOT hold here.
```

**Classic greedy algorithms:**

| Problem | Greedy choice | Why correct |
|---------|--------------|-------------|
| Activity selection | Earliest finish | Exchange argument |
| Fractional knapsack | Highest value/weight | Can take fractions |
| Dijkstra | Nearest unvisited | Non-negative weights |
| Kruskal's MST | Lightest safe edge | Cut property |
| Huffman coding | Two lowest-freq nodes | Exchange argument |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Greedy is always wrong; use DP" | Many problems have provably correct greedy solutions that are much faster than DP |
| "If greedy gives the right answer on test cases, it's correct" | Testing cannot prove greedy correctness; counterexamples may be rare; always prove via exchange argument or cut property |

---

### Failure Modes & Diagnosis

**Failure: Greedy gives suboptimal result**
- Root cause: Problem lacks greedy choice property
- Common example: Coin change with unusual denominations
- Diagnosis: Find a counterexample where greedy picks
  a choice that blocks the globally optimal solution
- Fix: Switch to DP or branch-and-bound for the problem

---

### Quick Reference Card

| Greedy works | Greedy fails |
|-------------|-------------|
| Activity selection | Coin change (non-standard coins) |
| Fractional knapsack | 0/1 knapsack |
| MST (Kruskal, Prim) | Longest path |
| Dijkstra | Bellman-Ford scenarios |
| Huffman encoding | General string compression |

---

### The Surprising Truth

Huffman coding (used in JPEG, ZIP, MP3) is a purely greedy
algorithm. The correctness proof uses an exchange argument:
the two lowest-frequency symbols must be siblings at the
deepest level in any optimal code; any deviation can be
improved by swapping. This greedy insight - published by
David Huffman in 1952 as a course assignment at MIT - is
the foundation of all modern lossless compression. His
professor Shannon had a less optimal solution; the student
proved greedy was optimal.

---

### Mastery Checklist

- [ ] Implements activity selection (earliest-finish greedy)
- [ ] Can explain why greedy fails for 0/1 knapsack
- [ ] Knows the exchange argument proof technique

---

### Interview Deep-Dive

**Q1 (Hard):** You have n tasks with deadlines and profits.
Each task takes 1 unit of time. Maximize total profit by
scheduling tasks before their deadlines.

> This is the Job Scheduling problem. Greedy approach:
> 1. Sort tasks by profit descending (greedily pick
>    highest-value tasks first)
> 2. For each task, find the latest available time slot
>    before its deadline using Union-Find for O(alpha(n))
>    slot lookup
> 3. Schedule the task; skip if no slot available
> Time: O(n log n) sort + O(n * alpha(n)) scheduling.
> Exchange argument proof: any solution can be improved
> by replacing a lower-profit task with a higher-profit
> one in the same slot - so sorting by profit and
> greedily filling latest available slots is optimal.
