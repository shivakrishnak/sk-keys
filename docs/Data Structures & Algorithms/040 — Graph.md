---
layout: default
title: "Graph"
parent: "Data Structures & Algorithms"
nav_order: 40
permalink: /dsa/graph/
number: "040"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, LinkedList, HashMap, Queue / Deque, Stack
used_by: BFS, DFS, Dijkstra's Algorithm, Topological Sort, Minimum Spanning Tree, Cycle Detection
tags:
  - datastructure
  - algorithm
  - intermediate
  - graph
---

# 040 — Graph

`#datastructure` `#algorithm` `#intermediate` `#graph`

⚡ TL;DR — A data structure of vertices (nodes) and edges (connections) used to model relationships and networks; the foundation for BFS, DFS, shortest path, and topological sort algorithms.

| #040 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList, HashMap, Queue / Deque, Stack | |
| **Used by:** | BFS, DFS, Dijkstra's Algorithm, Topological Sort, Minimum Spanning Tree, Cycle Detection | |

---

### 📘 Textbook Definition

A **graph** G = (V, E) is a data structure consisting of a set of *vertices* (nodes) V and a set of *edges* E representing pairwise relationships between vertices. Graphs can be: **directed** (edges have direction: u→v ≠ v→u) or **undirected** (edges bidirectional); **weighted** (edges have numeric weights) or **unweighted**; **cyclic** (contains a cycle) or **acyclic** (DAG — Directed Acyclic Graph). Primary representations: **adjacency list** (array/list of neighbours per vertex — O(V+E) space, efficient for sparse graphs) and **adjacency matrix** (V×V boolean/weight matrix — O(V²) space, efficient for dense graphs and O(1) edge existence check).

### 🟢 Simple Definition (Easy)

A graph is a collection of dots (vertices) connected by lines (edges). It models any network: social connections, road maps, websites linking to each other, or task dependencies.

### 🔵 Simple Definition (Elaborated)

Graphs are the most general data structure for modelling relationships. A social network is a graph: users are vertices, friendships are edges. A road map is a weighted graph: cities are vertices, roads are edges with distances. A software build system is a directed acyclic graph: packages are vertices, dependencies are directed edges. Almost every interesting graph algorithm — finding shortest paths, detecting cycles, finding connected components, scheduling tasks — works on this abstract structure, and the algorithms don't care about the domain, only the graph structure.

### 🔩 First Principles Explanation

**Graph variants:**

```
Undirected:    A --- B --- C   (edges: {A,B}, {B,C})
Directed:      A →  B →  C    (edges: (A,B), (B,C))
Weighted:      A -5→ B -3→ C  (edge weights: 5, 3)
DAG:           A → B → C; A → C (no cycle)
Tree:          connected DAG with exactly V-1 edges
```

**Adjacency List representation (preferred for sparse graphs):**

```java
// Map each vertex to its list of neighbours
Map<Integer, List<Integer>> graph = new HashMap<>();
graph.put(1, Arrays.asList(2, 3));  // 1 connects to 2, 3
graph.put(2, Arrays.asList(4));      // 2 connects to 4
graph.put(3, Arrays.asList(4));      // 3 connects to 4
graph.put(4, Collections.emptyList());

// Space: O(V + E)
// Edge check: O(degree) — scan neighbour list
```

**Adjacency Matrix representation (preferred for dense graphs):**

```java
int V = 5;
boolean[][] adj = new boolean[V][V];
adj[0][1] = true; // edge 0→1
adj[1][2] = true;
// Space: O(V²)
// Edge check: O(1) — adj[u][v]
// Finding all neighbours: O(V) — scan row u
```

**Weighted adjacency list:**

```java
Map<Integer, List<int[]>> graph = new HashMap<>();
// int[] = {neighbour, weight}
graph.get(0).add(new int[]{1, 5}); // 0→1 with weight 5
graph.get(0).add(new int[]{2, 3}); // 0→2 with weight 3
```

**Choosing representation:**

