---
id: DSA-036
title: Breadth-First Search (BFS)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-013, DSA-018, DSA-034
used_by: DSA-063
related: DSA-035, DSA-039, DSA-063
tags:
  - algorithms
  - graph
  - bfs
  - breadth-first
  - shortest-path
  - queue
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/dsa/breadth-first-search/
---

## TL;DR

BFS explores all neighbors at distance d before any at
distance d+1 - guaranteed shortest path in unweighted
graphs, O(V+E), powered by a queue.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-036 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, graph, BFS, shortest-path |
| **Prerequisites** | DSA-013, DSA-018, DSA-034 |

---

### The Problem This Solves

"What is the fewest steps from A to B?" DFS explores deep
paths first and may find a long path before a short one.
BFS explores in order of distance - it guarantees the first
time it reaches B is via the shortest path.

---

### Textbook Definition

Breadth-First Search traverses a graph level by level:
first all nodes at distance 1, then distance 2, etc. Uses
a FIFO queue. When it first visits a node, that path is
the shortest. Time: O(V + E). Space: O(V) for queue and
visited set. Does NOT use a stack or recursion.

---

### Understand It in 30 Seconds

```
Graph:  A - B - E
        |       |
        C - D - F

Shortest path A to F?

BFS from A:
Level 0: [A]
Level 1: [B, C]          (neighbors of A)
Level 2: [E, D]          (neighbors of B, C, not A)
Level 3: [F]             (neighbor of E, D)

Distance A→F = 3. Path: A→B→E→F (or A→C→D→F)
```

---

### How It Works

**BFS with shortest path reconstruction:**

```java
int bfsShortestPath(Map<Integer, List<Integer>> graph,
                    int start, int end) {
    if (start == end) return 0;
    Queue<Integer> queue = new LinkedList<>();
    Set<Integer> visited = new HashSet<>();
    queue.offer(start);
    visited.add(start);
    int distance = 0;

    while (!queue.isEmpty()) {
        int size = queue.size();    // nodes at current level
        distance++;
        for (int i = 0; i < size; i++) {
            int node = queue.poll();
            for (int neighbor : graph.getOrDefault(node, List.of())) {
                if (neighbor == end) return distance;
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.offer(neighbor);
                }
            }
        }
    }
    return -1; // unreachable
}
```

**BFS for tree level-order traversal:**

```java
List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> result = new ArrayList<>();
    if (root == null) return result;

    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);

    while (!queue.isEmpty()) {
        int levelSize = queue.size();
        List<Integer> level = new ArrayList<>();

        for (int i = 0; i < levelSize; i++) {
            TreeNode node = queue.poll();
            level.add(node.val);
            if (node.left != null)  queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }
        result.add(level);
    }
    return result;
}
```

---

### Comparison Table

| Property | BFS | DFS |
|---------|-----|-----|
| Data structure | Queue (FIFO) | Stack (recursion) |
| Finds shortest path | Yes (unweighted) | No |
| Space | O(max width) | O(max depth) |
| Cycle detection | Yes | Yes |
| Topological sort | Yes (Kahn's) | Yes (post-order) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "BFS finds shortest path in weighted graphs" | Only unweighted; use Dijkstra for weighted shortest path |
| "BFS requires more space than DFS" | Depends on graph shape; BFS uses O(width), DFS uses O(depth); wide shallow graphs favor DFS; tall narrow graphs favor BFS |

---

### Failure Modes & Diagnosis

**Failure: BFS finds a path but it's not shortest**
- Cause: Visited set missing; a node is processed multiple
  times, wrong distance stored
- Fix: Mark node visited WHEN ADDED TO QUEUE, not when
  polled; otherwise the same node enters queue multiple
  times with different distances

---

### Quick Reference Card

| Use BFS for | Reason |
|------------|--------|
| Shortest path (unweighted) | Level-by-level = distance |
| Level-order traversal | Floor by floor |
| Connected components | BFS from each unvisited |
| Social distance (degrees) | BFS level = hop count |

---

### Mastery Checklist

- [ ] Can implement BFS with correct queue and visited set
- [ ] Marks nodes visited when enqueued, not when polled
- [ ] Knows BFS gives shortest path only for unweighted
      graphs (Dijkstra for weighted)

---

### Interview Deep-Dive

**Q1 (Medium):** You have a grid of 0s and 1s. Find the
shortest path from top-left to bottom-right through 0s.

> BFS on a 2D grid (treating each cell as a graph node,
> edges to 4-directional neighbors). Start: (0,0). End:
> (rows-1, cols-1). Enqueue starting cell with distance 0.
> Process level by level. Mark visited to avoid revisiting.
> Each step increments distance by 1. Return distance when
> end cell dequeued.
> Time: O(rows * cols). Space: O(rows * cols) for queue.
> This "0-1 BFS on grid" pattern appears in every shortest
> path on a grid interview question.
