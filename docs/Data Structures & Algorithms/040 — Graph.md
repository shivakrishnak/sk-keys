---
layout: default
title: "Graph"
parent: "Data Structures & Algorithms"
nav_order: 40
permalink: /dsa/graph/
number: "0040"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, HashMap, LinkedList
used_by: BFS, DFS, Dijkstra, Topological Sort, Union-Find (Disjoint Set)
related: Tree, Matrix, Adjacency List
tags:
  - datastructure
  - intermediate
  - algorithm
  - distributed
---

# 040 — Graph

⚡ TL;DR — A Graph models pairwise relationships between entities as vertices and edges, enabling shortest-path, reachability, and dependency-analysis algorithms.

| #040 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, HashMap, LinkedList | |
| **Used by:** | BFS, DFS, Dijkstra, Topological Sort, Union-Find (Disjoint Set) | |
| **Related:** | Tree, Matrix, Adjacency List | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a navigation app. Cities are locations; roads connect cities. Users ask: "What is the shortest route from London to Paris?" If you store cities in a list and roads as strings "LondonParis", there is no way to *traverse* the connections algorithmically. You cannot determine reachability, shortest path, or cycles using lists and strings alone.

THE BREAKING POINT:
Real-world problems — routing, social networks, dependency resolution, scheduling — model *relationships* between entities, not just the entities themselves. Arrays and lists store individual items but have no first-class representation for "A is connected to B with a given weight." Without a structure for relationships, every algorithm must reinvent connection tracking ad hoc.

THE INVENTION MOMENT:
Define entities as *vertices* and relationships as *edges* connecting vertices. Edges can be directed or undirected, weighted or unweighted. This representation is general enough to model any pairwise relationship — and decades of algorithms (BFS, DFS, Dijkstra, Bellman-Ford, topological sort) work on it unchanged. This is exactly why the Graph was created.

### 📘 Textbook Definition

A **Graph** G = (V, E) is a mathematical structure consisting of a set of *vertices* (nodes) V and a set of *edges* E, where each edge connects two vertices. A *directed graph* (digraph) has edges with direction; an *undirected graph* has bidirectional edges. Edges may carry numerical *weights*. Common representations: an *adjacency matrix* (V × V 2D array, O(V²) space) and an *adjacency list* (array/map of edge lists, O(V + E) space). Graph algorithms solve problems including reachability, shortest path, cycle detection, topological ordering, and connected components.

### ⏱️ Understand It in 30 Seconds

**One line:**
A structure of nodes connected by edges — the universal model for networks and relationships.

**One analogy:**
> A graph is like an airport map: cities are airports (vertices) and flights are connections (edges). A flight's ticket price is the weight. "How do I get from New York to Tokyo with the cheapest connections?" is a shortest-path problem on this flight graph.

**One insight:**
A Graph is not a data structure — it is a *model*. Its power comes from the dozens of well-studied algorithms that work on it. When you model a problem as a graph, you instantly inherit BFS, DFS, Dijkstra, topological sort, and more, for free.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A graph consists of vertices (things) and edges (relationships between things).
2. An edge exists independently of the vertices it connects — two vertices can exist without an edge.
3. The representation (adjacency matrix vs list) determines the complexity of operations — the logical graph is the same.

DERIVED DESIGN:
The two classic representations have complementary trade-offs:

**Adjacency Matrix** (2D boolean/weight array):
- `matrix[u][v]` = 1/weight if edge (u,v) exists, 0 otherwise.
- `hasEdge(u,v)`: O(1). Add edge: O(1). Neighbours of u: O(V).
- Space: O(V²) — impractical for large sparse graphs.

**Adjacency List** (array of linked lists or `Map<Node, List<Node>>`):
- `list[u]` = list of u's neighbours.
- `hasEdge(u,v)`: O(degree(u)). Add edge: O(1). Neighbours of u: O(degree(u)).
- Space: O(V + E) — efficient for sparse graphs.

Rule: Use adjacency matrix when graph is dense (E ≈ V²) and O(1) edge queries matter. Use adjacency list when graph is sparse (E << V²) — most real-world graphs.

THE TRADE-OFFS:
Gain: Universal model for relationships; all graph algorithms available.
Cost: Memory and algorithm complexity depend on graph density; representation mismatch causes performance problems.

### 🧪 Thought Experiment

SETUP:
A social network with 100M users. You need to find if user A can reach user B through friend connections (are they in the same connected component?).

WHAT HAPPENS WITH A LIST OF USER OBJECTS:
Each user has a `List<User> friends`. To check A-B reachability, you must explore all reachable friends starting from A — this is BFS/DFS. But how many users do you visit? In the worst case, the entire connected component: up to 100M users. Without a visited set, you revisit nodes exponentially.

