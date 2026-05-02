---
layout: default
title: "Kruskal / Prim"
parent: "Data Structures & Algorithms"
nav_order: 63
permalink: /dsa/kruskal-prim/
number: "0063"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Graph, Union-Find (Disjoint Set), Priority Queue, Greedy Algorithm
used_by: Network Design, Cluster Analysis, Approximate TSP
related: Dijkstra, Minimum Spanning Tree, Union-Find (Disjoint Set)
tags:
  - algorithm
  - graph
  - advanced
  - deep-dive
  - pattern
---

# 063 — Kruskal / Prim

⚡ TL;DR — Kruskal and Prim are two greedy algorithms that find the Minimum Spanning Tree of a weighted graph — the cheapest set of edges that connects all nodes.

| #063 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Graph, Union-Find (Disjoint Set), Priority Queue, Greedy Algorithm | |
| **Used by:** | Network Design, Cluster Analysis, Approximate TSP | |
| **Related:** | Dijkstra, Minimum Spanning Tree, Union-Find (Disjoint Set) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A telecommunications company needs to lay cable to connect 100 cities. Any pair of cities can be connected, but the cost varies by distance and terrain. They need all cities connected using the minimum total cable length — wasting cable on redundant connections (cycles) costs money. Trying all possible spanning trees is 100^98 possibilities (Cayley's formula). Exhaustive search is impossible.

**THE BREAKING POINT:**
Finding the minimum-cost set of edges that connects all N nodes without cycles — a Minimum Spanning Tree — seems to require evaluating exponentially many candidate edge sets. No polynomial brute-force approach exists.

**THE INVENTION MOMENT:**
Two independent greedy strategies both produce the optimal MST:

**Kruskal (1956):** Sort all edges by weight. Add each edge if it doesn't create a cycle. Greedy justification: the cheapest edge that doesn't create a cycle must be in some MST — if not, swapping it with the more expensive edge in that MST gives a cheaper spanning tree.

**Prim (1957):** Start from any node. Repeatedly add the cheapest edge that connects the current tree to a new node. Greedy justification: the cheapest cross-edge (between tree and non-tree) must be in some MST — the "cut property" of matroids.

Both algorithms exploit that MSTs are matroid-structured: any greedy approach respecting the "no cycles" constraint always finds the optimal solution. This is exactly why **Kruskal and Prim** were created.

---

### 📘 Textbook Definition

A **Minimum Spanning Tree (MST)** of a connected weighted undirected graph is a spanning tree with minimum total edge weight. A spanning tree connects all V vertices with exactly V-1 edges and no cycles. **Kruskal's algorithm** sorts edges by weight and uses Union-Find to greedily add edges that don't create cycles. **Prim's algorithm** greedily extends a growing tree by always choosing the minimum-weight cross-edge. Both run in O(E log E) = O(E log V) time. The MST is unique if all edge weights are distinct.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Connect all points as cheaply as possible by always picking the cheapest safe edge.

**One analogy:**
> Imagine building roads to connect all villages. Kruskal surveys all possible roads, sorts by cost, and builds the cheapest ones that don't create redundant loops. Prim starts from one village and always extends to the nearest unconnected village. Both strategies build the same minimum-cost road network.

**One insight:**
The correctness of both algorithms rests on a single graph theory property: for any partition of graph vertices into two sets, the minimum-weight edge crossing the cut is in every MST. This "cut property" is the greedy invariant — it guarantees that every locally cheapest safe choice is globally consistent with the optimal solution.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An MST has exactly **V-1 edges** (connects V nodes without cycles).
2. **Cut Property:** For any cut (S, V\S) of the vertex set, the minimum-weight edge crossing the cut belongs to some MST.
3. **Cycle Property:** For any cycle, the maximum-weight edge in the cycle does NOT belong to any MST (there is always a cheaper way to connect those nodes).

**DERIVED DESIGN:**
**Kruskal** exploits the cycle property: when edges are sorted by weight, each edge in order is either the minimum-weight edge crossing some cut (include it) or it closes a cycle (skip it). Union-Find efficiently determines whether adding an edge creates a cycle — if both endpoints are in the same component, the edge would form a cycle.

**Prim** exploits the cut property directly: at every step, (tree, V\tree) is a cut, and adding the minimum cross-edge is justified by the cut property. A min-heap priority queue tracks the minimum cross-edge for each unvisited node.

**Why both algorithms are correct:**
Both maintain the invariant that selected edges are a subset of some MST at every step. The greedy invariant is preserved because:
- Kruskal: each non-cycle edge is the minimum in some cut (by the cycle-skip argument)
- Prim: each added edge is the minimum cross-edge for the current tree-cut

**THE TRADE-OFFS:**

| | Kruskal | Prim |
|---|---|---|
| Time (sparse graph) | O(E log E) | O((V+E) log V) |
| Time (dense graph) | O(E log E) | O(E log V) |
| When best | Sparse graphs (E ≈ V) | Dense graphs (E ≈ V²) |
| Data structure | Union-Find | Min-heap priority queue |

---

### 🧪 Thought Experiment

**SETUP:**
Graph with 4 nodes (A,B,C,D) and edges: A-B(1), B-C(4), C-D(2), A-D(3), A-C(5).

KRUSKAL:
Sort edges: A-B(1), C-D(2), A-D(3), B-C(4), A-C(5).
Add A-B(1): no cycle. MST={A-B}.
Add C-D(2): no cycle (C,D separate from A,B). MST={A-B, C-D}.
Add A-D(3): connects {A,B} and {C,D}. No cycle. MST={A-B, C-D, A-D}. V-1=3 edges. Done.
Total cost: 1+2+3=6.

PRIM (start at A):
A is in tree. Min cross-edges: A-B(1), A-D(3), A-C(5).
Add A-B(1). Tree={A,B}. Cross-edges: A-D(3), A-C(5), B-C(4).
Add A-D(3). Tree={A,B,D}. Cross-edges: D-C(2), A-C(5), B-C(4).
Add D-C(2). Tree={A,B,D,C}. All nodes in tree. Done.
MST edges: A-B(1), A-D(3), D-C(2). Total: 1+3+2=6. Same MST.

**THE INSIGHT:**
Both algorithms produce the same MST (cost 6: A-B, A-D, C-D). They make different traversal choices but both are guided by the same underlying cut/cycle property. For this graph, A-D(3) was cheaper to connect {C,D} to the tree than B-C(4) — both algorithms discovered this independently through their different strategies.

---

### 🧠 Mental Model / Analogy

> MST algorithms are like building the cheapest water supply network to serve all houses in a city. Kruskal is the accountant approach: list all possible pipes, sort by cost, and lay the cheapest ones that connect new areas. Prim is the surveyor approach: start from the water tower and always extend to the nearest unserved house. Both strategies lay the same minimum-cost network — they just think about it differently.

- "Cheapest pipe not creating redundancy" → minimum-weight non-cycle edge (Kruskal)
- "Extend to nearest unserved house" → minimum cross-edge (Prim)
- "All houses served, no redundant pipes" → V-1 edges, spanning tree
- "Total pipe cost" → MST weight

Where this analogy breaks down: Real pipe networks may require multiple water towers (multiple sources). MST assumes a single connected graph — for disconnected graphs, both algorithms produce a Minimum Spanning Forest.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
MST algorithms connect all points with the minimum total connection cost. Kruskal builds it edge-by-edge cheapest-first; Prim grows it outward from one point, always extending to the nearest unconnected point. Both find the same cheapest-possible fully-connected structure.

**Level 2 — How to use it (junior developer):**
Kruskal: sort edges by weight, iterate, use Union-Find to skip cycle-forming edges, add the rest. Stop when V-1 edges are added. Prim: use a priority queue of (weight, node) pairs; start from any node; repeatedly pop minimum (weight, node), skip if already in tree, add node to tree, push all its edges to the queue. Stop when all nodes are in tree.

**Level 3 — How it works (mid-level engineer):**
Kruskal complexity: O(E log E) for sort + O(E α(V)) for V union-find operations ≈ O(E log E). Prim complexity: O((V+E) log V) with binary heap — V extract-min operations + E decrease-key operations. For dense graphs (E ≈ V²), Prim with a Fibonacci heap runs in O(E + V log V). In practice, binary heap Prim is preferred for graphs up to V=100,000. Kruskal is preferred for sparse graphs or when edges are already sorted. For parallel MST, Borůvka's algorithm (each component picks its cheapest outgoing edge simultaneously) runs in O(log V) rounds — used in parallel MST algorithms.

**Level 4 — Why it was designed this way (senior/staff):**
Both algorithms are special cases of a general matroid greedy algorithm: given a graphic matroid (where independent sets are forests in the graph), the greedy algorithm always finds the minimum-weight basis (spanning tree). The correctness proof reduces to showing that graphic matroids satisfy the exchange property — any smaller-weight basis can replace edges in a larger-weight basis. Kruskal is the "edge-centric" view of this greedy; Prim is the "vertex-frontier" view. In practice, MST is the core subroutine in: (1) approximation algorithms for TSP (MST weight is a 2-approximation of TSP), (2) network design problems (optical fibre routing, VLSI routing), (3) clustering (cut the k-1 most expensive edges of MST to get k clusters).

---

### ⚙️ How It Works (Mechanism)

**Kruskal's Algorithm:**
```
┌────────────────────────────────────────────┐
│ Kruskal's MST                              │
│                                            │
│  1. Sort all edges by weight               │
│  2. Initialize Union-Find for V nodes      │
│  3. For each edge (u, v, w) in order:      │
│     if find(u) != find(v):                 │
│       add edge to MST                      │
│       union(u, v)                          │
│       if MST has V-1 edges: stop           │
│  4. Return MST edges                       │
└────────────────────────────────────────────┘
```

**Prim's Algorithm:**
```
┌────────────────────────────────────────────┐
│ Prim's MST (starting from node 0)          │
│                                            │
│  dist[0] = 0, dist[v] = ∞ for all v≠0     │
│  pq = MinHeap {(0, 0)}                     │
│  inTree = {}                               │
│                                            │
│  LOOP while pq not empty:                  │
│    (w, u) = pq.poll()                      │
│    if u in inTree: continue                │
│    inTree.add(u); MST weight += w          │
│                                            │
│    for each edge (u→v, weight ew):         │
│      if v not in inTree and ew < dist[v]:  │
│        dist[v] = ew                        │
│        parent[v] = u                       │
│        pq.offer((ew, v))                   │
└────────────────────────────────────────────┘
```

Note: Prim's `dist[v]` is the minimum edge weight to connect v to the current tree, not total distance from source (unlike Dijkstra).

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (Kruskal):
```
Weighted undirected graph G
→ Sort E edges by weight O(E log E)
→ Initialize Union-Find O(V)
→ [KRUSKAL ← YOU ARE HERE]
  → Iterate sorted edges
  → Check cycle via Union-Find
  → Add non-cycle edge to MST
  → Stop at V-1 edges
→ MST: V-1 edges, minimum total weight
→ Use for: cable layout, cluster analysis
```

**FAILURE PATH:**
```
Graph is disconnected
→ Kruskal terminates with fewer than V-1 edges
→ Produces Minimum Spanning Forest (one tree
  per connected component)
→ Prim: some nodes never added to tree
→ Caller must detect and handle disconnected case
```

**WHAT CHANGES AT SCALE:**
For VLSI chip routing (V=10⁷ nodes), Kruskal's sort of 10⁸ edges takes ~3 seconds. Borůvka's algorithm (O(E log V)) with parallel component processing suits distributed computing. For dynamic MST (edges added/removed), dynamic tree structures maintain MST in O(log²N) per update — essential for live network topology changes.

---

### 💻 Code Example

**Example 1 — Kruskal's algorithm:**
```java
int kruskalMST(int n, int[][] edges) {
    // edges[i] = [u, v, weight]
    Arrays.sort(edges,
        Comparator.comparingInt(e -> e[2]));

    UnionFind uf = new UnionFind(n);
    int totalWeight = 0;
    int edgesAdded = 0;
    List<int[]> mstEdges = new ArrayList<>();

    for (int[] edge : edges) {
        int u=edge[0], v=edge[1], w=edge[2];
        if (uf.union(u, v)) { // no cycle
            totalWeight += w;
            mstEdges.add(edge);
            edgesAdded++;
            if (edgesAdded == n-1) break;
        }
    }
    // If edgesAdded < n-1: graph disconnected
    return totalWeight;
}
```

**Example 2 — Prim's algorithm:**
```java
int primMST(int n,
    List<int[]>[] graph) {
    // graph[u] = list of [v, weight]
    boolean[] inMST = new boolean[n];
    int[] key = new int[n]; // min edge weight
    Arrays.fill(key, Integer.MAX_VALUE);
    key[0] = 0;

    // PQ: [weight, node]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(
            Comparator.comparingInt(a -> a[0]));
    pq.offer(new int[]{0, 0});

    int totalWeight = 0;

    while (!pq.isEmpty()) {
        int[] cur = pq.poll();
        int w = cur[0], u = cur[1];
        if (inMST[u]) continue; // lazy del
        inMST[u] = true;
        totalWeight += w;

        for (int[] edge : graph[u]) {
            int v = edge[0], ew = edge[1];
            if (!inMST[v] && ew < key[v]) {
                key[v] = ew;
                pq.offer(new int[]{ew, v});
            }
        }
    }
    return totalWeight;
}
```

**Example 3 — MST for cluster analysis (cut k-1 heaviest edges):**
```java
// Find k clusters by cutting k-1 most
// expensive MST edges
List<List<Integer>> cluster(int n,
    int[][] edges, int k) {
    // Step 1: build MST (Kruskal)
    Arrays.sort(edges,
        Comparator.comparingInt(e -> e[2]));
    UnionFind uf = new UnionFind(n);
    List<int[]> mst = new ArrayList<>();
    for (int[] e : edges) {
        if (uf.union(e[0], e[1]))
            mst.add(e);
        if (mst.size() == n-1) break;
    }

    // Step 2: remove k-1 heaviest MST edges
    mst.sort((a,b) -> b[2]-a[2]); // desc weight
    UnionFind uf2 = new UnionFind(n);
    // Add only first (n-k) edges (skip k-1 heavy)
    for (int i = k-1; i < mst.size(); i++)
        uf2.union(mst.get(i)[0], mst.get(i)[1]);

    // Group nodes by component
    Map<Integer,List<Integer>> clusters =
        new HashMap<>();
    for (int i = 0; i < n; i++) {
        clusters.computeIfAbsent(
            uf2.find(i), x -> new ArrayList<>()
        ).add(i);
    }
    return new ArrayList<>(clusters.values());
}
```

---

### ⚖️ Comparison Table

| Algorithm | Approach | Time (sparse) | Time (dense) | Best For |
|---|---|---|---|---|
| **Kruskal** | Edge-centric, sort + UF | O(E log E) | O(E log E) | Sparse graphs, pre-sorted edges |
| **Prim (binary heap)** | Vertex-centric, grow tree | O((V+E) log V) | O(E log V) | Dense graphs |
| Prim (Fibonacci heap) | Vertex-centric, grow tree | O(V log V + E) | O(V log V + E) | Very dense, theoretical optimum |
| Borůvka | Parallel, component edges | O(E log V) | O(E log V) | Parallel/distributed MST |

How to choose: Use Kruskal for sparse graphs or when edges arrive sorted. Use Prim for dense graphs. Use Borůvka for distributed/parallel settings.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MST and shortest path tree are the same | An MST minimises total edge weight; a shortest path tree minimises individual path weights from a source. They can be completely different trees for the same graph |
| Kruskal always produces the same MST as Prim | Both produce MSTs with the same total weight. The actual edge sets may differ if multiple edges have the same weight (tie-breaking determines which MST is found) |
| MST is unique | MST is unique if all edge weights are distinct. If multiple edges have the same weight, multiple MSTs may exist with identical total weight |
| Prim's algorithm is similar to Dijkstra | Prim and Dijkstra use similar priority queue expansion, but Prim tracks "cheapest edge to connect to tree" (edge weight only), while Dijkstra tracks "cheapest total path from source" (cumulative sum). Using Dijkstra's distance tracking in Prim produces wrong results |
| MST works on directed graphs | Standard Kruskal and Prim work only on undirected graphs. For directed MST (minimum spanning arborescence), Edmonds' (Chu-Liu/Edmonds') algorithm is required |

