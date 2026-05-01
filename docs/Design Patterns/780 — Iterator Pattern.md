---
layout: default
title: "Iterator Pattern"
parent: "Design Patterns"
nav_order: 780
permalink: /design-patterns/iterator-pattern/
number: "780"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Data Structures and Algorithms, Collections"
used_by: "java.util.Iterator, for-each loops, Stream API, Database cursors"
tags: #intermediate, #design-patterns, #behavioral, #oop, #collections, #traversal
---

# 780 — Iterator Pattern

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#collections` `#traversal`

⚡ TL;DR — **Iterator** provides a way to access elements of a collection sequentially without exposing the underlying data structure — so the client code can traverse an array, linked list, tree, or any other structure using the same interface (`hasNext()` / `next()`).

| #780 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Data Structures and Algorithms, Collections | |
| **Used by:** | java.util.Iterator, for-each loops, Stream API, Database cursors | |

---

### 📘 Textbook Definition

**Iterator** (GoF, 1994): a behavioral design pattern that provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation. The iterator object maintains the current traversal state; each call to `next()` advances to the next element. Multiple iterators can traverse the same collection simultaneously without interfering. GoF intent: "Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation." Java: `java.util.Iterator<E>` (hasNext(), next(), remove()), `java.lang.Iterable<E>` (iterator()), and the enhanced for-each loop (`for (E e : collection)`). Also: `ListIterator`, database `ResultSet`, `Stream<T>`.

---

### 🟢 Simple Definition (Easy)

A TV remote channel-up button. You press Next. The TV shows the next channel. You don't know how channels are stored internally (array? linked list? cable subscription map?). You just press Next. You can traverse all channels without knowing the underlying data structure. The remote's "channel iterator" maintains: what channel you're on (current state) and how to advance to the next.

---

### 🔵 Simple Definition (Elaborated)

`for (String name : names)` — Java's enhanced for-each loop is Iterator pattern sugar. The compiler translates this to: `Iterator<String> it = names.iterator(); while (it.hasNext()) { String name = it.next(); ... }`. Whether `names` is an `ArrayList`, `LinkedList`, `TreeSet`, or a custom `NameCollection` — the for-each loop works identically. The collection provides an iterator. Client code doesn't know how the collection stores or orders data.

---

### 🔩 First Principles Explanation

**How custom iterators work and multiple traversal strategies:**

