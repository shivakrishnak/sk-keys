---
layout: default
title: "Java - Collections"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 2
permalink: /interview/java/collections/
topic: Java
subtopic: Collections
keywords:
  - ArrayList
  - HashMap
  - TreeMap
  - HashSet
  - Queue and Deque
  - Iterator and Iterable
difficulty_range: mixed
status: in-progress
version: 2
---

# ArrayList

**TL;DR** - ArrayList is a resizable array backed by `Object[]` that gives O(1) random access but O(n) insertion at arbitrary positions, and understanding its growth strategy prevents memory waste and performance cliffs.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You need a list of customer orders, but you don't know how many there will be. With plain arrays, you must declare the size upfront. When the array fills up, you manually create a bigger one, copy everything over, and update every reference. Every team does this differently - some double the size, some add 10 slots, some forget to copy and lose data.

**THE BREAKING POINT:**
A team uses a fixed array of 100 for user sessions. On launch day, user 101 crashes the server with an `ArrayIndexOutOfBoundsException`. The hotfix - a manual resize routine - introduces an off-by-one error that silently drops every 100th session.

**THE INVENTION MOMENT:**
"This is exactly why ArrayList was created."

**EVOLUTION:**
Java 1.0 shipped `Vector`, a synchronized resizable array. But synchronization on every operation was expensive when thread safety wasn't needed. Java 1.2 introduced the Collections Framework with `ArrayList` - same concept, no synchronization overhead. Java 10+ added `List.of()` and `List.copyOf()` for immutable lists.

---

### Textbook Definition

`ArrayList` is a resizable-array implementation of the `List` interface in `java.util`. It maintains an internal `Object[]` array that grows automatically when capacity is exceeded, using an amortized growth strategy (typically 1.5x in OpenJDK). It permits all elements including `null`, is not synchronized, and provides O(1) index-based access with O(n) worst-case insertion and deletion.

---

### Understand It in 30 Seconds

**One line:**
A list that grows itself when full and gives instant access by position.

**One analogy:**

> Think of a notebook with numbered pages. You can flip to any page instantly. When you fill the last page, someone hands you a bigger notebook and copies everything over - you never run out of pages.

**One insight:**
The key insight is amortized cost. Growing the array is expensive (copy everything), but because you grow by a multiplicative factor, each element's average cost of being copied across all resizes is constant. This is why `add()` at the end is documented as "amortized constant time."

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Elements are stored contiguously in memory (array-backed)
2. Index-based access is always O(1) - direct memory offset
3. Size can exceed initial capacity - growth is automatic
4. Insertion order is preserved exactly

**DERIVED DESIGN:**
Contiguous storage forces a trade-off: random access is instant (pointer + offset), but inserting in the middle requires shifting all subsequent elements. The growth strategy (1.5x in OpenJDK) balances memory waste against copy frequency.

**THE TRADE-OFFS:**
**Gain:** O(1) random access, cache-friendly iteration, simple index math
**Cost:** O(n) insert/delete in middle, wasted capacity after growth, no thread safety

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any contiguous-memory list must copy on resize and shift on mid-insertion - these costs are inherent to the data structure.
**Accidental:** Boxing overhead when storing primitives (solved by specialized lists in Eclipse Collections or Java Valhalla value types).

---

### Mental Model / Analogy

> Imagine a parking lot with numbered spots in a row. You can drive straight to spot 47 because you know exactly where it is. But if you want to squeeze a new car between spot 10 and 11, every car from 11 onward must shift down one spot.

- "Parking spots" -> array indices
- "Drive straight to spot 47" -> O(1) index access
- "Squeeze in and shift" -> O(n) mid-insertion
- "Build a bigger lot and move all cars" -> array resize/copy
- "Empty spots at the end" -> unused capacity

Where this analogy breaks down: Real parking lots don't automatically build bigger versions of themselves.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ArrayList is a list that grows automatically when you add items. You can access any item by its position number instantly. It's the most commonly used list in Java.

**Level 2 - How to use it (junior developer):**
Create with `new ArrayList<>()` or `List.of()` for immutable. Use `add()` to append, `get(i)` to read, `remove(i)` to delete. Always use generics: `ArrayList<String>`, never raw `ArrayList`. Pre-size with `new ArrayList<>(expectedSize)` when you know the approximate count. Iterate with enhanced for-loop or streams.

**Level 3 - How it works (mid-level engineer):**
Internally it's an `Object[] elementData` with a `size` counter. When `size == elementData.length`, `grow()` allocates `oldCapacity + (oldCapacity >> 1)` (1.5x). `System.arraycopy` moves elements. `get(i)` is a bounds check plus array index. `add(index, element)` calls `System.arraycopy` to shift elements right. `remove(index)` shifts elements left and nulls the vacated slot to avoid memory leaks. The `modCount` field tracks structural modifications for fail-fast iterator behavior.

**Level 4 - Mastery (senior/staff+ engineer):**
ArrayList's 1.5x growth factor is a compromise - 2x (used in some C++ vectors) wastes more memory but resizes less often. The default capacity of 10 was chosen in JDK 1.2 and is often too small for real workloads, wasting 3-4 resize cycles. Experts pre-size aggressively. `subList()` returns a view, not a copy - modifications to the sublist mutate the original, a common source of bugs. `trimToSize()` reclaims wasted capacity after bulk loading. For primitive-heavy workloads, `int[]` or Eclipse Collections' `IntArrayList` avoids boxing overhead entirely. In high-throughput systems, ArrayList's non-thread-safe design is actually an advantage - you avoid `Vector`'s lock overhead and add explicit synchronization only where needed.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
ArrayList internal structure:

  elementData (Object[]):
  +---+---+---+---+---+---+---+---+---+---+
  | A | B | C | D | E |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+---+---+
    0   1   2   3   4   5   6   7   8   9

  size = 5       capacity = 10

  add("F"):
    elementData[5] = "F"
    size = 6       // O(1)

  add(2, "X"):   // insert at index 2
    arraycopy(data, 2, data, 3, size-2) // shift
    elementData[2] = "X"
    size = 7       // O(n) due to shift
```

**Growth sequence (starting from default 10):**
10 -> 15 -> 22 -> 33 -> 49 -> 73 -> 109 -> ...

Each `grow()` call:

1. Calculate new capacity: `oldCap + (oldCap >> 1)`
2. Allocate new `Object[]` with new capacity
3. `System.arraycopy` old array to new array
4. Point `elementData` to new array (old array becomes garbage)

**Why 1.5x and not 2x?**
With 2x growth, previously freed arrays can never be reused for the new allocation (their combined size is always less than the new size). With 1.5x, after several resizes the old freed blocks can be coalesced and reused.

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
new ArrayList<>(4)
  -> allocate Object[4]
  -> add("A"), add("B"), add("C"), add("D")
     <- YOU ARE HERE: size == capacity
  -> add("E") triggers grow()
  -> new Object[6], arraycopy, elementData = new
  -> add continues: elementData[4] = "E"
```

**FAILURE PATH:**

```
ArrayList used from 2 threads without sync
  -> Thread A: add() triggers grow + arraycopy
  -> Thread B: add() writes to old array ref
  -> Result: lost update, null elements,
     ArrayIndexOutOfBoundsException
```

**WHAT CHANGES AT SCALE:**
With millions of elements, a single resize copies millions of references, causing a GC pause spike and a latency blip. Pre-sizing eliminates this. At extreme scale (100M+ elements), even ArrayList's overhead (24 bytes per element due to object headers + references) becomes significant versus primitive arrays.

---

### Code Example

**Example 1 - Common mistake: not pre-sizing**

```java
// BAD: 7 resize operations for 10000 elements
List<String> names = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    names.add("user-" + i);
}

// GOOD: zero resize operations
List<String> names = new ArrayList<>(10000);
for (int i = 0; i < 10000; i++) {
    names.add("user-" + i);
}
```

**Example 2 - ConcurrentModificationException trap**

```java
// BAD: modifying list during iteration
List<String> items = new ArrayList<>(
    List.of("a", "b", "c", "d")
);
for (String item : items) {
    if (item.equals("b")) {
        items.remove(item); // throws CME
    }
}

// GOOD: use removeIf or Iterator.remove()
items.removeIf(item -> item.equals("b"));

// OR with explicit iterator
Iterator<String> it = items.iterator();
while (it.hasNext()) {
    if (it.next().equals("b")) {
        it.remove(); // safe
    }
}
```

**How to test / verify correctness:**
Write a unit test that adds elements beyond initial capacity, verifies `size()` and `get(i)` after each add, and checks that `ConcurrentModificationException` is thrown when modifying during iteration.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. O(1) access by index, O(n) insert/remove in the middle - it's an array underneath
2. Pre-size when you know the count to avoid resize copying
3. Not thread-safe - use `Collections.synchronizedList()` or `CopyOnWriteArrayList` for concurrency

**Interview one-liner:**
"ArrayList is a resizable Object array with O(1) random access and amortized O(1) append, but O(n) mid-insertion because elements must be shifted. I always pre-size it when the count is predictable to avoid resize copies."

---

### The Surprising Truth

ArrayList's default initial capacity of 10 was set in Java 1.2 and has never changed, despite being a poor fit for most real-world workloads. Internal JDK profiling showed that most ArrayLists either hold 0-2 elements (wasting 8 slots) or grow well past 10 (triggering multiple resizes). Modern Java actually optimizes the zero-element case: `new ArrayList<>()` creates a shared empty array and defers allocation until the first `add()`.

---

### Interview Deep-Dive

**Q1: What is the internal data structure of ArrayList and how does it grow?**

_Why they ask:_ Tests whether you understand the mechanics beyond "it's a list."

**Answer:**
ArrayList wraps an `Object[] elementData` with a `size` field tracking actual element count. When `add()` is called and `size == elementData.length`, the `grow()` method allocates a new array with capacity `oldCapacity + (oldCapacity >> 1)` - roughly 1.5x. It then uses `System.arraycopy` to copy all elements to the new array.

The 1.5x growth factor is deliberate. With 2x growth (as in some C++ vectors), previously freed memory blocks can never be reused for the next allocation because their combined size is always less than the new array. With 1.5x, after a few resizes, old blocks can be coalesced and potentially reused by the allocator.

The default capacity is 10, but `new ArrayList<>()` actually starts with a shared empty array (`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`). Real allocation happens on the first `add()`. This is a memory optimization added in Java 8.

Key insight: the amortized cost of `add()` is O(1) because each element is copied at most O(log n) times across all resizes, and the total copy work across n additions is O(n).

---

**Q2: You're seeing GC pause spikes every few minutes in production. Heap dumps show large Object[] arrays being promoted to old gen. What's happening and how do you fix it?**

_Why they ask:_ Tests ability to connect ArrayList internals to production symptoms.

**Answer:**
This is classic ArrayList resize behavior. Here's the diagnosis:

1. **Symptom mapping:** Large `Object[]` in old gen = ArrayList resize. The old array becomes garbage, the new one is larger. If the list is long-lived, both arrays survive minor GC and get promoted.

2. **Diagnosis steps:**

   ```bash
   jmap -histo:live <pid> | grep "\[Ljava"
   # Look for Object[] count and total bytes
   ```

   Check if Object[] instances are disproportionately large. Then use a heap dump:

   ```bash
   jcmd <pid> GC.heap_dump /tmp/heap.hprof
   ```

   Open in Eclipse MAT, find largest `Object[]`, trace back to the owning ArrayList.

3. **Root cause:** Code is creating ArrayLists without pre-sizing, then adding thousands of elements. Each resize creates a new large array and discards the old one.

4. **Fix:**
   - Pre-size: `new ArrayList<>(expectedSize)`
   - For batch operations: `ensureCapacity(n)` before bulk adds
   - After bulk loading, call `trimToSize()` to release unused capacity
   - For very large lists, consider off-heap storage or streaming instead of materializing

Key insight: in throughput-sensitive systems, a single ArrayList resize that copies 1M references can cause a 10-50ms pause - not from GC, but from the `System.arraycopy` itself.

