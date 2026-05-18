---
id: DSA-047
title: DSA Quick Reference Cheat Sheet
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-025
used_by: DSA-051, DSA-099
related: DSA-025, DSA-044, DSA-051, DSA-099
tags:
  - reference
  - cheat-sheet
  - complexity
  - java-collections
  - quick-reference
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/dsa/dsa-quick-reference-cheat-sheet/
---

## TL;DR

Complete complexity reference for all data structures and
algorithms in one place - the sheet to review the hour
before an interview.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-047 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | reference, cheat-sheet, complexity |
| **Prerequisites** | DSA-025 |

---

### Data Structure Complexity

| Structure | Access | Search | Insert | Delete | Space |
|-----------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Dynamic Array | O(1) | O(n) | O(1)* | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1)** | O(1)** | O(n) |
| Stack (Array) | O(n) | O(n) | O(1)* | O(1) | O(n) |
| Queue (Array) | O(n) | O(n) | O(1) | O(1) | O(n) |
| Hash Map | N/A | O(1)avg | O(1)avg | O(1)avg | O(n) |
| BST (balanced) | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | N/A | O(n) | O(log n) | O(log n) | O(n) |
| Trie | O(k) | O(k) | O(k) | O(k) | O(n*k) |

*amortized  **with reference to node

---

### Sorting Complexity

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | No |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Counting Sort | O(n+k) | O(n+k) | O(n+k) | O(k) | Yes |
| Radix Sort | O(dn) | O(dn) | O(dn) | O(n+k) | Yes |
| TimSort | O(n) | O(n log n) | O(n log n) | O(n) | Yes |

---

### Graph Algorithms

| Algorithm | Time | Space | Purpose |
|-----------|------|-------|---------|
| BFS | O(V+E) | O(V) | Shortest path (unweighted) |
| DFS | O(V+E) | O(V) | Cycle detect, topological sort |
| Dijkstra | O((V+E) log V) | O(V) | Shortest path (weighted) |
| Bellman-Ford | O(VE) | O(V) | Negative weights |
| Kruskal | O(E log E) | O(V) | Minimum spanning tree |
| Prim | O(E log V) | O(V) | Minimum spanning tree |
| Topological Sort | O(V+E) | O(V) | DAG ordering |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest path |

---

### Java Collections Quick Reference

| Need | Class | Note |
|------|-------|------|
| Fast key-value | `HashMap` | O(1) avg |
| Sorted keys | `TreeMap` | O(log n) |
| Insertion order | `LinkedHashMap` | O(1) |
| Unique elements | `HashSet` | O(1) |
| Sorted set | `TreeSet` | O(log n) |
| List (indexed) | `ArrayList` | O(1) access |
| Stack/Queue | `ArrayDeque` | O(1) both ends |
| Priority queue | `PriorityQueue` | O(log n) |
| Concurrent map | `ConcurrentHashMap` | Thread-safe |

---

### Common Problem Patterns

| Pattern | Use when | Algorithm |
|---------|---------|-----------|
| Two pointers | Sorted array, palindrome | O(n) |
| Sliding window | Subarray with constraint | O(n) |
| DFS + visited | Graph traversal, cycle | O(V+E) |
| BFS + queue | Shortest path, levels | O(V+E) |
| Heap + k | Top k, k-th largest | O(n log k) |
| HashMap complement | Two sum, anagram | O(n) |
| DP | Optimal substructure | varies |

---

### Mastery Checklist

- [ ] Can recall the complexity of all major structures
      without reference
- [ ] Knows Java's implementation for each abstract type
- [ ] Can map a problem to the correct algorithmic pattern
      before coding

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between O(1) and
O(1) amortized?

> O(1) means every single operation is constant time.
> O(1) amortized means the average cost over a sequence
> of operations is constant, even if some individual
> operations are expensive. Dynamic array `add()` is
> amortized O(1): most adds are O(1) (just write to next
> slot), but occasional resizes copy all n elements (O(n)).
> Averaged over n adds: total work = O(2n) = O(n).
> Per add: O(1) amortized.
