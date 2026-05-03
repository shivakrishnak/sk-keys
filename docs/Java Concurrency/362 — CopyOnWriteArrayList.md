---
layout: default
title: "CopyOnWriteArrayList"
parent: "Java Concurrency"
nav_order: 362
permalink: /java-concurrency/copyonwritearraylist/
number: "0362"
category: Java Concurrency
difficulty: ★★★
depends_on: ArrayList, Thread Safety, Volatile, Immutable Collections
used_by: Event Listeners, Observer Pattern, Read-Heavy Shared Lists
related: ConcurrentHashMap, ArrayList, Collections.synchronizedList, Immutable Collections
tags:
  - concurrency
  - list
  - thread-safe
  - java
  - advanced
  - copy-on-write
---

# 362 — CopyOnWriteArrayList

⚡ TL;DR — CopyOnWriteArrayList replaces the entire backing array on every write, giving lock-free reads and consistent snapshots at the cost of expensive, memory-intensive writes.

| #0362           | Category: Java Concurrency                                                        | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | ArrayList, Thread Safety, Volatile, Immutable Collections                         |                 |
| **Used by:**    | Event Listeners, Observer Pattern, Read-Heavy Shared Lists                        |                 |
| **Related:**    | ConcurrentHashMap, ArrayList, Collections.synchronizedList, Immutable Collections |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You manage a list of event listeners. Every event fires iterates all listeners. Occasionally (rarely) a new listener registers or an old one unregisters. Using `ArrayList` with `synchronized` blocks: every iteration acquires a lock — serializing all event processing. Using unsynchronized `ArrayList`: a `ConcurrentModificationException` crashes the system when a listener is added while another thread is iterating.

**THE BREAKING POINT:**
`ConcurrentModificationException` is thrown when the structural modification count (modCount) changes during iteration. It's a fast-fail mechanism, not a guarantee of detection — just enough to prevent silent data corruption. But wrapping ArrayList in synchronized blocks means all reads are serialized, eliminating parallelism entirely.

**THE INVENTION MOMENT:**
For lists dominated by reads with rare writes, Copy-On-Write gives a third option: every write creates a new copy of the entire array. All readers see a stable, immutable snapshot. No lock needed for reads. Writes are expensive (O(N) copy) but safe. Iterators never throw `ConcurrentModificationException` because they hold a reference to the old array snapshot, which never changes.

---

### 📘 Textbook Definition

**CopyOnWriteArrayList** is a thread-safe variant of `ArrayList` in `java.util.concurrent` where all mutative operations (`add`, `remove`, `set`) copy the underlying array. The internal array is declared `volatile`; writes are performed under a `ReentrantLock` by creating a new array copy, making the mutation, and replacing the volatile reference atomically. Reads and iterators access the array reference at the time they start — they see a stable snapshot and never encounter `ConcurrentModificationException`. The trade-off: read operations are O(1) with no locking; write operations are O(N) due to the full copy. Best suited for lists where iterations vastly outnumber modifications (e.g., listener registries, service directories).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CopyOnWriteArrayList gives every write its own new copy of the array, so readers always see a frozen snapshot and never block or crash.

**One analogy:**

> CopyOnWriteArrayList is like a library's reading room that uses a bulletin board. Reading notices: you walk up and read — no signing in, no waiting. Posting a new notice: the librarian takes the entire board to the back room, copies all notices onto a new board, pins the new notice, then swaps the new board into place. Readers in the reading room still see the old board (which never changes). Once the new board is up, new readers see the updated list.

**One insight:**
The "copy" in CopyOnWriteArrayList happens at write time, not read time. This is the opposite of traditional locking (where readers/writers contend at read time). The memory cost is high, but it makes iteration completely lock-free and immune to `ConcurrentModificationException` — the iterator holds a reference to the array that existed when iteration started.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Internal `volatile Object[] array` — volatile ensures visibility across threads.
2. All writes take a `ReentrantLock`, copy the array, modify the copy, publish via volatile write.
3. All reads (including iteration) snapshot the volatile reference at the moment of access — that snapshot is immutable.
4. Iterators hold the array reference at iterator creation; `ConcurrentModificationException` is NEVER thrown.
5. `size()`, `get(index)`, `contains()` — lock-free, read from current snapshot.

