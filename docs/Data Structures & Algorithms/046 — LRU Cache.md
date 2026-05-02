---
layout: default
title: "LRU Cache"
parent: "Data Structures & Algorithms"
nav_order: 46
permalink: /dsa/lru-cache/
number: "0046"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: HashMap, LinkedList, Queue / Deque
used_by: LFU Cache, HTTP Caching, OS Page Cache
related: LFU Cache, MRU Cache, TTL Cache
tags:
  - datastructure
  - intermediate
  - algorithm
  - caching
  - performance
---

# 046 — LRU Cache

⚡ TL;DR — An LRU Cache evicts the least recently used item when full, keeping hot data in O(1) time using a HashMap plus a doubly linked list.

| #046 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HashMap, LinkedList, Queue / Deque | |
| **Used by:** | LFU Cache, HTTP Caching, OS Page Cache | |
| **Related:** | LFU Cache, MRU Cache, TTL Cache | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A database query cache has limited memory for 1,000 entries but serves 10,000 different queries. You must decide which cached results to evict when new ones arrive. Random eviction keeps cold data as often as hot data. FIFO eviction may evict a query you just answered 10 seconds ago if it was the first to be inserted. Neither strategy reflects *how recently or frequently* the data was needed.

THE BREAKING POINT:
Cache eviction without recency knowledge wastes the cache by keeping cold, stale results and evicting warm, active ones. The result: cache hit rates of 20–30% instead of the 60–80% achievable with a recency-aware strategy.

