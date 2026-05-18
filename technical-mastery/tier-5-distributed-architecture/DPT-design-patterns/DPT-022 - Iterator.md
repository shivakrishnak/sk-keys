---
id: DPT-022
title: Iterator
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-014
used_by: DPT-064
related: DPT-014, DPT-027, DPT-021
tags:
  - pattern
  - behavioral
  - intermediate
  - collections
  - java
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/design-patterns/iterator/
---

⚡ TL;DR - Iterator provides a standard way to traverse
the elements of a collection without exposing the
collection's underlying representation - decoupling
traversal logic from the data structure.

| #22 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-014 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-014, DPT-027, DPT-021 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A data structure (binary tree) is used in three different
places: one needs in-order traversal, one needs breadth-
first, one needs pre-order. Without Iterator, each client
must implement its own traversal logic, coupling client
code to the tree's internal structure. If the tree's
internal representation changes (array-backed vs pointer-
based), all three traversal implementations must change.

**THE BREAKING POINT:**
The same data structure appears in five services. Adding
a new traversal method (post-order) requires modifying
all services. The tree's internal node references are
exposed to clients.

**THE INVENTION MOMENT:**
Iterator: create one object that knows how to traverse
the tree and exposes `hasNext()`/`next()` methods. Clients
use the iterator without knowing the tree's internal
structure. Different iterators (`InOrderIterator`,
`BFSIterator`) provide different traversal strategies
without changing the tree class or clients.

**EVOLUTION:**
Java's `Iterator<T>` interface is the direct implementation
of this pattern. The enhanced `for-each` loop (`for (T t : collection)`)
compiles to iterator usage. Java Streams are Iterators
with a functional API for transformation. Python generators,
C# IEnumerable - every modern language has built-in
Iterator support because traversal decoupling is universally
needed.

---

### 📘 Textbook Definition

The **Iterator** pattern is a Behavioral design pattern
that provides a way to access the elements of an aggregate
object sequentially without exposing its underlying
representation. An Iterator object encapsulates the
traversal algorithm and current position. The aggregate
creates the iterator; clients use the iterator's interface
(`hasNext()`, `next()`) to traverse without knowing the
aggregate's internal structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Iterator separates "how to traverse" from "what to traverse"
- providing a standard cursor API regardless of data structure.

**One analogy:**
> A TV remote control (Iterator) for the TV (Aggregate).
> You press "next channel" without knowing how the TV
> stores its channel list (array, hash map, satellite lookup).
> The remote provides the same interface regardless of
> the TV's internal channel storage.

**One insight:**
Java's `for-each` loop is Iterator pattern in disguise -
`for (String s : list)` silently creates a list iterator
and calls `hasNext()`/`next()` on each iteration.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The iterator maintains traversal STATE (current position).
2. The aggregate creates the iterator (factory method).
3. The iterator interface is the same regardless of the
   aggregate type - client code is unchanged when switching
   from List to TreeSet to a custom collection.

**DERIVED DESIGN:**
Two key participants:
- **Iterator interface**: `hasNext(): boolean`, `next(): T`,
  optionally `remove()`
- **Iterable interface**: `iterator(): Iterator<T>` -
  the aggregate implements this to provide an iterator

**JAVA INTEGRATION:**
Any class implementing `Iterable<T>` supports for-each loops.
Any class implementing `Iterator<T>` can be used directly.
Java Streams are lazy iterators: elements are computed
on-demand as the terminal operation pulls them.

**TRADE-OFFS:**

**Gain:** Client code is independent of data structure.
Multiple concurrent iterators can traverse the same collection
independently (each holds its own state). Traversal
algorithm is encapsulated and independently testable.

**Cost:** Iterators can become invalid if the underlying
collection is modified during traversal (ConcurrentModificationException
in Java). Each iterator allocates a stateful object.

---

### 🧪 Thought Experiment

**SETUP:**
A file system tree. A backup service needs depth-first
traversal; a search service needs breadth-first; a display
service needs pre-order with indentation.

**WITHOUT ITERATOR:**
Each service holds direct references to file tree nodes,
walks them with their own recursion. Adding a new traversal
mode: modify the tree class or duplicate tree-walking
code.

**WITH ITERATOR:**
`FileTree.depthFirstIterator()`, `FileTree.breadthFirstIterator()`,
`FileTree.preOrderIterator()` - three iterator factory
methods. Each client calls the relevant `iterator()` method
and iterates with `hasNext()`/`next()`. Adding a new
traversal: add one iterator class and one factory method
in `FileTree`. No client code changes.

---

### 🧠 Mental Model / Analogy

> Iterator is a BOOKMARK that knows how to advance
> through a book. The bookmark holds the current page;
> `hasNext()` = "more pages to read?"; `next()` = "turn to
> the next page and return it." The book (collection) does
> not need to know the bookmark exists. Multiple bookmarks
> can exist for the same book simultaneously.

- "Bookmark" = Iterator instance (holds state)
- "Book" = Aggregate (collection)
- "Turn page" = next()
- "Multiple bookmarks" = multiple concurrent iterators

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Iterator is the "next item" button. Press it to get
the next element of a collection, regardless of whether
the collection is a list, tree, or file system.