**DERIVED DESIGN:**

```
WRITE SEQUENCE (add):
  lock.lock();
  try {
    Object[] current = getArray();              // snapshot
    Object[] newArr = Arrays.copyOf(current,   // COPY
                       current.length + 1);
    newArr[current.length] = element;          // modify copy
    setArray(newArr); // volatile write: publish atomically
  } finally { lock.unlock(); }

READ SEQUENCE (iterator):
  Object[] snapshot = getArray(); // volatile read: take snapshot
  // snapshot is now immutable — no lock needed, ever
  // iteration over snapshot: no CME possible
  for (Object o : snapshot) process(o);
```

```
CONCURRENT SCENARIO:
Time ──────────────────────────────────────────────────►

Thread R1: [reading snapshot v1] ─────────────────────►
Thread R2:         [reading snapshot v1] ──────────────►
Thread W:              [writes: copies → v2] ──► v2 live
Thread R3:                             [reading snapshot v2]

R1 and R2 see list without new element (their snapshot is v1)
R3 sees list WITH new element (snapshot v2)
No thread blocks any other thread.
```

**THE TRADE-OFFS:**

- **Gain:** Zero-contention reads; no `ConcurrentModificationException`; iterators hold consistent snapshots.
- **Cost:** Every write copies the entire array — O(N) time and space. High GC pressure from array allocation. Memory usage doubles briefly on every write. NOT suitable for write-heavy lists.

---

### 🧪 Thought Experiment

**SETUP:**
A Spring application has 200 beans that register as `ApplicationListener<E>`. On each application event (fired ~10,000 times/second), all 200 listeners are iterated. A listener is added or removed maybe twice per hour.

**WITHOUT CopyOnWriteArrayList:**
Using `synchronized(listeners)` around the iteration: all 200 listeners are called while holding a lock. If any listener takes 1ms, the lock is held for 200ms total. At 10,000 events/second, throughput is limited to 5 events/second — 2,000× slowdown.

**WITH CopyOnWriteArrayList:**
Iterating the listener list is lock-free. All 10 event-dispatch threads iterate simultaneously without any contention. Adding/removing a listener: O(200) array copy every 30 minutes — negligible overhead. The listener-dispatch hotpath has zero locking.

**THE INSIGHT:**
CopyOnWriteArrayList's value is that the expensive operation (copy) happens off the hot path (rare writes), and the cheap operation (read/iterate) happens on the hot path (frequent events). This is the ideal case for copy-on-write semantics: the cost is amortized away from where it matters most.

---

### 🧠 Mental Model / Analogy

> CopyOnWriteArrayList is like a software release: every time a developer commits a change (write), they branch the entire codebase, apply the change to the branch, and swap the "current release" pointer to the new branch. All users running the current release (readers) use the old snapshot indefinitely — nothing breaks mid-run. Future users see the new version. The cost (full codebase copy per commit) is only acceptable because commits are rare relative to the number of running users.

- "Running users" → iterator threads reading snapshot
- "Full codebase copy" → `Arrays.copyOf(current, newLength)` on write
- "Swap current release pointer" → `setArray(newArray)` volatile write
- "Old snapshot still valid for running users" → iterator holds old array reference
- "Commits are rare" → write operations are infrequent

Where this analogy breaks down: in software, old snapshots are eventually garbage-collected when no users remain. With CopyOnWriteArrayList, the old array is GC'd as soon as no thread holds a reference — typically as soon as all active iterators complete.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CopyOnWriteArrayList is a thread-safe list where adding or removing items makes a fresh copy of the entire list. Readers always see a consistent picture and never crash, but writing is slow (copies everything).

