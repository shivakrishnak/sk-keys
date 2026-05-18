---
id: DSA-050
title: HashMap Mutation While Iterating Anti-Pattern
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-014, DSA-023
used_by: DSA-086
related: DSA-014, DSA-027, DSA-033
tags:
  - anti-pattern
  - hash-map
  - concurrent-modification
  - iterator
  - java
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/dsa/hashmap-mutation-while-iterating/
---

## TL;DR

Modifying a HashMap while iterating it throws
`ConcurrentModificationException` - use Iterator.remove(),
collect-then-modify, or a copy to safely remove entries
during traversal.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-050 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | anti-pattern, HashMap, ConcurrentModification |
| **Prerequisites** | DSA-014, DSA-023 |

---

### The Problem This Solves

A very common bug: you iterate a map, remove entries
matching a condition, and get an exception. The fix is
one of three safe patterns. Every Java developer encounters
this - knowing the patterns prevents the bug permanently.

---

### How It Fails and How to Fix It

**BAD - ConcurrentModificationException:**

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 50);
scores.put("Bob", 30);
scores.put("Carol", 80);

// WRONG: modifying while iterating throws exception
for (String key : scores.keySet()) {
    if (scores.get(key) < 60) {
        scores.remove(key);  // ConcurrentModificationException!
    }
}
```

**GOOD - Pattern 1: Iterator.remove() (in-place):**

```java
// Iterator.remove() is safe - removes via the iterator
Iterator<Map.Entry<String, Integer>> iter =
    scores.entrySet().iterator();
while (iter.hasNext()) {
    Map.Entry<String, Integer> entry = iter.next();
    if (entry.getValue() < 60) {
        iter.remove();  // safe remove via iterator
    }
}
```

**GOOD - Pattern 2: Collect then remove:**

```java
// Collect keys to remove first, then remove
List<String> toRemove = new ArrayList<>();
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    if (entry.getValue() < 60) toRemove.add(entry.getKey());
}
scores.keySet().removeAll(toRemove);
```

**GOOD - Pattern 3: Java 8 removeIf:**

```java
// Java 8+ - cleanest approach
scores.entrySet().removeIf(e -> e.getValue() < 60);
// or for lists:
list.removeIf(item -> item.isExpired());
```

**Why does ConcurrentModificationException happen?**

HashMap uses a `modCount` field incremented on every
structural modification (put, remove, resize). The iterator
captures `modCount` at creation. On each `next()`, it
checks if `modCount` still matches. If the map was modified
outside the iterator, they differ → exception.
This is "fail-fast" behavior - better to crash immediately
than silently skip or duplicate entries.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "ConcurrentModificationException = multi-threading issue" | It can occur in a single thread; the name refers to concurrent structural modification during iteration |
| "Using synchronized HashMap prevents this" | `Collections.synchronizedMap()` still throws CME; use `ConcurrentHashMap` which allows concurrent modification during iteration |

---

### Failure Modes & Diagnosis

**Failure: ConcurrentModificationException in production**
- Cause: Modify-while-iterating
- Diagnosis: Stack trace shows `HashMap$HashIterator.nextNode`
- Fix: Use `Iterator.remove()` or `removeIf()` or
  collect-then-remove pattern

---

### Quick Reference Card

| Pattern | When to use | Java version |
|---------|------------|--------------|
| `Iterator.remove()` | Low overhead, in-place | All versions |
| Collect then remove | Simple, readable | All versions |
| `removeIf()` | Cleanest one-liner | Java 8+ |
| `ConcurrentHashMap` | Multi-threaded access | All versions |

---

### Mastery Checklist

- [ ] Understands why ConcurrentModificationException
      occurs (modCount fail-fast mechanism)
- [ ] Can apply all three safe patterns
- [ ] Knows `removeIf()` as the Java 8+ clean solution

---

### Interview Deep-Dive

**Q1 (Easy):** What causes ConcurrentModificationException
and how do you prevent it when removing from a HashMap
during iteration?

> HashMap's iterator is fail-fast: it tracks a `modCount`
> counter and throws CME if the map is structurally modified
> outside the iterator during traversal. Prevention:
> (1) `iterator.remove()` - modifies through the iterator,
> increments the iterator's own expected count.
> (2) `entrySet().removeIf(predicate)` - Java 8+, one line.
> (3) Collect keys to remove, then `removeAll()` after.
> Never use `map.remove(key)` inside a for-each loop on
> the same map.