---

**Q3: What is the difference between ArrayList and LinkedList? When would you choose LinkedList?**

_Why they ask:_ Tests understanding of data structure trade-offs beyond textbook answers.

**Answer:**
The textbook answer is "ArrayList for random access, LinkedList for frequent insertion/deletion." The real answer is: **almost always use ArrayList.**

| Operation          | ArrayList      | LinkedList       |
| ------------------ | -------------- | ---------------- |
| `get(i)`           | O(1)           | O(n)             |
| `add(e)` at end    | O(1) amortized | O(1)             |
| `add(i, e)` middle | O(n)           | O(1)\*           |
| `remove(i)`        | O(n)           | O(1)\*           |
| Memory/element     | ~4 bytes (ref) | ~24 bytes (node) |
| Cache locality     | Excellent      | Terrible         |

The asterisk on LinkedList's O(1) is crucial: it's O(1) _if you already have the node reference_. Finding the node is O(n). So `list.add(500, element)` on LinkedList is O(500) to find the position plus O(1) to insert, versus O(n) shift on ArrayList.

In practice, ArrayList wins almost every benchmark because:

1. **CPU cache:** ArrayList's contiguous array fits in cache lines. LinkedList nodes are scattered across the heap - every `.next` pointer is a cache miss.
2. **Memory:** Each LinkedList node has prev + next pointers + object header = ~48 bytes overhead per element versus 4-8 bytes for ArrayList.
3. **GC:** Fewer objects, fewer references to trace.

When LinkedList actually wins: implementing a Queue/Deque where you only add/remove at the ends (but `ArrayDeque` is still faster). In practice, the only remaining use case is when you're iterating with a `ListIterator` and doing frequent insert/remove at the current position.

Key insight: Bjarne Stroustrup demonstrated that even for insert-in-middle workloads, `std::vector` (C++ ArrayList) beats `std::list` (C++ LinkedList) for lists up to millions of elements due to cache effects. The same applies to Java.

---

**Q4: Explain fail-fast iterators and ConcurrentModificationException. How would you safely modify a list during iteration?**

_Why they ask:_ Tests awareness of a common production bug.

**Answer:**
ArrayList tracks structural modifications via an `int modCount` field. When you create an iterator, it snapshots `expectedModCount = modCount`. Every `next()` call checks `modCount != expectedModCount` and throws `ConcurrentModificationException` if they differ.

"Structural modification" means changing the size (add/remove), not changing element values via `set()`.

**Four safe approaches:**

1. **`Iterator.remove()`** - removes the current element and updates expectedModCount:

   ```java
   Iterator<String> it = list.iterator();
   while (it.hasNext()) {
       if (shouldRemove(it.next())) {
           it.remove();
       }
   }
   ```

2. **`removeIf()`** (Java 8+) - cleanest for conditional removal:

   ```java
   list.removeIf(e -> e.startsWith("temp"));
   ```

3. **Reverse index loop** - safe for index-based removal:

   ```java
   for (int i = list.size() - 1; i >= 0; i--) {
       if (shouldRemove(list.get(i))) {
           list.remove(i);
       }
   }
   ```

4. **Copy-on-read** - collect items to remove, then remove:
   ```java
   List<String> toRemove = list.stream()
       .filter(this::shouldRemove)
       .toList();
   list.removeAll(toRemove);
   ```

Key insight: `ConcurrentModificationException` is **not** about threads - it happens in single-threaded code too. The name is misleading. It means "concurrent with iteration," not "concurrent threads."

---

**Q5: How does ArrayList compare to CopyOnWriteArrayList for read-heavy concurrent workloads?**

_Why they ask:_ Tests knowledge of concurrent alternatives.

**Answer:**
`CopyOnWriteArrayList` (COWAL) creates a new copy of the entire internal array on every write operation. Reads never block and never see partial state.

| Aspect     | ArrayList + sync | CopyOnWriteArrayList |
| ---------- | ---------------- | -------------------- |
| Read cost  | Lock acquisition | Zero overhead        |
| Write cost | Lock acquisition | Full array copy      |
| Iterator   | Fail-fast (CME)  | Snapshot (stale OK)  |
| Best for   | Balanced R/W     | 99%+ reads           |

Use COWAL when:

- Reads vastly outnumber writes (event listeners, config lists, observer patterns)
- List is small (< 1000 elements)
- Stale reads during iteration are acceptable

Never use COWAL when:

- Writes are frequent - each write copies the entire array
- List is large - copying 10K+ elements per write kills throughput
- You need consistent iteration - COWAL iterators see a snapshot from when they were created

Production pattern:

```java
// Listener registry - perfect COWAL use case
private final List<EventListener> listeners =
    new CopyOnWriteArrayList<>();

// Reads (frequent): no locks
for (EventListener l : listeners) {
    l.onEvent(event);
}

// Writes (rare): copies array
listeners.add(newListener);
```

Key insight: COWAL's iterator never throws `ConcurrentModificationException` because it iterates over a frozen snapshot array. But this means the iterator won't see elements added after it was created.

---

**Q6: What happens if you use an ArrayList as a key in a HashMap? Why is this dangerous?**

_Why they ask:_ Tests understanding of mutability and hashCode contracts.

**Answer:**
`ArrayList` implements `hashCode()` based on its contents. If you put an ArrayList as a HashMap key, then modify the ArrayList, its hashCode changes but the HashMap still has it filed under the old hash bucket.

```java
// DANGEROUS
Map<List<String>, String> map = new HashMap<>();
List<String> key = new ArrayList<>(List.of("a", "b"));
map.put(key, "value");

key.add("c"); // mutates the key!
map.get(key);  // returns null - hash bucket changed
map.get(List.of("a", "b")); // also null!
// The entry is orphaned - unreachable but not GC'd
```

The entry is now permanently orphaned. You can't find it with the old contents or the new contents. It's a memory leak.

**Prevention:** Never use mutable collections as map keys. Use `List.of()` or `Collections.unmodifiableList()` to create immutable keys, or use value objects with stable identity.

---

**Q7: You need to store 50 million integers. Would you use ArrayList<Integer>? What are the alternatives?**

_Why they ask:_ Tests awareness of boxing overhead and memory efficiency.

**Answer:**
`ArrayList<Integer>` for 50M elements would consume roughly:

- 50M `Integer` objects: 50M x 16 bytes (12 header + 4 int) = 800MB
- Object[] references: 50M x 8 bytes = 400MB
- Total: ~1.2GB

An `int[]` would use 50M x 4 bytes = 200MB - 6x less memory.

**Alternatives ranked by efficiency:**

1. **`int[]`** - 200MB, but fixed size
2. **Eclipse Collections `IntArrayList`** - 200MB, resizable, no boxing
3. **`ArrayList<Integer>` with pre-sizing** - 1.2GB
4. **`ArrayList<Integer>` default** - 1.2GB + resize copies

For 50M elements, I'd use `int[]` if size is known, or Eclipse Collections' `IntArrayList` if resizable behavior is needed. Java Valhalla (Project Valhalla value types) will eventually allow `ArrayList<int>` without boxing, but that's not production-ready yet.

Additional consideration: at 50M elements, even iterating has cache implications. `int[]` has perfect cache locality. `ArrayList<Integer>` chases 50M pointers to scattered heap locations.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ArrayList. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

---

---

# HashMap

**TL;DR** - HashMap stores key-value pairs in an array of buckets using hash codes for O(1) average lookup, and understanding hash collisions, load factors, and resizing prevents silent performance degradation.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You have a million user records and need to find one by email. With a list, you scan all million entries - O(n). A sorted list with binary search gives O(log n), but inserting new users requires re-sorting. You need constant-time lookup by arbitrary keys without maintaining sort order.

**THE BREAKING POINT:**
An e-commerce site stores product inventory in a `List<Product>`. Looking up a product by SKU scans the entire list. At 100K products, page load times hit 3 seconds. Adding an index manually means maintaining two data structures in sync - every bug is a data consistency bug.

**THE INVENTION MOMENT:**
"This is exactly why HashMap was created."

**EVOLUTION:**
Java 1.0 had `Hashtable` (synchronized, no nulls allowed). Java 1.2 introduced `HashMap` (unsynchronized, allows null key and values). Java 8 fundamentally changed HashMap internals by converting long chains to red-black trees (treeification), reducing worst-case from O(n) to O(log n).

---

### Textbook Definition

`HashMap` is a hash table implementation of the `Map` interface that stores key-value pairs in an array of buckets. It computes a hash of each key to determine the bucket index, provides O(1) average-case `get` and `put` operations, handles collisions via chaining (linked list, then red-black tree after threshold), and automatically resizes when the load factor is exceeded. It permits one null key and multiple null values, and is not thread-safe.

---

### Understand It in 30 Seconds

**One line:**
A dictionary that finds any value by its key in constant time using hashing.

**One analogy:**

> Think of a library with 16 shelves. Each book's title is converted to a shelf number using a formula. To find a book, compute its shelf number, go straight there, and scan only that shelf - not the whole library.

**One insight:**
The magic is in the hash function: it converts any key into an array index. When two keys hash to the same index (collision), HashMap chains them. Java 8's critical optimization converts long chains (8+) to balanced trees, preventing O(n) degradation from bad hash functions.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Every key has exactly one value (put with same key overwrites)
2. Key lookup is O(1) on average - hash determines bucket, bucket is small
3. Keys must correctly implement `hashCode()` and `equals()` - these form the identity contract
4. Iteration order is not guaranteed

**DERIVED DESIGN:**
The hash-to-index mapping creates a fixed-size bucket array. Collisions are inevitable (pigeonhole principle), so each bucket holds a chain. The load factor (default 0.75) triggers resize to keep chains short.

**THE TRADE-OFFS:**
**Gain:** O(1) average lookup, insert, delete by key
**Cost:** No ordering, wasted space (array larger than element count), requires good hashCode

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Hash collisions are mathematically unavoidable - any function mapping infinite keys to finite buckets must collide.
**Accidental:** Java's `Object.hashCode()` returning `int` (32-bit) while arrays can be much smaller means the hash must be compressed, adding a secondary hash spread.

---

### Mental Model / Analogy

> Imagine a post office with numbered P.O. boxes. Your name gets converted to a box number by a formula. To pick up mail, you compute your box number and go directly there. If two people get the same box number, their mail shares the box in a stack.

- "P.O. box number" -> bucket index
- "Name formula" -> hash function
- "Two people sharing a box" -> hash collision
- "Stack of mail in one box" -> linked list / tree chain
- "Adding more boxes when too crowded" -> resize/rehash

Where this analogy breaks down: P.O. boxes don't automatically reorganize themselves or convert stacks to sorted structures.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HashMap is a container that stores pairs of things: a key and a value. You give it a key, and it instantly gives back the associated value. Like a real dictionary where you look up a word (key) and get the definition (value).

**Level 2 - How to use it (junior developer):**
Create with `new HashMap<>()` or `Map.of()` for immutable. Use `put(key, value)`, `get(key)`, `containsKey(key)`, `remove(key)`. Always override both `hashCode()` and `equals()` on custom key classes. Use `getOrDefault()`, `computeIfAbsent()`, `merge()` for cleaner code. Never use mutable objects as keys.

**Level 3 - How it works (mid-level engineer):**
Internally it's a `Node<K,V>[] table` (bucket array). `put(key, value)` computes `(table.length - 1) & hash(key.hashCode())` to find the bucket index. The `hash()` method spreads the hashCode's higher bits into lower bits to reduce clustering. Collisions chain as linked list nodes. When a chain reaches 8 and table size >= 64, it treeifies into a red-black tree. Load factor 0.75 triggers `resize()` which doubles the table and rehashes all entries.

