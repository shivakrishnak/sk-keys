---
layout: default
title: "Graph Coloring"
parent: "Data Structures & Algorithms"
nav_order: 76
permalink: /dsa/graph-coloring/
number: "0076"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Graph, Backtracking, NP-Complete Problems
used_by: Compiler Register Allocation, Scheduling Problems, Map Coloring
related: Backtracking, Greedy Algorithm, Approximation Algorithms
tags:
  - algorithm
  - advanced
  - deep-dive
  - pattern
  - datastructure
---

# 076 — Graph Coloring

⚡ TL;DR — Graph Coloring assigns labels to graph vertices so no two adjacent vertices share a label, modelling conflict-avoidance problems in scheduling, compilers, and maps.

| #0076 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Graph, Backtracking, NP-Complete Problems | |
| **Used by:** | Compiler Register Allocation, Scheduling Problems, Map Coloring | |
| **Related:** | Backtracking, Greedy Algorithm, Approximation Algorithms | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A compiler assigns variables to CPU registers. Each variable has a "live range" — the span where it holds a value. Two variables with overlapping live ranges cannot share a register (one would overwrite the other). How do you assign the minimum number of registers?

THE BREAKING POINT:
With 100 variables and overlapping live ranges, naïve assignment might use 100 registers (one per variable) even though only 6 registers are simultaneously needed. Modern CPUs have 16-32 general-purpose registers; exceeding this requires "spilling" to RAM — 100× slower. Getting this wrong causes catastrophic performance degradation in compiled code.

THE INVENTION MOMENT:
Model variables as graph vertices; draw an edge between any two variables whose live ranges overlap. Now "assign registers" becomes "colour the graph such that no two adjacent vertices share a colour." Minimum registers needed = chromatic number χ(G). This is exactly why **Graph Coloring** is the fundamental model for conflict-avoidance problems.

### 📘 Textbook Definition

**Graph Coloring** is the assignment of labels ("colors") to the vertices of a graph such that no two adjacent vertices (connected by an edge) receive the same color. The **chromatic number** χ(G) is the minimum number of colors required for a valid coloring. The **k-coloring problem** asks whether a graph can be colored with at most k colors; for k ≥ 3, this is NP-complete (no polynomial-time algorithm is known). The **greedy coloring algorithm** achieves at most Δ(G)+1 colors (Δ = maximum vertex degree) in O(V+E) but may not be optimal. Exact algorithms use backtracking with pruning.

### ⏱️ Understand It in 30 Seconds

**One line:**
Assign colors to vertices so neighbours always differ — then find the minimum number of colors needed.

**One analogy:**
> Scheduling university exams: two exams share a student if they conflict (same student takes both). Students studying for conflicting exams cannot take them simultaneously. Assign time slots (colors) to exams (vertices) so no student has two exams at the same time. Minimum time slots = chromatic number of the conflict graph.

