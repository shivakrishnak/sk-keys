---
id: DSA-109
title: DSA Migration - JDK Collection Framework Upgrades
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-012, DSA-106
used_by: DSA-122
related: DSA-106, DSA-108
tags:
  - java
  - jdk-migration
  - collections
  - api-upgrade
  - best-practices
  - migration
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 109
permalink: /technical-mastery/dsa/jdk-collections-migration/
---

## TL;DR

Each major JDK version added collection improvements
that reduce boilerplate, improve performance, and
eliminate bugs. This guide covers the key migrations:
JDK 8 (stream APIs), JDK 9+ (immutable factory methods),
JDK 14+ (record keys), and JDK 21 (sequenced collections).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-109 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | java, JDK migration, collections framework |
| **Prerequisites** | DSA-012, DSA-106 |

---

### JDK 8: Streams and Method References

```java
// BEFORE JDK 8: verbose explicit loops
List<String> filtered = new ArrayList<>();
for (Product p : products) {
    if (p.getPrice() > 100) {
        filtered.add(p.getName());
    }
}

// AFTER JDK 8: Stream API
List<String> filtered = products.stream()
    .filter(p -> p.getPrice() > 100)
    .map(Product::getName)
    .collect(Collectors.toList());

// JDK 8 Map improvements:
Map<String, Integer> wordCount = new HashMap<>();

// BEFORE: manual null check
if (wordCount.containsKey(word)) {
    wordCount.put(word, wordCount.get(word) + 1);
} else {
    wordCount.put(word, 1);
}

// AFTER: merge (atomic for regular map, not thread-safe)
wordCount.merge(word, 1, Integer::sum);

// computeIfAbsent: lazy initialization pattern
Map<String, List<Order>> ordersByCustomer = new HashMap<>();
ordersByCustomer.computeIfAbsent(customerId,
    k -> new ArrayList<>()).add(order);
```

---

### JDK 9+: Immutable Collection Factories

```java
// BEFORE JDK 9: verbose immutable collections
List<String> colors = Collections.unmodifiableList(
    Arrays.asList("red", "green", "blue")
);
// OR:
List<String> colors2 = new ArrayList<>();
colors2.add("red"); colors2.add("green"); colors2.add("blue");
Collections.unmodifiableList(colors2);

// AFTER JDK 9: List.of(), Set.of(), Map.of()
List<String> colors = List.of("red", "green", "blue");
Set<String> flags = Set.of("active", "pending");
Map<String, Integer> scores = Map.of(
    "Alice", 100,
    "Bob", 95
);

// IMPORTANT: List.of() is:
// - Immutable: UnsupportedOperationException on modification
// - Null-hostile: throws NPE for null elements (unlike ArrayList)
// - Structurally unmodifiable: no add/remove/set
// - Memory efficient: compact representation for small sizes
//   List.of() with 0-2 elements uses specialized classes
//   (not ArrayList), extremely memory efficient

// For large maps: Map.copyOf() or Map.ofEntries()
Map<String, Product> catalog = Map.ofEntries(
    products.stream()
        .map(p -> Map.entry(p.getId(), p))
        .toArray(Map.Entry[]::new)
);
```

---

### JDK 14+: Record Classes as Map Keys

```java
// BEFORE JDK 14: verbose equals/hashCode/toString
class CacheKey {
    private final String userId;
    private final LocalDate date;

    CacheKey(String userId, LocalDate date) {
        this.userId = userId;
        this.date = date;
    }

    @Override
    public boolean equals(Object o) { ... }
    @Override
    public int hashCode() { ... }
    @Override
    public String toString() { ... }
}

// AFTER JDK 14+: record auto-generates equals/hashCode
record CacheKey(String userId, LocalDate date) {}
// equals: compares all fields
// hashCode: based on all fields (good distribution)
// toString: "CacheKey[userId=..., date=...]"
// Immutable by default (fields are final)

Map<CacheKey, Product> cache = new HashMap<>();
cache.put(new CacheKey("user123", LocalDate.now()), product);
Product hit = cache.get(new CacheKey("user123", LocalDate.now()));
// Works correctly because record equality is value-based
```

---

### JDK 21: Sequenced Collections

```java
// JDK 21 adds SequencedCollection, SequencedSet, SequencedMap
// These interfaces provide consistent first/last element access
// for collections that have a defined encounter order

// BEFORE JDK 21: inconsistent first/last access
List<String> list = new ArrayList<>(List.of("a","b","c"));
list.get(0);                    // first element (List)
list.get(list.size()-1);        // last element (List)
// LinkedList:
LinkedList<String> llist = ...;
llist.getFirst();               // Deque method
llist.getLast();                // Deque method
// TreeSet:
TreeSet<String> tset = ...;
tset.first();                   // SortedSet method
tset.last();                    // SortedSet method
// LinkedHashMap:
LinkedHashMap<String,Integer> lhm = ...;
lhm.keySet().iterator().next(); // no direct first()

// AFTER JDK 21: uniform interface
SequencedCollection<String> any = list; // or LinkedList
any.getFirst(); // uniform
any.getLast();  // uniform
any.addFirst("prepend");
any.addLast("append");
any.reversed(); // reverse view

// SequencedMap for LinkedHashMap
SequencedMap<String, Integer> smap = new LinkedHashMap<>();
smap.firstEntry(); // Map.Entry of first key
smap.lastEntry();  // Map.Entry of last key
```

---

### Migration Checklist by JDK Version

| Migration | Benefit | Risk |
|-----------|---------|------|
| `new ArrayList<>(Arrays.asList(...))` → `List.of()` | Immutable, memory efficient | List.of() rejects nulls; check for null elements first |
| `Collections.unmodifiableMap` → `Map.copyOf()` | Cleaner API | Map.copyOf() is a snapshot copy, not a live view |
| Manual null check + put → `computeIfAbsent` | Atomic, cleaner | Not thread-safe for concurrent maps; use CHM.computeIfAbsent |
| Custom key class → `record` | Auto-generated correct equals/hashCode | Records are shallow-equality; nested mutable objects still need care |
| Explicit size tracking → `SequencedCollection.getFirst/getLast` | Cleaner code | JDK 21+ only |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "List.of() is just like Collections.unmodifiableList()" | List.of() rejects null elements (NPE on creation). unmodifiableList wraps a mutable list and allows mutation of the backing list. List.of() creates a truly independent immutable list |
| "Records are always safe as HashMap keys" | Records with mutable field types (e.g., List, Date) can have their equality semantics break if those fields are mutated after the record is used as a map key. Use only immutable types as record components for map keys |

---

### Mastery Checklist

- [ ] Uses List.of()/Set.of()/Map.of() for small immutable collections
- [ ] Uses record for composite map keys (eliminating equals/hashCode boilerplate)
- [ ] Knows JDK 21 SequencedCollection API for ordered collections

---

### The Surprising Truth

Java's `List.of()` (JDK 9+) uses specialized
implementation classes for lists of 0, 1, and 2
elements that store the elements directly as fields
(not in an array), saving the array object allocation
and array header overhead. A `List.of("a", "b")` uses
less memory than `new ArrayList<>(Arrays.asList("a","b"))`.
For large numbers of small lists (e.g., millions of
tag lists in a data pipeline), this difference in
object count translates to measurably less GC pressure.
