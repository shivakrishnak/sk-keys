---
layout: default
title: "Recursion"
parent: "CS Fundamentals — Paradigms"
nav_order: 21
permalink: /cs-fundamentals/recursion/
number: "21"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Procedural Programming, Stack Memory, Functions
used_by: Tail Recursion, Functional Programming, Data Structures & Algorithms
tags: #intermediate, #algorithm, #datastructure, #foundational
---

# 21 — Recursion

`#intermediate` `#algorithm` `#datastructure` `#foundational`

⚡ TL;DR — A function that solves a problem by calling itself on a smaller version of the same problem, terminating when a base case is reached.

| #21             | Category: CS Fundamentals — Paradigms                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Procedural Programming, Stack Memory, Functions                      |                 |
| **Used by:**    | Tail Recursion, Functional Programming, Data Structures & Algorithms |                 |

---

### 📘 Textbook Definition

**Recursion** is a programming technique in which a function calls itself, directly or indirectly, to solve a problem by decomposing it into one or more simpler instances of the same problem. Every recursive definition requires at least one _base case_ — a condition under which the function returns without making a further recursive call — and one or more _recursive cases_ that reduce the problem toward the base case. Each call creates a new _stack frame_ on the call stack; the accumulated frames are popped in reverse order as the recursion unwinds. A recursive solution that lacks a reachable base case produces a stack overflow.

---

### 🟢 Simple Definition (Easy)

Recursion is when a function calls itself to solve a smaller version of the same problem, until it reaches a stopping point simple enough to answer directly.

---

### 🔵 Simple Definition (Elaborated)

Think of Russian nesting dolls (Matryoshka): to open the whole set, you open the outer doll, which reveals a smaller doll — and you repeat the same action on that smaller doll, until you reach the smallest doll with nothing inside (the base case). Recursion works the same way: to compute `factorial(5)`, you compute `5 × factorial(4)`, which needs `4 × factorial(3)`, down to `factorial(1) = 1`. The chain of waiting "5 × ?" frames is stored on the call stack. Once the base case returns, the answers unwind back through each frame: `1 → 2 → 6 → 24 → 120`. Recursion naturally models problems that have a self-similar structure: trees, file system directories, mathematical sequences, divide-and-conquer algorithms.

---

### 🔩 First Principles Explanation

**The problem: some problems are naturally self-similar.**

A directory listing: to list `/home/user`, you list all files and then recursively list every sub-directory. An `if` and a loop can do this, but the code becomes complex with an explicit stack. The natural description of the problem is recursive:

```
list(directory):
  for each item in directory:
    if item is a file: print it
    if item is a directory: list(item)   ← same problem, smaller input
```

**The mechanism — call stack:**

Each recursive call pushes a new frame. The frame stores the current parameters and the "return address" (where to continue when the call returns).

```
factorial(5)
  └─ 5 × factorial(4)
         └─ 4 × factorial(3)
                └─ 3 × factorial(2)
                       └─ 2 × factorial(1)
                              └─ returns 1  ← base case

Unwind:
factorial(1) = 1
factorial(2) = 2 × 1 = 2
factorial(3) = 3 × 2 = 6
factorial(4) = 4 × 6 = 24
factorial(5) = 5 × 24 = 120
```

**The constraint: stack depth.**

Each frame uses stack memory. The JVM default stack depth is typically 500–1000 recursive calls for simple frames. Exceed this → `StackOverflowError`. For deep recursion, iterative or tail-recursive solutions are required.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Recursion (iterative tree traversal — complex):

```java
// Iterative in-order traversal requires an explicit stack
Deque<TreeNode> stack = new ArrayDeque<>();
TreeNode curr = root;
while (curr != null || !stack.isEmpty()) {
    while (curr != null) {
        stack.push(curr);
        curr = curr.left;
    }
    curr = stack.pop();
    visit(curr);
    curr = curr.right;
}
// 10 lines to express a naturally recursive operation
```

What breaks without it:

1. Tree and graph traversal requires manually managing an explicit stack.
2. Divide-and-conquer algorithms (merge sort, quick sort, binary search) lose their natural structure.
3. Mutually recursive grammars (parsers) have no clean iterative equivalent.
4. Mathematical definitions that are inherently recursive cannot be expressed directly.

WITH Recursion:

