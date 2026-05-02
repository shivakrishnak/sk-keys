---
layout: default
title: "Stack"
parent: "Data Structures & Algorithms"
nav_order: 33
permalink: /dsa/stack/
number: "0033"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, LinkedList
used_by: DFS, Backtracking, Recursion vs Iteration Trade-offs
related: Queue / Deque, Recursion, Call Stack
tags:
  - datastructure
  - foundational
  - algorithm
---

# 033 — Stack

⚡ TL;DR — A Stack enforces last-in, first-out (LIFO) order so the most recently added item is always processed first.

| #033 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList | |
| **Used by:** | DFS, Backtracking, Recursion vs Iteration Trade-offs | |
| **Related:** | Queue / Deque, Recursion, Call Stack | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Imagine evaluating a mathematical expression like `3 + (4 * (2 + 1))`. You are reading it left to right. When you hit the inner parenthesis, you must remember you were in the middle of the outer multiplication and, before that, the outer addition. Without a disciplined structure, you either need a complex recursive parser or you lose track of "where you were" when stepping back out of nested constructs.

THE BREAKING POINT:
Nested processing — function calls, expression parsing, undo history, browser back navigation — all share a pattern: "go in, do something, come back out and resume exactly where you left off." An unordered collection cannot enforce this resume-in-reverse-order guarantee.

THE INVENTION MOMENT:
If you restrict a collection to add-to-top and remove-from-top only, the structure automatically guarantees that whatever you added most recently is what you get back first. This mirrors how function call frames work in hardware. This is exactly why the Stack was created.

---

### 📘 Textbook Definition

A **Stack** is an abstract data type that implements a collection with two primary operations: `push` (add an element to the top) and `pop` (remove and return the top element). It enforces Last-In, First-Out (LIFO) ordering: the element most recently pushed is always the next to be popped. `peek` (or `top`) reads the top element without removing it. All three operations are O(1).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A pile where you can only add or remove from the top.

**One analogy:**
> A stack of cafeteria trays: the last tray put on the pile is the first one taken. You cannot pull a tray from the middle without first removing all trays above it.

**One insight:**
A Stack's value is not what it stores — it's the *order guarantee* it enforces. Any code that needs "undo the last thing first" or "process the most nested context first" can delegate that bookkeeping to a Stack rather than writing custom tracking logic.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Elements are always added to and removed from the same end (the "top").
2. No element below the top is accessible without first removing all elements above it.
3. All operations (push, pop, peek) are O(1).

DERIVED DESIGN:
The LIFO invariant means the implementation only needs to track the top. An array with a `top` pointer or a linked list with a `head` pointer both suffice. The array implementation has better cache locality and lower overhead; the linked list handles unbounded growth without a resize copy.

Why not use a general deque or list? You could, but exposing only `push`/`pop`/`peek` provides an explicitly enforced contract — callers cannot accidentally access the middle of the stack. This is the interface-as-constraint principle.

THE TRADE-OFFS:
Gain: O(1) push/pop/peek, enforced LIFO semantics simplify nested-processing code.
Cost: Only the top is accessible; retrieving arbitrary elements requires popping and saving everything above.

---

### 🧪 Thought Experiment

SETUP:
You are implementing browser back-navigation. Each page visit should allow the user to press "back" and return to the previous page.

WHAT HAPPENS WITHOUT STACK:
You store URLs in an array with an integer `currentIndex`. Going back means `currentIndex--`. But when you visit a new page after going back, you must handle the "forward" history too. You write complex array-management code tracking forward/backward state, and it's easy to get wrong.

WHAT HAPPENS WITH STACK:
Push each new URL visited. "Back" is a `pop`. Navigate forward invalidates the forward stack. The back-navigation history is the stack itself; no index arithmetic, no manual cursor.

THE INSIGHT:
The Stack's LIFO guarantee is not just about storage — it's about making "reverse-order processing" a zero-logic operation. The discipline of the data structure replaces the discipline of manual bookkeeping.

---

### 🧠 Mental Model / Analogy

> A Stack is like the "Undo" list in a text editor. Every action is pushed on the undo stack. Pressing Ctrl+Z pops the top action and reverses it. You can only undo in reverse order of how you typed — the structure enforces the contract automatically.

"Undo action pushed" → `push(action)`
"Ctrl+Z reverses last action" → `pop()` then apply reverse
"See what would be undone" → `peek()`
"Can't undo actions from the middle" → no random access

Where this analogy breaks down: Some editors support selective undo (undo a specific action, not necessarily the last). That feature requires a more complex structure than a plain stack.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A stack is a pile where you can only add to or take from the top. The last thing you put on is always the first thing you get back.

