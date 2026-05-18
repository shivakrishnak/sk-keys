---
id: DSA-073
title: Graph Representation Trade-off Guide
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018, DSA-039
used_by: DSA-077
related: DSA-039, DSA-018, DSA-044
tags:
  - data-structures
  - graph-representation
  - adjacency-list
  - adjacency-matrix
  - decision-framework
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/dsa/graph-representation-tradeoff/
---

## TL;DR

Choose adjacency list for sparse graphs (most real-world
graphs) and adjacency matrix for dense graphs or when
O(1) edge existence check is critical - the choice
dramatically impacts memory and algorithm performance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-073 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, graph-representation, trade-off |
| **Prerequisites** | DSA-018, DSA-039 |

---

### The Problem This Solves

A social network with 1 billion users and 100 billion
friendships: adjacency matrix = 10^18 bits = 125 petabytes.
Adjacency list = 100 billion entries × 8 bytes = 800GB -
still large but feasible. Real systems choose representation
based on density, operation patterns, and memory budget.

---

### Textbook Definition

Two primary graph representations:
- Adjacency Matrix: V×V boolean/weight matrix where
  matrix[u][v] = 1 if edge u→v exists
- Adjacency List: array of V lists where adj[u] contains
  all neighbors of u
- Edge List: flat list of all (u, v, weight) triples

The choice determines memory usage (O(V^2) vs O(V+E))
and operation time (O(1) vs O(degree) for edge check).

---

### The Decision Framework

```
Graph density = E / V^2 (0=empty, 1=complete)

Density < 0.1 → SPARSE → Adjacency List
Density > 0.9 → DENSE  → Adjacency Matrix

Real-world examples:
  Social networks: E ≈ 100*V (avg 100 friends) → SPARSE
  Dense graph:     E ≈ V^2 (fully connected)   → MATRIX
  Road networks:   E ≈ 4*V  (4-way intersections) → SPARSE
  Airline routes:  E ≈ 0.01*V^2               → depends
```

**Operation comparison:**

```
             Adjacency List    Adjacency Matrix
Memory:      O(V + E)          O(V^2)
Add edge:    O(1)              O(1)
Remove edge: O(degree)         O(1)
Edge check:  O(degree)         O(1)
Neighbors:   O(degree)         O(V)
DFS/BFS:     O(V + E)          O(V^2)
```

**Java implementations:**

{% raw %}
```java
// Adjacency List (prefer for sparse graphs)
List<List<Integer>> adj = new ArrayList<>();
for (int i = 0; i < V; i++) adj.add(new ArrayList<>());
adj.get(u).add(v); // add edge u→v

// Adjacency Matrix (prefer for dense graphs or edge check)
int[][] matrix = new int[V][V];
matrix[u][v] = 1;  // add edge u→v

boolean hasEdge(int u, int v) {
    return matrix[u][v] == 1; // O(1)
}

// Edge List (prefer for Kruskal's MST - needs sorted edges)
int[][] edges = {{u1, v1, w1}, {u2, v2, w2}, ...};
Arrays.sort(edges, (a, b) -> a[2] - b[2]); // sort by weight
```
{% endraw %}

---

### Comparison Table

| Representation | Memory | Edge check | Neighbors | Best for |
|---------------|--------|-----------|-----------|---------|
| Adjacency List | O(V+E) | O(degree) | O(degree) | Sparse graphs, BFS/DFS |
| Adjacency Matrix | O(V^2) | O(1) | O(V) | Dense, Floyd-Warshall |
| Edge List | O(E) | O(E) | O(E) | Kruskal's MST, edge iterations |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Adjacency matrix is always faster for edge checks" | True for O(1) per check, but if graph is sparse, the O(V^2) memory causes cache thrashing that can make it slower than adjacency list with O(degree) check |
| "Adjacency list is always better" | Floyd-Warshall operates on V^2 matrix natively; using adjacency list forces matrix construction first |

---

### Failure Modes & Diagnosis

**Failure: OOM with adjacency matrix for sparse graph**
- Cause: V=100,000 nodes with E=200,000 edges;
  matrix = 100,000^2 * 4 bytes = 40GB
- Fix: Use adjacency list (O(V+E) = O(300,000) entries)

---

### Quick Reference Card

| Decision factor | Choose |
|----------------|--------|
| E << V^2 (sparse) | Adjacency List |
| E ≈ V^2 (dense) | Adjacency Matrix |
| Need O(1) edge check | Adjacency Matrix |
| Need fast BFS/DFS | Adjacency List |
| Kruskal's algorithm | Edge List |
| Floyd-Warshall | Adjacency Matrix |

---

### The Surprising Truth

Facebook's social graph (~1 billion nodes, ~100 billion
edges) uses custom sparse graph storage called "Unicorn" -
an adjacency-list structure with per-shard compression.
The same data as an adjacency matrix would require 125
petabytes per iteration - more than all of Facebook's
storage combined. Graph density determines whether social
network analysis is feasible at all.

---

### Mastery Checklist

- [ ] Can select the right representation given V, E, and
      required operations
- [ ] Knows Floyd-Warshall requires adjacency matrix
- [ ] Can calculate memory for both representations given
      V and E

---

### Interview Deep-Dive

**Q1 (Medium):** You're building a friend-recommendation
system for a social network with 500M users and average
200 friends each. Which graph representation?

> E = 500M * 200 / 2 = 50 billion edges (undirected).
> Adjacency matrix: (500M)^2 bits = 3 * 10^16 bytes =
> 30 petabytes. Not feasible.
> Adjacency list: 50B edges * 8 bytes = 400GB.
> Large but partitioned across machines (Facebook uses
> sharding across 1000+ servers = 400MB per shard).
> Friend-of-friend recommendations require 2-hop BFS
> from a user: O(degree + degree^2) = O(200 + 40,000)
> per query - feasible with adjacency list.
> Recommendation: adjacency list with sharding by user ID.
