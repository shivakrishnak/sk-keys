---
id: DSA-027
title: "Set (Hash Set)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-014
used_by: DSA-044, DSA-064
related: DSA-014, DSA-028
tags:
  - data-structures
  - set
  - hashset
  - deduplication
  - membership-test
  - fundamentals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/dsa/set-hashset/
---

## TL;DR

A Set stores unique elements with O(1) membership test and
insert - the right tool whenever you need deduplication or
fast "have I seen this?" lookups.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-027 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, set, HashSet, deduplication |
| **Prerequisites** | DSA-014 |

---

### The Problem This Solves

Finding duplicates in a list: scan the list, for each element
check if already seen. With a list: O(n) per check = O(n²)
total. With a HashSet: O(1) per check = O(n) total.
Any "have I seen this before?" problem belongs to a Set.

---

### Textbook Definition

A Set is an abstract data type that stores a collection of
distinct elements. Operations: add, remove, contains.
A HashSet implements Set using a hash table (internally
a HashMap with dummy values): O(1) average for all
operations. A TreeSet uses a Red-Black Tree: O(log n) but
maintains sorted order. A LinkedHashSet maintains insertion
order with O(1) operations.

---

### Understand It in 30 Seconds

```java
Set<String> seen = new HashSet<>();
seen.add("Alice");     // adds "Alice"
seen.add("Bob");       // adds "Bob"
seen.add("Alice");     // ignored (already present)
seen.size();           // 2, not 3
seen.contains("Bob");  // true - O(1)
seen.contains("Eve");  // false - O(1)
```

---

### How It Works

**HashSet internals:**
Java's `HashSet<E>` is backed by `HashMap<E, Object>` where
the value is a dummy `PRESENT` object. `add(e)` calls
`map.put(e, PRESENT)`. `contains(e)` calls `map.containsKey(e)`.
This gives O(1) average for all operations.

**BAD - O(n²) duplicate check with List:**

```java
// O(n²) - contains() on ArrayList is O(n)
List<Integer> input = Arrays.asList(1,2,3,1,4,2);
List<Integer> result = new ArrayList<>();
for (int n : input) {
    if (!result.contains(n))   // O(n) per call!
        result.add(n);
}
```

**GOOD - O(n) duplicate check with Set:**

```java
// O(n) - contains() on HashSet is O(1)
List<Integer> input = Arrays.asList(1,2,3,1,4,2);
Set<Integer> seen = new LinkedHashSet<>(); // preserves order
seen.addAll(input);
List<Integer> deduped = new ArrayList<>(seen);
```

**Java Set implementations:**

| Class | Order | Time | When to use |
|-------|-------|------|------------|
| HashSet | None | O(1) avg | Default - fast membership test |
| LinkedHashSet | Insertion | O(1) avg | Need insertion order |
| TreeSet | Sorted | O(log n) | Need sorted iteration or range ops |
| EnumSet | Enum order | O(1) | Set of enum values (very fast) |

**Set operations (mathematical):**

```java
Set<Integer> a = new HashSet<>(Arrays.asList(1,2,3));
Set<Integer> b = new HashSet<>(Arrays.asList(2,3,4));

// Union: a ∪ b
Set<Integer> union = new HashSet<>(a);
union.addAll(b);                    // {1,2,3,4}

// Intersection: a ∩ b
Set<Integer> intersection = new HashSet<>(a);
intersection.retainAll(b);          // {2,3}

// Difference: a \ b
Set<Integer> difference = new HashSet<>(a);
difference.removeAll(b);            // {1}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "HashSet is unordered so I can't predict iteration order" | True; use LinkedHashSet for stable iteration order or TreeSet for sorted order |
| "HashSet.add() returns void" | It returns `boolean` - `true` if element was added (not already present), `false` if duplicate; used as a clean "add and check" |
| "TreeSet is always better because it is sorted" | TreeSet is O(log n) vs HashSet O(1); only use TreeSet when sorted order is required |

---

### Failure Modes & Diagnosis

**Failure: Custom objects not working correctly in HashSet**
- Cause: `hashCode()` and `equals()` not overridden; two
  logically equal objects have different hash codes, so the
  Set does not deduplicate them
- Diagnosis: `set.contains(logicalDuplicate)` returns false
- Fix: Override both `hashCode()` and `equals()` consistently;
  if `a.equals(b)` then `a.hashCode() == b.hashCode()` is
  required

---

### Quick Reference Card

| Operation | HashSet | TreeSet |
|-----------|---------|---------|
| add | O(1) | O(log n) |
| remove | O(1) | O(log n) |
| contains | O(1) | O(log n) |
| iteration | O(n) | O(n) |
| first/last | N/A | O(log n) |
| sorted order | No | Yes |

---

### The Surprising Truth

`HashSet.add()` returns a boolean. This is the most
underused method in Java collections:
`if (!set.add(x)) { /* handle duplicate */ }` is more
concise than `if (set.contains(x)) { ... } else { set.add(x); }`.
One call instead of two. But most developers write the
two-call version because they assume `add()` is void.

---

### Mastery Checklist

- [ ] Knows the three Java Set implementations and when
      to use each
- [ ] Understands that `HashSet` requires `hashCode()` and
      `equals()` for correct behavior with custom objects
- [ ] Can use Set for deduplication, membership tests,
      and set operations (union, intersection, difference)

---

### Think About This

1. You have a `Person` class with `name` and `email`.
   Two Person objects with the same email should be
   considered duplicates. What do you override and how?
   What is the contract between `equals()` and `hashCode()`?

2. **TYPE G:** A service checks if a user ID is in an
   "allow list" of 500,000 IDs. The check happens on
   every request. The allow list is loaded at startup.
   What data structure and what Java type?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the contract between hashCode()
and equals() for objects used in a HashSet?

> The contract: if `a.equals(b)` is true, then
> `a.hashCode() == b.hashCode()` MUST be true. This is
> required for HashSet to work correctly - it uses the
> hash code to find the bucket and equals to confirm
> identity. Violation: two logically equal objects land
> in different buckets; `contains()` returns false
> even when the logically equal object is in the set.
> The reverse (equal hash codes) is not required - hash
> collisions are normal and handled by chaining.

**Q2 (Medium):** When would you use a TreeSet instead
of a HashSet?

> When sorted iteration or range operations are needed:
> `first()`, `last()`, `headSet(to)`, `tailSet(from)`,
> `subSet(from, to)`. Examples: maintaining a sorted
> leaderboard, finding the k-th smallest element, or
> implementing a sliding window minimum.
> Cost: O(log n) operations vs O(1) for HashSet.
> Never use TreeSet just for sorted output - add to
> HashSet then sort the result if you only need sorted
> output once.
