---
id: DSA-099
title: DSA Mastery Spaced Review
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-001, DSA-098
used_by: DSA-107, DSA-122
related: DSA-078, DSA-098
tags:
  - review
  - spaced-repetition
  - mastery
  - retention
  - dsa-summary
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 99
permalink: /technical-mastery/dsa/mastery-review/
---

## TL;DR

A curated spaced-repetition review card for DSA mastery:
30 high-signal questions covering the most commonly
tested and forgotten concepts across arrays, trees,
graphs, hash structures, and algorithms.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-099 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | review, spaced repetition, retention |
| **Prerequisites** | Full DSA category (DSA-001 onwards) |

---

### Review Round 1 - Foundations (L0/L1)

**Q1:** What is the difference between a stack and a queue?

> Stack: LIFO (Last In, First Out). push/pop at same end.
> Queue: FIFO (First In, First Out). enqueue at rear,
> dequeue at front.
> Stack: DFS, undo/redo, function call tracking.
> Queue: BFS, task scheduling, message buffers.

**Q2:** What makes an array better than a linked list
for most use cases?

> Cache locality: array elements occupy contiguous memory.
> CPU cache line (64 bytes) loads multiple array elements
> simultaneously. Linked list nodes scattered in heap =
> cache miss per element access.
> Random access: O(1) vs O(n).
> Modern CPUs optimize for sequential memory access.

**Q3:** What is the time complexity of building a
binary heap from n elements?

> O(n). Counter-intuitive (seems like O(n log n)).
> Proof: Floyd's heapify-down algorithm starts at
> last internal node (n/2) and heapifies down.
> Most nodes are near the leaves (short paths).
> Sum of work: Sum(depth * count_at_depth) = O(n).
> This is why heapSort uses O(n) heap build + O(n log n)
> extraction = O(n log n) total.

---

### Review Round 2 - Trees and Graphs (L1/L2)

**Q4:** What is the height of a balanced BST with n nodes?

> O(log n). Balanced BST: each subtree has at most 1
> node height difference. Height = floor(log2(n)).
> For 1M nodes: height = 20. For 1B nodes: height = 30.
> This is why BST operations are O(log n) = excellent
> at scale compared to O(n) for an unbalanced tree.

**Q5:** When does BFS fail where DFS succeeds, and vice versa?

> BFS fails (impractical): when the graph has a very
> large branching factor and the goal is deep.
> BFS memory = O(b^d) where b=branching, d=depth.
> DFS memory = O(d). For b=10, d=100: BFS needs 10^100
> nodes in memory. DFS needs only 100.
> 
> DFS fails: when you need the SHORTEST PATH in an
> unweighted graph. DFS finds A path, not the shortest.
> BFS guarantees shortest path (minimum hop count).

**Q6:** What is topological sort and when is it undefined?

> Topological sort: linear ordering of vertices in a DAG
> such that for every edge u->v, u comes before v.
> Used for: build dependency resolution (Maven, Gradle),
> task scheduling with dependencies, course prerequisite
> ordering.
> Undefined: when the graph has a CYCLE. Cycles create
> circular dependencies (A depends on B depends on A)
> with no valid linear ordering.

**Q7:** Red-Black Tree vs AVL Tree - which to prefer?

> AVL Tree: strictly balanced (height diff <= 1). Faster
> lookups (lower height). More rotations on insert/delete.
> Best for: read-heavy workloads.
> 
> Red-Black Tree: less strict balance (2:1 height ratio).
> Fewer rotations on insert/delete. Slightly taller tree.
> Best for: write-heavy workloads (Java TreeMap, C++ std::map).
> 
> In practice: use Java's built-in TreeMap (Red-Black).
> Only implement custom AVL if lookup performance is
> critical and updates are infrequent.

---

### Review Round 3 - Hash Structures (L2)

**Q8:** What causes a HashMap to have O(n) worst case
lookup, and how does Java 8 mitigate it?