THE INVENTION MOMENT:
Track which entry was accessed most recently. When the cache is full, evict the entry accessed least recently (the one you haven't needed for the longest time). This exploits temporal locality — the empirical observation that recently used data is likely to be used again soon. This is exactly why the LRU Cache was created.

### 📘 Textbook Definition

An **LRU (Least Recently Used) Cache** is a fixed-capacity cache with an eviction policy that removes the entry that was accessed (read or written) least recently when the cache is full and a new entry must be inserted. All operations — `get(key)` and `put(key, value)` — must complete in O(1) time. The standard implementation combines a `HashMap` (for O(1) key lookup) with a **doubly linked list** (for O(1) move-to-front and evict-from-tail), where the head is the most recently used and the tail is the least recently used.

### ⏱️ Understand It in 30 Seconds

**One line:**
A fixed-size cache that always evicts the longest-unused item when full.

**One analogy:**
> An LRU cache is like a desk with room for 5 open books. Whenever you pick up a new book, you put it at the front of the desk. If the desk is full, you remove the book at the very back — the one you haven't touched in the longest time. The most-used books stay front and center.

**One insight:**
The trick of combining a HashMap with a doubly linked list lets you do *both* O(1) lookup *and* O(1) update of access order. The HashMap finds the node in O(1); the doubly linked list moves it to the front and removes the tail in O(1). Neither structure alone can do both.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Every `get` and `put` marks the accessed entry as "most recently used" — it moves to the head.
2. When capacity is exceeded, the tail entry (least recently used) is evicted.
3. Every operation is O(1) — not O(N) search or O(N) reorder.

DERIVED DESIGN:
Why a doubly linked list?
- Move-to-front: unlink a node from its position (need `prev` pointer → doubly linked), relink at head. With only a singly linked list, unlinking requires knowing the predecessor — O(N) to find.
- Evict from tail: remove last node. With doubly linked: `tail = tail.prev; tail.next = null`. O(1).

Why a HashMap?
- O(1) access to the linked list node by key. Without it, finding a key in the linked list is O(N).

The HashMap stores `{key → Node}` where `Node` holds `(key, value, prev, next)`. The key is stored in the node so that when the tail is evicted, we can also remove it from the HashMap.

THE TRADE-OFFS:
Gain: O(1) get and put with optimal eviction for temporal-locality workloads.
Cost: 2× memory per entry (HashMap + list node), poor fit for frequency-based access patterns (use LFU), no built-in TTL.

### 🧪 Thought Experiment

SETUP:
LRU cache with capacity 3. Sequence: put(1), put(2), put(3), get(1), put(4).

WHAT HAPPENS WITHOUT LRU AWARENESS (FIFO queue):
put(1): cache = [1]. put(2): [1,2]. put(3): [1,2,3]. get(1): hit. put(4): FIFO evicts 1 (inserted first). Cache = [2,3,4]. get(1): miss — 1 was just accessed but evicted!

WHAT HAPPENS WITH LRU:
put(1): [1]. put(2): [2,1]. put(3): [3,2,1] (LRU=1).
get(1): mark 1 as MRU: [1,3,2] (LRU=2).
put(4): evict LRU=2. Cache = [4,1,3]. get(1): hit!

THE INSIGHT:
LRU preserved the entry that was just accessed (1) over the one that hadn't been touched (2). FIFO preserved insertion order, which has nothing to do with what's currently useful. Recency is a proxy for future utility — and empirically it's a very good proxy.

### 🧠 Mental Model / Analogy

> An LRU cache is like a browser's tab order by last use. The tab you switched to most recently is at the front. When your browser needs to suspend a tab to save memory, it suspends the one at the back — the one you haven't visited in hours.

"Tabs in recency order" → doubly linked list (head=MRU, tail=LRU)
"Tab title lookup" → HashMap (key → node)
"Switch to tab" → get() → move node to head
"Open new tab" → put() → new node at head; evict tail if full
"Suspend least-used tab" → evict tail node

Where this analogy breaks down: Browser tab suspension uses recency, but LFU would be better for tabs you visit regularly but infrequently (like a monthly report). LRU doesn't account for frequency — only recency.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A fixed-size storage that automatically removes the oldest-unused item to make room. The item you haven't touched in the longest time gets removed first.

**Level 2 — How to use it (junior developer):**
Java: use `LinkedHashMap` with `accessOrder=true` and override `removeEldestEntry()`. Custom: implement with `HashMap<K, DLinkedNode<K,V>>` + doubly linked list with sentinel head/tail nodes. Always store the key in the list node — needed to remove from HashMap on eviction. Check `size == capacity` before inserting.

**Level 3 — How it works (mid-level engineer):**
Two sentinel nodes (dummyHead, dummyTail) simplify edge cases (no null checks on empty list). `get(key)`: HashMap lookup → move node after dummyHead → return value. `put(key, value)`: if exists, update + move to front; else create node + add after dummyHead + if `size > capacity` remove node before dummyTail + remove its key from HashMap.

**Level 4 — Why it was designed this way (senior/staff):**
LRU is the standard CPU cache replacement policy and OS page replacement algorithm. The combination of HashMap + doubly linked list is O(1) for all operations — no other structure achieves this without trade-offs. Java's `LinkedHashMap(initialCapacity, loadFactor, accessOrder=true)` implements LRU in a single class: it maintains an internal doubly linked list ordered by access time. `removeEldestEntry()` is the hook for eviction. Caffeine (the modern Java cache library, used by Spring Boot's default cache) uses a Window-TinyLFU policy (admission + LFU + recency) that outperforms pure LRU by 50–80% on real workloads — LRU's weakness is workloads with "scans" (large reads that displace hot data without being hot themselves).

### ⚙️ How It Works (Mechanism)

**Node structure:**
```java
class Node<K, V> {
    K key; V val;
    Node<K, V> prev, next;
}
```

**LRU Cache internals:**
```java
class LRUCache<K, V> {
    Map<K, Node<K,V>> map = new HashMap<>();
    Node<K,V> head = new Node<>(), tail = new Node<>();
    int capacity, size;

    LRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail; tail.prev = head; // sentinels
    }

    // Move existing node to just after head (MRU position)
    void moveToFront(Node<K,V> node) {
        remove(node);
        addToFront(node);
    }

    void remove(Node<K,V> n) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    void addToFront(Node<K,V> n) {
        n.next = head.next; n.prev = head;
        head.next.prev = n; head.next = n;
    }

    V get(K key) {
        Node<K,V> n = map.get(key);
        if (n == null) return null;
        moveToFront(n);
        return n.val;
    }

    void put(K key, V value) {
        Node<K,V> n = map.get(key);
        if (n != null) { n.val = value; moveToFront(n); return; }
        n = new Node<>(); n.key = key; n.val = value;
        map.put(key, n);
        addToFront(n);
        if (++size > capacity) {
            Node<K,V> lru = tail.prev;
            remove(lru); map.remove(lru.key); size--;
        }
    }
}
```

