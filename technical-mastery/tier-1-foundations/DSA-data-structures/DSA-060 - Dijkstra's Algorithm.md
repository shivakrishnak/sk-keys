---
id: DSA-060
title: "Dijkstra's Algorithm"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018, DSA-028
used_by: DSA-061, DSA-091
related: DSA-061, DSA-059, DSA-064
tags:
  - algorithms
  - dijkstra
  - shortest-path
  - weighted-graph
  - greedy
  - o-e-log-v
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/dsa/dijkstras-algorithm/
---

## TL;DR

Dijkstra's algorithm finds the shortest path from a source
to all nodes in a weighted graph with non-negative edges in
O((V+E) log V) using a min-heap - the algorithm behind
GPS navigation and network routing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-060 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, shortest-path, Dijkstra, weighted-graph |
| **Prerequisites** | DSA-018, DSA-028 |

---

### The Problem This Solves

"What is the cheapest flight route from New York to Tokyo
with layovers?" Given a weighted graph (nodes=airports,
edges=flights, weights=cost), find the minimum total weight
path. BFS works only for unweighted graphs. Dijkstra handles
non-negative weights.

---

### Textbook Definition

Dijkstra's algorithm computes single-source shortest paths
in a weighted directed (or undirected) graph with
non-negative edge weights. Maintains a distance array d[]
initialized to infinity, d[source]=0. Uses a min-heap
(priority queue) to always process the nearest unvisited
node next. For each processed node, relaxes all outgoing
edges: if d[u] + weight(u,v) < d[v], update d[v].
Time: O((V+E) log V) with binary heap.

---

### How It Works

**Implementation:**

```java
int[] dijkstra(int source, List<int[]>[] adj, int n) {
    // adj[u] = list of [v, weight]
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[source] = 0;

    // Min-heap: [distance, node]
    PriorityQueue<int[]> pq = new PriorityQueue<>(
        Comparator.comparingInt(a -> a[0])
    );
    pq.offer(new int[]{0, source});

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int d = curr[0], u = curr[1];

        // Skip if we already found a better path
        if (d > dist[u]) continue;

        for (int[] edge : adj[u]) {
            int v = edge[0], w = edge[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.offer(new int[]{dist[v], v});
            }
        }
    }
    return dist; // dist[i] = shortest distance from source to i
}
```

**Why greedy works here (non-negative weights only):**

```
Once a node is popped from the min-heap with distance d,
d is FINAL - no future path can improve it because all
future edges add non-negative weight. This is the greedy
invariant that makes Dijkstra correct.

With negative weights, this invariant breaks:
  A --(-5)-- B -- 3 -- C
  Source=A, direct to C via B: 0-5+3 = -2
  But we might have popped C earlier at cost 0
  → wrong answer. Use Bellman-Ford for negative weights.
```

---

### Comparison Table

| Property | Dijkstra | Bellman-Ford | BFS |
|---------|----------|-------------|-----|
| Negative weights | No | Yes | No (unweighted only) |
| Time | O((V+E)logV) | O(V*E) | O(V+E) |
| SSSP | Yes | Yes | Yes (unweighted) |
| Detects negative cycles | No | Yes | N/A |
| Practical for GPS | Yes | No (too slow) | No |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Dijkstra works with negative edges" | It does NOT. Negative edges break the greedy invariant. Use Bellman-Ford for negative edges |
| "Dijkstra is BFS with weights" | Conceptually similar (both explore nearest-first), but Dijkstra uses a min-heap on cumulative distances, not a FIFO queue on hops |

---

### Failure Modes & Diagnosis

**Failure: Dijkstra gives wrong results**
- Cause 1: Graph has negative edge weights
- Cause 2: Not skipping stale heap entries
  (missing `if d > dist[u]: continue`)
- Fix: Check for negative weights; always skip stale entries

---

### Quick Reference Card

| Property | Dijkstra |
|---------|---------|
| Time (binary heap) | O((V+E) log V) |
| Space | O(V+E) |
| Negative edges | NOT supported |
| Output | Shortest dist from source to all nodes |
| Java class | PriorityQueue |

---

### The Surprising Truth

OSPF (Open Shortest Path First), the routing protocol
used by most corporate networks and the internet backbone,
runs Dijkstra's algorithm every time a router detects a
topology change. Every packet you send traverses paths
computed by Dijkstra. The algorithm (published 1959 by
Edsger Dijkstra) was designed when computers had no
magnetic tape - Dijkstra chose the algorithm that could
be computed mentally in 20 minutes by hand. He later
said it was one of the most elegant things he ever
designed.

---

### Mastery Checklist

- [ ] Can implement Dijkstra with PriorityQueue from memory
- [ ] Understands why negative weights break it
- [ ] Knows the stale-entry skip optimization

---

### Interview Deep-Dive

**Q1 (Hard):** You're designing a network router. Given
a topology of routers and link costs, find the least-cost
path from router A to all other routers. What algorithm
and data structure?

> Dijkstra's algorithm with adjacency list and min-heap.
> Model each router as a node, each link as a directed
> (or undirected) edge with weight = link cost.
> Use PriorityQueue<int[]> ordered by cumulative cost.
> Time: O((V+E) log V) where V=routers, E=links.
> This is exactly OSPF (Open Shortest Path First).
> Practical considerations: all link costs must be
> positive (use Bellman-Ford or constrained OSPF if
> negative cost links exist). For very large networks
> (BGP at internet scale), hierarchical approaches
> split the network into areas, running Dijkstra within
> each area. Java's NetworkTopology libraries expose
> exactly this interface.
