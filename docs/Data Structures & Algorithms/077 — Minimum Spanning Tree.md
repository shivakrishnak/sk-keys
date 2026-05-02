---
layout: default
title: "Minimum Spanning Tree"
parent: "Data Structures & Algorithms"
nav_order: 77
permalink: /dsa/minimum-spanning-tree/
number: "0077"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Graph, Greedy Algorithm, Union-Find (Disjoint Set), Priority Queue
used_by: Network Design, Cluster Analysis, Approximation Algorithms
related: Kruskal / Prim, Shortest Path, Strongly Connected Components
tags:
  - algorithm
  - advanced
  - deep-dive
  - datastructure
  - pattern
---

# 077 — Minimum Spanning Tree

⚡ TL;DR — A Minimum Spanning Tree connects all vertices of a weighted graph with the lowest total edge weight and no cycles — the cheapest way to wire a network.

| #0077 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Graph, Greedy Algorithm, Union-Find (Disjoint Set), Priority Queue | |
| **Used by:** | Network Design, Cluster Analysis, Approximation Algorithms | |
| **Related:** | Kruskal / Prim, Shortest Path, Strongly Connected Components | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are laying fibre optic cable to connect 20 cities. Each pair of cities has a cable cost. To make all cities reachable from each other, you must connect them all. Connecting every pair (complete graph) uses 190 cable segments — massively over-engineered. But you need all cities connected. What is the cheapest set of cables to install?

**THE BREAKING POINT:**
You need connectivity (all cities reachable from each other) but not redundancy. Any connected graph on V vertices requires at least V-1 edges. The challenge: which V-1 edges minimise total cost while keeping all V vertices connected? With 20 cities to choose V-1=19 cables from 190 possible cables, the brute force is C(190,19) ≈ 10^28 combinations — impossible.

**THE INVENTION MOMENT:**
The greedy insight: always add the cheapest edge that does NOT create a cycle. After V-1 additions, the result is connected (by induction: each addition connects a new vertex to the growing tree). This is Kruskal's algorithm. Prim's grows a single tree by always adding the cheapest edge reachable from the current tree. Both find the unique MST in O(E log E). This is exactly why **Minimum Spanning Tree** algorithms were created.

---

### 📘 Textbook Definition

A **Spanning Tree** of a connected weighted undirected graph G=(V,E) is a connected acyclic subgraph that includes all V vertices. A **Minimum Spanning Tree (MST)** is a spanning tree whose total edge weight is minimised. For a graph with unique edge weights, the MST is unique; with ties, there may be multiple MSTs of equal total weight. **Kruskal's algorithm** sorts edges by weight and adds each if it doesn't form a cycle (Union-Find for cycle detection): O(E log E). **Prim's algorithm** grows a tree from one vertex, always adding the minimum-weight edge connecting the tree to a non-tree vertex: O(E log V) with a binary heap, O(E + V log V) with a Fibonacci heap.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Connect all vertices at the lowest total cost — add the cheapest safe edge until everything is joined.

**One analogy:**
> Building the cheapest road network to connect 10 villages. You have a list of all possible roads with their construction costs. Build roads cheapest-first, skipping any road that would create a loop (loops are wasteful — two roads between the same villages when connectivity is already achieved). Stop when all villages are connected: 9 roads chosen from many options.

**One insight:**
The MST property: for any cut (partition of vertices into two non-empty groups), the minimum-weight edge crossing the cut is always in some MST. This **cut property** is the fundamental theorem behind both Kruskal's and Prim's correctness. It means greedy works: always picking the minimum safe edge can never make the wrong choice.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A spanning tree on V vertices has exactly V-1 edges and is connected.
2. Adding any edge to a spanning tree creates exactly one cycle.
3. The **cut property**: the minimum-weight edge crossing any cut of the graph is in every MST (assuming unique weights).

