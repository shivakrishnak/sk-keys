---
id: DSA-064
title: Minimum Spanning Tree (Kruskal and Prim)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018, DSA-028, DSA-059
used_by: DSA-077
related: DSA-059, DSA-060, DSA-063
tags:
  - algorithms
  - mst
  - kruskal
  - prim
  - spanning-tree
  - greedy
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/dsa/minimum-spanning-tree/
---

## TL;DR

MST algorithms find the minimum total-weight set of edges
that connects all nodes in a weighted undirected graph -
Kruskal uses Union-Find and edge sorting, Prim uses a min-heap
like Dijkstra.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-064 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, MST, Kruskal, Prim, greedy |
| **Prerequisites** | DSA-018, DSA-028, DSA-059 |

---

### The Problem This Solves

"Connect all offices with fiber cables at minimum total
cost." Given cities as nodes and cable costs as edges,
find the minimum-cost set of cables that keeps everything
connected (a spanning tree). MST solves this in
O(E log E) (Kruskal) or O((V+E) log V) (Prim).

---

### Textbook Definition

A Minimum Spanning Tree of a connected weighted undirected
graph is a subset of edges forming a tree that connects
all V nodes with minimum total edge weight. There are
V-1 edges. The tree is unique if all edge weights are
distinct. Two classic algorithms:
- Kruskal's: sort edges, greedily add smallest edge if
  it doesn't create a cycle (Union-Find)
- Prim's: grow tree from any start node, always adding
  the minimum-weight edge reaching an unvisited node

---

### How It Works

**Kruskal's Algorithm:**

```java
int kruskal(int n, int[][] edges) {
    // edges[i] = {u, v, weight}
    Arrays.sort(edges, Comparator.comparingInt(e -> e[2]));
    UnionFind uf = new UnionFind(n);

    int totalWeight = 0, edgesAdded = 0;
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        if (uf.union(u, v)) { // no cycle
            totalWeight += w;
            edgesAdded++;
            if (edgesAdded == n - 1) break; // MST complete
        }
    }
    return totalWeight; // returns MST weight
}
```

**Prim's Algorithm (Dijkstra-style):**

```java
int prim(int n, List<int[]>[] adj) {
    boolean[] inMST = new boolean[n];
    // [weight, node]
    PriorityQueue<int[]> pq = new PriorityQueue<>(
        Comparator.comparingInt(a -> a[0])
    );
    pq.offer(new int[]{0, 0}); // start from node 0
    int totalWeight = 0;

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int w = curr[0], u = curr[1];
        if (inMST[u]) continue;
        inMST[u] = true;
        totalWeight += w;

        for (int[] edge : adj[u]) {
            int v = edge[0], ew = edge[1];
            if (!inMST[v]) pq.offer(new int[]{ew, v});
        }
    }
    return totalWeight;
}
```

---

### Comparison Table

| Property | Kruskal | Prim |
|---------|---------|------|
| Time | O(E log E) | O((V+E) log V) |
| Space | O(V) for Union-Find | O(V+E) |
| Best for | Sparse graphs | Dense graphs |
| Implementation | Edge list + sort | Adjacency list + heap |
| Key data structure | Union-Find (DSU) | Min-heap |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "MST finds the shortest path between two nodes" | MST connects ALL nodes with minimum total weight; shortest paths are different (Dijkstra) |
| "MST is unique" | Unique only if all edge weights are distinct; with ties, multiple valid MSTs exist |

---

### Failure Modes & Diagnosis

**Failure: MST not found on disconnected graph**
- Cause: Graph has no spanning tree if disconnected
- Detection: If edgesAdded < n-1 after Kruskal, graph
  is disconnected; result has multiple components

---

### Quick Reference Card

| Property | Kruskal | Prim |
|---------|---------|------|
| Sort edges? | Yes | No |
| Data structure | Union-Find | Min-heap |
| Edge count preference | Sparse | Dense |
| Time | O(E log E) | O((V+E)logV) |

---

### The Surprising Truth

MST has a real-world application in cluster analysis:
remove the K-1 longest edges from an MST to get K
natural clusters (single-linkage hierarchical clustering).
This is the same principle used in phylogenetic trees in
biology (clustering species by genetic distance) and
network segmentation. The MST-based clustering is O(E log E)
vs naive O(n^2) for hierarchical clustering.

---

### Mastery Checklist

- [ ] Implements Kruskal's algorithm with Union-Find
- [ ] Implements Prim's algorithm with PriorityQueue
- [ ] Knows when to use Kruskal vs Prim (sparse/dense)

---

### Interview Deep-Dive

**Q1 (Medium):** You have n houses and can build roads
between them at given costs. Find the minimum total cost
to connect all houses.

> This is a classic Minimum Spanning Tree problem.
> Nodes = houses, edges = possible roads, weights = costs.
> Use Kruskal's: sort edges by cost, use Union-Find to
> greedily add cheapest edges that don't create cycles.
> Stop when n-1 edges are added.
> Time: O(E log E) for sorting + O(E alpha(V)) for DSU.
> If E is large (dense), Prim's with heap is preferred:
> O((V+E) log V).
> This exact problem appears in cloud network design where
> you minimize fiber cable cost to connect all data
> centers.
