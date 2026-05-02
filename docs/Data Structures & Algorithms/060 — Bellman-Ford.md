---
layout: default
title: "Bellman-Ford"
parent: "Data Structures & Algorithms"
nav_order: 60
permalink: /dsa/bellman-ford/
number: "0060"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Graph, Dynamic Programming, Dijkstra
used_by: OSPF/BGP Routing, Arbitrage Detection, SSSP with Negative Weights
related: Dijkstra, Floyd-Warshall, SPFA (Shortest Path Faster Algorithm)
tags:
  - algorithm
  - graph
  - advanced
  - deep-dive
  - pattern
---

# 060 — Bellman-Ford

⚡ TL;DR — Bellman-Ford finds shortest paths from a single source by relaxing all edges V-1 times — it handles negative edge weights and detects negative cycles where Dijkstra fails.

| #060 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Graph, Dynamic Programming, Dijkstra | |
| **Used by:** | OSPF/BGP Routing, Arbitrage Detection, SSSP with Negative Weights | |
| **Related:** | Dijkstra, Floyd-Warshall, SPFA (Shortest Path Faster Algorithm) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are building a currency arbitrage detector. The weighted graph has currencies as nodes and exchange rates as edges — but represented as negative logarithms of rates (so shortest path = highest-value conversion). Some exchange rates in this representation become negative edge weights. Dijkstra's algorithm cannot handle these — it finalises distances too eagerly and misses the benefit of negative-weight edges discovered later.

**THE BREAKING POINT:**
Financial routing graphs, VLSI timing analysis graphs, and difference-constraint systems all contain negative edge weights. Dijkstra's greedy finalisation property breaks entirely on negative edges. You need an algorithm that can keep distances "open" to improvement even after initial processing.

**THE INVENTION MOMENT:**
Instead of greedily finalising nodes one by one, relax ALL edges in the graph, V-1 times. After k iterations, `dist[v]` holds the shortest path using at most k edges. After V-1 iterations, all shortest paths of length up to V-1 edges are found — which covers all simple paths (simple paths have at most V-1 edges). A final V-th pass checks if any distance can still be relaxed: if yes, a negative cycle exists (distances would decrease forever). This is exactly why **Bellman-Ford** was created.

---

### 📘 Textbook Definition

**Bellman-Ford** is a single-source shortest path algorithm that works on graphs with negative edge weights (but no negative cycles reachable from the source). It relaxes all E edges in V-1 passes; after pass k, `dist[v]` holds the shortest path of at most k edges. An additional V-th pass detects negative cycles: if any distance decreases, a negative cycle reachable from the source exists. Time complexity: `O(VE)`. Space: `O(V)`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Try improving every route V-1 times, then check if anything can still be improved — that means a "money pump" cycle exists.

**One analogy:**
> Bellman-Ford is like repeatedly asking everyone in a network "is there a cheaper way to reach you that I haven't found yet?" After asking V-1 rounds, everyone should know their cheapest route. If in round V someone says "yes, I found an even cheaper route" — something is impossibly circular, like a perpetual money machine.

**One insight:**
Dijkstra locks in distances greedily; Bellman-Ford keeps all distances "negotiable" until V-1 rounds of negotiation are complete. This patience is what allows negative edges to propagate their savings correctly. The V-th round negative-cycle detection reveals whether any "loop of savings" exists — a structural defect that makes the problem unsolvable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. After `k` relaxation passes, `dist[v] ≤` the shortest path from source to `v` using **at most k edges**.
2. Any simple path has at most **V-1 edges** — V-1 passes are therefore sufficient to find all shortest paths.
3. If `dist[v]` still decreases after V-1 passes, there exists a **negative cycle** reachable from source, making the shortest path `-∞` for nodes on or reachable from that cycle.

**DERIVED DESIGN:**
The DP structure is explicit: `dist_k[v] = min over all edges (u→v): dist_{k-1}[u] + weight(u→v)`. This recurrence computes "shortest path using at most k edges" directly.

In practice, both `dist_k` and `dist_{k-1}` can use the same array — early relaxation (using an updated value in the same pass) only speeds up convergence, never produces wrong results (for correctness, a two-array approach preserves the strict k-edge semantics, but the single-array approach still terminates correctly).

**Negative cycle detection mechanism:**
After V-1 passes, perform pass V. If any edge (u→v) satisfies `dist[u] + w < dist[v]`, then v is on or reachable from a negative cycle. All nodes reachable from this cycle have distance `-∞`.

