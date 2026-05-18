---
id: DSA-062
title: Floyd-Warshall Algorithm (All-Pairs Shortest Path)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-060, DSA-061
used_by: DSA-077
related: DSA-060, DSA-061
tags:
  - algorithms
  - floyd-warshall
  - all-pairs-shortest-path
  - apsp
  - dynamic-programming
  - o-v3
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/dsa/floyd-warshall/
---

## TL;DR

Floyd-Warshall computes shortest paths between ALL pairs of
nodes in O(V^3) with O(V^2) space - a 3-line DP that works
with negative edges and detects negative cycles.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-062 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, Floyd-Warshall, APSP, DP |
| **Prerequisites** | DSA-060, DSA-061 |

---

### The Problem This Solves

Dijkstra from each source computes APSP in O(V*(V+E)logV).
For dense graphs where E ≈ V^2, this is O(V^3 log V).
Floyd-Warshall achieves O(V^3) with remarkably simple code:
3 nested loops, no heap, no recursion - the entire algorithm
is 3 lines of inner logic.

---

### Textbook Definition

Floyd-Warshall computes all-pairs shortest paths using DP.
State: `dist[i][j][k]` = shortest path from i to j using
only nodes {1..k} as intermediates. Transition:
`dist[i][j][k] = min(dist[i][j][k-1], dist[i][k][k-1] + dist[k][j][k-1])`.
After iteration k, all paths through nodes 1..k are optimal.
Negative cycles detected if dist[i][i] < 0 after completion.
Time: O(V^3). Space: O(V^2) with in-place optimization.

---

### How It Works

**Implementation (surprisingly simple):**

```java
int[][] floydWarshall(int[][] graph, int n) {
    // graph[i][j] = edge weight, INF if no edge
    int[][] dist = new int[n][n];
    for (int i = 0; i < n; i++)
        dist[i] = graph[i].clone();

    // Try each node k as intermediate point
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                // Can we improve i→j by going through k?
                if (dist[i][k] != Integer.MAX_VALUE &&
                    dist[k][j] != Integer.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }

    // Check for negative cycles:
    // If dist[i][i] < 0, node i is on a negative cycle
    for (int i = 0; i < n; i++) {
        if (dist[i][i] < 0) {
            throw new RuntimeException("Negative cycle at " + i);
        }
    }
    return dist;
}
```

**The DP insight (why k is the outer loop):**

```
When k is outer: "After considering k as intermediate,
all dist[i][j] use only nodes 0..k as intermediates."

If k were inner, dist[i][j] might use node k+1 before
we've considered it - breaking the DP invariant.
Wrong:
  for i, for j, for k → answer using ALL k at once
                         (uses future k, incorrect)
Correct:
  for k, for i, for j → build up k-step answers
```

---

### Comparison Table

| Property | Dijkstra * V | Floyd-Warshall |
|---------|-------------|---------------|
| Time | O(V*(V+E)logV) | O(V^3) |
| Space | O(V+E) | O(V^2) |
| Negative edges | No | Yes |
| Dense graphs | O(V^3 log V) | O(V^3) ← wins |
| Sparse graphs | O(V*E*logV) | O(V^3) |
| Code complexity | Moderate | 3 lines |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Floyd-Warshall is always worse than Dijkstra" | For dense graphs or when all-pairs are needed, Floyd-Warshall is simpler and competitive |
| "The k loop order doesn't matter" | k MUST be the outermost loop. This is critical to the DP correctness |

---

### Failure Modes & Diagnosis

**Failure: Wrong shortest paths**
- Cause: k is not the outermost loop; initialized with 0
  on diagonal but INF for self-loops when edge exists
- Fix: Verify loop order is k,i,j; initialize dist[i][i]=0
  always (a node is 0 distance from itself)

---

### Quick Reference Card

| Property | Floyd-Warshall |
|---------|---------------|
| Time | O(V^3) |
| Space | O(V^2) |
| Negative edges | Yes |
| Negative cycle detection | dist[i][i] < 0 |
| Output | V x V shortest-path matrix |
| Best for | Dense graphs, small V (V ≤ 500) |

---

### The Surprising Truth

Floyd-Warshall is the basis for transitive closure
computation. Replace "min(a+b, c)" with "(a AND b) OR c"
(boolean OR/AND) and you get the Warshall algorithm
(Robert Warshall, 1962) for computing reachability in
graphs - whether any path exists between every pair of
nodes. This boolean variant runs in O(V^3) using bitwise
operations on adjacency matrix rows, and is used in
program analysis (can variable A reach statement B?).

---

### Mastery Checklist

- [ ] Can implement Floyd-Warshall from memory (5 lines)
- [ ] Understands why k must be the outer loop
- [ ] Knows negative cycle detection via diagonal check

---

### Interview Deep-Dive

**Q1 (Hard):** Find the minimum number of currency
conversions to convert any currency to any other, with
negative arbitrage handled.

> This is an all-pairs shortest path problem. Use
> Floyd-Warshall with edge weight = -log(exchange_rate).
> Handles negative edges (rates < 1 mean negative log).
> After completion, check diagonal: if dist[i][i] < 0,
> currency i is on an arbitrage cycle.
> For pure conversion-hop-count (not rate), use BFS or
> Floyd-Warshall with unit weights.
> Time: O(V^3) where V = number of currencies (small).
> Result matrix: dist[i][j] = cheapest conversion cost.
