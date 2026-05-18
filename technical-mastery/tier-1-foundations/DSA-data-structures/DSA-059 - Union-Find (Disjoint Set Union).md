---
id: DSA-059
title: Union-Find (Disjoint Set Union)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018
used_by: DSA-064
related: DSA-018, DSA-052, DSA-064
tags:
  - data-structures
  - union-find
  - dsu
  - disjoint-set
  - connectivity
  - nearly-o-1
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/dsa/union-find/
---

## TL;DR

Union-Find tracks which elements belong to the same group
with near-O(1) union and find operations via path
compression and union by rank - essential for graph
connectivity and Kruskal's MST.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-059 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, union-find, DSU, connectivity |
| **Prerequisites** | DSA-018 |

---

### The Problem This Solves

"Are nodes A and B connected in this network?" For dynamic
networks where connections are added over time, re-running
BFS/DFS for each query is O(V+E). Union-Find answers
connectivity queries in amortized O(alpha(n)) where alpha
is the inverse Ackermann function - effectively O(1) for
any practical n.

---

### Textbook Definition

Union-Find (Disjoint Set Union, DSU) maintains a collection
of disjoint sets. Operations:
- `find(x)`: returns the representative (root) of the set
  containing x
- `union(x, y)`: merges the sets containing x and y

With path compression and union by rank, amortized time
per operation is O(alpha(n)) ≈ O(1) for all practical n
(alpha(n) ≤ 4 for n < 10^600).

---

### How It Works

**Implementation with path compression + union by rank:**

```java
class UnionFind {
    private int[] parent;
    private int[] rank;

    UnionFind(int n) {
        parent = new int[n];
        rank   = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i; // each is own root
    }

    // Find with path compression: O(alpha(n)) amortized
    int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]); // path compression
        }
        return parent[x];
    }

    // Union by rank: O(alpha(n))
    boolean union(int x, int y) {
        int rootX = find(x), rootY = find(y);
        if (rootX == rootY) return false; // already same set

        // Attach smaller rank under larger rank
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        return true; // merged
    }

    boolean connected(int x, int y) {
        return find(x) == find(y);
    }
}

// Kruskal's MST using Union-Find:
// Sort edges by weight. Add edge (u,v) if !connected(u,v)
// This efficiently avoids cycles in O(E log E + E*alpha(V))
```

**Path compression visualization:**

```
Before find(4) on chain 1<-2<-3<-4:

  1 <- 2 <- 3 <- 4
  
After find(4) with path compression:

  1 <- 2        (all directly point to root 1)
  1 <- 3
  1 <- 4
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Path compression changes which set elements belong to" | It only flattens the parent pointers for efficiency; the logical set membership is unchanged |
| "Union-Find supports split/disconnect" | Standard DSU only supports merges; disconnecting sets requires more complex structures (link-cut trees) |

---

### Failure Modes & Diagnosis

**Failure: Union-Find detects false cycles**
- Cause: Off-by-one in node indexing; node IDs not in [0, n)
- Fix: Verify all node IDs are mapped to 0-indexed range
  before creating the DSU; add bounds checking

---

### Quick Reference Card

| Operation | Time |
|-----------|------|
| find | O(alpha(n)) ≈ O(1) |
| union | O(alpha(n)) ≈ O(1) |
| connected | O(alpha(n)) ≈ O(1) |
| Space | O(n) |

**alpha(n) = inverse Ackermann; ≤ 4 for any real-world n.**

---

### The Surprising Truth

Kruskal's MST algorithm owes its O(E log E) efficiency
entirely to Union-Find. Without it, cycle detection during
edge-greedy MST building would be O(V) per edge (BFS/DFS),
making the total O(E*V). For a dense graph with E=V^2,
that's O(V^3). Union-Find reduces cycle detection to
O(alpha(V)) - effectively free - making Kruskal practical
for million-node graphs.

---

### Mastery Checklist

- [ ] Implements Union-Find with path compression and
      union by rank from memory
- [ ] Can use Union-Find to detect cycles during Kruskal's
- [ ] Understands why alpha(n) is effectively O(1)

---

### Interview Deep-Dive

**Q1 (Medium):** Given n cities and a list of roads,
find the number of disconnected provinces.

> Create Union-Find of size n. For each road (u,v),
> call union(u,v). Count distinct roots: iterate all
> nodes, call find(i), count unique results.
> Time: O(n * alpha(n)) = practically O(n).
> Space: O(n).
> Alternative: BFS/DFS per unvisited node = O(V+E).
> Union-Find is cleaner and faster for this class of
> connectivity problems.
