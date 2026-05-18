---
id: DSA-061
title: Bellman-Ford Algorithm
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018, DSA-060
used_by: DSA-062
related: DSA-060, DSA-062, DSA-067
tags:
  - algorithms
  - bellman-ford
  - shortest-path
  - negative-weights
  - negative-cycle
  - o-ve
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/dsa/bellman-ford/
---

## TL;DR

Bellman-Ford finds shortest paths with negative edge weights
and detects negative cycles in O(V*E) - slower than Dijkstra
but handles the cases Dijkstra cannot.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-061 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, Bellman-Ford, negative-weights, SSSP |
| **Prerequisites** | DSA-018, DSA-060 |

---

### The Problem This Solves

Dijkstra fails with negative edge weights. Bellman-Ford
handles arbitrage detection in financial markets (negative
cycles represent profit loops), routing with variable
latencies, or any graph where edge costs can be negative.

---

### Textbook Definition

Bellman-Ford computes single-source shortest paths in
directed weighted graphs, including negative edge weights.
Relaxes all V-1 edges V-1 times. If a V-th relaxation
still reduces a distance, a negative cycle exists.
Time: O(V*E). Space: O(V).

---

### How It Works

**Implementation:**

```java
// Returns dist[] or null if negative cycle found
int[] bellmanFord(int source, int[][] edges, int n) {
    // edges[i] = {u, v, weight}
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[source] = 0;

    // Relax all edges V-1 times
    for (int i = 0; i < n - 1; i++) {
        for (int[] edge : edges) {
            int u = edge[0], v = edge[1], w = edge[2];
            if (dist[u] != Integer.MAX_VALUE &&
                    dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }

    // V-th relaxation: detect negative cycle
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        if (dist[u] != Integer.MAX_VALUE &&
                dist[u] + w < dist[v]) {
            return null; // negative cycle found
        }
    }
    return dist;
}
```

**Why V-1 iterations suffice:**

```
In a graph with V nodes, the longest shortest path
has at most V-1 edges (visits each node once).

After iteration k, dist[v] = correct shortest path
using at most k edges.

After V-1 iterations, all shortest paths are found.
If a V-th pass still relaxes anything → a V-node
cycle with negative total weight exists.
```

**Negative cycle use case - arbitrage detection:**

```
Currencies: USD, EUR, GBP
Exchange rates:
  USD → EUR: multiply by 0.85
  EUR → GBP: multiply by 0.88
  GBP → USD: multiply by 1.35

Log transform: edge weight = -log(rate)
  (maximizing product → minimizing sum of negatives)

Check: USD→EUR→GBP→USD total = -(log(0.85)+log(0.88)+log(1.35))
= -((-0.163) + (-0.128) + 0.300) = 0.009 ← negative cycle!
Means multiplying USD→EUR→GBP→USD > 1: arbitrage exists.
```

---

### Comparison Table

| Property | Dijkstra | Bellman-Ford |
|---------|----------|-------------|
| Negative edges | No | Yes |
| Negative cycle detection | No | Yes |
| Time | O((V+E)logV) | O(V*E) |
| Space | O(V+E) | O(V) |
| Practical use | GPS, routing | Arbitrage detection, finance |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Bellman-Ford is just slower Dijkstra" | Different problem class - Bellman-Ford solves cases Dijkstra fundamentally cannot |
| "Negative cycles mean no shortest path exists" | Correct for nodes reachable through the negative cycle; shortest path = -infinity for those nodes |

---

### Quick Reference Card

| Property | Bellman-Ford |
|---------|-------------|
| Time | O(V*E) |
| Space | O(V) |
| Negative edges | Supported |
| Negative cycle detection | Yes (V-th relaxation) |
| Java implementation | Manual (no built-in) |

---

### The Surprising Truth

Bellman-Ford is the basis of the RIP (Routing Information
Protocol), used in smaller networks before OSPF became
dominant. RIP runs a distributed variant of Bellman-Ford
where each router tells neighbors its distance vector.
The "count to infinity" problem in RIP is a manifestation
of Bellman-Ford's inability to handle negative cycles
(topology loops) correctly in a distributed setting -
eventually solved by split-horizon and route poisoning.

---

### Mastery Checklist

- [ ] Implements Bellman-Ford from memory
- [ ] Understands negative cycle detection via V-th pass
- [ ] Knows the arbitrage detection application

---

### Interview Deep-Dive

**Q1 (Hard):** Detect currency arbitrage using graph
algorithms. What is the approach?

> Model currencies as nodes, exchange rates as directed
> edges. To convert a maximization problem (maximize
> product of rates along a path) to a sum minimization
> problem, take the negative logarithm of each rate:
> -log(rate). A negative cycle in this transformed
> graph means the product of original rates along the
> cycle exceeds 1 (profitable arbitrage).
> Run Bellman-Ford. If the V-th relaxation pass still
> reduces any distance, a negative cycle exists.
> Report the cycle nodes as the arbitrage opportunity.
> Time: O(V*E) where V = currencies, E = exchange pairs.
