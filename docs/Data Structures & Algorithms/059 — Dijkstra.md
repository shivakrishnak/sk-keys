---
layout: default
title: "Dijkstra"
parent: "Data Structures & Algorithms"
nav_order: 59
permalink: /dsa/dijkstra/
number: "0059"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Graph, Priority Queue, Greedy Algorithm, BFS
used_by: A* Search, GPS Navigation, Network Routing (OSPF)
related: Bellman-Ford, A* Search, BFS
tags:
  - algorithm
  - graph
  - intermediate
  - pattern
  - performance
---

# 059 — Dijkstra

⚡ TL;DR — Dijkstra's algorithm finds shortest paths from a single source in weighted graphs with non-negative edge weights using a greedy priority-queue expansion.

| #059 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Graph, Priority Queue, Greedy Algorithm, BFS | |
| **Used by:** | A* Search, GPS Navigation, Network Routing (OSPF) | |
| **Related:** | Bellman-Ford, A* Search, BFS | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a GPS navigation app. The road network is a weighted graph where edge weights are travel times in minutes. You need the fastest route from location A to location B. BFS would find the fewest road segments, but road segments vary widely in length and speed — a 1-hop highway route might be faster than a 5-hop city-street route. Naive exhaustive search of all paths is exponential.

THE BREAKING POINT:
Weighted graphs require a fundamentally different strategy than unweighted BFS. A path via 10 fast edges might beat a direct but slow edge. You need an algorithm that accounts for cumulative weights, not just hop counts.

THE INVENTION MOMENT:
Edsger Dijkstra observed in 1956 that you can greedily expand the shortest-path frontier: always process the node with the currently smallest known distance from the source. Once a node is processed, its shortest distance is finalised — no later path can improve it (because all edge weights are non-negative, any extension of the current path can only increase or maintain the total distance). This greedy invariant makes the algorithm correct. This is exactly why **Dijkstra's algorithm** was created.

---

### 📘 Textbook Definition

**Dijkstra's algorithm** solves the Single-Source Shortest Path (SSSP) problem on weighted directed or undirected graphs with non-negative edge weights. It maintains a priority queue of (distance, node) pairs, always processing the minimum-distance node first. It relaxes edges: for each neighbour `v` of processed node `u`, if `dist[u] + weight(u,v) < dist[v]`, update `dist[v]` and enqueue `(dist[v], v)`. The algorithm runs in `O((V + E) log V)` with a binary heap priority queue.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Always take the nearest unvisited city next, recording the best known route to each city as you go.

**One analogy:**
> Imagine water flowing from a source through a network of pipes of different widths. Water always takes the path of least resistance first. The water front reaches each junction via the fastest route — because water, like Dijkstra's frontier, always expands in the direction of least total resistance.

**One insight:**
The key correctness property is: **once a node is popped from the priority queue, its distance is final.** This works exclusively because edge weights are non-negative — any path that continues from an unvisited node can only increase (or stay equal) in total distance. Negative edges break this guarantee, which is why Dijkstra fails on graphs with negative edge weights.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. `dist[v]` stores the best known distance from source to `v`. Initially `dist[source] = 0`, all others `= ∞`.
2. Processed nodes have their **exact shortest distance finalised** — they are never revisited.
3. All edge weights must be **non-negative** for the greedy invariant to hold.

DERIVED DESIGN:
Given invariant 2, the algorithm needs a data structure that efficiently yields the minimum-distance unprocessed node. A min-heap priority queue achieves this in `O(log V)` per operation. The outer loop runs V times (once per node processed) and the inner edge relaxation runs E times total. Combined: `O((V + E) log V)`.

**Edge relaxation:**
```
if dist[u] + weight(u→v) < dist[v]:
    dist[v] = dist[u] + weight(u→v)
    parent[v] = u
    enqueue (dist[v], v)
```

**Why greedy works here but not generally:**
Dijkstra is a greedy algorithm — it commits to the locally optimal choice (expand nearest node). This works because of the non-negative weight invariant: once node `u` is selected as minimum-distance, no future path can reach `u` with a smaller distance (any extension adds non-negative weight). If edges could be negative, a later-processed "shortcut" via a negative edge could improve an already-finalised distance — breaking correctness.

