---
id: DSA-086
title: LRU Cache Implementation (LinkedHashMap Pattern)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-014, DSA-011
used_by: DSA-077, DSA-087
related: DSA-087, DSA-014, DSA-011
tags:
  - data-structures
  - lru-cache
  - cache-eviction
  - linked-hash-map
  - o-1
  - design
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 86
permalink: /technical-mastery/dsa/lru-cache/
---

## TL;DR

LRU Cache evicts the least-recently-used item when full,
implemented with HashMap + Doubly Linked List for O(1) get
and put - or with Java's LinkedHashMap in 3 lines. The
#1 most-asked cache design interview question.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-086 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, LRU-cache, eviction-policy |
| **Prerequisites** | DSA-014, DSA-011 |

---

### The Problem This Solves

A database call takes 10ms. The top 1% of queries account
for 50% of traffic. Cache those 1% in RAM: 99% of response
time drops to microseconds. But RAM is finite - when the
cache is full, which entry to evict? LRU evicts the item
not accessed for the longest time - assuming recently used
items will be used again soon (temporal locality).

---

### Two Implementations

**Option A: HashMap + Doubly Linked List (from scratch)**

```java
class LRUCache {
    private class Node {
        int key, val;
        Node prev, next;
        Node(int k, int v) { key = k; val = v; }
    }

    private final int capacity;
    private final Map<Integer, Node> map = new HashMap<>();
    // Sentinel head/tail for O(1) operations
    private final Node head = new Node(0, 0);
    private final Node tail = new Node(0, 0);

    LRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    private void remove(Node n) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    private void insertAfterHead(Node n) {
        n.next = head.next;
        n.prev = head;
        head.next.prev = n;
        head.next = n;
    }

    // Get: O(1) - move to MRU position
    int get(int key) {
        if (!map.containsKey(key)) return -1;
        Node n = map.get(key);
        remove(n);
        insertAfterHead(n); // mark as most-recently-used
        return n.val;
    }

    // Put: O(1) - evict LRU if needed
    void put(int key, int val) {
        if (map.containsKey(key)) {
            Node n = map.get(key);
            remove(n);
            n.val = val;
            insertAfterHead(n);
        } else {
            if (map.size() == capacity) {
                // Evict LRU: node before tail
                Node lru = tail.prev;
                remove(lru);
                map.remove(lru.key);
            }
            Node n = new Node(key, val);
            insertAfterHead(n);
            map.put(key, n);
        }
    }
}
```

**Option B: Java LinkedHashMap (production shortcut)**

```java
class LRUCacheSimple extends LinkedHashMap<Integer, Integer> {
    private final int capacity;

    LRUCacheSimple(int capacity) {
        super(capacity, 0.75f, true); // accessOrder=true!
        this.capacity = capacity;
    }

    int get(int key) {
        return super.getOrDefault(key, -1); // updates access order
    }

    void put(int key, int val) {
        super.put(key, val); // updates access order
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > capacity; // auto-evict when over capacity
    }
}
// 3 lines vs 50 lines - use this in production code
// Use the DLL version only when Java's LinkedHashMap isn't available
```

---

### How LinkedHashMap Works Internally

LinkedHashMap maintains a doubly-linked list through all
entries in insertion order (default) or access order
(`accessOrder=true`). When `accessOrder=true`:
- `get(k)` moves the entry to the end of the linked list
- `put(k,v)` for existing key moves it to the end
- `removeEldestEntry()` callback triggers after each put
  to allow custom eviction; returning true removes the
  head entry (oldest/least-recently-used)

This is the EXACT HashMap + DLL design described above,
implemented in the JDK.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LRU is always the best eviction policy" | LRU can thrash for cyclic access patterns (cache size = pattern size - 1); LFU (DSA-087) handles repeated popular items better |
| "LinkedHashMap is thread-safe for LRU" | LinkedHashMap is NOT thread-safe; use Collections.synchronizedMap() or ConcurrentHashMap with explicit eviction logic for multi-threaded use |

---

### Failure Modes & Diagnosis

**Failure: LRU cache hit rate unexpectedly low**
- Cause 1: Cache capacity too small; all entries evicted
  before being reused
- Cause 2: Access pattern is cyclic (scan through n items
  with cache size n-1 = 0% hit rate)
- Diagnosis: Instrument hit/miss rate; graph access patterns
- Fix: Increase capacity; or switch to CLOCK algorithm
  or 2Q cache for scan-resistant behavior

---

### Quick Reference Card

| Operation | LRU Cache |
|-----------|----------|
| Get | O(1) |
| Put | O(1) |
| Eviction policy | Least-recently-used |
| Java shortcut | LinkedHashMap(cap, 0.75f, true) |
| Thread-safe version | ConcurrentLinkedHashMap (Guava) |

---

### The Surprising Truth

CPU L1/L2/L3 caches use approximations of LRU called
"PLRU" (Pseudo-LRU) because true LRU requires tracking
last-access time for every cache line - too much hardware.
PLRU uses one bit per cache entry (indicating recently used
or not) and achieves ~95% of true LRU's effectiveness at
a fraction of the hardware cost. The algorithm you
implement in interviews is actually more precise than what
your CPU does.

---

### Mastery Checklist

- [ ] Can implement LRU from scratch with HashMap + DLL
- [ ] Can implement it in 3 lines with LinkedHashMap
- [ ] Knows LinkedHashMap(accessOrder=true) is the key flag

---

### Interview Deep-Dive

**Q1 (Hard - LeetCode 146):** Design an LRU cache with
O(1) get and O(1) put operations.

> HashMap + Doubly Linked List.
> HashMap: key → Node reference for O(1) access.
> DLL: maintains access order; MRU at head, LRU at tail.
> Sentinel head and tail nodes avoid null checks.
> Get: map lookup O(1), move to head O(1) DLL ops.
> Put (new): create node, add to map, insert at head,
>   evict tail if over capacity.
> Put (update): map lookup, update value, move to head.
> All operations: O(1) time. O(capacity) space.
> Java shortcut: LinkedHashMap with accessOrder=true +
> override removeEldestEntry - but interviewers expect
> you to know the HashMap+DLL approach.