WHAT HAPPENS WITH A PROPER GRAPH REPRESENTATION:
Adjacency list: `Map<Integer, List<Integer>> graph`. BFS with a `Set<Integer> visited`. Each user visited once: O(V + E) total. For a sparse social graph, E ≈ 10 × V (each person has ~10 friends), so total work is O(11V) = O(V). For 100M users: ~1 billion operations — feasible in seconds.

THE INSIGHT:
Without explicit visited tracking, graph traversal re-enters nodes infinitely in cyclic graphs. The graph model provides the structure; BFS/DFS with a visited set provides the protocol. Both are required — neither works alone.

### 🧠 Mental Model / Analogy

> A graph is a roadmap. Cities are vertices; roads are edges; distances are weights. Navigation algorithms (BFS = bidi search, Dijkstra = GPS routing) drive on this map to find paths. The map does nothing by itself — it enables navigation algorithms.

"City" → vertex
"Road between cities" → edge
"One-way road" → directed edge
"Road length" → edge weight
"GPS routing" → Dijkstra's algorithm on the graph

Where this analogy breaks down: Real roads are embedded in 2D space; graph edges have no spatial layout — a "vertex" might connect to 10,000 others (as in a web page linking to many URLs), which no real road can do.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A collection of things (nodes) connected by links (edges). Think of a social network: people are nodes, friendships are edges.

**Level 2 — How to use it (junior developer):**
Represent as `Map<Integer, List<Integer>> graph = new HashMap<>()`. For undirected graph, add each edge in both directions: `graph.get(u).add(v); graph.get(v).add(u)`. For directed: `graph.get(u).add(v)` only. For weighted: use `Map<Integer, List<int[]>>` where `int[0]=neighbour, int[1]=weight`. Always initialise each vertex with an empty list before adding edges.

**Level 3 — How it works (mid-level engineer):**
BFS traversal: O(V + E) — every vertex and every edge visited once. DFS: same O(V + E). Key: always maintain a `visited` set to prevent re-visiting in cycles. For directed graphs, distinguish between "visited" (reachability) and "in-current-path" (cycle detection). Topological sort requires a DAG (Directed Acyclic Graph); cycles break it. Dijkstra requires non-negative edge weights; Bellman-Ford handles negative edges.

**Level 4 — Why it was designed this way (senior/staff):**
Graph theory predates computers (Euler's Bridges of Königsberg, 1736). The adjacency list representation was formalised because real-world graphs have E << V² (sparse). Social networks, dependency trees, internet topology, road networks — all sparse. The sparse: O(V+E) adjacency list outperforms dense: O(V²) matrix for algorithms whose inner loop iterates neighbours (DFS, BFS, Dijkstra). Modern graph processing frameworks (Apache Spark GraphX, Neo4j, NetworkX) all use adjacency lists internally. Distributed graph processing (Pregel model, used by Google's PageRank computation) partitions vertices across machines with edge messages crossing partitions.

### ⚙️ How It Works (Mechanism)

**Building an undirected weighted graph:**
```java
Map<Integer, List<int[]>> graph = new HashMap<>();

void addEdge(int u, int v, int w) {
    graph.computeIfAbsent(u, k -> new ArrayList<>())
         .add(new int[]{v, w});
    graph.computeIfAbsent(v, k -> new ArrayList<>())
         .add(new int[]{u, w}); // undirected: both ways
}

// Example: addEdge(0, 1, 4), addEdge(0, 2, 2)
// graph = {0: [(1,4),(2,2)], 1: [(0,4)], 2: [(0,2)]}
```

**Graph traversal (BFS):**
```java
void bfs(int start) {
    Set<Integer> visited = new HashSet<>();
    Deque<Integer> queue = new ArrayDeque<>();
    queue.offer(start);
    visited.add(start);
    while (!queue.isEmpty()) {
        int u = queue.poll();
        System.out.print(u + " ");
        for (int[] edge : graph.getOrDefault(u, List.of())) {
            int v = edge[0];
            if (!visited.contains(v)) {
                visited.add(v);
                queue.offer(v);
            }
        }
    }
}
```

┌───────────────────────────────────────────────────────┐
│  Directed Weighted Graph (adjacency list)             │
│                                                       │
│  0 ──4──► 1 ──3──► 4                                 │
│  │                    ↑                               │
│  2──► 2 ──1──► 3 ──7──┘                              │
│                                                       │
│  Adjacency list:                                      │
│  0: [(1,4), (2,2)]                                    │
│  1: [(4,3)]                                           │
│  2: [(3,1)]                                           │
│  3: [(4,7)]                                           │
│  4: []                                                │
└───────────────────────────────────────────────────────┘