**Comparison with BFS:**
BFS is Dijkstra with all weights = 1. Replacing BFS's FIFO queue with a min-heap priority queue yields Dijkstra. This is not a coincidence: both algorithms maintain a "frontier" and expand in order of distance from source — BFS just happens to work when "distance = hop count."

THE TRADE-OFFS:
Gain: Optimal single-source shortest paths in `O((V+E) log V)`.
Cost: Requires non-negative edge weights; does not detect negative cycles; `O(V)` memory for dist[] and priority queue.

---

### 🧪 Thought Experiment

SETUP:
Graph: S→A (weight 4), S→B (weight 1), B→A (weight 2), A→D (weight 3), B→D (weight 8). Find shortest distance from S to D.

WHAT HAPPENS WITHOUT DIJKSTRA (greedy by hop count like BFS):
S→A→D = 2 hops. S→B→D = 2 hops. BFS picks S→A→D = weight 4+3=7 or S→B→D = weight 1+8=9. Might pick 7.

WHAT HAPPENS WITH DIJKSTRA:
dist = {S:0, A:∞, B:∞, D:∞}. Queue: [(0,S)].
Pop (0,S). Relax S→A: dist[A]=4. Relax S→B: dist[B]=1. Queue: [(1,B),(4,A)].
Pop (1,B). Relax B→A: 1+2=3 < 4 → dist[A]=3. Relax B→D: 1+8=9. Queue: [(3,A),(4,A),(9,D)].
Pop (3,A) — duplicate (4,A) in queue, skip when popped. Relax A→D: 3+3=6 < 9 → dist[D]=6. Queue: [(4,A),(6,D),(9,D)].
Pop (4,A) — already processed (dist[A]=3 < 4 in queue), skip.
Pop (6,D). Optimal: S→B→A→D = 1+2+3 = 6.

THE INSIGHT:
The path S→B→A→D (3 hops) beats S→A→D (2 hops) because going through B first to reach A via the cheaper edge outweighs the extra hop. BFS (hop count) would have missed this. Dijkstra found it by always expanding the smallest-cost frontier.

---

### 🧠 Mental Model / Analogy

> Dijkstra is like a relay race where you always send the fastest available runner next. You track the minimum arrival time at every checkpoint. When a runner arrives at a checkpoint, they immediately dispatch the fastest available runner to each connected checkpoint. The first time a checkpoint is "confirmed reached," that arrival time is the globally minimum time.

"Runner arrives at checkpoint" → node popped from priority queue
"Minimum arrival time" → dist[node]
"Dispatch to connected checkpoints" → edge relaxation to neighbours
"Checkpoint confirmed" → node permanently processed

Where this analogy breaks down: Real relay races don't allow revisiting checkpoints with faster times. Dijkstra does allow updating `dist[v]` if a faster route is found before `v` is processed — this is the relaxation step that moves `v` "earlier" in the priority queue.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Dijkstra finds the fastest route between two places on a map. It greedily expands outward from the starting point, always exploring the closest unvisited location next, until it reaches the destination.

**Level 2 — How to use it (junior developer):**
Initialize `dist[src] = 0`, all others `= Integer.MAX_VALUE`. Use a priority queue sorted by distance. Loop: pop minimum-distance node, skip if already processed, mark processed, relax all edges to unvisited neighbours (if shorter distance found, update and enqueue). When target is popped, return its distance.

**Level 3 — How it works (mid-level engineer):**
The standard priority-queue implementation allows multiple entries for the same node in the queue (lazy deletion). When a node is popped, check if its queued distance equals `dist[node]` — if not, it's an outdated entry, skip it. This avoids the complexity of a decrease-key operation. In dense graphs (E ≫ V), a Fibonacci heap gives O(V log V + E) but is rarely used in practice due to high constant factors. Array-based implementation O(V²) is preferable for very dense graphs where E ≈ V².

