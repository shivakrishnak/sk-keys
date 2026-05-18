---
id: DSA-053
title: AVL Tree (Self-Balancing BST)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-017
used_by: DSA-054
related: DSA-017, DSA-054, DSA-055
tags:
  - data-structures
  - avl-tree
  - self-balancing
  - bst
  - rotations
  - o-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/dsa/avl-tree/
---

## TL;DR

An AVL tree enforces that every node's left and right
subtrees differ in height by at most 1 - guaranteeing
O(log n) operations via rotations after every insert/delete.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-053 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, AVL-tree, self-balancing, rotations |
| **Prerequisites** | DSA-017 |

---

### The Problem This Solves

A plain BST degrades to O(n) for sorted insertions. AVL
trees (Adelson-Velsky and Landis, 1962) were the first
self-balancing BSTs. They maintain strict balance via
rotations, guaranteeing O(log n) for all operations -
the theoretical foundation for TreeMap's Red-Black Tree.

---

### Textbook Definition

An AVL tree is a BST where for every node, the balance
factor (height(left) - height(right)) is in {-1, 0, +1}.
After each insert or delete, the tree re-balances by
walking up the modified path and applying rotations at
the first unbalanced node. Four rotation cases: Left-Left,
Right-Right, Left-Right, Right-Left.

---

### Understand It in 30 Seconds

```
Insert 3, 2, 1 into plain BST:        AVL fixes imbalance:
    3                                      2
     \  ← wait no, left-left            /   \
      2   imbalance at 3               1     3
     /    (balance = -2)
    1     → Right-rotate at 3

Balance factor at every node must be -1, 0, or +1.
Violation → rotate to restore balance.
```

---

### How It Works

**Balance factor and rotation decision:**

```
After insert, walk up to find first node with |bf| > 1.

Case 1: Left-Left (bf = +2, left child bf = +1)
→ Right rotation at unbalanced node

Case 2: Right-Right (bf = -2, right child bf = -1)
→ Left rotation at unbalanced node

Case 3: Left-Right (bf = +2, left child bf = -1)
→ Left rotate left child, then Right rotate node

Case 4: Right-Left (bf = -2, right child bf = +1)
→ Right rotate right child, then Left rotate node
```

**Right rotation (the core operation):**

```java
TreeNode rightRotate(TreeNode y) {
    TreeNode x = y.left;
    TreeNode T2 = x.right;

    // Rotation
    x.right = y;
    y.left = T2;

    // Update heights (y first, then x since x is now parent)
    y.height = 1 + Math.max(height(y.left), height(y.right));
    x.height = 1 + Math.max(height(x.left), height(x.right));

    return x; // x is the new root
}
```

**Height guarantee:**
AVL tree with n nodes: height <= 1.44 * log2(n).
Plain BST worst case: height = n.

---

### Comparison Table

| Property | BST | AVL | Red-Black Tree |
|---------|-----|-----|----------------|
| Height guarantee | None | 1.44 log n | 2 log n |
| Search | O(n) worst | O(log n) | O(log n) |
| Insert rotations | 0 | Up to 2 | Up to 2 |
| Delete rotations | 0 | O(log n) | Up to 3 |
| Rebalancing cost | None | Higher | Lower |
| Lookup speed | Fastest (if balanced) | Fastest balanced | Slightly slower |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "AVL trees are used in Java TreeMap" | Java TreeMap uses Red-Black Trees, not AVL trees. Red-Black allows slightly worse height (2 log n vs 1.44 log n) but fewer rotations on delete |
| "AVL tree rotations are O(log n)" | A single rotation is O(1); after insert, at most 2 rotations needed; after delete, O(log n) rotations possible |

---

### Quick Reference Card

| Operation | Time | Rotations |
|-----------|------|-----------|
| Search | O(log n) | 0 |
| Insert | O(log n) | ≤ 2 |
| Delete | O(log n) | ≤ O(log n) |
| Height bound | 1.44 log2(n) | - |

---

### The Surprising Truth

AVL trees require more rotations on delete than Red-Black
trees (O(log n) vs O(1) for RB). This is why database
indexes and Java's TreeMap use Red-Black Trees rather than
AVL trees - lower write amplification under mixed
insert/delete workloads. AVL trees win only for
read-heavy workloads where the stricter height balance
translates to faster lookups.

---

### Mastery Checklist

- [ ] Can identify all 4 rotation cases from a diagram
- [ ] Understands AVL vs Red-Black trade-off
      (more balanced vs fewer rotations)
- [ ] Knows Java TreeMap uses Red-Black, not AVL

---

### Interview Deep-Dive

**Q1 (Hard):** Why does Java use Red-Black Tree instead
of AVL tree in TreeMap?

> Red-Black trees allow a height up to 2*log2(n+1) vs
> AVL's 1.44*log2(n). The slightly worse height means
> slightly slower lookups. However, Red-Black trees
> require at most 2 rotations on insert and 3 on delete.
> AVL trees require up to O(log n) rotations on delete.
> For a map under heavy insert/delete workload (which
> TreeMap faces in real applications), Red-Black's
> O(1) amortized rotations per modification dominates.
> AVL trees are preferred for read-heavy, rarely-modified
> data where the tighter height bound pays off.