```
Sparse (E << V²): Adjacency List  — less memory, faster iteration
Dense (E ≈ V²):   Adjacency Matrix — faster edge check
Both:             Time to iterate all edges: O(E) list vs O(V²) matrix
                  Time to check edge (u,v): O(degree(u)) list vs O(1) matrix
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Graphs:

- Social connections: store as pairs in a list — finding if Alice connects to Charlie requires O(n) scan.
- Road routing: no efficient structure to represent network topology.
- Dependency resolution (build systems, package managers): must detect cycles and order tasks.

What breaks without it:
1. BFS and DFS have no structure to traverse — we need the adjacency list to know "which nodes are adjacent to this one."
2. Dijkstra's algorithm requires knowing all edges from a vertex with their weights.

WITH Graph:
→ Uniform representation for any relational data structure.
→ All graph algorithms (BFS, DFS, Dijkstra, Kruskal, Floyd-Warshall) operate on this abstraction independently of domain.

### 🧠 Mental Model / Analogy

> A graph is like a city map. Cities are vertices; roads are edges; road lengths are edge weights. Directed graphs are one-way streets. BFS finds the fewest road-changes from A to B. Dijkstra finds the shortest-distance route. Topological sort orders stops so you never visit a city before all cities you must visit before it. DFS explores as far as possible down one road before backtracking.

"Cities" = vertices, "roads" = edges, "one-way streets" = directed edges, "road length" = edge weight.

Every graph algorithm has an intuitive road-network interpretation.

### ⚙️ How It Works (Mechanism)

**Graph traversal – BFS vs DFS:**

```
Graph:  1→2, 1→3, 2→4, 3→4, 4→5
        (Starting from 1)

BFS (Queue — FIFO, level by level):
  Level 0: [1]
  Level 1: [2, 3]
  Level 2: [4]
  Level 3: [5]
  → Visits: 1, 2, 3, 4, 5
  → Shortest path in unweighted graph

DFS (Stack — LIFO, depth first):
  → Visits: 1, 2, 4, 5, 3 (or 1, 3, 4, 5, 2 depending on order)
  → Useful for cycle detection, topological sort, connected components
```

**Topological sort (DAG only):**

```
Dependencies: A→C, B→C, C→D, C→E
Order: A, B must come before C; C must come before D, E
Valid topological sort: A, B, C, D, E (or A, B, C, E, D)

