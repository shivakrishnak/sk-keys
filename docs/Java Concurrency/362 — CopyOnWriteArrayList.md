---
layout: default
title: "CopyOnWriteArrayList"
parent: "Java Concurrency"
nav_order: 362
permalink: /java-concurrency/copyonwritearraylist/
number: "362"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, Race Condition, ArrayList, volatile
used_by: Event Listeners, Observer Pattern, Read-Heavy Lists
tags: #java, #concurrency, #collections, #copy-on-write, #read-heavy
---

# 362 — CopyOnWriteArrayList

`#java` `#concurrency` `#collections` `#copy-on-write` `#read-heavy`

⚡ TL;DR — CopyOnWriteArrayList is a thread-safe List where every write (add, remove, set) creates a full copy of the underlying array — reads are lock-free and never throw ConcurrentModificationException, making it ideal for rarely-written, frequently-read lists.

| #362 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, Race Condition, ArrayList, volatile | |
| **Used by:** | Event Listeners, Observer Pattern, Read-Heavy Lists | |

---

### 📘 Textbook Definition

`java.util.concurrent.CopyOnWriteArrayList<E>` is a thread-safe variant of `ArrayList` that implements **copy-on-write** semantics. All mutative operations (`add`, `remove`, `set`) acquire an exclusive lock, create a fresh copy of the underlying array, write the modification to the copy, and atomically publish the new array via a `volatile` reference. Readers access the current array snapshot directly, with no locking. Iterators operate on the array snapshot at the time the iterator was created — they reflect the list state at that moment and never throw `ConcurrentModificationException`.

---

### 🟢 Simple Definition (Easy)

Every time you add or remove from a `CopyOnWriteArrayList`, it makes a complete copy of the internal array, modifies the copy, and swaps it in. Readers always see a stable, consistent snapshot — no ConcurrentModificationException, no locks needed for reads.

---

### 🔵 Simple Definition (Elaborated)

`ArrayList` throws `ConcurrentModificationException` if iterated while another thread modifies it. `Collections.synchronizedList` locks the entire list for every read and write. `CopyOnWriteArrayList` takes a different approach: writes are expensive (full copy) but reads are completely free. This trade-off pays off when reads vastly outnumber writes — for example, a list of event listeners registered at startup and iterated thousands of times per second.

---

### 🔩 First Principles Explanation

```
ArrayList concurrent problem:
  Thread A: iterates list (reads element[2])
  Thread B: adds element  (resizes the array)
  Thread A: next iteration → modCount changed → ConcurrentModificationException

CopyOnWriteArrayList solution — write creates snapshot:
  volatile Object[] array;  // current array — published atomically

  add(element):
    lock.lock()
    try {
      Object[] snapshot = array;  // read current
      Object[] newArray = Arrays.copyOf(snapshot, snapshot.length + 1);
      newArray[snapshot.length] = element;
      array = newArray;           // atomic volatile write
    } finally { lock.unlock() }

  get(index):
    return array[index];          // volatile read — no lock
    // reads the most recently published array atomically including all its contents

  iterator():
    Object[] snap = array;        // take snapshot NOW
    return new COWIterator(snap); // iterates over THAT snapshot
    // no ConcurrentModificationException — snap never changes
    // may not reflect writes that happen after iterator creation
```

---

### 🧠 Mental Model / Analogy

> A notice board with announcements (the list). Every time someone posts a new notice (write), they reprint the ENTIRE board and pin up the fresh copy. Readers (iterators) take a photo of the current board and read from their photo — modifications to the board don't affect photos already taken. No two people fight over the board for reading.

---

### ⚙️ How It Works

```
Write operations (synchronized):
  lock acquired → copy array → modify copy → volatile-publish new array → unlock
  Cost: O(n) per write — copy entire array

Read operations (lock-free):
  volatile read of array reference → direct array access
  Cost: O(1) — standard array access, no sync

Iterator:
  Snapshot of array at iterator creation time
  Iterator reads are safe even if list is modified concurrently
  Iterator does NOT reflect changes after creation
  Iterator.remove() throws UnsupportedOperationException

Memory:
  Each write creates an entirely new array in heap
  Old array GC'd when no longer referenced
  High write frequency → many short-lived arrays → GC pressure
```

---

### 🔄 How It Connects

