---
id: DSA-017
title: Binary Search Tree (BST)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-016
used_by: DSA-034, DSA-053, DSA-054, DSA-055
related: DSA-014, DSA-016, DSA-020, DSA-053
tags:
  - data-structures
  - bst
  - binary-search-tree
  - ordered
  - search
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/dsa/binary-search-tree/
---

## TL;DR

A BST maintains sorted order in a tree: left subtree contains
only smaller values, right contains only larger - enabling
O(log n) search, insert, and delete on ordered data.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-017 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, BST, ordered, search |
| **Prerequisites** | DSA-016 |

---

### The Problem This Solves

A hash map gives O(1) lookup but no ordering. An array can
be sorted for binary search but O(n) insert/delete.
A BST gives O(log n) for search, insert, AND delete while
maintaining sorted order - the combination arrays and hash
maps cannot both offer.

**EVOLUTION:**
BSTs were formalized in the late 1950s. The critical insight
that unbalanced BSTs degrade to O(n) led to self-balancing
variants: AVL trees (1962, Adelson-Velsky and Landis) and
Red-Black trees (1972, Guibas and Sedgewick).

---

### Textbook Definition

A binary search tree is a binary tree where for every node N:
- All values in N's left subtree are less than N's value
- All values in N's right subtree are greater than N's value
- Both subtrees are also valid BSTs

This ordering invariant enables binary search on the tree
structure: at each node, eliminate half the remaining nodes
based on comparison.

---

### Understand It in 30 Seconds

Search for 35 in this BST:

```
        50
       /  \
      30   70
     /  \
    20   40
```

35 < 50 → go left to 30.
35 > 30 → go right to 40.
35 < 40 → go left (null) → not found.

Three comparisons for a tree with 5 nodes. Tree with 1M
nodes: ~20 comparisons.

---

### First Principles

**The BST invariant:**
left.value < parent.value < right.value (for all nodes)

This invariant is what makes O(log n) search possible:
at each node, you eliminate the half of the tree that
cannot contain the target.