**Why Dijkstra fails and Bellman-Ford succeeds:**
Dijkstra finalises node A at distance 5. If a later negative edge (B→A, weight -10) is discovered, A's true shortest distance is `dist[B] + (-10)`, potentially less than 5. Dijkstra never re-processes A. Bellman-Ford does not finalise nodes — every pass may re-relax every edge, catching all such improvements.

**THE TRADE-OFFS:**
**Gain:** Handles negative edges; detects negative cycles; simpler to implement correctly than Dijkstra.
**Cost:** O(VE) vs Dijkstra's O((V+E) log V) — much slower for large graphs. For a graph with V=1000, E=500000: Bellman-Ford needs 500,000,000 operations; Dijkstra needs ~6,500,000.

---

### 🧪 Thought Experiment

**SETUP:**
Graph: S→A (weight 4), S→B (weight 5), B→A (weight -6). Shortest path from S to A?

**WHAT HAPPENS WITH DIJKSTRA:**
Pass 1: Pop S. dist[A]=4, dist[B]=5. Pop A (dist=4, finalised).
Discover B→A (weight -6). True dist[A] = dist[B] + (-6) = 5 + (-6) = -1.
But A is already finalised at 4. Dijkstra returns: dist[A] = 4. WRONG.

**WHAT HAPPENS WITH BELLMAN-FORD:**
Pass 1: Relax S→A: dist[A]=4. Relax S→B: dist[B]=5. Relax B→A: dist[B]+(-6)=-1 < 4 → dist[A]=-1.
Pass 2: Relax S→A: 4 > -1, no change. Relax S→B: 5, no change. Relax B→A: -1. No change.
After V-1=2 passes: dist[A] = -1. CORRECT.

**THE INSIGHT:**
Bellman-Ford "re-negotiates" A's distance in pass 1 when it processes B→A after setting dist[A]=4. Dijkstra cannot do this because it finalises A immediately. The key difference is not algorithmic cleverness — it is the willingness to reconsider.

---

### 🧠 Mental Model / Analogy

> Bellman-Ford is like a price negotiation network. Everyone starts with "infinite price" except the seller (source = 0). Each round, everyone asks their neighbours: "Could you sell to me cheaper via you than my current best offer?" After V-1 rounds, all stable minimum prices are found. If in round V someone gets a lower price — there's a loop deal where everyone in the cycle can keep lowering prices forever. That loop is the negative cycle.

- "Current best offer" → dist[v]
- "Asking neighbour" → edge relaxation
- "V-1 rounds" → V-1 Bellman-Ford passes
- "Round V still lowers price" → negative cycle detected
- "Loop deal" → prices decrease forever = no stable shortest path

Where this analogy breaks down: In real negotiation, loops don't create infinite savings. In weighted graphs, negative cycles allow paths of arbitrarily small total weight — the "shortest path" becomes undefined (−∞).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Bellman-Ford finds cheapest routes by repeatedly trying to find cheaper routes V-1 times. Unlike Dijkstra, it handles "discounts" (negative edges). If trying again in round V still finds cheaper routes, something loopy is going on — a cycle that makes costs infinitely reducible.

**Level 2 — How to use it (junior developer):**
Initialize `dist[src]=0`, all others `=∞`. Run V-1 loops: in each loop, go through every edge (u,v,w) and update `dist[v] = min(dist[v], dist[u]+w)`. After V-1 loops, run one more: if any edge still reduces a distance, a negative cycle exists.

**Level 3 — How it works (mid-level engineer):**
Bellman-Ford is a DP algorithm on the "shortest path with at most k edges" recurrence. Its worst-case V-1 passes are tight: a path of V-1 edges (S→1→2→3→...→V-1) requires exactly V-1 passes to propagate the initial distance from S through all nodes. In practice, distances often converge in far fewer passes — SPFA (Shortest Path Faster Algorithm / Bellman-Ford with a queue) runs faster on average by only re-relaxing edges from nodes whose distances changed.

