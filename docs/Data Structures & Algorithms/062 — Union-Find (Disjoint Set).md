---
layout: default
title: "Union-Find (Disjoint Set)"
parent: "Data Structures & Algorithms"
nav_order: 62
permalink: /dsa/union-find-disjoint-set/
number: "0062"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Graph, Arrays
used_by: Kruskal MST, Connected Components, Cycle Detection in Undirected Graphs
related: BFS, DFS, Kruskal / Prim
tags:
  - datastructure
  - graph
  - intermediate
  - algorithm
  - pattern
---

# 062 — Union-Find (Disjoint Set)

⚡ TL;DR — Union-Find tracks which elements belong to the same group using near-O(1) amortised operations, making it the fastest way to merge groups and check connectivity at scale.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #062         │ Category: Data Structures & Algorithms │ Difficulty: ★★☆        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Graph, Arrays                          │                        │
│ Used by:     │ Kruskal MST, Connected Components,     │                        │
│              │ Cycle Detection (undirected graphs)    │                        │
│ Related:     │ BFS, DFS, Kruskal / Prim               │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a network monitoring system. As links come online one-by-one, you need to know: "Are server A and server B now in the same connected cluster?" Using BFS each time would cost O(V+E) per query. With 1 million servers and 10 million link additions, that's 10 trillion operations.

THE BREAKING POINT:
Maintaining and querying connected components dynamically — as edges are added one by one — is prohibitively expensive with standard graph traversal. Re-running BFS or DFS after every edge addition does not scale.

THE INVENTION MOMENT:
Represent each connected component as a tree with a designated root (representative). Store only `parent[i]` — the parent of element `i` in its tree. "Find" the representative by walking to the root. "Union" two elements by merging their trees (link one root to the other). With two optimisations — **path compression** (flatten the tree on every find) and **union by rank** (always attach smaller tree under larger) — the amortised cost per operation becomes nearly O(1): formally O(α(N)) where α is the inverse Ackermann function, effectively constant for all practical N. This is exactly why **Union-Find** was created.

### 📘 Textbook Definition

**Union-Find (Disjoint Set Union / DSU)** is a data structure that maintains a partition of a set into disjoint subsets, supporting two operations: `find(x)` returns the representative (root) of x's subset, and `union(x, y)` merges the subsets containing x and y. With **path compression** and **union by rank** (or size), both operations run in O(α(N)) amortised time, where α is the inverse Ackermann function — practically constant for all real inputs. Supports N elements and Q queries in O((N+Q)α(N)) total time.

### ⏱️ Understand It in 30 Seconds

**One line:**
Track which items are in the same group with nearly-instant merge and query operations.

**One analogy:**
> Each person in a company belongs to a team. To find which team someone is on, ask their manager, then their manager's manager, until you reach the CEO (team representative). To merge two teams, make one CEO report to the other. Path compression means everyone you spoke to on the way now reports directly to the CEO — making future queries instant.

**One insight:**
The magic of Union-Find is that path compression and union by rank together reduce a potentially linear-depth tree to nearly flat over a series of operations. The inverse Ackermann function grows so slowly (α(10^80) = 4) that this is effectively constant time. This combination is a rare example of a data structure that is simple to code yet achieves near-optimal theoretical bounds through two independently simple ideas.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Every element `x` has a `parent[x]`. If `parent[x] == x`, then `x` is the root (representative) of its set.
2. `find(x)` returns the root of x's tree by following `parent` pointers until `parent[x] == x`.
3. `union(x, y)` merges the sets by setting the root of one tree as the child of the root of the other.

DERIVED DESIGN:
Without optimisations, trees can degenerate to chains (O(N) find). Two complementary optimisations prevent this:

**Path Compression:**
During `find(x)`, after reaching the root, walk back along the path and set `parent[i] = root` for every node visited. Future finds on any of those nodes go directly to root in O(1).

**Union by Rank (or Size):**
When merging two trees, always attach the smaller tree under the larger. This bounds tree height at O(log N) without compression, and combined with compression gives O(α(N)).

