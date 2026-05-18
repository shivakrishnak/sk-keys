---
id: DSA-091
title: A-Star Search Algorithm
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-060, DSA-036
used_by: DSA-077
related: DSA-060, DSA-036
tags:
  - algorithms
  - a-star
  - heuristic
  - shortest-path
  - pathfinding
  - game-dev
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 91
permalink: /technical-mastery/dsa/a-star-search/
---

## TL;DR

A* finds the shortest path using a heuristic to guide
search toward the goal, exploring far fewer nodes than
Dijkstra - the algorithm behind game pathfinding and
GPS route guidance when destination is known.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-091 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, A*, heuristic, pathfinding |
| **Prerequisites** | DSA-060, DSA-036 |

---

### The Problem This Solves

Dijkstra from source to all nodes is O((V+E)logV). But
if we know the destination, why explore nodes in the
opposite direction? A* guides exploration toward the goal
using a heuristic (e.g., straight-line distance), visiting
far fewer nodes while guaranteeing optimality when the
heuristic is admissible (never over-estimates).

---

### Textbook Definition

A* is a best-first search that uses f(n) = g(n) + h(n)
where g(n) = cost from start to node n, h(n) = heuristic
estimate of cost from n to goal. Expands node with
minimum f value. If h is admissible (h(n) <= actual cost
to goal for all n), A* returns the optimal path.
If h=0, A* degenerates to Dijkstra.

---

### Understand It in 30 Seconds

Dijkstra spreads outward like a growing circle until it
reaches the goal. A* spreads like an ellipse - wide at
the source, narrowing toward the goal. The heuristic
is the "compass" that points toward the destination. Same
optimality guarantee, fewer nodes explored.

---

### First Principles

Dijkstra explores nodes in order of g(n) (true cost from
source). A* explores in order of f(n) = g(n) + h(n) where
h is optimistic about remaining cost. The admissibility
condition (h never over-estimates) ensures A* never skips
a node that could be on the optimal path: "if we're
optimistic about the rest, we still won't miss the best."

---

### Thought Experiment

You're driving from Boston to New York. Dijkstra: explore
all roads expanding outward from Boston (including roads
heading north to Maine!). A*: estimate remaining distance
using straight-line to NYC and prefer roads that head
south. You never explore north-bound roads unless a
southern route is completely blocked. Admissibility means
straight-line distance never exceeds driving distance -
true by definition for Euclidean distance.

---

### Mental Model / Analogy

A* is like a smart GPS vs a dumb GPS:
- Dijkstra = dumb GPS, explores all roads expanding from
  source outward (correct but slow)
- A* = smart GPS, knows destination direction and prefers
  roads heading that way (correct AND fast)
- Heuristic = the "as the crow flies" estimate
- Admissibility = that estimate is always optimistic
  (real road distance >= straight-line distance)

---

### Gradual Depth - Five Levels

**Level 1 (Child):** A* is like finding your way in a
maze by always trying the path that "looks like" it's
heading toward the exit.

**Level 2 (Student):** A* extends Dijkstra with a
heuristic. Instead of expanding nearest node, expand
the node with best (current cost + estimated remaining).

**Level 3 (Developer):** Priority queue on f = g + h.
Admissible h guarantees optimal path. Choice of h
determines exploration pattern: h=0 is Dijkstra,
h=perfect is oracle that explores only optimal path.

**Level 4 (Senior):** Memory-bounded A* variants:
IDA* (iterative deepening), SMA* (Simplified Memory-
Bounded A*) for large state spaces. Bi-directional A*
runs two A* instances from source and target to reduce
explored nodes to O(b^(d/2)). Google Maps uses a form
of contraction hierarchies + A*.

**Level 5 (Expert):** Weighted A* (WA*): f = g + w*h
where w > 1 sacrifices optimality for speed, finding
a path with cost at most w times optimal. Useful in
game AI where "good enough" path at 60fps is needed.
Jump Point Search (JPS) prunes A* neighbors on uniform
grids, reducing explored nodes 10-100x. Used in AAA
games for grid-based maps.

---

### How It Works

**Implementation:**