**Level 2 — How to use it (junior developer):**
In Java, use `Deque<T> stack = new ArrayDeque<>()`. Use `push()` to add, `pop()` to remove, `peek()` to look. Avoid `java.util.Stack` — it extends `Vector` and is synchronized unnecessarily. `ArrayDeque` is the modern replacement. Check `isEmpty()` before `pop()` to avoid `EmptyStackException`.

**Level 3 — How it works (mid-level engineer):**
`ArrayDeque` uses a resizable circular array. `push` maps to `addFirst`, `pop` maps to `removeFirst`. The head index moves forward on `addFirst`, backward on `removeFirst`, wrapping around with modular arithmetic. Capacity doubles when full (amortized O(1) push). All operations touch only the head — no shifting.

**Level 4 — Why it was designed this way (senior/staff):**
The JVM's call stack is itself a hardware-level Stack: each `invokevirtual` bytecode pushes a stack frame (local variables + operand stack); `return` pops it. This is why recursive algorithms have a natural stack analogy and can be re-implemented iteratively using an explicit Stack. Stack-based architectures (JVM, Python interpreter, WASM) are simpler and more portable than register-based architectures, which is why language VMs often choose them.

---

### ⚙️ How It Works (Mechanism)

**Array-backed Stack (ArrayDeque internals):**
```
Capacity: 16 (initial default)
head pointer: 0 (next push goes here)

push("A"):  elements[head=15] = "A"; head = 15 (wrap)
push("B"):  elements[head=14] = "B"; head = 14
pop():      val = elements[head=14]; head = 15; return "B"
```

┌──────────────────────────────────────────────┐
│  Stack (ArrayDeque push/pop)                 │
│                                              │
│  push(C)    push(B)   push(A)               │
│    ↓          ↓         ↓                   │
│  [C][B][A][_][_][_] ← top = index 2         │
│                                              │
│  pop() → A (top moves left)                 │
│  pop() → B                                  │
│  pop() → C                                  │
└──────────────────────────────────────────────┘

**Linked-list Stack:**
```
Push: newNode.next = head; head = newNode
Pop:  val = head.data; head = head.next; return val
```
Head pointer = top of stack. Both are O(1) with no shifting.

**DFS via explicit Stack (avoids call stack overflow):**
```java
Deque<Node> stack = new ArrayDeque<>();
stack.push(root);
while (!stack.isEmpty()) {
    Node curr = stack.pop();
    process(curr);
    if (curr.right != null) stack.push(curr.right);
    if (curr.left  != null) stack.push(curr.left);
}
```
This replaces recursion, avoids `StackOverflowError` for deep trees.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Nested call or action begins
→ State pushed to Stack [STACK ← YOU ARE HERE]
→ Inner operation executes
→ Inner operation completes
→ State popped from Stack
→ Outer context resumes
```

FAILURE PATH:
```
Recursive algorithm on deep input without explicit Stack
→ Each call pushes a JVM stack frame
→ JVM stack depth limit exceeded (~500–1000 frames default)
→ StackOverflowError thrown
→ Fix: use explicit Stack on heap instead
```

WHAT CHANGES AT SCALE:
At scale (millions of events per second), the overhead of `ArrayDeque` is negligible — all operations touch one cache line. The risk at scale is stack depth: a DFS on a graph with 1M nodes will overflow the JVM call stack if implemented recursively. Always use an explicit stack for graph traversal at production scale.

---

### 💻 Code Example

**Example 1 — Balanced parentheses check:**
```java
boolean isBalanced(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '[' || c == '{') {
            stack.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (stack.isEmpty()) return false;
            char top = stack.pop();
            if ((c == ')' && top != '(')
             || (c == ']' && top != '[')
             || (c == '}' && top != '{'))
                return false;
        }
    }
    return stack.isEmpty();
}
```

**Example 2 — Iterative DFS (avoids StackOverflowError):**
```java
// BAD: recursive DFS on deep graph crashes with
//      StackOverflowError for 10k+ depth
void dfsRecursive(Node node) {
    if (node == null) return;
    visit(node);
    dfsRecursive(node.left);
    dfsRecursive(node.right);
}

