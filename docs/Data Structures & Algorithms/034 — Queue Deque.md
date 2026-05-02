---
layout: default
title: "Queue / Deque"
parent: "Data Structures & Algorithms"
nav_order: 34
permalink: /dsa/queue-deque/
number: "0034"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, LinkedList
used_by: BFS, LRU Cache, Sliding Window
related: Stack, Priority Queue, BlockingQueue
tags:
  - datastructure
  - foundational
  - algorithm
  - concurrency
---

# 034 — Queue / Deque

⚡ TL;DR — A Queue delivers items in the order they arrived (FIFO); a Deque extends this with O(1) add/remove at both ends.

| #034 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList | |
| **Used by:** | BFS, LRU Cache, Sliding Window | |
| **Related:** | Stack, Priority Queue, BlockingQueue | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Imagine a print-job spooler. Multiple users send documents to one printer. Without a Queue, there is no fair ordering — whoever checks the list last wins, jobs are processed in random order, early senders wait indefinitely, and the system is unpredictable and unfair.

THE BREAKING POINT:
Processing tasks in arrival order requires that the structure rewards patience: the earlier you arrived, the sooner you are served. A Stack does the opposite — last in, first out. A random-access list requires an external pointer to the "current" position and manual management. Neither enforces fairness automatically.

THE INVENTION MOMENT:
Restrict the collection so items are added to one end (tail) and removed from the other end (head). The first item added is always the first removed. Processing order matches arrival order automatically. This is exactly why the Queue was created.

### 📘 Textbook Definition

A **Queue** is an abstract data type implementing First-In, First-Out (FIFO) ordering. Elements are enqueued at the tail and dequeued from the head; all operations are O(1). A **Deque** (double-ended queue) generalises this by allowing O(1) add and remove at both the head and tail, making it usable as both a queue and a stack. Java's `ArrayDeque` implements `Deque` and is the preferred implementation for both use cases.

### ⏱️ Understand It in 30 Seconds

**One line:**
A waiting line: first person there is first to be served.

**One analogy:**
> Think of a supermarket checkout queue. You join at the back. The cashier serves the person at the front. No one cuts. No one is skipped. The order you arrived is the exact order you leave.

**One insight:**
A Queue's power is *fairness and predictability*. Any system that must process items without favouritism — network packets, print jobs, BFS exploration, thread scheduling — needs a FIFO contract. A Queue provides that contract as a data structure guarantee, not a policy you enforce manually.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Items exit in the exact order they entered (FIFO).
2. Add (enqueue) happens at the tail; remove (dequeue) happens at the head.
3. All four operations (enqueue, dequeue, peekHead, peekTail) are O(1).

DERIVED DESIGN:
To maintain O(1) at both ends without shifting, we need two independently movable pointers. An array with head and tail indices, interpreted as a circular buffer, achieves this. When tail wraps past the end of the array, it returns to index 0 — "circular" means we reuse vacated space without copying.

Why not just use an array with index 0 as head? Dequeuing from index 0 requires shifting all elements left — O(N). The circular buffer avoids this entirely: dequeue is just `head++`, enqueue is just `elements[tail++] = val`.

**Deque** extends to O(1) at the head too: `addFirst` is `elements[--head] = val`, `removeFirst` is `head++`. Both ends are symmetric.

THE TRADE-OFFS:
Gain: O(1) enqueue/dequeue, fair FIFO processing.
Cost: No random access; O(N) search/access by value or index.

### 🧪 Thought Experiment

SETUP:
You are implementing BFS on a graph with 1,000 nodes. You need to visit all nodes level by level (breadth-first), processing all neighbours before their children.

WHAT HAPPENS WITHOUT QUEUE (using Stack accidentally):
You use a Stack. When you visit node A with neighbours B and C, you push C then B. You pop B next — then B's children — going deep instead of broad. You implement DFS, not BFS. Level-by-level processing is destroyed.

WHAT HAPPENS WITH QUEUE:
You enqueue B and C. You dequeue B (first in), process it, enqueue B's children. Then dequeue C, process it, enqueue C's children. You maintain level order because arrival order = processing order.

THE INSIGHT:
The difference between BFS and DFS is literally one data structure choice: Queue vs Stack. The algorithm is identical — only the container changes. This makes the Queue's FIFO contract the precise mechanism that determines exploration order in graph traversal.

### 🧠 Mental Model / Analogy

> A Deque is like a queue at an airport with a VIP fast-track entrance at the front AND a regular entrance at the back. Normal passengers join the back; VIPs join the front. The agent at the desk always serves from the front. You can also pull someone off the back if they need to leave before being served.

"VIP entering front" → `addFirst()`
"Normal joining back" → `addLast()`
"Agent serving front" → `removeFirst()`
"Person leaving back" → `removeLast()`

Where this analogy breaks down: Real airport queues have a fixed order once joined; a Deque allows removal from either end at any time — there's no "cutting" social contract in the data structure.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A queue is a waiting line. First to arrive, first to be served. A deque lets you add or remove from either end.

