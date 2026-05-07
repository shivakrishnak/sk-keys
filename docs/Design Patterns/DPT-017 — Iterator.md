---
layout: default
title: "Iterator"
parent: "Design Patterns"
nav_order: 17
permalink: /design-patterns/iterator/
number: "DPT-017"
category: Design Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming (OOP), Collections, Interface, Encapsulation
used_by: Java Collections Framework, Stream API, For-Each Loop, Composite Traversal
related: Composite, Visitor, Strategy, Generator Pattern
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - foundational
---

# DPT-017 — Iterator

⚡ TL;DR — Iterator provides a standard way to sequentially access elements of a collection without exposing its internal structure.

| #782 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Collections, Interface, Encapsulation | |
| **Used by:** | Java Collections Framework, Stream API, For-Each Loop, Composite Traversal | |
| **Related:** | Composite, Visitor, Strategy, Generator Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `ProductCatalog` stores products in an array. Clients loop with `for (int i = 0; i < catalog.size(); i++) catalog.get(i)`. The catalog switches to a `LinkedList` internally (for faster insertions). The `get(i)` method now has O(n) complexity instead of O(1) — but callers don't know this and still write index-based loops that are now catastrophically slow. Worse: clients directly access `catalog.products[i]` — coupling themselves to the array implementation. Changing the internal data structure breaks every caller.

**THE BREAKING POINT:**
Client code that knows HOW a collection is stored (array index access, tree traversal, database cursor) is coupled to the collection's internal representation. Any change to the collection's structure requires updating every caller. Multiple clients each implement their own traversal logic — if a new traversal order is needed (reverse, random, filtered), it must be added at every call site.

**THE INVENTION MOMENT:**
This is exactly why the Iterator pattern was created. The collection provides an `Iterator` with `hasNext()` and `next()`. Clients use the iterator without knowing the underlying data structure. ArrayList, LinkedList, TreeSet — all provide iterators. Clients write the same traversal code regardless. The collection can change its representation; the iterator contract remains.

---

### 📘 Textbook Definition

The **Iterator** pattern is a behavioural design pattern that provides a way to access elements of a collection sequentially without exposing its underlying representation. An `Iterator` object maintains traversal state (current position) and exposes `hasNext()` (returns true if more elements remain) and `next()` (returns the current element and advances). The collection creates and returns the appropriate iterator for its structure. Multiple iterators over the same collection can exist simultaneously, each maintaining independent traversal state.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A cursor that moves through a collection one element at a time, hiding the collection's structure.

**One analogy:**
> A hotel concierge's guest checklist. The concierge (iterator) has a clipboard with one guest name shown at a time. You ask "is there a next?" — they check the clipboard. You ask "who?" — they read the name and advance. You never see the full guest list. The list can be a binder, a tablet, or a database — the clipboard interface is the same.

**One insight:**
The Iterator doesn't just simplify traversal — it makes traversal order a first-class design decision. The same collection can return different iterators: forward, reverse, filtered, shuffled. The client code is identical for all traversal modes; only the iterator changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Sequential access to a collection should not require knowing the collection's internal structure.
2. Multiple independent traversals of the same collection must be possible simultaneously.
3. Different traversal strategies (forward, reverse, filtered) should be expressible without changing the collection.

**DERIVED DESIGN:**
Given invariant 1: define an `Iterator<T>` interface independent of the concrete collection type. Given invariant 2: each call to `collection.iterator()` creates a NEW iterator object with independent state — two iterators of the same list maintain separate positions. Given invariant 3: the collection can return different iterator implementations from different factory methods (`iterator()`, `descendingIterator()`, `filteredIterator(Predicate)`).

The iterator's state: typically an index (for array-based) or a current node reference (for linked/tree-based). `hasNext()` checks if this position is valid. `next()` returns the current element and advances the position.

**THE TRADE-OFFS:**
**Gain:** Collection internals are encapsulated; universal traversal interface across all collection types; independent concurrent iteration (but not concurrent modification); traversal strategies are replaceable; Java's for-each loop is syntactic sugar over Iterator.
**Cost:** Cannot modify collection structure during iteration (without `Iterator.remove()`); forward-only iterators don't support random access; `ConcurrentModificationException` if collection is modified while iterating without proper handling.

---

### 🧪 Thought Experiment