---

### 🚨 Failure Modes & Diagnosis

**1. Prim using cumulative distance (Dijkstra-style) instead of edge weight**

**Symptom:** Prim returns a spanning tree that is not minimal; its total weight differs from Kruskal's result.

**Root Cause:** Using `dist[v] = dist[u] + edge_weight` (Dijkstra-style) instead of `dist[v] = edge_weight` (Prim-style). Prim selects by edge weight, not cumulative path weight.

**Diagnostic:**
```java
// Verify: Kruskal and Prim must agree on
// total MST weight for the same graph:
int kruskalWeight = kruskalMST(n, edges);
int primWeight = primMST(n, adjList);
assert kruskalWeight == primWeight
    : "Mismatch: K=" + kruskalWeight
    + " P=" + primWeight;
```

**Fix:** In Prim, update `key[v] = edge_weight` (NOT `key[u] + edge_weight`). This is the single most common Prim implementation bug.

**Prevention:** Clearly distinguish: Dijkstra = minimise total path distance from source. Prim = minimise weight of connection edge to MST.

---

**2. Kruskal applied to directed graph**

**Symptom:** Kruskal produces a tree that is not a valid spanning arborescence (root to all nodes directed).

**Root Cause:** Kruskal treats each edge as undirected (merges both endpoints). On directed graphs, this is semantically wrong — reachability in directed graphs is asymmetric.

