---
id: DSA-015
title: Tree (General Tree Concept)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-002, DSA-010
used_by: DSA-016, DSA-017, DSA-034, DSA-053, DSA-056
related: DSA-016, DSA-017, DSA-018
tags:
  - data-structures
  - tree
  - hierarchical
  - graph
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/dsa/tree/
---

## TL;DR

A tree is a hierarchical data structure of nodes connected by
directed edges with no cycles - the model behind file systems,
org charts, HTML DOM, and all search-tree structures.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-015 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, tree, hierarchical |
| **Prerequisites** | DSA-002, DSA-010 |

---

### The Problem This Solves

Many real-world relationships are hierarchical - a company
has departments which have teams which have employees. Flat
lists cannot represent this structure efficiently. Trees
provide the natural model for hierarchical data with
efficient traversal and search.

---

### Textbook Definition

A tree is a connected acyclic directed graph with a
designated root node. Every node except the root has exactly
one parent. Nodes with no children are leaves. The depth of
a node is its distance from the root. The height of a tree
is the maximum depth of any leaf.

---

### Understand It in 30 Seconds

Your company org chart: CEO at the top, VPs below, Directors
below VPs, ICs at the bottom. Each person has exactly one
manager (parent). People at the bottom have no reports
(leaves). The CEO has no manager (root).

---

### How It Works

**Tree terminology:**

```
         root (A)         depth 0
        /       \
      (B)       (C)       depth 1
     /   \       |
   (D)   (E)   (F)        depth 2  <- leaves D, E, F

root: A (no parent)
parent of B: A
children of B: D, E
siblings of D: E
leaf: D, E, F (no children)
height of tree: 2
```

**Tree types and their use cases:**

| Tree Type | Property | Use Case |
|-----------|----------|---------|
| General tree | Any number of children | File system, org chart |
| Binary tree | Max 2 children | Expression trees |
| BST | Left < root < right | Sorted search |
| AVL/Red-Black | Self-balancing BST | Guaranteed O(log n) |
| B-Tree | Many children, disk-friendly | Database indexes |
| Trie | Characters in edges | Autocomplete, prefix search |
| Heap | Parent >= or <= children | Priority queue |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "A graph with no cycles is always a tree" | A forest (disconnected acyclic graph) is not a tree; a tree is connected + acyclic |
| "All trees are binary trees" | Binary trees are a special case; general trees can have any number of children |
| "Trees are just for search" | DOM, file systems, compilers (AST), organization charts, decision trees - all are trees |

---

### Failure Modes & Diagnosis

**Failure: Stack overflow on deep tree recursion**
- Symptom: StackOverflowError on deep tree traversal
- Cause: Recursion depth exceeds JVM stack size for trees
  with thousands of levels
- Fix: Convert to iterative traversal using explicit stack

---

### Quick Reference Card

| Concept | Definition |
|---------|-----------|
| Root | Node with no parent |
| Leaf | Node with no children |
| Depth | Distance from root |
| Height | Max depth of any leaf |
| Subtree | Node + all its descendants |
| Balanced | Height is O(log n) |

---

### Mastery Checklist

- [ ] Can draw and label a tree with root, leaves, depth,
      height, parent, children
- [ ] Understands that a binary tree is a special case of
      a general tree
- [ ] Can name 5 real systems that use tree structures

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between depth and
height in a tree?

> Depth: distance from root to a specific node (root has
> depth 0). Height: the maximum depth of any leaf in the tree.
> A single-node tree has depth 0 and height 0. Height is a
> property of the tree; depth is a property of a node.

**Q2 (Medium):** Why is a balanced tree important for
search performance?

> A balanced tree has height O(log n). BST search is O(height).
> A balanced BST: O(log n) search. An unbalanced BST
> (e.g. inserting sorted data into a plain BST creates a
> linked list): O(n) search. Balance guarantees that the
> tree's height stays logarithmic, maintaining O(log n)
> operations regardless of insertion order.