```
Example: union by rank
  rank[A]=2, rank[B]=1
  union(A,B): B attaches under A (smaller rank)
  rank[A] stays 2 — no change needed

Example: path compression on find(5)
  5 → 3 → 1 → root
  After find: parent[5]=root, parent[3]=root
  Next find(5): goes directly to root
```

THE TRADE-OFFS:
Gain: O(α(N)) ≈ O(1) amortised per operation; O(N) space.
Cost: Does not support split (un-union) operations; only works for offline connectivity queries (edges are added, not removed). For edge removal, more complex structures (Link-Cut Trees) are needed.

### 🧪 Thought Experiment

SETUP:
5 nodes: {0,1,2,3,4}, initially all in separate sets. Perform: union(0,1), union(2,3), union(0,2), then ask: find(4) and find(1).

WITHOUT UNION-FIND (list-based tracking):
Maintain a list of sets. union(0,1) merges lists: [{0,1},{2},{3},{4}]. union(2,3): [{0,1},{2,3},{4}]. union(0,2): merge {0,1} and {2,3}: [{0,1,2,3},{4}]. find(1): scan all sets, return set containing 1. O(N) per operation.

WITH UNION-FIND:
Initial: parent=[0,1,2,3,4], rank=[0,0,0,0,0].
union(0,1): root(0)=0, root(1)=1. Attach 1 under 0. parent=[0,0,2,3,4], rank=[1,0,0,0,0].
union(2,3): root(2)=2, root(3)=3. Attach 3 under 2. parent=[0,0,2,2,4], rank=[1,0,1,0,0].
union(0,2): root(0)=0, root(2)=2. Both rank 1. Attach 2 under 0, rank[0]++. parent=[0,0,0,2,4], rank=[2,0,1,0,0].
find(1): 1→0 (root). O(1).
find(4): 4→4 (root of its own component). O(1).

THE INSIGHT:
Union-Find tracks connectivity with O(1) per operation after optimisations, whereas general list/set merging takes O(N). The tree with a path-compressed root structure is the minimal representation that achieves this — no simpler solution exists.

### 🧠 Mental Model / Analogy

> Union-Find is like a corporate hierarchy where each department has a CEO. To check if two people work for the same company, ask each: "who's your CEO?" If they have the same CEO, they're in the same company. When two companies merge, one CEO becomes the boss of the other. Over time, everyone learns to call the top CEO directly (path compression) instead of going through a chain of managers.

"Find: who's your CEO?" → find(x) = traverse parent[] to root
"Same CEO = same company" → find(x)==find(y) = same component
"Merger: one CEO reports to other" → union: link one root under the other
"Everyone calls CEO directly" → path compression flattens the tree

Where this analogy breaks down: Real companies don't instantly update everyone's "CEO" pointer when merging. Path compression is purely algorithmic — it happens automatically during each find operation, with no explicit restructuring step needed.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Union-Find quickly answers "are these two things connected?" and "connect these two things." It is a grouping tracker — think of sorting people into teams where you want to instantly check if two people are on the same team after any number of merges.

**Level 2 — How to use it (junior developer):**
Create `int[] parent` and `int[] rank`, initialised to `parent[i]=i`, `rank[i]=0`. `find(x)`: if `parent[x]==x`, return x; else return `parent[x] = find(parent[x])` (path compression). `union(x,y)`: if `find(x) != find(y)`, attach smaller rank under larger rank. Check connectivity: `find(x) == find(y)`. Count components: track `components--` in union when actually merging.

**Level 3 — How it works (mid-level engineer):**
The amortised complexity proof of O(α(N)) uses the "weighted union lemma": trees always have at most O(log N) height after union-by-rank without compression. Path compression further flattens these trees in amortised O(α(N)) per operation via the potential argument. The inverse Ackermann function arises because the combined effect of compression and rank creates a partition of nodes into "groups" (by rank) where the total work across all finds is bounded by a sum involving a tower-of-powers function.

