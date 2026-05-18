---
id: DSA-012
title: Stack (LIFO)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-008, DSA-010
used_by: DSA-024, DSA-026, DSA-029, DSA-035, DSA-068
related: DSA-013, DSA-026
tags:
  - data-structures
  - stack
  - lifo
  - fundamentals
  - call-stack
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/dsa/stack/
---

## TL;DR

A stack is a LIFO (Last-In, First-Out) collection with O(1)
push and pop - the structure behind function call management,
undo systems, and depth-first search.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-012 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, stack, LIFO, call-stack |
| **Prerequisites** | DSA-008, DSA-010 |

---

### The Problem This Solves

Many problems require processing items in reverse order of
arrival, or require tracking "where you came from" to return
when done. Function calls, browser history, expression
evaluation, and DFS all share this "last-visited, first-
returned" structure. The stack formalizes this pattern.

---

### Textbook Definition

A stack is an abstract data type that stores elements and
enforces Last-In, First-Out (LIFO) access. Only the top
element is accessible. Operations: push(x) adds to the top,
pop() removes and returns the top, peek() returns the top
without removing. All three are O(1).

---

### Understand It in 30 Seconds

Stack of plates. Put a plate on top: push. Take the top
plate: pop. Look at the top plate without taking it: peek.

The bottom plate is always added first and leaves last.
The most recently added plate is always removed first.

---

### First Principles

**Why LIFO enables recursive problems:**
When a function calls another function, the CPU must remember
where to return. It pushes the return address onto the call
stack. When the function returns, the address is popped.
Recursive calls push multiple frames; returns pop them in
reverse order. LIFO is the natural model for "undo" of
sequential actions.

---

### How It Works

**Java ArrayDeque-based stack (preferred):**

```java
// BAD: using legacy java.util.Stack (synchronized, slow)
Stack<Integer> stack = new Stack<>();
stack.push(1);
stack.push(2);
int top = stack.pop(); // 2

// GOOD: ArrayDeque as stack (faster, not synchronized)
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);  // addFirst()
stack.push(2);
int top = stack.pop();  // removeFirst() → 2
int peek = stack.peek(); // peekFirst() → 1
```

**Call stack in action:**

```
main() calls foo() calls bar():
Call stack:
+--------+  <- top
| bar()  |  push when bar() entered
| foo()  |  push when foo() entered
| main() |  push at program start
+--------+

bar() returns: pop bar() frame → execution resumes in foo()
foo() returns: pop foo() frame → execution resumes in main()
```

---

### Comparison Table

| | Stack | Queue | Deque |
|--|-------|-------|-------|
| Order | LIFO | FIFO | Both |
| Add | push (top) | enqueue (back) | both ends |
| Remove | pop (top) | dequeue (front) | both ends |
| Use case | DFS, undo, call | BFS, task queue | sliding window |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java Stack class is the best stack" | `java.util.Stack` extends Vector (synchronized); use `ArrayDeque` instead |
| "Stacks are only for function calls" | Expression parsing, DFS, undo/redo, parenthesis validation all use stacks |
| "You need a linked list for a stack" | ArrayDeque is faster than LinkedList for stack operations |

---

### Failure Modes & Diagnosis

**Failure: StackOverflowError**
- Symptom: JVM crashes with StackOverflowError
- Cause: Infinite recursion or recursion depth exceeds JVM
  thread stack size (default 512KB-1MB)
- Diagnosis: Stack trace shows repeating method calls
- Fix: Add base case; convert deep recursion to iterative
  using explicit stack

**Failure: EmptyStackException on pop()**
- Symptom: Exception when popping empty stack
- Cause: No isEmpty() check before pop()
- Fix: Always guard with `if (!stack.isEmpty())` before pop

---

### Quick Reference Card

| Operation | Complexity | Java method (ArrayDeque) |
|-----------|-----------|--------------------------|
| push(x) | O(1) | `deque.push(x)` |
| pop() | O(1) | `deque.pop()` |
| peek() | O(1) | `deque.peek()` |
| isEmpty() | O(1) | `deque.isEmpty()` |
| size() | O(1) | `deque.size()` |

**Use cases:** DFS traversal, undo/redo, parenthesis validation,
expression evaluation, browser back navigation.

---

### The Surprising Truth

The CPU's call stack is the stack data structure implemented
in hardware. The `RSP` register on x86 is the stack pointer.
`PUSH` and `POP` are native CPU instructions. The abstract
"stack" you program with is literally the same hardware
mechanism managing every function call.

---

### Mastery Checklist

- [ ] Can implement a stack using ArrayDeque and array
- [ ] Can solve "valid parentheses" problem using a stack
- [ ] Can convert recursive DFS to iterative using explicit
      stack
- [ ] Knows why `java.util.Stack` is deprecated in favor
      of `ArrayDeque`

---

### Think About This

1. Implement a stack that supports `push`, `pop`, `peek`,
   and `getMin()` (returns minimum element) all in O(1).
   How does a second stack help?

2. Given an expression like `3 + (4 * 2) - (1 + 5)`, how
   would you evaluate it using two stacks (one for
   operators, one for operands)?

3. **TYPE G:** Your application has StackOverflowErrors
   appearing under load but not in development. What is
   the likely cause, and how do you diagnose and fix it?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between push, pop,
and peek?

> push: add element to top of stack, O(1).
> pop: remove AND return top element, O(1). Stack shrinks.
> peek: return top element WITHOUT removing it, O(1).
>   Stack unchanged. Use peek when you need the top value
>   but may not want to remove it yet.

**Q2 (Medium):** How do you validate balanced parentheses
using a stack?

> For each character:
> - If opening bracket `(`, `[`, `{`: push onto stack
> - If closing bracket `)`, `]`, `}`:
>   if stack is empty or top doesn't match: return false
>   else: pop the opening bracket
> After all characters: valid if stack is empty.
> O(n) time, O(n) space.

**Q3 (Hard):** Convert recursive DFS to iterative using
an explicit stack. Why would you do this?

> ```java
> void dfsIterative(Node root) {
>     Deque<Node> stack = new ArrayDeque<>();
>     stack.push(root);
>     while (!stack.isEmpty()) {
>         Node node = stack.pop();
>         process(node);
>         // push right first so left is processed first
>         if (node.right != null) stack.push(node.right);
>         if (node.left != null) stack.push(node.left);
>     }
> }
> ```
> Reason: deep trees cause StackOverflowError with recursion
> (JVM default stack ~512KB = ~5000-10000 frames). An
> explicit stack on the heap is unbounded (until heap OOM).
> Also avoids function call overhead for each frame.
