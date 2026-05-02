---
layout: default
title: "Skip List"
parent: "Data Structures & Algorithms"
nav_order: 43
permalink: /dsa/skip-list/
number: "0043"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: LinkedList, Randomized Algorithms
used_by: ConcurrentSkipListMap, Database Index
related: TreeMap, B-Tree, AVL Tree
tags:
  - datastructure
  - advanced
  - algorithm
  - deep-dive
  - concurrency
---

# 043 — Skip List

⚡ TL;DR — A Skip List achieves O(log N) expected search, insert, and delete on sorted data using randomised multi-level linked lists — simpler to implement concurrently than balanced trees.

| #043 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | LinkedList, Randomized Algorithms | |
| **Used by:** | ConcurrentSkipListMap, Database Index | |
| **Related:** | TreeMap, B-Tree, AVL Tree | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A database needs an ordered index supporting concurrent reads and writes without locking the entire structure. Balanced BSTs (AVL, red-black) achieve O(log N) operations but require rotations on insert/delete — rotations must lock multiple nodes simultaneously, creating contention in concurrent workloads. A single global lock serialises all access.

THE BREAKING POINT:
Balanced tree rebalancing is inherently non-local: a single insert can trigger rotations propagating up to the root, requiring locks on an entire path. In a concurrent system, this creates a sequential bottleneck. The more threads, the worse the contention.

THE INVENTION MOMENT:
Replace deterministic rebalancing with probabilistic layer promotion. A node is promoted to the next level with probability ½. On average, this creates a structure equivalent to a balanced tree — but with no rotations, and with lock-free insertion achievable through CAS operations on individual node pointers. This is exactly why the Skip List was created.

---

### 📘 Textbook Definition

A **Skip List** is a probabilistic data structure consisting of multiple levels of sorted linked lists. Level 0 contains all elements; each higher level is a randomly chosen subset (typically each element promoted with probability p=0.5). Search, insert, and delete operate in O(log N) *expected* time and O(N log N) *expected* space. The structure was invented by William Pugh in 1990 as a simpler alternative to balanced BSTs for sorted data, particularly suited to concurrent access patterns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A sorted linked list with express lanes that let you skip ahead fast — like a subway with local and express tracks.

**One analogy:**
> Think of a subway system with express and local trains. Local stops at every station. Express stops only every 4th station. Express-Express only every 16th. To get from station 1 to station 60, take express-express to station 48, express to station 56, local to station 60 — much faster than stopping at all 60 stations.

**One insight:**
The skip list's O(log N) performance is probabilistic — not guaranteed. But the probability that it *doesn't* perform in O(log N) decreases exponentially with N. For practical purposes, the performance is indistinguishable from a balanced tree, with the bonus that no rebalancing logic is required.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Level 0 is a fully sorted singly linked list of all elements.
2. Level k contains each level k-1 element independently with probability p.
3. A node at level k has pointers to the next node at levels 0 through k.

DERIVED DESIGN:
Expected elements at level k: N × p^k. Expected height: log_{1/p}(N) = O(log N) for p=0.5.

**Search(x)**: Start at top-left node (header at highest level). Advance right if next node ≤ x. Drop one level if next node > x. Repeat until level 0. O(log N) expected.