**Level 2 - How to use it (junior developer):**
Implement `Iterable<T>` on your custom collection. The
`iterator()` method returns an `Iterator<T>` implementation
holding the traversal state. This enables for-each loops
on your custom collection.

**Level 3 - How it works (mid-level engineer):**
Java's for-each: `for (T t : collection)` compiles to:
```java
Iterator<T> it = collection.iterator();
while (it.hasNext()) { T t = it.next(); /* body */ }
```
`ArrayList.iterator()` returns a private `Itr` class holding
`cursor` (next index) and `expectedModCount`. If the list
is modified while iterating, `modCount != expectedModCount`
triggers `ConcurrentModificationException` on the next
`next()` call (fail-fast behavior).

**Level 4 - Why it was designed this way (senior/staff):**
Iterator is the foundation of the Java Collections Framework's
polymorphism. `Collections.sort`, `Collections.shuffle`,
and `Collections.unmodifiableCollection` all operate on
`Iterable`/`Iterator` interfaces - they work on ANY
collection implementation. JDBC's `ResultSet` IS an iterator
over database rows: `rs.next()` advances the cursor;
`rs.getXxx()` reads the current row. Without the Iterator
abstraction, these utilities would need a separate version
for List, Set, Queue, Tree, and every other data structure.

**Level 5 - Mastery (distinguished engineer):**
Java Streams extend Iterator with a pull-based lazy pipeline.
`stream.filter(p).map(f).findFirst()` does not create an
intermediate collection: elements are pulled one-by-one
from the source iterator through the filter and map
functions. The terminal operation (`findFirst`) pulls
one element at a time until one passes the filter.
This is Iterator + Strategy (filter and map are strategies)
+ lazy evaluation. For infinite data sources (`Stream.iterate(0,
n -> n + 1)`), this is essential: a conventional collection
cannot hold infinitely many elements, but a lazy Stream
(Iterator) can represent one.

---

### ⚙️ How It Works (Mechanism)

```
Iterator Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ <<interface>> Iterable<T>                               │
│   + iterator(): Iterator<T>                             │
│                                                         │
│ <<interface>> Iterator<T>                               │
│   + hasNext(): boolean                                  │
│   + next(): T                                           │
│   + remove(): void  ← optional                          │
│                                                         │
│ CustomCollection<T> implements Iterable<T>              │
│   - elements: T[]                                       │
│   + iterator(): Iterator<T>                             │
│       return new CustomIterator(elements);              │
│                                                         │
│ CustomIterator<T> implements Iterator<T>                │
│   - elements: T[]  ← reference to collection data       │
│   - cursor: int = 0  ← traversal state                  │
│   + hasNext(): cursor < elements.length                 │
│   + next(): elements[cursor++]                          │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Collection: ["A", "B", "C"]
Iterator created: cursor = 0

for (String s : collection):
  it.hasNext(): cursor(0) < size(3) → true
  it.next(): elements[0] = "A"; cursor = 1; return "A"
  it.hasNext(): cursor(1) < size(3) → true
  it.next(): elements[1] = "B"; cursor = 2; return "B"
  it.hasNext(): cursor(2) < size(3) → true
  it.next(): elements[2] = "C"; cursor = 3; return "C"
  it.hasNext(): cursor(3) < size(3) → false
  loop ends
```

---

### 💻 Code Example

**Example 1 - Custom Iterable binary tree:**

```java
// GOOD: implement Iterable to support for-each

class BinaryTree<T extends Comparable<T>>
    implements Iterable<T> {

    private Node<T> root;

    // In-order iterator (sorted traversal)
    @Override
    public Iterator<T> iterator() {
        return new InOrderIterator<>(root);
    }

    // BFS iterator - different traversal
    public Iterator<T> breadthFirstIterator() {
        return new BFSIterator<>(root);
    }

    private static class InOrderIterator<T>
        implements Iterator<T> {
        private final Deque<Node<T>> stack = new ArrayDeque<>();

        InOrderIterator(Node<T> root) {
            pushLeft(root); // push all leftmost path
        }

        private void pushLeft(Node<T> node) {
            while (node != null) {
                stack.push(node);
                node = node.left;
            }
        }

        @Override
        public boolean hasNext() {
            return !stack.isEmpty();
        }

        @Override
        public T next() {
            if (!hasNext()) throw new NoSuchElementException();
            Node<T> node = stack.pop();
            pushLeft(node.right); // prepare right subtree
            return node.value;
        }
    }
}

// Client: no knowledge of tree internal structure
BinaryTree<Integer> tree = new BinaryTree<>();
tree.insert(5); tree.insert(3); tree.insert(7);

// for-each works because tree is Iterable
for (int val : tree) {
    System.out.println(val); // prints in sorted order
}

// Different traversal without changing client code:
Iterator<Integer> bfs = tree.breadthFirstIterator();
while (bfs.hasNext()) {
    System.out.println(bfs.next());
}
```

**Example 2 - ConcurrentModificationException trap:**

