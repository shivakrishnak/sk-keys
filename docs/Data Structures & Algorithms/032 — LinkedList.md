---
layout: default
title: "LinkedList"
parent: "Data Structures & Algorithms"
nav_order: 32
permalink: /dsa/linkedlist/
number: "0032"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, Memory Management Models
used_by: Stack, Queue / Deque, LRU Cache
related: Array, ArrayList, Deque
tags:
  - datastructure
  - foundational
  - memory
  - algorithm
---

# 032 — LinkedList

⚡ TL;DR — A LinkedList chains nodes via pointers to allow O(1) insert/delete at known positions without shifting elements.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #032         │ Category: Data Structures & Algorithms │ Difficulty: ★☆☆        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Array, Memory Management Models        │                        │
│ Used by:     │ Stack, Queue / Deque, LRU Cache        │                        │
│ Related:     │ Array, ArrayList, Deque                │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a music playlist app. Users add and remove songs constantly at any position. You use an array. Every time someone inserts a song in the middle, you shift all subsequent elements one position right. With 10,000 songs, every mid-list insertion copies up to 10,000 references. Add 100 songs in random positions and you've done 1,000,000 element copies for what felt like trivial edits.

THE BREAKING POINT:
Arrays excel at random access but pay O(N) for insertion and deletion in the middle because they must maintain contiguity. For workloads dominated by mid-sequence mutation, this cost compounds into serious latency.

THE INVENTION MOMENT:
If we allow elements to live at non-contiguous addresses, and each element simply remembers where the next one lives, insertion becomes "update two pointers" — O(1) given a reference to the insertion point. This is exactly why the LinkedList was created.

### 📘 Textbook Definition

A **LinkedList** is a linear data structure in which each element (called a *node*) contains a data field and one or more references (pointers) to the next (and optionally previous) node. A *singly linked list* has one pointer per node (to the next); a *doubly linked list* has two pointers per node (to next and previous). Insertion and deletion at a known node position are O(1); access by index is O(N) because traversal from the head is required.

### ⏱️ Understand It in 30 Seconds

**One line:**
Nodes scattered in memory, each holding a value and a "next" address.

**One analogy:**
> Think of a scavenger hunt where each clue tells you exactly where to find the next clue. You can only get clue 7 by following the chain from clue 1. But adding a new clue between clue 3 and 4 just means updating two clue sheets — no moving other clues.

**One insight:**
A LinkedList trades random access for O(1) mutation. The "pointer chase" that makes access slow is the same property that makes insertion free — because you never have to move anyone else to make room.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Each node stores exactly one value and a pointer to the next node (null for the last).
2. No contiguity requirement — nodes can be anywhere in memory.
3. The list is traversed only in pointer order; no index formula exists.

DERIVED DESIGN:
Because nodes are independent, insertion between node A and node B is: create new node C, set `C.next = B`, set `A.next = C`. Zero copies. For deletion of node B: set `A.next = B.next`. One pointer update.

The cost is access: to reach `node[500]`, you must follow 500 `next` pointers. Each pointer dereference is likely a cache miss (nodes are scattered), making traversal 5–20× slower than an equivalent array scan.

Doubly linked lists add a `prev` pointer, enabling O(1) backward traversal and O(1) remove-by-node-reference without needing the predecessor. They cost one extra pointer per node (8 bytes on 64-bit JVM).

THE TRADE-OFFS:
Gain: O(1) insert/delete at known position, dynamic size without copying.
Cost: O(N) access by index, high memory overhead (pointer storage + GC pressure), poor cache locality.

### 🧪 Thought Experiment

SETUP:
A to-do app stores 1,000 tasks in a list. A user selects task #500 and inserts a new task immediately before it.

WHAT HAPPENS WITHOUT LINKEDLIST (using array):
Find task #500 in O(1). Then shift tasks #500–#999 one position to the right: 500 copy operations. Insert the new task. Total: 501 operations.

WHAT HAPPENS WITH LINKEDLIST:
Traverse to node #499 in O(499). Set `newNode.next = node499.next`. Set `node499.next = newNode`. Total: 499 traversal steps + 2 pointer updates. Insertion itself is O(1) — the traversal is the cost.

THE INSIGHT:
LinkedList makes insertion free but charges you the traversal. If you already hold a reference to the insertion point (e.g., from a previous iteration), the cost truly is O(1). This is why iterators in Java's `LinkedList` can remove while iterating cheaply — they track the current node.

### 🧠 Mental Model / Analogy

> A LinkedList is a chain of train carriages. Each carriage knows which carriage is directly behind it. To detach carriage 5 and insert a new one, you just re-hook two connections. But to check what's in carriage 500, you must walk from carriage 1.

"Carriage" → node
"Cargo in carriage" → node's data field
"Coupling hook" → `next` pointer
"Walk from carriage 1" → O(N) traversal

Where this analogy breaks down: Real carriages are physically adjacent; linked nodes are scattered in memory, so the cache penalty is far higher than just "walking" suggests.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A chain of items where each item knows the address of the next one. You can add or remove items cheaply, but finding item number 500 means counting from the start.