**Adjacency matrix for dense graphs:**
```java
int[][] matrix = new int[V][V];
// matrix[u][v] = weight (0 = no edge)
matrix[0][1] = 4;
matrix[0][2] = 2;
// hasEdge(u,v): matrix[u][v] != 0 — O(1)
// neighbours of u: scan matrix[u][0..V-1] — O(V) ← expensive
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Problem identified as graph problem (relationships exist)
→ Choose representation: adjacency list (sparse, typical)
→ [GRAPH ← YOU ARE HERE]
→ Apply algorithm: BFS (shortest hops), Dijkstra (weighted shortest),
  DFS (connectivity, cycles), Topo sort (dependency order)
→ Extract result: path, distance, ordering, components
```

FAILURE PATH:
```
Graph contains cycles but algorithm assumes DAG (e.g., topological sort)
→ Topological sort enters infinite loop or produces wrong results
→ Fix: detect cycles before applying topology sort
→ Use DFS with "in-stack" flag; if back-edge found, report cycle
```

WHAT CHANGES AT SCALE:
At V=100M vertices (Twitter user graph), a single-machine adjacency list requires O(V+E) in memory (~50GB for 100M users × 200 friends each). Real social graph algorithms use distributed processing: split vertices across machines; edges crossing partition boundaries become inter-machine messages. Pregel, PowerGraph, GraphX all use this message-passing model. For road networks with V=10M junctions, Dijkstra is too slow — use A* with geographic heuristics or pre-computed landmarks.

### 💻 Code Example

**Example 1 — Cycle detection in directed graph (DFS):**
```java
boolean hasCycle(Map<Integer, List<Integer>> graph) {
    Set<Integer> visited = new HashSet<>();
    Set<Integer> inStack = new HashSet<>();
    for (int node : graph.keySet())
        if (dfsDetect(graph, node, visited, inStack))
            return true;
    return false;
}

boolean dfsDetect(Map<Integer, List<Integer>> g,
                  int node,
                  Set<Integer> visited,
                  Set<Integer> inStack) {
    if (inStack.contains(node)) return true;  // back edge!
    if (visited.contains(node)) return false;
    visited.add(node); inStack.add(node);
    for (int neighbor : g.getOrDefault(node, List.of()))
        if (dfsDetect(g, neighbor, visited, inStack))
            return true;
    inStack.remove(node);
    return false;
}
```

**Example 2 — Connected components (BFS):**
```java
int countComponents(int n,
                    Map<Integer, List<Integer>> graph) {
    Set<Integer> visited = new HashSet<>();
    int components = 0;
    for (int i = 0; i < n; i++) {
        if (!visited.contains(i)) {
            bfsComponent(graph, i, visited);
            components++;
        }
    }
    return components;
}
```

**Example 3 — Build graph from edge list (common interview pattern):**
```java
Map<Integer, List<Integer>> buildGraph(int[][] edges) {
    Map<Integer, List<Integer>> g = new HashMap<>();
    for (int[] e : edges) {
        g.computeIfAbsent(e[0], k -> new ArrayList<>())
         .add(e[1]);
        g.computeIfAbsent(e[1], k -> new ArrayList<>())
         .add(e[0]); // undirected
    }
    return g;
}
```

### ⚖️ Comparison Table

| Representation | hasEdge | Neighbours | Space | Best For |
|---|---|---|---|---|
| **Adjacency List** | O(degree) | O(degree) | O(V+E) | Sparse graphs (real world) |
| Adjacency Matrix | O(1) | O(V) | O(V²) | Dense graphs, fast edge queries |
| Edge List | O(E) | O(E) | O(E) | Simple storage, algorithm input |
| Implicit (function) | O(1) | Computed | O(1) | Grids, infinite graphs |