**Level 2 — How to use it (junior developer):**
Use when: many threads read/iterate the list; few threads write to it. Example: event listeners, plugin registries. Create with `new CopyOnWriteArrayList<>()`. Use like any list — the thread safety is transparent. Be aware that `iterator()` returns a snapshot — changes after `iterator()` is called are NOT visible to that iterator. Do NOT use for lists that are frequently modified.

**Level 3 — How it works (mid-level engineer):**
Internally: `volatile transient Object[] array`. Writes acquire `lock` (ReentrantLock), call `Arrays.copyOf` to create a larger array, insert/modify the element, then `setArray(newArray)` (a `volatile` write). The volatile write ensures all reader threads see the new array immediately without a memory barrier on their side (Java Memory Model: volatile write happens-before any subsequent volatile read). Readers call `getArray()` (a volatile read) once and then iterate the returned reference — which can never change, so iteration never needs re-checking or locking.

**Level 4 — Why it was designed this way (senior/staff):**
The copy-on-write approach leverages immutability as a concurrency primitive: immutable data needs no synchronization. By making each "version" of the array immutable (once published, never modified), CopyOnWriteArrayList achieves lock-free reads. The volatile reference is the single point of synchronization between writer and all future readers — this is the "publication idiom" from the Java Memory Model. The design is correct even in the presence of CPU instruction reordering and cache invalidation because the JMM guarantees that a volatile write is visible to all subsequent volatile reads. This is the same principle behind immutable-object-based concurrent systems (Akka, Clojure persistent data structures).

---

### ⚙️ How It Works (Mechanism)

```java
// Simplified CopyOnWriteArrayList internals:
public class CopyOnWriteArrayList<E> {
    private transient volatile Object[] array;
    final transient ReentrantLock lock = new ReentrantLock();

    public boolean add(E e) {
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();          // read current
            int len = elements.length;
            Object[] newElements =
                Arrays.copyOf(elements, len + 1);   // COPY
            newElements[len] = e;                   // modify copy
            setArray(newElements);                  // volatile write
            return true;
        } finally {
            lock.unlock();
        }
    }

    // READ: no lock, just volatile read + index access
    public E get(int index) {
        return elementAt(getArray(), index);        // volatile read
    }

    // ITERATOR: holds snapshot from creation time
    public Iterator<E> iterator() {
        return new COWIterator<E>(getArray(), 0);   // snapshot
    }
    // COWIterator.next() iterates snapshot array
    // Cannot call remove() — throws UnsupportedOperationException
}
```

```
MEMORY LAYOUT:
Before add("D"):
  volatile ref → [A, B, C]

add("D") executes:
  copy → [A, B, C, _]
  modify → [A, B, C, D]
  volatile write → ref now points to [A, B, C, D]
  old [A, B, C] eligible for GC (if no iterators hold it)

After add("D"):
  volatile ref → [A, B, C, D]
  Any iterator created before add("D") still sees [A, B, C]
  Any iterator created after add("D") sees [A, B, C, D]
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (Spring event listeners):
ApplicationEvent fired → EventMulticaster iterates listeners
→ COWArrayList.iterator() [snapshot of array v42]
→ [CopyOnWriteArrayList ← YOU ARE HERE]
→ Lock-free iteration over snapshot array
→ Each listener.onApplicationEvent() called
→ Concurrent bean registers new listener
→ add() executes: copy array v42 → v43, insert, volatile write
→ Existing iterators unaffected (still on v42)
→ Next event dispatch: gets snapshot v43 → sees new listener

FAILURE PATH:
Frequent writes to large CopyOnWriteArrayList:
→ Each write: Arrays.copyOf(list, N) = N object copies
→ GC sees N allocations per write
→ Young gen fills rapidly → more frequent Minor GC
→ Observable: GC logs show allocation rate spike on writes
→ Fix: replace with ConcurrentHashMap<K, List<V>> or
       use read-write lock (ReadWriteLock) instead

WHAT CHANGES AT SCALE:
With 10,000 elements, each write copies 10,000 references
(~80KB per copy on 64-bit JVM). At 100 writes/second,
that's 8 MB/sec of array allocation going to GC.
At 1000 writes/second on large lists, GC pressure becomes
the bottleneck. Prefer ConcurrentHashMap or ReadWriteLock.
```

