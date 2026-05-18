---
id: DSA-039
title: Adjacency List vs Adjacency Matrix
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-018
used_by: DSA-035, DSA-036, DSA-063, DSA-064
related: DSA-018, DSA-035, DSA-036
tags:
  - data-structures
  - graph
  - adjacency-list
  - adjacency-matrix
  - representation
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/dsa/adjacency-list-vs-matrix/
---

## TL;DR

Adjacency list stores each vertex's neighbors - O(V+E)
space, ideal for sparse graphs. Adjacency matrix stores
all V×V pairs - O(V²) space, ideal for dense graphs and
O(1) edge lookup.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-039 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, graph, representation |
| **Prerequisites** | DSA-018 |

---

### The Problem This Solves

A graph has V vertices and E edges. You need to store and
query it efficiently. Two key representations have
opposite trade-offs: one is memory-efficient for sparse
graphs; the other is time-efficient for edge existence queries.

---

### Textbook Definition

**Adjacency list:** Each vertex stores a list of its
neighbors. Space: O(V + E). Edge check: O(degree of vertex).
Traversal: O(V + E). Best for sparse graphs (E << V²).

**Adjacency matrix:** V×V boolean (or weight) matrix.
`matrix[i][j] = true` if edge i→j exists. Space: O(V²).
Edge check: O(1). Traversal: O(V²). Best for dense graphs
(E ≈ V²) or when edge existence must be O(1).

---

### How It Works

**Building both representations:**

```java
int V = 5; // vertices 0..4

// Adjacency List
List<List<Integer>> adjList = new ArrayList<>();
for (int i = 0; i < V; i++) adjList.add(new ArrayList<>());
// Add edge 0→1 and 0→2
adjList.get(0).add(1);
adjList.get(0).add(2);
adjList.get(1).add(3);

// Adjacency Matrix
int[][] adjMatrix = new int[V][V];
// Add edge 0→1 and 0→2
adjMatrix[0][1] = 1;
adjMatrix[0][2] = 1;
adjMatrix[1][3] = 1;

// Check edge 0→2:
// List:   adjList.get(0).contains(2)  → O(degree) = slow
// Matrix: adjMatrix[0][2] == 1        → O(1) = fast

// Iterate all neighbors of vertex 0:
// List:   for (int n : adjList.get(0)) → O(degree) = fast
// Matrix: for (int j = 0; j < V; j++) if (adjMatrix[0][j]...)
//         → O(V) = slow (checks all V vertices)
```

**Weighted graph:**

```java
// Adjacency List for weighted graph
// List of (neighbor, weight) pairs
List<List<int[]>> weightedList = new ArrayList<>();
for (int i = 0; i < V; i++) weightedList.add(new ArrayList<>());
weightedList.get(0).add(new int[]{1, 5}); // 0→1, weight 5
weightedList.get(0).add(new int[]{2, 3}); // 0→2, weight 3

// Adjacency Matrix for weighted graph
int[][] weightMatrix = new int[V][V]; // 0 = no edge
weightMatrix[0][1] = 5;
weightMatrix[0][2] = 3;
```

---

### Comparison Table

| Property | Adjacency List | Adjacency Matrix |
|---------|----------------|-----------------|
| Space | O(V + E) | O(V²) |
| Edge check | O(degree) | O(1) |
| All neighbors | O(degree) | O(V) |
| Add edge | O(1) | O(1) |
| Remove edge | O(degree) | O(1) |
| Dense graph (E≈V²) | Larger overhead | Same as list |
| Sparse graph (E<<V²) | Much less space | Wastes space |
| DFS/BFS traversal | O(V + E) | O(V²) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Matrix is always faster" | Matrix is O(1) for edge check but O(V) per vertex for neighbor iteration; list wins for traversal on sparse graphs |
| "Adjacency list can't handle weighted edges" | Use List<List<int[]>> or List<List<Pair<Integer,Integer>>> for weights |

---

### Quick Reference Card

| Use Adjacency List when | Use Adjacency Matrix when |
|------------------------|--------------------------|
| Sparse graph (social, roads) | Dense graph (complete graph) |
| DFS/BFS traversal | Frequent edge-exists queries |
| Memory is limited | V is small (V² fits in memory) |
| E << V² | E ≈ V² |

---

### Mastery Checklist

- [ ] Can build both representations from an edge list
- [ ] Can explain the O(V+E) vs O(V²) space trade-off
- [ ] Chooses the right representation based on graph density

---

### Interview Deep-Dive

**Q1 (Easy):** You're implementing Dijkstra's shortest path
algorithm on a road map with 10,000 cities and 50,000 roads.
Which representation?

> Adjacency list. 10,000 cities (V=10K), 50,000 roads
> (E=50K). E << V² (50K vs 100M). Adjacency matrix would
> use 10K×10K = 100M entries (400MB for int). Adjacency list
> uses O(V+E) = ~60K entries (a few hundred KB). DFS/BFS
> traversal in Dijkstra is O(V+E) with adjacency list vs
> O(V²) with matrix. For sparse real-world graphs (roads,
> social networks), adjacency list is almost always correct.
