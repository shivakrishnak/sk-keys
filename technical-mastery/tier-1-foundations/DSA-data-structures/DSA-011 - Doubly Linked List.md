---
id: DSA-011
title: Doubly Linked List
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-010
used_by: DSA-086, DSA-087
related: DSA-010, DSA-045
tags:
  - data-structures
  - linked-list
  - doubly-linked
  - lru
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/dsa/doubly-linked-list/
---

## TL;DR

A doubly linked list adds a backward pointer to each node,
enabling O(1) delete at any known node and backward traversal
- the critical structure underlying LRU caches.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-011 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, linked-list, doubly-linked, lru |
| **Prerequisites** | DSA-010 |

---

### The Problem This Solves

A singly linked list can delete a node in O(1) only if you
have a reference to its PREVIOUS node. Without a back
pointer, deletion requires O(n) traversal to find the
predecessor.

Doubly linked lists add a `prev` pointer so deletion at any
known node is O(1) without knowing its predecessor.

---

### Textbook Definition

A doubly linked list is a linked list where each node
contains a reference to both the next and previous nodes.
The head's `prev` is null; the tail's `next` is null.
This enables O(1) deletion at any known node, O(1) prepend
and append, and bidirectional traversal.

---

### Mental Model / Analogy

**The two-way street:** Each house on a street has a sign
pointing both left and right. You can start at any house
and walk either direction without backtracking.

---

### How It Works

**Node structure:**

```java
class Node<T> {
    T value;
    Node<T> prev;
    Node<T> next;
}
```

**O(1) delete at known node:**

```java
// BAD (singly linked): O(n) to find prev
void delete(Node<T> target) {
    Node<T> curr = head;
    while (curr.next != target) curr = curr.next; // O(n)
    curr.next = target.next;
}

// GOOD (doubly linked): O(1) with prev pointer
void delete(Node<T> target) {
    if (target.prev != null) target.prev.next = target.next;
    else head = target.next;  // target was head
    if (target.next != null) target.next.prev = target.prev;
    else tail = target.prev;  // target was tail
    target.prev = target.next = null; // help GC
}
```

**LRU cache pattern:**

```
HashMap<K, Node> for O(1) lookup
+---+                              +---+
|LRU|<--[B]<--[C]<--[D]<--[E]-->|MRU|
+---+  prev/next pointers        +---+

On get(K): find node via map, move to MRU end (O(1))
On put(K): add to MRU end; if capacity, remove LRU end (O(1))
```

---

### Comparison Table

| | Singly Linked | Doubly Linked | Array |
|--|--------------|---------------|-------|
| Delete at known node | O(n) find prev | O(1) | O(n) shift |
| Backward traversal | No | Yes | Yes |
| Memory per node | data + 1 ptr | data + 2 ptrs | data only |
| Insert at head | O(1) | O(1) | O(n) |
| Insert at tail | O(1) w/ tail | O(1) | O(1) amortized |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Doubly linked lists are always better than singly linked" | Extra pointer adds memory overhead; singly linked suffices when deletion at known-node is not needed |
| "LinkedHashMap is just a HashMap" | It is a HashMap + DLL internally, enabling LRU cache behavior |

---

### Failure Modes & Diagnosis

**Failure: Broken prev/next pointers after update**
- Symptom: List traversal produces wrong results or loops
- Cause: Incomplete pointer update during insert/delete
  (forgot to update prev pointer of successor)
- Fix: Always update all four pointers: prev.next, next.prev,
  node.prev, node.next

---

### Quick Reference Card

| Use Case | Why DLL |
|----------|---------|
| LRU cache | O(1) move-to-front + O(1) remove-from-tail |
| Browser history | Bidirectional navigation |
| Text editor cursor | Move forward/backward in O(1) |
| Undo/redo system | Walk history both directions |

---

### The Surprising Truth

Java's `LinkedHashMap` is a hash map with a doubly linked
list connecting all entries in insertion (or access) order.
By overriding `removeEldestEntry()`, it becomes a complete
LRU cache in ~5 lines of code - built into the JDK.

---

### Mastery Checklist

- [ ] Can implement DLL insert/delete with correct pointer
      updates from memory
- [ ] Can build an LRU cache using DLL + HashMap
- [ ] Understands why DLL is preferable to singly linked
      for LRU cache implementation

---

### Think About This

1. In an LRU cache with doubly linked list, what is the
   time complexity of each operation: get, put, evict?
   Why does the DLL enable O(1) eviction while a singly
   linked list cannot?

2. Implement a doubly linked list that supports O(1)
   insert and delete at head/tail and O(n) reverse.

---

### Interview Deep-Dive

**Q1 (Medium):** Design an LRU cache with O(1) get and put.

> Combine: `HashMap<Key, Node>` for O(1) lookup +
> doubly linked list for O(1) recency tracking.
> - `get(key)`: lookup node, move to list front → O(1)
> - `put(key, val)`: create node at front; if over capacity,
>   remove tail node + its map entry → O(1)
>
> Java shortcut: `LinkedHashMap(capacity, 0.75f, true)` with
> `removeEldestEntry(e) { return size() > capacity; }`.
