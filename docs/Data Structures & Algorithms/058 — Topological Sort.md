---
layout: default
title: "Topological Sort"
parent: "Data Structures & Algorithms"
nav_order: 58
permalink: /dsa/topological-sort/
number: "0058"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Graph, DFS, Queue / Deque
used_by: Build Systems, Task Scheduling, Course Prerequisites
related: DFS, BFS, Strongly Connected Components
tags:
  - algorithm
  - graph
  - intermediate
  - pattern
  - datastructure
---

# 058 — Topological Sort

⚡ TL;DR — Topological Sort orders nodes of a DAG so every directed edge points forward — essential for dependency resolution in build systems and task schedulers.

| #058 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Graph, DFS, Queue / Deque | |
| **Used by:** | Build Systems, Task Scheduling, Course Prerequisites | |
| **Related:** | DFS, BFS, Strongly Connected Components | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You have 10 Java modules: module A depends on B, B on C, C on D. When Maven builds these modules, it must compile D before C, C before B, B before A. Without an ordering algorithm, Maven would either compile modules in random order (failing when A tries to import B before B is compiled) or require the user to manually specify the correct build order.

THE BREAKING POINT:
Real dependency graphs have hundreds of modules with complex interdependencies. Human-specified build orders are error-prone and break whenever dependencies change. The system needs to automatically determine a valid execution order from the dependency graph.

THE INVENTION MOMENT:
A dependency graph has a crucial property: it must be a DAG (Directed Acyclic Graph) — a cycle would mean "A depends on B depends on A," which is unsatisfiable. Given a DAG, there always exists at least one ordering where every dependency comes before the thing depending on it. The algorithm to find this ordering is called **Topological Sort**, and it is exactly why build systems, task schedulers, and package managers work correctly.

### 📘 Textbook Definition

**Topological Sort** produces a linear ordering of the vertices of a Directed Acyclic Graph (DAG) such that for every directed edge `u → v`, vertex `u` appears before vertex `v` in the ordering. Topological Sort is only possible on DAGs — a cycle makes it impossible because cyclic dependencies have no valid ordering. Two standard algorithms produce a topological ordering: DFS-based (reverse finish order) running in `O(V+E)` and Kahn's algorithm (BFS-based in-degree processing) also in `O(V+E)`.

### ⏱️ Understand It in 30 Seconds

**One line:**
Arrange tasks so every task comes after all its prerequisites.

**One analogy:**
> Imagine dressing in the morning: you must put on socks before shoes, underwear before trousers. Topological sort is finding a valid dressing order — any order that respects the "X before Y" constraints. There may be multiple valid orders (you can put on your shirt before or after your trousers), but every valid order satisfies all constraints.

**One insight:**
A topological sort exists if and only if the graph has no cycles. This means topological sort *simultaneously* validates the dependency structure (cycle = error) and produces the correct execution order. Build systems use this duality: "is the dependency graph valid?" and "what order should we build?" are answered by the same algorithm.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The input must be a **DAG** — cycles make topological ordering impossible.
2. For every edge `u → v`, `u` must appear **before** `v` in the output ordering.
3. A DAG always has at least one **source** node (in-degree 0); removing a source reveals new source nodes — this produces Kahn's algorithm.

DERIVED DESIGN:
There are two standard derivations:

**DFS-based:** When DFS finishes a node (all its descendants processed), preprend it to the output. Nodes that finish last in DFS are the ones with no outgoing edges — they should appear last in the topological order. Prepending reverses this: the last-finishing node appears first in the reversed order. If any back edge is found during DFS, the graph has a cycle and topological sort is impossible.

**Kahn's algorithm (BFS-based):** Start with all nodes of in-degree 0 (no dependencies). Add them to a queue. Process queue: dequeue a node, add it to output, decrement in-degree of all its successors. If a successor's in-degree reaches 0, enqueue it. If the output contains fewer than V nodes at the end, the remaining nodes form a cycle.

