---
id: DSA-082
title: Skip List
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-010, DSA-017
used_by: DSA-077
related: DSA-053, DSA-054, DSA-086
tags:
  - data-structures
  - skip-list
  - probabilistic
  - sorted-structure
  - redis
  - concurrent
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 82
permalink: /technical-mastery/dsa/skip-list/
---

## TL;DR

A Skip List is a probabilistic multi-level linked list that
achieves O(log n) search, insert, and delete through random
"express lanes" - simpler to implement than balanced trees
and the data structure behind Redis's sorted sets.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-082 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, skip-list, probabilistic |
| **Prerequisites** | DSA-010, DSA-017 |

---

### The Problem This Solves

Linked lists: O(n) search. Balanced BSTs: O(log n) but
complex to implement correctly (rotations, rebalancing).
Skip Lists achieve O(log n) expected time via probabilistic
balancing - no rotations, simple implementation, and
naturally supports concurrent modifications (Redis uses
them for exactly this reason).

---

### Textbook Definition

A Skip List is a layered linked list structure with multiple
levels. Level 0 = complete sorted linked list. Level k =
a "highway" containing a random subset of level k-1 elements
(each element promoted with probability p=0.5). Search
proceeds from top level, skipping large portions; drops
down when overshot. Expected height: O(log n). Expected
time: O(log n) for search, insert, delete.

---

### How It Works

**Structure visualization:**

```
Level 3: head -----------------------------> [50] --> null
Level 2: head ------> [20] ---------------> [50] --> null
Level 1: head ------> [20] --> [30] ------> [50] --> null
Level 0: head -> [10] -> [20] -> [30] -> [40] -> [50] -> null

Search for 35:
  Level 3: head → 50 (overshoot), drop to level 2
  Level 2: head → 20 → 50 (overshoot), drop to level 1
  Level 1: head → 20 → 30 → 50 (overshoot), drop to level 0
  Level 0: head → 10 → 20 → 30 → 40 (found 35 between 30 and 40)
```

**Implementation:**

```java
class SkipList {
    static final int MAX_LEVEL = 16;
    static final double P = 0.5;

    class Node {
        int val;
        Node[] next; // next[i] = next node at level i
        Node(int val, int level) {
            this.val = val;
            this.next = new Node[level + 1];
        }
    }

    private Node head = new Node(Integer.MIN_VALUE, MAX_LEVEL);
    private int level = 0;
    private Random rand = new Random();

    // Probabilistic level assignment: O(log 1/P) expected
    private int randomLevel() {
        int lvl = 0;
        while (rand.nextDouble() < P && lvl < MAX_LEVEL) lvl++;
        return lvl;
    }

    // Search: O(log n) expected
    boolean search(int target) {
        Node curr = head;
        for (int i = level; i >= 0; i--) {
            while (curr.next[i] != null &&
                   curr.next[i].val < target) {
                curr = curr.next[i];
            }
        }
        curr = curr.next[0];
        return curr != null && curr.val == target;
    }

    // Insert: O(log n) expected
    void insert(int val) {
        Node[] update = new Node[MAX_LEVEL + 1];
        Node curr = head;
        for (int i = level; i >= 0; i--) {
            while (curr.next[i] != null &&
                   curr.next[i].val < val) {
                curr = curr.next[i];
            }
            update[i] = curr; // remember predecessor at each level
        }
        int newLevel = randomLevel();
        if (newLevel > level) {
            for (int i = level + 1; i <= newLevel; i++) {
                update[i] = head;
            }
            level = newLevel;
        }
        Node newNode = new Node(val, newLevel);
        for (int i = 0; i <= newLevel; i++) {
            newNode.next[i] = update[i].next[i];
            update[i].next[i] = newNode;
        }
    }
}
```

---

### Comparison Table

| Property | Skip List | Red-Black Tree | AVL Tree |
|---------|-----------|---------------|---------|
| Search | O(log n) expected | O(log n) | O(log n) |
| Insert | O(log n) expected | O(log n) | O(log n) |
| Implementation | Simple | Complex | Complex |
| Concurrent ops | Easy (lock-free possible) | Hard | Hard |
| Deterministic | No (probabilistic) | Yes | Yes |
| Usage | Redis sorted sets | TreeMap | Legacy |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Skip List is slower than balanced trees due to randomness" | Expected time is O(log n) and practically fast; constants are competitive with RB trees; random level assignment is O(1) |
| "Skip List needs complex implementation" | It's significantly simpler than Red-Black trees; no rotations, no color flipping |

---

### Failure Modes & Diagnosis

**Failure: Skip list degrades to O(n) performance**
- Cause: Extremely unlucky random level assignments
  (all nodes at level 0); probability 0.5^n ≈ 0 for large n
- In practice: This is theoretically possible but vanishingly
  unlikely; Skip lists are robust in practice
- Real risk: MAX_LEVEL too low for actual data size;
  use MAX_LEVEL = log(expectedSize)/log(1/P) + 1

---

### Quick Reference Card

| Property | Skip List |
|---------|----------|
| Search | O(log n) expected |
| Insert | O(log n) expected |
| Delete | O(log n) expected |
| Space | O(n log n) expected (extra pointers) |
| Real usage | Redis sorted sets (ZADD, ZRANK) |
| Concurrent | Lock-free variants exist |

---

### The Surprising Truth

Redis's sorted sets (ZSET) use a skip list as the primary
data structure, not a balanced tree. When you call ZADD,
ZRANK, ZRANGE on Redis, you're using a skip list under the
hood. Redis chose skip lists over red-black trees because:
(1) simpler implementation = fewer bugs; (2) range queries
are naturally efficient (sequential level-0 traversal);
(3) concurrent access patterns are easier with skip lists
than with rotating trees.

---

### Mastery Checklist

- [ ] Can explain skip list search with the multi-level
      "highway" analogy
- [ ] Knows Redis sorted sets use skip lists
- [ ] Understands probabilistic height guarantees

---

### Interview Deep-Dive

**Q1 (Hard):** Redis uses a skip list for sorted sets.
When would you choose a skip list over a red-black tree?

> Choose skip list when:
> 1. Range queries are frequent: level-0 linked list
>    makes sequential range scan O(k) vs tree's O(k log n)
> 2. Concurrent access needed: lock-free skip list
>    implementations exist; concurrent RB trees require
>    complex locking or transactional memory
> 3. Implementation simplicity matters: skip list avoids
>    rotations and rebalancing; fewer lines of code = fewer
>    bugs in production
> 4. Memory overhead acceptable: skip list uses O(n log n)
>    pointers vs RB tree's O(n)
> Choose RB tree when: deterministic O(log n) guarantees
> required (skip list is expected O(log n)); or memory
> is constrained.