**Level 4 - Mastery (senior/staff+ engineer):**
HashMap's `hash()` function XORs `h ^ (h >>> 16)` to spread high bits into the low bits that determine bucket index - this matters because `table.length` is always a power of 2, so only the lowest bits of the hash are used for indexing. The treeification threshold of 8 was chosen based on Poisson distribution: with a good hash function and load factor 0.75, the probability of 8+ collisions in one bucket is less than 1 in 10 million. `resize()` is O(n) but happens infrequently enough that amortized cost is O(1). In Java 8+, when the table is resized, each node either stays in the same bucket or moves to `oldIndex + oldCapacity` - no hash recomputation needed, just check one bit.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
HashMap structure (Java 8+):

  table (Node[]):
  [0] -> null
  [1] -> (K1,V1) -> (K5,V5) -> null
  [2] -> null
  [3] -> (K2,V2) -> null
  [4] -> TreeNode(K3,V3)  [treeified]
          /        \
     (K7,V7)    (K8,V8)
  ...
  [15] -> (K4,V4) -> null

  put("email", "a@b.com"):
  1. hash = hash("email".hashCode())
  2. index = hash & (table.length - 1)
  3. If table[index] == null:
       table[index] = new Node(hash,key,val)
  4. If table[index] exists:
       Walk chain, check equals() for each
       If found: replace value
       If not: append to chain
  5. If chain.length >= 8:
       treeifyBin() -> red-black tree
  6. If ++size > threshold (capacity*0.75):
       resize() -> double table, rehash all
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
put(key, value)
  -> hashCode() on key
  -> hash() spreads bits
  -> index = hash & (len-1)
  -> bucket lookup  <- YOU ARE HERE
  -> chain walk / tree search
  -> insert or replace
  -> check load factor -> resize if needed
```

**FAILURE PATH:**

```
All keys hash to same bucket
  -> chain grows to n entries
  -> get() becomes O(n) [or O(log n) if treeified]
  -> Response times spike
  -> Symptom: CPU-bound, high latency, profiler
     shows time in HashMap.get()
```

**WHAT CHANGES AT SCALE:**
With millions of entries, `resize()` becomes expensive - doubling a 10M-entry table copies 10M nodes and triggers old-gen GC. At extreme scale, consider `ConcurrentHashMap` for thread safety or off-heap maps like Chronicle Map for memory-mapped storage that doesn't burden GC.

---

### Code Example

**Example 1 - Broken hashCode/equals**

```java
// BAD: mutable key with default hashCode
public class UserId {
    String email;
    // no hashCode/equals override
}

Map<UserId, String> map = new HashMap<>();
UserId id = new UserId();
id.email = "a@b.com";
map.put(id, "Alice");
map.get(id); // works... for now

UserId lookup = new UserId();
lookup.email = "a@b.com";
map.get(lookup); // null! Different identity

// GOOD: immutable key with proper contracts
public record UserId(String email) {}
// record auto-generates hashCode, equals, toString

Map<UserId, String> map = new HashMap<>();
map.put(new UserId("a@b.com"), "Alice");
map.get(new UserId("a@b.com")); // "Alice"
```

**Example 2 - Efficient map operations (Java 8+)**

```java
// BAD: check-then-act pattern
Map<String, List<String>> groups = new HashMap<>();
String key = "admin";
if (!groups.containsKey(key)) {
    groups.put(key, new ArrayList<>());
}
groups.get(key).add("Alice");

// GOOD: computeIfAbsent - atomic, clean
groups.computeIfAbsent(key, k -> new ArrayList<>())
      .add("Alice");

// GOOD: merge for counting
Map<String, Integer> counts = new HashMap<>();
for (String word : words) {
    counts.merge(word, 1, Integer::sum);
}
```

**How to test / verify correctness:**
Test that your key class's `hashCode()` and `equals()` satisfy the contract: equal objects must have equal hash codes. Use `map.get(new Key(sameValue))` to verify lookup by value equality, not identity.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Always override both `hashCode()` and `equals()` on key classes - breaking either breaks the map
2. Java 8 treeifies long chains (8+) to prevent O(n) degradation from bad hashes
3. Default load factor 0.75 balances space vs time - pre-size to avoid costly resizes

**Interview one-liner:**
"HashMap uses an array of buckets indexed by key hash, handling collisions with linked lists that treeify to red-black trees at 8 nodes. It resizes at 75% load factor. The critical contract is that keys must correctly implement hashCode and equals."

---

### The Surprising Truth

HashMap's treeification threshold of 8 wasn't arbitrary - it was derived from Poisson probability analysis. With a load factor of 0.75 and a reasonably distributed hash function, the probability of any single bucket containing 8 or more entries is approximately 0.00000006 (6 in 100 million). The feature exists almost exclusively as a defense against hash-flooding denial-of-service attacks, where an attacker deliberately crafts keys with identical hash codes to degrade HashMap to O(n) performance.

---

### Interview Deep-Dive

**Q1: Walk me through what happens internally when you call `map.put(key, value)`.**

_Why they ask:_ Foundational understanding of the core operation.

**Answer:**
The full sequence in Java 8+ HashMap:

1. **Null check:** If key is null, it goes to bucket 0 (special case).
2. **Hash computation:** `hash = (h = key.hashCode()) ^ (h >>> 16)`. This XOR-spreads the upper 16 bits into the lower 16 bits because the bucket index uses only the lowest bits.
3. **Bucket index:** `index = (table.length - 1) & hash`. Since table length is always a power of 2, this is equivalent to `hash % table.length` but faster.
4. **Empty bucket:** If `table[index] == null`, create a new `Node(hash, key, value, null)` and place it there.
5. **Existing bucket - chain walk:** If the bucket has entries, walk the linked list. For each node, check `hash == node.hash && (key == node.key || key.equals(node.key))`. Hash comparison first is a fast-path optimization - avoids expensive `equals()` when hashes differ.
6. **Key found:** Replace the value, return the old value.
7. **Key not found:** Append a new node to the end of the chain.
8. **Treeification check:** If chain length >= `TREEIFY_THRESHOLD` (8) AND table length >= 64, convert the chain to a red-black tree. If table is too small, resize instead.
9. **Size check:** Increment `size`. If `size > threshold` (capacity x load factor), call `resize()` to double the table.

Key insight: the hash comparison in step 5 is crucial for performance. String.equals() might compare many characters, but `int == int` is a single CPU instruction. Since most comparisons are mismatches, this saves significant time.

---

**Q2: Your application's response time increases from 5ms to 500ms after deploying a new entity class used as a HashMap key. What do you investigate?**

_Why they ask:_ Tests debugging ability connecting HashMap internals to production symptoms.

**Answer:**
This is almost certainly a broken `hashCode()` implementation. My investigation:

1. **Check the entity's hashCode():** If it returns a constant (like `return 1;`) or has very low entropy, all entries land in the same bucket, degrading from O(1) to O(n) or O(log n).

   ```bash
   # Check hash distribution in a running app
   jcmd <pid> VM.classloader_stats
   ```

2. **Profile to confirm:** Use async-profiler:

   ```bash
   ./profiler.sh -e cpu -d 30 -f profile.html <pid>
   ```

   Look for `HashMap.get` or `HashMap.put` dominating CPU time. If you see `TreeNode.find()` or `HashMap.getNode()` high in the flame graph, it confirms collision chains.

3. **Verify hashCode/equals contract:**

   ```java
   // Quick test
   Set<Integer> hashes = entities.stream()
       .map(Object::hashCode)
       .collect(Collectors.toSet());
   System.out.printf(
       "%d entities, %d unique hashes%n",
       entities.size(), hashes.size());
   // If unique hashes << entities: bad hash
   ```

4. **Fix:** Implement `hashCode()` using `Objects.hash()` or the effective Java recipe:

   ```java
   @Override
   public int hashCode() {
       return Objects.hash(field1, field2, field3);
   }
   ```

   Or better: use `record` which generates correct implementations.

5. **Verify the fix:** Compare response times before/after. Check bucket distribution in tests.

Key insight: the 5ms to 500ms jump (100x) strongly suggests O(n) degradation. With treeification, it would be O(log n) which is more like 5ms to 50ms. If you see 100x, the keys might not implement `Comparable`, which prevents treeification from working efficiently.

---

**Q3: Compare HashMap, TreeMap, and LinkedHashMap. When would you choose each?**

_Why they ask:_ Tests decision-making between map implementations.

**Answer:**

| Aspect     | HashMap   | TreeMap       | LinkedHashMap   |
| ---------- | --------- | ------------- | --------------- |
| Order      | None      | Sorted by key | Insertion order |
| Get/Put    | O(1) avg  | O(log n)      | O(1) avg        |
| Null keys  | 1 allowed | Not allowed   | 1 allowed       |
| Implements | Map       | NavigableMap  | Map             |
| Memory     | Lowest    | Higher (tree) | Higher (links)  |

**Choose HashMap when:** You need fast lookup and don't care about order. This is the default choice for 90% of use cases.

**Choose TreeMap when:** You need sorted iteration, range queries (`subMap`, `headMap`, `tailMap`), or finding nearest keys (`floorKey`, `ceilingKey`). Example: a leaderboard where you need "all scores between 80 and 90."

**Choose LinkedHashMap when:** You need predictable iteration order matching insertion order. Two critical use cases:

1. **LRU Cache:** `LinkedHashMap(capacity, 0.75f, true)` with `removeEldestEntry()` override gives you a complete LRU cache in 5 lines.
2. **JSON serialization:** When field order in output must match insertion order.

```java
// LRU cache in 5 lines
Map<String, Data> cache = new LinkedHashMap<>(
    100, 0.75f, true) {
    protected boolean removeEldestEntry(
            Map.Entry<String, Data> e) {
        return size() > MAX_SIZE;
    }
};
```

Key insight: if you're choosing between these three, the real question is "do I need ordering?" If no: HashMap. If sorted: TreeMap. If insertion-ordered: LinkedHashMap.

---

**Q4: How does ConcurrentHashMap differ from HashMap? Can you explain its internal structure?**

_Why they ask:_ Tests concurrent programming knowledge.

**Answer:**
`ConcurrentHashMap` (CHM) provides thread-safe operations without locking the entire map.

**Java 8+ internals:** CHM uses the same bucket array structure as HashMap but replaces locking with:

1. **CAS (Compare-And-Swap)** for inserting into empty buckets - lock-free for the common case
2. **Per-bucket `synchronized`** blocks for collision handling - only locks the specific bucket being modified, not the whole map
3. **Volatile reads** for `get()` operations - completely lock-free reads

Key differences from `Collections.synchronizedMap(new HashMap<>())`:

| Aspect           | synchronizedMap | ConcurrentHashMap  |
| ---------------- | --------------- | ------------------ |
| Read locking     | Full map lock   | None (volatile)    |
| Write locking    | Full map lock   | Per-bucket         |
| Iteration        | Fail-fast (CME) | Weakly consistent  |
| Null keys/values | Allowed         | NOT allowed        |
| Compound ops     | Not atomic      | `compute`, `merge` |

**Why no null values in CHM?** Because `get(key)` returning null is ambiguous: does the key not exist, or is the value null? In a single-threaded HashMap, you can call `containsKey()` to disambiguate. In CHM, another thread could modify the map between `containsKey()` and `get()` - making the check-then-act pattern unsafe.

**Production guidance:** Use CHM when multiple threads read and write. Use HashMap (faster) when access is single-threaded or externally synchronized. Never wrap CHM in `Collections.synchronizedMap()` - it defeats the purpose.

---

**Q5: Explain how HashMap handles hash collisions and why Java 8 introduced treeification.**

_Why they ask:_ Tests depth of understanding of the collision resolution mechanism.

**Answer:**
HashMap handles collisions through **separate chaining**: each bucket holds a linked list (or tree) of entries that hash to the same index.

**Pre-Java 8 (linked list only):**
When multiple keys map to the same bucket, they form a singly-linked list. `get()` walks the list comparing `hash` and `equals()`. Worst case: all n keys in one bucket = O(n) lookup.

**Java 8+ (linked list + red-black tree):**
When a chain reaches `TREEIFY_THRESHOLD` (8 nodes) AND the table has at least 64 buckets, the chain converts to a balanced red-black tree. This changes worst-case lookup from O(n) to O(log n).

**Why was this needed?** Hash-flooding attacks. An attacker who knows the hash function can craft keys that all collide in one bucket, degrading HashMap to O(n) and causing denial of service. Before Java 8, this was a real CVE (hash collision DoS attacks on web frameworks). Treeification limits the damage to O(log n).

**Treeification conditions:**

1. Chain length >= 8
2. Table size >= 64 (if table is too small, it resizes instead)
3. Key class implements `Comparable` (for tree ordering) OR keys are compared by `System.identityHashCode` as tiebreaker

**Untreeification:** When resize reduces a bucket's count below `UNTREEIFY_THRESHOLD` (6), the tree converts back to a linked list. The gap between 8 and 6 prevents thrashing.

Key insight: under normal conditions with a good hash function, treeification almost never triggers. Its value is entirely as a safety net against pathological inputs.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for HashMap. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

---

---

# TreeMap

**TL;DR** - TreeMap is a sorted map backed by a red-black tree that maintains keys in natural order, giving O(log n) operations and enabling range queries that HashMap cannot do.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You need a leaderboard showing scores from highest to lowest. With HashMap, you can look up any player's score in O(1), but to get "all players scoring between 80 and 90" you must scan every entry. Sorting the entire map on every query kills performance.

**THE BREAKING POINT:**
A trading system needs the best bid and best ask prices at all times. HashMap can't answer "what's the highest key?" without scanning everything. Maintaining a separate sorted structure alongside a HashMap doubles the code complexity and introduces synchronization bugs.

**THE INVENTION MOMENT:**
"This is exactly why TreeMap was created."

**EVOLUTION:**
TreeMap was introduced in Java 1.2 as part of the Collections Framework. It implements `NavigableMap` (added in Java 6), providing rich navigation methods like `floorKey()`, `ceilingKey()`, `subMap()`, and `descendingMap()`. The underlying red-black tree has remained stable, though Java 8 added `merge()` and `compute()` methods.

---

### Textbook Definition

`TreeMap` is a red-black tree-based implementation of the `NavigableMap` interface. It stores key-value pairs sorted by keys' natural ordering (via `Comparable`) or by a provided `Comparator`. All basic operations (`get`, `put`, `remove`, `containsKey`) run in O(log n) time. It does not permit null keys (when using natural ordering) and guarantees that iteration follows key order.

---

### Understand It in 30 Seconds

**One line:**
A map that keeps its keys sorted and lets you query ranges efficiently.

**One analogy:**

> Think of a physical dictionary (the book kind). Words are sorted alphabetically. You can find any word quickly by opening near the right spot, and you can easily find "all words between M and N" by flipping to that section.

**One insight:**
The key insight is the trade-off: TreeMap sacrifices HashMap's O(1) lookup for O(log n), but gains the ability to answer "what's the nearest key?" and "give me everything between X and Y" - questions HashMap cannot answer without scanning all entries.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Keys are always maintained in sorted order (no explicit sort step needed)
2. All operations are O(log n) - guaranteed, not amortized
3. The tree is self-balancing (red-black) - no degenerate O(n) cases
4. Iteration order matches key sort order

**DERIVED DESIGN:**
A balanced binary search tree inherently maintains sorted order at the cost of O(log n) per operation. Red-black trees guarantee the tree height stays at most 2\*log(n), preventing the worst case of unbalanced BSTs.

**THE TRADE-OFFS:**
**Gain:** Sorted iteration, range queries, nearest-key lookups, guaranteed O(log n)
**Cost:** Slower than HashMap for pure key-value lookup, higher memory per entry (tree node overhead), keys must be Comparable

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Maintaining sort order during insertions requires tree rotations - this is inherent to balanced BSTs.
**Accidental:** Java's `Comparable` interface requirement adds boilerplate to custom key classes that could be simplified.

---

### Mental Model / Analogy

> Imagine a filing cabinet where folders are always kept in alphabetical order. Finding a folder takes a bit longer than reaching into a numbered bin, but you can instantly find "all folders from M to P" by looking at one section.

- "Alphabetical order" -> sorted keys via Comparable/Comparator
- "Finding a folder" -> O(log n) tree traversal
- "All folders from M to P" -> `subMap("M", "Q")`
- "Auto-rearranging on insert" -> red-black tree rebalancing

Where this analogy breaks down: Filing cabinets don't automatically rebalance themselves when one section gets too full.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
TreeMap is a map that keeps its keys sorted automatically. When you iterate over it, entries come out in order. It's slower than HashMap but lets you do things like "find all entries between two values."

**Level 2 - How to use it (junior developer):**
Create with `new TreeMap<>()` (natural ordering) or `new TreeMap<>(comparator)`. Same `put`/`get`/`remove` as HashMap. Use `firstKey()`, `lastKey()`, `subMap(from, to)`, `headMap(to)`, `tailMap(from)` for range operations. Keys must implement `Comparable` or you must provide a `Comparator`.

**Level 3 - How it works (mid-level engineer):**
Internally a red-black tree: each node has key, value, left/right children, parent pointer, and a color bit. Insertions and deletions trigger rotations and recoloring to maintain balance invariants: no two consecutive red nodes, and all paths from root to leaves have the same number of black nodes. This guarantees tree height <= 2\*log2(n+1).

**Level 4 - Mastery (senior/staff+ engineer):**
TreeMap is the right choice when you need SortedMap/NavigableMap operations. In practice, the O(log n) vs O(1) difference matters less than people think for small-to-medium maps (< 10K entries) because TreeMap has better cache behavior than HashMap for ordered scans. For high-frequency trading or order books, `ConcurrentSkipListMap` provides the same sorted semantics with better concurrency. TreeMap's `subMap()` returns a view, not a copy - modifications to the submap modify the original tree, which is powerful for windowed processing.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
Red-Black Tree structure (simplified):

          (50, Black)
         /            \
    (30, Red)      (70, Red)
    /     \         /     \
 (20,B) (40,B)  (60,B) (80,B)

  put(35):
  1. BST insert: navigate 50->30->40->left
  2. Color new node Red
  3. Check RB violations
  4. Recolor or rotate to fix
  5. Root stays Black

  subMap(25, 45):
  Returns view: {30->v, 35->v, 40->v}
  (inclusive start, exclusive end by default)
```