┌──────────────────────────────────────────────┐
│  LRU Cache state: capacity=3, put(1,2,3)     │
│                                              │
│  DLL: head ⇔ [3] ⇔ [2] ⇔ [1] ⇔ tail        │
│  Map: {1→node1, 2→node2, 3→node3}           │
│                                              │
│  get(1): move node1 to front                │
│  DLL: head ⇔ [1] ⇔ [3] ⇔ [2] ⇔ tail        │
│                                              │
│  put(4): capacity exceeded, evict tail.prev  │
│  Evict [2]; add [4] to front                │
│  DLL: head ⇔ [4] ⇔ [1] ⇔ [3] ⇔ tail        │
└──────────────────────────────────────────────┘

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Request arrives with key K
→ get(K) checks HashMap: O(1)
→ [LRU CACHE ← YOU ARE HERE]
→ Hit: move to front, return value
→ Miss: compute/fetch value
→ put(K, value): add to front, evict tail if full
```

FAILURE PATH:
```
Cache scan: sequential access of N unique keys
→ Each access evicts MRU, fills with new
→ After scan, all original hot keys evicted
→ Hit rate drops to 0% (cache pollution)
→ Fix: use LIRS or TinyLFU for scan-resistant policy
```

WHAT CHANGES AT SCALE:
A single-threaded LRU is O(1) but needs external synchronization for concurrent access. `Collections.synchronizedMap` on a `LinkedHashMap` creates a global lock — a bottleneck at high concurrency. Caffeine's W-TinyLFU uses a write buffer + frequency sketch + LRU window for concurrent writes without global locking. At distributed scale (cross-machine caching), LRU is approximated through TTL + access-time tracking; true distributed LRU is impractical due to the coordination overhead.

### 💻 Code Example

**Example 1 — One-liner using LinkedHashMap:**
```java
// Java's LinkedHashMap with accessOrder=true is an LRU cache
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    LRUCache(int capacity) {
        super(capacity, 0.75f, true); // accessOrder=true
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K,V> e) {
        return size() > capacity; // evict when over capacity
    }
}

LRUCache<Integer, String> cache = new LRUCache<>(3);
cache.put(1, "one"); cache.put(2, "two"); cache.put(3, "three");
cache.get(1);       // marks 1 as MRU
cache.put(4, "four"); // evicts 2 (LRU after get(1) made 1 MRU)
System.out.println(cache.containsKey(2)); // false — evicted
```

**Example 2 — Thread-safe LRU with Caffeine:**
```java
// Production-grade: Caffeine W-TinyLFU
Cache<String, UserProfile> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(5, TimeUnit.MINUTES)
    .recordStats()
    .build();