```java
// Recursive in-order traversal — mirrors the problem definition
void inOrder(TreeNode node) {
    if (node == null) return;   // base case
    inOrder(node.left);         // recurse left
    visit(node);
    inOrder(node.right);        // recurse right
}
// 5 lines. Exactly matches the mathematical definition.
```

---

### 🧠 Mental Model / Analogy

> Think of looking up a word in a dictionary that contains technical terms defined using other technical terms. You look up "concurrency" — it says "see parallelism." You look up "parallelism" — it says "see simultaneous execution." Eventually you reach a word defined in plain English (the base case) and you unwind back through your stack of tabs to understand each definition in context.

"Looking up the next word" = recursive call
"The plain English definition" = base case
"Tabs open in the dictionary" = stack frames waiting to return
"Closing tabs in reverse order" = unwinding the call stack

The key: you always make progress toward a simpler definition (smaller problem), and you always reach plain English (base case).

---

### ⚙️ How It Works (Mechanism)

**Call stack during recursion:**

```
┌──────────────────────────────────────────────────────┐
│         Call Stack: factorial(4)                     │
│                                                      │
│  Frame 4: factorial(4) — waiting for factorial(3)    │
│  Frame 3: factorial(3) — waiting for factorial(2)    │
│  Frame 2: factorial(2) — waiting for factorial(1)    │
│  Frame 1: factorial(1) — base case: returns 1        │
│                          ↑ stack pops from here       │
└──────────────────────────────────────────────────────┘
```

**Three laws of recursion:**

1. Must have a base case (termination condition).
2. Must change state and move toward the base case.
3. Must call itself recursively.

**Canonical implementations:**

```java
// Factorial — classic linear recursion
int factorial(int n) {
    if (n <= 1) return 1;           // base case
    return n * factorial(n - 1);   // recursive case: n → n-1
}

// Fibonacci — two recursive calls (tree recursion — expensive!)
int fib(int n) {
    if (n <= 1) return n;           // base case
    return fib(n - 1) + fib(n - 2); // two recursive calls
}
// fib(50) makes ~2^50 calls — use memoisation or iteration

// Binary search — divide and conquer
int binarySearch(int[] arr, int target, int lo, int hi) {
    if (lo > hi) return -1;         // base case: not found
    int mid = (lo + hi) / 2;
    if (arr[mid] == target) return mid;
    if (arr[mid] < target) return binarySearch(arr, target, mid+1, hi);
    return binarySearch(arr, target, lo, mid-1);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Procedural Programming → Functions → Stack Memory
        │
        ▼
Recursion  ◄──── (you are here)
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
Tail Recursion                         Tree / Graph Traversal
(stack-safe recursion)                (DFS is naturally recursive)
        │                                         │
        ▼                                         ▼
Functional Programming               Divide-and-Conquer Algorithms
(recursion replaces loops)           (merge sort, quick sort, FFT)
```

---

### 💻 Code Example

**Example 1 — Tree traversal:**

```java
// Pre-order traversal of a binary tree (root, left, right)
void preOrder(TreeNode node) {
    if (node == null) return;       // base case
    System.out.println(node.value); // process root
    preOrder(node.left);            // recurse left
    preOrder(node.right);           // recurse right
}
// This mirrors the mathematical definition exactly
```

**Example 2 — Directory listing:**

```java
void listDirectory(Path dir, int indent) throws IOException {
    // base case: list files in this dir
    try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
        for (Path entry : stream) {
            System.out.println("  ".repeat(indent) + entry.getFileName());
            if (Files.isDirectory(entry)) {
                listDirectory(entry, indent + 1); // recurse into sub-dirs
            }
        }
    }
}
```

**Example 3 — Memoisation to avoid redundant calls:**

```java
// BAD: exponential time — fib(n) recomputes the same sub-problems
int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2); // fib(30) makes 2^30 calls
}

// GOOD: memoised — O(n) time, O(n) space
Map<Integer, Long> memo = new HashMap<>();
long fib(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n); // cache hit
    long result = fib(n-1) + fib(n-2);
    memo.put(n, result);                          // cache result
    return result;
}
```

**Example 4 — Merge sort (divide and conquer):**

