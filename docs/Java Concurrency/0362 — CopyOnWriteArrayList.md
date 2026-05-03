---
layout: default
title: "CopyOnWriteArrayList"
parent: "Java Concurrency"
nav_order: 362
permalink: /java-concurrency/copyonwritearraylist/
number: "0362"
category: Java Concurrency
difficulty: ★★★
depends_on: ArrayList, Thread Safety, Immutability, ReentrantLock
used_by: Event Listener Registration, Read-Heavy Concurrent Lists
related: ConcurrentHashMap, Collections.synchronizedList, ArrayList
tags:
  - java
  - concurrency
  - deep-dive
  - data-structures
  - read-heavy
---

# 0362 — CopyOnWriteArrayList

⚡ TL;DR — `CopyOnWriteArrayList` is a thread-safe `ArrayList` where every write (add/remove/set) creates a full copy of the underlying array — making reads completely lock-free and ConcurrentModificationException-free, at the cost of O(n) write operations. Use it only when reads vastly outnumber writes.

| #0362           | Category: Java Concurrency                                 | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | ArrayList, Thread Safety, Immutability, ReentrantLock      |                 |
| **Used by:**    | Event Listener Registration, Read-Heavy Concurrent Lists   |                 |
| **Related:**    | ConcurrentHashMap, Collections.synchronizedList, ArrayList |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A plugin system maintains a list of registered event listeners. The list is read thousands of times per second (every event dispatched). Listeners are rarely added or removed (maybe once per minute). Using `ArrayList + synchronized(list)`: every single event dispatch must acquire and release a lock. At 10,000 events/second, the lock becomes a bottleneck. 10,000 threads/second are serialised through one lock — even though they're all just reading and never conflicting with each other.

**THE BREAKING POINT:**
For a list that is read 10,000x for every 1 write, the `synchronized` list model pays the full cost of locking on 99.99% of operations that have no actual conflict. Additionally, iterating a `synchronized` list while another thread modifies it throws `ConcurrentModificationException` — forcing you to either lock for the entire iteration duration (holding the lock while dispatching to every listener, which is a long time to hold a lock) or copy the list before iterating.

**THE INVENTION MOMENT:**
`CopyOnWriteArrayList` was introduced in Java 5 to handle precisely this pattern: read-heavy, write-rare, concurrent lists. The "copy on write" strategy: every write creates a new backing array, replacing the reference atomically. Active readers see the old snapshot — they never conflict with writers. Readers need zero locks.

---

### 📘 Textbook Definition

**CopyOnWriteArrayList:** A thread-safe variant of `ArrayList` (`java.util.concurrent.CopyOnWriteArrayList`) in which all mutative operations (add, set, remove, etc.) are implemented by making a fresh copy of the underlying array. This provides thread safety for reads and iterations at the cost of O(n) write operations. Iterators return a snapshot of the array as of the time the iterator was created — they do NOT reflect subsequent modifications and never throw `ConcurrentModificationException`.

