---
id: DSA-010
title: Linked List (Singly Linked)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-002
used_by: DSA-011, DSA-012, DSA-013
related: DSA-008, DSA-009, DSA-011
tags:
  - data-structures
  - linked-list
  - pointers
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/dsa/linked-list/
---

## TL;DR

A singly linked list chains nodes via pointers - enabling
O(1) insert/delete at the head but paying O(n) for access
and suffering poor cache behavior compared to arrays.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-010 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, linked-list, pointers |
| **Prerequisites** | DSA-002 |

---

### The Problem This Solves

Arrays have O(n) insert and delete in the middle because
elements must be shifted. Linked lists sacrifice random
access to gain O(1) insert/delete at any known position -
useful when modifications at known positions outweigh
random access needs.

---

### Textbook Definition

A singly linked list is a linear data structure where each
element (node) contains a data value and a pointer to the
next node. The last node points to null. Traversal is
sequential from head to tail; there is no reverse traversal.

---

### Understand It in 30 Seconds

Each node is a slip of paper with a value and an address
pointing to the next slip. To get to slip #5, you start
from the first slip and follow 4 addresses. No shortcut.

But to insert a new slip between #2 and #3: update two
pointers. No shifting needed. O(1) if you have a reference
to node #2.

---

### First Principles

**The node invariant:**
- Every node has a reference to the next node (or null)
- The list is valid as long as no pointer is broken
- There is no index - position is determined by traversal

**The core trade-off:**
Array: O(1) access, O(n) insert (shift).
Linked list: O(n) access, O(1) insert (if at known node).

This is a direct consequence of memory layout:
- Array: contiguous → address computable
- Linked list: scattered → must follow pointers

---

### Mental Model / Analogy

**The treasure hunt:** A chain of clues, each clue pointing
to the next location. To reach clue #10, you must follow
9 previous clues. But adding a new clue #3.5 between clue
#3 and #4 only requires rewriting one clue's pointer.

---

### Gradual Depth - Five Levels

**Level 1 - Five-year-old:**
Each toy is in a box with a note saying where the next box
is. To find toy #5, you open 5 boxes in sequence.

**Level 2 - Junior developer:**
A `Node` has `value` and `next` fields. The list has a `head`
pointer. `addFirst()` is O(1): create node, point to old
head, update head. `get(i)` is O(n): traverse from head.

**Level 3 - Mid engineer:**
Linked lists have poor cache behavior. Nodes are scattered in
heap memory. Each `node.next` access is likely a cache miss.
For most real-world use cases, an array-backed structure
(ArrayList) is faster despite "worse" Big O for insert.

**Level 4 - Senior/staff engineer:**
The correct use case for linked lists: implementing stacks and
queues where you only access the head/tail (both O(1)). Java's
`LinkedList` as a general-purpose `List` is almost always the
wrong choice - cache misses make it 5-10x slower than
`ArrayList` for traversal-heavy workloads.

**Level 5 - Expert/architect:**
Lock-free linked lists (using CAS - compare-and-swap) are the
foundation of wait-free queues and stacks in concurrent systems.
The pointer-based structure enables atomic head/tail updates
without global locking. Java's `ConcurrentLinkedQueue` is
implemented as a non-blocking linked list.

---

### How It Works

**Node structure:**

```java
class Node<T> {
    T value;
    Node<T> next;  // null for last node

    Node(T value) {
        this.value = value;
        this.next = null;
    }
}
```

**Operations:**

```java
// BAD: add to end in O(n) - traverse to find tail each time
class BadList<T> {
    Node<T> head;
    void addLast(T value) {
        Node<T> current = head;
        while (current.next != null) current = current.next;
        current.next = new Node<>(value); // O(n) each add
    }
}

// GOOD: maintain tail pointer for O(1) addLast
class GoodList<T> {
    Node<T> head;
    Node<T> tail;
    int size;

    void addLast(T value) {
        Node<T> node = new Node<>(value);
        if (tail != null) tail.next = node;
        else head = node;
        tail = node;
        size++;
    }  // O(1)

    void addFirst(T value) {
        Node<T> node = new Node<>(value);
        node.next = head;
        head = node;
        if (tail == null) tail = node;
        size++;
    }  // O(1)
}
```

**Memory layout:**

```
head -> [val=A|next=*] -> [val=B|next=*] -> [val=C|next=null]
         address:1000        address:2040        address:1520
```

Nodes at non-contiguous addresses → cache misses on traversal.

---

### Comparison Table

