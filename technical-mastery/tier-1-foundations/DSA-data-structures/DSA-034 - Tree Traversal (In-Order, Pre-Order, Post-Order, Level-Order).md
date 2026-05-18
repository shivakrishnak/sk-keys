---
id: DSA-034
title: "Tree Traversal (In-Order, Pre-Order, Post-Order, Level-Order)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-016, DSA-026
used_by: DSA-035, DSA-036
related: DSA-016, DSA-017, DSA-035, DSA-036
tags:
  - algorithms
  - tree
  - traversal
  - dfs
  - bfs
  - recursion
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/dsa/tree-traversal/
---

## TL;DR

Tree traversal visits every node exactly once in a defined
order: in-order (sorted for BST), pre-order (copy/serialize),
post-order (delete/evaluate), and level-order (BFS shortest
path).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-034 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, tree, traversal, DFS, BFS |
| **Prerequisites** | DSA-016, DSA-026 |

---

### The Problem This Solves

A tree has no natural linear order. To visit all nodes (to
print, search, copy, or evaluate), you must choose an order.
Each traversal order serves different use cases:
- In-order: sorted output from BST
- Pre-order: copy structure, serialize tree
- Post-order: delete tree, evaluate expression tree
- Level-order: find shortest path, process nodes by depth

---

### Textbook Definition

**Depth-First Traversals** (use recursion or explicit stack):
- In-order: Left → Root → Right. For BST: visits nodes in
  ascending sorted order.
- Pre-order: Root → Left → Right. Root first; useful for
  tree serialization (you can reconstruct the tree).
- Post-order: Left → Right → Root. Root last; useful for
  deletion (children before parent) and expression trees.

**Breadth-First (Level-Order):** Visit all nodes at depth d
before any nodes at depth d+1. Uses a queue. Finds shortest
path in unweighted trees/graphs.

---

### Understand It in 30 Seconds

```
        4
       / \
      2   6
     / \ / \
    1  3 5  7

In-order:    1, 2, 3, 4, 5, 6, 7  (sorted!)
Pre-order:   4, 2, 1, 3, 6, 5, 7  (root first)
Post-order:  1, 3, 2, 5, 7, 6, 4  (root last)
Level-order: 4, 2, 6, 1, 3, 5, 7  (row by row)
```

---

### How It Works

**All four traversals:**

```java
// In-order: Left, Root, Right
void inOrder(TreeNode node) {
    if (node == null) return;
    inOrder(node.left);
    visit(node);         // between children
    inOrder(node.right);
}

// Pre-order: Root, Left, Right
void preOrder(TreeNode node) {
    if (node == null) return;
    visit(node);         // before children
    preOrder(node.left);
    preOrder(node.right);
}

// Post-order: Left, Right, Root
void postOrder(TreeNode node) {
    if (node == null) return;
    postOrder(node.left);
    postOrder(node.right);
    visit(node);         // after children
}

// Level-order: BFS with queue
void levelOrder(TreeNode root) {
    if (root == null) return;
    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);
    while (!queue.isEmpty()) {
        TreeNode node = queue.poll();
        visit(node);
        if (node.left != null)  queue.offer(node.left);
        if (node.right != null) queue.offer(node.right);
    }
}
```

**Iterative in-order (avoids recursion, O(1) extra space):**

```java
void inOrderIterative(TreeNode root) {
    Deque<TreeNode> stack = new ArrayDeque<>();
    TreeNode curr = root;
    while (curr != null || !stack.isEmpty()) {
        // Go to leftmost node
        while (curr != null) {
            stack.push(curr);
            curr = curr.left;
        }
        // Visit node, then go right
        curr = stack.pop();
        visit(curr);
        curr = curr.right;
    }
}
```

---

### Comparison Table

| Traversal | Visit order | Stack/Queue | Use case |
|-----------|------------|-------------|---------|
| In-order | L → N → R | Stack (recursion) | BST sorted output |
| Pre-order | N → L → R | Stack (recursion) | Serialize/copy tree |
| Post-order | L → R → N | Stack (recursion) | Delete tree, evaluate expr |
| Level-order | Row by row | Queue (BFS) | Shortest path, tree levels |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "In-order traversal gives sorted output for any tree" | Only for BST; for general binary tree, in-order output has no guaranteed order |
| "Level-order is a DFS" | Level-order is BFS (uses a queue); DFS (pre/in/post-order) uses a stack |
| "Traversal modifies the tree" | Traversal is read-only; the visit() operation determines what happens, not the traversal itself |

---

### Failure Modes & Diagnosis

**Failure: StackOverflowError on deep tree traversal**
- Cause: Recursive traversal on a degenerate tree (height n)
  exhausts call stack
- Fix: Use iterative traversal (explicit stack) for any
  tree of unknown depth

---

### Quick Reference Card

| Traversal | Mnemonic | Queue/Stack |
|-----------|---------|------------|
| Pre-order | Root before kids | Stack |
| In-order | Root between kids | Stack |
| Post-order | Root after kids | Stack |
| Level-order | Floor by floor | Queue |

---

### Mastery Checklist

- [ ] Can write all four traversals from memory
- [ ] Knows the BST in-order → sorted output property
- [ ] Understands which traversal to use for which problem
- [ ] Can write iterative in-order traversal

---

### Interview Deep-Dive

**Q1 (Easy):** Given a BST, print all nodes in sorted order.

> In-order traversal: visit left subtree, visit root,
> visit right subtree. For any BST, in-order traversal
> visits nodes in ascending sorted order because all
> left subtree values are less than root, and all right
> subtree values are greater. O(n) time.

**Q2 (Medium):** How do you find the maximum depth of a
binary tree?

> Post-order recursion: depth(node) = 1 + max(depth(left),
> depth(right)). Base case: null node = 0.
> ```java
> int maxDepth(TreeNode node) {
>     if (node == null) return 0;
>     return 1 + Math.max(maxDepth(node.left),
>                         maxDepth(node.right));
> }
> ```
> This is post-order: compute children before root. O(n).
