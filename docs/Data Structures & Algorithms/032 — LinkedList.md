---
layout: default
title: "LinkedList"
parent: "Data Structures & Algorithms"
nav_order: 32
permalink: /dsa/linked-list/
number: "032"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, Memory Management Models
used_by: Stack, Queue / Deque, Graph, LRU Cache
tags:
  - datastructure
  - algorithm
  - foundational
---

# 032 — LinkedList

`#datastructure` `#algorithm` `#foundational`

⚡ TL;DR — A sequence of nodes where each node holds data and a pointer to the next (and optionally previous) node, trading O(1) insert/delete at a known position for O(n) index access.

| #032 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, Memory Management Models | |
| **Used by:** | Stack, Queue / Deque, Graph, LRU Cache | |

---

### 📘 Textbook Definition

A **linked list** is a linear data structure where each element is stored in a *node* containing a data field and one or more pointer fields. In a **singly linked list**, each node has one `next` pointer to the subsequent node; the last node's `next` is null. In a **doubly linked list**, each node has both `next` and `prev` pointers, enabling traversal in both directions and O(1) removal given a reference to the node. Linked lists do not require contiguous memory and support O(1) insertion/deletion at any position given a reference to the predecessor node, but require O(n) traversal to find elements by index.

### 🟢 Simple Definition (Easy)

A linked list is a chain of boxes — each box contains a value and a pointer to the next box. Fast to add or remove boxes anywhere in the chain, but slow to reach a specific position.

### 🔵 Simple Definition (Elaborated)

Unlike an array where all elements are packed into one contiguous block of memory, a linked list stores each element separately and uses pointer references to chain them together in sequence. Adding or removing an element only requires updating a couple of pointers — you don't need to shift anything. But finding the 50th element means starting at the first element and following 49 `next` pointers, one by one — no shortcuts. This O(n) traversal cost makes linked lists a poor choice for random access, but excellent for queues, stacks, and situations where you're frequently inserting/deleting at the front or middle.

### 🔩 First Principles Explanation

**Why not just use arrays everywhere?**

Arrays need contiguous memory. For a 10M-element array, the OS must find a 40 MB contiguous free block. As memory fragments over time, large contiguous allocations fail even if total free memory is sufficient. Linked lists allocate nodes individually — each node is a small, independent allocation wherever memory is available.

**Node structure:**

```
Singly Linked List Node:
┌──────────────────┐
│  data  │  next  →│─────►[ next node ]
└──────────────────┘

Doubly Linked List Node:
┌──────────────────────────┐
│◄─ prev │  data  │ next ─►│
└──────────────────────────┘
```

**Singly vs Doubly:**
- Singly: less memory (one pointer), can only traverse forward.
- Doubly: more memory (two pointers), can traverse backward and remove nodes without the predecessor reference.

**Insert/Delete at position given a reference:**

```
Insert after node X:
  New node.next = X.next
  X.next = New node
  → O(1): only 2 pointer updates

Delete node X (doubly linked, given X itself):
  X.prev.next = X.next
  X.next.prev = X.prev
  → O(1): 2 pointer updates, no traversal needed
```

**Java's `LinkedList` is doubly linked with sentinel head/tail nodes** — simplifying edge cases (no special handling for empty list).

### ❓ Why Does This Exist (Why Before What)

WITHOUT LinkedList:

- Queue implementation on an array shifts all elements on dequeue: O(n) per dequeue.
- Inserting in sorted order into an array: O(n) shift.
- Doubly linked list enables O(1) LRU cache eviction — no array alternative achieves this.

What breaks without it:
1. O(n) queue operations (ArrayDeque solves this too, but requires resizing).
2. No O(1) arbitrary removal given a node reference.

WITH LinkedList:
→ O(1) prepend/append/removal given position reference.
→ No contiguous memory requirement — allocate anywhere.
→ Foundation for LRU cache, adjacency lists, and undo-history patterns.

### 🧠 Mental Model / Analogy

> A linked list is like a treasure hunt where each clue (node) tells you the location of the next clue. To find clue number 47, you must start at clue 1 and follow 46 locations in sequence — you can't skip ahead. But adding a new clue between clues 5 and 6 is easy: you just rewrite clue 5 to point to the new clue, and the new clue points to where clue 6 was.