**Level 4 — Why it was designed this way (senior/staff):**
Bellman-Ford is the canonical algorithm for difference constraint systems: given constraints `x_j - x_i ≤ w_{ij}`, transform to a graph where each constraint is an edge (i→j, weight `w_{ij}`), add a supersource with 0-weight edges to all nodes. Bellman-Ford on this graph finds a feasible solution, or reports infeasibility if a negative cycle exists. This connection makes Bellman-Ford essential in STAs (Static Timing Analysis) for VLSI chip design — path delays create constraints that must be solved efficiently. In distributed routing (BGP, RIP), each router runs a distributed version of Bellman-Ford: nodes exchange their current distance estimates with neighbours and update if a shorter path is found. This is the "distributed Bellman-Ford" — correct but vulnerable to the "counting to infinity" problem that BGP mitigates via other mechanisms.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Bellman-Ford Algorithm                     │
│                                            │
│  dist[src] = 0, dist[v] = ∞ for all v≠src │
│                                            │
│  RELAXATION: V-1 passes                    │
│  for i in 1..V-1:                          │
│    for each edge (u, v, weight w):         │
│      if dist[u] + w < dist[v]:            │
│        dist[v] = dist[u] + w              │
│        parent[v] = u                       │
│                                            │
│  NEGATIVE CYCLE CHECK: pass V              │
│  for each edge (u, v, weight w):          │
│    if dist[u] + w < dist[v]:              │
│      → NEGATIVE CYCLE REACHABLE!          │
│        (report, mark affected nodes)       │
│                                            │
│  Result: dist[] = shortest distances,     │
│          or negative cycle detected        │
└────────────────────────────────────────────┘
```

**Marking negative-cycle-affected nodes:**
The V-th pass only reveals nodes directly relaxable by the cycle. To mark ALL nodes reachable from the cycle as `-∞`, run BFS/DFS from all nodes relaxed in pass V and set their distances to `-∞`.

**Early termination:**
If a complete pass makes no updates to any `dist[v]`, the algorithm has converged early. Add a `boolean updated = false` flag — if false after a complete pass, terminate.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Weighted graph (may have negative edges)
→ Initialize dist[] = ∞, dist[src] = 0
→ [BELLMAN-FORD ← YOU ARE HERE]
  → V-1 relaxation passes
  → Distances converge to shortest paths
  → V-th pass negative cycle check
→ Return dist[] (or "negative cycle" error)
```

**FAILURE PATH:**
```
Negative cycle reachable from source
→ V-th pass still relaxes some edge
→ Node on cycle has dist = -∞
→ All nodes reachable from cycle: dist = -∞
→ Algorithm reports: NEGATIVE CYCLE FOUND
→ Problem is unsolvable for those destinations
→ Caller decides: filter out, report error
```

**WHAT CHANGES AT SCALE:**
For dense networks (V=10000, E=10⁸), Bellman-Ford's O(VE) = 10¹² operations is infeasible. Use SPFA (queue-based Bellman-Ford) for average O(kE) where k ≪ V in practice. For Internet routing, distributed Bellman-Ford (RIP protocol) runs asynchronously — each router only re-relaxes when it receives an update from a neighbour. The "counting to infinity" problem (slow convergence on link failures with negative distance loops) is managed by split-horizon and route poisoning heuristics.

---

### 💻 Code Example

**Example 1 — Standard Bellman-Ford:**
```java
int[] bellmanFord(int n, int[][] edges, int src) {
    // edges[i] = [u, v, weight]
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;

    // V-1 relaxation passes
    for (int i = 0; i < n-1; i++) {
        boolean updated = false;
        for (int[] edge : edges) {
            int u = edge[0], v = edge[1];
            int w = edge[2];
            if (dist[u] != Integer.MAX_VALUE
                && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                updated = true;
            }
        }
        if (!updated) break; // early convergence
    }

    // Negative cycle detection (pass V)
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        if (dist[u] != Integer.MAX_VALUE
            && dist[u] + w < dist[v]) {
            throw new RuntimeException(
                "Negative cycle detected!");
        }
    }
    return dist;
}
```

**Example 2 — Currency arbitrage detection:**
```java
// Currencies: nodes 0..N-1
// rates[i][j] = exchange rate from i to j
// Use log-transformed weights: -log(rate)
// Negative cycle = arbitrage opportunity
boolean hasArbitrage(double[][] rates) {
    int n = rates.length;
    double[] dist = new double[n];
    // All nodes reachable from "virtual source"
    // So source is connected to all with weight 0

    // V-1 passes with log weights
    for (int i = 0; i < n-1; i++) {
        boolean updated = false;
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                if (rates[u][v] <= 0) continue;
                double w = -Math.log(rates[u][v]);
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    updated = true;
                }
            }
        }
        if (!updated) return false;
    }

    // Check for negative cycle (arbitrage)
    for (int u = 0; u < n; u++) {
        for (int v = 0; v < n; v++) {
            if (rates[u][v] <= 0) continue;
            double w = -Math.log(rates[u][v]);
            if (dist[u] + w < dist[v]) return true;
        }
    }
    return false;
}
```