**SETUP:**
A company directory stores employees in a social graph (each employee has manager and direct-report connections). Clients need to traverse the directory.

**WHAT HAPPENS WITHOUT ITERATOR:**
Each client that needs to traverse employees writes its own BFS or DFS traversal with an explicit queue or stack. Three clients implement three versions of the same graph traversal, each with subtle differences. When the graph storage changes to a database-backed adjacency list, all three traversals break.

**WHAT HAPPENS WITH ITERATOR:**
`CompanyDirectory.bfsIterator()` returns a `BFSIterator<Employee>`. Clients use `while (iter.hasNext()) { Employee e = iter.next(); ... }`. The graph traversal algorithm is encapsulated in the iterator. Changing graph storage: update the iterator implementation, not the clients. Want DFS? `directory.dfsIterator()` — same client loop, different traversal.

**THE INSIGHT:**
Iterator moves the traversal algorithm from the client to the collection side. Clients express "give me each element" — not "I know how to walk your structure." The algorithm is in one place and can be changed once.

---

### 🧠 Mental Model / Analogy

> Iterator is like a moving spotlight on a stage. You see only one performer at a time — whoever the spotlight illuminates. The spotlight moves on command: "next." You don't see the whole stage or know how many performers there are until the spotlight reaches the end. Multiple spotlights can move independently across the same stage.

- "Spotlight" → the iterator object
- "Performer in the spotlight" → the current element (from `next()`)
- "Moving spotlight to next" → calling `next()` and advancing position
- "Is there a next performer?" → calling `hasNext()`
- "Multiple spotlights" → multiple independent iterators over same collection
- "Stage layout" → internal collection structure (hidden from spotlight controller)

Where this analogy breaks down: a stage spotlight reveals the performer's position. `Iterator` does not expose the current index — that requires `ListIterator` (Java) or an explicit counter.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Iterator is a "one at a time" access pattern. You say "give me the next thing." The iterator gives it to you. You ask again. Eventually it says "there is no more." You never need to know how many things there are or how they are stored.

**Level 2 — How to use it (junior developer):**
In Java: use the for-each loop — it uses `Iterable`/`Iterator` automatically. For manual use: `Iterator<String> it = list.iterator(); while (it.hasNext()) { String s = it.next(); }`. To remove during iteration: use `it.remove()` (not `list.remove()`). Implement `Iterable<T>` on your custom collection by implementing `iterator()` to return a new iterator instance.

**Level 3 — How it works (mid-level engineer):**
Java's `for (T item : collection)` is syntax sugar for `Iterator<T> it = collection.iterator(); while (it.hasNext()) { T item = it.next(); ... }`. The JVM desugars this at compile time — no performance difference from manual iteration. `ConcurrentModificationException`: ArrayList, LinkedList maintain a `modCount` field that increments on structural changes. Iterator captures `expectedModCount` at creation time and checks it on each `next()` call — if they differ, the exception fires. This is fail-fast iteration. `CopyOnWriteArrayList` creates a snapshot for iteration — fail-safe but uses more memory. `BatchIterator` pattern: returns batches of N elements per `next()` call — used in data processing to reduce overhead.

**Level 4 — Why it was designed this way (senior/staff):**
Iterator was the canonical solution to external collection traversal before Java had Streams. `java.util.Iterator` was introduced in Java 1.2 (1998) to replace the older `Enumeration` (no `remove()`, verbose method names). The pattern's design reveals a tension: *external* iterators (client pulls elements) vs *internal* iterators (collection pushes elements). Java's `Iterator` is external; Java Streams are internal (you pass a function, the stream pushes elements to it). External iterators give the client more control (pause, early exit without special exception); internal iterators (Streams) are more composable (`filter`, `map`, `reduce` pipelines). In distributed systems, cursor-based pagination (`SELECT * WHERE id > :lastId LIMIT 100`) IS the Iterator pattern applied to database result sets — `hasNext()` is whether the last page was full; `next()` is fetching the next page.

---

### ⚙️ How It Works (Mechanism)