**DERIVED DESIGN:**
The cut property directly justifies greedy algorithms:
- **Kruskal's:** Sort edges by weight. For each edge (u,v), check if u and v are in different components (use Union-Find). If yes, adding (u,v) is the minimum edge crossing the cut between u's component and v's component → it must be in the MST. Add it.
- **Prim's:** Maintain a priority queue of edges connecting the current tree to non-tree vertices. Always extract the minimum-weight edge to a new vertex → this is the minimum edge crossing the cut between the current tree and the rest.

Both algorithms are greedy and provably correct via the cut property. Their correctness is not heuristic — it is exact.

**THE TRADE-OFFS:**
**Gain:** Optimal connectivity with minimum total edge weight; provably correct; O(E log E) or O(E log V) time.
**Cost:** Undirected graphs only (directed graphs need "minimum spanning arborescence" — much harder). Does not minimise path length between pairs (that's shortest path). Handles negative weights correctly (unlike shortest-path algorithms that require Dijkstra's non-negative constraint).

---

### 🧪 Thought Experiment

**SETUP:**
Graph with 4 vertices and edges: A-B(cost 4), A-C(cost 2), B-C(cost 1), B-D(cost 3), C-D(cost 5). Find MST.

**WHAT HAPPENS WITHOUT MST ALGORITHM:**
All spanning trees of 4 vertices have exactly 3 edges. Enumerate all 8 possible spanning trees, compute total cost, take minimum. At 20 vertices, enumeration is Cayley's formula: 20^18 ≈ 10^23 trees — impossible.

**WHAT HAPPENS WITH KRUSKAL'S:**
Sort edges: B-C(1), A-C(2), B-D(3), A-B(4), C-D(5).
1. B-C(1): B and C in different components → ADD. Tree: {B-C}. Cost: 1.
2. A-C(2): A and C in different components → ADD. Tree: {B-C, A-C}. Cost: 3.
3. B-D(3): B and D in different components → ADD. Tree: {B-C, A-C, B-D}. Cost: 6.
4. A-B(4): A and B SAME component → SKIP (would create cycle).
5. Done: 3 edges = V-1. MST cost: 6. ✓

**THE INSIGHT:**
The cycle check ensures no redundant edges. Each U-F union merges components; the MST is complete when 1 component remains. Kruskal's never "undoes" a choice — the cut property guarantees each greedy selection is permanently correct.

---

### 🧠 Mental Model / Analogy

> Prim's algorithm is like growing a coral reef. Start with one piece of coral. Each time step, add the nearest unattached sea creature (cheapest edge to a new vertex) to the existing reef. The reef grows outward, always picking the nearest addition. After V-1 additions the entire area is covered.

- "Current reef" → set of tree vertices
- "Nearest sea creature" → minimum-weight edge to non-tree vertex
- "Joining the reef" → adding vertex to MST
- "Reef covers entire area" → all vertices in MST

- "Kruskal's" → different analogy: "cheapest powerline first, skip if it causes a ring"

Where this analogy breaks down: Prim's always grows a contiguous tree; Kruskal's processes all edges globally and can add edges between disjoint components. The reef analogy captures Prim's geographic growth but not Kruskal's global edge sorting.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Minimum Spanning Tree is the cheapest way to connect all points in a network with no redundant connections. Imagine connecting cities with roads — use only the roads you need and no others, choosing the cheapest ones until everything is reachable.

**Level 2 — How to use it (junior developer):**
Implement Kruskal's: sort all edges by weight; use Union-Find to detect cycles; add N-1 edges. Time: O(E log E). Implement Prim's: start from any vertex, use a min-heap of (weight, vertex) pairs; always extract minimum and add if not yet in tree. Time: O(E log V). Use Kruskal's for sparse graphs (E ≈ V), Prim's for dense graphs (E ≈ V²) since Prim's with Fibonacci heap runs in O(E + V log V).

**Level 3 — How it works (mid-level engineer):**
Union-Find with path compression and union by rank gives near-O(1) amortized operations (inverse Ackermann function O(α(V))). Kruskal's total: O(E log E) dominated by sorting. Prim's with binary heap: O(E log V) for decrease-key operations. Prim's with Fibonacci heap: O(E + V log V) — theoretically optimal but Fibonacci heap has large constants in practice. For Euclidean MST (points in 2D), Delaunay triangulation first reduces E to O(V), then Kruskal's runs in O(V log V) total.