```java
void mergeSort(int[] arr, int lo, int hi) {
    if (lo >= hi) return;           // base case: single element
    int mid = (lo + hi) / 2;
    mergeSort(arr, lo, mid);        // sort left half
    mergeSort(arr, mid+1, hi);      // sort right half
    merge(arr, lo, mid, hi);        // merge sorted halves
}
// Each call halves the problem → O(n log n) total
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recursion is always elegant and preferred                 | Recursion is natural for self-similar problems; for simple sequential tasks, iteration is clearer and more efficient                                                                      |
| Recursion is always slower than iteration                 | The call stack overhead is small; well-implemented recursion (tail-recursive or memoised) matches iteration; naive tree recursion (Fibonacci without memoisation) is exponentially slower |
| Recursion always causes stack overflow                    | Only if depth exceeds the stack limit (~500–1000 frames for typical JVM stacks). For bounded-depth problems (e.g., a 10-level directory tree), this is irrelevant                         |
| Every recursive function can be replaced by a simple loop | Many recursive algorithms require an explicit stack data structure when converted to iteration — not a "simple loop"                                                                      |

---

### 🔥 Pitfalls in Production

**Missing or wrong base case — StackOverflowError**

```java
// BAD: base case never reached for negative input
int factorial(int n) {
    if (n == 0) return 1;           // base case — but never reached for n<0!
    return n * factorial(n - 1);   // n=-1 → n=-2 → ... → StackOverflowError
}

// GOOD: validate input and handle all termination conditions
int factorial(int n) {
    if (n < 0) throw new IllegalArgumentException("n must be >= 0");
    if (n == 0) return 1;
    return n * factorial(n - 1);
}
```

---

**Naive Fibonacci — exponential time in production**

```java
// BAD: called for fib(40) on every API request → server stalls
@GetMapping("/fib/{n}")
int fibonacci(@PathVariable int n) {
    return fib(n); // fib(40) = 10^9 operations!
}

// GOOD: iterative or memoised with bounded input
@GetMapping("/fib/{n}")
long fibonacci(@PathVariable @Max(80) int n) {
    if (n <= 1) return n;
    long prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        long next = prev + curr;
        prev = curr; curr = next;
    }
    return curr;
}
```

---

**Recursive file traversal on malicious inputs (zip bombs)**

```java
// BAD: unbounded recursion on user-supplied directory
void extract(ZipFile zip, Path dest) {
    for (ZipEntry entry : zip.entries()) {
        if (isDirectory(entry)) {
            extract(nestedZip, dest); // zip bomb: 1 file → 10^9 files
        }
    }
}

// GOOD: limit recursion depth / total extracted size
void extract(ZipFile zip, Path dest, int depth) {
    if (depth > 5) throw new SecurityException("Zip nesting too deep");
    // ... same logic ...
}
```

---

### 🔗 Related Keywords

- `Stack Memory` — the runtime data structure that stores each recursive call frame
- `Stack Frame` — the record pushed per call containing parameters, locals, and the return address
- `Tail Recursion` — the optimised form where the recursive call is the last operation, enabling stack reuse
- `Functional Programming` — uses recursion in place of loops; languages like Haskell rely on it exclusively
- `Divide-and-Conquer` — the algorithm strategy built on recursive decomposition
- `Memoisation` — caching recursive subresults to convert exponential to linear time
- `Tree` — the data structure most naturally traversed recursively
- `Dynamic Programming` — converts recursive sub-problem solutions into a bottom-up table

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Solve problem by calling self on a        │
│              │ smaller version; base case stops recursion│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Problem is self-similar: trees, graphs,   │
│              │ divide-and-conquer, mathematical defs     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Deep unbounded recursion (use iteration); │
│              │ multiple redundant sub-calls (use memo)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "To understand recursion, you must first  │
│              │ understand recursion."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tail Recursion → Memoisation →            │
│              │ Dynamic Programming → Divide-and-Conquer  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A recursive JSON parser processes arbitrarily nested JSON objects. In production, a user submits a JSON document with 10,000 levels of nesting. The service crashes with a `StackOverflowError`. Describe two different solutions — one that eliminates the recursion entirely and one that keeps the recursive structure but prevents the crash — and explain the trade-offs between them in terms of code readability, memory usage, and worst-case performance.

**Q2.** Mutual recursion occurs when function A calls function B which calls function A. A simple expression parser uses two mutually recursive functions: `parseExpr()` calls `parseTerm()` which calls `parseExpr()` for sub-expressions. Standard tail-call optimisation cannot be applied directly to mutual recursion. Explain why, describe the trampolining technique that makes mutual recursion stack-safe, and identify in which JVM languages trampolining is natively supported vs where it must be manually implemented.