```java
// BAD: modifying collection while iterating
List<String> items = new ArrayList<>(List.of("A","B","C","D"));
for (String item : items) {
    if (item.equals("B")) {
        items.remove(item); // throws ConcurrentModificationException!
    }
}
// ArrayList tracks modCount; iterator checks on next()
// modCount change during iteration = CME thrown

// GOOD: use Iterator.remove() or removeIf()
Iterator<String> it = items.iterator();
while (it.hasNext()) {
    if (it.next().equals("B")) {
        it.remove(); // safe: Iterator.remove() doesn't throw CME
    }
}

// Or more idiomatic (Java 8+):
items.removeIf(item -> item.equals("B")); // no iterator needed
```

**How to test/verify correctness:**
Test `hasNext()` returns false after last element. Test
`next()` throws `NoSuchElementException` when empty.
Test all elements are visited in correct order. Test that
two independent iterators on the same collection do not
interfere. Test fail-fast behavior: modify collection
during iteration, verify `ConcurrentModificationException`.

---

### ⚖️ Comparison Table

| Approach | Separation of traversal | Type-independent | Concurrent iterators | Lazy |
|---|---|---|---|---|
| **Iterator** | Yes | Yes | Yes | Optional |
| Direct index loop | No | No | N/A | No |
| Java Stream | Yes | Yes | Yes (parallel) | Yes |
| Cursor/pointer | No | No | Careful | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| for-each doesn't use Iterator | Javac compiles for-each to explicit `iterator().hasNext()/next()` calls - it IS Iterator pattern under the hood |
| Iterator is only for collections | Any data source that can produce elements sequentially can be an Iterator: file lines, database result sets, network streams, infinite mathematical sequences |
| Java 8 Streams replaced Iterator | Streams are built ON TOP of Spliterator (a parallel-capable Iterator variant). `Collection.stream()` wraps the collection's Spliterator. Streams complement Iterator; they do not replace it |
| ConcurrentModificationException means a race condition | CME is fail-fast validation in single-threaded code too: if you modify the collection while YOUR iterator is active (same thread), CME is thrown. It prevents silent incorrect iteration, not just threading issues |

---

### 🚨 Failure Modes & Diagnosis

**ConcurrentModificationException During Iteration**

**Symptom:**
`java.util.ConcurrentModificationException` thrown mid-loop.
Often in code that filters and removes elements.

**Root Cause:**
Collection modified (add/remove) while an active iterator
exists. Java's ArrayList/LinkedList/HashMap iterators
are fail-fast.

**Diagnostic Signal:**
Stack trace shows `AbstractList$Itr.checkForComodification`
or `HashMap$HashIterator.nextNode`. The modification
and iteration happen in the same code block.

**Fix:**
Use `Iterator.remove()` for safe removal during iteration.
Or collect elements to remove in a separate list, then
call `removeAll()` after iteration.

**Prevention:**
`CopyOnWriteArrayList` provides iterators that NEVER throw
CME (iterate over a snapshot). Use when reads dominate
and writes are infrequent.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Composite` - DPT-014; iterating a tree is the most
  common Composite + Iterator combination

**Builds On This (learn these next):**
- `Visitor` - DPT-029; Visitor is a way to process each
  element an iterator visits with type-specific behavior

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cursor object traverses aggregate without│
│              │ exposing internal representation         │
├──────────────┼──────────────────────────────────────────┤
│ JAVA BUILT-IN│ Iterator<T>, Iterable<T>, for-each loop  │
│              │ ResultSet, Stream - all are Iterator     │
├──────────────┼──────────────────────────────────────────┤
│ CME RULE     │ Never add/remove from collection during  │
│              │ for-each; use Iterator.remove() instead  │
├──────────────┼──────────────────────────────────────────┤
│ FOR-EACH     │ Compiles to: it = col.iterator();        │
│              │ while(it.hasNext()) { t = it.next(); }   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Mediator → Memento → Observer → State    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Java's for-each IS the Iterator pattern - compiles to
   `iterator().hasNext()/next()` calls under the hood
2. Never modify a collection inside a for-each loop -
   use `Iterator.remove()` or `removeIf()` for safe
   concurrent modification
3. JDBC's `ResultSet.next()` and Java Streams are both
   Iterator implementations - same pattern, different contexts

**Interview one-liner:**
"Iterator decouples traversal logic from the data structure
by providing a cursor abstraction (hasNext/next). Java's
for-each loop is Iterator pattern compiled to explicit iterator
calls. The classic bug: modifying a collection during for-each
throws ConcurrentModificationException - use Iterator.remove()
or removeIf() instead."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] What bytecode Java's for-each generates -
   walk through the compiled form with hasNext/next calls
2. [IMPLEMENT] Write a custom Iterable binary tree that
   supports in-order traversal via for-each loop
3. [DIAGNOSE] Identify why `list.remove(item)` inside
   a for-each throws ConcurrentModificationException and
   fix it using Iterator.remove()
4. [COMPARE] Explain why JDBC's ResultSet is an Iterator
   implementation but can only move forward (no hasNext)