UserProfile profile = cache.get(userId, id -> db.load(id));
// Caffeine handles eviction, expiry, and concurrent access
System.out.println(cache.stats().hitRate());
```

### ⚖️ Comparison Table

| Policy | Hit Rate | Scan Resistant | Implementation | Best For |
|---|---|---|---|---|
| **LRU** | High | ✗ | Medium | General temporal locality |
| LFU | Higher (freq) | ✓ | Hard | Frequency-based access |
| FIFO | Low | ✗ | Easy | Simple background buffers |
| Clock (Approximate LRU) | Near-LRU | Partial | Medium | OS page cache |
| TinyLFU (Caffeine) | Best | ✓ | Very hard | Production caches |

How to choose: Use LRU (LinkedHashMap or custom) for simple caches. Use Caffeine (W-TinyLFU) for production caches where hit rate matters. Use FIFO only for simplest cases. Never implement LFU from scratch without careful consideration of implementation complexity.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LRU always has the best hit rate | LFU often outperforms LRU for frequency-skewed workloads; TinyLFU (Caffeine) outperforms both |
| LinkedHashMap is automatically an LRU cache | Only if created with `accessOrder=true` AND `removeEldestEntry()` is overridden; default `LinkedHashMap` is insertion-ordered |
| Moving to front means O(N) re-sort | Moving a node to front in a doubly linked list is O(1) — just pointer manipulation |
| LRU protects against cache flooding | A sequential scan of N unique items empties the LRU cache of all hot data; TinyLFU resists this |
| LRU and TTL serve the same purpose | LRU evicts by recency (memory pressure); TTL evicts by age (staleness); most production caches need both |

### 🚨 Failure Modes & Diagnosis

**1. Cache pollution from linear scans**

Symptom: After a bulk data export or report query, cache hit rate drops from 80% to 20%; hot user-specific data is evicted.

Root Cause: A scan of N unique keys cycles through the entire LRU cache, evicting all hot user data. Scan data is never reused but temporarily dominant.

Diagnostic:
```bash
# Monitor cache stats over time:
cache.stats().hitRate() # Caffeine
# Sudden drop in hit rate after bulk operation
```

Fix: Use Caffeine (W-TinyLFU) which has a "window" LRU + admission filter. Or implement "scan-resistant" LRU by putting scan keys into a secondary cache or using a single read-through pass without caching.

Prevention: Separate bulk scan queries from the main cache; use a different cache instance for batch workloads.

---

**2. Thread safety violation with plain LRU**

Symptom: Wrong values returned or NullPointerException in concurrent access.

Root Cause: Custom `HashMap + LinkedList` LRU is not thread-safe; concurrent `get()` and `put()` corrupt the doubly linked list pointers.

Diagnostic:
```bash
jstack <pid> | grep "RUNNABLE" -A 30
# Multiple threads in LRU methods simultaneously
```

Fix: Use `Caffeine` or wrap `LinkedHashMap` with `Collections.synchronizedMap()` (for low concurrency) or use `ConcurrentLinkedHashMap` (Caffeine's core) for high concurrency.

Prevention: Never share a plain LRU cache across threads without synchronization.

---

**3. Memory leak from unbounded growth (capacity set too high)**

Symptom: Heap grows continuously; heap dump shows LRU cache holding millions of entries.

Root Cause: Capacity was set to an unrealistic value; in practice, far more unique keys exist than anticipated.

Diagnostic:
```bash
jmap -histo:live <pid> | grep "Node\|Cache"
# Count LRU nodes vs expected capacity
```

Fix: Set capacity based on available heap × acceptable cache fraction. Monitor `cache.estimatedSize()` vs capacity.

Prevention: Set cache size as a fraction of available heap (e.g., 10%); use `Caffeine.maximumWeight()` for memory-bounded caches.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HashMap` — O(1) key lookup is required; the LRU's HashMap provides this.
- `LinkedList` — a doubly linked list provides O(1) move-to-front and evict-from-tail.
- `Queue / Deque` — LRU can be viewed as a queue where access moves items to the front.

**Builds On This (learn these next):**
- `LFU Cache` — evicts by frequency instead of recency; harder to implement in O(1).
- `OS Page Cache` — the OS uses a variant of LRU (Clock algorithm) for page frame management.

**Alternatives / Comparisons:**
- `LFU Cache` — better hit rate for frequency-skewed workloads but O(log N) or complex O(1).
- `TTL Cache` — evicts by age, not recency; useful for stale data prevention.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fixed-capacity cache evicting the item    │
│              │ unused longest; O(1) get/put              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Random or FIFO eviction wastes the cache  │
│ SOLVES       │ — keeps cold data, evicts hot data        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ HashMap for O(1) find + doubly linked     │
│              │ list for O(1) reorder = O(1) total        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Caching with temporal locality (web,      │
│              │ DB query results, user sessions)          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Workload has scans (use TinyLFU) or       │
│              │ frequency matters more than recency (LFU) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ High hit rate for temporal workloads vs   │
│              │ 2× memory per entry + no scan resistance  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The book at the back of your desk is     │
│              │  the first to be put away"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LFU Cache → OS Page Cache → Caffeine      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** An LRU cache of capacity 1,000 is used to cache database query results. Traffic shows that 100 queries account for 90% of requests ("hot queries") and 900 queries each account for 0.01% of requests. After deploying the cache, the hit rate is only 55% instead of the expected 90%. Trace through exactly why this happens given the workload distribution and cache capacity, and propose what change to the cache design would raise the hit rate to ~90%.

**Q2.** The OS uses the Clock algorithm (second-chance page replacement) as an approximation of LRU for page frames. Unlike true LRU, the Clock algorithm doesn't move recently-accessed pages to the front — it simply marks them and gives them a "second chance" before eviction. What is the time complexity of true LRU page replacement in an OS context (why O(1) per access is not sufficient), and what specific constraint of OS page fault handling makes the Clock algorithm's O(1) overhead critical even if it sacrifices some optimality?