**Insert(x)**: Search and record the "update" nodes at each level (the last node per level that we didn't advance past). Create new node. Flip coin to determine its height: if heads, extend to next level; repeat. Link new node at each level it reaches.

**Delete(x)**: Search for x, splice out its pointers at each level. No rebalancing needed.

The randomness is the key: because promotions are independent coin flips, the structure self-organises around a balanced tree shape in expectation, without any deterministic balancing logic.

THE TRADE-OFFS:
Gain: Simple implementation, lock-friendly concurrent access, no rebalancing.
Cost: O(N log N) expected space (pointer overhead per node), non-deterministic worst case (O(N) with exponentially small probability), less cache-friendly than arrays.

---

### 🧪 Thought Experiment

SETUP:
Sorted set of 16 elements. Search for element 13.

WHAT HAPPENS WITHOUT SKIP LIST (sorted linked list):
Must traverse all elements from 1 to 13 — 13 pointer dereferences.

WHAT HAPPENS WITH SKIP LIST (4 levels):
- Level 3: header → 1 → 9 → null. 9 < 13 → advance. 13 > null → drop to level 2.
- Level 2: from 9 → 13. Found. Total: 4 pointer dereferences.

THE INSIGHT:
At each level, you skip over roughly half the remaining elements (the ones not promoted). This binary-search-like elimination is why O(log N) expected time emerges from simple coin flips.

---

### 🧠 Mental Model / Analogy

> A skip list is like a city with expressways at multiple scales. The expressway at the top level jumps 100 km at a time. The next level jumps 10 km. The street level visits every address. To reach any destination, start on the highest expressway and switch to slower roads as you approach the target.

"Highest expressway" → top level (few nodes)
"Street level" → level 0 (all elements)
"Switching to slower road" → dropping a level
"Coin flip for expressway on-ramp" → random level promotion

Where this analogy breaks down: Real expressways have fixed distances between exits; skip list "skips" are determined by random coin flips — variable-size jumps that average out to logarithmic.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A sorted list with multiple "fast lanes." You can search using fast lanes to skip many elements at once, and slow down to the normal lane as you get close to your target.

**Level 2 — How to use it (junior developer):**
Java provides `ConcurrentSkipListMap<K,V>` and `ConcurrentSkipListSet<K>` — use these rather than implementing from scratch. They provide sorted concurrent access with O(log N) expected operations. Iteration is always in key order. Use when you need a `TreeMap` that supports concurrent read/write without full locking.

**Level 3 — How it works (mid-level engineer):**
Each node stores its `key`, `value`, and `next[]` — an array of forward pointers, one per level. The `MAX_LEVEL` is typically `log₂(N_max)`. `insert(key)`: search down each level recording the last node with `next[level].key < key` ("predecessors"). Flip coin to determine new node's height. Link new node into each active level's chain. `search(key)`: drop levels when next pointer exceeds target key.

**Level 4 — Why it was designed this way (senior/staff):**
The core advantage over balanced BSTs in concurrent systems is that skip list insert modifies only a *fixed set of local pointers* — no global rebalancing. This makes CAS-based lock-free skip lists possible (Java's `ConcurrentSkipListMap` uses this). A lock-free balanced BST is significantly harder to implement correctly. Redis uses skip lists for sorted sets (ZADD/ZRANGE) precisely because range queries are natural (level 0 is always sorted), and concurrent access patterns are simpler. LevelDB and RocksDB use skip lists for their in-memory MemTable before flushing to disk.

---

### ⚙️ How It Works (Mechanism)

**Skip list structure (N=8, 3 levels, p=0.5):**
```
Level 2: H ────────────────────► 6 ──────► null
Level 1: H ──────► 3 ──► 5 ──► 6 ──► 8 ► null
Level 0: H ► 1 ► 2 ► 3 ► 4 ► 5 ► 6 ► 7 ► 8 null
```

**Search(7):**
```
Level 2: H (∞ jump) → 6: 6 < 7 → advance. Next=null > 7 → drop
Level 1: from 6 → 8: 8 > 7 → drop
Level 0: from 6 → 7: found! 3 comparisons
```

**Node structure:**
```java
class SkipNode<K, V> {
    K key;
    V value;
    SkipNode<K, V>[] next; // length = node's level
    SkipNode(K key, V value, int level) {
        this.key = key; this.value = value;
        next = new SkipNode[level + 1];
    }
}
```

**randomLevel():**
```java
int randomLevel() {
    int level = 0;
    while (rng.nextDouble() < 0.5 && level < MAX_LEVEL)
        level++;
    return level;
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Search(key):
→ Start at header, highest level
→ Advance right if next.key ≤ key
→ Drop level if next.key > key
→ [SKIP LIST ← YOU ARE HERE]
→ Return value when key found at level 0
→ Insert: coin-flip height, link at each level
```

FAILURE PATH:
```
Pathological random seed → all elements promoted to max level
→ O(N log N) space consumed
→ Each node is a full-height tower → O(N) search
→ Probability: (1/2)^maxLevel per element — negligible
```

WHAT CHANGES AT SCALE:
At 10M+ elements, the pointer overhead of skip lists (~8 bytes per pointer × avg 2 pointers/node) becomes significant compared to B-trees (which pack many keys per cache line). Database systems (Redis, RocksDB MemTable) accept this overhead for the lock-free concurrency benefit. At extreme scale, trees are preferred because spatial locality (cache lines) matters more than lock-free code.

---

### 💻 Code Example

**Example 1 — Using Java's ConcurrentSkipListMap:**
```java
// Thread-safe sorted map — O(log N) operations
ConcurrentSkipListMap<Integer, String> skipMap =
    new ConcurrentSkipListMap<>();

skipMap.put(5, "five");
skipMap.put(3, "three");
skipMap.put(7, "seven");

// Sorted iteration
skipMap.forEach((k, v) ->
    System.out.println(k + ":" + v)); // 3, 5, 7

// Floor/ceiling like TreeMap
System.out.println(skipMap.floorKey(4));   // 3
System.out.println(skipMap.ceilingKey(4)); // 5

// Thread-safe range view
SortedMap<Integer, String> sub =
    skipMap.subMap(3, true, 6, true); // {3=three, 5=five}
```

**Example 2 — Redis sorted set (conceptual):**
```bash
# Redis uses skip list internally for ZSETs
ZADD leaderboard 1500 "Alice"
ZADD leaderboard 2000 "Bob"
ZADD leaderboard 1750 "Carol"

# Range query by rank — O(log N + K) skip list traversal
ZRANGE leaderboard 0 2 WITHSCORES
# 1) Alice, 1500  2) Carol, 1750  3) Bob, 2000
```

---

### ⚖️ Comparison Table

| Structure | Search | Insert | Delete | Concurrent | Best For |
|---|---|---|---|---|---|
| **Skip List** | O(log N) exp | O(log N) exp | O(log N) exp | ✓ easy | Concurrent sorted access |
| Red-Black Tree | O(log N) | O(log N) | O(log N) | ✗ hard | Deterministic sorted sets |
| B-Tree | O(log N) | O(log N) | O(log N) | ✓ moderate | Disk-based, cache-friendly |
| Hash Map | O(1) avg | O(1) avg | O(1) avg | ✓ moderate | Unsorted lookup |

How to choose: Use `ConcurrentSkipListMap` when you need a thread-safe sorted map in Java. Use `TreeMap` in single-threaded contexts. Use B-trees for disk-based storage. Use hash maps if ordering is not required.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Skip list O(log N) is guaranteed like BSTs | Skip list time complexity is expected O(log N) — worst case is O(N) with exponentially small probability |
| Skip lists are only useful in concurrent settings | Skip lists are faster to implement than balanced BSTs even in single-threaded contexts |
| All levels must have at least one element | A skip list is valid even if upper levels are empty for small N |
| Skip lists waste less memory than trees | Skip lists use O(N log N) expected space due to pointer arrays; trees use O(N) nodes |

---

### 🚨 Failure Modes & Diagnosis

**1. Non-deterministic performance under adversarial seeds**

Symptom: Skip list operations take O(N) in rare pathological cases.

Root Cause: If the random number generator is seeded with a value that promotes too many elements to the top level, chains become unbalanced.

Diagnostic:
```java
// Add operation counter and assert:
int ops = skipList.search(key);
assert ops < 3 * (int)(Math.log(N) / Math.log(2)) :
    "Unexpected O(N) operation: " + ops;
```

Fix: Use a good PRNG (e.g., `java.util.Random` or `ThreadLocalRandom`). Avoid seeding from system time in production systems with predictable patterns.

Prevention: For security-sensitive code, use cryptographically secure random promotion.

---

**2. Race condition in non-concurrent implementation**

Symptom: Concurrent inserts and searches return incorrect results or cause NullPointerException.

Root Cause: Plain skip list (without CAS/locks) is not thread-safe. Concurrent insert modifies the same predecessor's `next` pointer simultaneously.

Diagnostic:
```bash
jstack <pid> | grep "RUNNABLE"
# Multiple threads in SkipList.insert() simultaneously
```

Fix: Use `ConcurrentSkipListMap` from Java's concurrent package, or implement with CAS.

Prevention: Never share a plain skip list implementation between threads.

---

**3. Excessive height from MAX_LEVEL too high**

Symptom: Skip list uses far more memory than expected; many empty levels per node.

Root Cause: MAX_LEVEL set too high for actual N. For N=1000, MAX_LEVEL=32 is wasteful (expected max needed height ~10).

Diagnostic:
```java
// Print average node height:
double avgHeight = nodes.stream()
    .mapToInt(n -> n.level).average().orElse(0);
System.out.println("Avg height: " + avgHeight);
// Should be ≈ 2 for p=0.5
```

Fix: Set `MAX_LEVEL = ceil(log₂(expectedMaxN))`. For N up to 10^6, MAX_LEVEL=20 is sufficient.

Prevention: Size MAX_LEVEL to your expected dataset; document the reasoning.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `LinkedList` — a skip list's level 0 is a sorted linked list; linked list traversal is the base operation.
- `Randomized Algorithms` — skip lists rely on probabilistic analysis for their O(log N) expected complexity.

**Builds On This (learn these next):**
- `ConcurrentSkipListMap` (Java) — production concurrent sorted map backed by skip list.

**Alternatives / Comparisons:**
- `TreeMap` — deterministic O(log N) but harder to make concurrent; use for single-threaded sorted maps.
- `B-Tree` — preferred for disk storage; better cache locality than skip lists.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multi-level sorted linked list; O(log N)  │
│              │ expected search/insert/delete             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Balanced BST rebalancing requires multi-  │
│ SOLVES       │ node locks — bottleneck in concurrent code│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Random coin flips create balance without  │
│              │ deterministic rebalancing or rotations    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Concurrent sorted access (Java            │
│              │ ConcurrentSkipListMap), Redis sorted sets │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Memory is tight or worst-case guarantee   │
│              │ is required (use Red-Black tree instead)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple concurrent code vs O(N log N)      │
│              │ space + probabilistic (not guaranteed) O  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A subway with express and local trains   │
│              │  built by coin flips"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentSkipListMap → B-Tree → Bloom    │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `ConcurrentSkipListMap` achieves lock-free reads and CAS-based writes. When two threads simultaneously insert keys that map to adjacent positions at level 0, why does a skip list allow this operation to proceed concurrently while a red-black tree would require serialisation? What specific structural property of skip lists enables local CAS operations to serve as the synchronisation primitive without violating sorted order?

**Q2.** Redis uses skip lists for sorted sets instead of AVL trees, despite having access to well-tested AVL implementations. One cited reason is that "range queries by rank are easier on skip lists." Explain precisely why this is true: in a skip list, what property makes O(log N) "find the K-th element" trivial to implement, whereas in an AVL tree it requires augmenting each node with a subtree-count field (an O(log N) operation requiring careful maintenance on rebalancing)?