---

### 💻 Code Example

```java
import java.util.concurrent.*;

// Example 1 — Event listener registry (ideal use case)
CopyOnWriteArrayList<EventListener> listeners =
    new CopyOnWriteArrayList<>();

// Registration (rare): safe from any thread
void registerListener(EventListener l) {
    listeners.add(l); // O(N) copy — but rare
}

// Dispatch (frequent): lock-free iteration
void dispatchEvent(Event e) {
    for (EventListener l : listeners) { // snapshot, no lock
        l.onEvent(e); // safe even if list is modified
    }
}

// Example 2 — WRONG: using COWAL for write-heavy list
// BAD: 1000 ops/sec, each copies a 500-element list
CopyOnWriteArrayList<LogEntry> logs = new CopyOnWriteArrayList<>();
// If you call logs.add() 1000/sec → 500,000 object copies/sec!

// Example 2 — GOOD: use ConcurrentLinkedQueue instead
Queue<LogEntry> logs = new ConcurrentLinkedQueue<>();

// Example 3 — Iterator is a snapshot (expected behaviour)
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("a"); list.add("b"); list.add("c");

Iterator<String> it = list.iterator(); // snapshot: [a, b, c]
list.add("d");                         // modifies list to [a, b, c, d]
// Iteration still sees [a, b, c] — NOT [a, b, c, d]
while (it.hasNext()) {
    System.out.println(it.next()); // prints: a, b, c
}
// This is correct and intentional — not a bug

// Example 4 — Iterator doesn't support remove
// BAD
Iterator<String> iter = list.iterator();
iter.remove(); // throws UnsupportedOperationException

// GOOD: use removeIf (takes a write lock internally)
list.removeIf(s -> s.equals("a")); // atomic removal
```

---

### ⚖️ Comparison Table