**Level 4 — Why it was designed this way (senior/staff):**
Union-Find is the canonical example of an "online" dynamic connectivity algorithm for acyclically-growing graphs (edges only added, never removed). The O(α(N)) bound was proven tight by Tarjan (1975) — no comparison-based union-find can do better. For fully dynamic connectivity (edges added AND removed), the best known structure is the HDT (Holm-de Lichtenberg-Thorup) tree, running in O(log²N) per operation. Union-Find's simplicity makes it the default for Kruskal's MST and related algorithms where edges are processed once in sorted order without deletion.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Union-Find Internal Structure              │
│                                            │
│  parent[]:  parent[i] = i means i is root  │
│  rank[]:    upper bound on subtree height  │
│                                            │
│  Initial (5 nodes):                        │
│    parent = [0, 1, 2, 3, 4]               │
│    rank   = [0, 0, 0, 0, 0]               │
│                                            │
│  After union(0,1), union(2,3):             │
│    parent = [0, 0, 2, 2, 4]               │
│         0    2    4                        │
│         |    |                             │
│         1    3                             │
│                                            │
│  Path compression during find(1):          │
│    1→0 (root). parent[1]=0 (already flat)  │
│                                            │
│  After union(0,2) (both rank 1):           │
│    parent = [0, 0, 0, 2, 4], rank[0]=2    │
│              0                             │
│             / \                            │
│            1   2                           │
│                |                           │
│                3                           │
└────────────────────────────────────────────┘
```

**find with path compression:**
```java
int find(int x) {
    if (parent[x] != x)
        parent[x] = find(parent[x]); // compress
    return parent[x];
}
```

**union by rank:**
```java
boolean union(int x, int y) {
    int rx = find(x), ry = find(y);
    if (rx == ry) return false; // already same set
    if (rank[rx] < rank[ry]) {
        int tmp = rx; rx = ry; ry = tmp;
    }
    // rx has >= rank; attach ry under rx
    parent[ry] = rx;
    if (rank[rx] == rank[ry]) rank[rx]++;
    components--;
    return true; // merged
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
N elements, M union/find queries
→ Initialise parent[i]=i, rank[i]=0
→ For each union(x,y): [UNION-FIND ← YOU ARE HERE]
  → find(x), find(y)
  → If different roots: merge by rank
  → Decrement component count
→ For each connected(x,y): find(x)==find(y)
→ Final component count available at any time
```

FAILURE PATH:
```
Detect cycle in undirected graph (Kruskal):
edge (u,v) arrives → find(u)==find(v)
→ They are already in same component
→ Adding this edge creates a cycle
→ Skip the edge (Kruskal: don't add to MST)
```

WHAT CHANGES AT SCALE:
For N=10⁹ elements, the `parent[]` and `rank[]` arrays use 8 GB of memory — infeasible. Solutions: use a HashMap for sparse union-find (only store elements that have been referenced); use union-find on a compressed ID space (map original IDs to sequential integers). For distributed systems, union-find cannot be run naively in parallel — concurrent updates to `parent[]` require locks. Parallel union-find algorithms use CAS (Compare-And-Swap) operations to merge components in parallel with O(log N × α(N)) amortised time.

### 💻 Code Example

**Example 1 — Complete Union-Find implementation:**
```java
class UnionFind {
    private int[] parent;
    private int[] rank;
    private int components;

    UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        components = n;
        for (int i = 0; i < n; i++)
            parent[i] = i; // each is its own root
    }

    // Path compression (recursive)
    int find(int x) {
        if (parent[x] != x)
            parent[x] = find(parent[x]);
        return parent[x];
    }

    // Iterative path compression (no stack risk)
    int findIterative(int x) {
        int root = x;
        while (parent[root] != root)
            root = parent[root];
        // Compress: all nodes on path → root
        while (parent[x] != root) {
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    boolean union(int x, int y) {
        int rx = find(x), ry = find(y);
        if (rx == ry) return false;
        if (rank[rx] < rank[ry]) {
            int temp = rx; rx = ry; ry = temp;
        }
        parent[ry] = rx;
        if (rank[rx] == rank[ry]) rank[rx]++;
        components--;
        return true;
    }

    boolean connected(int x, int y) {
        return find(x) == find(y);
    }

    int getComponents() { return components; }
}
```

**Example 2 — Cycle detection in undirected graph:**
```java
boolean hasCycle(int n, int[][] edges) {
    UnionFind uf = new UnionFind(n);
    for (int[] edge : edges) {
        // If u and v already connected, adding
        // this edge creates a cycle
        if (!uf.union(edge[0], edge[1]))
            return true; // cycle detected
    }
    return false;
}
```

**Example 3 — Number of connected components:**
```java
int countComponents(int n, int[][] edges) {
    UnionFind uf = new UnionFind(n);
    for (int[] edge : edges)
        uf.union(edge[0], edge[1]);
    return uf.getComponents();
}

// Online (incremental) connectivity queries:
UnionFind uf = new UnionFind(n);
for (int[] event : edgeStream) {
    uf.union(event[0], event[1]);
    // Query connectivity after each edge:
    if (uf.connected(src, dst))
        System.out.println("Now connected!");
}
```

### ⚖️ Comparison Table

| Approach | Find | Union | Space | Dynamic (add edge) | Dynamic (remove edge) |
|---|---|---|---|---|---|
| **Union-Find (path+rank)** | O(α(N)) | O(α(N)) | O(N) | Yes | No |
| BFS/DFS per query | O(V+E) | N/A | O(V+E) | Re-run each time | Yes (rebuild) |
| Adjacency matrix | O(V) | O(1) | O(V²) | O(1) update | O(1) update |
| Link-Cut Tree | O(log N) | O(log N) | O(N) | Yes | Yes |

How to choose: Use Union-Find when edges are only added (not removed) and you need fast online connectivity queries. Use BFS/DFS for one-time queries. Use Link-Cut Trees when edges can also be removed.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Union-Find supports edge deletion | Standard Union-Find only supports edge addition. Removing an edge (un-union) requires rebuilding the structure or using more complex data structures like Link-Cut Trees |
| Path compression changes the logical grouping | Path compression only flattens the tree structure (parent pointers), not the logical grouping. find(x) always returns the same root before and after compression |
| Union-by-rank and union-by-size are equivalent | Both give O(log N) tree height and O(α(N)) amortised find, but union-by-size provides tighter constants in practice. The choice rarely matters in competitive programming but can matter in high-performance C++ |
| find(x)==find(y) is O(1) | find(x) is O(α(N)) amortised — nearly O(1), but not strictly O(1) in the worst case for any single find. Over N operations, the total cost is O(Nα(N)) |
| Union-Find detects cycles in directed graphs | Union-Find detects cycles in undirected graphs (via "both endpoints already in same component" check). For directed graph cycle detection, use DFS with three-color marking instead |

### 🚨 Failure Modes & Diagnosis

**1. Using union-find without path compression (O(N) degeneration)**

Symptom: Union-find operations slow to O(N) as N grows; profiler shows `find()` visiting many nodes.

Root Cause: Without path compression, repeatedly unioning elements in a chain (0→1→2→3→...→N) creates a tree of depth N. Every `find(0)` traverses N nodes.

Diagnostic:
```java
// Measure tree depth:
int depth(int x) {
    int d = 0;
    while (parent[x] != x) { x=parent[x]; d++; }
    return d;
}
int maxDepth = IntStream.range(0,n)
    .map(this::depth).max().getAsInt();
System.out.println("Max tree depth: " + maxDepth);
// Should be ~O(log N) with union-by-rank,
// ~O(1) amortised with path compression
```

Fix: Add path compression to `find()`. Add union-by-rank to `union()`. Both are one-line additions.

Prevention: Never implement Union-Find without both optimisations. They are always required.

---

**2. Applying Union-Find to directed graphs for cycle detection**

Symptom: Union-Find reports "no cycle" for a directed graph with a cycle (e.g., A→B→C→A declared as undirected). Or reports a false cycle.

Root Cause: Union-Find models undirected connectivity. In directed graphs, A→B means A can reach B but not vice versa. Union-Find treats edges as bidirectional, merging A and B regardless of direction — this is semantically incorrect for directed cycle detection.

Diagnostic:
```java
// Test: directed chain 0→1→2, no cycle
// Undirected UF would see no cycle here too
// Test: directed 0→1, 1→2, 2→0 = cycle
// DFS detects this; UF also merges all into
// one component — but cannot distinguish
// directed vs undirected cycles
```

Fix: Use DFS with three-color marking (WHITE/GRAY/BLACK) for directed graph cycle detection.

Prevention: Document clearly: "Union-Find cycle detection is for undirected graphs only."

---

**3. Integer overflow in rank-based union (rare edge case)**

Symptom: After many operations on large N, rank[] values overflow `int` bounds (requires N ~= 2^31, virtually impossible in practice).

Root Cause: Rank doubles at most O(log N) times; for int, this is limited to rank ≤ 31 for N ≤ 2^32. Practically never overflows within real problem sizes.

Diagnostic: This is a theoretical failure mode only. If building a library for extremely large N, use rank capped at log₂(MAX_INT) = 31.

Fix: Cap rank at 31 (`if (rank[rx] < 31) rank[rx]++`). Correctness is unaffected — rank only needs to distinguish "which tree is taller."

Prevention: Not a practical concern for N ≤ 10⁹; document theoretically.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — Union-Find models graph connectivity; understand nodes, edges, and connected components.
- `Arrays` — the `parent[]` and `rank[]` arrays are the entire data structure; understand array indexing.

**Builds On This (learn these next):**
- `Kruskal / Prim` — Kruskal's MST algorithm processes edges in weight order, using Union-Find to detect whether adding an edge would create a cycle.
- `Connected Components` — Union-Find provides the most efficient solution for online connected component tracking.
- `Network Dynamic Connectivity` — extends Union-Find concepts to edge-deletion scenarios using advanced structures.

**Alternatives / Comparisons:**
- `BFS` — can find connected components in O(V+E) but requires re-running for each query; not suitable for dynamic edge insertion.
- `DFS` — same limitations as BFS for dynamic connectivity; use DFS for directed cycle detection where Union-Find is inappropriate.
- `Link-Cut Trees` — supports both edge insertion and deletion in O(log N); use when edges can be removed.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Disjoint set data structure tracking      │
│              │ which elements are in the same group      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dynamic connectivity: "are these two      │
│ SOLVES       │ nodes connected?" after each edge add     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Path compression + union-by-rank gives    │
│              │ O(α(N)) ≈ O(1) per operation in practice  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Online connectivity, Kruskal MST, cycle   │
│              │ detection in undirected graphs            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Edges are removed (use Link-Cut Trees);   │
│              │ directed graph cycle detection (use DFS)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(α(N)) time, O(N) space;                 │
│              │ no edge deletion support                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two root operations: find your CEO,      │
│              │  merge two companies"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Kruskal/Prim → Minimum Spanning Tree →    │
│              │ Network Connectivity                      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Consider a Union-Find with N=8 elements where the following union operations are performed in sequence: union(0,1), union(2,3), union(4,5), union(6,7), union(0,2), union(4,6), union(0,4). After all unions, what does the tree look like with union-by-rank? Now perform find(7): trace each step of path compression. What does the tree look like after find(7)? How many parent pointer updates occurred, and what is the amortised significance of those updates for future queries?

**Q2.** Union-Find only supports edge insertion, not deletion. Suppose you need an "offline" dynamic connectivity algorithm where you are given all edge insertions and deletions upfront (before any queries). How could you use Union-Find as a building block — perhaps with a divide-and-conquer approach — to answer "were nodes u and v connected at time T?" queries offline? What is the time complexity of this approach, and how does it compare to the online case where deletions are not known in advance?