**One insight:**
Graph Coloring is NP-complete for k ≥ 3, but several special graph classes are solvable in polynomial time: bipartite graphs (k=2, use BFS), planar graphs (k≤4, Four Color Theorem), interval graphs (k=ω(G), greedy on sorted intervals), and perfect graphs (k=ω(G), polynomial via ellipsoid method). Real-world applications exploit these special structures rather than solving the general NP-complete problem.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A valid coloring requires: ∀ edge (u,v) ∈ E: color(u) ≠ color(v).
2. The chromatic number χ(G) ≥ ω(G) (clique number — the size of the largest complete subgraph; all vertices need different colors).
3. χ(G) ≤ Δ(G) + 1 always (greedy achieves this bound; Brooks' theorem tightens it for most graphs).

DERIVED DESIGN:
**Greedy coloring:** Iterate vertices in some order. For each vertex, assign the smallest color not used by its already-colored neighbours. Runs in O(V + E). Result depends on vertex ordering — different orderings give different chromatic numbers. The **smallest-last ordering** (iteratively remove the minimum-degree vertex) achieves at most degeneracy + 1 colors, which is optimal for chordal and planar graphs.

**Backtracking exact coloring:** Try assigning color 1..k to each vertex recursively. Prune if any two adjacent vertices have the same color. Lower bound: use clique detection; upper bound: greedy solution. With pruning this handles graphs up to ~50 vertices practically.

THE TRADE-OFFS:
Gain: Models a wide class of conflict-avoidance problems exactly; provides optimal register allocation, exam scheduling, frequency assignment.
Cost: NP-complete for k ≥ 3 on general graphs; exact algorithms only practical for small graphs (<100 vertices). Production systems use approximation algorithms (greedy, tabu search, DSATUR heuristic) or polynomial-time algorithms on structured (interval/chordal) graphs.

### 🧪 Thought Experiment

SETUP:
Three university courses: Math, Physics, Chemistry. Students overlap: Math-Physics share 5 students, Math-Chemistry share 8 students, Physics-Chemistry share no students. How many exam time slots are needed?

WHAT HAPPENS WITHOUT GRAPH COLORING:
Assign 3 separate slots (one per course) — safe, but wasteful if fewer slots suffice.

WHAT HAPPENS WITH GRAPH COLORING:
Build conflict graph: vertices={Math, Physics, Chemistry}, edges={(Math,Physics), (Math,Chemistry)}.
Greedy coloring (vertex order: Math, Physics, Chemistry):
- Math → color 1.
- Physics → adjacent to Math(1) → assign color 2.
- Chemistry → adjacent to Math(1), not Physics → assign color 2 (reuse Physics's slot!).
Result: 2 slots: {Math in slot 1}, {Physics, Chemistry in slot 2}. Physics and Chemistry can be simultaneous since no student takes both.

THE INSIGHT:
Graph coloring reduces "can these two things simultaneously occur?" to an edge existence check. The chromatic number directly translates to the minimum resource count (slots, registers, frequencies). Every conflict-avoidance problem that can be expressed as a graph is immediately solved by graph coloring.

### 🧠 Mental Model / Analogy

> Graph Coloring is a map-maker's problem. On a map, countries sharing a border must get different colors so they're visually distinct. The Four Color Theorem says 4 colors always suffice for any flat map. A country's color is assigned by looking at its neighbours and picking any unused color — that's greedy coloring.

"Countries" → graph vertices
"Shared border" → graph edge
"Map colors" → assigned label/color
"Minimum colors needed" → chromatic number χ(G)
"No two bordering countries same color" → no two adjacent vertices same color

Where this analogy breaks down: Real maps are planar graphs (always 4-colorable); general graphs like register interference graphs are non-planar and may require more colors. The map analogy doesn't communicate the NP-completeness of the general case.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Graph Coloring is the challenge of painting a network's dots so that no two connected dots share the same color, using as few colors as possible. It models any situation where conflicting items cannot be assigned the same resource.

**Level 2 — How to use it (junior developer):**
Implement greedy coloring: for each vertex (in any order), assign the smallest color not used by its neighbours. Use a boolean array `usedColors[k]` scanned for each neighbour. This gives a valid coloring in O(V + E) but may use more colors than χ(G). For interval scheduling (1D overlap), sort by start time and greedily assign: optimal for interval graphs.

**Level 3 — How it works (mid-level engineer):**
DSATUR (Degree of Saturation) heuristic: always color the vertex with the most distinctly colored neighbours next (highest saturation). Tie-break by vertex degree. This often achieves χ(G) in practice. DSATUR is optimal for bipartite and cycle graphs and outperforms simple greedy significantly. For register allocation, compilers use a simplified Chaitin-Briggs algorithm: build interference graph, greedy-color with spilling — mark uncolorable vertices as "spilled to memory."

**Level 4 — Why it was designed this way (senior/staff):**
Chaitin's 1982 paper proved register allocation is equivalent to graph coloring, converting compiler optimisation into a graph theory problem. Modern compilers (LLVM, GCC) use a simplified coalescing-friendly coloring where **copy-related** variables (from phi-nodes) are preferentially assigned the same color when possible (copy elimination). General graph coloring being NP-complete is a practical concern: for 1000-variable functions, exact coloring is infeasible. LLVM uses Linear Scan Register Allocation (O(N log N)) instead — solving an interval graph (always optimal for 1D intervals). The distinction between special graph structures (interval, chordal, perfect) that permit polynomial-time coloring and general NP-complete coloring is fundamental to understanding when to apply which algorithm.

### ⚙️ How It Works (Mechanism)

**Greedy Coloring Algorithm:**

```
┌────────────────────────────────────────────────┐
│ Greedy Coloring: graph with 5 vertices         │
│                                                │
│ Edges: 1-2, 1-3, 2-4, 3-4, 4-5               │
│                                                │
│ Process vertex 1: no neighbors colored         │
│   → assign color 1                            │
│ Process vertex 2: neighbor 1 has color 1       │
│   → assign color 2                            │
│ Process vertex 3: neighbor 1 has color 1       │
│   → assign color 2 (2≠1 ✓)                   │
│ Process vertex 4: neighbors 2(col2), 3(col2)  │
│   colors 1,2 used → assign color 1            │
│   (but 4-1 not connected → valid!)            │
│ Process vertex 5: neighbor 4 has color 1       │
│   → assign color 2                            │
│                                                │
│ Result: 2 colors used                         │
└────────────────────────────────────────────────┘
```

**Backtracking exact k-coloring:**

```java
boolean colorGraph(int[][] graph, int[] colors,
                   int v, int k) {
    if (v == graph.length) return true; // all colored
    for (int c = 1; c <= k; c++) {
        if (isSafe(graph, colors, v, c)) {
            colors[v] = c;
            if (colorGraph(graph, colors, v+1, k))
                return true;
            colors[v] = 0; // backtrack
        }
    }
    return false;
}
boolean isSafe(int[][] graph, int[] colors,
               int v, int c) {
    for (int u = 0; u < graph.length; u++)
        if (graph[v][u] == 1 && colors[u] == c)
            return false;
    return true;
}
```

**Bipartite check (2-coloring via BFS):**
Graph is 2-colorable iff it is bipartite (no odd cycles). BFS from each unvisited vertex; alternately assign colors. If a neighbour has the same color: not bipartite → χ(G) ≥ 3.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Conflict problem (register overlap, exam conflict, etc.)
→ Model as graph: items=vertices, conflicts=edges
→ [GRAPH COLORING ← YOU ARE HERE]
  → Check special structure (interval? bipartite?)
  → Apply polynomial algorithm if applicable
  → Otherwise: greedy + DSATUR + backtracking
  → Result: valid coloring with color count k
→ Map colors to resources (registers, timeslots)
→ Validate: no conflicts in schedule/allocation
```

FAILURE PATH:
```
Graph is k-colorable but greedy uses k+2 colors
→ Scheduler assigns too many time slots (wasted resources)
→ Fix: use better vertex ordering (DSATUR);
  try random restarts with different orderings
→ Or: prove graph is chordal → perfect graph → exact
```

WHAT CHANGES AT SCALE:
For VLSI chip design with 10,000 nets needing frequency assignment, exact coloring is infeasible. Production tools use simulated annealing or tabu search to find near-optimal k-colorings. For distributed graph coloring (graph partitioned across 1,000 servers), distributed DSATUR-style algorithms require multi-round message passing — O(Δ) rounds for Δ-colorings, where each round broadcasts and receives neighbour colors.

### 💻 Code Example

**Example 1 — Greedy coloring:**
```java
int greedyColor(List<List<Integer>> adj, int V) {
    int[] color = new int[V];
    Arrays.fill(color, -1);
    color[0] = 0;
    boolean[] available = new boolean[V];
    for (int u = 1; u < V; u++) {
        // Mark colors used by neighbours
        for (int v : adj.get(u))
            if (color[v] != -1)
                available[color[v]] = true;
        // Find first available color
        int c;
        for (c = 0; c < V; c++)
            if (!available[c]) break;
        color[u] = c;
        // Reset for next vertex
        for (int v : adj.get(u))
            if (color[v] != -1)
                available[color[v]] = false;
    }
    return Arrays.stream(color).max().getAsInt() + 1;
}
```

**Example 2 — Bipartite check (2-coloring):**
```java
boolean isBipartite(int[][] graph) {
    int n = graph.length;
    int[] color = new int[n];
    Arrays.fill(color, -1);
    for (int start = 0; start < n; start++) {
        if (color[start] != -1) continue;
        Queue<Integer> q = new LinkedList<>();
        q.offer(start);
        color[start] = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : graph[u]) {
                if (color[v] == -1) {
                    color[v] = 1 - color[u]; // alternate
                    q.offer(v);
                } else if (color[v] == color[u]) {
                    return false; // same color → odd cycle
                }
            }
        }
    }
    return true;
}
```

**Example 3 — Register allocation model (simplified):**
```java
// Build interference graph: O(V²) for V variables
// variables[i] = {start, end} of live range
boolean[][] interferes(int[][] liveRanges) {
    int n = liveRanges.length;
    boolean[][] adj = new boolean[n][n];
    for (int i = 0; i < n; i++)
        for (int j = i+1; j < n; j++)
            if (liveRanges[i][0] < liveRanges[j][1] &&
                liveRanges[j][0] < liveRanges[i][1]) {
                adj[i][j] = adj[j][i] = true; // overlap
            }
    return adj;
}
// Then greedyColor(adj) = registers needed
```

### ⚖️ Comparison Table

| Algorithm | Time | Colors Used | Optimality | Best For |
|---|---|---|---|---|
| **Greedy (any order)** | O(V+E) | ≤ Δ+1 | Suboptimal | Large graphs, quick approximation |
| DSATUR | O(V²) | Often χ(G) | Near-optimal | Medium graphs in practice |
| Backtracking | O(k^V) pruned | χ(G) | Optimal | Small graphs (V ≤ 50) |
| BFS (bipartite) | O(V+E) | 2 | Optimal | Bipartite/2-colorable graphs |
| Interval Graph Greedy | O(V log V) | ω(G) | Optimal | Interval graphs (scheduler, compiler) |

How to choose: Use BFS 2-coloring to first check bipartiteness. Use greedy for large-scale approximations. Use DSATUR for better practical results. Use backtracking only for small exact problems.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Graph Coloring can always be solved in polynomial time | For k ≥ 3, k-coloring is NP-complete. Only special graph classes (bipartite, interval, perfect, planar) admit polynomial time exact algorithms. |
| The greedy algorithm always finds the chromatic number | Greedy depends heavily on vertex ordering. For the same graph, different orderings can produce k and k+3 colors. Greedy is a heuristic, not an exact algorithm. |
| 4 colors suffice for any graph | The Four Color Theorem applies only to planar graphs (maps). Non-planar graphs can require any number of colors. Complete graph Kₙ requires n colors. |
| Register allocation always uses the minimum registers | Chaitin's algorithm may spill variables to memory when the graph cannot be k-colored (k = available registers). Perfect coloring is not guaranteed — some spilling is accepted as a practical trade-off. |

### 🚨 Failure Modes & Diagnosis

**1. Greedy coloring uses too many colors due to poor vertex ordering**

Symptom: Compiler allocates more registers than physically available; unnecessary spilling to memory.

Root Cause: Random or sequential vertex ordering can cause greedy to produce a coloring far from optimal.

Diagnostic:
```bash
# LLVM has a register allocation dump flag:
clang -mllvm -debug-only=regalloc -O2 foo.c 2>&1 |
  grep "spilled"