**Level 2 — How to use it (junior developer):**
Use `LinkedList<E>` in Java. Call `addFirst()`, `addLast()`, `removeFirst()`, `removeLast()` for O(1) operations. Use `ListIterator` to insert/remove during traversal. Avoid `get(i)` — it is O(N) and signals you should use `ArrayList` instead.

**Level 3 — How it works (mid-level engineer):**
Java's `LinkedList<E>` is a doubly linked list of `Node<E>` objects. Each node: `item`, `next`, `prev`. `size`, `first`, `last` are maintained. `add(index, value)` traverses from the nearer end (head if `index < size/2`, tail otherwise) for a slight optimisation. Internally used as a `Deque` for O(1) queue/stack operations.

**Level 4 — Why it was designed this way (senior/staff):**
Java's `LinkedList` implements both `List` and `Deque`. The `List` interface forces `get(int index)` to exist, but it's O(N). This is a leaky abstraction — the interface does not communicate the complexity contract. `ArrayDeque` outperforms `LinkedList` as a queue in virtually every benchmark because node allocation + GC churn dominates. Prefer `ArrayDeque` for queue/stack; prefer `ArrayList` for random access. `LinkedList` wins only when you need both ends access AND mid-list mutation via iterator.

### ⚙️ How It Works (Mechanism)

**Node Structure (Java internal):**
```java
private static class Node<E> {
    E item;
    Node<E> next;
    Node<E> prev;
}
```
Each node allocates a separate heap object: 16-byte header + 3 reference fields = ~40 bytes per element on a 64-bit JVM with compressed oops.

**Insert at tail:**
```
tail → [A | prev=B, next=null]
new node N: [val | prev=A, next=null]
A.next = N; N.prev = A; tail = N; size++
```

**Insert at index (doubly linked optimisation):**
```java
// Traverses from head or tail based on index
Node<E> node(int index) {
    if (index < (size >> 1)) {
        // start from head
    } else {
        // start from tail
    }
}
```

┌───────────────────────────────────────────────────────┐
│       Doubly Linked List — Insert Node C              │
│  Before: [A] ⇄ [B]                                   │
│  Step 1: C.next = B; C.prev = A                       │
│  Step 2: A.next = C; B.prev = C                       │
│  After:  [A] ⇄ [C] ⇄ [B]                            │
└───────────────────────────────────────────────────────┘

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Create list → add elements via addFirst/addLast (O(1))
→ Traverse via iterator [LINKEDLIST ← YOU ARE HERE]
→ Remove current node via iterator.remove() (O(1))
→ Result: mutated list without shifting
```

FAILURE PATH:
```
Call get(index) in a tight loop
→ O(N) per call → O(N²) total
→ Application appears to hang under load
→ Thread dump shows time in LinkedList.node()
```

WHAT CHANGES AT SCALE:
With millions of nodes, GC pause time dominates because each node is a separate heap object to mark and sweep. At scale, chunk-based structures like `ArrayDeque` or skip lists outperform `LinkedList` dramatically. Avoid `LinkedList` in latency-sensitive code with more than ~10,000 elements.

### 💻 Code Example

**Example 1 — O(1) queue operations:**
```java
// GOOD: LinkedList as Deque for O(1) both ends
Deque<String> queue = new LinkedList<>();
queue.addLast("task-1");
queue.addLast("task-2");
String next = queue.removeFirst(); // O(1)
```

**Example 2 — BAD: random access on LinkedList:**
```java
// BAD: O(N²) — each get(i) traverses from head
LinkedList<Integer> list = new LinkedList<>();
for (int i = 0; i < 100_000; i++) list.add(i);
int sum = 0;
for (int i = 0; i < list.size(); i++)
    sum += list.get(i); // O(N) each call!

// GOOD: use iterator for O(N) total
for (int val : list) sum += val;
```

**Example 3 — Remove during iteration (O(1) per removal):**
```java
LinkedList<Integer> list = new LinkedList<>(
    List.of(1, 2, 3, 4, 5));
ListIterator<Integer> it = list.listIterator();
while (it.hasNext()) {
    if (it.next() % 2 == 0)
        it.remove(); // O(1) — no shifting
}
// list: [1, 3, 5]
```

### ⚖️ Comparison Table

| Structure | Access | Insert mid | Insert ends | Memory/elem | Best For |
|---|---|---|---|---|---|
| **LinkedList** | O(N) | O(1)* | O(1) | ~40 B | Mid-list mutation via iter |
| Array | O(1) | O(N) | O(1) end only | 4–8 B | Random access |
| ArrayList | O(1) | O(N) | O(1) amort. | ~16 B | General purpose |
| ArrayDeque | O(1) ends | O(N) | O(1) | ~8 B | Queue/stack |

*O(1) given a reference to the node via an active iterator.

How to choose: If you need a queue or stack, prefer `ArrayDeque` over `LinkedList`. If you need random access, use `ArrayList`. Use `LinkedList` only when you need O(1) mid-list insertion while iterating.

### 🔁 Flow / Lifecycle

```
Create Node → set item, next=null, prev=null
     ↓
