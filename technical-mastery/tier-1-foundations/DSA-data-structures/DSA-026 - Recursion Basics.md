---
id: DSA-026
title: Recursion Basics
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-004, DSA-022
used_by: DSA-034, DSA-035, DSA-036, DSA-066, DSA-068
related: DSA-068, DSA-069, DSA-070
tags:
  - algorithms
  - recursion
  - call-stack
  - base-case
  - divide-and-conquer
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/dsa/recursion-basics/
---

## TL;DR

Recursion solves problems by having a function call itself
on a smaller subproblem until a base case is reached -
the foundation of tree traversal, DFS, and divide-and-conquer.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-026 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, recursion, call-stack, base-case |
| **Prerequisites** | DSA-004, DSA-022 |

---

### The Problem This Solves

Some problems are naturally self-similar: a tree is a root
plus smaller trees; a factorial is n times a smaller
factorial; a directory contains files and sub-directories.
Recursion mirrors this structure directly - often making
code shorter and clearer than iterative equivalents.

---

### Textbook Definition

Recursion is a technique where a function calls itself with
a reduced version of the original problem. Every recursive
solution requires: (1) a base case - the simplest version
of the problem that can be answered directly; (2) a recursive
case - breaking the problem into a smaller subproblem and
combining results. Without a correct base case, recursion
leads to infinite calls and a stack overflow.

---

### Understand It in 30 Seconds

```
factorial(4)
= 4 * factorial(3)
= 4 * (3 * factorial(2))
= 4 * (3 * (2 * factorial(1)))
= 4 * (3 * (2 * 1))   ← base case
= 4 * (3 * 2)
= 4 * 6
= 24
```

Each call is on the call stack until base case is reached,
then results unwind back up.

---

### How It Works

**BAD - missing base case:**

```java
// BUG: no base case → StackOverflowError
int factorial(int n) {
    return n * factorial(n - 1);  // never stops
}
```

**GOOD - correct recursive structure:**

```java
// Base case + recursive case
int factorial(int n) {
    if (n <= 1) return 1;          // base case
    return n * factorial(n - 1);   // recursive case
}
// Stack depth = n → O(n) space
// Time = O(n)
```

**The call stack visualization:**

```
factorial(4)           ← pushed first
  factorial(3)         ← pushed
    factorial(2)       ← pushed
      factorial(1)     ← base case, returns 1
    returns 2*1 = 2
  returns 3*2 = 6
returns 4*6 = 24
```

**Recursive tree traversal (the natural case for recursion):**

```java
// In-order BST traversal: recursion mirrors tree structure
void inOrder(TreeNode node) {
    if (node == null) return;         // base case
    inOrder(node.left);               // recurse left
    System.out.println(node.value);   // process
    inOrder(node.right);              // recurse right
}
```

**Recursive vs iterative - the tail recursion case:**

```java
// Recursive: O(n) stack space
int sum(int n) {
    if (n == 0) return 0;
    return n + sum(n - 1);
}

// Iterative: O(1) stack space (always prefer for simple loops)
int sumIterative(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) total += i;
    return total;
    // Or: return n * (n + 1) / 2  // O(1)
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Recursion is always elegant and preferred" | For simple iterations (sum, reverse), iterative is O(1) space vs O(n) recursive stack. Use recursion where problem structure is self-similar (trees, DFS) |
| "Recursion is slow" | Overhead is one function call per level - negligible for O(log n) depth. O(n) depth (like factorial) accumulates O(n) stack frames |
| "Tail recursion optimizes stack in Java" | Java does NOT perform tail-call optimization (unlike functional languages). Tail recursion in Java still uses O(n) stack space |

---

### Failure Modes & Diagnosis

**Failure 1: StackOverflowError**
- Cause: Missing base case, or recursion depth exceeds JVM
  thread stack size (default ~500-1000 frames)
- Diagnosis: Stack trace shows the same method repeated
  hundreds of times
- Fix: Add correct base case; convert to iterative for deep
  recursion; or increase stack size (-Xss JVM flag)

**Failure 2: Exponential time from repeated subproblems**
- Cause: `fib(n) = fib(n-1) + fib(n-2)` recomputes fib(n-2)
  for both calls → O(2^n) time
- Fix: Memoization (cache computed values) or bottom-up DP

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Requires | Base case + recursive case |
| Space | O(depth) call stack frames |
| When to use | Tree/graph traversal, divide-and-conquer, backtracking |
| When to avoid | Simple loops (O(n) space vs O(1) iterative) |
| Java stack limit | ~500-1000 frames default; large recursion → StackOverflow |

---

### Mastery Checklist

- [ ] Can identify base case and recursive case in any
      recursive function
- [ ] Understands that recursion uses O(depth) stack space
- [ ] Knows Java does not optimize tail recursion
- [ ] Can convert simple recursion to iteration to save
      stack space

---

### Think About This

1. Write a recursive function to compute the sum of
   digits of a number (e.g., 1234 → 10). What is the
   depth? Is iteration better here?

2. Fibonacci using naive recursion is O(2^n). Draw the
   recursion tree for fib(5). How many total calls are
   made? Where is the redundancy?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the base case, and why is it
required for recursion?

> The base case is the simplest version of the problem
> that can be answered directly without further recursion.
> Without it, the function calls itself indefinitely,
> exhausting the call stack and causing StackOverflowError.
> The base case is what guarantees termination: each
> recursive call must bring the problem closer to the base
> case (usually by reducing n, shrinking an array, or
> moving to a smaller tree node).

**Q2 (Medium):** What is the space complexity of recursive
tree traversal for a balanced vs unbalanced tree?

> Space complexity is O(h) where h = tree height, because
> at most h stack frames are active simultaneously (the
> deepest path from root to leaf). For a balanced tree,
> h = O(log n), so space = O(log n). For a degenerate
> (linked-list-like) tree, h = O(n), so space = O(n).
> This is a key reason why unbalanced trees are dangerous:
> they degrade both time AND space complexity.