**The balance problem:**
If you insert values 1, 2, 3, 4, 5 in order into a plain
BST, you get a linked list (each node's right child only).
Height = n. Search = O(n). The BST invariant is maintained
but the balance is destroyed.

Solution: self-balancing trees (AVL, Red-Black) rotate to
maintain O(log n) height after every insert/delete.

---

### How It Works

**BST operations:**

```java
class BST {
    TreeNode root;

    // Search: O(h) where h = height
    TreeNode search(TreeNode node, int val) {
        if (node == null) return null;       // not found
        if (val == node.val) return node;    // found
        if (val < node.val)
            return search(node.left, val);   // go left
        return search(node.right, val);      // go right
    }

    // Insert: O(h)
    TreeNode insert(TreeNode node, int val) {
        if (node == null) return new TreeNode(val);
        if (val < node.val)
            node.left = insert(node.left, val);
        else if (val > node.val)
            node.right = insert(node.right, val);
        // val == node.val: BST typically ignores duplicates
        return node;
    }

    // In-order traversal: O(n) → visits in SORTED order
    void inOrder(TreeNode node) {
        if (node == null) return;
        inOrder(node.left);
        process(node.val);   // left < current < right
        inOrder(node.right);
    }
}
```

**In-order traversal yields sorted output:**

```
BST:      In-order traversal:
    4          1, 2, 3, 4, 5, 6, 7
   / \
  2   6
 / \ / \
1  3 5  7
```

**Delete is the hard case:**

```
3 cases:
1. Node is leaf: just remove
2. Node has one child: replace with child
3. Node has two children: replace with in-order successor
   (smallest value in right subtree), then delete that successor
```

---

### Comparison Table

| Structure | Search | Insert | Delete | Ordered | Range Query |
|-----------|--------|--------|--------|---------|-------------|
| Array (sorted) | O(log n) | O(n) | O(n) | Yes | O(log n + k) |
| Hash Map | O(1) avg | O(1) avg | O(1) avg | No | Not efficient |
| BST (balanced) | O(log n) | O(log n) | O(log n) | Yes | O(log n + k) |
| BST (unbalanced) | O(n) | O(n) | O(n) | Yes | O(n) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "BST guarantees O(log n)" | Only if balanced; a plain BST degrades to O(n) with sorted insertion |
| "BST and binary tree are the same" | Binary tree: structural constraint (2 children max). BST: binary tree + ordering invariant |
| "HashMap is always better than BST" | BST supports range queries and ordered iteration; HashMap does not |
| "BST deletes are O(log n)" | Delete requires finding in-order successor; O(log n) for balanced, O(n) for degenerate |

---

### Failure Modes & Diagnosis

**Failure 1: Degenerate BST from sorted insertion**
- Symptom: BST operations are O(n) not O(log n)
- Cause: Inserting data in sorted (or nearly sorted) order;
  tree becomes a right-leaning linked list
- Diagnosis: Tree height = n, not log n
- Fix: Use self-balancing tree (TreeMap in Java = Red-Black
  Tree; guarantees O(log n) always)

**Failure 2: BST invariant violation after custom modification**
- Symptom: search() fails to find values that are present
- Cause: Direct node value modification breaks the invariant;
  must delete + re-insert
- Fix: Never modify a node's value directly; use delete + insert

---

### Related Keywords

**Prerequisites:**
- [[DSA-016 - Binary Tree]]

**Builds toward:**
- [[DSA-034 - Tree Traversal (In-Order, Pre-Order, Post-Order, Level-Order)]]
- [[DSA-053 - AVL Tree (Self-Balancing BST)]]
- [[DSA-054 - Red-Black Tree]]

**See also:**
- [[DSA-014 - Hash Map (Hash Table, Dictionary)]]
- [[DSA-020 - Binary Search]]

---

### Quick Reference Card

| Operation | Balanced BST | Degenerate BST |
|-----------|-------------|----------------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Min/Max | O(log n) | O(n) |
| In-order sorted output | O(n) | O(n) |

**Use Java TreeMap:** Red-Black tree, always O(log n).

---

### The Surprising Truth

Java's `TreeMap` and `TreeSet` are Red-Black Trees, not plain
BSTs. You never interact with plain BSTs in production Java -
every "BST" you use is automatically self-balancing.
Plain BSTs exist only as interview problems and as the
conceptual foundation for understanding why balancing matters.

---

### Mastery Checklist

- [ ] Can implement BST search, insert, in-order traversal
      from memory
- [ ] Can explain why sorted insertion creates a degenerate
      BST and why this requires self-balancing trees
- [ ] Understands the difference between Java TreeMap
      (Red-Black Tree) and a plain BST
- [ ] Can identify when to use TreeMap vs HashMap

---

### Think About This

1. You insert 1, 2, 3, 4, 5, 6, 7 into a plain BST in
   order. Draw the resulting tree. What is its height?
   How does this compare to inserting 4, 2, 6, 1, 3, 5, 7?

2. BST in-order traversal returns sorted output. Can you
   implement BST sort (insert all elements, traverse in-order)?
   What is its time complexity? How does it compare to merge sort?

3. **TYPE G:** A codebase uses `ArrayList<Integer>` sorted
   via `Collections.sort()` for a set of integers that
   changes frequently (inserts and deletes). What data
   structure would you suggest, and why?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the BST invariant?

> For every node N: all values in N's left subtree are less
> than N.value; all values in N's right subtree are greater
> than N.value. This applies recursively to all subtrees.
> This invariant is what makes O(log n) search possible.

**Q2 (Medium):** How do you find the k-th smallest element
in a BST?

> In-order traversal of a BST visits nodes in ascending
> order. The k-th node visited is the k-th smallest.
> ```java
> int count = 0;
> int kthSmallest(TreeNode node, int k) {
>     if (node == null) return -1;
>     int left = kthSmallest(node.left, k);
>     if (left != -1) return left;
>     count++;
>     if (count == k) return node.val;
>     return kthSmallest(node.right, k);
> }
> ```
> O(h + k) time where h = height.

**Q3 (Hard):** How does Java TreeMap use a Red-Black Tree
to guarantee O(log n) operations?

> Red-Black Tree maintains balance via 5 properties:
> (1) every node is red or black; (2) root is black;
> (3) all null leaves are black; (4) red node has no red
> child; (5) all paths from node to leaves have same number
> of black nodes. These constraints guarantee height <=
> 2*log2(n+1). After insert/delete, the tree "fixes"
> violations via color flips and rotations in O(log n).
> TreeMap wraps this in the familiar Map interface, giving
> you sorted key iteration, floorKey, ceilingKey, subMap -
> all in O(log n).