**Why two algorithms?**
DFS-based is elegant and implicitly detects cycles. Kahn's is iterative (no stack overflow risk), explicitly detects cycles (output size < V), and produces the ordering level-by-level which naturally reveals parallelizable stages (all nodes in queue simultaneously can be processed in parallel in a build system).

THE TRADE-OFFS:
Gain: O(V+E) ordering of dependencies; simultaneous cycle detection.
Cost: Only applicable to DAGs; requires understanding the graph structure upfront.

### 🧪 Thought Experiment

SETUP:
Build system with 4 modules: A→B, A→C, B→D, C→D. A depends on B and C; both depend on D.

WHAT HAPPENS WITHOUT TOPOLOGICAL SORT:
Build order is arbitrary: maybe D, B, A, C. Building A before C fails because A requires C. The build error reports "C not found" with no hint about the correct order.

WHAT HAPPENS WITH TOPOLOGICAL SORT (Kahn's):
In-degrees: A=0, B=1 (from A), C=1 (from A), D=2 (from B and C).
Queue starts: [A] (only in-degree 0 node).
Process A → output [A] → decrement B (now 0), C (now 0). Queue: [B, C].
Process B → output [A, B] → decrement D (now 1). Queue: [C].
Process C → output [A, B, C] → decrement D (now 0). Queue: [D].
Process D → output [A, B, C, D].
Build in this order: succeeds because D is built last (after B and C).

THE INSIGHT:
The ordering A, B, C, D is not the only valid one — A, C, B, D is equally valid. Topological sort does not produce a unique ordering; it produces *a* valid ordering (or reports impossibility if a cycle exists). The non-uniqueness reveals which steps can be parallelized: B and C in the queue simultaneously means they can be built in parallel.

### 🧠 Mental Model / Analogy

> Topological sort is like ordering domino pieces before setting them up. You must place a domino before any domino it will knock over. Given the "will knock over" relationships, find an order to place them all so the chain will work exactly as designed. If two dominoes knock over each other, the setup is invalid — that's a cycle, and no valid placement order exists.

"Place domino X before Y" → edge X→Y means X must precede Y
"Finding placement order" → producing the topological ordering
"Two dominoes knock over each other" → cycle in the graph, topological sort impossible
"Pieces with no incoming arrows" → in-degree-0 nodes, start of Kahn's queue

Where this analogy breaks down: Real dominoes are physical — you always find some valid placement. In dependency graphs, cyclic dependencies are genuinely unsatisfiable, not just inconvenient — no placement order can satisfy the constraint.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Topological sort puts tasks in an order where every task comes after all the tasks it depends on. Like planning a recipe: you must chop vegetables before cooking them, and cook everything before serving.

**Level 2 — How to use it (junior developer):**
Use Kahn's algorithm: (1) compute in-degree for every node, (2) enqueue all nodes with in-degree 0, (3) while queue non-empty: dequeue u, add to output, decrement in-degree of u's successors, enqueue any that reach 0. If all V nodes appear in output, sorting succeeded. If output.size() < V, a cycle exists in the remaining nodes.

**Level 3 — How it works (mid-level engineer):**
DFS-based topological sort uses the finish-time property: the last node to finish in DFS has no outgoing edges — it must appear last in topological order. Collecting nodes in reverse finish order gives a valid topological ordering. The DFS-based approach is O(V+E) and naturally integrates cycle detection (any GRAY node reached = cycle = abort). Kahn's algorithm is preferred when you need to identify which tasks can run in parallel at each "wave" — all nodes in the queue simultaneously form a parallelizable batch.

**Level 4 — Why it was designed this way (senior/staff):**
Topological sort on DAGs is the algorithmic foundation for dependency resolution in all modern software build systems (Maven, Gradle, Make, Bazel) and package managers (npm, pip, cargo). The connection to linear extensions of partial orders is the mathematical foundation: a topological ordering is a linear extension of the partial order defined by the dependency relation. A DAG is "topologically sortable" iff its dependency relation is a strict partial order (irreflexive, asymmetric, transitive) — a cycle violates asymmetry. Kahn's algorithm produces the canonical "level-order" topological sort, which maps directly to parallel build stages: all nodes at depth d can be processed simultaneously by separate workers.

### ⚙️ How It Works (Mechanism)

**Kahn's Algorithm (BFS-based):**
```
┌────────────────────────────────────────────┐
│ Kahn's Topological Sort                    │
│                                            │
│  1. Compute in-degree for every node       │
│  2. Enqueue all nodes with in-degree = 0   │
│  3. While queue not empty:                 │
│     a. Dequeue node u                      │
│     b. Add u to output                     │
│     c. For each successor v of u:          │
│        in-degree[v] -= 1                   │
│        if in-degree[v] == 0:               │
│           enqueue v                        │
│  4. If output.size() < V:                  │
│     → CYCLE DETECTED (remaining nodes     │
│       form the cycle)                      │
└────────────────────────────────────────────┘
```

**DFS-based Algorithm:**
```
┌────────────────────────────────────────────┐
│ DFS Topological Sort                       │
│                                            │
│  result = empty deque                      │
│  For each unvisited node u:                │
│    dfs_topo(u):                            │
│      mark u GRAY (in-progress)             │
│      for each successor v:                 │
│        if v is GRAY → CYCLE!              │
│        if v is WHITE → dfs_topo(v)        │
│      mark u BLACK (done)                  │
│      result.addFirst(u) ← prepend!        │
│  Return result                             │
└────────────────────────────────────────────┘
```

**Difference in output:**
- Kahn's produces a breadth-first topological order (source nodes first, sinks last).
- DFS produces a depth-first topological order (nodes with long dependency chains may appear later).
- Both are valid topological orderings; neither is "more correct."

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Dependency specification (pom.xml, package.json)
→ Parse into directed graph (module → dependency)
→ Build adjacency list + in-degree map
→ [TOPOLOGICAL SORT ← YOU ARE HERE]
  → Kahn's: process sources wave-by-wave
→ Ordered build list (each wave parallelizable)
→ Execute tasks in order
→ All dependencies satisfied at each step
```

FAILURE PATH:
```
Circular dependency: A depends on B, B on A
→ Kahn's: queue empties with output.size() < V
→ Remaining nodes form the cycle: {A, B}
→ Report cycle to user: "Circular dependency:
  A → B → A"
→ Build fails with actionable error
```

WHAT CHANGES AT SCALE:
In monorepos with 10,000+ modules (Google's monorepo, Facebook's), topological sort is combined with dependency caching: the build system only rebuilds modules whose transitive dependencies changed. The topological order also determines the critical path — the longest dependency chain — which is the minimum build time with infinite parallelism.

### 💻 Code Example

**Example 1 — Kahn's algorithm:**
```java
List<Integer> topoSort(int n,
    int[][] edges) {
    List<List<Integer>> adj =
        new ArrayList<>();
    int[] inDegree = new int[n];
    for (int i = 0; i < n; i++)
        adj.add(new ArrayList<>());

    for (int[] e : edges) {
        adj.get(e[0]).add(e[1]);
        inDegree[e[1]]++;
    }

    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < n; i++)
        if (inDegree[i] == 0)
            queue.offer(i);

    List<Integer> result = new ArrayList<>();
    while (!queue.isEmpty()) {
        int u = queue.poll();
        result.add(u);
        for (int v : adj.get(u)) {
            if (--inDegree[v] == 0)
                queue.offer(v);
        }
    }

    if (result.size() != n)
        throw new RuntimeException(
            "Cycle detected!");
    return result;
}
```

**Example 2 — Course schedule (LeetCode 207 pattern):**
```java
boolean canFinish(int numCourses,
    int[][] prerequisites) {
    // prerequisites[i] = [course, prereq]
    // means: to take course, must take prereq first
    int[] inDegree = new int[numCourses];
    List<List<Integer>> adj = new ArrayList<>();
    for (int i=0; i<numCourses; i++)
        adj.add(new ArrayList<>());

    for (int[] pre : prerequisites) {
        // prereq → course (prereq must come first)
        adj.get(pre[1]).add(pre[0]);
        inDegree[pre[0]]++;
    }

    Queue<Integer> q = new LinkedList<>();
    for (int i=0; i<numCourses; i++)
        if (inDegree[i] == 0) q.offer(i);

    int count = 0;
    while (!q.isEmpty()) {
        int course = q.poll();
        count++;
        for (int next : adj.get(course))
            if (--inDegree[next] == 0)
                q.offer(next);
    }
    return count == numCourses; // false = cycle
}
```

**Example 3 — Parallel build waves:**
```java
// Returns list of waves; each wave can be
// executed in parallel
List<List<Integer>> parallelWaves(int n,
    int[][] edges) {
    int[] inDegree = new int[n];
    List<List<Integer>> adj = new ArrayList<>();
    for (int i = 0; i < n; i++)
        adj.add(new ArrayList<>());
    for (int[] e : edges) {
        adj.get(e[0]).add(e[1]);
        inDegree[e[1]]++;
    }

    List<List<Integer>> waves = new ArrayList<>();
    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < n; i++)
        if (inDegree[i] == 0) queue.offer(i);

    while (!queue.isEmpty()) {
        int size = queue.size();
        List<Integer> wave = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            int u = queue.poll();
            wave.add(u);
            for (int v : adj.get(u))
                if (--inDegree[v] == 0)
                    queue.offer(v);
        }
        waves.add(wave);
    }
    return waves; // each inner list = one parallel wave
}
```

### ⚖️ Comparison Table

| Algorithm | Style | Cycle Detection | Parallel Waves | Stack Risk | Best For |
|---|---|---|---|---|---|
| **Kahn's (BFS)** | Iterative | Yes (output.size() <V) | Natural (queue = wave) | None | Build systems, explicit cycle reporting |
| DFS finish-order | Recursive | Yes (GRAY node = cycle) | Not natural | Yes (deep graphs) | Elegant, integrated cycle detection |
| Iterative DFS | Iterative | Needs extra tracking | Not natural | None | Large graphs, production safety |

How to choose: Use Kahn's algorithm for production build systems (explicit cycle detection, parallel wave identification, no stack overflow risk). Use DFS-based for competitive programming or when you need SCC integration.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Topological sort produces a unique ordering | A DAG can have multiple valid topological orderings. The sort produces one valid ordering, not the only valid ordering |
| Any graph can be topologically sorted | Only DAGs can be topologically sorted. Any cycle makes topological ordering impossible — cyclic dependencies are fundamentally unsatisfiable |
| Kahn's output has fewer nodes than V means exactly one cycle | output.size() < V means one or more cycles exist. The remaining nodes in the graph (not in output) form the cyclic subgraph, but it may contain multiple cycles |
| BFS and Kahn's algorithm are not related | Kahn's is a BFS variant on the in-degree graph. The queue in Kahn's plays the role BFS's queue plays in graph traversal |
| Topological sort only works on dependency trees | Topological sort works on DAGs, which include diamond-shaped dependencies (multiple dependency chains converging on a single node) — not just trees |

### 🚨 Failure Modes & Diagnosis

**1. Cycle in dependency graph — infinite build or silent failure**

Symptom: Build system hangs, or reports confusing errors like "module not found" instead of "circular dependency."

Root Cause: Cyclic dependencies mean no valid ordering exists. A naive build system might cycle indefinitely or attempt to build in an arbitrary order that always violates some dependency.

Diagnostic:
```bash
# Maven cycle detection:
mvn dependency:tree | grep -i "cycle"
# For npm:
npm ls --depth=0 2>&1 | grep "cycle"
# Manual: run Kahn's and report remaining nodes
```

Fix: Break the cycle by extracting the shared code into a new module that both cyclic modules depend on, not each other.

Prevention: Run topological sort as part of the build validation step before any compilation begins.

---

**2. Multiple valid orderings causing non-deterministic builds**

Symptom: Build order changes between runs; cache invalidation becomes unreliable; different engineers get different orderings.

Root Cause: Topological sort is not unique — many valid orderings exist. Different queue insertion orders (e.g., HashMap iteration order) produce different valid orderings.

Diagnostic:
```bash
# Compare two build orderings:
mvn --batch-mode clean install -T 1 > order1.txt
mvn --batch-mode clean install -T 1 > order2.txt
diff order1.txt order2.txt
```

Fix: Use a deterministic tie-breaking rule in the priority queue (e.g., alphabetical or numeric ordering of node IDs). Replace `Queue` with `PriorityQueue` sorted by node ID.

Prevention: Always use a sorted queue (lexicographic or numeric) in build system topological sorts for reproducible builds.

---

**3. Missing edges producing incorrect ordering**

Symptom: Build fails because module A compiled before its dependency B.

Root Cause: A dependency edge "A depends on B" was missing from the graph (e.g., an implicit transitive dependency not declared explicitly, or a code-level dependency not captured in the build manifest).

Diagnostic:
```bash
# Maven: find undeclared dependencies
mvn dependency:analyze
# Output: [WARNING] Used undeclared dependencies
```

Fix: Declare all dependencies explicitly. Use dependency analyzers to detect undeclared usages.

Prevention: Enforce that all imports must have corresponding explicit dependency declarations.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Graph` — topological sort operates on directed graphs; understand directed edges and adjacency lists.
- `DFS` — the DFS-based topological sort uses finish-time ordering of DFS traversal.
- `Queue / Deque` — Kahn's algorithm uses a FIFO queue to process nodes level-by-level.