```java
// A* from source to target on weighted graph
// adj[u] = list of [v, weight], heuristic[v] = h(v)
int[] astar(int src, int target, List<int[]>[] adj,
            int[] h, int n) {
    int[] g = new int[n];
    Arrays.fill(g, Integer.MAX_VALUE);
    g[src] = 0;

    // min-heap on f = g + h: [f_value, node]
    PriorityQueue<int[]> pq = new PriorityQueue<>(
        Comparator.comparingInt(a -> a[0])
    );
    pq.offer(new int[]{h[src], src});

    int[] parent = new int[n];
    Arrays.fill(parent, -1);
    boolean[] visited = new boolean[n];

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int u = curr[1];
        if (visited[u]) continue;
        visited[u] = true;

        if (u == target) break;

        for (int[] edge : adj[u]) {
            int v = edge[0], w = edge[1];
            if (!visited[v] && g[u] + w < g[v]) {
                g[v] = g[u] + w;
                parent[v] = u;
                pq.offer(new int[]{g[v] + h[v], v});
            }
        }
    }
    return parent;
}
```

**Admissible heuristics for common problems:**

```
Grid (no diagonals) - Manhattan distance:
  h(n) = |n.x - goal.x| + |n.y - goal.y|
  Admissible: Manhattan = min steps without walls

Grid (with diagonals) - Chebyshev distance:
  h(n) = max(|n.x-goal.x|, |n.y-goal.y|)

Geographic routing - Euclidean distance:
  h(n) = sqrt((n.x-goal.x)^2 + (n.y-goal.y)^2)
  Admissible: straight-line <= road distance

h = 0: degenerates to Dijkstra (always admissible)
h = infinity: greedy best-first (fast but not optimal)
```

---

### Complete Picture - End-to-End Flow

```
Source S ---------> Target T
        \         /
         \  A*   /
          v     v
     Opens neighbors by f = g + h
     h = straight-line to T
     Explores fewer nodes on path S -> T

ASCII: Dijkstra vs A* explored nodes

Dijkstra: explores all (circles outward from S)
     S###T
     ######
     ######

A*: explores cone toward T
     S..T
     ..
     (fewer cells)
```

```mermaid
flowchart LR
    A[Start node S] --> B[Open list: sorted by f=g+h]
    B --> C{Pop min-f node u}
    C -->|u == target| D[Reconstruct path]
    C -->|u != target| E[For each neighbor v]
    E --> F{g+w < g[v]?}
    F -->|Yes| G[Update g[v], push v with f=g+h]
    F -->|No| C
    G --> C
```

---

### Comparison Table

| Property | BFS | Dijkstra | A* |
|---------|-----|----------|-----|
| Weighted edges | No | Yes | Yes |
| Direction aware | No | No | Yes |
| Nodes explored | All reachable | All | Guided subset |
| Optimal | Yes (unweighted) | Yes | Yes (admissible h) |
| Space | O(V) | O(V) | O(V) |
| Best for | Unweighted | Single-source all | Known source+dest |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "A* is always faster than Dijkstra" | Only when h is informative. With h=0, A* IS Dijkstra. On graphs with no structure (random weights), h provides no guidance |
| "Any heuristic makes A* optimal" | Only admissible h (never over-estimates) guarantees optimality. Inadmissible h finds a path but maybe not the shortest |
| "A* guarantees fewer node expansions" | With inadmissible h, A* can expand MORE nodes than Dijkstra if h causes incorrect pruning and revisits |

---

### Failure Modes & Diagnosis

**Failure 1: A* returns suboptimal path**
- Cause: Heuristic over-estimates (not admissible)
- Diagnosis: Run Dijkstra on same graph; if Dijkstra
  finds shorter path, h is inadmissible
- Fix: Prove h(n) <= actual_cost(n, goal) for all n.
  For grid: Manhattan distance proof by induction.

**Failure 2: A* slower than Dijkstra**
- Cause: h provides little to no guidance (near-zero h)
- Diagnosis: Check h(n) values - if most are 0 or very
  small relative to g values, the heuristic is weak
- Fix: Use a stronger admissible heuristic

**Failure 3: Security - adversarial inputs**
- Cause: Pathological graphs where h always points wrong
  (not admissible, or adversary controls edge weights)
- Fix: Validate edge weights >= 0, validate graph
  structure, use Dijkstra if graph is untrusted/dynamic

---

### Related Keywords

**Prerequisites:** DSA-060 (Dijkstra), DSA-036 (BFS)

**See also:** DSA-077 (DSA System Design), DSA-064 (MST)

**Applications:** Game pathfinding, GPS routing, robotics

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Time | O((V+E) log V) worst |
| Space | O(V) |
| Optimal when | h is admissible |
| h = 0 | Becomes Dijkstra |
| h = actual | Optimal (perfect oracle) |
| Java | PriorityQueue<int[]> on f=g+h |