**Red-black invariants:**

1. Every node is red or black
2. Root is always black
3. No two consecutive red nodes (parent-child)
4. Every path from root to null leaf has the same number of black nodes

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
put(key, value)
  -> compareTo()/Comparator.compare()
  -> BST traversal to find position
  -> insert new red node  <- YOU ARE HERE
  -> fixAfterInsertion() - recolor/rotate
  -> size++
```

**FAILURE PATH:**

```
Key doesn't implement Comparable
  AND no Comparator provided
  -> ClassCastException on first put()

Inconsistent compareTo/equals
  -> TreeMap finds key, HashMap doesn't
  -> Subtle bugs when switching implementations
```

**WHAT CHANGES AT SCALE:**
TreeMap's O(log n) is very stable - doubling the entries adds only one more comparison. At 1M entries, lookup takes ~20 comparisons. The bottleneck at scale is usually the `Comparable.compareTo()` implementation itself - complex string comparisons or multi-field comparisons dominate. For concurrent sorted access at scale, `ConcurrentSkipListMap` scales better across cores.

---

### Code Example

**Example 1 - Range queries**

```java
// BAD: filtering HashMap for range
Map<Integer, String> scores = new HashMap<>();
// ... populate
List<Map.Entry<Integer, String>> range =
    scores.entrySet().stream()
        .filter(e -> e.getKey() >= 80
                  && e.getKey() <= 90)
        .sorted(Map.Entry.comparingByKey())
        .toList(); // O(n) scan + O(n log n) sort

// GOOD: TreeMap range query
TreeMap<Integer, String> scores = new TreeMap<>();
// ... populate
Map<Integer, String> range =
    scores.subMap(80, true, 90, true);
// O(log n) to find boundaries, O(k) to iterate
```

**Example 2 - Finding nearest keys**

```java
TreeMap<LocalTime, String> schedule =
    new TreeMap<>();
schedule.put(LocalTime.of(9, 0), "standup");
schedule.put(LocalTime.of(10, 30), "review");
schedule.put(LocalTime.of(14, 0), "planning");

LocalTime now = LocalTime.of(10, 0);

// What's the next event?
Map.Entry<LocalTime, String> next =
    schedule.ceilingEntry(now);
// 10:30 -> "review"

// What was the last event?
Map.Entry<LocalTime, String> prev =
    schedule.floorEntry(now);
// 09:00 -> "standup"
```

**How to test / verify correctness:**
Verify that `subMap()` boundaries work correctly (inclusive vs exclusive), that `firstKey()`/`lastKey()` return expected values, and that custom Comparators produce the expected sort order.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. O(log n) for everything - guaranteed, not amortized - but no O(1) fast path like HashMap
2. Use it when you need sorted iteration, range queries, or nearest-key lookups
3. Keys must implement `Comparable` or you must provide a `Comparator` at construction

**Interview one-liner:**
"TreeMap is a red-black tree that keeps keys sorted, trading HashMap's O(1) for O(log n) in exchange for range queries via subMap, floorKey, and ceilingKey - essential for things like order books or time-series indexes."

---

### The Surprising Truth

TreeMap's `subMap()`, `headMap()`, and `tailMap()` return live views, not copies. Inserting into the view inserts into the original tree, and vice versa. But if you insert a key outside the view's range, it throws `IllegalArgumentException`. This means you can use a subMap view as a "windowed writer" that enforces key bounds at the API level - a design pattern rarely taught but extremely useful for partitioned processing.

---

### Interview Deep-Dive

**Q1: When would you choose TreeMap over HashMap?**

_Why they ask:_ Tests decision-making ability.

**Answer:**
Choose TreeMap when you need any of these capabilities that HashMap cannot provide:

1. **Sorted iteration:** Entries come out in key order without explicit sorting
2. **Range queries:** `subMap(from, to)` returns all entries in a range in O(log n + k)
3. **Nearest-key lookups:** `floorKey()`, `ceilingKey()`, `higherKey()`, `lowerKey()`
4. **First/last access:** `firstKey()`, `lastKey()` in O(log n)
5. **Descending views:** `descendingMap()` for reverse-order iteration

Real-world examples: leaderboards (range of scores), scheduling systems (next event after time T), order books in trading (best bid/ask), IP range lookups (which subnet contains this IP).

Choose HashMap for everything else. The O(1) vs O(log n) difference is significant at scale: for 1M entries, HashMap does 1 operation, TreeMap does ~20 comparisons. For < 1000 entries, the difference is negligible.

---

**Q2: Can TreeMap have a null key? What about null values?**

_Why they ask:_ Tests attention to edge cases.

**Answer:**
Null values are always allowed in TreeMap. Null keys depend on the ordering:

- **Natural ordering (Comparable):** Null key throws `NullPointerException` because `compareTo()` is called on the key, and you can't call a method on null.
- **Custom Comparator:** Null key is allowed if and only if the Comparator handles null. Example:
  ```java
  TreeMap<String, Integer> map = new TreeMap<>(
      Comparator.nullsFirst(
          Comparator.naturalOrder()));
  map.put(null, 42); // works
  ```

This is different from HashMap, which always allows one null key (stored in bucket 0 as a special case).

Key insight: this difference means switching from HashMap to TreeMap can break code that uses null keys - a subtle migration bug.

---

**Q3: What's the time complexity of iterating over all entries in a TreeMap vs HashMap?**

_Why they ask:_ Tests understanding of iteration behavior.

**Answer:**
Both are O(n) for full iteration, but with important differences:

**TreeMap:** O(n) - in-order traversal of the tree. Each `next()` call is amortized O(1) using a successor-finding algorithm that touches each edge at most twice. The iteration is always in sorted key order.

**HashMap:** O(n + capacity) - must scan the entire bucket array, including empty buckets. If you have 100 entries in a HashMap with capacity 16384, iteration still touches all 16384 buckets. This is why a large, sparse HashMap iterates slower than expected.

**LinkedHashMap:** O(n) - follows the linked list regardless of capacity. Best of both worlds for iteration performance.

This is a non-obvious performance difference. For maps with high capacity but few entries, TreeMap or LinkedHashMap iterates significantly faster than HashMap.

---

**Q4: How does TreeMap's red-black tree ensure O(log n) guarantees? What happens during rebalancing?**

_Why they ask:_ Tests data structure knowledge depth.

**Answer:**
Red-black trees maintain balance through two invariants that limit height:

1. **No consecutive reds:** A red node cannot have a red child
2. **Black-height consistency:** Every path from root to any null leaf has the same number of black nodes

These guarantee that the longest path (alternating red-black) is at most 2x the shortest path (all black), bounding height to 2\*log2(n+1).

**After insertion (new node is red):**

- If parent is black: done (no violation)
- If parent is red (violation): fix by examining uncle:
  - Uncle is red: recolor parent, uncle, grandparent
  - Uncle is black: rotate (left or right) + recolor

**After deletion:**

- Similar but more complex - up to 3 rotations
- The key insight is that rotations are O(1) operations (pointer swaps), so rebalancing after any insert/delete is O(log n) at worst

In practice, Java's TreeMap performs at most 2 rotations per insertion and 3 per deletion. The constant factors are small.

---

**Q5: Design a time-based cache where you can efficiently evict all entries older than T.**

_Why they ask:_ Tests ability to apply TreeMap in system design.

**Answer:**
Use a `TreeMap<Instant, V>` keyed by insertion timestamp:

```java
public class TimeCache<V> {
    private final TreeMap<Instant, V> store =
        new TreeMap<>();
    private final Duration ttl;