```
JAVA ITERATOR INTERFACE:

  interface Iterator<E> {
      boolean hasNext();   // is there a next element?
      E next();            // return current element and advance
      default void remove() { throw new UnsupportedOperationException(); }
  }
  
  interface Iterable<E> {
      Iterator<E> iterator();   // creates a new iterator for this collection
  }
  
  // Any class implementing Iterable<E> can be used in for-each.
  
CUSTOM ITERATOR — Binary Tree In-Order Traversal:

  class BinaryTree<T extends Comparable<T>> implements Iterable<T> {
      private Node<T> root;
      
      static class Node<T> {
          T value; Node<T> left, right;
          Node(T value) { this.value = value; }
      }
      
      // ---- In-order iterator (left → root → right) ----
      @Override
      public Iterator<T> iterator() {
          return new InOrderIterator(root);
      }
      
      private class InOrderIterator implements Iterator<T> {
          private final Deque<Node<T>> stack = new ArrayDeque<>();
          
          InOrderIterator(Node<T> root) {
              pushLeft(root);   // push all left-spine nodes
          }
          
          private void pushLeft(Node<T> node) {
              while (node != null) { stack.push(node); node = node.left; }
          }
          
          @Override
          public boolean hasNext() { return !stack.isEmpty(); }
          
          @Override
          public T next() {
              if (!hasNext()) throw new NoSuchElementException();
              Node<T> node = stack.pop();
              pushLeft(node.right);   // process right subtree
              return node.value;
          }
      }
      
      // BONUS: Could add a different traversal:
      public Iterator<T> preOrderIterator()  { ... }
      public Iterator<T> postOrderIterator() { ... }
      public Iterator<T> breadthFirstIterator() { ... }
      // Same collection, multiple traversal strategies — all via Iterator!
  }
  
  // Usage — identical to iterating an ArrayList:
  BinaryTree<Integer> tree = new BinaryTree<>();
  tree.insert(5); tree.insert(3); tree.insert(7); tree.insert(1);
  
  for (int val : tree) {         // for-each works because tree is Iterable<Integer>
      System.out.print(val + " ");   // prints: 1 3 5 7 (in-order: sorted)
  }
  
MULTIPLE ITERATORS ON SAME COLLECTION:

  // Two independent iterators on the same list — no interference:
  List<String> names = List.of("Alice", "Bob", "Charlie", "Dave");
  
  Iterator<String> it1 = names.iterator();   // independent state
  Iterator<String> it2 = names.iterator();   // independent state
  
  it1.next();  // "Alice"  — it1 at index 1
  it2.next();  // "Alice"  — it2 still at index 0 → 1
  it1.next();  // "Bob"    — it1 at index 2
  it2.next();  // "Bob"    — it2 at index 1 → 2
  
  // Each iterator maintains its own traversal position.
  // No shared state between it1 and it2.
  
FAIL-FAST ITERATORS:

  // Java's ArrayList iterator is fail-fast:
  List<String> names = new ArrayList<>(List.of("Alice", "Bob", "Charlie"));
  Iterator<String> it = names.iterator();
  
  names.add("Dave");  // structural modification after iterator created
  it.next();          // throws ConcurrentModificationException!
  
  // Fail-fast: detects concurrent modification via modCount.
  // Iterator stores modCount snapshot at creation; checks on each next().
  // If collection's modCount changed → throw CME.
  
  // SAFE: use Iterator.remove() for removal during iteration:
  Iterator<String> it = names.iterator();
  while (it.hasNext()) {
      if (it.next().startsWith("A")) it.remove();  // safe: updates modCount
  }
  
  // Or use removeIf() (Java 8):
  names.removeIf(name -> name.startsWith("A"));
  
DATABASE CURSOR AS ITERATOR:

  // ResultSet is Iterator over database rows:
  ResultSet rs = statement.executeQuery("SELECT * FROM users");
  while (rs.next()) {               // hasNext() + advance in one call
      String name = rs.getString("name");
  }
  
  // Spring JDBC JdbcTemplate uses RowMapper — wraps ResultSet iterator:
  jdbcTemplate.query("SELECT * FROM users",
      (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name")));
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Iterator:
- Client must know internal data structure to traverse: arrays use index, linked lists use pointer, trees use recursion — different code per structure
- Traversal code mixed with business logic

WITH Iterator:
→ `for (Element e : collection)` — same code for any collection
→ Change from ArrayList to TreeSet: zero client code changes

---

### 🧠 Mental Model / Analogy

> A book index. You have a book with chapters. A traditional index lets you flip through pages sequentially (iterator over pages). A table of contents is an iterator over chapters. A concordance index is an iterator over keyword occurrences. Same book (collection) — multiple iterators (traversal strategies). You use the appropriate "index" for your access pattern. The iterator maintains your current position (bookmark) as you traverse.

"The book" = collection (the aggregate)
"Each iterator (page/chapter/keyword)" = different traversal strategy
"Bookmark" = iterator's current position (cursor)
"Turn to next page / next chapter" = iterator.next()
"Any more pages?" = iterator.hasNext()

---

### ⚙️ How It Works (Mechanism)

```
ITERATOR INTERACTION:

  Collection → iterator() → Iterator object (encapsulates traversal state)
  
  while (iterator.hasNext()) {
      Element e = iterator.next();  // returns current, advances position
      process(e);
  }
  
  Collection's internal structure: irrelevant to client.
  Multiple iterators: each has independent position cursor.
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to traverse collection without exposing internal structure
        │
        ▼
Iterator Pattern ◄──── (you are here)
(hasNext/next interface; multiple independent iterators; decouples traversal)
        │
        ├── Composite: iterator traverses composite tree nodes
        ├── Factory Method: collection.iterator() creates the iterator (factory method)
        ├── Visitor: combination — iterate with visitor performing operations on each element
        └── Stream API: Java 8 Streams = lazy iterator with functional pipeline operations
```

---

### 💻 Code Example

```java
// Pagination iterator — iterate over database pages lazily:
class PaginatedIterator<T> implements Iterator<T> {
    private final Function<PageRequest, Page<T>> pageLoader;
    private int currentPage = 0;
    private Iterator<T> currentPageIterator;
    private boolean hasMorePages = true;
    
    PaginatedIterator(Function<PageRequest, Page<T>> pageLoader) {
        this.pageLoader = pageLoader;
        loadNextPage();
    }
    
    private void loadNextPage() {
        if (!hasMorePages) return;
        Page<T> page = pageLoader.apply(PageRequest.of(currentPage++, 100));
        currentPageIterator = page.getContent().iterator();
        hasMorePages = page.hasNext();
    }
    