```
CopyOnWriteArrayList
  ├─ Read-heavy ──→ observers, listeners, config snapshots
  ├─ vs ArrayList → COW is thread-safe; ArrayList is not (ConcurrentModificationException)
  ├─ vs synchronizedList → COW allows concurrent reads; synced blocks ALL for reads too
  ├─ vs ConcurrentHashMap → both copy-on-write for different collection types
  └─ Companion: CopyOnWriteArraySet → backed by COW list (uses contains() for uniqueness)
```

---

### 💻 Code Example

```java
// Thread-safe listener registry
CopyOnWriteArrayList<EventListener> listeners = new CopyOnWriteArrayList<>();

// At startup: register listeners (rare writes)
listeners.add(new LoggingListener());
listeners.add(new AuditListener());

// Per-event: fire all listeners (frequent reads)
for (EventListener l : listeners) {  // iterates a snapshot — always safe
    l.onEvent(event);
    // Even if another thread calls listeners.add() during iteration:
    // this iterator still sees the original list — no exception
}
```

```java
// Concurrent add and iterate
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
ExecutorService pool = Executors.newFixedThreadPool(4);

// Writer adds items slowly
pool.submit(() -> {
    for (int i = 0; i < 1000; i++) {
        list.add("item-" + i);
        Thread.sleep(1);
    }
});

// Readers iterate continuously — NEVER throw ConcurrentModificationException
for (int i = 0; i < 3; i++) {
    pool.submit(() -> {
        while (true) {
            for (String s : list) { process(s); } // snapshot-based, always safe
        }
    });
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Iterating COW always sees latest data | Iterator sees a SNAPSHOT as of creation time — writes after that are NOT visible to iterator |
| COW is suitable for frequent writes | O(n) copy per write → expensive for large or frequently-modified lists |
| `iterator.remove()` works on COW | Not supported — throws `UnsupportedOperationException` |
| COW eliminates all synchronization | Only reads are unsynchronized; writes still use a lock (exclusive) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using COW for a large, frequently-modified list**

```java
// ❌ COW list with 10,000 elements, 1000 writes/sec → 10MB of copying/sec
CopyOnWriteArrayList<Order> orders = new CopyOnWriteArrayList<>();
// Every order addition copies 10,000 elements → massive GC pressure

// Fix: use ConcurrentLinkedQueue or synchronizedList for write-heavy data
Queue<Order> orders = new ConcurrentLinkedQueue<>();
```

**Pitfall 2: Expecting iterator to reflect concurrent adds**

```java
Iterator<String> it = list.iterator(); // snapshot taken HERE
list.add("new-item");
while (it.hasNext()) {
    System.out.println(it.next()); // "new-item" NOT visible — old snapshot
}
// Fine if snapshot consistency is acceptable; bug if you need up-to-date view
```

---

### 🔗 Related Keywords

- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — analogous thread-safe map
- **[Race Condition](./072 — Race Condition.md)** — COW eliminates read-side races
- **[volatile](./070 — volatile.md)** — COW uses volatile array reference for visibility
- **[Producer-Consumer Pattern](./086 — Producer-Consumer Pattern.md)** — COW is NOT for P/C (use BlockingQueue)
- **ArrayList** — unsafe predecessor; use COW for shared lists with rare writes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Writes copy the array; reads are free;        │
│              │ iterators never throw CME — snapshot-based    │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Rarely-modified list read by many threads:    │
│              │ event listeners, observers, config snapshots  │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Frequent writes or large lists → O(n) copy    │
│              │ per write causes GC and latency spikes        │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Reads are free; writes pay with a full copy" │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentHashMap → ConcurrentLinkedQueue →   │
│              │ BlockingQueue → Read-Write Lock               │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `CopyOnWriteArrayList` iterators reflect the snapshot at creation time. Is this behaviour a bug or a feature? Give a use case where stale reads are acceptable and one where they are a problem.

**Q2.** The copy-on-write strategy trades write cost for read freedom. What is the memory complexity of COW during a write — in terms of the list's current size? What happens under heavy concurrent writes (say, 100 writes/second on a 100,000-element list)?

**Q3.** Can you implement a thread-safe `Set` using `CopyOnWriteArrayList`? Java provides `CopyOnWriteArraySet` which does exactly this. What is its complexity for `contains()`, `add()`, and `remove()`? When should you prefer it over `Collections.newSetFromMap(new ConcurrentHashMap<>())`?

