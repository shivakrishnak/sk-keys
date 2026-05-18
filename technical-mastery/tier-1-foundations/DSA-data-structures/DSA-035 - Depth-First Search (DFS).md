---
id: DSA-035
title: Depth-First Search (DFS)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-018, DSA-026, DSA-034
used_by: DSA-064, DSA-064, DSA-069
related: DSA-036, DSA-039, DSA-064, DSA-069
tags:
  - algorithms
  - graph
  - dfs
  - depth-first
  - traversal
  - backtracking
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/dsa/depth-first-search/
---

## TL;DR

DFS explores as far as possible down each branch before
backtracking - O(V+E) on graphs, the foundation of cycle
detection, topological sort, connected components, and
backtracking algorithms.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-035 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, graph, DFS, traversal |
| **Prerequisites** | DSA-018, DSA-026, DSA-034 |

---

### The Problem This Solves

Given a graph, how do you visit all reachable nodes? How do
you detect cycles? How do you find if a path exists between
two nodes? DFS is the fundamental algorithm for all of these
- explore deep, backtrack, explore next branch.

---

### Textbook Definition

Depth-First Search traverses a graph by starting at a source
vertex, exploring as far as possible along each branch before
backtracking. Uses a stack (either explicit or recursive call
stack). Time: O(V + E) for adjacency list representation.
Space: O(V) for visited tracking + O(depth) for stack.

---

### Understand It in 30 Seconds

```
Graph:  A - B - D
        |   |
        C - E

DFS from A:
Visit A → go to B → go to D (dead end) → backtrack to B
→ go to E → go to C (already visited) → backtrack to A
→ go to C (already visited)

Order visited: A, B, D, E, C
```

---

### How It Works

**Recursive DFS:**

```java
void dfs(Map<Integer, List<Integer>> graph,
         int node, Set<Integer> visited) {
    if (visited.contains(node)) return;
    visited.add(node);
    process(node);
    for (int neighbor : graph.getOrDefault(node, List.of())) {
        dfs(graph, neighbor, visited);
    }
}
// Call: dfs(graph, startNode, new HashSet<>())
// Time: O(V + E),  Space: O(V) visited + O(depth) stack
```

**Iterative DFS (explicit stack):**

```java
void dfsIterative(Map<Integer, List<Integer>> graph,
                  int start) {
    Set<Integer> visited = new HashSet<>();
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(start);

    while (!stack.isEmpty()) {
        int node = stack.pop();
        if (visited.contains(node)) continue;
        visited.add(node);
        process(node);
        for (int neighbor : graph.getOrDefault(node, List.of())) {
            if (!visited.contains(neighbor))
                stack.push(neighbor);
        }
    }
}
```

**DFS for cycle detection (directed graph):**

```java
// 3 states: UNVISITED, IN_PROGRESS (on current path), DONE
enum State { UNVISITED, IN_PROGRESS, DONE }

boolean hasCycle(Map<Integer, List<Integer>> graph,
                 int node, Map<Integer, State> state) {
    state.put(node, State.IN_PROGRESS);
    for (int neighbor : graph.getOrDefault(node, List.of())) {
        State s = state.getOrDefault(neighbor, State.UNVISITED);
        if (s == State.IN_PROGRESS) return true; // back edge!
        if (s == State.UNVISITED && hasCycle(graph, neighbor, state))
            return true;
    }
    state.put(node, State.DONE);
    return false;
}
```

---

### Comparison Table

| Property | DFS | BFS |
|---------|-----|-----|
| Data structure | Stack (recursion) | Queue |
| Explores | Deep first | Shallow first |
| Space | O(max depth) | O(max width) |
| Shortest path | No | Yes (unweighted) |
| Cycle detection | Yes | Yes |
| Topological sort | Yes (post-order) | Yes (Kahn's) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "DFS finds shortest paths" | DFS finds a path, not the shortest; use BFS for shortest path in unweighted graphs |
| "Recursive DFS is always fine" | For graphs with depth 10,000+, recursive DFS causes StackOverflowError; use iterative |
| "DFS visited array is optional" | Without visited tracking, DFS will loop forever on cycles |

---

### Failure Modes & Diagnosis

**Failure: Infinite loop in DFS on cyclic graph**
- Cause: Forgot to mark nodes as visited before recursing
- Fix: Mark visited BEFORE recursing (not after), to prevent
  re-entering the same node during the current traversal

---

### Quick Reference Card

| Use DFS for | Reason |
|------------|--------|
| Cycle detection | Back edge = cycle |
| Topological sort | Post-order of DFS |
| Connected components | DFS from each unvisited node |
| Path exists A → B | DFS from A, check if B visited |
| Backtracking (N-Queens etc) | DFS + undo on backtrack |

---

### Mastery Checklist

- [ ] Can implement recursive and iterative DFS
- [ ] Can use DFS for cycle detection with 3-state coloring
- [ ] Knows DFS does not find shortest path (use BFS)
- [ ] Can identify when iterative DFS is needed
      (deep graphs, no StackOverflow risk)

---

### Interview Deep-Dive

**Q1 (Medium):** How do you detect a cycle in a directed
graph using DFS?

> Use three states: UNVISITED, IN_PROGRESS, DONE.
> Start DFS from each UNVISITED node. Mark it IN_PROGRESS
> before recursing into neighbors. If you reach a neighbor
> that is IN_PROGRESS, you found a back edge = cycle.
> When done processing a node, mark it DONE. DONE means
> no cycle was found through that node.
> Time: O(V + E). This is the coloring algorithm used in
> dependency graph cycle detection (e.g., circular Maven
> dependencies, circular Spring bean injection).