**Level 4 — Why it was designed this way (senior/staff):**
MST appears naturally in approximation algorithms: the 2-MST approximation for TSP (Hamiltonian cycle ≤ 2× MST weight for metric spaces, via Euler tour interpretation). Borůvka's algorithm — the oldest MST algorithm (1926) — is optimal for parallel computation: each component simultaneously selects its cheapest outgoing edge, halving components each round in O(log V) rounds. GHD oracle (Gómory-Hu tree) precomputes all-pairs minimum cuts in O(V) MST calls. In clustering, removing the k-1 heaviest edges from a MST instantly partitions the graph into k clusters — Euclidean MST clustering.

---

### ⚙️ How It Works (Mechanism)

**Kruskal's Algorithm:**

```
┌────────────────────────────────────────────────┐
│ Kruskal's MST (sorted edges, Union-Find)        │
│                                                │
│ Edges sorted: (B-C,1),(A-C,2),(B-D,3),        │
│               (A-B,4),(C-D,5)                  │
│                                                │
│ Components init: {A},{B},{C},{D}               │
│                                                │
│ (B-C,1): find(B)≠find(C) → union(B,C) ADD     │
│   Components: {A},{B,C},{D}. MST edges: 1      │
│                                                │
│ (A-C,2): find(A)≠find(C) → union(A,C) ADD     │
│   Components: {A,B,C},{D}. MST edges: 2        │
│                                                │
│ (B-D,3): find(B)≠find(D) → union(B,D) ADD     │
│   Components: {A,B,C,D}. MST edges: 3 = V-1   │
│   → DONE. Total cost: 1+2+3 = 6               │
└────────────────────────────────────────────────┘
```

**Prim's Algorithm:**

```
┌────────────────────────────────────────────────┐
│ Prim's MST (min-heap, start at A)              │
│                                                │
│ Start: inTree={A}. Heap: [(2,C),(4,B)]         │
│                                                │
│ Extract (2,C): C not in tree → ADD A-C(2)      │
│   inTree={A,C}. Heap+: [(1,B via C),(5,D)]     │
│                                                │
│ Extract (1,B via C): B not in tree → ADD C-B(1)│
│   inTree={A,C,B}. Heap+: [(3,D via B)]         │
│   (A-B edge cost 4 > 3 → ignored)              │
│                                                │
│ Extract (3,D via B): D not in tree → ADD B-D(3)│
│   inTree={A,C,B,D}. All vertices → DONE       │
│   Total: 2+1+3 = 6 ✓                          │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Weighted undirected connected graph G=(V,E,w)
→ Choose algorithm: Kruskal (sparse) / Prim (dense)
→ [MINIMUM SPANNING TREE ← YOU ARE HERE]
  Kruskal: sort E by w, Union-Find cycle detection → O(E log E)
  Prim: min-heap from start vertex → O(E log V)
  → Result: V-1 edges forming MST
→ Total cost: sum of V-1 edge weights
→ Apply to: network design, clustering, TSP approx
```

**FAILURE PATH:**
```
Graph is disconnected
→ Algorithm finds MST of each connected component (spanning forest)
→ No single spanning tree exists for all V vertices
→ Diagnostic: after MST, check: number of components > 1?
   result.edges.size() < V-1 → disconnected graph
→ Fix: add minimum-weight edges between components
  (minimum spanning forest then merge)
```

**WHAT CHANGES AT SCALE:**
For a network graph with 10 billion edges (social network), sorting all edges is infeasible. Borůvka's algorithm is preferred for parallelism: each vertex independently selects its cheapest edge, then contracted nodes repeat — O(E log V) total but naturally parallelisable. Apache Spark implementations use Borůvka's in O(log V) supersteps for distributed MST computation.

---

### 💻 Code Example