> Cause: all keys hash to the same bucket (hash collision
> attack or poor hashCode). Lookup traverses the entire
> chain = O(n).
> Java 8 mitigation: treeification - when a bucket
> reaches 8 entries AND table capacity >= 64, converts
> chain to Red-Black Tree. O(n) -> O(log n) per bucket.
> Also: Java 7u6+ randomizes String.hashCode() seed per
> JVM run, preventing pre-computed collision attacks.

**Q9:** What is a Bloom filter and what can it NOT do?

> Bloom filter: probabilistic set membership check.
> Returns "definitely not in set" or "probably in set."
> Space: ~10 bits per element for 1% false positive rate.
> Use: cache miss reduction (check Bloom before DB),
> deduplication pre-filter, network packet filtering.
> 
> Cannot do:
> - Delete elements (deletions corrupt other elements)
> - Return which element matched
> - Give exact count
> - Give 0% false positive rate
> 
> Extension: Counting Bloom Filter allows deletions
> but uses 3-4x more space.

**Q10:** When would you use a TreeMap over a HashMap?

> Use TreeMap when: you need sorted key iteration, range
> queries (subMap, headMap, tailMap), floor/ceiling
> operations, or the key type has natural ordering.
> Cost: O(log n) vs O(1) for get/put. Accept the 10-50x
> slower operations for ordered iteration capability.
> 
> Classic use: sliding window statistics, ordered
> event processing, price range queries (stock ticker).

---

### Review Round 4 - Sorting and Searching (L2)

**Q11:** What sorting algorithm does Java use for
Arrays.sort() on primitives vs objects?

> Primitives (int[], long[], double[], etc.):
> Dual-Pivot Quicksort (Java 7+). O(n log n) expected,
> O(n^2) worst case (unlikely with dual pivot). Not stable.
> In-place: O(log n) stack space.
> 
> Objects (Object[], generic collections):
> TimSort (merge sort + insertion sort hybrid). O(n log n)
> always. STABLE (equal elements maintain original order).
> Exploits existing sorted runs in the data.
> Python also uses TimSort since Python 2.3.
> 
> Key: always use stable sort for objects when sort
> order relative to equal elements matters.

**Q12:** Explain binary search's precondition and a
common off-by-one error.

> Precondition: array must be SORTED. Binary search on
> unsorted data gives wrong results (not just slow).
> 
> Common off-by-one: `mid = (lo + hi) / 2` causes
> integer overflow when lo and hi are large ints.
> Correct: `mid = lo + (hi - lo) / 2`.
> Java's Arrays.binarySearch had this bug until 2006
> (Java release notes acknowledge it explicitly).
> 
> Template: while (lo <= hi) { mid = lo + (hi-lo)/2;
> if (arr[mid] == target) return mid;
> else if (arr[mid] < target) lo = mid + 1;
> else hi = mid - 1; }

---

### Review Round 5 - Advanced Algorithms (L3)

**Q13:** What is the invariant of Dijkstra's algorithm?

> After processing node u (removing from priority queue),
> dist[u] is finalized as the shortest path from source.
> This works because all edge weights are non-negative:
> any path that reaches u via another node v not yet
> processed must be longer (v's dist >= u's dist).
> Invariant breaks with negative edges: a shorter path
> via a negative edge to an unprocessed node might exist.
> For negative edges: use Bellman-Ford.

**Q14:** What is dynamic programming's essential insight?

> Overlapping subproblems + optimal substructure.
> Overlapping subproblems: the same sub-problem is solved
> multiple times in naive recursion.
> Optimal substructure: optimal solution to the whole
> problem contains optimal solutions to subproblems.
> DP stores sub-problem solutions (memoization = top-down,
> tabulation = bottom-up) to eliminate recomputation.
> Without overlapping subproblems, divide-and-conquer
> works (each subproblem solved only once).
> Without optimal substructure, DP does not apply
> (traveling salesman on certain graph types).

**Q15:** Union-Find detect vs prevent cycles - explain
the difference.

