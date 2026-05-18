---
id: DSA-063
title: Topological Sort
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-018, DSA-035, DSA-036
used_by: DSA-064, DSA-077
related: DSA-035, DSA-052, DSA-064
tags:
  - algorithms
  - topological-sort
  - dag
  - dependency-resolution
  - o-v-e
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 63
permalink: /technical-mastery/dsa/topological-sort/
---

## TL;DR

Topological Sort orders nodes of a DAG so every edge
points forward - the algorithm behind build systems,
dependency resolution, and compiler scheduling.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-063 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, topological-sort, DAG, dependencies |
| **Prerequisites** | DSA-018, DSA-035, DSA-036 |

---

### The Problem This Solves

"In what order should we compile modules so that every
dependency is compiled before the modules that use it?"
This is dependency ordering on a DAG (Directed Acyclic
Graph). Topological Sort gives a valid linear ordering
in O(V+E). If a cycle exists, no valid ordering exists
(circular dependency - detected by the algorithm).

---

### Textbook Definition

A topological ordering of a DAG is a linear sequence of
nodes where for every directed edge (u→v), u appears
before v. Only valid for DAGs (directed acyclic graphs).
Two algorithms:
1. Kahn's Algorithm (BFS-based): repeatedly removes
   nodes with in-degree 0
2. DFS-based: DFS post-order with a stack

Time: O(V+E). Space: O(V+E).

---

### How It Works

**Kahn's Algorithm (BFS-based):**

```java
List<Integer> topologicalSort(int n, List<List<Integer>> adj) {
    int[] inDegree = new int[n];
    for (int u = 0; u < n; u++)
        for (int v : adj.get(u)) inDegree[v]++;

    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < n; i++)
        if (inDegree[i] == 0) queue.offer(i);

    List<Integer> result = new ArrayList<>();
    while (!queue.isEmpty()) {
        int u = queue.poll();
        result.add(u);
        for (int v : adj.get(u)) {
            inDegree[v]--;
            if (inDegree[v] == 0) queue.offer(v);
        }
    }

    // Cycle detected if not all nodes processed
    if (result.size() != n)
        throw new RuntimeException("Cycle detected");
    return result;
}
```

**DFS-based approach:**

```java
void dfsTopoSort(int u, boolean[] visited,
                 Deque<Integer> stack,
                 List<List<Integer>> adj) {
    visited[u] = true;
    for (int v : adj.get(u))
        if (!visited[v])
            dfsTopoSort(v, visited, stack, adj);
    stack.push(u); // add AFTER visiting all descendants
}
// Post-order push → when popped, all dependencies come first
```

**Build system analogy:**

```
Modules: A depends on B, C depends on A and B

DAG:  B → A → C
          ↑
          B ←────── already handled

Valid orderings: B, A, C  (only one valid order here)
Kahn: start with B (in-degree 0) → process A (in-degree
      becomes 0) → process C.
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Topological sort is unique" | Multiple valid orderings exist when nodes have equal in-degree 0; the choice affects output but not correctness |
| "Topological sort works on any graph" | ONLY for DAGs; any cycle = no valid ordering; Kahn's detects this by checking result.size() != V |

---

### Failure Modes & Diagnosis

**Failure: Build system hangs or reports "cannot build"**
- Cause: Circular dependency between modules creates a
  cycle; topological sort cannot complete
- Diagnosis: If Kahn's result.size() < V, the missing
  nodes form the cycle; report them to the developer
- Fix: Break the cycle by refactoring (extract shared
  code into a new independent module)

---

### Quick Reference Card

| Property | Topological Sort |
|---------|-----------------|
| Input | DAG |
| Output | Linear ordering |
| Time | O(V+E) |
| Space | O(V+E) |
| Cycle detection | Yes (result.size() != V in Kahn's) |
| Algorithms | Kahn's (BFS), DFS post-order |

---

### The Surprising Truth

Maven's dependency resolution, Gradle's task graph,
npm's package installation order, and GNU Make all use
topological sort. The "circular dependency" error you've
seen in build tools is precisely the algorithm detecting
a cycle. Java's class loading also performs a form of
topological ordering: a class is loaded only after its
superclass and interfaces are loaded - guaranteed by the
JVM specification.

---

### Mastery Checklist

- [ ] Implements Kahn's algorithm from memory
- [ ] Detects cycles via result.size() < V check
- [ ] Understands DFS post-order variant

---

### Interview Deep-Dive

**Q1 (Medium):** Given a list of courses and prerequisite
pairs, determine if all courses can be finished.

> This is cycle detection on a DAG. Build adjacency list
> from prerequisites. Run Kahn's topological sort.
> If result.size() == numCourses, no cycle exists and
> all courses can be finished (result = valid order).
> If result.size() < numCourses, a cycle exists among
> the remaining nodes - impossible to finish all courses.
> Time: O(V+E) = O(numCourses + numPrerequisites).
> This is LeetCode 207 (Course Schedule).
