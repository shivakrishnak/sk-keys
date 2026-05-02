---
layout: default
title: "A* Search"
parent: "Data Structures & Algorithms"
nav_order: 61
permalink: /dsa/a-star-search/
number: "0061"
category: Data Structures & Algorithms
difficulty: â˜…â˜…â˜…
depends_on: Dijkstra, Priority Queue, Graph, Heuristic Functions
used_by: GPS Navigation, Game Pathfinding, Robotics Motion Planning
related: Dijkstra, Greedy Best-First Search, Bidirectional Dijkstra
tags:
  - algorithm
  - graph
  - advanced
  - deep-dive
  - pattern
  - performance
---

# 061 â€” A* Search

âš¡ TL;DR â€” A* finds shortest paths faster than Dijkstra by using a heuristic to guide expansion toward the goal, exploring far fewer nodes when the heuristic is accurate.

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #061         â”‚ Category: Data Structures & Algorithms â”‚ Difficulty: â˜…â˜…â˜…        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ Dijkstra, Priority Queue, Graph,       â”‚                        â”‚
â”‚              â”‚ Heuristic Functions                    â”‚                        â”‚
â”‚ Used by:     â”‚ GPS Navigation, Game Pathfinding,      â”‚                        â”‚
â”‚              â”‚ Robotics Motion Planning               â”‚                        â”‚
â”‚ Related:     â”‚ Dijkstra, Greedy Best-First Search,    â”‚                        â”‚
â”‚              â”‚ Bidirectional Dijkstra                 â”‚                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

### ðŸ”¥ The Problem This Solves

WORLD WITHOUT IT:
You are building a game with a 1,000 Ã— 1,000 grid map. A player asks for the path from their position to a destination 800 cells away. Dijkstra's algorithm explores outward in all directions from the source â€” expanding a circle of radius 800, touching up to 2 million cells â€” many of them in the wrong direction, far from the actual destination.

THE BREAKING POINT:
Dijkstra is optimal in its exploration â€” it finds the shortest path â€” but it is direction-blind. It expands equally in all directions regardless of where the goal is. For large maps with a specific destination, most of Dijkstra's exploration is wasted effort in the wrong direction.

THE INVENTION MOMENT:
Dijkstra prioritises `g(n)` â€” the actual known distance from source to node `n`. What if we also added a guess `h(n)` â€” the estimated remaining distance from `n` to the goal? Prioritise by `f(n) = g(n) + h(n)`. Nodes that are both close to the source AND estimated close to the goal get priority. With a good estimate (e.g., Euclidean distance), A* explores a narrow corridor toward the goal instead of expanding in all directions. This is exactly why **A* Search** was created.

### ðŸ“˜ Textbook Definition

**A* Search** is an informed best-first search algorithm that finds the shortest path between a source and a goal node by maintaining a priority queue ordered by `f(n) = g(n) + h(n)`, where `g(n)` is the exact cost from source to `n` and `h(n)` is an **admissible heuristic** â€” an estimate of the cost from `n` to the goal that never overestimates. When `h(n)` is admissible and consistent (monotone), A* is complete (finds a solution if one exists) and optimal (finds the shortest path). Time complexity ranges from O(E log V) with a near-perfect heuristic to O((V+E) log V) when `h(n)=0` (reducing to Dijkstra).

### â±ï¸ Understand It in 30 Seconds

**One line:**
Find the shortest path by always expanding the node closest to "distance traveled + estimated distance remaining."

**One analogy:**
> Imagine navigating a maze by always moving toward the exit (you can roughly see which direction it is). Instead of exploring every tunnel, you preferentially take tunnels pointing toward the exit. When you hit dead ends, you backtrack â€” but most of the time the direction sense gets you there faster than random exploration.

**One insight:**
A* is only as good as its heuristic. With `h(n) = 0`, A* reduces exactly to Dijkstra. With a perfect heuristic (h(n) = true remaining distance), A* explores only the nodes on the optimal path. The **admissibility** condition (`h(n)` never overestimates) is what preserves the optimality guarantee â€” it ensures A* never dismisses a path that could be shorter.