// GOOD: explicit stack, unbounded depth
void dfsIterative(Node root) {
    Deque<Node> stack = new ArrayDeque<>();
    stack.push(root);
    while (!stack.isEmpty()) {
        Node n = stack.pop();
        visit(n);
        if (n.right != null) stack.push(n.right);
        if (n.left  != null) stack.push(n.left);
    }
}
```

---

### ⚖️ Comparison Table

| Structure | LIFO | FIFO | Both-ends | Best For |
|---|---|---|---|---|
| **Stack (ArrayDeque)** | ✓ | ✗ | ✗ | LIFO processing, DFS |
| Queue (ArrayDeque) | ✗ | ✓ | ✗ | FIFO processing, BFS |
| Deque (ArrayDeque) | ✓ | ✓ | ✓ | Both ends access |
| java.util.Stack | ✓ | ✗ | ✗ | Legacy — avoid |

How to choose: Use `ArrayDeque` as a Stack for all new code. Use `Deque` when you need both ends. Never use `java.util.Stack` — it is synchronised and inherits inappropriate `Vector` methods.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| java.util.Stack is the right class to use | `java.util.Stack` extends `Vector` (synchronized) and exposes index-based access; `ArrayDeque` is preferred |
| A stack can only be array-based | Stacks are commonly implemented with linked lists — Java's `ArrayDeque` happens to use an array |
| Stack and Queue are fundamentally different | Both are restricted Deques — the only difference is which end is used for removal |
| Recursion is a better Stack than coding one explicitly | Recursion uses the limited JVM call stack; an explicit heap Stack avoids `StackOverflowError` for deep inputs |

---

### 🚨 Failure Modes & Diagnosis

**1. StackOverflowError from deep recursion**

Symptom: `java.lang.StackOverflowError` in production on large inputs that work fine in tests.

Root Cause: Each recursive call consumes a JVM stack frame. Default thread stack size is 512 KB (server JVM); depth limit is typically 5,000–10,000 frames for small methods.

Diagnostic:
```bash
# Check stack depth limit:
java -XX:+PrintFlagsFinal -version | grep ThreadStackSize
# Increase with:
java -Xss4m MyApp
```

Fix: Convert recursive algorithm to iterative using an explicit `ArrayDeque` stack.

Prevention: Always implement DFS/tree traversal iteratively for production code.

---

**2. Pop from empty stack**

Symptom: `java.util.EmptyStackException` or `NoSuchElementException` at runtime.

Root Cause: `pop()` called when stack is empty — common off-by-one in loop termination.

Diagnostic:
```bash
# Check stack trace; add isEmpty() guard
```

Fix:
```java
// BAD
String val = stack.pop(); // throws if empty

// GOOD
if (!stack.isEmpty()) {
    String val = stack.pop();
}
```

Prevention: Always check `isEmpty()` before `pop()`; treat empty stack as a recoverable state, not a crash condition.

---

**3. Unintended shared state via static Stack**

Symptom: DFS returns wrong results in multi-threaded code; results appear to bleed between requests.

Root Cause: A `static` Stack is shared across all threads; concurrent pushes/pops corrupt the state.

Diagnostic:
```bash
jstack <pid> | grep "BLOCKED\|WAITING"
# Multiple threads blocked on same Stack object
```

Fix: Always allocate stacks locally within method scope, not as shared fields.

Prevention: Never make a mutable Stack a class-level or static field in concurrent code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — the typical backing store for an array-based Stack implementation.
- `LinkedList` — alternative backing store for a node-based Stack.

**Builds On This (learn these next):**
- `DFS` — depth-first search uses a Stack (explicit or implicit via recursion) to track unvisited nodes.
- `Backtracking` — uses a Stack to record partial solutions and undo decisions on failure.
- `Recursion vs Iteration Trade-offs` — converting recursion to iteration always involves replacing the call stack with an explicit Stack.

**Alternatives / Comparisons:**
- `Queue / Deque` — FIFO version; same O(1) ends but opposite ordering.
- `Recursion` — implicit call stack; limited in depth, cleaner syntax for naturally recursive problems.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ LIFO collection: last pushed is first     │
│              │ popped; O(1) push/pop/peek                │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Nested processing requires reversing      │
│ SOLVES       │ order to return to previous state         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The JVM call stack IS a hardware stack;   │
│              │ explicit stacks mirror this for safety    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DFS, expression parsing, undo history,    │
│              │ bracket matching, function call emulation │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ FIFO order is needed; use Queue instead   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) LIFO access vs no random access      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The last tray on the stack is always     │
│              │  the first one you grab"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Queue → DFS → Backtracking                │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A production service processes deeply-nested JSON configs (up to 50,000 levels deep) using recursive descent parsing. On most inputs it works fine, but on adversarially crafted inputs it throws `StackOverflowError`. You cannot increase JVM stack size (-Xss) because thousands of threads share the pool. Describe step-by-step how you would refactor the recursive parser to use an explicit stack while preserving identical output semantics.

**Q2.** Both a Stack and the JVM call stack enforce LIFO ordering. If they serve the same logical purpose, why does converting a recursive DFS to an iterative version using an explicit Stack sometimes produce different node-visit order unless the push order is reversed? What does this reveal about the implicit ordering that the call stack imposes versus the explicit ordering you control?

