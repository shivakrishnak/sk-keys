---
id: DSA-040
title: Recursion vs Iteration Trade-off
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-022, DSA-026
used_by: DSA-067
related: DSA-026, DSA-034, DSA-067
tags:
  - algorithms
  - recursion
  - iteration
  - trade-off
  - stack-overflow
  - tail-recursion
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/dsa/recursion-vs-iteration/
---

## TL;DR

Recursion mirrors problem structure but uses O(depth) stack
space; iteration uses O(1) space. Java lacks tail-call
optimization - deep recursion always risks StackOverflowError.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-040 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, recursion, iteration, trade-off |
| **Prerequisites** | DSA-022, DSA-026 |

---

### The Problem This Solves

A recursive tree traversal is 4 lines. The iterative
equivalent is 15 lines. But the recursive version crashes
with StackOverflowError on a deep tree. Understanding
when to use which - and how to convert between them -
is a core production skill.

---

### Textbook Definition

**Recursion:** Function calls itself. Uses the JVM call
stack: each call adds a stack frame. Max depth: ~500-1000
frames (JVM default ~512KB thread stack). Space: O(depth).

**Iteration:** Uses explicit loops. Stack frames do not
accumulate. Space: O(1) (or O(n) for explicit data
structure stack if simulating recursion).

**Tail call optimization (TCO):** In languages with TCO
(Scala, Kotlin with `tailrec`, Haskell), tail-recursive
functions are compiled to loops. Java JVM does NOT perform
TCO - tail recursion still uses O(n) stack frames.

---

### How It Works

**Fibonacci: recursion → iteration → O(1) optimization:**

```java
// Recursive: O(2^n) time, O(n) stack space
int fibRec(int n) {
    if (n <= 1) return n;
    return fibRec(n-1) + fibRec(n-2);
}

// Memoized recursion: O(n) time, O(n) memo + O(n) stack
int fibMemo(int n, int[] memo) {
    if (n <= 1) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fibMemo(n-1, memo) + fibMemo(n-2, memo);
}

// Bottom-up iteration: O(n) time, O(n) space
int fibIter(int n) {
    if (n <= 1) return n;
    int[] dp = new int[n + 1];
    dp[1] = 1;
    for (int i = 2; i <= n; i++) dp[i] = dp[i-1] + dp[i-2];
    return dp[n];
}

// Optimized: O(n) time, O(1) space
int fibOptimal(int n) {
    if (n <= 1) return n;
    int prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}
```

**Converting recursive DFS to iterative:**

```java
// Recursive DFS - simple but O(depth) stack
void dfsRec(TreeNode node) {
    if (node == null) return;
    visit(node);
    dfsRec(node.left);
    dfsRec(node.right);
}

// Iterative DFS - explicit stack, safe for deep trees
void dfsIter(TreeNode root) {
    if (root == null) return;
    Deque<TreeNode> stack = new ArrayDeque<>();
    stack.push(root);
    while (!stack.isEmpty()) {
        TreeNode node = stack.pop();
        visit(node);
        // Push right first so left processed first (LIFO)
        if (node.right != null) stack.push(node.right);
        if (node.left != null)  stack.push(node.left);
    }
}
```

---

### Comparison Table

| Aspect | Recursion | Iteration |
|--------|-----------|-----------|
| Code clarity | Better for self-similar problems | Better for simple loops |
| Stack space | O(depth) - can overflow | O(1) - no overflow |
| Java TCO | None - always O(depth) stack | N/A |
| Debugging | Harder (stack trace deep) | Easier (flat flow) |
| Best for | Trees, DFS, divide-and-conquer | Simple scans, DP |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java optimizes tail recursion" | Java JVM (HotSpot) does NOT perform TCO; tail-recursive Java code still uses O(n) stack frames |
| "Recursion is always slower than iteration" | Negligible overhead per call; the issue is stack depth, not speed |
| "Any recursion can be converted to iteration easily" | Tree traversal conversions need explicit stacks; mutual recursion is harder to convert |

---

### Failure Modes & Diagnosis

**Failure: StackOverflowError in production**
- Cause: Deep recursion (e.g., recursive processing of
  10,000-node linked list or deep tree)
- Diagnosis: Stack trace shows repeated method frames
- Fix options: (1) Convert to iterative; (2) Increase JVM
  stack size via `-Xss` (risk: OOM); (3) Use trampolining
  (simulate TCO in Java manually)

---

### Quick Reference Card

| When to use recursion | When to use iteration |
|----------------------|----------------------|
| Tree/graph traversal (bounded depth) | Fibonacci, sum, loops |
| Divide and conquer | Deep traversal (depth > 500) |
| Backtracking | Simple array/list scans |
| Natural self-similar structure | Memory-constrained context |

---

### Mastery Checklist

- [ ] Can convert any simple recursive function to
      iterative
- [ ] Can convert recursive tree DFS to iterative using
      explicit stack
- [ ] Knows Java has no tail-call optimization
- [ ] Can explain when StackOverflowError risk is real
      vs theoretical

---

### Interview Deep-Dive

**Q1 (Medium):** How would you convert a recursive
in-order BST traversal to iterative?

> Use an explicit stack. Simulate the recursive call stack:
> (1) Go as far left as possible, pushing each node. (2)
> When null is reached, pop and visit the top node. (3)
> Move to its right subtree, repeat. This mirrors the
> recursion exactly without using the JVM call stack.
> ```java
> void inOrderIterative(TreeNode root) {
>     Deque<TreeNode> stack = new ArrayDeque<>();
>     TreeNode curr = root;
>     while (curr != null || !stack.isEmpty()) {
>         while (curr != null) {
>             stack.push(curr);
>             curr = curr.left;
>         }
>         curr = stack.pop();
>         visit(curr);
>         curr = curr.right;
>     }
> }
> ```
> O(n) time, O(h) space where h = height.