**Level 4 — Why it was designed this way (senior/staff):**
Dijkstra's algorithm is the direct application of the greedy algorithm paradigm to the SSSP problem. Its correctness proof by induction on the number of processed nodes is a model of clean algorithmic reasoning. The non-negative weight constraint is not an arbitrary limitation: it is the precise condition under which the greedy invariant (processed nodes have final distances) holds. OSPF routing in IP networks uses Dijkstra: each router computes the shortest path tree rooted at itself, then routes packets to the next hop in that tree. The Dijkstra-like expansion is also the foundation of Prim's MST algorithm — both maintain a "cheapest-to-reach" frontier and greedily commit to cheapest available extensions.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Dijkstra's Algorithm                       │
│                                            │
│  dist[src] = 0, dist[v] = ∞ for all v≠src │
│  pq = MinHeap {(0, src)}                   │
│  processed = {}                            │
│                                            │
│  LOOP while pq not empty:                  │
│    (d, u) = pq.poll()                      │
│    if u in processed: continue ← lazy del  │
│    processed.add(u)                        │
│                                            │
│    for each edge (u → v, weight w):        │
│      if d + w < dist[v]:                   │
│        dist[v] = d + w                     │
│        parent[v] = u                       │
│        pq.offer((dist[v], v))              │
│                                            │
│  Result: dist[] = shortest distances       │
│          Trace parent[] for paths          │
└────────────────────────────────────────────┘
```

**Complexity analysis:**
- V nodes, each popped at most once (after first pop, skipped via lazy deletion)
- E edges total, each relaxation does at most one enqueue
- Priority queue operations: O((V + E) log(V + E)) = O((V + E) log V)

**Path reconstruction (same as BFS):**
`parent[v] = u` records which node was the predecessor on the shortest path to `v`. Trace backwards from target to source and reverse.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Weighted graph + source node
→ Initialize dist[] = ∞, dist[src] = 0
→ Push (0, src) to min-heap
→ [DIJKSTRA ← YOU ARE HERE]
  → Pop min (d, u)
  → Skip if u already processed
  → Relax all outgoing edges of u
  → Push updated (dist[v], v) to heap
→ Repeat until heap empty or target popped
→ Return dist[target], reconstruct path
```

FAILURE PATH:
```
Negative edge weight in graph
→ Dijkstra finalises a node u too early
→ A later path via negative edge gives
  smaller distance to u
→ u is NOT re-processed (already marked)
→ dist[u] returns WRONG (too large) answer
→ Use Bellman-Ford for negative edges
```

WHAT CHANGES AT SCALE:
For road networks (V=10⁷ nodes, E=10⁸ edges), vanilla Dijkstra takes several seconds. Production GPS systems use bidirectional Dijkstra (expand from source AND target simultaneously, meet in the middle — reduces search radius from r to r/2, so explored nodes ~O(r²/4) vs O(r²)), plus preprocessing shortcuts (Contraction Hierarchies) to reduce queries to milliseconds.

---

### 💻 Code Example

**Example 1 — Standard Dijkstra:**
```java
int[] dijkstra(int n,
    List<int[]>[] graph, int src) {
    // graph[u] = list of [v, weight]
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;

    // PQ: [distance, node]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(
            Comparator.comparingInt(a -> a[0]));
    pq.offer(new int[]{0, src});

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int d = curr[0], u = curr[1];
        if (d > dist[u]) continue; // lazy del

        for (int[] edge : graph[u]) {
            int v = edge[0], w = edge[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.offer(new int[]{dist[v], v});
            }
        }
    }
    return dist;
}
```

**Example 2 — Dijkstra with path reconstruction:**
```java
int[] parent;

int shortestPath(int n,
    List<int[]>[] graph, int src, int dst) {
    int[] dist = new int[n];
    parent = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    Arrays.fill(parent, -1);
    dist[src] = 0;

    PriorityQueue<int[]> pq =
        new PriorityQueue<>(
            Comparator.comparingInt(a -> a[0]));
    pq.offer(new int[]{0, src});

    while (!pq.isEmpty()) {
        int[] cur = pq.poll();
        int d = cur[0], u = cur[1];
        if (d > dist[u]) continue;
        if (u == dst) break; // early exit

        for (int[] e : graph[u]) {
            int v = e[0], w = e[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                parent[v] = u;
                pq.offer(new int[]{dist[v],v});
            }
        }
    }
    return dist[dst];
}

List<Integer> getPath(int dst) {
    List<Integer> path = new ArrayList<>();
    for (int v = dst; v != -1; v = parent[v])
        path.add(v);
    Collections.reverse(path);
    return path;
}
```