| List                         | Read Speed          | Write Speed           | ConcurrentModException      | Memory | Best For                      |
| ---------------------------- | ------------------- | --------------------- | --------------------------- | ------ | ----------------------------- |
| ArrayList (sync'd)           | Serialized          | Serialized            | No                          | Low    | Simple single-threaded use    |
| **CopyOnWriteArrayList**     | Very fast (no lock) | Very slow (O(N) copy) | Never                       | High   | Read-dominated listener lists |
| Collections.synchronizedList | Serialized          | Serialized            | Possible without sync block | Low    | Simple wrapping               |
| ConcurrentLinkedQueue        | Fast                | Fast                  | N/A                         | Medium | High-throughput queues        |

**How to choose:** Use CopyOnWriteArrayList only when reads vastly outnumber writes AND the list is small (< ~1000 elements). For write-heavy lists, use `ReadWriteLock`-protected `ArrayList` or `ConcurrentLinkedQueue`. For maps, use `ConcurrentHashMap`.

---

### ⚠️ Common Misconceptions

| Misconception                                                                   | Reality                                                                                                                                                                                  |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CopyOnWriteArrayList is always a drop-in replacement for synchronized ArrayList | It only outperforms synchronized access when reads are much more frequent than writes. For balanced or write-heavy access, it is dramatically slower and generates excessive GC pressure |
| Iterating CopyOnWriteArrayList sees up-to-date data                             | Iterator uses a snapshot from creation time. Mutations after iterator() is called are NOT visible. This is by design — but it means iterating and expecting live data is incorrect       |
| CopyOnWriteArrayList's iterator supports remove()                               | It does NOT. Iterator.remove() throws UnsupportedOperationException. Use list.removeIf() or list.remove(index) instead                                                                   |
| Writing to CopyOnWriteArrayList is thread-safe without locks                    | The internal writes DO use a ReentrantLock. Multiple concurrent writers are serialized. Only reads are lock-free. The copy-on-write gives readers zero-lock access, not writers          |

---

### 🚨 Failure Modes & Diagnosis

**GC Pressure from Frequent Writes**

**Symptom:** Young gen GC frequency increases; application pauses increase; GC logs show high allocation rate in threads that write to the list.

**Root Cause:** Each `add()` call allocates a new array of size N+1. At high write frequency on large lists, this generates megabytes per second of garbage.

**Diagnostic Command:**

```bash
# Monitor allocation rate:
jstat -gcutil <pid> 500 20
# Watch: YGCT (Young GC time) rising rapidly

# Find high-allocation threads:
jmap -histo:live <pid> | grep -E "Object\[\]|String"
# Large count of Object[] arrays suggests COW thrashing
```

**Fix:** Replace with `ArrayList` protected by `ReadWriteLock`, or `CopyOnWriteArrayList` only if writes are truly rare.

**Prevention:** Benchmark: if writes > 1% of operations, profile before committing to CopyOnWriteArrayList.

---

**Stale Iterator Data Causing Logic Errors**

**Symptom:** Processing loop misses recently added items or processes already-removed items.

**Root Cause:** Iterator snapshot taken before modifications; iteration sees stale state.

**Diagnostic Command:**

```java
// Instrument with size check:
int sizeBefore = list.size();
Iterator<T> it = list.iterator();
// ... process ...
if (list.size() != sizeBefore) {
    log.warn("List modified during iteration — may have stale view");
}
```

**Fix:** Accept the snapshot semantics (CopyOnWriteArrayList design), or switch to a list type where you need live iteration.

**Prevention:** Document that iterator gives a snapshot. Don't use CopyOnWriteArrayList where live iteration is required.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ArrayList` — the non-thread-safe list CopyOnWriteArrayList replaces
- `Volatile` — the JMM primitive used to publish new array references
- `Immutable Collections` — the principle that immutable data needs no synchronization

**Builds On This (learn these next):**

- `ReadWriteLock` — alternative for read-heavy write-rare lists where list size is large
- `Persistent Data Structures` — the general principle of copy-on-write in functional programming
- `Reactive Streams` — lock-free data flow pipelines as an alternative to shared mutable lists

**Alternatives / Comparisons:**

- `Collections.synchronizedList` — simpler but serialized; no snapshot iterators
- `ConcurrentLinkedQueue` — fast concurrent queue (not list); no indexed access
- `ReadWriteLock + ArrayList` — more flexible than CopyOnWriteArrayList for large, rarely-written lists

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe list: each write copies the   │
│              │ entire array; readers see frozen snapshot │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Frequent iteration of rarely-changed      │
│ SOLVES       │ lists without locking or CME crashes      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Iterator holds OLD array snapshot; it     │
│              │ never sees concurrent adds/removes        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Reads >> writes; small list (<1000 items);│
│              │ event listeners; service registries       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy: each write is O(N) copy →   │
│              │ GC thrashing; large lists (>10K elements) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock-free reads vs O(N) write cost        │
│              │ and high transient memory usage           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A library bulletin board: free to read,  │
│              │  full reprint required for every update"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ReadWriteLock → Persistent Data Structures│
│              │ → Immutable Collections                   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** CopyOnWriteArrayList serializes writes via a ReentrantLock. If two threads simultaneously call `add()` on the same list, they are serialized at the lock: one waits for the other's array copy to complete. Now consider 100 threads each simultaneously calling `add()` once. Calculate the total wall-clock time for all adds to complete if the list starts at 10,000 elements and each `Arrays.copyOf` takes 1 microsecond per element — and explain why this is qualitatively different from the same 100 adds on a `synchronized(ArrayList)`.

**Q2.** CopyOnWriteArrayList's iterator holds a reference to the array at the time `iterator()` is called. The iterator cannot see subsequent mutations. Now consider a listener dispatch loop using CopyOnWriteArrayList where a listener's `onEvent()` method adds a new listener to the same list. Trace exactly what happens to the new listener: does it receive the current event? The next event? What if the loop is using a `for-each` vs a manual `Iterator`?