**Three things to remember:**
1. f = g + h: actual cost + optimistic estimate
2. Admissible h means "never overestimates remaining cost"
3. Manhattan distance is admissible for grid (no diagonals)

**One-line interview answer:** "A* is Dijkstra with a
GPS - the heuristic guides search toward the goal,
reducing explored nodes while maintaining optimality."

---

### Transferable Wisdom

The A* insight transfers broadly: "guided search beats
blind search when you have domain knowledge." In ML,
beam search (language model decoding) is A*-inspired.
In constraint solving, arc consistency + forward checking
uses heuristics to guide variable ordering. In planning,
STRIPS/PDDL planners use heuristics derived from problem
structure. The f = g + h decomposition is fundamental:
"what I know" + "what I estimate" = "what to prioritize."

---

### The Surprising Truth

Google Maps does NOT use classic A*. It uses Contraction
Hierarchies (CH) - a preprocessing algorithm that pre-
computes shortcuts for high-traffic roads. During routing,
CH finds routes 1000x faster than A* on continental
road networks. A* is optimal for unknown graphs (games,
robotics) but for known, static graphs (maps), CH and
similar techniques dominate. Peter Hart (co-inventor of
A*) publicly stated that A* is used for real-time
pathfinding where the graph changes (game AI), not for
static road network routing.

---

### Mastery Checklist

- [ ] Implements A* from memory with priority queue on f
- [ ] Verifies heuristic admissibility formally
- [ ] Knows when to use A* vs Dijkstra vs BFS
- [ ] Understands bidirectional A* for large graphs
- [ ] Can derive Manhattan distance heuristic from scratch

---

### Think About This

1. Can you prove Manhattan distance is admissible for
   a grid without obstacles?

2. What happens to A* when the heuristic equals the
   actual remaining cost perfectly? How many nodes get
   expanded?

3. If you run A* on a weighted graph with negative edge
   weights (after Bellman-Ford confirms no negative
   cycles), is admissibility still sufficient for
   correctness?

**TYPE G - Generalization:** The f = g + h framework
is an instance of a broader principle: "combine known
information with estimated future information to make
decisions." Where else does this appear in computer
science? (Hint: Alpha-Beta pruning in game trees, beam
search in NLP, branch-and-bound in optimization.)

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between BFS,
Dijkstra, and A*?

> BFS: unweighted graphs, explores all nodes layer by
> layer (level order), guarantees minimum hop count.
> Dijkstra: weighted graphs (non-negative), explores
> nodes in order of minimum accumulated cost g(n).
> A*: weighted graphs with known goal, explores in order
> of f(n) = g(n) + h(n) where h guides toward goal.
> Key: BFS and Dijkstra don't know the destination
> direction; A* uses heuristic to guide exploration.

**Q2 (Medium):** How do you prove a heuristic is
admissible?

> For a heuristic h(n) to be admissible:
> h(n) <= actual_cost(n, goal) for all nodes n.
> 
> Manhattan distance on grid:
> - In a grid with unit costs and no diagonal moves, the
>   minimum steps from (x1,y1) to (x2,y2) is |x1-x2|
>   + |y1-y2| WITH NO OBSTACLES (best case).
> - With obstacles, the actual path can only be longer
>   or equal to this minimum.
> - Therefore h(n) = Manhattan distance <= actual cost.
> - This is an admissible lower bound. QED.
> 
> General proof strategy: show h(n) = some geometric or
> relaxed-problem distance that ignores constraints
> (obstacles, traffic). Relaxed solutions are always <=
> constrained solutions.

**Q3 (Hard):** Design a multi-target A* where you want
to find the shortest path from one source to any one
of k target nodes.

> Option 1: Run A* k times (source to each target).
> O(k * (V+E) log V). Simple but doesn't exploit
> shared computation.
> 
> Option 2: Reverse the problem. Start search from
> all k targets simultaneously (multi-source BFS-style).
> Create virtual super-target T* connected to all k
> targets with 0-weight edges. Run A* from source to T*.
> This explores the intersection of paths to all targets.
> 
> Heuristic for multi-target: h(n) = min over all
> targets t of h_t(n). This is admissible if each h_t
> is admissible and the min of admissible heuristics
> is admissible.
> 
> Real application: nearest facility search (find
> nearest hospital from current location among k
> hospitals). Google Maps uses this approach with
> precomputed distance tables.