**Level 2 — How to use it (junior developer):**
Use `Deque<T> queue = new ArrayDeque<>()`. For FIFO queue: `offer(val)` to add back, `poll()` to remove front. For LIFO stack: `push(val)` to add front, `pop()` to remove front. `peek()` looks at front without removing. Always use `offer/poll` over `add/remove` — they return null/false on failure instead of throwing exceptions.

**Level 3 — How it works (mid-level engineer):**
`ArrayDeque` uses a resizable circular array (`Object[] elements`). `head` and `tail` are integer indices. `addLast`: `elements[tail] = val; tail = (tail + 1) & (elements.length - 1)`. `pollFirst`: `val = elements[head]; elements[head] = null; head = (head + 1) & (capacity - 1)`. Capacity is always a power of 2 so the bitwise AND replaces modulo. When `head == tail`, the deque is empty; when `tail + 1 == head`, it's full — resize doubles the array.

**Level 4 — Why it was designed this way (senior/staff):**
The circular buffer design in `ArrayDeque` achieves amortized O(1) for all operations without the GC overhead of `LinkedList`. The power-of-2 capacity requirement allows bitwise AND for the wrap — `x & (n-1)` is equivalent to `x % n` but one instruction instead of a division. Java's `LinkedList` as a queue suffers from per-node allocation, double-pointer overhead, and GC pressure at high throughput. At 1M operations/second, `ArrayDeque` outperforms `LinkedList` by 3–5× due to cache locality.

### ⚙️ How It Works (Mechanism)

**Circular buffer (ArrayDeque):**
```
Capacity: 8 (power of 2)
head: 0, tail: 0 (empty)

offer("A"): elements[0]="A"; tail=1
offer("B"): elements[1]="B"; tail=2
offer("C"): elements[2]="C"; tail=3
poll():     val="A"; elements[0]=null; head=1

head=1, tail=3 → 2 elements: [B, C]
```

┌──────────────────────────────────────────────┐
│  Circular Buffer — Queue State               │
│                                              │
│  [null][B][C][null][null]...                 │
│         ↑        ↑                          │
│        head     tail                        │
│                                              │
│  offer("D") → elements[3]="D"; tail=4       │
│  poll()     → returns "B"; head=2           │
└──────────────────────────────────────────────┘

**Resize on full:**
When `(tail + 1) & mask == head`, the array is full. A new array of double size is allocated. Elements are copied starting from `head` in order, resetting `head=0, tail=originalSize`.

**BFS template using Queue:**
```java
Deque<Node> queue = new ArrayDeque<>();
queue.offer(root);
while (!queue.isEmpty()) {
    Node node = queue.poll();
    visit(node);
    for (Node neighbour : node.neighbours)
        queue.offer(neighbour);
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Producer generates task
→ task.offer() adds to tail [QUEUE ← YOU ARE HERE]
→ Consumer calls poll() from head
→ Task processed in arrival order
→ Next task immediately available
```

FAILURE PATH:
```
Producer far outpaces consumer
→ Queue grows unbounded
→ Heap exhaustion → OutOfMemoryError
→ Fix: use bounded BlockingQueue with back-pressure
```

WHAT CHANGES AT SCALE:
At high producer-consumer rates, a single `ArrayDeque` with external synchronization is a bottleneck. Use `ArrayBlockingQueue` (bounded, blocks producer when full) or `LinkedTransferQueue` (unbounded, lock-free for high throughput). The choice between bounded and unbounded is a back-pressure decision: bounded queues push back to the producer, preventing OOM.

### 💻 Code Example

**Example 1 — BFS level-order traversal:**
```java
void bfs(TreeNode root) {
    if (root == null) return;
    Deque<TreeNode> q = new ArrayDeque<>();
    q.offer(root);
    while (!q.isEmpty()) {
        int size = q.size(); // nodes at current level
        for (int i = 0; i < size; i++) {
            TreeNode node = q.poll();
            System.out.print(node.val + " ");
            if (node.left  != null) q.offer(node.left);
            if (node.right != null) q.offer(node.right);
        }
        System.out.println(); // next level
    }
}
```

**Example 2 — Deque as sliding window tracker:**
```java
// Maximum in every window of size k
int[] maxSlidingWindow(int[] nums, int k) {
    int n = nums.length;
    int[] result = new int[n - k + 1];
    // Deque stores indices; front = max element index
    Deque<Integer> dq = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        // Remove indices outside window
        while (!dq.isEmpty() && dq.peekFirst() < i-k+1)
            dq.pollFirst();
        // Remove smaller elements from back
        while (!dq.isEmpty()
               && nums[dq.peekLast()] < nums[i])
            dq.pollLast();
        dq.offerLast(i);
        if (i >= k - 1)
            result[i - k + 1] = nums[dq.peekFirst()];
    }
    return result;
}
```

### ⚖️ Comparison Table

