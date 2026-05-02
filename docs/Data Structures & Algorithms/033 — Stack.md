---
layout: default
title: "Stack"
parent: "Data Structures & Algorithms"
nav_order: 33
permalink: /dsa/stack/
number: "033"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, LinkedList
used_by: DFS, Backtracking, Expression Evaluation, Call Stack, Undo / Redo Pattern
tags:
  - datastructure
  - algorithm
  - foundational
---

# 033 — Stack

`#datastructure` `#algorithm` `#foundational`

⚡ TL;DR — A LIFO (Last-In, First-Out) collection where push adds to the top and pop removes from the top — like a stack of plates.

| #033 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList | |
| **Used by:** | DFS, Backtracking, Expression Evaluation, Call Stack, Undo / Redo Pattern | |

---

### 📘 Textbook Definition

A **stack** is an abstract data type implementing a Last-In, First-Out (LIFO) ordering constraint on its elements. The primary operations are: `push(element)` — add an element to the top in O(1); `pop()` — remove and return the top element in O(1); `peek()` — return the top element without removing it in O(1); and `isEmpty()` — test for empty. Implementations use either an array (with top-of-stack index) or a singly linked list (with head as top). Java provides `Deque<E>` (via `ArrayDeque`) as the recommended stack implementation; `java.util.Stack` is a legacy class extending `Vector` (synchronised, avoided in new code).

### 🟢 Simple Definition (Easy)

A stack is like a pile of plates: you can only add to the top or take from the top. The last plate you put on is the first one you take off.

### 🔵 Simple Definition (Elaborated)

A stack enforces a strict access order — you can only interact with the most recently added item. Push adds an item to the top; pop takes the top item away. This LIFO behaviour exactly models many real problems: function calls (the most recently called function must return before the caller can continue), undo operations (the most recent action is undone first), and syntax checking (the most recently opened parenthesis must be closed first). Stack's three operations — push, pop, peek — are all O(1), making it extremely efficient.

### 🔩 First Principles Explanation

**Why LIFO?**

Many real-world processes have a "last opened, first closed" structure:
- Function calls: `f()` calls `g()` which calls `h()` — `h()` returns before `g()` can continue.
- Nested brackets: `((()))` — the innermost bracket closes first.
- Undo history: the most recent action is the first to undo.

These cannot be modelled by a queue (FIFO) or random access. Stack is the minimal structure that captures this constraint efficiently.

**Array-based implementation:**

```
Stack (array-based):
arr:    [ 5 | 3 | 8 | _ | _ ]
                  ↑ top = 2

push(7): arr[3] = 7, top = 3
         [ 5 | 3 | 8 | 7 | _ ]

pop():   val = arr[3], top = 2
         returns 7, arr: [ 5 | 3 | 8 | _ | _ ]

peek():  returns arr[top] = 8, no state change
```

**Linked list-based implementation:**

```
head → [8] → [3] → [5] → null

push(7): new node [7] → head
         head → [7] → [8] → [3] → [5] → null

pop():   remove head, head = head.next
         returns 7, head → [8] → [3] → [5] → null
```

**Trade-offs:**
- Array stack: O(1) amortised operations, cache-friendly, prone to overflow if fixed-size.
- Linked list stack: dynamic size, O(1) operations, slightly higher memory per element.

**The call stack is literally a stack:** Each function call pushes a stack frame (local variables, return address, arguments) onto the call stack. Return pops the frame, restoring the caller's context.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Stack:

- Recursion can be modelled but requires explicit tracking of state at each recursion level.
- Bracket validation requires iterating twice: once to collect, once to check.
- Undo requires iterating backwards through an entire list.

What breaks without it:
1. Function call return addresses can't be properly tracked with FIFO.
2. DFS algorithms on graphs require re-visiting the most recently discovered unvisited node — exactly LIFO.

WITH Stack:
→ DFS, expression evaluation, bracket matching — natural O(n) implementations.
→ Backtracking algorithms explicitly manage return state via stack.
→ CPU call stack primitive enables function invocation in all programming languages.

### 🧠 Mental Model / Analogy

> A stack is exactly like a stack of trays in a cafeteria. You place a clean tray on top (push). When a student needs one, they take the top tray (pop). Nobody reaches into the middle. Yesterday's trays remain at the bottom until today's are gone. The discipline is strict: you interact only with the top.

"Tray" = element, "placing on top" = push, "taking top tray" = pop, "looking at top without taking" = peek.

The constraint is the feature: LIFO enforces the exact ordering needed for call stacks, undo, and DFS.

### ⚙️ How It Works (Mechanism)

**Classic algorithms using stack:**

**Bracket matching:**
```
Input: "({[]})"
Push (, {, [ when open bracket seen
Compare with top when close bracket seen;
pop if match, else invalid.

'(' → push → [(]
'{' → push → [(, {]
'[' → push → [(, {, []
']' → pop [, matches ] → [(, {]
'}' → pop {, matches } → [(]
')' → pop (, matches ) → []
Empty stack → valid!
```

**Evaluate reversed Polish notation (postfix):**
```
"4 5 + 3 *"
Push 4 → [4]
Push 5 → [4, 5]
'+' → pop 5,4; push 4+5=9 → [9]
Push 3 → [9, 3]
'*' → pop 3,9; push 9*3=27 → [27]
Result: 27
```

### 🔄 How It Connects (Mini-Map)

```
Array | LinkedList (implementations)
           ↓ abstracted as
Stack ← you are here (LIFO)
           ↓ used in
DFS (graph/tree traversal)
Backtracking (N-Queens, permutations)
Expression evaluation (infix→postfix)
Call Stack (JVM/OS thread stack)
Undo/Redo (editor history)
           ↓ related abstract structure
Queue (FIFO) — contrast partner
```