    @Override
    public boolean hasNext() {
        if (currentPageIterator.hasNext()) return true;
        if (!hasMorePages) return false;
        loadNextPage();
        return currentPageIterator.hasNext();
    }
    
    @Override
    public T next() {
        if (!hasNext()) throw new NoSuchElementException();
        return currentPageIterator.next();
    }
}

// Usage — transparently iterates ALL users across N database pages:
Iterable<User> allUsers = () -> new PaginatedIterator<>(
    pageRequest -> userRepository.findAll(pageRequest)
);

for (User user : allUsers) {        // for-each: seamlessly crosses page boundaries
    processUser(user);              // client never sees pages — just individual users
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java Stream and Iterator are the same | Both traverse sequences but with different paradigms. Iterator: imperative (explicit hasNext/next loop), stateful, can be used only once. Stream: declarative (pipeline of operations: map/filter/collect), lazy, supports parallel execution. Stream is built on top of Spliterator (parallel-capable Iterator), but the usage model and capabilities are very different. |
| Iterator is only for in-order traversal | Iterators can traverse in any order. Java's TreeSet iterator traverses in sorted order. LinkedList iterator: insertion order. Reverse iterators: `List.listIterator(list.size())` then `previous()`. Custom iterators: any order (random, shuffled, depth-first, breadth-first). |
| Removing elements from a collection during iteration is always unsafe | It's unsafe to use `collection.remove()` during iteration (throws ConcurrentModificationException for fail-fast iterators). But `Iterator.remove()` IS safe — it removes the element returned by the last `next()` call and updates the iterator's state accordingly. Also: `Collection.removeIf()`, `Stream.filter().collect()`, `List.subList().clear()` are all safe alternatives. |

---

### 🔥 Pitfalls in Production

**ConcurrentModificationException from modifying collection during for-each:**

```java
// ANTI-PATTERN: Modifying list during enhanced for-each:
List<User> users = new ArrayList<>(getUserList());

for (User user : users) {               // creates iterator internally
    if (user.isInactive()) {
        users.remove(user);             // MODIFIES list → ConcurrentModificationException!
    }
}

// EXPLANATION: Enhanced for-each compiles to iterator.
// users.remove() increments list's modCount.
// Iterator checks modCount on next iteration → mismatch → CME.

// FIX 1: Use Iterator.remove():
Iterator<User> it = users.iterator();
while (it.hasNext()) {
    if (it.next().isInactive()) it.remove();  // safe: iterator updates its state
}

// FIX 2: Use removeIf (Java 8 — cleanest):
users.removeIf(User::isInactive);

// FIX 3: Collect and then remove:
List<User> toRemove = users.stream().filter(User::isInactive).collect(toList());
users.removeAll(toRemove);

// FIX 4: Stream to new list (if immutable result is fine):
List<User> activeUsers = users.stream().filter(u -> !u.isInactive()).collect(toList());
```

---

### 🔗 Related Keywords

- `java.util.Iterator` — Java's standard Iterator interface (hasNext/next/remove)
- `Iterable` — Java interface marking a collection as for-each compatible
- `Stream API` — lazy functional pipeline built on Spliterator (enhanced Iterator)
- `Composite Pattern` — Iterator traverses Composite tree nodes uniformly
- `Cursor (Database)` — database ResultSet is an Iterator over query result rows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sequential access to elements without    │
│              │ exposing internal structure. hasNext() + │
│              │ next() works for any collection type.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need to traverse collection without       │
│              │ coupling to its structure; multiple      │
│              │ traversal strategies for same collection  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need parallel/random access by index;    │
│              │ Stream API is more expressive for        │
│              │ functional transformations               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "TV remote: press Next to see next       │
│              │  channel — don't know or care how       │
│              │  channels are stored internally."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stream API → Spliterator →                │
│              │ Composite Pattern → Visitor Pattern       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `java.util.Spliterator` was introduced in Java 8 to support parallel stream processing. Unlike `Iterator` (sequential, one element at a time), `Spliterator` can split itself into two independent spliterators that can be processed in parallel on different CPU cores. How does `Spliterator` extend the Iterator concept to support parallelism? What method on `Spliterator` enables this splitting? How does `Stream.parallel()` use Spliterators under the hood?

**Q2.** Java's `Iterator<E>` is external: the client drives the iteration (calls hasNext/next). Python generators and Java's `Stream` with lazy evaluation can represent internal iterators — the collection pushes elements to a consumer via callbacks. What are the tradeoffs between external iterators (client-driven) and internal iterators (collection-driven)? When is each approach more useful? How does the Observer/Reactive Streams pattern relate to internal iteration?