How to choose: Use adjacency list for all sparse real-world graphs. Use adjacency matrix only when V is small (≤ 1,000) AND O(1) edge queries are critical. Edge lists are useful for sorting edges (Kruskal's MST) but not traversal.

### 🔁 Flow / Lifecycle

```
Model the problem:
  → Identify vertices and edges
  → Directed or undirected? Weighted?
     ↓
Choose representation:
  → Sparse → adjacency list
  → Dense  → adjacency matrix
     ↓
Populate:
  → addEdge(u, v, w) or read from input
     ↓
Apply algorithm:
  → BFS (unweighted shortest), DFS (reachability, cycles)
  → Dijkstra (weighted shortest), Bellman-Ford (negative edges)
  → Topo sort (dependencies), Union-Find (components)
     ↓
Return result and free memory
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Trees are not graphs | A tree is a connected acyclic undirected graph — a special case of graph |
| Graphs must be connected | Disconnected graphs are valid; BFS/DFS from one node only visits its component |
| Adjacency list is always better than matrix | For dense graphs (E ≈ V²) and O(1) edge queries, matrix is better |
| DFS always finds the shortest path | DFS finds A path, not the shortest; BFS finds the shortest path in unweighted graphs |
| A graph must have unique edges | Multigraphs allow multiple edges between the same pair of vertices |

### 🚨 Failure Modes & Diagnosis

**1. Infinite loop from missing visited set in cyclic graph**

Symptom: BFS or DFS never terminates; CPU at 100%, thread appears hung.

Root Cause: Graph has a cycle; traversal revisits nodes indefinitely without a visited set.

Diagnostic:
```bash
jstack <pid> | grep "RUNNABLE" -A 20
# Will show thread stuck in BFS/DFS loop forever
```

Fix:
```java
// BAD: no visited tracking
queue.offer(start);
while (!queue.isEmpty()) {
    int u = queue.poll();
    for (int v : graph.get(u)) queue.offer(v); // loops!
}

// GOOD: visited set prevents re-entry
Set<Integer> visited = new HashSet<>();
visited.add(start);
queue.offer(start);
while (!queue.isEmpty()) {
    int u = queue.poll();
    for (int v : graph.getOrDefault(u, List.of()))
        if (visited.add(v)) queue.offer(v); // Set.add returns false if dupe
}
```

Prevention: Always initialise a `visited` set before any graph traversal.

---

**2. Wrong answer from missing nodes in adjacency list**

Symptom: BFS doesn't visit all nodes; some nodes with no outgoing edges are silently skipped.

Root Cause: Nodes with only incoming edges never appear as keys in the adjacency list and are never seeded into BFS.

Diagnostic:
```bash
# Check if node count matches expected:
System.out.println("graph size: " + graph.size());
System.out.println("n = " + n);
```

Fix: Initialise all nodes explicitly in the adjacency list, even if they have no outgoing edges:
```java
for (int i = 0; i < n; i++)
    graph.putIfAbsent(i, new ArrayList<>());
```

Prevention: Separate vertex creation from edge creation; always initialise all V vertices.

---

**3. StackOverflowError from recursive DFS on large graphs**

Symptom: `StackOverflowError` during DFS on graphs with long chains (e.g., linked-list-shaped graphs or dense dependency trees).

Root Cause: Recursive DFS uses JVM call stack; depth limited to ~5,000–10,000 frames.

Diagnostic:
```bash
java -Xss1m MyApp  # increase stack size — band-aid
```

Fix: Convert recursive DFS to iterative using an explicit `ArrayDeque` stack.

Prevention: Always use iterative DFS for production graph traversal where input size is unbounded.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — adjacency matrix representation uses a 2D array.
- `HashMap` — adjacency list often uses `Map<Integer, List<Integer>>` for flexible vertex IDs.
- `LinkedList` — early adjacency list implementations used linked lists per vertex.

**Builds On This (learn these next):**
- `BFS` — breadth-first traversal on a graph; finds shortest path in unweighted graphs.
- `DFS` — depth-first traversal; used for cycle detection, topological sort, and connectivity.
- `Dijkstra` — shortest-path algorithm on weighted graphs using a priority queue.
- `Topological Sort` — linear ordering of vertices in a DAG respecting edge directions.
- `Union-Find (Disjoint Set)` — alternative for connected components in undirected graphs.

**Alternatives / Comparisons:**
- `Tree` — a connected acyclic undirected graph; simpler traversal (no cycles to handle).
- `Matrix` — 2D grid is an implicit graph where each cell connects to its 4 or 8 neighbours.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ V vertices + E edges: universal model for │
│              │ pairwise relationships between entities   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Lists and arrays have no native model for │
│ SOLVES       │ "A is connected to B" relationships       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A graph is a model, not an algorithm:     │
│              │ it enables BFS, DFS, Dijkstra, and more   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Navigation, social networks, dependency   │
│              │ resolution, scheduling, network topology  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data is purely hierarchical (use Tree) or │
│              │ pairwise relationships don't exist        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Adjacency list: O(V+E) space, O(degree)   │
│              │ edge query vs matrix O(V²) / O(1) query   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Airports are nodes, flights are edges —  │
│              │  the flight map is the graph"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BFS → DFS → Dijkstra                      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A dependency resolution system for package management (like npm or Maven) must detect circular dependencies and refuse to build them. Model this as a graph problem: what do vertices and edges represent, what property of the graph indicates a circular dependency, and what algorithm detects it? At 100,000 packages with an average of 10 dependencies each, what is the time complexity of the detection algorithm, and would it run in under 1 second?

**Q2.** Google's original PageRank algorithm treats the web as a directed graph where each page is a vertex and each hyperlink is a directed edge. The rank of a page is proportional to the ranks of all pages linking to it. This creates a system of linear equations. Why does this problem require the graph to be treated as a whole (not processed vertex by vertex independently), and what graph property — specifically about dangling nodes and disconnected components — required Google to add the "damping factor" to make the algorithm converge?