**Example 3 — SPFA (Bellman-Ford with queue):**
```java
int[] spfa(int n, List<int[]>[] graph, int src) {
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;
    boolean[] inQueue = new boolean[n];
    int[] count = new int[n]; // relax count

    Queue<Integer> queue = new LinkedList<>();
    queue.offer(src);
    inQueue[src] = true;

    while (!queue.isEmpty()) {
        int u = queue.poll();
        inQueue[u] = false;
        for (int[] edge : graph[u]) {
            int v = edge[0], w = edge[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                if (!inQueue[v]) {
                    count[v]++;
                    if (count[v] >= n)
                        throw new RuntimeException(
                            "Negative cycle!");
                    queue.offer(v);
                    inQueue[v] = true;
                }
            }
        }
    }
    return dist;
}
// SPFA: average O(kE) where k << V in practice
// Worst case still O(VE)
```

---

### ⚖️ Comparison Table

| Algorithm | Negative Edges | Negative Cycle | Time | Space | Best For |
|---|---|---|---|---|---|
| **Bellman-Ford** | Yes | Detects | O(VE) | O(V) | Negative weights, cycle detection |
| Dijkstra | No | N/A | O((V+E) log V) | O(V) | Non-negative weights, most graphs |
| SPFA | Yes | Detects | O(kE) avg | O(V) | Negative weights, average-case speed |
| Floyd-Warshall | Yes (no neg cycle) | Detects | O(V³) | O(V²) | All-pairs, small dense graphs |
| A* | No | N/A | O(E log V) | O(V) | Heuristic, map routing |

How to choose: Use Bellman-Ford when negative edges exist and you need guaranteed correctness. Use SPFA for average-case speed improvement over Bellman-Ford. Use Dijkstra when all weights are non-negative.

---

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────┐
│ Bellman-Ford: Pass Lifecycle                  │
│                                              │
│  Pass 1: Propagate distances 1 hop from src  │
│  Pass 2: Propagate distances 2 hops from src │
│  ...                                         │
│  Pass k: Propagate distances k hops from src │
│  ...                                         │
│  Pass V-1: All shortest simple paths found   │
│  Pass V:   Check for negative cycle          │
│    → No change: algorithm complete           │
│    → Change: negative cycle reachable        │
└──────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bellman-Ford always runs exactly V-1 passes | Early termination: if no distance changes in a pass, the algorithm can stop immediately. V-1 is the worst-case bound |
| Negative edge weight = negative cycle | A single negative edge does not create a cycle. A negative cycle requires a sequence of edges that form a cycle with a total negative weight sum |
| Bellman-Ford detects all negative cycles in a graph | Bellman-Ford only detects negative cycles reachable from the source. Negative cycles in disconnected components or not reachable from the source are not detected |
| SPFA always runs in O(VE) | SPFA's worst case is O(VE) like Bellman-Ford, but the average case is much better (O(kE), k≈2 in practice). Adversarial inputs can force worst-case behavior |
| Bellman-Ford is obsolete given Dijkstra's better complexity | Bellman-Ford remains essential for graphs with negative weights (financial networks, VLSI timing), and its distributed version underlies RIP and BGP routing protocols |

---

### 🚨 Failure Modes & Diagnosis

**1. Integer overflow during distance addition**

**Symptom:** Incorrect distances; random-looking wrong answers; negative distances on graphs with no negative edges.

**Root Cause:** `dist[u] = Integer.MAX_VALUE`. Adding any weight gives overflow: `MAX_VALUE + 1 = -2147483648`. All subsequent comparisons are corrupted.

**Diagnostic:**
```java
// If dist[v] suddenly decreases before any
// valid relaxation, overflow has occurred
System.out.println("OVERFLOW at v=" + v +
    " dist[u]+w=" + (dist[u] + w));
```

**Fix:**
```java
// Guard: only relax if u is reachable
if (dist[u] != Integer.MAX_VALUE
    && dist[u] + w < dist[v])
    dist[v] = dist[u] + w;
```

**Prevention:** Always guard with a reachability check before addition.

---

**2. False negative cycle detection due to source isolation**

**Symptom:** Algorithm reports "negative cycle" but no actual cycle exists; the reported cycle nodes are not reachable from the source.

