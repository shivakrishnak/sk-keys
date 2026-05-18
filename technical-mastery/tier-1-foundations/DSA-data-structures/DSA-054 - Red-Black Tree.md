---
id: DSA-054
title: Red-Black Tree
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-017, DSA-053
used_by: DSA-093
related: DSA-053, DSA-055
tags:
  - data-structures
  - red-black-tree
  - self-balancing
  - java-treemap
  - o-log-n
  - rotations
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/dsa/red-black-tree/
---

## TL;DR

A Red-Black Tree is a self-balancing BST with 5 coloring
properties that guarantee height ≤ 2 log n and O(1) amortized
rotations per insert/delete - the tree behind Java's TreeMap
and TreeSet.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-054 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, red-black-tree, TreeMap |
| **Prerequisites** | DSA-017, DSA-053 |

---

### The Problem This Solves

AVL trees maintain strict balance (height ≤ 1.44 log n)
but require O(log n) rotations on delete. Red-Black trees
relax balance (height ≤ 2 log n) to achieve O(1) amortized
rotations - the right balance for a general-purpose sorted
map under mixed read/write workloads.

---

### Textbook Definition

A Red-Black Tree is a BST where each node is colored red
or black, satisfying these 5 properties:
1. Every node is red or black
2. The root is black
3. All null (leaf sentinel) nodes are black
4. A red node has no red children (no two consecutive reds)
5. Every path from a node to its descendant null nodes
   has the same number of black nodes

These properties guarantee: height ≤ 2 * log2(n+1).

---

### The 5 Properties Explained

**Property 4 (no consecutive reds):**
Prevents a long chain of red nodes that would unbalance
the tree.

**Property 5 (equal black height):**
Every root-to-null path has the same count of black nodes.
This is the key balance guarantee: if every path has k
black nodes, the shortest path is k (all black) and the
longest is 2k (alternating red-black). Ratio = 2.
So height ≤ 2k = O(log n).

---

### How It Works

**Structural invariant (5 properties visualized):**

```
       [B]13           B = Black, R = Red
      /     \
  [R]8     [R]17
  /  \      /  \
[B]1  [B]11 [B]15 [B]25
          \
          [R]...

- Root 13: Black (property 2)
- 13→8 and 13→17: black parent, red children (4 OK)
- 8→1 and 8→11: red parent, black children (4 OK)
- All null paths: same black height (property 5)
```

**Insert: recoloring and rotations**

When a new node is inserted (initially red):
- Uncle is red: recolor parent, uncle to black; grandparent to red
- Uncle is black: 1 or 2 rotations depending on "zig-zig" or "zig-zag"

At most 2 rotations per insert. O(log n) recolorings.

**Why Java's TreeMap uses Red-Black Tree:**

```java
// Java TreeMap: Red-Black Tree
// All operations guaranteed O(log n)
TreeMap<String, Integer> map = new TreeMap<>();
map.put("banana", 2);
map.put("apple", 1);
map.put("cherry", 3);

map.firstKey();           // "apple"  O(log n)
map.lastKey();            // "cherry" O(log n)
map.floorKey("blueberry");// "banana" O(log n)
map.subMap("apple","cherry");// ["apple","banana"] O(log n)
// All of these work because tree is sorted
```

---

### Comparison Table

| Property | AVL | Red-Black |
|---------|-----|-----------|
| Height | 1.44 log n | 2 log n |
| Insert rotations | ≤ 2 | ≤ 2 |
| Delete rotations | ≤ O(log n) | ≤ 3 |
| Lookup speed | Slightly faster | Standard |
| Write performance | Slower | Faster |
| Java use | Not used | TreeMap, TreeSet |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Red nodes are inferior to black nodes" | Color is just a balance-tracking label; both colors are regular tree nodes |
| "Red-Black tree is the only self-balancing BST in Java" | Java also uses B-Trees in some contexts (ConcurrentSkipListMap uses skip list, not tree) |

---

### Failure Modes & Diagnosis

**Failure: TreeMap behaves O(n) instead of O(log n)**
- Cause: Custom Comparator with inconsistent ordering
  (a.compareTo(b) = 0 but not equal per equals())
  corrupts the tree structure
- Fix: Comparator must be consistent with equals():
  `compare(a, b) == 0` iff `a.equals(b)` for correct behavior

---

### Quick Reference Card

| Property | Red-Black Tree |
|---------|---------------|
| Height | ≤ 2 log2(n+1) |
| Search | O(log n) |
| Insert | O(log n), ≤ 2 rotations |
| Delete | O(log n), ≤ 3 rotations |
| Java class | TreeMap, TreeSet |
| Java since | JDK 1.2 |

---

### Mastery Checklist

- [ ] Can state all 5 Red-Black properties from memory
- [ ] Can explain why height ≤ 2 log n follows from
      properties 4 and 5
- [ ] Knows TreeMap uses Red-Black Tree and understands
      all its ordered operations

---

### Interview Deep-Dive

**Q1 (Hard):** How does the Red-Black Tree property
guarantee O(log n) height?

> Properties 4 and 5 together bound the height.
> Property 5: every root-to-leaf path has k black nodes.
> Property 4: no two consecutive red nodes.
> Therefore, the shortest path is k (all black).
> The longest path is at most 2k (alternating red-black,
> so red count ≤ black count = k).
> Total nodes n ≥ 2^k - 1, so k ≤ log2(n+1).
> Height ≤ 2k ≤ 2*log2(n+1) = O(log n).