### 💻 Code Example

Example 1 — Using ArrayDeque as a stack in Java:

```java
// Java 21: Use ArrayDeque — NOT java.util.Stack (legacy)
Deque<Integer> stack = new ArrayDeque<>();

stack.push(5);   // O(1) - adds to front (top)
stack.push(3);
stack.push(8);

System.out.println(stack.peek()); // 8 — top without removing
System.out.println(stack.pop());  // 8 — remove and return
System.out.println(stack.pop());  // 3
System.out.println(stack.isEmpty()); // false (5 remains)
```

Example 2 — Valid parentheses checker:

```java
public boolean isValid(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '{' || c == '[') {
            stack.push(c); // open bracket → push
        } else {
            if (stack.isEmpty()) return false;
            char top = stack.pop();
            if (c == ')' && top != '(') return false;
            if (c == '}' && top != '{') return false;
            if (c == ']' && top != '[') return false;
        }
    }
    return stack.isEmpty(); // all brackets matched
}
// Input: "()[]{}" → true
// Input: "([)]"   → false
```

Example 3 — Iterative DFS using explicit stack:

```java
// Iterative DFS replaces recursive call stack with explicit stack
public <T> void dfs(Graph<T> graph, T start,
                    Consumer<T> visit) {
    Deque<T> stack = new ArrayDeque<>();
    Set<T> visited = new HashSet<>();

    stack.push(start);
    while (!stack.isEmpty()) {
        T node = stack.pop();
        if (visited.contains(node)) continue;
        visited.add(node);
        visit.accept(node);
        // Push neighbours (unvisited, in reverse order
        // if order matters)
        for (T neighbour : graph.neighbours(node)) {
            if (!visited.contains(neighbour)) {
                stack.push(neighbour);
            }
        }
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| java.util.Stack is the right Java class to use | java.util.Stack extends Vector (synchronised) — it's a legacy class. Use ArrayDeque<> or LinkedList<> for modern code. |
| Stack overflow means the data structure Stack is full | StackOverflowError in Java means the JVM's call stack is exhausted (too many nested method calls). This is a different Stack from the data structure. |
| Stack can only be used LIFO — no other access | While the ADT only exposes push/pop/peek, the underlying array/list can technically be accessed directly; but doing so violates the stack contract. |
| LIFO and FIFO are equivalent for most problems | They produce fundamentally different results: LIFO DFS explores depth-first; FIFO BFS explores breadth-first. Wrong choice for a problem gives wrong algorithm. |

### 🔥 Pitfalls in Production

**1. Using java.util.Stack in Multithreaded Code**

```java
// BAD: Stack extends Vector — ALL methods synchronised
// heavy synchronisation even when not needed
java.util.Stack<Integer> stack = new java.util.Stack<>();
stack.push(1); // acquires synchronised lock!

// GOOD: ArrayDeque for single-threaded or ThreadLocal use
Deque<Integer> stack = new ArrayDeque<>();

// For thread-safe concurrent use:
Deque<Integer> safeStack = new ConcurrentLinkedDeque<>();
```

**2. Stack Overflow from Unbounded Recursion**

```java
// BAD: No base case or infinite recursion
public long fib(int n) {
    return fib(n-1) + fib(n-2); // stack overflow for large n!
    // Each call adds a stack frame (~2KB) → thread stack full at ~1000 calls
}

// GOOD: Iterative or use explicit stack data structure
public long fib(int n) {
    if (n <= 1) return n;
    long a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        long c = a + b; a = b; b = c;
    }
    return b;
}
```

**3. Empty Stack Pop Without Check**

```java
// BAD: NoSuchElementException if stack is empty
int val = stack.pop(); // throws if empty!

// GOOD: Check before pop or use peek
if (!stack.isEmpty()) {
    int val = stack.pop();
}
// Or: use pollFirst() which returns null if empty
Integer val = stack.pollFirst(); // null if empty
```

### 🔗 Related Keywords

- `Queue / Deque` — the FIFO contrast; both share the deque implementation in Java.
- `DFS` — the graph traversal algorithm that uses stack for LIFO frontier management.
- `Call Stack` — the OS/JVM mechanism implementing function call return order.
- `Backtracking` — systematically explores possibilities using stack to track state.
- `ArrayDeque` — Java's recommended stack and queue implementation.
- `Expression Evaluation` — infix-to-postfix conversion and evaluation use stacks.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ LIFO: last pushed is first popped.        │
│              │ push/pop/peek all O(1).                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DFS, bracket matching, undo, call stack,  │
│              │ expression evaluation, backtracking.      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ FIFO needed → Queue; random access needed │
│              │ → Array/ArrayList.                        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Stack: the plate pile of computing —     │
│              │ last placed is first taken."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Queue/Deque → HashMap → DFS → Call Stack  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Recursive DFS and iterative DFS (using an explicit stack) are algorithmically equivalent but have different production characteristics. The JVM call stack has a default limit of ~1000–2000 frames. For a DFS on a graph with 1,000,000 nodes forming a single long path (worst case), the recursive version overflows. The iterative version uses a heap-allocated stack instead. Compare the memory usage of both approaches for this worst case, and explain why the iterative version's heap stack doesn't have the same overflow limitation as the JVM call stack.

**Q2.** A monotonic stack is a stack where elements are maintained in increasing or decreasing order. Describe the algorithm for finding the "next greater element" for every element in an array using a monotonic stack, trace it through the array `[2, 1, 5, 3, 4]`, and explain why it achieves O(n) time complexity despite having a nested loop structure in a naive reading.