**Root Cause:** The V-th pass check finds an edge (u→v) where `dist[u]+w < dist[v]`, but `u` was never relaxed (dist[u] = ∞). Initial ∞ + w = overflow → incorrect trigger.

**Diagnostic:**
```java
for (int[] edge : edges) {
    int u=edge[0], v=edge[1], w=edge[2];
    if (dist[u] == Integer.MAX_VALUE) continue;
    if (dist[u] + w < dist[v])
        System.out.println("Neg cycle via edge "
            + Arrays.toString(edge));
}
```

**Fix:** Skip edges where `dist[u] == MAX_VALUE` in the negative cycle check (node u is unreachable, its edge cannot contribute to a meaningful cycle).

**Prevention:** Always guard the negative cycle check with a reachability condition.

---

**3. "Counting to infinity" in distributed Bellman-Ford**

**Symptom:** After a link failure, routing tables slowly count up to "infinity" through many update cycles, causing prolonged routing loops.

**Root Cause:** In distributed Bellman-Ford (RIP protocol), when a link breaks, nodes that previously used the broken link to reach a destination keep advertising stale routes to each other. They incrementally count the hop count up to the infinity threshold (typically 16 in RIP) before convergence.

**Diagnostic:**
```bash
# On a router (Cisco IOS) check RIP updates:
debug ip rip
# Watch for "metric = 15" steadily increasing
# to 16 (infinity) on a removed route
```

**Fix:** Implement split-horizon (don't advertise a route back to the neighbour from which it was learned) and route poisoning (immediately advertise infinity for a failed route) to accelerate convergence.

**Prevention:** Use BGP or OSPF (which use link-state, not distance-vector algorithms) for production Internet routing where convergence speed matters.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — Bellman-Ford operates on directed weighted graphs; understand edge lists and weight representations.
- `Dynamic Programming` — Bellman-Ford is DP on "shortest path with at most k edges"; understand recurrence relations.
- `Dijkstra` — Dijkstra's failure on negative edges is the motivation for Bellman-Ford; understand Dijkstra first.

**Builds On This (learn these next):**
- `Floyd-Warshall` — extends Bellman-Ford to all-pairs shortest paths using a DP over intermediate nodes.
- `Difference Constraint Systems` — Bellman-Ford's most powerful application: solving systems of linear difference constraints.
- `Network Routing (BGP/RIP)` — distributed Bellman-Ford is the algorithm underlying distance-vector routing protocols.

**Alternatives / Comparisons:**
- `Dijkstra` — faster O((V+E) log V) but requires non-negative weights; use it when weights are non-negative.
- `SPFA` — Bellman-Ford with a queue; faster in practice but same worst-case complexity; less predictable runtime.
- `Johnson's Algorithm` — uses Bellman-Ford to re-weight edges (eliminating negatives), then runs Dijkstra from every source; gives all-pairs shortest paths in O(V² log V + VE).

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SSSP via repeated edge relaxation; handles│
│              │ negative weights and detects neg cycles   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shortest paths when negative edge weights │
│ SOLVES       │ make Dijkstra incorrect                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ V-1 passes suffice for simple paths;      │
│              │ V-th pass improvement = negative cycle    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Graph has negative edge weights, detect   │
│              │ arbitrage, solve difference constraints   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ All weights non-negative (use Dijkstra);  │
│              │ graph is very large and dense (O(VE))     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(VE) time (slower than Dijkstra) vs      │
│              │ ability to handle negative edges          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "V-1 rounds of negotiation; round V = the │
│              │  loop that never ends"                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Floyd-Warshall → Johnson's → Diff Constr. │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Bellman-Ford is described as a Dynamic Programming algorithm. Write the DP recurrence explicitly: let `dp[k][v]` be the length of the shortest path from source `s` to node `v` using at most `k` edges. Express `dp[k][v]` in terms of `dp[k-1]`. How does this recurrence relate to the Bellman-Ford outer loop? Why is `k = V-1` a sufficient upper bound on the number of edges in a shortest simple path?

**Q2.** In a financial graph where each edge weight is `-log(exchange_rate)`, a negative cycle corresponds to a profitable arbitrage opportunity (a sequence of currency exchanges that returns more than you started with). Bellman-Ford detects this negative cycle in O(VE). However, detecting a negative cycle is not the same as finding the *most profitable* arbitrage loop. Describe how you would modify Bellman-Ford to identify the specific cycle (sequence of currencies) that forms a negative cycle, not just report that one exists. What information must be tracked in the `parent[]` array, and how do you reconstruct the cycle path from the detection step?