**Example 1 — Kruskal's with Union-Find:**
```java
int[] parent, rank;
int find(int x) {
    if (parent[x] != x)
        parent[x] = find(parent[x]); // path compression
    return parent[x];
}
boolean union(int x, int y) {
    int px = find(x), py = find(y);
    if (px == py) return false; // same component
    if (rank[px] < rank[py]) { int t=px; px=py; py=t; }
    parent[py] = px;
    if (rank[px] == rank[py]) rank[px]++;
    return true;
}

int kruskalMST(int V, int[][] edges) {
    // edges[i] = {weight, u, v}
    Arrays.sort(edges, (a,b) -> a[0] - b[0]);
    parent = new int[V]; rank = new int[V];
    for (int i = 0; i < V; i++) parent[i] = i;
    int totalCost = 0, edgeCount = 0;
    for (int[] e : edges) {
        if (union(e[1], e[2])) {
            totalCost += e[0];
            if (++edgeCount == V-1) break; // MST complete
        }
    }
    return totalCost;
}
```

**Example 2 — Prim's with priority queue:**
```java
int primMST(int V, List<int[]>[] adj) {
    // adj[u] = list of {v, weight}
    boolean[] inTree = new boolean[V];
    PriorityQueue<int[]> pq =
        new PriorityQueue<>((a,b)->a[0]-b[0]);
    pq.offer(new int[]{0, 0}); // {weight, vertex}
    int totalCost = 0;
    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int w = curr[0], u = curr[1];
        if (inTree[u]) continue; // already in MST
        inTree[u] = true;
        totalCost += w;
        for (int[] next : adj[u])
            if (!inTree[next[0]])
                pq.offer(new int[]{next[1], next[0]});
    }
    return totalCost;
}
```

**Example 3 — MST-based clustering:**
```java
// Remove k-1 heaviest edges from MST → k clusters
List<int[]> mstEdges = kruskalEdges(V, edges);
// Already sorted ascending; remove last k-1 edges
// for k clusters, keep only V-k MST edges
mstEdges.subList(V-k, V-1).clear();
// Union-Find gives cluster membership
```

---

### ⚖️ Comparison Table

| Algorithm | Time | Best For | Data Structure |
|---|---|---|---|
| **Kruskal's** | O(E log E) | Sparse graphs (E ≈ V) | Union-Find + sort |
| **Prim's (binary heap)** | O(E log V) | General graphs | Min-heap |
| **Prim's (Fibonacci heap)** | O(E + V log V) | Dense graphs (E ≈ V²) | Fibonacci heap |
| Borůvka's | O(E log V) | Parallel / distributed | Component merging |
| Dijkstra (shortest path) | O(E log V) | Shortest paths (not MST) | Min-heap |