    public TimeCache(Duration ttl) {
        this.ttl = ttl;
    }

    public void put(V value) {
        store.put(Instant.now(), value);
    }

    public void evictExpired() {
        Instant cutoff =
            Instant.now().minus(ttl);
        // headMap returns view of all keys < cutoff
        store.headMap(cutoff).clear();
        // O(log n) to find cutoff + O(k) to remove
    }

    public Collection<V> getRecent(Duration window) {
        Instant since =
            Instant.now().minus(window);
        return store.tailMap(since).values();
    }
}
```

This is O(log n + k) for eviction where k is evicted entries, versus O(n) if using HashMap (scan all entries to find expired ones). For a cache with millions of entries where only hundreds expire per cycle, this is orders of magnitude faster.

For concurrent access, replace TreeMap with `ConcurrentSkipListMap` which provides the same NavigableMap interface with thread safety.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for TreeMap. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

---

---

# HashSet

**TL;DR** - HashSet is a collection of unique elements backed by a HashMap internally, giving O(1) add/remove/contains, and understanding that it delegates to HashMap explains every behavior.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You need to track which users are currently online. Using a List, checking "is user X online?" scans the entire list - O(n). Adding a user requires first checking the whole list for duplicates. At 100K online users, every status check takes milliseconds.

**THE BREAKING POINT:**
A deduplication pipeline uses `list.contains()` before adding each item. With 1M items, each contains check scans the growing list. Processing time grows quadratically - what started at 10 minutes now takes 12 hours.

**THE INVENTION MOMENT:**
"This is exactly why HashSet was created."

**EVOLUTION:**
Java 1.0 had no Set interface. Java 1.2 introduced the Collections Framework with `HashSet`, `TreeSet`, and `LinkedHashSet`. HashSet's implementation is simple: it wraps a `HashMap` where elements are keys and values are a dummy constant object. Java 9+ added `Set.of()` and `Set.copyOf()` for immutable sets.

---

### Textbook Definition

`HashSet` is an implementation of the `Set` interface backed internally by a `HashMap`. It stores unique elements with no guaranteed iteration order, provides O(1) average-case `add`, `remove`, and `contains` operations, permits one null element, and is not thread-safe. Two elements are considered duplicates if their `equals()` method returns true.

---

### Understand It in 30 Seconds

**One line:**
A bag that automatically rejects duplicates and finds any element instantly.

**One analogy:**

> Think of a bouncer with a guest list. When someone arrives, the bouncer checks the list in constant time (it's organized by name hash). If the name is already on the list, they're turned away. No duplicates get in.

**One insight:**
HashSet is literally a HashMap with ignored values. `set.add(element)` calls `map.put(element, PRESENT)` where PRESENT is a dummy Object. Every HashSet behavior - capacity, load factor, resizing, collision handling - is inherited directly from HashMap.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. No duplicate elements (defined by `equals()`)
2. At most one null element
3. O(1) average for add/remove/contains (same as HashMap)
4. No guaranteed iteration order

**DERIVED DESIGN:**
Since a Set is conceptually a Map with only keys, HashSet delegates everything to HashMap. The element is the key; the value is a static dummy object. This reuses all of HashMap's hashing, collision handling, and resizing logic.

**THE TRADE-OFFS:**
**Gain:** O(1) membership testing, automatic deduplication
**Cost:** No ordering, no index-based access, memory overhead of HashMap wrapper

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Uniqueness requires a way to efficiently check membership before adding - hashing is the most practical approach.
**Accidental:** Each element has a dummy value object consuming 16+ bytes of overhead - a purpose-built hash set could eliminate this.

---

### Mental Model / Analogy

> Think of a jar of unique marbles. Each marble has a color, and the jar rejects any marble whose color is already present. Finding "do I have a blue marble?" is instant because marbles are organized by color hash.

- "Marble color" -> element's hashCode
- "Rejecting duplicates" -> add() returns false if equals() matches
- "Organized by color hash" -> HashMap bucket structure
- "Jar capacity" -> internal HashMap capacity and load factor

Where this analogy breaks down: Real jars don't organize contents by hash - finding a specific marble in a real jar is O(n).

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HashSet is a collection that stores unique items. If you try to add something that's already there, it silently ignores the duplicate. You can quickly check if any item exists in the set.

**Level 2 - How to use it (junior developer):**
Create with `new HashSet<>()` or `Set.of()` for immutable. Use `add(e)` (returns boolean), `contains(e)`, `remove(e)`. For deduplication: `new HashSet<>(listWithDupes)`. Use `retainAll()` for intersection, `addAll()` for union, `removeAll()` for difference. Always override `hashCode()` and `equals()` on custom element classes.

**Level 3 - How it works (mid-level engineer):**
Internally it's `private transient HashMap<E, Object> map` with `private static final Object PRESENT = new Object()`. `add(e)` calls `map.put(e, PRESENT)`, returns true if no previous mapping. `contains(e)` calls `map.containsKey(e)`. All performance characteristics are inherited from HashMap: same load factor (0.75), same treeification, same resizing behavior.

**Level 4 - Mastery (senior/staff+ engineer):**
The "HashMap with dummy values" design is memory-inefficient - each element wastes ~16 bytes on the PRESENT value and map entry overhead. For memory-critical workloads, Eclipse Collections' `UnifiedSet` or Koloboke's `HashObjSet` are 2-3x more memory-efficient. When you need a concurrent set, `ConcurrentHashMap.newKeySet()` (Java 8+) is preferred over `Collections.synchronizedSet(new HashSet<>())` because it provides per-bucket locking. For enum sets, `EnumSet` is drastically more efficient - it uses a bit vector internally.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
HashSet internal delegation:

  HashSet.add("hello"):
    -> HashMap.put("hello", PRESENT)
      -> hash("hello".hashCode())
      -> index = hash & (table.length - 1)
      -> insert if not present
      -> return null (new) or PRESENT (dup)
    -> return putResult == null  // true = new

  HashSet.contains("hello"):
    -> HashMap.containsKey("hello")
      -> same hash + bucket lookup
      -> return true if found
```

Everything - capacity, load factor, resizing, collision handling, treeification - is pure HashMap behavior.

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
add(element)
  -> hashCode() on element
  -> HashMap.put(element, PRESENT)
     <- YOU ARE HERE
  -> returns true if new, false if duplicate
```

**FAILURE PATH:**

```
Element class overrides equals() but not hashCode()
  -> Two "equal" elements hash to different buckets
  -> Set allows both "duplicates"
  -> contains() finds one but not the other
  -> Subtle logic bugs
```

**WHAT CHANGES AT SCALE:**
At millions of elements, HashSet's memory overhead becomes significant. Each element costs: object header (16 bytes) + HashMap.Node overhead (32 bytes) + PRESENT reference (8 bytes). For 10M strings averaging 40 bytes each, the set overhead nearly doubles memory usage. At this scale, consider Bloom filters for probabilistic membership testing or bitmap-based sets for integer elements.

---

### Code Example

**Example 1 - Deduplication**

```java
// BAD: O(n^2) deduplication with List
List<String> unique = new ArrayList<>();
for (String item : input) {
    if (!unique.contains(item)) { // O(n) scan
        unique.add(item);
    }
}

// GOOD: O(n) deduplication with HashSet
Set<String> unique = new LinkedHashSet<>(input);
// LinkedHashSet preserves insertion order
// Total: O(n)
```

**Example 2 - Set operations**

```java
Set<String> teamA = new HashSet<>(
    Set.of("Alice", "Bob", "Carol"));
Set<String> teamB = new HashSet<>(
    Set.of("Bob", "David", "Carol"));

// Intersection (members in both teams)
Set<String> both = new HashSet<>(teamA);
both.retainAll(teamB); // {"Bob", "Carol"}

// Union (all unique members)
Set<String> all = new HashSet<>(teamA);
all.addAll(teamB);
// {"Alice","Bob","Carol","David"}

// Difference (only in A)
Set<String> onlyA = new HashSet<>(teamA);
onlyA.removeAll(teamB); // {"Alice"}
```

**How to test / verify correctness:**
Verify that `add()` returns false for duplicates, that `size()` reflects unique count, and that custom objects with proper `hashCode()`/`equals()` are correctly deduplicated.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. HashSet is literally a HashMap underneath - element is the key, value is a dummy constant
2. `hashCode()` AND `equals()` must both be correctly implemented on element classes
3. Use `LinkedHashSet` when you need uniqueness plus insertion order preservation

**Interview one-liner:**
"HashSet delegates to HashMap internally - the element is the key, the value is a dummy object. It gives O(1) add, contains, and remove, but you must ensure your element class correctly implements both hashCode and equals."

---

### The Surprising Truth

Because HashSet wraps HashMap, creating a `HashSet<>(collection)` actually creates a HashMap with capacity sized for the collection's size divided by the load factor (0.75). So `new HashSet<>(Arrays.asList(1,2,3))` creates an internal HashMap with capacity 4 (3/0.75 = 4, rounded to next power of 2 = 4). This means small sets are more memory-efficient than you'd expect, but the PRESENT dummy value is still wasted space - a fact that led Google's Guava and Eclipse Collections to create Set implementations that don't wrap Map.

---

### Interview Deep-Dive

**Q1: How does HashSet determine if two elements are duplicates?**

_Why they ask:_ Tests understanding of the equals/hashCode contract.

**Answer:**
HashSet uses a two-step process, inherited from HashMap's key comparison:

1. **Hash comparison:** `hash(a.hashCode()) == hash(b.hashCode())`
2. **Equality check (only if hashes match):** `a == b || a.equals(b)`

Both steps must pass for elements to be considered duplicates. This means:

- Two objects with different `hashCode()` are always different elements (even if `equals()` returns true - which would be a contract violation)
- Two objects with the same `hashCode()` are only duplicates if `equals()` also returns true

The critical contract: **if `a.equals(b)` then `a.hashCode() == b.hashCode()`**. The reverse is not required - different objects can have the same hashCode (collision).

Common bugs:

```java
// BUG: overrides equals but not hashCode
class Item {
    String name;
    public boolean equals(Object o) {
        return name.equals(((Item) o).name);
    }
    // hashCode defaults to memory address!
}
Set<Item> set = new HashSet<>();
set.add(new Item("A"));
set.contains(new Item("A")); // false!
```

---

**Q2: What is the difference between HashSet, LinkedHashSet, and TreeSet?**

_Why they ask:_ Tests knowledge of Set implementation trade-offs.

**Answer:**

| Aspect       | HashSet   | LinkedHashSet | TreeSet      |
| ------------ | --------- | ------------- | ------------ |
| Order        | None      | Insertion     | Sorted       |
| Backed by    | HashMap   | LinkedHashMap | TreeMap      |
| add/contains | O(1)      | O(1)          | O(log n)     |
| Memory       | Lowest    | +linked list  | +tree nodes  |
| Null         | 1 allowed | 1 allowed     | No (natural) |

**Decision framework:**

- **Default choice:** HashSet (fastest, lowest memory)
- **Need insertion order:** LinkedHashSet (e.g., ordered dedup)
- **Need sorted iteration or range operations:** TreeSet
- **Need concurrent access:** `ConcurrentHashMap.newKeySet()` or `ConcurrentSkipListSet`

```java
// Preserves order of first occurrence
Set<String> ordered =
    new LinkedHashSet<>(listWithDups);