**Example 3 — Network delay time (all-nodes shortest path):**
```java
int networkDelayTime(int[][] times, int n, int k){
    // times[i] = [src, dst, weight]
    List<int[]>[] graph = new List[n+1];
    for (int i=1; i<=n; i++)
        graph[i] = new ArrayList<>();
    for (int[] t : times)
        graph[t[0]].add(new int[]{t[1],t[2]});

    int[] dist = dijkstra(n+1, graph, k);

    int max = 0;
    for (int i = 1; i <= n; i++) {
        if (dist[i] == Integer.MAX_VALUE)
            return -1; // unreachable node
        max = Math.max(max, dist[i]);
    }
    return max; // max dist = last node reached
}
```

---

### ⚖️ Comparison Table

| Algorithm | Negative Weights | Negative Cycles | Time | Space | Best For |
|---|---|---|---|---|---|
| **Dijkstra** | No | N/A | O((V+E) log V) | O(V) | Non-negative weights, GPS, routing |
| Bellman-Ford | Yes | Detects | O(VE) | O(V) | Negative weights, cycle detection |
| A* | No | N/A | O(E log V) | O(V) | Heuristic-guided, map routing |
| BFS | No (unit weight) | N/A | O(V+E) | O(V) | Unweighted graphs |
| Floyd-Warshall | Yes (no neg cycle) | Detects | O(V³) | O(V²) | All-pairs shortest path |

How to choose: Use Dijkstra for non-negative weights (the common case). Use Bellman-Ford if negative edges exist. Use A* when a heuristic can guide the search (path-finding in physical space). Use Floyd-Warshall when you need all-pairs shortest paths and V is small.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Dijkstra works with negative edge weights | A single negative edge can cause Dijkstra to produce wrong results. The greedy finalisation invariant requires all edge weights ≥ 0 |
| Once target is popped from queue, we can stop | Yes — this is correct and a useful optimisation. The first time target is popped, its distance is final. Many textbooks describe running to completion — stopping early is more efficient |
| Dijkstra finds shortest paths to ALL nodes | Dijkstra naturally computes SSSP (single-source, all destinations). To find just the shortest path to one target, stop when the target is first popped |
| The priority queue should use set/visited instead of lazy deletion | Both approaches are correct. Lazy deletion (allow duplicates, skip stale entries on pop) is simpler to implement and performs identically in practice |
| Dijkstra is O(V²) | With a binary heap, Dijkstra is O((V+E) log V). The O(V²) bound applies only to the naive array-based implementation (scan all V nodes per step instead of using a heap) |

---

### 🚨 Failure Modes & Diagnosis

**1. Negative edge weight causes incorrect shortest path**

Symptom: Dijkstra returns a distance that is larger than expected; verified incorrect by manual calculation.

Root Cause: A node `u` is finalised too early (before the path through a negative edge reaches it). The negative edge would reduce `dist[u]` further, but `u` is already marked processed.

Diagnostic:
```java
// Validate all edge weights before running:
for (int[] edge : edges)
    if (edge[2] < 0)
        throw new IllegalArgumentException(
            "Dijkstra: negative edge " +
            Arrays.toString(edge));
```

Fix: Use Bellman-Ford for graphs with negative edges.

Prevention: Document that the graph must have non-negative weights. Validate at input boundary.

---

**2. Integer overflow in distance addition**

Symptom: Dijkstra returns a negative distance or crashes with unexpected results.

Root Cause: `dist[u] = Integer.MAX_VALUE` (initial "infinity"). Adding any positive weight overflows to a negative number. `Integer.MAX_VALUE + 1 = Integer.MIN_VALUE`.