**Snapshot iterator:** An iterator that operates on a fixed array copy captured at the time of `iterator()` creation. Modifications to the list after the iterator was created are not visible through the iterator. The iterator is read-only (modification methods like `iterator.remove()` throw `UnsupportedOperationException`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CopyOnWriteArrayList is a thread-safe list where writes make a full copy of the array so reads never need locks and iterators never throw ConcurrentModificationException.

**One analogy:**

> A restaurant's daily menu is updated overnight (write) but read by hundreds of customers all day (read). The chef doesn't lock every customer out while updating the menu — they write a completely new printed menu board (full array copy) and swap it out between customers. Customers reading the old menu aren't interrupted. The next customer gets the new menu. No customer ever sees a half-updated menu.

**One insight:**
The fundamental trade-off is temporal isolation via immutability: a writer creates an entirely new array, making the write O(n), so that every reader can work with a logically immutable snapshot. This is the opposite trade-off from `Collections.synchronizedList` (O(1) writes, O(1) reads, but serialised). The correct question is: what is your read:write ratio? If it's 1000:1, CopyOnWriteArrayList wins despite its O(n) writes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The internal `array` field is declared `volatile` — writes are atomically visible to readers.
2. Every mutative operation acquires a `ReentrantLock`, creates a new array copy, modifies it, then atomically publishes it by setting `array = newArray`.
3. `getArray()` returns the current array reference — a simple volatile read. No lock.
4. Iterators capture `getArray()` at construction time — they hold a reference to the snapshot, not the live array.
5. The lock is only held by writers (one writer at a time). Readers never acquire any lock.

**INTERNAL MECHANISM:**

```java
// Simplified mental model of CopyOnWriteArrayList:
class CopyOnWriteArrayList<E> {
    private volatile Object[] array;  // THE LIVE ARRAY
    final ReentrantLock lock = new ReentrantLock();

    public E get(int index) {
        return (E) getArray()[index];  // PURE VOLATILE READ — no lock
    }

    public boolean add(E e) {
        lock.lock();                   // ONE writer at a time
        try {
            Object[] elements = getArray();
            int len = elements.length;
            Object[] newElements = Arrays.copyOf(elements, len + 1); // FULL COPY
            newElements[len] = e;
            setArray(newElements);     // ATOMIC PUBLISH via volatile write
            return true;
        } finally {
            lock.unlock();
        }
    }

    public Iterator<E> iterator() {
        return new COWIterator<E>(getArray(), 0); // SNAPSHOT — current array
        // Future writes create a NEW array — this iterator keeps the old one
    }
}
```

**ITERATOR SNAPSHOT BEHAVIOUR:**

```
t=0: list = ["A", "B", "C"]   array reference = @REF1

t=1: Iterator it = list.iterator()
     it captures: snapshot = @REF1 (["A", "B", "C"])

t=2: list.add("D")             (writer)
     NEW array = ["A", "B", "C", "D"]   @REF2
     list.array = @REF2 (volatile write)
     @REF1 still valid — it holds the snapshot

t=3: it.next() → "A"           (reader, reads @REF1)
t=4: it.next() → "B"           (reader, reads @REF1)
     it will NEVER see "D" — it holds the old snapshot
     it will NEVER throw ConcurrentModificationException

t=5: new list.iterator()
     captures: snapshot = @REF2 (["A", "B", "C", "D"])
```

---

### 🧪 Thought Experiment

**SETUP:**
An event bus with 1,000 registered listeners. Events fire at 10,000/second. Listener registration/deregistration: 1/minute.

**READ:WRITE RATIO:** 10,000 reads × 1,000 listeners/event = 10,000,000 reads/minute. 1–2 writes/minute. Ratio: ~5,000,000:1 reads:writes.

**WITH `Collections.synchronizedList`:**

```
Every event dispatch: acquire lock, iterate all 1,000 listeners, release lock.
10,000 events/second → 10,000 lock acquisitions/second.
Lock held for entire iteration (must hold to prevent CME).
Duration per lock hold: time to dispatch to all 1,000 listeners.
Result: All events serialised through single lock. Throughput: 1x.
```

**WITH `CopyOnWriteArrayList`:**

```
Every event dispatch: volatile read of array pointer, iterate snapshot.
10,000 events/second → 10,000 volatile reads/second (no lock).
All event dispatches run CONCURRENTLY.
Result: All events dispatched in parallel. Throughput: Nx (N = cores).

1/minute write: lock, copy 1,000-element array, add, unlock.
Duration: ~1μs for array copy (1,000 object references = ~8KB).
Impact: essentially zero (1μs blocked per minute).
```

**THE INSIGHT:**
The O(n) write cost (copying 8KB of data once per minute) is absolutely trivial compared to the benefit of removing lock contention from 10,000,000 reads per minute.

---

### 🧠 Mental Model / Analogy

> CopyOnWriteArrayList is like a city's law book with a distributed read model. The city has one master copy of the laws (the live array). When a new law is passed (write), the clerk prints an entirely new law book from scratch (full array copy), and the new book becomes the official one. Every courtroom, library, and citizen already reading from their copy of the law book (snapshot iterators) continues reading their copy without interruption — they'll use the new book the next time they open a new one.

Explicit mapping:

- "law book" → the backing array
- "printing a new book from scratch" → `Arrays.copyOf()` in every write
- "the official law book" → the volatile `array` field
- "courtrooms reading their existing copy" → iterators holding a snapshot
- "ConcurrentModificationException" → a problem that doesn't exist because each reader has their own book

Where this analogy breaks down: courtrooms reading the OLD law book won't see new laws — this is intentional in COWAL but could be incorrect in your application if iterators must see the latest data. If readers MUST see the latest state, use `ConcurrentHashMap` or a `ReadWriteLock`.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CopyOnWriteArrayList is a thread-safe list where every modification (add, remove) creates a completely fresh copy of the list. This means reading from the list never needs any locking, and iterating is always safe even if the list is modified simultaneously.

**Level 2 — How to use it (junior developer):**
Use `new CopyOnWriteArrayList<>()` in place of `ArrayList` when the list will be read by multiple threads frequently but written to rarely. Iterate safely with a `for-each` loop — you'll get a snapshot, not a live view. Do NOT use for write-heavy scenarios (every add copies the whole array). Do NOT call `iterator.remove()` — snapshot iterators don't support mutation.

**Level 3 — How it works (mid-level engineer):**
The `array` field is `volatile`. Reads call `getArray()` — a volatile read returning the current reference. Writes acquire a `ReentrantLock`, copy the entire array, modify the copy, then call `setArray(newArray)` — a volatile write that atomically publishes the new reference. Readers that started reading the old array continue reading it safely (the old array is not modified — it's garbage collected after all readers drop their references). Iterators capture the array reference at construction time (`snapshot = getArray()`) and never call `getArray()` again.

**Level 4 — Why it was designed this way (senior/staff):**
The design elegance is the use of volatile for the array reference combined with the immutability-of-snapshots guarantee. A volatile write ensures that all subsequent volatile reads by other threads see the new array (Java Memory Model happens-before). Because the OLD array is NEVER modified after being published as a snapshot, readers never see torn state — the array is a consistent immutable snapshot from the moment it is published. This is a classic "publish-safe" pattern: create an object, fully initialise it, THEN publish a reference to it via volatile. Any thread reading the volatile reference sees the fully-initialised object. This pattern appears throughout the JDK (e.g., `String` fields, `FinalReference`). The O(n) write cost is the accepted trade-off for eliminating all read-side synchronisation. For write-heavy workloads, the correct alternatives are `Collections.synchronizedList` (simple serialisation) or a custom `ReadWriteLock` solution.

---

### ⚙️ How It Works (Mechanism)

```
CopyOnWriteArrayList STATE:

  volatile Object[] array  ← THE KEY: volatile reference, immutable content

CONCURRENT READ (zero locks):
  Thread reads array reference (volatile read → sees latest published array)
  Reads element at index (no contention — array not modified after publish)

CONCURRENT WRITE (one writer at a time):
  lock.lock()
  Object[] snapshot = array          // read current
  Object[] newArr = Arrays.copyOf(snapshot, newLen)  // FULL COPY
  newArr[...] = newValue             // modify copy
  array = newArr                     // ATOMIC PUBLISH (volatile write)
  lock.unlock()
  // Old snapshot: still valid for any reader that captured it
  // Will be GC'd when all such readers drop their reference

ITERATOR (permanent snapshot):
  Object[] snapshot = array          // volatile read at iterator creation
  // Iterate over snapshot — NEVER accesses array again
  // Future writes don't affect this iterator
  // iterator.remove() → UnsupportedOperationException
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();

[startup]: register 1,000 listeners (1,000 copies of array during startup)

[runtime - 10,000 events/second]:
  for (Listener l : listeners) {  ← takes snapshot; NO LOCK
    l.onEvent(event);             ← concurrent with writers and other iterators
  }

[rare]: listeners.add(newListener);  ← LOCK, copy 1001 elements, publish
[rare]: listeners.remove(old);       ← LOCK, copy 999 elements, publish

ITERATION SNAPSHOT:
  When event dispatch loop captures snapshot at t=0
  If listener added at t=1 mid-iteration:
    → the event dispatch loop does NOT see the new listener
    → the new listener fires from t=2 (next event dispatch cycle)
    → this is correct and expected behaviour
```

---

### 💻 Code Example

**Example 1 — Event listener registry:**

```java
import java.util.concurrent.CopyOnWriteArrayList;

public class EventBus {
    // Classic use case: read-heavy listener list
    private final CopyOnWriteArrayList<EventListener> listeners
        = new CopyOnWriteArrayList<>();

    // Called infrequently (plugin registration)
    public void register(EventListener listener) {
        listeners.add(listener);  // O(n) copy — but rare
    }

    // Called very frequently (every event — thousands per second)
    public void publish(Event event) {
        // for-each takes snapshot — lock-free, never throws CME
        for (EventListener listener : listeners) {
            try {
                listener.onEvent(event);
            } catch (Exception e) {
                log.error("Listener error", e);
                // Iteration continues — other listeners not affected
            }
        }
    }
}
```

**Example 2 — Correct iteration patterns:**

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>(
    Arrays.asList("A", "B", "C"));

// CORRECT: for-each (snapshot)
for (String s : list) {
    System.out.println(s);  // safe even if list modified concurrently
}

// CORRECT: indexed access (reads latest volatile array)
for (int i = 0; i < list.size(); i++) {
    String s = list.get(i);  // safe — volatile read each time
}

// WRONG: iterator.remove() — not supported
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (shouldRemove(it.next())) {
        it.remove();  // throws UnsupportedOperationException!
    }
}

// CORRECT: use removeIf (atomic under the write lock)
list.removeIf(s -> shouldRemove(s));
```

**Example 3 — Anti-pattern: write-heavy workload:**

```java
// WRONG for write-heavy:
CopyOnWriteArrayList<String> writeHeavy = new CopyOnWriteArrayList<>();
for (int i = 0; i < 100_000; i++) {
    writeHeavy.add(String.valueOf(i));  // 100,000 array copies!
    // Each add copies the ENTIRE array: O(1) + O(2) + ... + O(N) = O(N²) total
}

// CORRECT for write-heavy: ArrayList + synchronisation
List<String> better = Collections.synchronizedList(new ArrayList<>());
// OR: build with ArrayList, then wrap:
List<String> result = new ArrayList<>(100_000);
result.addAll(source);
List<String> concurrent = new CopyOnWriteArrayList<>(result); // one copy at end
```

---

### ⚖️ Comparison Table

| List                         | Thread-safe | Read performance | Write performance | Iterator safety                       |
| ---------------------------- | ----------- | ---------------- | ----------------- | ------------------------------------- |
| **CopyOnWriteArrayList**     | Yes         | O(1) lock-free   | O(n) (full copy)  | Snapshot, no CME                      |
| Collections.synchronizedList | Yes         | O(1) (locked)    | O(1) (locked)     | Throws CME (must lock externally)     |
| ArrayList                    | No          | O(1)             | O(1) amortised    | Throws CME on concurrent modification |
| LinkedList                   | No          | O(n)             | O(1) at pointer   | Throws CME                            |
| ConcurrentLinkedQueue        | Yes (queue) | O(n) for search  | O(1) lock-free    | Weakly consistent, no CME             |

How to choose: `CopyOnWriteArrayList` when reads >> writes and concurrent iteration safety matters (event systems, plugin registries). `Collections.synchronizedList` when write rate is moderate and you can tolerate locking during iteration. Plain `ArrayList` when single-threaded.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                  |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Iterating COWAL reflects live changes"                | Iterators see a snapshot at the time of iterator creation. Changes after that point are invisible to the iterator. This is intentional, not a bug.                                                       |
| "COWAL is always better than synchronizedList"         | Only when reads >> writes. For write-heavy workloads, COWAL's O(n) copy makes it far slower and memory-intensive.                                                                                        |
| "COWAL prevents out-of-bounds from concurrent removes" | Indexed access (`get(i)`) reads the current (not snapshot) array. If another thread removes an element between `size()` and `get(i)`, `get()` may return a stale index. Use for-each for safe iteration. |
| "COWAL is a good general-purpose concurrent list"      | No. It's a specialised optimisation for specific patterns (read-heavy, infrequent writes). Most concurrent list needs are better served by a different structure.                                        |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory/GC Pressure from Write-Heavy Workload**

**Symptom:** GC pauses increase. `java.lang.OutOfMemoryError: GC overhead limit exceeded`. Heap profiler shows many short-lived `Object[]` instances.

**Root Cause:** Code adds to a `CopyOnWriteArrayList` in a write-heavy loop. Each add allocates a new array of size N, copies N elements, then the old array becomes garbage. For a list of 100,000 elements, each add allocates and GCs 800KB.

**Diagnostic:**

```bash
# Enable GC logging
-Xlog:gc:file=gc.log:time,uptime
# Look for frequent short GC cycles with high allocation rate

# Heap profiler (async-profiler)
./profiler.sh -e alloc -d 10 -f flamegraph.html <pid>
# Look for Object[] allocations from CopyOnWriteArrayList.add()
```

**Fix:** Replace `CopyOnWriteArrayList` with `Collections.synchronizedList(new ArrayList<>())` or a `ReadWriteLock`-protected `ArrayList`. If writes are bursty (many writes, then many reads), accumulate writes in a local `ArrayList` and bulk-replace with `new CopyOnWriteArrayList<>(localList)`.

**Prevention:** Only use `CopyOnWriteArrayList` when write rate < 1% of read rate.

---

**2. Stale Data from Snapshot Iterators**

**Symptom:** Event listeners registered during the first 100ms of startup are not fired for events in the first 100ms. Newly added listeners miss events that fire before the snapshot is refreshed.

**Root Cause:** Expected behaviour of `CopyOnWriteArrayList`. Iterators capture a snapshot. Events published during the same event-dispatch loop that started BEFORE a new listener was added don't go to the new listener.

**Diagnostic:**

```java
// Add debug logging to detect snapshot age:
long snapshotTime = System.nanoTime();
for (Listener l : listeners) {
    long dispatchDelay = System.nanoTime() - snapshotTime;
    // If dispatchDelay >> event SLA, snapshots are stale
}
```

**Fix:** This is expected, not a bug. If you need real-time listener registration visibility, use `Collections.synchronizedList` + external synchronisation during iteration, or publish events through a message channel (queue) where new listeners pick up from a specific position.

**Prevention:** Document that `CopyOnWriteArrayList` iterators are snapshots. Design event-listener contracts to accept "may miss first event" semantics if registration is concurrent with dispatch.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ArrayList` — the base structure COWAL is built around
- `Thread Safety` — the problem COWAL solves for lists
- `Immutability` — the strategy COWAL uses for read safety
- `ReentrantLock` — the lock COWAL uses to serialise writers

**Builds On This (learn these next):**

- `ConcurrentHashMap` — similar philosophy applied to maps (different implementation: striped locking vs. copy-on-write)
- `Event-Driven Programming` — the primary use case for COWAL (listener registries)

**Alternatives / Comparisons:**

- `Collections.synchronizedList` — whole-list lock; O(1) writes; throws CME during concurrent iteration unless you lock externally
- `ArrayList` — fastest; single-threaded only
- `ConcurrentLinkedQueue` — lock-free queue; different semantics (FIFO, not random access)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe ArrayList: writes copy the    │
│              │ full array; reads and iteration lock-free │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Locking during iteration blocks all       │
│ SOLVES       │ concurrent readers in synchronizedList    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Iterators snapshot on creation — never    │
│              │ throw CME; never see concurrent writes    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Reads >> writes (1000:1+); event          │
│              │ listeners; plugin registries              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Frequent writes (each write = O(n) copy); │
│              │ very large lists with any write volume    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(n) writes + stale iterators vs.         │
│              │ lock-free reads + no ConcurrentModEx      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Print a new menu board for every change; │
│              │  readers keep reading their old copy."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentHashMap → Atomic Classes        │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A monitoring system uses a `CopyOnWriteArrayList<MetricCollector>` to store 50 metric collectors. Every 100ms, a timer thread iterates all 50 collectors and aggregates metrics. Metric collectors are added/removed dynamically as services start/stop (say, 5 changes per minute). One metric collector's `collect()` method sometimes takes 2 seconds (external HTTP call). Identify ALL the concurrency and performance problems in this design, and propose a correct, performant solution.

**Q2.** `CopyOnWriteArrayList` uses a single `ReentrantLock` to serialise writers. Suppose you redesign it to allow two concurrent writers by using two separate internal arrays (sharded) and merging on read. Describe all the correctness problems that would arise: what happens to iterator semantics, `size()` accuracy, and atomic compound operations like `addIfAbsent()`? Why is the single-writer model correct despite its serialisation constraint?