// Sorted unique values
Set<Integer> sorted =
    new TreeSet<>(listOfNumbers);
sorted.subSet(10, 20); // range query
```

---

**Q3: How would you create a thread-safe Set in Java?**

_Why they ask:_ Tests concurrent programming knowledge.

**Answer:**
Four approaches, each with trade-offs:

1. **`Collections.synchronizedSet()`** - wraps any Set with synchronized methods:

   ```java
   Set<String> set = Collections.synchronizedSet(
       new HashSet<>());
   ```

   Problem: compound operations (check-then-act) are not atomic. Iteration requires manual synchronization.

2. **`ConcurrentHashMap.newKeySet()`** (Java 8+) - best general choice:

   ```java
   Set<String> set =
       ConcurrentHashMap.newKeySet();
   ```

   Per-bucket locking, weakly consistent iteration, no null elements.

3. **`CopyOnWriteArraySet`** - copies on every write:

   ```java
   Set<String> set =
       new CopyOnWriteArraySet<>();
   ```

   Perfect for small sets with rare writes (observer lists). Terrible for large or write-heavy sets.

4. **`ConcurrentSkipListSet`** - concurrent sorted set:
   ```java
   Set<String> set =
       new ConcurrentSkipListSet<>();
   ```
   O(log n), sorted, concurrent. Use when you need both thread safety and sorted access.

For most production use cases, `ConcurrentHashMap.newKeySet()` is the right answer.

---

**Q4: How would you efficiently find the intersection of two large sets (millions of elements each)?**

_Why they ask:_ Tests algorithm thinking with real data structures.

**Answer:**
Iterate over the smaller set and check membership in the larger:

```java
public static <T> Set<T> intersect(
        Set<T> a, Set<T> b) {
    // Always iterate the smaller set
    Set<T> smaller = a.size() <= b.size() ? a : b;
    Set<T> larger = a.size() > b.size() ? a : b;

    Set<T> result = new HashSet<>(
        Math.min(smaller.size(), 1024));
    for (T element : smaller) {
        if (larger.contains(element)) {
            result.add(element);
        }
    }
    return result;
}
```

Time complexity: O(min(|a|, |b|)) since `contains()` is O(1) on HashSet.

For parallel processing of very large sets:

```java
Set<T> result = smaller.parallelStream()
    .filter(larger::contains)
    .collect(Collectors.toSet());
```

If sets are too large for memory, use a Bloom filter for approximate intersection testing, or sort both sets and do a merge-intersection in O(n + m) with streaming I/O.

---

**Q5: What happens if you put a mutable object in a HashSet and then modify it?**

_Why they ask:_ Tests understanding of a common production bug.

**Answer:**
The object becomes unreachable in the set. Its hashCode changes, but it's still stored in the bucket corresponding to the old hashCode. Neither `contains()` nor `remove()` can find it.

```java
List<String> list = new ArrayList<>(
    List.of("a", "b"));
Set<List<String>> set = new HashSet<>();
set.add(list);

set.contains(list);  // true
list.add("c");        // mutate!
set.contains(list);  // false - hash changed
set.remove(list);    // false - can't find it

// The entry is orphaned in the set
// It still counts toward size()
// It will appear during iteration
// But it can never be found by contains/remove
```

This is a memory leak. The object is referenced by the set (preventing GC) but cannot be found or removed through the API.

**Prevention rules:**

1. Only use immutable objects as Set elements (and Map keys)
2. Use `Set.of()`, records, or value objects
3. If you must use mutable elements, never modify them while they're in a set

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for HashSet. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

---

---

# Queue and Deque

**TL;DR** - Queue provides FIFO ordering and Deque extends it with double-ended operations, and choosing between `LinkedList`, `ArrayDeque`, and `PriorityQueue` determines whether you optimize for flexibility, performance, or ordering.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You need to process incoming requests in order. With a List, you `add()` at the end and `remove(0)` from the front. But `remove(0)` on ArrayList shifts every element - O(n). With LinkedList used as a List, you lose type safety that enforces FIFO discipline. Any developer can accidentally `get(5)` and break the ordering guarantee.

**THE BREAKING POINT:**
A message processing system uses `ArrayList.remove(0)` to dequeue messages. At 50K messages, dequeue takes 0.5ms. At 500K, it takes 5ms. The processing pipeline falls behind, messages back up, and the system runs out of memory.

**THE INVENTION MOMENT:**
"This is exactly why Queue and Deque were created."

**EVOLUTION:**
Java 1.2 had only `LinkedList`. Java 5 introduced the `Queue` interface and `PriorityQueue`. Java 6 added `Deque` (double-ended queue) and `ArrayDeque`. Java 5 also added `java.util.concurrent` queues: `BlockingQueue`, `ConcurrentLinkedQueue`, `LinkedBlockingQueue`, and `ArrayBlockingQueue`.

---

### Textbook Definition

`Queue` is a `Collection` subinterface modeling a FIFO (first-in, first-out) data structure with operations for insertion (`offer`/`add`), removal (`poll`/`remove`), and inspection (`peek`/`element`). `Deque` (double-ended queue) extends `Queue` to support insertion and removal at both ends. Implementations include `ArrayDeque` (resizable array, fastest general-purpose), `LinkedList` (doubly-linked list, implements both `List` and `Deque`), and `PriorityQueue` (binary heap, elements dequeued by priority).

---

### Understand It in 30 Seconds

**One line:**
A line where people join at the back and leave from the front.

**One analogy:**

> Think of a grocery store checkout line. New customers join at the back (enqueue). The cashier serves whoever's at the front (dequeue). A Deque is like a line where people can also join or leave from the front - think of a VIP lane.

**One insight:**
The critical decision is implementation choice. `ArrayDeque` is faster than `LinkedList` for both Queue and Stack use cases due to cache locality. `PriorityQueue` isn't FIFO at all - it's a min-heap that always dequeues the smallest element. Knowing which to pick is the real skill.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Queue: FIFO - first element added is first removed
2. Deque: Elements can be added/removed from either end
3. The interface distinguishes "throw exception" vs "return special value" for each operation

**DERIVED DESIGN:**
The dual-method design (`add`/`offer`, `remove`/`poll`, `element`/`peek`) exists because queues are often used in bounded-capacity scenarios. `offer()` returns false when full; `add()` throws. This lets the caller choose error handling strategy.

**THE TRADE-OFFS:**
**Gain:** Enforced ordering discipline, efficient operations at both ends
**Cost:** No random access by index (unlike List), limited API surface

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** FIFO ordering requires maintaining insertion order and providing efficient head removal - either circular array or linked nodes.
**Accidental:** Java having both `Queue` and `Deque` interfaces (when Deque can do everything Queue can) adds cognitive overhead.

---

### Mental Model / Analogy

> A conveyor belt in a factory: items are placed on one end and taken off the other end in the same order they were placed. A Deque is a conveyor belt that can run in both directions.

- "Place item on belt" -> `offer()` / `add()`
- "Take item off belt" -> `poll()` / `remove()`
- "Look at next item without taking" -> `peek()`
- "Belt capacity" -> bounded queue limit
- "Belt running both ways" -> Deque operations

Where this analogy breaks down: PriorityQueue doesn't follow conveyor order - it's more like a sorting machine that always outputs the smallest item.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A Queue is a line - first in, first out. A Deque (pronounced "deck") lets you add or remove from either end. Java gives you several implementations optimized for different scenarios.

**Level 2 - How to use it (junior developer):**
Use `ArrayDeque` as your default Queue and Stack implementation. `offer(e)` to add, `poll()` to remove and get (returns null if empty), `peek()` to look without removing. For priority ordering, use `PriorityQueue`. For thread-safe queues, use `ConcurrentLinkedQueue` or `BlockingQueue` implementations.

**Level 3 - How it works (mid-level engineer):**
`ArrayDeque` uses a circular array with `head` and `tail` pointers. Adding to the tail increments `tail % array.length`. Removing from the head increments `head % array.length`. When head meets tail, the array doubles and elements are copied. This gives O(1) amortized add/remove at both ends with excellent cache locality. `PriorityQueue` uses a binary min-heap: insert bubbles up (O(log n)), remove-min swaps root with last and sifts down (O(log n)).

**Level 4 - Mastery (senior/staff+ engineer):**
ArrayDeque outperforms LinkedList for all queue/stack operations because of cache locality - the circular array fits in CPU cache lines while LinkedList nodes are scattered across the heap. The only remaining use case for LinkedList as a Deque is when you need to remove elements from the middle during iteration (ListIterator.remove()). For concurrent producer-consumer patterns, `LinkedBlockingQueue` (separate locks for head and tail) outperforms `ArrayBlockingQueue` (single lock) when producers and consumers operate at similar rates. For single-producer/single-consumer, `Disruptor` or `JCTools` SPSCQueue achieve 100M+ ops/sec by eliminating locks entirely.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
ArrayDeque circular buffer:

  [_, _, C, D, E, F, _, _]
         ^           ^
         head        tail

  offer("G"):
    array[tail] = "G"
    tail = (tail + 1) & (length - 1)

  [_, _, C, D, E, F, G, _]
         ^              ^
         head           tail

  poll():  // returns "C"
    result = array[head]
    array[head] = null
    head = (head + 1) & (length - 1)

  [_, _, _, D, E, F, G, _]
            ^           ^
            head        tail

  Wrap-around:
  [H, I, _, _, _, F, G, _]
         ^        ^
         tail     head
  (head > tail = wrapped around)
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Producer: offer(element)
  -> element added at tail  <- YOU ARE HERE
  -> tail pointer advances
Consumer: poll()
  -> element removed from head
  -> head pointer advances
  -> process element
```

**FAILURE PATH:**

```
Unbounded queue + slow consumer
  -> Queue grows without limit
  -> Memory exhaustion -> OutOfMemoryError
  -> Fix: use bounded queue (ArrayBlockingQueue)
     with backpressure
```

**WHAT CHANGES AT SCALE:**
At high throughput, the choice between queue implementations becomes critical. ArrayDeque resizes by doubling (copies all elements). For millions of ops/sec, lock-free queues (`ConcurrentLinkedQueue`) or bounded ring buffers avoid this overhead. At 10M+ msgs/sec, even ConcurrentLinkedQueue's CAS contention becomes the bottleneck - specialized libraries like LMAX Disruptor or JCTools are required.

---

### Code Example

**Example 1 - Queue implementation choice**

```java
// BAD: using LinkedList as Queue
Queue<Task> queue = new LinkedList<>();
queue.offer(task);  // works but slow
Task next = queue.poll();
// LinkedList: poor cache locality,
// 48 bytes overhead per node

// GOOD: use ArrayDeque
Queue<Task> queue = new ArrayDeque<>();
queue.offer(task);  // O(1), cache-friendly
Task next = queue.poll();
// ArrayDeque: contiguous array, minimal overhead
```

**Example 2 - Using Deque as Stack**

```java
// BAD: using java.util.Stack (legacy, synchronized)
Stack<String> stack = new Stack<>();
stack.push("a");
String top = stack.pop();
// Stack extends Vector - unnecessary sync overhead

// GOOD: use ArrayDeque as Stack
Deque<String> stack = new ArrayDeque<>();
stack.push("a");     // addFirst
String top = stack.pop();  // removeFirst
// Faster, no sync overhead
```