"Clues" = nodes, "location on clue" = next pointer, "following clues" = O(n) traversal, "rewriting clue 5" = O(1) pointer update for insertion.

### ⚙️ How It Works (Mechanism)

**Complexity comparison with Array:**

```
Operation         Array   Singly LL  Doubly LL
─────────────────────────────────────────────────
Access by index   O(1)    O(n)       O(n)
Search            O(n)    O(n)       O(n)
Insert at front   O(n)    O(1)       O(1)
Insert at back    O(1)*   O(n)**     O(1)***
Insert at middle  O(n)    O(n)****   O(n)****
Delete at front   O(n)    O(1)       O(1)
Delete at back    O(1)    O(n)       O(1)***
Delete at middle  O(n)    O(n)       O(1)*****

*  amortised, ** with no tail pointer, *** with tail pointer
**** traversal to find predecessor, ***** given node reference
```

**Java LinkedList internals:**

```java
// Java's LinkedList is doubly linked + deque
// Each node: Node<E> { E item; Node<E> next; Node<E> prev; }
// Has sentinel: first (head) and last (tail) Node references

LinkedList<Integer> ll = new LinkedList<>();
ll.addFirst(1);  // O(1): update head
ll.addLast(2);   // O(1): update tail
ll.add(1, 99);   // O(n): traverse to index 1 first
ll.removeFirst();// O(1): update head
ll.removeLast(); // O(1): update tail
```

**Circular linked list — used in OS scheduling:**

```
head → [1] → [2] → [3] → [4] →
         ↑___________________________│
(last.next points back to head — round-robin)
```

### 🔄 How It Connects (Mini-Map)

```
Array (contiguous, O(1) access, O(n) insert)
        ↕ compare
LinkedList ← you are here
(scattered, O(n) access, O(1) insert given ref)
        ↓ used to implement
Stack (push/pop from head)
Queue (enqueue at tail, dequeue from head)
Deque (both ends O(1))
LRU Cache (doubly linked + hashmap)
Graph adjacency list (list of neighbour lists)
```

### 💻 Code Example

Example 1 — Implementing a singly linked list:

```java
public class SinglyLinkedList<T> {
    private static class Node<T> {
        T data;
        Node<T> next;
        Node(T data) { this.data = data; }
    }

    private Node<T> head;
    private int size;

    // O(1): prepend
    public void addFirst(T item) {
        Node<T> node = new Node<>(item);
        node.next = head;
        head = node;
        size++;
    }

    // O(n): access by index
    public T get(int index) {
        Node<T> current = head;
        for (int i = 0; i < index; i++) {
            current = current.next;
        }
        return current.data;
    }

    // O(n): remove by value
    public boolean remove(T item) {
        if (head == null) return false;
        if (head.data.equals(item)) {
            head = head.next; size--; return true;
        }
        Node<T> curr = head;
        while (curr.next != null) {
            if (curr.next.data.equals(item)) {
                curr.next = curr.next.next;
                size--;
                return true;
            }
            curr = curr.next;
        }
        return false;
    }
}
```

Example 2 — LRU Cache: classic doubly linked list + HashMap:

```java
// O(1) get and put — requires doubly linked list
class LRUCache {
    private final int capacity;
    private final Map<Integer, Node> map = new HashMap<>();
    private final Node head = new Node(0, 0); // sentinel
    private final Node tail = new Node(0, 0); // sentinel

    LRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    int get(int key) {
        if (!map.containsKey(key)) return -1;
        Node node = map.get(key);
        moveToFront(node); // O(1) — doubly linked allows this
        return node.val;
    }

    void put(int key, int val) {
        if (map.containsKey(key)) {
            Node node = map.get(key);
            node.val = val;
            moveToFront(node);
        } else {
            if (map.size() == capacity) {
                Node lru = tail.prev; // least recently used
                remove(lru);         // O(1) removal
                map.remove(lru.key);
            }
            Node node = new Node(key, val);
            insertFront(node);       // O(1) insert
            map.put(key, node);
        }
    }

    // Node, remove(), insertFront(), moveToFront() omitted for brevity
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LinkedList is always slower than ArrayList | For frequent front/middle insertions and deletions with known node references, LinkedList is O(1) vs ArrayList's O(n). |
| Java's LinkedList is more memory-efficient | LinkedList uses 24–32 bytes per node (object header + 2 pointers + data). ArrayList uses ~4 bytes per reference element. LinkedList has 6–8× memory overhead per element. |
| LinkedList is better for a stack | In Java, ArrayDeque is preferred for both stack and queue — better cache performance than LinkedList. |
| Removing an element from middle is always O(1) | Removing requires a reference to the node (or its predecessor for singly linked). Finding that reference requires O(n) traversal. Removal itself (given reference) is O(1). |
| Doubly linked lists use twice the memory of singly linked | Doubly linked adds one extra pointer per node (8 bytes). For small values, this can be significant; for large objects, it's negligible. |

### 🔥 Pitfalls in Production

**1. Using LinkedList Instead of ArrayDeque for Stack/Queue**

```java
// BAD: LinkedList has poor cache locality for LIFO/FIFO
Deque<Integer> stack = new LinkedList<>();

// GOOD: ArrayDeque is 2-3× faster, better cache behaviour
Deque<Integer> stack = new ArrayDeque<>();
// ArrayDeque is backed by a circular array — cache-friendly
// Use LinkedList only when O(1) middle-insert with node reference needed
```

**2. Iterating by Index — O(n²) Trap**

```java
LinkedList<Integer> list = new LinkedList<>();
// ... add 10,000 elements ...

// BAD: O(n) traversal × O(n) iterations = O(n²)
for (int i = 0; i < list.size(); i++) {
    process(list.get(i)); // each get(i) traverses from head!
}

// GOOD: Use iterator — O(n) total
for (int val : list) {
    process(val); // iterator maintains current pointer
}
```

**3. Forgetting to Handle Head Update on Delete**

```java
// BAD: Doesn't handle deleting the head node
public Node deleteNode(Node head, int val) {
    // if head.val == val, returns old head without nullifying!
    Node curr = head;
    while (curr.next != null) {
        if (curr.next.val == val) {
            curr.next = curr.next.next;
            return head;
        }
        curr = curr.next;
    }
    return head; // never handles head deletion!
}

// GOOD: Handle head case explicitly
if (head.val == val) return head.next;
```

### 🔗 Related Keywords

- `Array` — the contrast: contiguous vs. scattered memory; O(1) access vs. O(n).
- `Stack` — commonly implemented via linked list (push/pop at head).
- `Queue / Deque` — linked list enables O(1) enqueue at tail and dequeue at head.
- `LRU Cache` — doubly linked list + hashmap enables O(1) get and eviction.
- `Graph` — adjacency list representation uses list-of-lists of linked nodes.
- `HashMap` — separate chaining collision resolution uses a linked list per bucket.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Node chain via pointers: O(1) insert/del  │
│              │ at known position; O(n) index access.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ LRU cache, undo history, queue/stack with │
│              │ frequent front insertion; O(1) node       │
│              │ removal with reference.                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Random index access needed → Array;       │
│              │ simple LIFO/FIFO → ArrayDeque;            │
│              │ memory-sensitive small elements.          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "LinkedList: easy to reshuffle, hard to   │
│              │ find by number."                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stack → Queue/Deque → HashMap → LRU Cache │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A browser implements "back/forward navigation history" using a doubly linked list where each node stores a URL. The "back" button moves to `current.prev`; "forward" moves to `current.next`. If the user navigates forward to 10 pages, then goes back 5, then visits a new page, describe exactly what happens to the forward history in the linked list, how many nodes should be deallocated and when, and how this differs from implementing the same feature with a fixed-size ArrayList.

**Q2.** Java's `HashMap` uses a linked list per bucket for separate chaining collision resolution (until Java 8 converts to a tree at threshold 8). When a HashMap with 16 buckets holds 100 entries where all keys happen to hash to bucket 3, every `get()` degrades from O(1) to O(n). Describe the exact condition under which this can happen with real-world data (not maliciously crafted), and explain what Java 8's tree conversion threshold achieves in terms of worst-case asymptotic complexity.