### ðŸ”© First Principles Explanation

CORE INVARIANTS:
1. `f(n) = g(n) + h(n)` where `g(n)` is exact cost from source to `n`, and `h(n)` is an admissible estimate of cost to goal.
2. **Admissibility**: `h(n) â‰¤ actual_distance(n, goal)` for all `n`. This ensures no node on the optimal path is incorrectly deprioritised.
3. **Consistency (monotonicity)**: `h(n) â‰¤ cost(n â†’ n') + h(n')` for any edge (nâ†’n'). This is equivalent to "f values never decrease along a path" â€” guaranteeing the first-pop finalisation invariant (same as Dijkstra).

DERIVED DESIGN:
When the goal is popped from the priority queue, `g(goal)` is the shortest path. Proof by contradiction: suppose a shorter path to goal exists. Every node on that shorter path would have f-value â‰¤ shorter path's total cost (because h is admissible). That node would have been popped before goal. A shorter path to goal would have been found first. Contradiction.

**Common admissible heuristics:**
- 4-directional grid: Manhattan distance `|x1-x2| + |y1-y2|`
- Euclidean space / 8-directional: Euclidean distance `sqrt((x1-x2)Â² + (y1-y2)Â²)`
- Road networks: Haversine distance between GPS coordinates

**Why h=0 is always admissible (degenerates to Dijkstra):**
0 â‰¤ actual distance for all nodes. So Dijkstra is a special case of A* â€” a fully uninformed A*.

THE TRADE-OFFS:
Gain: Explores fewer nodes than Dijkstra when heuristic is tight; same correctness guarantees.
Cost: Requires a domain-specific admissible heuristic to design and validate; memory unchanged at O(V) worst case; inadmissible heuristic sacrifices optimality silently.

### ðŸ§ª Thought Experiment

SETUP:
4Ã—4 grid, all moves cost 1. Source = top-left (0,0). Goal = bottom-right (3,3). Manhattan distance heuristic: `h(r,c) = (3-r) + (3-c)`.

DIJKSTRA (no heuristic):
Expands distance rings outward: distance 0 (1 cell), distance 1 (2 cells), distance 2 (3 cells), distance 3 (4 cells), distance 4 (3 cells), distance 5 (2 cells), distance 6 (goal). Explores approximately 13 cells.

A* (Manhattan heuristic):
f(0,0) = 0+6 = 6. Explores only nodes along the diagonal where f=6. Reaches (3,3) after exploring approximately 7 cells â€” only the corridor along the optimal path diagonal.

THE INSIGHT:
The Manhattan heuristic confines A* to the "corridor" of nodes on or near the optimal path. Cells far from the diagonal (top-right corner, bottom-left corner) have f > 6 and are never explored. The heuristic acts as a focus beam, eliminating irrelevant exploration â€” which is exactly what makes A* faster than Dijkstra in practice.

### ðŸ§  Mental Model / Analogy

> A* is like a GPS that combines two signals: how far you have already driven (g), and the straight-line remaining distance to your destination (h). It always sends you down the road that minimises total estimated trip time. A GPS with only the driven distance (Dijkstra) zigzags uniformly in all directions. A GPS with only the remaining estimate (greedy best-first) drives in a straight line and gets stuck in cul-de-sacs. A* uses both to navigate intelligently.

"Distance already driven" â†’ g(n) = exact cost from source to n
"Straight-line remaining estimate" â†’ h(n) = heuristic estimate to goal
"Total estimated trip length" â†’ f(n) = g(n) + h(n)
"Always pick next road minimising total" â†’ priority queue ordered by f

Where this analogy breaks down: GPS estimates can be wrong (traffic). An inadmissible heuristic (overestimates) causes A* to skip the optimal path â€” the GPS would send you on a suboptimal route without warning.

### ðŸ“¶ Gradual Depth â€” Four Levels

**Level 1 â€” What it is (anyone can understand):**
A* is a smarter path-finder. Instead of exploring all directions equally, it focuses toward the goal using a rough estimate of how far away it is. Like searching for your keys by starting in rooms nearest where you last had them, rather than searching every room alphabetically.

**Level 2 â€” How to use it (junior developer):**
Take Dijkstra's code and replace the priority key `dist[n]` with `dist[n] + h(n)`. Choose h(n) based on your domain: Manhattan for 4-directional grids, Euclidean for 2D space, 0 for general graphs. Verify that h(n) never overestimates the true remaining cost. Everything else is identical to Dijkstra â€” same lazy deletion, same parent tracking.

**Level 3 â€” How it works (mid-level engineer):**
A* maintains an "open set" (priority queue by f) and tracks g-values. Consistency guarantees f-values are non-decreasing along paths, enabling the same lazy-deletion correctness as Dijkstra. Weighted A* (`f = g + w*h`, w > 1) explores fewer nodes but may return a path up to w times the optimal length â€” useful when bounded suboptimality is acceptable (real-time games). IDA* uses iterative deepening with f-cost bounds to achieve O(path length) memory at the cost of repeated re-exploration.

**Level 4 â€” Why it was designed this way (senior/staff):**
A* (Hart, Nilsson, Raphael, 1968) is information-theoretically optimal: among all best-first algorithms using the same admissible heuristic, A* expands the minimum number of nodes to guarantee optimality. The heuristic h encodes domain knowledge â€” better heuristics = fewer expanded nodes. In game AI, Jump Point Search (JPS) exploits grid symmetry to skip equivalent paths, reducing A* explored nodes by ~10x on open maps. In robotics, A* on discretised configuration spaces uses bespoke heuristics that account for kinodynamic constraints, ensuring the heuristic remains admissible despite the continuous space approximation.

### âš™ï¸ How It Works (Mechanism)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ A* Algorithm                               â”‚
â”‚                                            â”‚
â”‚  g[src]=0, g[v]=âˆž for all vâ‰ src            â”‚
â”‚  pq = MinHeap by f(n) = g(n)+h(n)         â”‚
â”‚  pq.offer( (h(src), src) )                 â”‚
â”‚                                            â”‚
â”‚  LOOP while pq not empty:                  â”‚
â”‚    (f, u) = pq.poll()                      â”‚
â”‚    if u == goal: return g[goal]            â”‚
â”‚    if f > g[u]+h(u): continue â† stale    â”‚
â”‚                                            â”‚
â”‚    for each edge (uâ†’v, weight w):          â”‚
â”‚      newG = g[u] + w                       â”‚
â”‚      if newG < g[v]:                       â”‚
â”‚        g[v] = newG                         â”‚
â”‚        parent[v] = u                       â”‚
â”‚        pq.offer((newG + h(v), v))          â”‚
â”‚                                            â”‚
â”‚  return -1 (no path exists)                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

The only change from Dijkstra: priority key is `g[v] + h(v)` instead of `g[v]`. When h=0 everywhere, f=g and the algorithm is exactly Dijkstra.

### ðŸ”„ The Complete Picture â€” End-to-End Flow

NORMAL FLOW:
```
Graph + source + goal + heuristic function h
â†’ Initialize g[src]=0
â†’ Push (h(src), src) to min-heap
â†’ [A* â† YOU ARE HERE]
  â†’ Pop min-f node u
  â†’ If u == goal: done, return g[u]
  â†’ Relax edges: update g[v], push (g[v]+h(v), v)
â†’ Reconstruct path via parent[]
â†’ Return optimal distance to goal
```

FAILURE PATH:
```
Inadmissible heuristic: h(n) > true distance
â†’ Optimal-path nodes get higher f than
  suboptimal-path nodes
â†’ A* pops suboptimal path before optimal
â†’ Returns wrong (too large) distance
â†’ Silent failure â€” no runtime error
â†’ Debug: compare A* vs Dijkstra on same input
```

WHAT CHANGES AT SCALE:
For city-scale road networks (V=10 million), A* with Euclidean heuristic still explores millions of nodes. Production GPS uses bidirectional A* plus Contraction Hierarchies: preprocessing builds a hierarchy allowing A* to skip low-importance roads entirely. This reduces query time from seconds (Dijkstra) to milliseconds (CH+A*).

### ðŸ’» Code Example

**Example 1 â€” A* on 2D grid:**
{%- raw -%}
```java
static final int INF = Integer.MAX_VALUE;

int astar(int[][] grid,
    int[] src, int[] goal) {
    int R = grid.length, C = grid[0].length;
    int sr=src[0],sc=src[1],gr=goal[0],gc=goal[1];

    int[][] g = new int[R][C];
    for (int[] row : g) Arrays.fill(row, INF);
    g[sr][sc] = 0;

    // PQ: [f, row, col]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(
            Comparator.comparingInt(a -> a[0]));
    pq.offer(new int[]{h(sr,sc,gr,gc), sr, sc});

    int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};

    while (!pq.isEmpty()) {
        int[] cur = pq.poll();
        int r = cur[1], c = cur[2];
        if (r==gr && c==gc) return g[gr][gc];

        // Lazy deletion: skip stale entries
        if (cur[0] != g[r][c]+h(r,c,gr,gc))
            continue;

        for (int[] d : dirs) {
            int nr=r+d[0], nc=c+d[1];
            if (nr<0||nr>=R||nc<0||nc>=C
                ||grid[nr][nc]==1) continue;
            int ng = g[r][c] + 1;
            if (ng < g[nr][nc]) {
                g[nr][nc] = ng;
                pq.offer(new int[]{
                    ng + h(nr,nc,gr,gc), nr, nc});
            }
        }
    }
    return -1; // no path
}

// Manhattan distance (admissible for 4-dir)
int h(int r,int c,int gr,int gc) {
    return Math.abs(r-gr)+Math.abs(c-gc);
}
```
{%- endraw -%}

**Example 2 â€” Verify admissibility:**
```java
// Unit test: heuristic must never overestimate
void verifyAdmissibility(int[][] grid,
    int[] goal) {
    // Compute true distances to goal via BFS
    int[][] trueDist = bfsAllDistances(
        grid, goal);

    for (int r = 0; r < grid.length; r++) {
        for (int c = 0; c < grid[0].length; c++) {
            if (grid[r][c] == 1) continue;
            int h = h(r, c, goal[0], goal[1]);
            int td = trueDist[r][c];
            assert h <= td
                : "Inadmissible at (" + r
                + "," + c + "): h=" + h
                + " true=" + td;
        }
    }
}
```

**Example 3 â€” Weighted A* for speed over optimality:**
```java
// w=1.5: path cost <= 1.5 * optimal
// Explores far fewer nodes than standard A*
double W = 1.5;

PriorityQueue<double[]> pq =
    new PriorityQueue<>(
        Comparator.comparingDouble(a -> a[0]));
double[] gCost = new double[n];
Arrays.fill(gCost, Double.MAX_VALUE);
gCost[src] = 0;
pq.offer(new double[]{W * h(src,goal), src});

while (!pq.isEmpty()) {
    double[] cur = pq.poll();
    int u = (int)cur[1];
    if (u == goal) return gCost[goal];
    for (int[] edge : graph[u]) {
        int v = edge[0];
        double w = edge[1];
        double ng = gCost[u] + w;
        if (ng < gCost[v]) {
            gCost[v] = ng;
            pq.offer(new double[]{
                ng + W*h(v,goal), v});
        }
    }
}
```

### âš–ï¸ Comparison Table

| Algorithm | Heuristic | Optimal | Nodes Explored | Time | Best For |
|---|---|---|---|---|---|
| **A*** | Admissible h(n) | Yes | Focused (heuristic quality) | O(E log V) | Map/game pathfinding, known goal |
| Dijkstra | None (h=0) | Yes | All reachable | O((V+E) log V) | General weighted graphs |
| Greedy Best-First | h(n) only | No | Minimal (fast but wrong) | O(E log V) | Approximate, real-time game AI |
| Weighted A* | w * h(n) | Bounded â‰¤ wÃ—opt | Between A* and Greedy | O(E log V) | Real-time constraint, bounded suboptimality |
| IDA* | Admissible h(n) | Yes | Same as A* | O(same) | Low-memory environments |

How to choose: Use A* when you have a good admissible heuristic and need optimal paths. Use Dijkstra for general graphs without a heuristic. Use weighted A* when bounded suboptimality is acceptable for speed gains.

### âš ï¸ Common Misconceptions

| Misconception | Reality |
|---|---|
| Any heuristic makes A* faster than Dijkstra | An inadmissible heuristic makes A* incorrect. Only admissible heuristics guarantee both correctness and potential exploration reduction |
| A* always uses less memory than Dijkstra | A* and Dijkstra have the same O(V) asymptotic memory. A* may expand fewer nodes in practice, resulting in a smaller open set â€” but worst case is identical |
| h(n)=0 makes A* equal to BFS | h(n)=0 makes A* equal to Dijkstra. BFS is for unweighted graphs. Dijkstra equals BFS only when all edge weights are 1 |
| Admissible always implies consistent | Admissibility does not imply consistency. A consistent heuristic is always admissible. Most real-world heuristics (Manhattan, Euclidean) are both, but the implication is one-directional |
| A* with admissible heuristic always terminates correctly | Only if the heuristic is also consistent (for the standard lazy-deletion implementation). Admissible-but-inconsistent heuristics may require re-processing already-closed nodes |

### ðŸš¨ Failure Modes & Diagnosis

**1. Inadmissible heuristic returns suboptimal path**

Symptom: A* returns a longer path than Dijkstra (h=0) on the same graph.

Root Cause: `h(n) > true_remaining_distance(n, goal)` for some node n. That node gets a higher f-value than it deserves, causing it to be deprioritised. The optimal path through n is never found first.

Diagnostic:
```java
// Sample random nodes and compare h vs true dist:
int[] trueDist = dijkstra(graph, goal);
for (int n = 0; n < V; n++) {
    assert heuristic(n) <= trueDist[n]
        : "Inadmissible at node " + n;
}
```

Fix: Reduce heuristic values to ensure they never exceed true remaining distances. Euclidean distance is always admissible for unit-cost edges in Euclidean space.

Prevention: Unit-test heuristic admissibility against BFS/Dijkstra ground truth on representative test cases.

---

**2. A* slower than expected on maze-like graphs**

Symptom: A* explores more nodes than Dijkstra for certain graphs despite having a "good" heuristic.

Root Cause: Maze-like graphs have many walls and dead ends. The heuristic estimates a short remaining distance, but the actual path navigates around walls â€” the heuristic is very loose relative to the true remaining distance. Each dead end forces backtracking, and A* re-explores heavily.

Diagnostic:
```bash
# Count nodes expanded in both:
# Dijkstra expanded: N1 nodes
# A* expanded: N2 nodes
# If N2 > 0.8 * N1, heuristic provides little value
```

Fix: Accept that A* provides less benefit on maze-like graphs. Use or accept Dijkstra, or design a better heuristic that accounts for obstacles (e.g., True Distance Heuristic precomputed via backward BFS from goal).

Prevention: Benchmark A* on representative graphs. Report "ratio of A* nodes to Dijkstra nodes" as a heuristic quality metric.

---

**3. Goal check missing â€” explores entire graph**

Symptom: A* always runs to completion even when goal is very close to source.

Root Cause: The early exit check `if (u == goal) return g[goal]` is missing. A* explores all reachable nodes before returning.

Diagnostic:
```java
// Add explicit termination log:
int popped = 0;
while (!pq.isEmpty()) {
    int u = pq.poll()[1];
    popped++;
    if (u == goal) {
        System.out.println("Goal reached after "
            + popped + " pops");
        return g[goal];
    }
    // ...
}
// If "Goal reached" never prints â†’ goal check missing
```

Fix: Add `if (u == goal) return g[goal];` immediately after popping from the priority queue.

Prevention: The goal-check is always required in A* â€” it is the primary optimisation over running to completion.

### ðŸ”— Related Keywords

**Prerequisites (understand these first):**
- `Dijkstra` â€” A* is Dijkstra with a heuristic; you must understand Dijkstra's priority queue and edge relaxation first.
- `Priority Queue` â€” the min-heap ordered by f(n) is A*'s core data structure.
- `Graph` â€” A* operates on weighted directed graphs; understand adjacency list representations.

**Builds On This (learn these next):**
- `Jump Point Search (JPS)` â€” A* specialisation for uniform-cost grids that skips symmetric paths, reducing explored nodes by ~10x.
- `IDA* (Iterative Deepening A*)` â€” A* with O(path length) memory via iterative deepening on f-cost threshold.
- `Contraction Hierarchies` â€” preprocessing technique that makes A* on road networks millisecond-fast via shortcut edges.

**Alternatives / Comparisons:**
- `Dijkstra` â€” same optimality guarantee but direction-blind; use when no heuristic is available.
- `Greedy Best-First Search` â€” uses h(n) alone (no g); fast but not optimal; acceptable for real-time games where approximate paths suffice.
- `Bidirectional Dijkstra` â€” explores from both source and goal simultaneously; achieves similar speedup to A* without needing a heuristic.

### ðŸ“Œ Quick Reference Card

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ WHAT IT IS   â”‚ Dijkstra + admissible heuristic = guided  â”‚
â”‚              â”‚ shortest-path search toward a goal        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ PROBLEM IT   â”‚ Dijkstra explores all directions; need    â”‚
â”‚ SOLVES       â”‚ focused search when goal is known         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ KEY INSIGHT  â”‚ Admissibility (h â‰¤ true remaining cost)   â”‚
â”‚              â”‚ preserves optimality; h=0 = Dijkstra      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Physical map routing, game pathfinding,   â”‚
â”‚              â”‚ known goal with a distance-like metric    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ No good heuristic (use Dijkstra); graphs  â”‚
â”‚              â”‚ with negative edges                       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ TRADE-OFF    â”‚ Fewer nodes explored vs heuristic design  â”‚
â”‚              â”‚ complexity; inadmissible h sacrifices opt â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Dijkstra with a compass pointing at      â”‚
â”‚              â”‚  the goal"                                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ JPS â†’ IDA* â†’ Bidirectional A*             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

---
### ðŸ§  Think About This Before We Continue

**Q1.** A* with an admissible heuristic guarantees optimality. Consider a graph where the true shortest path to the goal has cost 10, but the heuristic at the source overestimates the remaining distance as 12, making f(source) = 0+12 = 12. A suboptimal path of true cost 11 reaches the goal with h(goal)=0, giving f=11. A* would pop this suboptimal path first and return 11. Trace exactly which admissibility property is violated, and explain why the proof of A* optimality breaks down when h overestimates.

**Q2.** In a 3D robot configuration space (x, y, z, orientation Î¸), the state space has 10 million discretised states. Euclidean distance to the goal in (x,y,z) is admissible for the spatial component, but Î¸ is a circular variable (0 and 2Ï€ are the same orientation). Design an admissible heuristic that correctly accounts for both spatial and rotational distance. What constraint must the rotational cost function satisfy relative to the minimum rotation arc, and how does the combined heuristic's tightness affect how many nodes A* explores compared to a heuristic that ignores Î¸ entirely?