> Union-Find DETECTS cycles (in undirected graphs):
> Before adding edge (u,v): if find(u) == find(v), they're
> already connected = adding the edge creates a cycle.
> This is Kruskal's MST: skip edges that create cycles.
> 
> Union-Find does NOT prevent cycles directly - it
> detects them at edge-insertion time and lets you skip.
> It cannot check if a proposed set of operations
> WOULD create a cycle; it checks after you attempt union.

---

### Review Round 6 - Complexity and Trade-offs (L3/META)

**Q16:** What is the trade-off between space and time
in memoization vs tabulation?

> Both achieve O(n) time for DP problems.
> Memoization (top-down recursion + cache):
> - Only computes needed subproblems (lazy evaluation)
> - O(n) stack space + O(n) cache = 2x overhead
> - Easier to implement from recursive solution
> - Risk: stack overflow for large n (deep recursion)
> 
> Tabulation (bottom-up iteration + table):
> - Computes ALL subproblems (may compute unnecessary ones)
> - O(n) table space only, no stack frames
> - Can often optimize to O(1) or O(k) space by keeping
>   only the last k rows/entries needed
> - Better for large n (no recursion limit)
> 
> Production: prefer tabulation for large inputs.
> Space optimization: Fibonacci tabulation can use
> O(1) space (keep only prev, curr).

**Q17:** Why is Quick Sort O(n log n) average but
O(n^2) worst case? How do you prevent the worst case?

> Average: pivot divides array roughly in half. T(n) =
> 2T(n/2) + O(n) = O(n log n) by master theorem.
> Worst case: pivot is always min or max (sorted array).
> T(n) = T(n-1) + O(n) = O(n^2).
> 
> Prevention:
> 1. Randomized pivot: shuffle array before sorting OR
>    pick random pivot. Makes O(n^2) probability negligible.
> 2. Median-of-three: pivot = median of first/middle/last.
>    Prevents sorted array worst case.
> 3. IntroSort: switch to HeapSort after O(log n) depth
>    recursion. Java Arrays.sort uses Dual-Pivot QuickSort
>    which is empirically faster and avoids classic worst case.

**Q18:** What is amortized O(1) for ArrayList.add()
and how does ArrayList avoid O(n^2) total for n adds?

> ArrayList doubles capacity when full. Resize = O(n) copy.
> But resizes happen at sizes 1, 2, 4, 8, ... n.
> Total copy work: 1+2+4+...+n = O(2n) = O(n).
> n add operations total O(n) copy work = O(1) amortized.
> 
> Alternative proof: each element is copied at most
> O(log n) times (once per doubling it participates in).
> But only the LAST 50% of elements are copied once,
> the 25% before that copied twice, etc.
> Total copies = n*1/2 + n*1/4 + ... = n*1 = O(n).

---

### Spaced Review Schedule

```
Week 1: Rounds 1-2 (Q1-Q7)   - Foundations + Trees
Week 2: Rounds 3-4 (Q8-Q12)  - Hash + Sort/Search
Week 3: Rounds 5-6 (Q13-Q18) - Advanced + Trade-offs
Week 4: Full review (Q1-Q18)  - All 18 questions
Month 2: Q1-Q18 in random order, target <30s per answer
Month 3: Answer Q1-Q18 from memory, no notes
```

---

### Mastery Checklist

- [ ] Answers all 18 questions in under 3 minutes total
- [ ] Explains amortized complexity with concrete examples
- [ ] Identifies when NOT to use each data structure
- [ ] Derives complexity from first principles (not memory)

---

### The Surprising Truth

Spaced repetition increases long-term retention by 200-400%
compared to massed practice (cramming). The Ebbinghaus
forgetting curve shows 50% of learned material is lost
within 24 hours without review. The optimal review
intervals (1 day, 3 days, 7 days, 14 days, 30 days)
are well-established. Engineers who review DSA concepts
on this schedule can maintain expert-level recall with
only 15 minutes per week of review.