**ArrayList Iterator internals:**
```
┌───────────────────────────────────────────────────┐
│  ArrayList<String>: ["A", "B", "C", "D"]          │
│  modCount = 5                                     │
│                                                   │
│  new Itr() {                                      │
│    int cursor = 0;          ← current position    │
│    int expectedModCount = 5 ← capture at creation │
│                                                   │
│    hasNext(): cursor < 4 (size)                   │
│                                                   │
│    next():                                        │
│      checkModCount(): 5 == 5 ✓                    │
│      element = list[cursor] = "A"                 │
│      cursor++ → cursor = 1                        │
│      return "A"                                   │
│  }                                                │
│                                                   │
│  If list.add("E") between iterations:             │
│    modCount becomes 6                             │
│    next() checks: 6 != 5 → ConcurrentModification│
└───────────────────────────────────────────────────┘
```

**Custom tree iterator (in-order traversal):**
```java
// Uses explicit stack to simulate recursion
class InOrderIterator<T> implements Iterator<T> {
    private final Deque<TreeNode<T>> stack = new ArrayDeque<>();

    InOrderIterator(TreeNode<T> root) {
        pushLeft(root);  // pre-load leftmost path
    }

    private void pushLeft(TreeNode<T> node) {
        while (node != null) {
            stack.push(node);
            node = node.left;
        }
    }

    public boolean hasNext() { return !stack.isEmpty(); }

    public T next() {
        TreeNode<T> node = stack.pop();
        pushLeft(node.right); // load next subtree
        return node.value;
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client needs to process all products
  → catalog.iterator() called
  → ArrayList.Itr created with cursor=0
                              ← YOU ARE HERE
  → for-each loop calls it.hasNext()
  → true: it.next() returns Product at cursor 0
  → cursor++ → cursor=1
  → [process product]
  → ... repeat until cursor == size
  → hasNext() returns false
  → loop ends
```

**FAILURE PATH:**
```
During iteration: anotherThread.catalog.add(product)
  → catalog modCount incremented
  → iterator's expectedModCount no longer matches
  → next() throws ConcurrentModificationException
Fix options:
  1. Synchronise external access (lock during iteration)
  2. Use CopyOnWriteArrayList (snapshot-based iteration)
  3. Use concurrent-safe iterator from ConcurrentHashMap.values()
```

**WHAT CHANGES AT SCALE:**
For 100M-element collections, iterating in batches reduces overhead. Java's `Spliterator` (Java 8+) extends Iterator for parallel traversal — `Spliterator.trySplit()` divides the collection into independent ranges, each traversable by a separate thread. `Stream.parallel()` uses `Spliterator` internally. For database result sets (server-side cursors), the iterator fetches rows in pages — network round-trip amortised across N rows per batch.

---

### 💻 Code Example

**Example 1 — BAD: Index-based traversal (couples to array):**
```java
// BAD: couples client to ArrayList's indexed access
ArrayList<Product> products = catalog.getProducts();
for (int i = 0; i < products.size(); i++) {
    Product p = products.get(i); // O(n) for LinkedList!
    process(p);
}
// Switching catalog to LinkedList makes this O(n²)
```

**Example 2 — GOOD: Iterator-based traversal:**
```java
// GOOD: works for any Iterable — ArrayList, LinkedList, Set
// Java's for-each uses Iterator automatically
for (Product p : catalog) {
    process(p);
}

// Equivalent manual form:
Iterator<Product> it = catalog.iterator();
while (it.hasNext()) {
    Product p = it.next();
    if (shouldRemove(p)) {
        it.remove(); // safe removal during iteration
    } else {
        process(p);
    }
}
```

**Example 3 — Custom Iterable collection:**
```java
public class ProductCatalog implements Iterable<Product> {
    private final List<Product> products = new ArrayList<>();

    public void add(Product p) { products.add(p); }

    @Override
    public Iterator<Product> iterator() {
        return products.iterator(); // delegate to list
    }

    // Custom filtered iterator:
    public Iterator<Product> inStockIterator() {
        return products.stream()
            .filter(Product::isInStock)
            .iterator();
    }
}

// Usage:
ProductCatalog catalog = new ProductCatalog();
// ...add products...
for (Product p : catalog) {          // all products
    displayProduct(p);
}
Iterator<Product> inStock =
    catalog.inStockIterator();
while (inStock.hasNext()) {          // only in-stock
    displayProduct(inStock.next());
}
```