| Structure | FIFO | LIFO | Both ends | Thread-safe | Best For |
|---|---|---|---|---|---|
| **ArrayDeque** | ✓ | ✓ | ✓ | ✗ | General single-thread queue/stack |
| ArrayBlockingQueue | ✓ | ✗ | ✗ | ✓ | Bounded producer-consumer |
| LinkedBlockingQueue | ✓ | ✗ | ✗ | ✓ | Unbounded producer-consumer |
| PriorityQueue | Priority | ✗ | ✗ | ✗ | Priority-ordered processing |
| ConcurrentLinkedQueue | ✓ | ✗ | ✗ | ✓ | Lock-free high-throughput |

How to choose: For single-threaded use, `ArrayDeque` is always preferred. For producer-consumer patterns, use `ArrayBlockingQueue` (bounded) to apply back-pressure or `LinkedTransferQueue` for maximum throughput.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LinkedList is a good Queue implementation | `ArrayDeque` outperforms `LinkedList` as a queue in all modern JVM benchmarks due to cache locality |
| Queue and Deque are different classes | `Deque` extends `Queue`; `ArrayDeque` implements `Deque` and serves as both |
| `add()` and `offer()` are equivalent | `add()` throws on full bounded queue; `offer()` returns false — use `offer/poll` for safe code |
| A Queue prevents OutOfMemoryError | Unbounded queues grow without limit; only bounded queues with back-pressure prevent OOME |
| Queue FIFO order is guaranteed across threads | Only concurrent Queue implementations (BlockingQueue, ConcurrentLinkedQueue) are thread-safe |

### 🚨 Failure Modes & Diagnosis

**1. Unbounded queue causing OutOfMemoryError**

Symptom: Heap exhaustion after sustained high load; heap dump shows millions of queue entries.

Root Cause: Producer rate exceeds consumer rate; unbounded `ArrayDeque` or `LinkedList` grows until OOM.

Diagnostic:
```bash
jmap -histo:live <pid> | head -20
# Look for large ArrayDeque or Node count
```

Fix: Replace with `ArrayBlockingQueue` with a capacity limit and implement back-pressure (block or drop with alert).

Prevention: Always bound queues in producer-consumer systems; monitor queue depth as a metric.

---

**2. Queue processed in wrong order (DFS instead of BFS)**

Symptom: BFS algorithm visits nodes in depth-first order; level-order output is wrong.

Root Cause: Accidentally used a `Stack`/`push`+`pop` instead of a Queue's `offer`+`poll`.

Diagnostic:
```bash
# Review code: are you using push/pop (Stack) 
# or offer/poll (Queue)?
grep -n "push\|pop\|offer\|poll" BfsAlgorithm.java
```

Fix: Replace `stack.push/pop` with `queue.offer/poll`.

Prevention: Name your variable `queue` when BFS is intended; use it only through the `Queue` interface.

---

**3. Concurrent modification from unsynchronized access**

Symptom: `ConcurrentModificationException` or corrupt queue state in multi-threaded code.

Root Cause: `ArrayDeque` is not thread-safe; concurrent offer and poll corrupt head/tail indices.

Diagnostic:
```bash
jstack <pid> | grep "RUNNABLE" 
# Multiple threads in ArrayDeque methods simultaneously
```

Fix: Use `ArrayBlockingQueue`, `LinkedBlockingDeque`, or `ConcurrentLinkedQueue` for shared queues.

Prevention: Never share a plain `ArrayDeque` between threads without external locking.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — the circular array is the backing store for `ArrayDeque`.
- `LinkedList` — alternative queue implementation; useful to understand why arrays are preferred.

**Builds On This (learn these next):**
- `BFS` — relies on a Queue to maintain level-order traversal in graph/tree search.
- `LRU Cache` — uses a Deque to track recency; O(1) remove-from-middle via doubly linked structure.
- `Sliding Window` — monotonic deque tracks range maxima/minima efficiently.

**Alternatives / Comparisons:**
- `Stack` — LIFO counterpart; same underlying `ArrayDeque`, different access pattern.
- `Priority Queue` — processes elements by priority, not arrival order.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ FIFO collection: first enqueued is first  │
│              │ dequeued; Deque extends to both ends      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Processing tasks in arrival order without │
│ SOLVES       │ fairness or ordering logic                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ BFS vs DFS is one choice: Queue vs Stack  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ BFS traversal, task scheduling, producer- │
│              │ consumer pipelines, sliding window        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Priority ordering needed (use             │
│              │ PriorityQueue) or LIFO needed (Stack)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fair FIFO processing vs no random access  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A checkout queue: first in line is       │
│              │  always first served"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stack → BFS → Priority Queue              │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A Kafka consumer group reads messages from a topic and processes them via an in-memory `ArrayDeque`. The consumer processes 10,000 messages/second but the producer publishes 15,000 messages/second during peak. After 10 minutes, the service crashes with `OutOfMemoryError`. Trace exactly what happens step by step, describe exactly where the queue backlog forms, and propose two architectural solutions with their respective trade-offs.

**Q2.** The sliding window maximum problem requires finding the maximum element in every contiguous subarray of size k. A naïve solution uses O(k) per window for O(N*k) total. Show why a monotonic deque solves this in O(N) — specifically, what invariant does the deque maintain, and why does pollLast() before inserting a new element preserve that invariant without losing future maxima?

