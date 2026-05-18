---
id: DSA-024
title: Build a Stack and Queue from Scratch
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-009, DSA-010, DSA-012, DSA-013
used_by: DSA-035
related: DSA-012, DSA-013, DSA-038
tags:
  - data-structures
  - stack
  - queue
  - implementation
  - linked-list
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/dsa/build-stack-queue-from-scratch/
---

## TL;DR

Implementing Stack and Queue from scratch with a linked list
reinforces core DSA: nodes, pointers, O(1) operations at
both ends, and the discipline of maintaining invariants.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-024 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, implementation, linked-list |
| **Prerequisites** | DSA-009, DSA-010, DSA-012, DSA-013 |

---

### The Problem This Solves

Using `java.util.Stack` and `ArrayDeque` hides the mechanics.
Building from scratch forces you to think through: how do
nodes link, what constitutes an empty structure, what
invariants must the implementation maintain, and how are
edge cases (empty pop/dequeue) handled.

---

### How It Works

**Stack from linked list (O(1) push and pop):**

```java
class LinkedStack<T> {
    private static class Node<T> {
        T value;
        Node<T> next;
        Node(T value) { this.value = value; }
    }

    private Node<T> top;
    private int size;

    public void push(T value) {
        Node<T> node = new Node<>(value);
        node.next = top;
        top = node;
        size++;
    }

    public T pop() {
        if (isEmpty())
            throw new NoSuchElementException("Stack is empty");
        T value = top.value;
        top = top.next;  // unlink head node (GC eligible)
        size--;
        return value;
    }

    public T peek() {
        if (isEmpty())
            throw new NoSuchElementException("Stack is empty");
        return top.value;
    }

    public boolean isEmpty() { return top == null; }
    public int size() { return size; }
}
```

**Queue from linked list (O(1) enqueue and dequeue):**

```java
class LinkedQueue<T> {
    private static class Node<T> {
        T value;
        Node<T> next;
        Node(T value) { this.value = value; }
    }

    private Node<T> head;  // dequeue from here
    private Node<T> tail;  // enqueue here
    private int size;

    public void enqueue(T value) {
        Node<T> node = new Node<>(value);
        if (tail != null) tail.next = node;
        tail = node;
        if (head == null) head = node;  // first element
        size++;
    }

    public T dequeue() {
        if (isEmpty())
            throw new NoSuchElementException("Queue is empty");
        T value = head.value;
        head = head.next;
        if (head == null) tail = null;  // queue now empty
        size--;
        return value;
    }

    public boolean isEmpty() { return head == null; }
    public int size() { return size; }
}
```

**Common interview variant: Queue using two Stacks:**

```java
// Enqueue: push to stack1
// Dequeue: if stack2 empty, drain stack1 into stack2
// Amortized O(1) per operation
class QueueViaStacks<T> {
    Deque<T> inbox = new ArrayDeque<>();   // enqueue
    Deque<T> outbox = new ArrayDeque<>();  // dequeue

    void enqueue(T value) {
        inbox.push(value);
    }

    T dequeue() {
        if (outbox.isEmpty()) {
            while (!inbox.isEmpty()) outbox.push(inbox.pop());
        }
        if (outbox.isEmpty())
            throw new NoSuchElementException();
        return outbox.pop();
    }
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java's Stack class is the right stack" | `java.util.Stack` is synchronized and extends Vector (legacy). Use `ArrayDeque` as a stack in production |
| "Queue is harder to implement than Stack" | Queue needs two pointers (head and tail) but each operation is still O(1) with a linked list |

---

### Quick Reference Card

| Structure | Key pointers | push/enqueue | pop/dequeue |
|-----------|-------------|--------------|-------------|
| Stack | top | head insert | head remove |
| Queue | head + tail | tail insert | head remove |

---

### Mastery Checklist

- [ ] Can implement a linked-list Stack with push/pop/peek
      handling empty case correctly
- [ ] Can implement a linked-list Queue with O(1) enqueue
      and dequeue using head + tail pointers
- [ ] Can implement Queue using two stacks and explain
      amortized O(1) cost

---

### Interview Deep-Dive

**Q1 (Medium):** Implement a min-stack that supports push,
pop, and getMin all in O(1).

> Use two stacks: one for values, one for minimums. On push,
> push to value stack. Push to min stack if value <= current
> min (or if min stack is empty). On pop, pop from value stack;
> if popped value equals top of min stack, also pop min stack.
> getMin returns min stack's top. O(1) for all operations,
> O(n) space.
>
> ```java
> class MinStack {
>     Deque<Integer> vals = new ArrayDeque<>();
>     Deque<Integer> mins = new ArrayDeque<>();
>     void push(int val) {
>         vals.push(val);
>         if (mins.isEmpty() || val <= mins.peek())
>             mins.push(val);
>     }
>     void pop() {
>         int val = vals.pop();
>         if (val == mins.peek()) mins.pop();
>     }
>     int getMin() { return mins.peek(); }
> }
> ```