Algorithm (Kahn's — BFS-based):
  in-degree[v] = number of edges pointing into v
  Start with all nodes of in-degree 0 → queue
  Process: dequeue, output, reduce in-degree of neighbours
  If any unprocessed: cycle detected
```

**Cycle detection:**

```
Undirected graph: BFS/DFS — if we reach an already-visited node
Directed graph:   DFS with 3 colours:
  WHITE = unvisited, GRAY = in current path, BLACK = done
  If DFS reaches a GRAY node → cycle
```

### 🔄 How It Connects (Mini-Map)

```
Graph ← you are here (data structure: V + E)
        ↓ traversed by
BFS (shortest path in unweighted)
DFS (cycle detection, topological sort, SCC)
        ↓ weighted shortest path
Dijkstra (non-negative weights)
Bellman-Ford (negative weights)
Floyd-Warshall (all-pairs shortest paths)
        ↓ spanning tree
Prim's / Kruskal's MST
        ↓ ordering
Topological Sort (DAG — task scheduling)
```

### 💻 Code Example

Example 1 — BFS shortest path (unweighted):

```java
public int shortestPath(Map<Integer,List<Integer>> graph,
                        int src, int dest) {
    Queue<Integer> q = new ArrayDeque<>();
    Map<Integer, Integer> dist = new HashMap<>();
    q.offer(src);
    dist.put(src, 0);

    while (!q.isEmpty()) {
        int node = q.poll();
        if (node == dest) return dist.get(node);
        for (int neighbour : graph.getOrDefault(node,
                                     List.of())) {
            if (!dist.containsKey(neighbour)) {
                dist.put(neighbour, dist.get(node) + 1);
                q.offer(neighbour);
            }
        }
    }
    return -1; // unreachable
}
```

Example 2 — Cycle detection in directed graph (DFS):

```java
public boolean hasCycle(Map<Integer,List<Integer>> graph,
                        int V) {
    Set<Integer> grey = new HashSet<>(); // in current path
    Set<Integer> black = new HashSet<>(); // fully explored

    for (int v = 0; v < V; v++) {
        if (!black.contains(v))
            if (dfs(graph, v, grey, black)) return true;
    }
    return false;
}

boolean dfs(Map<Integer,List<Integer>> g, int v,
            Set<Integer> grey, Set<Integer> black) {
    grey.add(v);
    for (int nb : g.getOrDefault(v, List.of())) {
        if (grey.contains(nb)) return true; // back edge = cycle!
        if (!black.contains(nb))
            if (dfs(g, nb, grey, black)) return true;
    }
    grey.remove(v); black.add(v);
    return false;
}
```

Example 3 — Topological sort (Kahn's algorithm):

```java
public List<Integer> topologicalSort(
        Map<Integer,List<Integer>> graph, int V) {
    int[] inDegree = new int[V];
    for (List<Integer> edges : graph.values())
        for (int v : edges) inDegree[v]++;

    Queue<Integer> q = new ArrayDeque<>();
    for (int i = 0; i < V; i++)
        if (inDegree[i] == 0) q.offer(i);

    List<Integer> result = new ArrayList<>();
    while (!q.isEmpty()) {
        int node = q.poll();
        result.add(node);
        for (int nb : graph.getOrDefault(node, List.of())) {
            if (--inDegree[nb] == 0) q.offer(nb);
        }
    }
    // If result.size() < V: graph has a cycle
    return result.size() == V ? result : Collections.emptyList();
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All graphs are trees | Trees are a special case of graphs (connected, acyclic, V-1 edges). General graphs can be cyclic, disconnected, or dense. |
| BFS always finds the shortest path | BFS finds the shortest path in terms of edge count (unweighted). For weighted graphs, use Dijkstra's algorithm instead. |
| DFS and BFS always visit all nodes | Only if the graph is fully connected or you start DFS/BFS from every unvisited node. Disconnected graphs require running BFS/DFS from each connected component. |
| Adjacency list uses more memory than matrix | For sparse graphs (real-world networks, roads, social graphs), adjacency list uses far less memory than V² matrix. Matrix is only beneficial for dense graphs. |
| Directed and undirected graphs use the same algorithms | Many algorithms work differently or need modification: BFS works the same; DFS cycle detection differs (undirected: any back edge = cycle; directed: only back edges to grey nodes = cycle). |

### 🔥 Pitfalls in Production

**1. Building Adjacency Matrix for Sparse Graph**

```java
// BAD: 1M node graph as adjacency matrix
// 1M × 1M boolean matrix = 10^12 booleans = 1 TB memory!
boolean[][] adj = new boolean[1_000_000][1_000_000];

// GOOD: Adjacency list for sparse graphs
Map<Integer, List<Integer>> adj = new HashMap<>();
// For 1M nodes each with avg 5 edges = 5M edges entries only
```

**2. Not Handling Disconnected Components**

```java
// BAD: BFS from single node misses disconnected components
bfs(graph, 0, visited);
// Nodes in components disconnected from 0 never visited!

// GOOD: Run BFS/DFS for each unvisited node
for (int v = 0; v < V; v++) {
    if (!visited.contains(v)) {
        bfs(graph, v, visited); // covers all components
    }
}
```

**3. Forgetting to Mark Visited — Infinite Loop on Cyclic Graph**

```java
// BAD: DFS/BFS without visited tracking on cyclic graph
void dfs(Map<Integer,List<Integer>> g, int v) {
    for (int nb : g.get(v)) dfs(g, nb); // infinite loop on cycle!
}

// GOOD: Track visited
Set<Integer> visited = new HashSet<>();
void dfs(Map<Integer,List<Integer>> g, int v) {
    if (visited.contains(v)) return;
    visited.add(v);
    for (int nb : g.getOrDefault(v, List.of()))
        dfs(g, nb);
}
```

### 🔗 Related Keywords

- `BFS` — breadth-first traversal using a queue; finds shortest path in unweighted graphs.
- `DFS` — depth-first traversal using a stack; used for topological sort and cycle detection.
- `Dijkstra's Algorithm` — weighted shortest path using a priority queue.
- `Topological Sort` — linear ordering of vertices in a DAG by Kahn's/DFS.
- `Minimum Spanning Tree` — Prim's/Kruskal's algorithms on weighted undirected graphs.
- `Cycle Detection` — DFS with colouring (directed) or parent tracking (undirected).

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Vertices + Edges = any network/relation.  │
│              │ Adj list O(V+E) sparse; matrix O(V²) dense│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Social networks, routing, scheduling,     │
│              │ dependencies, recommendation systems.     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hierarchical data without cross-links →   │
│              │ use Tree; flat sequential → use Array.    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Graph: the universal structure for        │
│              │ anything connected to anything."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BFS → DFS → Dijkstra → Topological Sort   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A social network graph has 500 million users (vertices) and 5 billion friendships (edges). The engineering team must decide between adjacency list and adjacency matrix representations for the "find all friends of friends of user X" query. Analyse memory requirements for both representations, then explain why even the adjacency list at this scale requires a distributed graph database rather than an in-memory structure on a single machine — and name one approach used by production graph databases to partition this data.

**Q2.** Topological sort produces a valid ordering only for DAGs. A package manager runs topological sort on package dependencies to determine installation order. If package A depends on B, B depends on C, and C depends on A (circular dependency), Kahn's algorithm fails to produce a complete ordering. Describe exactly what observable output the algorithm produces when given a cyclic graph, explain how this output can be used to report the specific packages involved in the cycle to the user, and outline an algorithm to identify all nodes participating in any cycle in a directed graph in O(V+E) time.

