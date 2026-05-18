---
id: DSA-052
title: Graph Cycle Detection
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-018, DSA-035, DSA-036
used_by: DSA-064, DSA-065
related: DSA-035, DSA-036, DSA-064, DSA-065
tags:
  - algorithms
  - graph
  - cycle-detection
  - directed
  - undirected
  - dfs
  - union-find
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/dsa/graph-cycle-detection/
---

## TL;DR

Directed graph cycles: DFS 3-color (white/gray/black).
Undirected graph cycles: DFS parent tracking or Union-Find.
Both O(V+E). Detecting cycles validates DAG properties
(dependency graphs, build systems).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-052 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, graph, cycle-detection, DFS |
| **Prerequisites** | DSA-018, DSA-035, DSA-036 |

---

### The Problem This Solves

Maven dependency resolution fails if dependencies are
circular (A depends on B depends on A). Spring fails on
circular bean injection. Course prerequisites must be a
DAG. Detecting cycles prevents infinite loops and ensures
topological ordering is possible.

---

### How It Works

**Directed graph - DFS 3-color:**

```java
enum Color { WHITE, GRAY, BLACK }
// WHITE = unvisited, GRAY = in current path, BLACK = done

boolean hasCycleDirected(
        Map<Integer, List<Integer>> graph,
        int node,
        Map<Integer, Color> color) {

    color.put(node, Color.GRAY);  // mark as being processed

    for (int neighbor : graph.getOrDefault(node, List.of())) {
        Color c = color.getOrDefault(neighbor, Color.WHITE);
        if (c == Color.GRAY) return true;  // back edge = cycle
        if (c == Color.WHITE && hasCycleDirected(
                graph, neighbor, color)) return true;
    }
    color.put(node, Color.BLACK);  // fully processed
    return false;
}

// Check all nodes (disconnected components)
boolean hasAnyCycle(Map<Integer, List<Integer>> graph, int V) {
    Map<Integer, Color> color = new HashMap<>();
    for (int i = 0; i < V; i++) {
        if (color.getOrDefault(i, Color.WHITE) == Color.WHITE) {
            if (hasCycleDirected(graph, i, color)) return true;
        }
    }
    return false;
}
```

**Undirected graph - DFS parent tracking:**

```java
boolean hasCycleUndirected(
        Map<Integer, List<Integer>> graph,
        int node, int parent,
        Set<Integer> visited) {

    visited.add(node);
    for (int neighbor : graph.getOrDefault(node, List.of())) {
        if (!visited.contains(neighbor)) {
            if (hasCycleUndirected(graph, neighbor, node, visited))
                return true;
        } else if (neighbor != parent) {
            return true;  // found cycle (not back to parent)
        }
    }
    return false;
}
```

**Union-Find for undirected cycles (cleaner):**

```java
// If adding edge (u,v) and they're already in the same
// component → adding this edge creates a cycle
int[] parent = new int[V];
Arrays.fill(parent, -1);

int find(int x) {
    if (parent[x] < 0) return x;
    return parent[x] = find(parent[x]);  // path compression
}

boolean detectCycleUF(int[][] edges) {
    for (int[] edge : edges) {
        int root1 = find(edge[0]);
        int root2 = find(edge[1]);
        if (root1 == root2) return true;  // cycle!
        parent[root1] = root2;            // union
    }
    return false;
}
```

---

### Comparison Table

| Approach | Graph Type | Detects | Time | Space |
|---------|-----------|---------|------|-------|
| DFS 3-color | Directed | Back edges | O(V+E) | O(V) |
| DFS parent | Undirected | Non-parent revisit | O(V+E) | O(V) |
| Union-Find | Undirected | Same component | O(E α(V)) | O(V) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "DFS for undirected graphs detects cycles the same as directed" | Undirected: must skip the edge back to parent (not a cycle). Directed: GRAY = cycle; parent edge is fine to revisit |
| "Cycle detection only matters for algorithms" | Spring's circular bean dependency check, Maven's circular dependency detection, and Git's DAG validation all use cycle detection |

---

### Quick Reference Card

| Graph type | Use | Cycle indicator |
|-----------|-----|----------------|
| Directed | DFS 3-color | Reach GRAY node |
| Undirected | DFS + parent | Reach visited non-parent |
| Undirected | Union-Find | Same root before union |

---

### Mastery Checklist

- [ ] Can implement DFS cycle detection for directed graphs
      using 3-color marking
- [ ] Knows why undirected cycle detection differs
      (skip parent edge)
- [ ] Can implement Union-Find cycle detection for
      undirected graphs

---

### Interview Deep-Dive

**Q1 (Medium):** You're building a course scheduler.
Each course has prerequisites. How do you check if
the prerequisites form a valid DAG (no cycles)?

> Model as a directed graph: edge from prereq to course.
> Apply DFS cycle detection with 3-color marking.
> Start DFS from each unvisited node. If any DFS path
> reaches a GRAY node (currently in the recursion stack),
> we have a circular dependency - the schedule is
> impossible. If DFS completes for all nodes without
> finding a back edge, no cycle exists and a valid
> course order exists (topological sort order).
> This is exactly LeetCode #207 "Course Schedule" -
> a very common interview question.