```

Fix: Use DSATUR ordering (always color the most-constrained vertex next). For compilers, use reverse post-order of dominator tree.

Prevention: Test coloring quality with the chromatic upper bound: χ ≤ greedy uses ≤ Δ+1.

---

**2. Confusing graph coloring with edge coloring**

Symptom: Algorithm assigns colors to edges instead of vertices; conflict constraints not satisfied.

Root Cause: Edge coloring (no two edges sharing a vertex get the same color) is a different problem (models railway scheduling, not register allocation).

Diagnostic:
```java
// Vertex coloring invariant: for each edge (u,v)
for each edge (u, v):
    assert color[u] != color[v] : "vertex coloring violation";
```

Fix: Clarify the problem: vertex coloring vs edge coloring. They have different algorithms and chromatic numbers.

Prevention: Map the concrete problem (variables → vertices; live-range overlap → edges) explicitly before choosing algorithm.

---

**3. Treating NP-complete coloring as tractable for large instances**

Symptom: Backtracking solver runs for hours on a 200-vertex graph.

Root Cause: Exact k-coloring for k ≥ 3 has exponential worst-case time. For 200 vertices with k=10, the search space is 10^200.

Diagnostic:
```bash
# Monitor CPU time — if > 10 seconds for V=50, algorithm won't scale:
time java GraphColoring 200 10
```

Fix: Switch to approximation algorithms (DSATUR, tabu search) or exploit graph structure (is it chordal? interval?).

Prevention: Profile graph structure before choosing algorithm. Reserve exact coloring for V < 50.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — Graph Coloring operates on graph vertices and edges; understanding adjacency lists and basic graph properties is essential.
- `Backtracking` — The exact k-coloring algorithm is a direct application of backtracking with pruning.
- `NP-Complete Problems` — k-coloring (k ≥ 3) is one of Karp's 21 NP-complete problems; understanding the class explains why no fast exact algorithm exists.

**Builds On This (learn these next):**
- `Approximation Algorithms` — When exact coloring is infeasible, approximation algorithms (greedy, randomised) provide near-optimal solutions with performance guarantees.
- `Compiler Register Allocation` — The primary industrial application of graph coloring; Chaitin-Briggs algorithm models variables as vertices.
- `Scheduling Problems` — Exam scheduling, timetabling, and frequency assignment are all graph coloring applications.

**Alternatives / Comparisons:**
- `Greedy Algorithm` — O(V+E) but suboptimal; use as approximation baseline.
- `Randomized Algorithms` — Random restarts with greedy can find better colorings on average.
- `SAT Solver` — k-coloring encodes directly as a SAT formula; industrial SAT solvers (CaDiCaL) can handle hundreds of vertices exactly.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Assign labels to vertices: no two         │
│              │ adjacent vertices share a label           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Conflict avoidance: registers, exam slots,│
│ SOLVES       │ radio frequencies, map colours            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Minimum colors needed (χ) is the minimum  │
│              │ resources to avoid all conflicts           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Modelling conflict-avoidance: any two      │
│              │ conflicting items need different resources │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ General case with V > 50 and exact χ      │
│              │ needed — use greedy/DSATUR approximation  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Exact (optimal) exponential vs greedy      │
│              │ (O(V+E) but may use k+extra colors)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "No two neighbours can share a resource"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Register Allocation → DSATUR → SAT Solvers│
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A compiler's register allocator builds an interference graph G where each variable is a vertex and each overlapping live-range pair is an edge. The target CPU has k=8 registers. Greedy coloring gives 11 colors (3 variables must spill). DSATUR gives 9 colors (1 spill). Trace why DSATUR outperforms greedy for interference graphs specifically — what property of interference graphs (which are perfect graphs) guarantees DSATUR achieves χ(G)?

**Q2.** The Four Color Theorem states that every planar graph is 4-colorable. Yet proving this required computer-assisted case analysis of 1,936 reducible configurations. A simpler upper bound is 6-colorable (provable by hand using Euler's formula). Design an algorithm that 6-colors any planar graph in O(V+E): what is the key structural property of planar graphs (related to minimum degree) that makes a greedy 6-coloring always succeed, and why does the same argument fail for 5-coloring?

