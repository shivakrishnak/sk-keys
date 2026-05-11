#!/usr/bin/env python3
"""
Pass 2: Fill remaining TODO sections (misconceptions, failures,
related keywords) using regex matching to handle whitespace variations.
"""

import re

FILE = "interview/java/Java - Collections.md"

KEYWORDS_ORDER = [
    "ArrayList", "HashMap", "TreeMap",
    "HashSet", "Queue and Deque", "Iterator and Iterable",
]

MISCONCEPTIONS = {
    "ArrayList": [
        ("LinkedList is faster for insertions",
         "Only at a known node position. Finding the node is O(n), "
         "and cache misses make LinkedList 5-10x slower than "
         "ArrayList for most real workloads."),
        ("ArrayList capacity equals size",
         "Capacity is the internal array length; size is the "
         "number of elements. `new ArrayList<>(100)` allocates "
         "space for 100 but `size()` is 0."),
        ("`trimToSize()` should be called after every removal",
         "Shrinking the array copies all elements. Only call when "
         "the list is finalized and memory matters."),
        ("`Collections.synchronizedList()` makes it fully "
         "thread-safe",
         "Individual operations are synchronized, but compound "
         "operations (iterate-then-modify) still need external "
         "locking. Use `CopyOnWriteArrayList` for read-heavy "
         "concurrent access."),
    ],
    "HashMap": [
        ("HashMap maintains insertion order",
         "HashMap makes no ordering guarantees. Use "
         "`LinkedHashMap` for insertion order or `TreeMap` for "
         "sorted order."),
        ("`hashCode()` alone determines the bucket",
         "HashMap applies a secondary spread function "
         "`h ^ (h >>> 16)` to reduce collisions from poor "
         "`hashCode()` implementations."),
        ("HashMap handles concurrent access with external sync",
         "External `synchronized` blocks work but are coarse-"
         "grained. `ConcurrentHashMap` uses fine-grained striped "
         "locking for 10-100x better throughput."),
        ("HashMap always uses linked lists for collisions",
         "Since Java 8, buckets with 8+ collisions treeify into "
         "red-black trees (O(log n) worst case), preventing "
         "hash-flooding DoS from degrading to O(n)."),
    ],
    "TreeMap": [
        ("TreeMap is always slower than HashMap",
         "For range queries, floor/ceiling, and sorted iteration, "
         "TreeMap is faster because HashMap would require "
         "collecting and sorting all entries."),
        ("TreeMap uses a plain binary search tree",
         "It uses a red-black tree (self-balancing BST). A plain "
         "BST degrades to O(n) with sorted insertions; red-black "
         "guarantees O(log n)."),
        ("Any object can be a TreeMap key",
         "Keys must implement `Comparable` or a `Comparator` "
         "must be provided. Otherwise `ClassCastException` at "
         "runtime."),
        ("TreeMap is a good choice for caching",
         "TreeMap has no size limit or eviction policy. For "
         "caching, use `LinkedHashMap` with `removeEldestEntry()` "
         "or Caffeine/Guava caches."),
    ],
    "HashSet": [
        ("HashSet maintains insertion order",
         "HashSet has no ordering guarantees. Use "
         "`LinkedHashSet` for insertion order or `TreeSet` for "
         "sorted order."),
        ("Two equal objects can exist in a HashSet",
         "Objects with the same `equals()` result occupy the same "
         "slot. But if `hashCode()` is broken (equal objects return "
         "different hashes), duplicates can appear."),
        ("HashSet is memory-efficient",
         "Each element costs ~48 bytes (HashMap.Node + dummy "
         "Object). For large primitive sets, use BitSet or "
         "primitive-specialized sets (fastutil)."),
        ("`set.remove(obj)` always works if obj was added",
         "If `obj` was mutated after adding (changing its "
         "`hashCode`), `remove()` cannot find it - same "
         "stranded-entry problem as HashMap."),
    ],
    "Queue and Deque": [
        ("`java.util.Stack` is the recommended stack",
         "`Stack` extends `Vector` (synchronized everything). Use "
         "`ArrayDeque` with `push()`/`pop()` instead - 5-10x "
         "faster."),
        ("LinkedList is better than ArrayDeque for queues",
         "ArrayDeque is faster due to cache locality. LinkedList "
         "creates a new Node object per element, causing GC "
         "pressure and cache misses."),
        ("PriorityQueue sorts elements on insertion",
         "PriorityQueue is a min-heap. Only the head is guaranteed "
         "minimum. Iteration order is NOT sorted - use `poll()` "
         "repeatedly to get sorted output."),
        ("Queue.add() and Queue.offer() are identical",
         "`add()` throws on a full bounded queue; `offer()` returns "
         "`false`. In production, prefer `offer()` to avoid "
         "exceptions in normal flow."),
    ],
    "Iterator and Iterable": [
        ("`for (T x : collection)` creates a copy",
         "For-each compiles to `Iterator` calls. No copy is made. "
         "Modifying the collection during iteration causes "
         "`ConcurrentModificationException`."),
        ("Iterator can be reused after reaching the end",
         "Iterators are single-pass. Once `hasNext()` returns "
         "false, you must obtain a new Iterator from the "
         "Iterable."),
        ("All Iterators are fail-fast",
         "Only modifiable-collection iterators (ArrayList, HashMap) "
         "are fail-fast. Concurrent collections use snapshot or "
         "weakly-consistent iterators."),
        ("Iterable and Iterator are the same thing",
         "`Iterable` has `iterator()` which creates a new "
         "`Iterator`. `Iterator` has `hasNext()`, `next()`, "
         "`remove()`. One creates, the other traverses."),
    ],
}