**Example 3 - PriorityQueue for task scheduling**

```java
PriorityQueue<Task> pq = new PriorityQueue<>(
    Comparator.comparingInt(Task::priority));
pq.offer(new Task("backup", 3));
pq.offer(new Task("alert", 1));  // highest prio
pq.offer(new Task("report", 2));

// Dequeues in priority order: alert, report, backup
while (!pq.isEmpty()) {
    process(pq.poll());
}
```

**How to test / verify correctness:**
Verify FIFO order with sequential offer/poll, test empty queue returns null from `poll()`, verify PriorityQueue ordering with a custom Comparator, and test boundary behavior when ArrayDeque resizes.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Use `ArrayDeque` as your default Queue AND Stack - faster than LinkedList and Stack in every benchmark
2. `offer()`/`poll()`/`peek()` return special values; `add()`/`remove()`/`element()` throw exceptions
3. PriorityQueue is NOT FIFO - it's a min-heap that dequeues the smallest element first

**Interview one-liner:**
"For Queue and Stack, I always use ArrayDeque - it's a circular array with O(1) operations at both ends and excellent cache locality. PriorityQueue is for ordered processing using a binary heap. For concurrent scenarios, I choose between LinkedBlockingQueue and ConcurrentLinkedQueue based on whether I need blocking semantics."

---

### The Surprising Truth

Java's `Stack` class is universally considered a design mistake. It extends `Vector` (synchronized array), which means every push/pop acquires a lock even in single-threaded code. Worse, because it extends `Vector`, you can call `get(3)` on a Stack - breaking the LIFO abstraction entirely. The official Javadoc for `Stack` says: "A more complete and consistent set of LIFO stack operations is provided by the Deque interface." Yet `Stack` cannot be deprecated because too much legacy code depends on it.

---

### Interview Deep-Dive

**Q1: What's the difference between `offer()` and `add()` on a Queue?**

_Why they ask:_ Tests understanding of the dual-API design.

**Answer:**
Both insert an element, but they differ in failure behavior:

| Method     | Success      | Failure (queue full)           |
| ---------- | ------------ | ------------------------------ |
| `add(e)`   | returns true | throws `IllegalStateException` |
| `offer(e)` | returns true | returns false                  |

The same pattern applies to removal and inspection:

| Operation | Throws      | Returns special value   |
| --------- | ----------- | ----------------------- |
| Insert    | `add(e)`    | `offer(e)`              |
| Remove    | `remove()`  | `poll()` (returns null) |
| Examine   | `element()` | `peek()` (returns null) |

In practice, `offer`/`poll`/`peek` are preferred because they allow graceful handling of boundary conditions. `add`/`remove`/`element` are inherited from the Collection interface and useful when the queue should never be full or empty in normal operation (exceptions signal bugs, not expected conditions).

For bounded queues (`ArrayBlockingQueue`), `offer()` is essential:

```java
BlockingQueue<Task> q =
    new ArrayBlockingQueue<>(100);
if (!q.offer(task)) {
    // Queue full - apply backpressure
    metrics.increment("queue.rejected");
    fallbackStrategy(task);
}
```

---

**Q2: Why should you prefer ArrayDeque over LinkedList for Queue operations?**

_Why they ask:_ Tests practical performance knowledge.

**Answer:**
ArrayDeque beats LinkedList in every queue/deque benchmark for three reasons:

1. **Cache locality:** ArrayDeque stores elements in a contiguous array. When you access one element, adjacent elements are already in the CPU cache line. LinkedList nodes are scattered across the heap - every `.next` traversal is a cache miss.

2. **Memory efficiency:** ArrayDeque has zero per-element overhead (just array slots). LinkedList has ~48 bytes per node: prev pointer (8), next pointer (8), element reference (8), object header (16), padding.

3. **Allocation pressure:** ArrayDeque allocates one array and resizes occasionally. LinkedList allocates a new Node object for every `offer()` and makes it garbage on every `poll()` - constant GC pressure.

Benchmark data (JMH, 1M operations):

```
ArrayDeque.offer+poll: ~25 ns/op
LinkedList.offer+poll: ~50-80 ns/op
```

The only case where LinkedList wins: when you need to remove elements from the middle during iteration using `ListIterator.remove()`. ArrayDeque doesn't implement `List` and doesn't support efficient mid-removal.

---

**Q3: Design a task queue with priority levels that supports concurrent producers and a single consumer.**

_Why they ask:_ Tests ability to combine queue knowledge with concurrency and design.

**Answer:**
Use a `PriorityBlockingQueue` with a priority-aware task wrapper:

```java
public class PriorityTaskQueue {
    private final PriorityBlockingQueue<PriTask>
        queue = new PriorityBlockingQueue<>();

    record PriTask(int priority, long seq,
            Runnable task)
            implements Comparable<PriTask> {
        public int compareTo(PriTask o) {
            int p = Integer.compare(
                priority, o.priority);
            return p != 0 ? p
                : Long.compare(seq, o.seq);
        }
    }

    private final AtomicLong seq =
        new AtomicLong();

    public void submit(int prio, Runnable task) {
        queue.offer(new PriTask(
            prio, seq.getAndIncrement(), task));
    }

    public void consume() { // single consumer
        while (!Thread.currentThread()
                       .isInterrupted()) {
            PriTask t = queue.take(); // blocks
            t.task().run();
        }
    }
}
```

Design decisions:

- **Sequence number tiebreaker:** Same-priority tasks are processed in FIFO order (arrival order). Without this, PriorityQueue doesn't guarantee FIFO among equal priorities.
- **`PriorityBlockingQueue`:** Thread-safe, unbounded, `take()` blocks when empty - no busy-waiting.
- **Single consumer:** Avoids out-of-order processing within a priority level.

For bounded backpressure, wrap with a semaphore or use a custom bounded priority queue.

---

**Q4: What is a blocking queue and when would you use one?**

_Why they ask:_ Tests understanding of producer-consumer patterns.

**Answer:**
A `BlockingQueue` extends `Queue` with operations that wait:

- `put(e)` - blocks if queue is full (until space available)
- `take()` - blocks if queue is empty (until element available)

This eliminates busy-waiting in producer-consumer patterns:

```java
BlockingQueue<Event> queue =
    new LinkedBlockingQueue<>(1000);

// Producer thread
executor.submit(() -> {
    while (running) {
        Event e = receiveFromNetwork();
        queue.put(e); // blocks if full
    }
});

// Consumer thread
executor.submit(() -> {
    while (running) {
        Event e = queue.take(); // blocks if empty
        process(e);
    }
});
```

**Implementation choices:**

| Implementation      | Bounded    | Lock            | Best for        |
| ------------------- | ---------- | --------------- | --------------- |
| ArrayBlockingQueue  | Yes        | Single          | Simple bounded  |
| LinkedBlockingQueue | Optional   | Two (head+tail) | High throughput |
| SynchronousQueue    | 0 capacity | -               | Direct handoff  |
| DelayQueue          | No         | Single          | Scheduled tasks |

Key insight: `LinkedBlockingQueue` uses separate locks for `put()` and `take()`, allowing concurrent producers and consumers. `ArrayBlockingQueue` uses a single lock, so put and take can't run simultaneously. For high-throughput producer-consumer, `LinkedBlockingQueue` is typically faster.

---

**Q5: Explain the difference between `ConcurrentLinkedQueue` and `LinkedBlockingQueue`.**

_Why they ask:_ Tests nuanced understanding of concurrent queue options.

**Answer:**

| Aspect    | ConcurrentLinkedQueue | LinkedBlockingQueue |
| --------- | --------------------- | ------------------- |
| Blocking  | No                    | Yes (put/take)      |
| Bounded   | No                    | Optional            |
| Algorithm | Lock-free (CAS)       | Lock-based          |
| `size()`  | O(n) traversal        | O(1) counter        |
| Best for  | Non-blocking          | Producer-consumer   |

**ConcurrentLinkedQueue:** Uses lock-free CAS operations. `offer()` and `poll()` never block. `size()` is O(n) because maintaining an atomic counter would add contention. Best for scenarios where threads should never wait: event buses, work-stealing queues.

**LinkedBlockingQueue:** Uses `ReentrantLock`s (separate for head and tail). `put()` blocks when capacity is reached. `take()` blocks when empty. Maintains an `AtomicInteger` count for O(1) `size()`. Best for classic producer-consumer where you want threads to sleep when there's no work.

Decision: "Can my producer afford to spin or skip when the queue is full?" If yes: `ConcurrentLinkedQueue`. If no (must process every item): `LinkedBlockingQueue` with bounded capacity.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Queue and Deque. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

---

---

# Iterator and Iterable

**TL;DR** - Iterable marks a collection as for-each-loopable, Iterator provides the actual traversal logic, and understanding this contract lets you write custom data sources that plug into Java's entire collection ecosystem.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every collection has its own way to traverse: arrays use index loops, linked lists follow pointers, trees do recursive walks. Client code must know the internal structure of each collection to iterate. Changing from ArrayList to TreeSet requires rewriting every loop.

**THE BREAKING POINT:**
A library exposes a custom data structure. Users must learn its proprietary traversal API. When the library changes internal representation, all client code breaks. There's no way to write a generic "process every element" method that works on any collection.

**THE INVENTION MOMENT:**
"This is exactly why Iterator and Iterable were created."

**EVOLUTION:**
Java 1.0 had `Enumeration` with `hasMoreElements()`/`nextElement()`. Java 1.2 replaced it with `Iterator` (simpler names, added `remove()`). Java 5 introduced the enhanced for-each loop (`for (T item : collection)`) which requires `Iterable`. Java 8 added `Iterable.forEach()` and `Iterator.forEachRemaining()`, plus `Spliterator` for parallel streams.

---

### Textbook Definition

`Iterable<T>` is a functional interface with one method, `iterator()`, that returns an `Iterator<T>`. Any class implementing `Iterable` can be used in Java's enhanced for-each loop. `Iterator<T>` is a stateful cursor with `hasNext()`, `next()`, and optionally `remove()`. Together they implement the Iterator design pattern, decoupling traversal logic from collection internals and providing a uniform interface for sequential element access.

---

### Understand It in 30 Seconds

**One line:**
Iterable says "I can be looped over," Iterator does the actual looping.

**One analogy:**

> Think of a book (Iterable) and a bookmark (Iterator). The book says "you can read me page by page." The bookmark tracks where you are, moves forward on request, and tells you when you've reached the end.

**One insight:**
The for-each loop `for (String s : list)` is syntactic sugar. The compiler converts it to: `Iterator<String> it = list.iterator(); while (it.hasNext()) { String s = it.next(); }`. Understanding this transformation explains why you can't modify a collection during for-each and why your own classes can participate.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Iterable produces a fresh Iterator on each `iterator()` call
2. Iterator is forward-only, single-use (no reset)
3. `hasNext()` is idempotent - calling it multiple times doesn't advance
4. `next()` advances the cursor and returns the current element

**DERIVED DESIGN:**
Separating "I am iterable" (Iterable) from "I am iterating" (Iterator) allows multiple independent traversals of the same collection. Each `iterator()` call creates a new cursor at the beginning.

**THE TRADE-OFFS:**
**Gain:** Uniform traversal, collection-agnostic code, for-each support, custom data source integration
**Cost:** Forward-only (no backtracking without ListIterator), one-element-at-a-time (no batch access)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any sequential traversal needs state (current position) - Iterator provides this.
**Accidental:** Java's `remove()` on Iterator is optional and error-prone - many developers don't know it exists or when it's safe to call.

---

### Mental Model / Analogy

> A TV remote (Iterator) and a TV channel list (Iterable). The channel list says "you can browse me." The remote has "next channel" and "is there another channel?" buttons. Each person gets their own remote, so multiple viewers can browse independently.

