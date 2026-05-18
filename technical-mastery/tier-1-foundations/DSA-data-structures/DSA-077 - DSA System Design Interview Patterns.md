---
id: DSA-077
title: DSA System Design Interview Patterns
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-044, DSA-065, DSA-060
used_by: DSA-098, DSA-107
related: DSA-044, DSA-098, DSA-103
tags:
  - system-design
  - interview
  - patterns
  - dsa-application
  - architecture
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/dsa/dsa-system-design-patterns/
---

## TL;DR

System design interviews test whether you can map real-world
requirements to the right data structures and algorithms -
LRU caches, top-k elements, rate limiting, and recommendation
systems each have a canonical DSA solution.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-077 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | system-design, interview, DSA-application |
| **Prerequisites** | DSA-044, DSA-065, DSA-060 |

---

### The Problem This Solves

System design interviews expect you to identify WHICH data
structure solves the problem, WHY, and what the trade-offs
are. "Design a trending topics system" = top-k with a
min-heap. "Design an autocomplete" = trie. "Design a
rate limiter" = sliding window with circular buffer.
This entry maps common system design problems to their
DSA solutions.

---

### Pattern Catalog

**Pattern 1: Top-K Elements**
- Problem: "Show top 10 trending hashtags from 1B tweets/day"
- Solution: Min-heap of size K
- Rationale: Min-heap maintains K largest seen; O(log K) per
  insertion (much faster than sort every time)
- Implementation:

```java
// Top-K from stream using min-heap
PriorityQueue<Map.Entry<String, Integer>> heap =
    new PriorityQueue<>(K, Comparator.comparingInt(Map.Entry::getValue));
for (Map.Entry<String, Integer> entry : countMap.entrySet()) {
    heap.offer(entry);
    if (heap.size() > K) heap.poll(); // remove minimum
}
// heap now contains K largest
```

**Pattern 2: LRU Cache**
- Problem: "Cache last N accessed pages"
- Solution: HashMap + Doubly Linked List (DSA-086)
- Rationale: HashMap for O(1) get; DLL for O(1) eviction
  of least-recently-used; move accessed node to head

**Pattern 3: Rate Limiting**
- Problem: "Allow 100 requests per minute per user"
- Solution: Sliding window with circular buffer (DSA-041)
- Rationale: Fixed window: unfair near boundaries.
  Sliding window: accurate but O(n) memory per user.
  Sliding window counter: O(1) with approximate accuracy

**Pattern 4: Autocomplete**
- Problem: "Return top 5 completions for a prefix"
- Solution: Trie with min-heap at each node (DSA-056)
- Rationale: Trie gives O(k) prefix lookup; heap at each
  node stores precomputed top-5 by frequency

**Pattern 5: Shortest Path / Navigation**
- Problem: "Fastest route between two points"
- Solution: Dijkstra's (DSA-060) for non-negative weights
- Rationale: O((V+E)logV) with min-heap; works on real
  road networks with positive distances

**Pattern 6: Social Graph Connectivity**
- Problem: "Are users A and B in the same network?"
- Solution: Union-Find (DSA-059)
- Rationale: O(alpha(n)) per query after O(E) setup;
  handles dynamic edge additions

**Pattern 7: Range Queries**
- Problem: "Sum of user activity scores for date range"
- Solution: Segment Tree or BIT (DSA-057, DSA-058)
- Rationale: O(log n) per query and update vs O(n) brute force

**Pattern 8: Recommendation System**
- Problem: "Find K most similar users to user X"
- Solution: Min-heap of size K on cosine similarity
- Rationale: O(n log K) to find top-K from n users vs
  O(n log n) sorting all users

---

### DSA-to-System-Design Mapping

| System Design Component | DSA Solution | Key Property |
|------------------------|-------------|-------------|
| LRU Cache | HashMap + DLL | O(1) get and evict |
| Rate Limiter | Circular Buffer / sliding window | O(1) per request |
| Autocomplete | Trie + min-heap | O(k) prefix, O(log k) top |
| Trending Topics | Min-heap size K | O(n log K) vs O(n log n) |
| Social Graph | Union-Find | O(alpha(n)) connectivity |
| Navigation / GPS | Dijkstra's | O((V+E)log V) shortest path |
| Range Analytics | Segment Tree | O(log n) range query |
| Search Index | Inverted Index + Trie | O(k) prefix search |
| Consistent Hashing | Circular structure + TreeMap | O(log n) node lookup |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "HashMap solves all lookup problems" | HashMap has no ordering; range queries, prefix search, and sorted iteration need TreeMap, Trie, or segment tree |
| "BFS/DFS solves all graph problems" | Unweighted traversal only; shortest weighted paths need Dijkstra/Bellman-Ford; MST needs Kruskal/Prim |

---

### Failure Modes & Diagnosis

**Failure: Trie runs out of memory at scale**
- Cause: 100M unique words × 10 chars avg = 1B nodes at
  8 bytes each = 8GB - too large for single machine
- Fix: Compressed trie (Patricia tree); DAWG (merges
  common suffixes too); or sharded trie by first char

---

### Quick Reference Card

| Interview Pattern | DSA Pick | Time |
|------------------|---------|------|
| Top-K elements | Min-heap size K | O(n log K) |
| LRU cache | HashMap + DLL | O(1) ops |
| Autocomplete | Trie | O(k) |
| Rate limiting | Sliding window | O(1) |
| Shortest path | Dijkstra | O((V+E)logV) |
| Connectivity | Union-Find | O(alpha(n)) |
| Range sum/min | Segment Tree / BIT | O(log n) |

---

### The Surprising Truth

LinkedIn's "People You May Know" feature uses a combination
of BFS (2-hop network), Union-Find (connected components),
and cosine similarity (min-heap top-K) in a distributed
graph processing framework (Spark GraphX). What looks like
a simple "suggest friends" feature requires all three
major graph algorithm categories working together. The
correct DSA selection at each layer determines whether
the feature is O(n) feasible or O(n^2) impossible at
500M user scale.

---

### Mastery Checklist

- [ ] Can immediately identify the right DSA for each of
      the 8 canonical system design patterns
- [ ] Can justify WHY that DSA (not just which)
- [ ] Knows the scale at which each approach breaks down

---

### Interview Deep-Dive

**Q1 (Hard):** Design a system to find the median of
a stream of numbers in O(log n) per insert.

> Two heaps: max-heap for lower half, min-heap for upper half.
> Invariant: both heaps balanced (sizes differ by ≤ 1).
> Insert: add to appropriate heap; rebalance if needed.
> Get median: if same size → average of both tops;
> otherwise → top of larger heap.
> Each insert: O(log n) (heap push + optional rebalance).
> Get median: O(1).
> 
> This pattern appears in sliding window median,
> network percentile computation (P50/P95/P99 latency),
> and real-time analytics. The two-heap approach is
> the canonical O(log n) solution for the "median of
> stream" problem class.