FAILURES = {
    "ArrayList": """**Failure Mode 1: ConcurrentModificationException during iteration**
**Symptom:** `ConcurrentModificationException` from `Iterator.next()` during for-each.
**Root Cause:** Modifying the list (add/remove) while iterating with a fail-fast iterator.
**Diagnostic:**

```
grep -n 'for.*:.*list' MyClass.java
# Find list.remove() or list.add() inside for-each
```

**Fix:**
```java
// BAD: modify during iteration
for (String s : list) {
    if (s.isEmpty()) list.remove(s);
}

// GOOD: use removeIf
list.removeIf(String::isEmpty);
```
**Prevention:** Use `removeIf()`, `Iterator.remove()`, or stream-filter-collect.

**Failure Mode 2: OutOfMemoryError from unbounded growth**
**Symptom:** `OutOfMemoryError: Java heap space` after hours/days of operation.
**Root Cause:** ArrayList used as buffer/log that grows without bound.
**Diagnostic:**

```
jmap -histo:live <pid> | head -20
# Look for Object[] with millions of instances
```

**Fix:**
```java
// BAD: unbounded accumulation
List<Event> events = new ArrayList<>();
void onEvent(Event e) { events.add(e); }

// GOOD: bounded with eviction
ArrayDeque<Event> events = new ArrayDeque<>();
void onEvent(Event e) {
    if (events.size() >= MAX) events.pollFirst();
    events.addLast(e);
}
```
**Prevention:** Always set size bounds on in-memory collections. Monitor collection sizes.

**Failure Mode 3: Latency spikes from resize-and-copy**
**Symptom:** Periodic latency spikes. `Arrays.copyOf` in profiler hot paths.
**Root Cause:** Default capacity (10) causes repeated resize when adding thousands of elements.
**Diagnostic:**

```
asprof -e alloc -d 30 -f alloc.html <pid>
# Look for Object[] from ArrayList.grow
```

**Fix:**
```java
// BAD: default capacity, many resizes
List<Row> rows = new ArrayList<>();

// GOOD: pre-size when count is known
List<Row> rows = new ArrayList<>(expectedCount);
```
**Prevention:** Pre-size lists when expected count is known. Use `ensureCapacity()` before bulk adds.""",

    "HashMap": """**Failure Mode 1: Lost entries from mutable keys**
**Symptom:** `map.get(key)` returns null for a key that was just inserted.
**Root Cause:** Key object mutated after insertion, changing its `hashCode()`. Entry is stranded in wrong bucket.
**Diagnostic:**

```
jshell> map.entrySet().stream()
  .filter(e -> e.getKey().equals(target))
  .count()
# If 0 but map.size() grew, key hash changed
```

**Fix:**
```java
// BAD: mutable key
List<String> key = new ArrayList<>();
map.put(key, "val");
key.add("oops"); // hashCode changed!

// GOOD: immutable key
String key = String.join(",", items);
map.put(key, "val");
```
**Prevention:** Only use immutable types as keys (String, Integer, Records, enums).

**Failure Mode 2: Infinite loop from concurrent modification**
**Symptom:** Thread hangs at 100% CPU. Thread dump shows `HashMap.get()` or `resize()` looping.
**Root Cause:** Two threads trigger simultaneous resize, creating circular linked list in a bucket.
**Diagnostic:**

```
jstack <pid> | grep -A 5 "HashMap"
# Threads stuck in HashMap.getNode or resize
```

**Fix:**
```java
// BAD: shared HashMap across threads
Map<String, Integer> shared = new HashMap<>();

// GOOD: use ConcurrentHashMap
Map<String, Integer> shared =
    new ConcurrentHashMap<>();
```
**Prevention:** Never share HashMap across threads. Use ConcurrentHashMap or thread-local maps.

**Failure Mode 3: Hash-flooding DoS attack**
**Symptom:** API latency spikes to seconds. CPU 100% in `HashMap.put()`.
**Root Cause:** Attacker crafts keys with identical hash codes, degrading to O(n) per operation.
**Diagnostic:**

```
asprof -e cpu -d 30 -f cpu.html <pid>
# HashMap.putVal or TreeNode.find dominating CPU
```

**Fix:**
```java
// Limit input sizes at API boundaries
if (input.size() > MAX_ENTRIES)
    throw new IllegalArgumentException();
// Java 8+ treeifies at 8 collisions (O(log n))
// Ensure keys implement Comparable
```
**Prevention:** Validate and limit input sizes at API boundaries. Use Java 8+. Keys should implement `Comparable`.""",

    "TreeMap": """**Failure Mode 1: ClassCastException on put()**
**Symptom:** `ClassCastException: MyKey cannot be cast to Comparable` on first `put()`.
**Root Cause:** Key class does not implement `Comparable` and no `Comparator` provided.
**Diagnostic:**

```
javap -p MyKey.class | grep Comparable
# Check if key implements Comparable
```

**Fix:**
```java
// BAD: no ordering defined
TreeMap<MyKey, String> map = new TreeMap<>();

// GOOD: provide Comparator
TreeMap<MyKey, String> map = new TreeMap<>(
    Comparator.comparing(MyKey::getName));
```
**Prevention:** Always define ordering via `Comparable` or `Comparator`.

**Failure Mode 2: Corrupt tree from broken compareTo()**
**Symptom:** `get()` returns null for existing keys. Entries disappear.
**Root Cause:** `compareTo()` violates transitivity or is inconsistent with `equals()`.
**Diagnostic:**

```
jshell> var c = map.comparator();
jshell> c.compare(a, b) + c.compare(b, a)
# Must be 0 (antisymmetry). Non-zero = broken.
```

**Fix:**
```java
// BAD: overflow in subtraction
int compareTo(MyKey o) {
    return this.value - o.value; // overflow!
}

// GOOD: safe comparison
int compareTo(MyKey o) {
    return Integer.compare(this.value, o.value);
}
```
**Prevention:** Use `Integer.compare()`, `Comparator.comparing()`. Unit test transitivity.

**Failure Mode 3: Performance degradation with expensive compareTo()**
**Symptom:** TreeMap operations slower than expected. `compareTo()` dominates profiler.
**Root Cause:** Comparison involves string concatenation, regex, or I/O. Called O(log n) times per op.
**Diagnostic:**

```
asprof -e cpu -d 30 -f cpu.html <pid>
# Look for compareTo dominating hot methods
```

**Fix:**
```java
// BAD: expensive comparison
int compareTo(Key o) {
    return toString().compareTo(o.toString());
}

// GOOD: compare primitive fields
int compareTo(Key o) {
    return Integer.compare(priority, o.priority);
}
```
**Prevention:** Compare primitive fields directly. Cache derived comparison keys.""",

    "HashSet": """**Failure Mode 1: Duplicates appear in the Set**
**Symptom:** `set.size()` larger than expected. Iteration shows duplicate-looking elements.
**Root Cause:** `hashCode()` and/or `equals()` not properly overridden.
**Diagnostic:**

```
jshell> var a = new MyObj("x");
jshell> var b = new MyObj("x");
jshell> a.equals(b) // should be true
jshell> a.hashCode() == b.hashCode() // must match
```

**Fix:**
```java
// BAD: no equals/hashCode override
class Item { String name; }

// GOOD: use Record (auto equals/hashCode)
record Item(String name) {}
```
**Prevention:** Use Records for value types. Override `equals`/`hashCode` with IDE generation.

**Failure Mode 2: Set operations produce wrong results**
**Symptom:** `retainAll()` or `removeAll()` returns unexpected results.
**Root Cause:** Mixing types (e.g., `Set<Integer>` vs `Set<Long>`). `Integer.equals(Long)` is always false.
**Diagnostic:**

```
jshell> new Integer(1).equals(new Long(1))
# false - different types never equal
```

**Fix:**
```java
// BAD: mixed types
Set<Integer> a = Set.of(1, 2, 3);
Set<Long> b = Set.of(1L, 2L);
a.retainAll(b); // empty!

// GOOD: consistent types
Set<Long> a = Set.of(1L, 2L, 3L);
Set<Long> b = Set.of(1L, 2L);
a.retainAll(b); // {1L, 2L}
```
**Prevention:** Use identical element types in set operations.

**Failure Mode 3: Memory overhead for large primitive sets**
**Symptom:** Excessive heap for a Set of integers. Millions of `Integer` wrapper objects.
**Root Cause:** HashSet stores boxed wrappers (~48 bytes each) not primitives (4 bytes).
**Diagnostic:**

```
jmap -histo:live <pid> | grep Integer
# Millions of java.lang.Integer instances
```

**Fix:**
```java
// BAD: 48 bytes per element
Set<Integer> ids = new HashSet<>();

// GOOD: 1 bit per element (dense range)
BitSet ids = new BitSet();
ids.set(userId);
// Or: IntOpenHashSet from fastutil (sparse)
```
**Prevention:** Use BitSet for dense ranges, primitive-specialized sets for sparse data.""",

    "Queue and Deque": """**Failure Mode 1: NPE from null elements in ArrayDeque**
**Symptom:** `NullPointerException` from `ArrayDeque.addLast()` or `offerFirst()`.
**Root Cause:** ArrayDeque prohibits null elements (null is the empty-slot marker internally).
**Diagnostic:**

```
grep -n '\\.offer(null)\\|\\.add(null)' MyClass.java
```

**Fix:**
```java
// BAD: null element
deque.offer(null); // NPE

// GOOD: filter nulls
if (value != null) deque.offer(value);
// Or wrap: deque.offer(Optional.ofNullable(v));
```
**Prevention:** Filter nulls at the producer side. Use `Optional` if null is meaningful.

**Failure Mode 2: Unbounded queue causing OOM**
**Symptom:** Heap grows until `OutOfMemoryError`. Producer faster than consumer.
**Root Cause:** Unbounded `ArrayDeque` or `LinkedList` as work queue without backpressure.
**Diagnostic:**

```
jmap -histo:live <pid> | head -20
# Look for ArrayDeque or Node[] with millions
```

**Fix:**
```java
// BAD: unbounded
Queue<Task> q = new ArrayDeque<>();

// GOOD: bounded with backpressure
BlockingQueue<Task> q =
    new ArrayBlockingQueue<>(1000);
q.offer(task, 5, TimeUnit.SECONDS);
```
**Prevention:** Bound all queues in production. Use `BlockingQueue` with capacity limits. Monitor queue depth.

**Failure Mode 3: Wrong element order (FIFO vs LIFO confusion)**
**Symptom:** Elements processed in wrong order. BFS produces DFS results.
**Root Cause:** Using `push()`/`pop()` (LIFO) when `offer()`/`poll()` (FIFO) intended, or vice versa.
**Diagnostic:**

```
grep -n 'push\\|pop\\|offer\\|poll' MyClass.java
# push/pop = LIFO; offer/poll = FIFO
```

**Fix:**
```java
// FIFO queue:
Queue<Node> q = new ArrayDeque<>();
q.offer(root); q.poll();

// LIFO stack:
Deque<Node> s = new ArrayDeque<>();
s.push(root); s.pop();
```
**Prevention:** Declare type as `Queue<>` for FIFO or `Deque<>` for LIFO to signal intent.""",

    "Iterator and Iterable": """**Failure Mode 1: ConcurrentModificationException**
**Symptom:** `ConcurrentModificationException` during for-each loop.
**Root Cause:** Collection modified (add/remove) while iterating. Fail-fast iterator detects via `modCount`.
**Diagnostic:**

```
# Stack trace shows Iterator.next() - find
# collection.remove()/add() inside the loop
grep -n 'for.*:.*list' MyClass.java
```

**Fix:**
```java
// BAD: modify during for-each
for (String s : list) {
    if (s.isEmpty()) list.remove(s);
}

// GOOD: use Iterator.remove()
var it = list.iterator();
while (it.hasNext()) {
    if (it.next().isEmpty()) it.remove();
}
// Or: list.removeIf(String::isEmpty);
```
**Prevention:** Use `removeIf()` or explicit `Iterator.remove()`. Never modify inside for-each.

**Failure Mode 2: NoSuchElementException from bare next()**
**Symptom:** `NoSuchElementException` from `Iterator.next()`.
**Root Cause:** Calling `next()` without checking `hasNext()` first.
**Diagnostic:**

```
grep -n '\\.next()' MyClass.java
# Verify each has a corresponding hasNext() check
```

**Fix:**
```java
// BAD: no guard
String first = iterator.next();

// GOOD: check first
if (iterator.hasNext()) {
    String first = iterator.next();
}
```
**Prevention:** Always pair `next()` with `hasNext()`. Use for-each when possible.

**Failure Mode 3: Custom Iterable returns same Iterator instance**
**Symptom:** Second for-each over the same object produces no elements.
**Root Cause:** `iterator()` returns a cached Iterator; after first traversal, cursor is at end.
**Diagnostic:**

```
jshell> var a = myIterable.iterator();
jshell> var b = myIterable.iterator();
jshell> a == b // true means bug!
```

**Fix:**
```java
// BAD: reuses iterator
public Iterator<T> iterator() {
    return this.cachedIterator;
}

// GOOD: new iterator each call
public Iterator<T> iterator() {
    return new MyIterator<>(this.data);
}
```
**Prevention:** `iterator()` must always return a new instance. Test by iterating twice.""",
}

