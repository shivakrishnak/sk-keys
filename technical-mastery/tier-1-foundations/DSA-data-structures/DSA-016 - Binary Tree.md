---
id: DSA-016
title: Binary Tree
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-015
used_by: DSA-017, DSA-028, DSA-034, DSA-057, DSA-058
related: DSA-015, DSA-017, DSA-034
tags:
  - data-structures
  - binary-tree
  - tree
  - traversal
  - recursion
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/dsa/binary-tree/
---

## TL;DR

A binary tree is a tree where each node has at most two
children (left and right) - the foundation for BSTs, heaps,
and most tree algorithms.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-016 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, binary-tree, traversal |
| **Prerequisites** | DSA-015 |

---

### The Problem This Solves

General trees with arbitrary child counts are complex to
implement and traverse. Binary trees constrain each node to
at most two children, simplifying both implementation and
algorithm design while still supporting efficient hierarchical
organization.

---

### Textbook Definition

A binary tree is a tree data structure where each node has at
most two children, designated as left and right child. A full
binary tree has every node with either 0 or 2 children. A
complete binary tree fills all levels left-to-right. A perfect
binary tree is both full and complete.

---

### Understand It in 30 Seconds

Each node has at most a left child and a right child.
That's it. This simple constraint enables divide-and-conquer:
to find something, go left or right based on a rule.
Half the tree is eliminated at each step → O(log n).

---

### How It Works

**Node structure:**

```java
class TreeNode<T> {
    T value;
    TreeNode<T> left;
    TreeNode<T> right;

    TreeNode(T value) {
        this.value = value;
    }
}
```

**Tree types:**

```
Full BT:          Complete BT:      Perfect BT:
    A                A                  A
   / \             /   \             /     \
  B   C           B     C           B       C
 / \   \         / \   /           / \     / \
D   E   F       D   E F           D   E   F   G
```

**Height analysis:**
- Perfect binary tree with n nodes: height = log2(n)
- Degenerate (linked list): height = n-1
- Balanced: height = O(log n)

**Common binary tree problems:**

```java
// Height of binary tree (recursive)
int height(TreeNode node) {
    if (node == null) return -1;
    return 1 + Math.max(height(node.left), height(node.right));
}

// Count nodes
int count(TreeNode node) {
    if (node == null) return 0;
    return 1 + count(node.left) + count(node.right);
}

// Check if balanced (height diff <= 1 at every node)
boolean isBalanced(TreeNode node) {
    return checkHeight(node) != Integer.MIN_VALUE;
}
int checkHeight(TreeNode node) {
    if (node == null) return 0;
    int left = checkHeight(node.left);
    if (left == Integer.MIN_VALUE) return Integer.MIN_VALUE;
    int right = checkHeight(node.right);
    if (right == Integer.MIN_VALUE) return Integer.MIN_VALUE;
    if (Math.abs(left - right) > 1) return Integer.MIN_VALUE;
    return 1 + Math.max(left, right);
}
```

---

### Comparison Table

| Type | Nodes per level | Height | Property |
|------|----------------|--------|---------|
| Perfect | 2^k at level k | log n | All levels full |
| Complete | All levels full except last | log n | Last level left-filled |
| Full | 0 or 2 children | log n to n | No nodes with 1 child |
| Degenerate | 1 | n-1 | Each node has 1 child (linked list) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Binary tree and BST are the same" | Binary tree = structural constraint (2 children max); BST = binary tree + ordering constraint |
| "Binary trees are always balanced" | Only self-balancing trees (AVL, Red-Black) maintain balance automatically |
| "Heap is a binary search tree" | A heap is a complete binary tree with the heap property (parent >= or <= children), not the BST ordering |

---

### Failure Modes & Diagnosis

**Failure: NullPointerException in tree traversal**
- Cause: Accessing `node.left` or `node.right` without null
  check; every recursive step must guard against null leaves
- Fix: Base case `if (node == null) return` in every recursive
  method

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Max children | 2 (left and right) |
| Height (balanced) | O(log n) |
| Height (degenerate) | O(n) |
| Traversal types | Pre-order, In-order, Post-order, Level-order |

---

### Mastery Checklist

- [ ] Can implement a binary tree node and basic operations
- [ ] Can calculate height and count nodes recursively
- [ ] Understands the difference between full, complete,
      perfect, and degenerate binary trees
- [ ] Can identify which type of tree a diagram represents

---

### Interview Deep-Dive

**Q1 (Easy):** What is the maximum number of nodes in a
binary tree of height h?

> Perfect binary tree of height h has 2^(h+1) - 1 nodes
> (level 0: 1 node, level 1: 2 nodes, ... level h: 2^h
> nodes; sum = 2^0 + 2^1 + ... + 2^h = 2^(h+1) - 1).

**Q2 (Medium):** How do you check if a binary tree is
symmetric (mirror of itself)?

> Recursive: A tree is symmetric if left subtree is a mirror
> of right subtree.
> ```java
> boolean isSymmetric(TreeNode root) {
>     return isMirror(root.left, root.right);
> }
> boolean isMirror(TreeNode a, TreeNode b) {
>     if (a == null && b == null) return true;
>     if (a == null || b == null) return false;
>     return a.val == b.val
>         && isMirror(a.left, b.right)
>         && isMirror(a.right, b.left);
> }
> ```