Link to list → update predecessor.next, successor.prev
     ↓
Access → traverse from head/tail
     ↓
Remove → update neighbour pointers, GC reclaims node
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LinkedList is faster than ArrayList for all insertions | Only true if you already hold the insertion point reference; finding the position is O(N) for both |
| LinkedList uses less memory than ArrayList | Each node carries 2 pointers + object header = ~40 bytes vs ~4–8 bytes per element in an array |
| Java's LinkedList is a good general-purpose list | For almost all use cases, ArrayList outperforms LinkedList because of cache locality |
| Removing an element by value from LinkedList is O(1) | Removing by value requires O(N) search first; only removing via an active iterator is O(1) |
| LinkedList has no overhead compared to arrays | Node objects add GC pressure; millions of nodes cause significant GC pause time |

### 🚨 Failure Modes & Diagnosis

**1. O(N²) performance from random access in loop**

Symptom: Loop over a `LinkedList` using `get(i)` grinds to a halt; 100k elements take seconds.

Root Cause: `LinkedList.get(i)` traverses from head (or tail) every call — O(N). A loop of N calls becomes O(N²).

Diagnostic:
```bash
# Thread dump will show long time in LinkedList.node():
jstack <pid> | grep -A 5 "LinkedList"
```

Fix:
```java
// BAD
for (int i = 0; i < list.size(); i++) process(list.get(i));

// GOOD
for (Integer val : list) process(val);
// or convert to ArrayList first for mixed access
```

Prevention: Never call `get(int)` on `LinkedList` in a performance path; switch to `ArrayList`.

---

**2. Memory explosion with large LinkedList**

Symptom: OutOfMemoryError with far fewer elements than expected; heap dumps show millions of small Node objects.

Root Cause: Each `LinkedList` node is a separate heap object (~40 bytes). 10M nodes = ~400 MB vs ~40 MB for an equivalent `int[]`.

Diagnostic:
```bash
jmap -histo:live <pid> | grep LinkedList
# Look for Node count × size
```

Fix: Replace `LinkedList` with `ArrayList` or a primitive collection library (Eclipse Collections, Trove) for large integer/long collections.

Prevention: Choose data structure based on memory profile; avoid `LinkedList` for large sets of primitives.

---

**3. ConcurrentModificationException during iteration**

Symptom: `java.util.ConcurrentModificationException` when modifying list while iterating.

Root Cause: Java's `LinkedList` maintains a `modCount`. The iterator snapshots `modCount` at creation; any structural modification outside the iterator increments it, causing the exception on next `iterator.next()`.

Diagnostic:
```bash
grep "ConcurrentModificationException" app.log
# Identify the modification site from the stack trace
```

Fix:
```java
// BAD: modify list directly in loop
for (Integer val : list)
    if (val < 0) list.remove(val); // throws CME

// GOOD: use iterator's own remove
Iterator<Integer> it = list.iterator();
while (it.hasNext())
    if (it.next() < 0) it.remove(); // safe
```

Prevention: Never modify a collection during an enhanced for loop; use `ListIterator.remove()`.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — contrasting contiguous storage with pointer-based storage reveals why linked lists make the trade they do.
- `Memory Management Models` — understanding heap allocation explains the per-node overhead.

**Builds On This (learn these next):**
- `Stack` — can be implemented as a linked list with O(1) push/pop.
- `Queue / Deque` — doubly linked list directly implements queue operations.
- `LRU Cache` — classic LinkedList + HashMap combination for O(1) eviction.

**Alternatives / Comparisons:**
- `ArrayList` — contiguous storage, O(1) access, preferred for most workloads.
- `ArrayDeque` — array-backed double-ended queue, outperforms LinkedList as a queue.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Chain of pointer-linked nodes; O(1)       │
│              │ insert/delete at known position           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Array insert/delete forces O(N) shifts    │
│ SOLVES       │                                           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "O(1) insert" only if you hold the node   │
│              │ reference — finding it is still O(N)      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Frequent mid-list mutation via iterator   │
│              │ and O(1) both-ends queue/stack needed     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Random access by index or large           │
│              │ memory-sensitive collections needed       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) insert vs O(N) access + memory cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Free insertion, but you pay to find      │
│              │  the spot first"                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stack → Queue / Deque → LRU Cache         │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Java's `LinkedList` implements both `List` and `Deque`. If you need a double-ended queue that supports O(1) add/remove at both ends, you have two options: `LinkedList` and `ArrayDeque`. Both claim O(1) at the ends. In a system processing 100 million events per second, which would you choose and why? What specific hardware characteristic causes one to outperform the other even when big-O is identical?

**Q2.** An LRU cache implementation uses a `HashMap<Key, Node>` and a `DoublyLinkedList`. When an entry is accessed, you move its node to the front of the list in O(1). Why is it impossible to achieve O(1) move-to-front with an `ArrayList` instead of a linked list, even if you store the index in the HashMap? What fundamental property of arrays makes this impossible?