**Example 4 — Database cursor as Iterator (pagination):**
```java
public class PagedProductIterator implements Iterator<Product> {
    private final ProductRepository repo;
    private final int pageSize;
    private long lastId = 0;
    private Iterator<Product> currentPage;
    private boolean exhausted = false;

    public PagedProductIterator(
            ProductRepository repo, int pageSize) {
        this.repo     = repo;
        this.pageSize = pageSize;
        fetchNextPage();
    }

    private void fetchNextPage() {
        List<Product> page =
            repo.findByIdGreaterThan(lastId, pageSize);
        if (page.isEmpty()) {
            exhausted = true;
        } else {
            lastId = page.get(page.size() - 1).getId();
            currentPage = page.iterator();
        }
    }

    @Override
    public boolean hasNext() {
        if (currentPage.hasNext()) return true;
        if (exhausted) return false;
        fetchNextPage();
        return currentPage.hasNext();
    }

    @Override
    public Product next() {
        if (!hasNext()) throw new NoSuchElementException();
        return currentPage.next();
    }
}
// Client: iterates all products across all DB pages
// transparently — no pagination logic in client
```

---

### ⚖️ Comparison Table

| Mechanism | Traversal Control | Lazy | Memory | Best For |
|---|---|---|---|---|
| **Iterator** | External (pull) | Yes | O(1) per step | Sequential access, early exit |
| Java Stream | Internal (push) | Yes | O(1) per step | Pipelines (filter, map, reduce) |
| for-each / Iterable | External (auto) | Yes | O(1) per step | Simple sequential access |
| ListIterator | External (bidirectional) | Yes | O(1) | Bidirectional list traversal |
| Spliterator | Parallel-capable | Yes | O(1) | Parallel stream traversal |
| toList() then loop | N/A (eager) | No | O(n) | When all elements needed upfront |

How to choose: use Iterator (for-each) for simple sequential traversal. Use Streams when composing transformations (`filter().map().collect()`). Use `Spliterator` when parallel processing is needed. Use `ListIterator` when bidirectional traversal is needed.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ConcurrentModificationException means you used multiple threads | CME happens even on a single thread if you modify the collection while iterating with a non-concurrent iterator. Use `it.remove()` from the iterator itself for safe removal |
| Iterator is only for List — you can't iterate Sets or Maps | All Java `Collection` implementations implement `Iterable`. `Map.entrySet()`, `Map.keySet()`, `Map.values()` all return `Collection`s that are `Iterable` |
| for-each loop is more efficient than manual Iterator | They compile to identical bytecode. for-each IS manual iterator — it's syntactic sugar |
| Iterator always returns elements in insertion order | Order depends on the collection. LinkedHashMap: insertion order. TreeMap: sorted order. HashSet: undefined order. The iterator traverses in the collection's natural order |
| You can create an Iterator that also modifies the collection safely | Only `Iterator.remove()` and `ListIterator.add()`/`set()` are safe. Any other structural modification (`list.add()`, `list.remove()`) triggers CME |

---

### 🚨 Failure Modes & Diagnosis

**1. ConcurrentModificationException in Single-Threaded Code**

**Symptom:** `ConcurrentModificationException` in a for-each loop on a `List`. No other threads involved.

**Root Cause:** The loop body calls `list.remove(element)` directly instead of using `iterator.remove()`. This modifies `modCount` while the iterator's `expectedModCount` is stale.

**Diagnostic:**
```java
// Find collection modification inside iteration:
for (Product p : products) {
    if (p.isExpired()) {
        products.remove(p);  // BAD: direct remove triggers CME
    }
}
```

**Fix:**
```java
// Option 1: Iterator.remove()
Iterator<Product> it = products.iterator();
while (it.hasNext()) {
    if (it.next().isExpired()) it.remove(); // safe
}

// Option 2: removeIf (Java 8+)
products.removeIf(Product::isExpired); // atomic removal

// Option 3: collect to remove, then removeAll
List<Product> expired = products.stream()
    .filter(Product::isExpired).collect(toList());
products.removeAll(expired);
```

**Prevention:** Never modify a collection inside a for-each loop. Use `removeIf`, `replaceAll`, or an explicit iterator.

---

**2. Iterator Not Closed — Resource Leak**

**Symptom:** A database connection leak when iterating over a JDBC result set or Hibernate scroll cursor. Connections accumulate until the pool is exhausted.

**Root Cause:** `ResultSet` and `ScrollableResults` are resource-backed iterators. If iteration completes early (early `break` or exception), the underlying cursor is not closed.