How to choose: For sparse graphs use Kruskal's (simple to implement, O(E log E)). For dense graphs use Prim's (O(E log V) = O(V² log V) < O(V² log V²) = O(V² log V) – tied but Prim's wins with Fibonacci heap). For parallel systems use Borůvka's.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MST gives shortest paths between all pairs | MST minimises total edge weight for connectivity. Shortest paths between pairs require Dijkstra/Floyd-Warshall. MST path between A and B can be longer than direct shortest path. |
| MST requires non-negative edge weights | Unlike Dijkstra, both Kruskal's and Prim's work correctly with negative edge weights. The greedy correctness proof via cut property holds regardless. |
| There is only one MST | For graphs with unique edge weights there is exactly one MST. With ties (equal edge weights), multiple MSTs of equal total weight may exist. |
| Directed graphs have MSTs | Undirected only. Directed graphs need "minimum spanning arborescence" (Edmonds' Chu-Liu algorithm) — O(EV) and considerably harder. |

---

### 🚨 Failure Modes & Diagnosis

**1. Cycle detection missing — wrong "spanning" graph**

**Symptom:** Algorithm adds V or more edges; result has cycles and is not a tree.

**Root Cause:** Union-Find not used (or broken); both endpoints hash to the same component but union is not called correctly.

**Diagnostic:**
```java
// After MST: verify no cycles
assert mstEdges.size() == V - 1 :
    "MST should have V-1 edges, got " + mstEdges.size();
// DFS/BFS on MST: visits V vertices from any start?
```

**Fix:** Use Union-Find with both `find` (path-compressed) and `union` (rank-merged) correctly.

**Prevention:** Unit test Union-Find separately; test with a complete 4-vertex graph where cycles are obvious.

---

**2. Graph is disconnected — partial MST**

**Symptom:** MST has fewer than V-1 edges; not all vertices are connected.

**Root Cause:** Input graph is not fully connected; some vertices have no path to others.

**Diagnostic:**
```java
int components = 0;
for (int i = 0; i < V; i++)
    if (find(i) == i) components++;
System.out.println("Components: " + components);
// components > 1 → disconnected
```

**Fix:** Handle disconnected graphs explicitly: find spanning forest (one tree per component); report which components are isolated.

**Prevention:** Pre-validate graph connectivity with BFS/DFS before MST; document precondition "connected graph required."

---

**3. Confusing MST with shortest path tree**

**Symptom:** After running Prim's "MST" from a source vertex, using it to route packets — some routes are suboptimal.

**Root Cause:** MST minimises total edge weight; shortest path tree from a source minimises individual path lengths. These are different objectives and produce different trees.

**Diagnostic:**
```java
// Compare Prim MST total vs Dijkstra path costs:
// MST may give path A→B of cost 10,
// while direct edge A-B exists at cost 3
```

**Fix:** Use Dijkstra's algorithm for shortest paths. Use MST only for network connectivity minimisation.

**Prevention:** Clearly separate the two use cases in design documents: "MST = cheapest network; Dijkstra = fastest routes."

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — MST is a property of weighted undirected graphs; understanding adjacency representation and traversal is fundamental.
- `Greedy Algorithm` — Both Kruskal's and Prim's are greedy algorithms; the cut property theorem justifies their correctness.
- `Union-Find (Disjoint Set)` — Kruskal's cycle detection relies on Union-Find with path compression and union by rank.
- `Priority Queue` — Prim's algorithm uses a min-priority queue for efficient minimum-edge extraction.

**Builds On This (learn these next):**
- `Kruskal / Prim` — The two canonical MST algorithms; worth studying their implementation differences in depth.
- `Approximation Algorithms` — MST is the foundation of the 2-approximation for metric TSP via Euler tour construction.

**Alternatives / Comparisons:**
- `Shortest Path (Dijkstra)` — Solves a different problem: minimum distance from source to all vertices; not the same as MST.
- `Strongly Connected Components` — For directed graphs: finds groups where all vertices reach each other. Not related to spanning trees directly.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ V-1 edges connecting all V vertices with  │
│              │ minimum total weight and no cycles         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Connect N nodes at minimum total cable/    │
│ SOLVES       │ road/network cost without redundancy       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cut property: minimum edge crossing any   │
│              │ cut is always in some MST → greedy correct │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Minimise total connection cost; spanning   │
│              │ connectivity; Euclidean clustering         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need shortest individual paths (Dijkstra); │
│              │ directed graphs (Edmonds' algorithm)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Optimal total weight vs not minimising     │
│              │ pairwise distances; O(E log E) time        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cheapest wiring; no loops needed"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Kruskal/Prim → Borůvka → TSP Approx       │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The cut property proves greedy MST algorithms are correct: the minimum-weight edge crossing any cut is in some MST. Now consider a graph where the minimum cut edge has weight w and an equal-weight edge also crosses the cut. Is the MST still unique? Prove whether modifying Kruskal's to break ties by vertex index produces a canonical MST, and whether two different tie-breaking rules can produce two different spanning trees, both of which are valid MSTs.

**Q2.** The Metro network of a large city has 500 stations (vertices) with 1,200 possible connecting tunnels (edges) at various construction costs. You want the MST to plan which tunnels to build. However, due to geology, 50 specific tunnel pairs cannot both be built (mutual exclusion constraints). How does this constraint transform the MST problem? Is the modified problem still polynomial-time solvable, and what algorithmic paradigm would you apply?