RELATED = {
    "ArrayList": """**Prerequisites (understand these first):**

- Variables and Data Types - arrays and reference types
- Generics and Type Erasure - how `ArrayList<T>` stores `Object[]` internally

**Builds on this (learn these next):**

- ConcurrentCollections - thread-safe alternatives (`CopyOnWriteArrayList`)
- Streams API - functional operations over collections

**Alternatives / Comparisons:**

- LinkedList - when you need O(1) insert/remove at known positions
- `List.of()` / `Collections.unmodifiableList()` - when immutability is required""",

    "HashMap": """**Prerequisites (understand these first):**

- `equals()` and `hashCode()` contract - foundation of HashMap correctness
- Variables and Data Types - object identity vs equality

**Builds on this (learn these next):**

- ConcurrentHashMap - thread-safe version with segment locking
- Streams `Collectors.groupingBy()`, `toMap()` patterns

**Alternatives / Comparisons:**

- TreeMap - when sorted key order is required
- LinkedHashMap - when insertion order or LRU eviction is needed""",

    "TreeMap": """**Prerequisites (understand these first):**

- Comparable and Comparator - required for key ordering
- HashMap - the unordered alternative for informed choice

**Builds on this (learn these next):**

- ConcurrentSkipListMap - thread-safe sorted map alternative
- NavigableMap API - `floorKey()`, `ceilingKey()`, `subMap()` range ops

**Alternatives / Comparisons:**

- HashMap + sort-on-read - faster for infrequent sorted access
- Skip list - probabilistic alternative with simpler concurrency""",

    "HashSet": """**Prerequisites (understand these first):**

- `equals()` and `hashCode()` contract - HashSet correctness depends on this
- HashMap - HashSet is literally backed by HashMap

**Builds on this (learn these next):**

- EnumSet - ultra-efficient bit-vector set for enum types
- Streams `distinct()` - uses HashSet internally for deduplication

**Alternatives / Comparisons:**

- TreeSet - when sorted iteration is required
- BitSet - for dense integer membership with minimal memory""",

    "Queue and Deque": """**Prerequisites (understand these first):**

- ArrayList - understanding array-backed collections
- Data Structures basics - FIFO, LIFO, and heap concepts

**Builds on this (learn these next):**

- BlockingQueue and producer-consumer patterns
- PriorityQueue - heap-based priority ordering

**Alternatives / Comparisons:**

- LMAX Disruptor - lock-free ring buffer for extreme throughput
- Kafka/SQS - distributed durable queues for cross-service communication""",

    "Iterator and Iterable": """**Prerequisites (understand these first):**

- Collections Framework basics - List, Set, Map interfaces
- For-each loop syntax - syntactic sugar calling `iterator()` under the hood

**Builds on this (learn these next):**

- Streams API - functional evolution of Iterator
- Spliterator - parallelizable iterator for fork-join decomposition

**Alternatives / Comparisons:**

- Python generators (`yield`) - lazy iteration with simpler syntax
- Reactive Streams (Publisher/Subscriber) - push-based with backpressure""",
}


def apply_remaining(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Replace misconceptions using regex
    mc_pattern = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )

    for keyword in KEYWORDS_ORDER:
        if keyword in MISCONCEPTIONS:
            rows = MISCONCEPTIONS[keyword]
            replacement = "\n".join(
                f"| {i+1} | {m} | {r} |"
                for i, (m, r) in enumerate(rows)
            )
            m = mc_pattern.search(content)
            if m:
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Replace failure modes using regex
    fm_pattern = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )

    for keyword in KEYWORDS_ORDER:
        if keyword in FAILURES:
            m = fm_pattern.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[keyword] + content[m.end():]
                changes += 1

    # Replace related keywords using regex
    rk_pattern = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n\n'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n\n'
        r'\*\*Alternatives / Comparisons:\*\*\n\n'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )

    for keyword in KEYWORDS_ORDER:
        if keyword in RELATED:
            m = rk_pattern.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[keyword] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_remaining(FILE)