**Diagnostic:**
```bash
# DB-side check (PostgreSQL):
SELECT count(*) FROM pg_stat_activity
  WHERE state = 'idle in transaction';
# Accumulating idle cursors = resource leak
```

**Fix:**
```java
// Use try-with-resources for resource-backed iterators:
try (ScrollableResults results =
         query.scroll(ScrollMode.FORWARD_ONLY)) {
    while (results.next()) {
        process(results.get(0));
    }
} // automatically closed even on exception/break
```

**Prevention:** Any iterator backed by an I/O resource (file, database, network) must implement `AutoCloseable`. Always use try-with-resources.

---

**3. Iterator in Multi-Threaded Context Without Synchronisation**

**Symptom:** Intermittent `ConcurrentModificationException` or `ArrayIndexOutOfBoundsException` during list iteration when multiple threads access the list.

**Root Cause:** A non-thread-safe `ArrayList` is being modified by one thread while another iterates. The modCount check may pass (race condition) but the array may shift, causing out-of-bounds access.

**Diagnostic:**
```bash
jstack <PID> | grep -B 5 "ConcurrentModification\|ArrayIndexOutOf"
# Look for two threads stuck on different ArrayList methods
```

**Fix:**
Use thread-safe alternatives:
```java
// Option 1: CopyOnWriteArrayList (read-heavy)
List<Product> list = new CopyOnWriteArrayList<>(products);

// Option 2: Synchronised wrapper with explicit lock during iter
List<Product> syncList = Collections.synchronizedList(list);
synchronized(syncList) {
    for (Product p : syncList) { process(p); }
}

// Option 3: Snapshot at iteration start
List<Product> snapshot = new ArrayList<>(list); // atomically copied
for (Product p : snapshot) { process(p); }
```

**Prevention:** Document collection thread-safety contracts at declaration time. Choose the right collection type for concurrent access patterns.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Collections` — Java's Collection framework is the primary context for Iterator; understanding List, Set, Map structures is foundational
- `Interface` — `java.util.Iterator<T>` and `java.lang.Iterable<T>` are interfaces; understanding interface contracts is required
- `Encapsulation` — Iterator encapsulates traversal state and algorithm; this is encapsulation applied to iteration behaviour

**Builds On This (learn these next):**
- `Java Stream API` — extends Iterator with lazy, composable pipeline operations; Streams build on the same Iterable infrastructure
- `Composite` — Composite trees need external iterators for uniform traversal; Iterator is the canonical companion for Composite
- `Visitor` — Visitor traverses a Composite structure; it can be implemented using Iterator for the traversal mechanism

**Alternatives / Comparisons:**
- `Java Stream` — internal iterator with composable pipeline (filter, map, reduce); use when transformations are needed in addition to traversal
- `Generator Pattern` — lazy iteration; elements are produced on demand (Python generators, Java `Stream.generate()`)
- `Enumeration` — Java's legacy iterator (pre-Java 1.2); `hasMoreElements()` + `nextElement()` — replaced by `Iterator`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cursor that traverses a collection        │
│              │ without revealing its internal structure  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Client code couples to collection internals│
│ SOLVES       │ (index access, node pointers, cursors)    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ for-each is Iterator; Streams are iterators│
│              │ — the pattern is everywhere in Java       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sequential access to any collection       │
│              │ without needing random access or index    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Random access by index is needed          │
│              │ (use List.get(i) directly instead)        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Encapsulation + universality vs no random  │
│              │ access and CME on concurrent modification │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Give me one at a time — I don't need      │
│              │  to know how you store them."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Java Stream API → Spliterator →            │
│              │ Database Cursor Pattern                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `ProductRepository.findAll()` returns an `Iterator<Product>` backed by a database scroll cursor. A client iterates through all 10 million products, breaking out of the loop early when a condition is met (after product 50,000). The cursor is never explicitly closed. Describe the full resource leak chain — from the `Iterator` object to the database connection pool — and explain why Java's garbage collection does NOT prevent this leak and what specific Java language feature does.

**Q2.** A Composite tree of `MenuItems` uses an in-order `Iterator` for rendering. A new requirement: render menu items in sorted alphabetical order within each composite group. The current iterator returns items in insertion order. Describe two approaches to implement sorted iteration: (a) modifying the Iterator implementation, (b) using the Visitor pattern. Compare the two approaches for: the number of classes modified, the ability to switch back to insertion-order iteration, and the overhead per render call.