**Builds On This (learn these next):**
- `Strongly Connected Components` — after topological sort identifies a DAG order, SCC algorithms decompose graphs with cycles into DAGs of SCCs.
- `Critical Path Method` — topological sort underlies critical path analysis in project scheduling: the longest path sets the minimum completion time.
- `Build Systems (Make, Maven, Gradle)` — topological sort is the core algorithm in every dependency-aware build system.

**Alternatives / Comparisons:**
- `DFS` — DFS can produce a topological sort via reverse finish order; Kahn's is preferred for explicit cycle detection and parallel wave extraction.
- `BFS` — Kahn's algorithm IS BFS applied to the in-degree graph; pure BFS without in-degree tracking cannot produce a topological ordering.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Linear ordering of a DAG where every edge │
│              │ points "forward" in the order             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dependency resolution: what order to      │
│ SOLVES       │ build/execute when tasks have prereqs     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Only possible on DAGs; cycle = impossible  │
│              │ constraint; Kahn's detects cycle explicitly│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Build systems, task schedulers, course    │
│              │ prerequisites, package managers           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Graph has cycles — break cycles first or  │
│              │ report error to user                      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(V+E) time; only for DAGs;               │
│              │ ordering not unique                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every dependency before the thing that   │
│              │  depends on it"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strongly Connected Components → Critical  │
│              │ Path → Build Systems                      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** In a build system with 1000 modules, Kahn's topological sort produces waves of [100, 200, 400, 300] modules respectively (wave 1 has 100 independent modules, wave 2 has 200 that only depend on wave 1, etc.). The critical path is 4 waves long. You have 50 parallel build workers. What is the minimum build time in terms of the per-module build duration T? Now consider: if module M in wave 2 takes 10T (ten times longer than average), how does this change the critical path, and what is the new minimum build time?

**Q2.** Kahn's algorithm detects cycles by checking whether `output.size() < V` after the queue empties. But it does not tell you which nodes are in the cycle — only that a cycle exists. Design an algorithm that, given the remaining un-processed nodes after Kahn's terminates early, identifies and reports the exact cycle (list of nodes forming the shortest cycle). What is the time complexity of your cycle-identification step?