- "Channel list" -> Iterable (the data source)
- "Remote control" -> Iterator (the cursor)
- "Next channel button" -> `next()`
- "Is there another channel?" -> `hasNext()`
- "Each person gets their own remote" -> `iterator()` returns a new Iterator

Where this analogy breaks down: TV remotes can go backward; standard Java Iterators cannot.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Iterable is a promise: "you can go through my items one by one." Iterator is the mechanism that actually steps through them. Together, they let Java's for-each loop work on any collection.

**Level 2 - How to use it (junior developer):**
Any class implementing `Iterable<T>` works with for-each. Use `iterator()` explicitly when you need `remove()` during traversal. Never call `next()` without checking `hasNext()` first. Never modify a collection during for-each - use `iterator.remove()` or `removeIf()` instead.

**Level 3 - How it works (mid-level engineer):**
For-each is compiler sugar: `for (T x : iterable)` becomes `Iterator<T> it = iterable.iterator(); while (it.hasNext()) { T x = it.next(); }`. ArrayList's Iterator stores an index cursor and checks `modCount` for fail-fast behavior. LinkedList's Iterator stores a node reference. TreeMap's Iterator does in-order successor traversal. Each implementation hides its internal structure behind the same interface.

**Level 4 - Mastery (senior/staff+ engineer):**
Iterable is a functional interface (`@FunctionalInterface`), meaning you can use lambdas: `Iterable<String> lines = () -> scanner;` wraps any Iterator in an Iterable. `Spliterator` (Java 8) extends the concept for parallel traversal - it can `trySplit()` to divide work across threads. Custom Iterators over I/O sources (database cursors, file lines, network streams) enable lazy evaluation that processes billions of records without loading them all into memory. The key architectural pattern: write methods that accept `Iterable<T>` instead of `List<T>` to keep APIs collection-agnostic.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works

```
for-each desugaring:

  // What you write:
  for (String s : list) {
      System.out.println(s);
  }

  // What the compiler generates:
  Iterator<String> it = list.iterator();
  while (it.hasNext()) {
      String s = it.next();
      System.out.println(s);
  }

  ArrayList.Iterator internals:
  +---+---+---+---+---+
  | A | B | C | D | E |
  +---+---+---+---+---+
    ^
    cursor = 0

  next() -> returns "A", cursor = 1
  next() -> returns "B", cursor = 2
  hasNext() -> cursor < size? true
  ...
  next() -> returns "E", cursor = 5
  hasNext() -> 5 < 5? false -> done
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
for (T item : collection)
  -> compiler: collection.iterator()
  -> new Iterator created <- YOU ARE HERE
  -> while hasNext(): call next()
  -> process each element
  -> Iterator becomes garbage (GC)
```

**FAILURE PATH:**

```
Collection modified during iteration
  (not via iterator.remove())
  -> modCount != expectedModCount
  -> ConcurrentModificationException
```

**WHAT CHANGES AT SCALE:**
For large collections, Iterator's one-element-at-a-time model becomes a bottleneck. Java 8's Spliterator addresses this: it can split the data source in half for parallel processing. A 10M-element collection can be split into chunks processed by different threads via `parallelStream()`, which uses Spliterator internally.

---

### Code Example

**Example 1 - Custom Iterable**

```java
// Making a custom class work with for-each
public class NumberRange implements Iterable<Integer> {
    private final int start, end;

    public NumberRange(int start, int end) {
        this.start = start;
        this.end = end;
    }

    @Override
    public Iterator<Integer> iterator() {
        return new Iterator<>() {
            private int current = start;

            public boolean hasNext() {
                return current <= end;
            }

            public Integer next() {
                if (!hasNext()) throw
                    new NoSuchElementException();
                return current++;
            }
        };
    }
}

// Usage - works with for-each!
for (int n : new NumberRange(1, 10)) {
    System.out.println(n);
}
```

**Example 2 - Safe removal during iteration**

```java
// BAD: ConcurrentModificationException
List<String> items = new ArrayList<>(
    List.of("keep", "remove", "keep"));
for (String item : items) {
    if (item.equals("remove")) {
        items.remove(item); // throws CME!
    }
}

// GOOD: Iterator.remove()
Iterator<String> it = items.iterator();
while (it.hasNext()) {
    if (it.next().equals("remove")) {
        it.remove(); // safe
    }
}

// BETTER: removeIf (Java 8+)
items.removeIf(s -> s.equals("remove"));
```

**How to test / verify correctness:**
Test that your custom Iterable supports multiple independent iterations, that `hasNext()` is idempotent, that `next()` throws `NoSuchElementException` when exhausted, and that for-each loop works correctly.

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. For-each is compiler sugar for `iterator()` + `hasNext()` + `next()` - knowing this explains every for-each behavior
2. Implement `Iterable<T>` on your class to make it work with for-each loops
3. Never modify a collection during for-each - use `iterator.remove()` or `removeIf()` instead

**Interview one-liner:**
"Iterable produces an Iterator via iterator() - this is what enables for-each loops. The compiler desugars for-each into hasNext/next calls. Each iterator() call returns a fresh cursor, allowing independent concurrent traversals of the same collection."

---

### The Surprising Truth

`Iterable` is a `@FunctionalInterface` with a single abstract method (`iterator()`). This means you can create an Iterable with a lambda: `Iterable<String> words = () -> scanner;` wraps any Iterator in an Iterable. This trick is particularly powerful for adapting I/O sources (Scanners, BufferedReaders, database result sets) to work with for-each loops without writing a full class.

---

### Interview Deep-Dive

**Q1: What is the difference between Iterable and Iterator? Why are they separate interfaces?**

_Why they ask:_ Tests understanding of the design rationale.

**Answer:**
`Iterable` is the _source_ - it says "I can produce a way to traverse my elements." It has one method: `iterator()`.

`Iterator` is the _cursor_ - it tracks position and provides `hasNext()`, `next()`, and `remove()`.

They're separate because of the **multiple traversal requirement.** If a collection was itself the iterator (tracking position), only one loop could traverse it at a time. By separating them:

```java
List<String> list = List.of("a", "b", "c");

// Two independent traversals of the same list
Iterator<String> it1 = list.iterator();
Iterator<String> it2 = list.iterator();

it1.next(); // "a"
it2.next(); // "a" - independent cursor!
it1.next(); // "b"
```

Each `iterator()` call creates a fresh cursor. This enables nested loops over the same collection, concurrent iteration from different threads, and separation of "what to traverse" from "how far along."

This is the classic GoF Iterator pattern: separate the traversal algorithm from the aggregate object.

---

**Q2: How does the fail-fast mechanism work in Java iterators?**

_Why they ask:_ Tests understanding of ConcurrentModificationException.

**Answer:**
Every modifiable collection maintains an `int modCount` that increments on structural modifications (add, remove, clear - not `set()`). When an iterator is created, it snapshots this value as `expectedModCount`.

On every `next()` call, the iterator checks:

```java
if (modCount != expectedModCount)
    throw new ConcurrentModificationException();
```

The name is misleading - this is not about threads. It detects modification "concurrent with iteration," which happens in single-threaded code too:

```java
for (String s : list) {
    list.add("new"); // modCount changes
    // next iteration: CME!
}
```

**Why fail-fast, not fail-safe?**
The alternative (ignoring modifications) leads to undefined behavior: skipped elements, duplicates, `ArrayIndexOutOfBoundsException`. Failing immediately is safer.

**Truly concurrent (multi-threaded) scenarios:**
Fail-fast is best-effort, not guaranteed. The `modCount` check is not synchronized. Under true concurrency, you might not get CME but instead see corrupted data. For thread-safe iteration, use:

- `CopyOnWriteArrayList` (snapshot iterator)
- `ConcurrentHashMap` (weakly consistent iterator)
- External synchronization

---

**Q3: How would you implement a lazy Iterator that reads from a database cursor without loading all rows into memory?**

_Why they ask:_ Tests ability to apply Iterator pattern to real-world I/O.

**Answer:**
Wrap the JDBC `ResultSet` in an Iterator:

```java
public class ResultSetIterator
        implements Iterator<Row>, AutoCloseable {
    private final ResultSet rs;
    private boolean hasNext;

    public ResultSetIterator(ResultSet rs)
            throws SQLException {
        this.rs = rs;
        this.hasNext = rs.next(); // prefetch first
    }

    public boolean hasNext() {
        return hasNext;
    }

    public Row next() {
        if (!hasNext)
            throw new NoSuchElementException();
        try {
            Row row = mapRow(rs);
            hasNext = rs.next(); // prefetch next
            return row;
        } catch (SQLException e) {
            throw new UncheckedSQLException(e);
        }
    }

    public void close() throws SQLException {
        rs.close();
    }
}
```

Key design decisions:

1. **Prefetch one row:** `hasNext()` must be idempotent (no side effects), so we advance the cursor in the constructor and after each `next()`, storing the result.
2. **Wrap checked exceptions:** Iterator's `next()` doesn't declare checked exceptions. Wrap `SQLException` in an unchecked wrapper.
3. **Resource management:** Implement `AutoCloseable` so the cursor can be used in try-with-resources.

Usage pattern:

```java
try (var it = new ResultSetIterator(rs)) {
    while (it.hasNext()) {
        process(it.next()); // one row in memory
    }
}
```

This processes millions of rows with constant memory - only one row is loaded at a time. The key constraint is that `ResultSet` is forward-only, which maps perfectly to Iterator's forward-only contract.

---

**Q4: What is a Spliterator and how does it relate to Iterator?**

_Why they ask:_ Tests knowledge of Java 8's parallel infrastructure.

**Answer:**
`Spliterator` (splittable iterator) is Java 8's evolution of Iterator for parallel processing. Key differences:

| Aspect          | Iterator     | Spliterator                  |
| --------------- | ------------ | ---------------------------- |
| Direction       | Forward-only | Forward-only                 |
| Parallelism     | No           | Yes (trySplit)               |
| Bulk ops        | No           | tryAdvance, forEachRemaining |
| Size info       | No           | estimateSize()               |
| Characteristics | None         | ORDERED, SIZED, etc.         |

The critical method is `trySplit()`: it splits the remaining elements roughly in half, returning a new Spliterator for the first half while retaining the second half. This enables the ForkJoinPool to divide work across threads:

```
Original Spliterator: [1, 2, 3, 4, 5, 6, 7, 8]
  trySplit() ->
    Returns: [1, 2, 3, 4]  (Thread A)
    Retains: [5, 6, 7, 8]  (Thread B)
```

`parallelStream()` uses this internally:

```java
list.parallelStream()
    .filter(...)
    .collect(...);
// Uses list's Spliterator to divide work
```

Characteristics (bit flags) help the stream pipeline optimize:

- `SIZED`: exact size known - pre-allocate results
- `ORDERED`: order matters - preserve encounter order
- `SORTED`: already sorted - skip sorting step
- `DISTINCT`: no duplicates - skip dedup

Custom Spliterators enable parallel processing of non-collection sources (files, I/O, generators).

---

**Q5: Can you use for-each on an array? How does that work if arrays don't implement Iterable?**

_Why they ask:_ Tests understanding of a subtle language detail.

**Answer:**
Yes, arrays work with for-each, but not through `Iterable`. The Java compiler treats arrays as a special case:

```java
// What you write:
for (int n : numbers) { ... }

// For arrays, compiler generates index loop:
for (int i = 0; i < numbers.length; i++) {
    int n = numbers[i];
    ...
}

// For Iterables, compiler generates:
Iterator<T> it = iterable.iterator();
while (it.hasNext()) {
    T item = it.next();
    ...
}
```

Arrays can't implement interfaces - they're a special JVM type, not a class. The language spec (JLS 14.14.2) explicitly states that for-each works for both `Iterable` and array types, using different desugaring for each.

This means you can't pass an array to a method expecting `Iterable<T>`:

```java
void process(Iterable<String> data) { ... }

String[] arr = {"a", "b"};
process(arr);  // COMPILE ERROR
process(List.of(arr));  // works
```

Key insight: this is a language-level special case, not a type system relationship. It's one of the few places where Java's grammar treats arrays differently from objects.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Iterator and Iterable. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]