Diagnostic:
```java
// Symptom: dist[target] = -2147483647
// or similar negative value
```

Fix:
```java
// BAD: overflows when dist[u] = MAX_VALUE
if (dist[u] + w < dist[v]) ...

// GOOD: check before adding
if (dist[u] != Integer.MAX_VALUE
    && dist[u] + w < dist[v]) ...
```

Prevention: Use `Long.MAX_VALUE / 2` as infinity, or explicit overflow check before addition.

---

**3. Missing lazy deletion check causes processing node twice**

Symptom: Correct results but slower than expected; profiling shows the inner loop executes more than E times total.

Root Cause: Without the `if (d > dist[u]) continue` check, outdated queue entries cause a node to be processed multiple times. Each re-processing re-relaxes all edges from that node unnecessarily.

Diagnostic:
```java
int processCount = 0;
while (!pq.isEmpty()) {
    processCount++;
    // ... if this >> V, lazy deletion missing
}
System.out.println("Total pops: " + processCount);
// Should be ≈ E (with lazy deletions),
// not >> E
```

Fix: Add `if (d > dist[u]) continue;` immediately after `pq.poll()`.

Prevention: This check is non-optional in the lazy-deletion implementation. Make it a template habit.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — Dijkstra operates on weighted directed/undirected graphs; understand adjacency list with weights.
- `Priority Queue` — the min-heap is the core data structure enabling O(log V) minimum extraction.
- `Greedy Algorithm` — Dijkstra's proof of correctness is the greedy invariant: processed node distances are final.
- `BFS` — BFS is Dijkstra with unit weights; understanding BFS makes Dijkstra's extension to weighted graphs clear.

**Builds On This (learn these next):**
- `A* Search` — Dijkstra with a heuristic function guiding the priority; reduces explored nodes dramatically for geometric graphs.
- `Bellman-Ford` — handles negative edge weights; understands where Dijkstra's greedy fails.
- `Kruskal / Prim` — Prim's MST algorithm uses the same "expand cheapest frontier" pattern as Dijkstra.

**Alternatives / Comparisons:**
- `Bellman-Ford` — slower (O(VE)) but handles negative edges; use when graph has negative weights.
- `Floyd-Warshall` — all-pairs shortest paths in O(V³); use when you need distances between all pairs.
- `BFS` — exact replacement for Dijkstra in unweighted graphs; no priority queue needed.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Greedy single-source shortest path for    │
│              │ non-negative weighted graphs              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Fastest route in a weighted graph         │
│ SOLVES       │ (GPS, network routing, game pathfinding)  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ First-pop = final distance ONLY because   │
│              │ all weights ≥ 0; negative weights break   │
│              │ this guarantee                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Weighted shortest path, non-negative      │
│              │ edges, single source to all destinations  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Negative edge weights (use Bellman-Ford); │
│              │ unweighted graphs (use BFS)               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O((V+E) log V) with heap vs O(V²) array;  │
│              │ non-negative weight constraint            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Always go to the nearest unvisited node" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bellman-Ford → A* Search → Kruskal/Prim   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Dijkstra's algorithm processes the node with the smallest current distance at each step. Consider a graph where all edge weights are equal (say, weight 1). Prove that in this case, Dijkstra's algorithm produces exactly the same traversal order as BFS. What does this reveal about the relationship between BFS and Dijkstra? Now consider: if you change the priority queue in Dijkstra to a LIFO stack instead of a min-heap (and use weight 1 for all edges), what traversal algorithm do you get?

**Q2.** In a road network with 10 million nodes and 50 million edges, running Dijkstra from every possible source to compute all-pairs shortest paths would take O(V × (V+E) log V) time — impractical. Contraction Hierarchies (CH) is a preprocessing technique that reduces routing queries to milliseconds. The key idea is to "shortcut" low-importance nodes: if A→B→C is the shortest path and B is a "low importance" node, add a direct edge A→C. After preprocessing, queries run bidirectional Dijkstra only on "important" nodes. What property must the shortcut edges satisfy to guarantee that CH-augmented Dijkstra still returns correct shortest paths? What does this imply about the correctness condition for using shortcuts?