| Operation | Singly Linked | Doubly Linked | ArrayList |
|-----------|---------------|---------------|-----------|
| Access by index | O(n) | O(n) | O(1) |
| Insert at head | O(1) | O(1) | O(n) |
| Insert at tail | O(1) if tail ptr | O(1) | O(1) amortized |
| Insert after node | O(1) | O(1) | O(n) |
| Delete head | O(1) | O(1) | O(n) |
| Delete tail | O(n) | O(1) if prev ptr | O(1) |
| Cache behavior | Poor | Poor | Excellent |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LinkedList is faster for frequent insertions" | O(1) insert is only at known node; finding the position is O(n) first |
| "Java LinkedList should be used as a List" | ArrayDeque is almost always faster as a queue; ArrayList for general lists |
| "Linked lists waste less memory than arrays" | Each node carries a pointer (8 bytes on 64-bit) - often more overhead than array padding |
| "Circular linked list solves the tail problem" | It helps with rotation; does not improve general access patterns |

---

### Failure Modes & Diagnosis

**Failure 1: Memory leak via lingering head reference**
- Symptom: Memory grows; GC cannot collect list nodes
- Cause: External reference holds the head pointer; entire
  chain is live even after logical "deletion"
- Fix: Null out node references after logical removal;
  clear the list if discarding

**Failure 2: Null pointer on empty list traversal**
- Symptom: NullPointerException on `head.value`
- Cause: No null check before accessing head
- Fix: Always guard with `if (head != null)`

**Failure 3: O(n^2) total for n individual get(i) calls**
- Symptom: Performance degrades quadratically with list size
- Cause: Each `list.get(i)` on a LinkedList traverses from
  head; n calls → O(n^2) total
- Fix: Use ArrayList for random access; use iterator for
  sequential access

---

### Related Keywords

**Prerequisites:**
- [[DSA-002 - What Is a Data Structure?]]

**Builds toward:**
- [[DSA-011 - Doubly Linked List]]
- [[DSA-012 - Stack (LIFO)]]
- [[DSA-013 - Queue (FIFO)]]

**See also:**
- [[DSA-008 - Array (Static Array)]]
- [[DSA-009 - Dynamic Array (Resizable Array, ArrayList)]]

---

### Quick Reference Card

| Operation | Complexity |
|-----------|-----------|
| Access by index | O(n) |
| Insert at head | O(1) |
| Insert at tail | O(1) with tail ptr |
| Insert after known node | O(1) |
| Delete head | O(1) |
| Search | O(n) |

**When to use:** Implementing stacks/queues where only
head/tail operations are needed; when insert frequency at
known positions outweighs traversal.

**When NOT to use:** Random access by index; traversal-heavy
workloads; when cache behavior matters.

---

### The Surprising Truth

Java's `LinkedList` implements both `List` and `Deque`.
As a `List`, it is almost never the right choice - ArrayList
dominates. As a `Deque`, `ArrayDeque` is faster for most
workloads. The correct usage of `LinkedList` in Java is rare.

---

### Mastery Checklist

- [ ] Can implement a singly linked list (addFirst, addLast,
      delete, reverse) from memory
- [ ] Can reverse a linked list in O(n) time and O(1) space
- [ ] Understands why Java `LinkedList.get(i)` is O(n) and
      can explain the impact on a loop that calls it
- [ ] Knows when to prefer `ArrayDeque` over `LinkedList`
      for queue operations

---

### Think About This

1. How would you detect a cycle in a linked list? (Floyd's
   slow/fast pointer algorithm) What is the complexity?

2. Given a linked list, how would you find the middle node
   in a single pass without knowing the length?

3. **TYPE G:** A legacy codebase uses Java `LinkedList<User>`
   for a service that processes all users sequentially once
   per request. The list has grown to 50k users. Performance
   is degrading. Is the LinkedList the likely cause? How
   do you verify and what is the fix?

---

### Interview Deep-Dive

**Q1 (Easy):** How do you reverse a singly linked list?

> Iterative O(n) time, O(1) space:
> ```java
> Node prev = null, curr = head;
> while (curr != null) {
>     Node next = curr.next;
>     curr.next = prev;
>     prev = curr;
>     curr = next;
> }
> head = prev;
> ```
> Walk through: for each node, redirect its next pointer
> to the previous node. Three pointers: prev, curr, next.

**Q2 (Medium):** How do you find the middle of a linked list
in one pass?

> Floyd's slow/fast pointer (tortoise and hare):
> ```java
> Node slow = head, fast = head;
> while (fast != null && fast.next != null) {
>     slow = slow.next;
>     fast = fast.next.next;
> }
> return slow; // middle node
> ```
> Fast moves 2x speed. When fast reaches end, slow is at
> middle. O(n) time, O(1) space.

**Q3 (Hard):** Implement an LRU cache using a linked list
and hash map. What is the complexity?

> Combine: HashMap<Key, Node> (O(1) lookup) + Doubly Linked
> List (O(1) move-to-front and remove-from-tail).
> - get(key): O(1) - hash lookup + move node to front of DLL
> - put(key, val): O(1) - add to front; if at capacity,
>   remove tail node + its hash entry
> The DLL tracks recency (head = most recent, tail = least).
> Java's LinkedHashMap with accessOrder=true + custom
> removeEldestEntry implements this pattern.