**Diagnostic:**
```bash
# Check: can source reach all other nodes
# in the produced tree?
# If some nodes unreachable: Kruskal applied
# to directed graph incorrectly
```

**Fix:** For directed MST, use Edmonds' algorithm (Chu-Liu/Edmonds'). For undirected subgraph of directed graph, explicitly add both directions.

**Prevention:** Document whether graph is directed/undirected at algorithm entry point.

---

**3. Disconnected graph — MST not spanning all nodes**

**Symptom:** MST contains fewer than V-1 edges; some nodes are not connected.

**Root Cause:** The graph is disconnected — no spanning tree exists. Kruskal processes all edges but adds fewer than V-1 (can't bridge disconnected components).

**Diagnostic:**
```java
int edgesAdded = 0;
for (int[] edge : sortedEdges) {
    if (uf.union(edge[0], edge[1]))
        edgesAdded++;
}
if (edgesAdded < n-1) {
    int components = uf.getComponents();
    System.out.println("Graph has "
        + components + " components");
    // Report Minimum Spanning Forest
}
```

**Fix:** Return a Minimum Spanning Forest (one tree per component). Report disconnected components to caller.

**Prevention:** Check graph connectivity before claiming MST; assert `edgesAdded == V-1` after Kruskal completes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — MST algorithms operate on connected weighted undirected graphs; understand the graph representation.
- `Union-Find (Disjoint Set)` — Kruskal uses Union-Find for cycle detection; essential for efficient Kruskal implementation.
- `Priority Queue` — Prim's algorithm uses a min-heap; understand heap operations and ordering.
- `Greedy Algorithm` — both Kruskal and Prim are greedy algorithms; understand the greedy choice property.

**Builds On This (learn these next):**
- `Minimum Spanning Tree` — MST properties and the cut/cycle properties that justify both algorithms.
- `Approximate TSP` — MST gives a 2-approximation for the Travelling Salesman Problem.
- `VLSI Physical Design` — MST used in wire routing and floorplanning algorithms.

**Alternatives / Comparisons:**
- `Dijkstra` — finds shortest paths from a source; structurally similar to Prim but minimises cumulative distance, not edge weight.
- `Borůvka's Algorithm` — parallel MST algorithm; each component picks cheapest outgoing edge simultaneously; O(log V) rounds.
- `Edmonds' Algorithm` — directed MST (minimum cost arborescence); the directed counterpart to Kruskal/Prim.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two greedy algorithms finding the minimum │
│              │ cost spanning tree of a weighted graph    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Connect all nodes with minimum total edge │
│ SOLVES       │ weight (network design, clustering)       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cut property: cheapest cross-edge is in   │
│              │ MST. Cycle property: most expensive cycle │
│              │ edge is NOT in MST. Both are greedy-safe  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Kruskal: sparse graphs, edges pre-sorted  │
│              │ Prim: dense graphs, adjacency list        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Directed graphs (use Edmonds');            │
│              │ disconnected graphs (get Spanning Forest) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(E log E) / O((V+E) log V); undirected   │
│              │ only; unique MST only if weights distinct  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cheapest connection that doesn't loop    │
│              │  back" (Kruskal) or "nearest new node"    │
│              │  (Prim)                                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Minimum Spanning Tree → Approximate TSP → │
│              │ Borůvka's Algorithm                       │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Prim's algorithm is structurally almost identical to Dijkstra's algorithm — both use a min-heap priority queue and process nodes one by one. The only difference is in what value is stored in the priority queue: Dijkstra stores `g(u) + edge_weight` (cumulative distance), while Prim stores `edge_weight` only. Consider a graph where nodes are placed on a number line at positions 1, 2, 4, 8 (total 4 nodes), with edges between consecutive nodes weighted by their distance. Starting from position 1, show that Dijkstra and Prim produce different spanning trees. What does this reveal about the fundamental difference between MST and shortest-path trees?

**Q2.** Borůvka's algorithm finds the MST by having each component simultaneously select its minimum outgoing edge, contracting components, and repeating for O(log V) rounds. Unlike Kruskal and Prim, it is naturally parallel. Design a parallel Borůvka implementation using a work-sharing thread pool. What synchronisation primitives are needed when multiple threads try to merge the same pair of components simultaneously? What is the theoretical speedup with P processors compared to sequential Kruskal, and where does Amdahl's Law limit the parallelism?

