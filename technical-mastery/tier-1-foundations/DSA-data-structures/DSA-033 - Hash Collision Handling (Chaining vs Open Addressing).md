---
id: DSA-033
title: Hash Collision Handling (Chaining vs Open Addressing)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-014
used_by: DSA-086
related: DSA-014, DSA-027, DSA-045
tags:
  - data-structures
  - hash-map
  - collision
  - chaining
  - open-addressing
  - internals
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/dsa/hash-collision-handling/
---

## TL;DR

When two keys hash to the same bucket, chaining adds a
linked list at that bucket; open addressing probes for the
next empty slot - Java uses chaining with trees for Java 8+.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-033 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, hash-map, collision, chaining |
| **Prerequisites** | DSA-014 |

---

### The Problem This Solves

A hash function maps keys to bucket indices. Two different
keys can produce the same index (collision). The hash map
must handle collisions correctly - all keys must be
retrievable even if they share a bucket.

---

### Textbook Definition

**Chaining (separate chaining):** Each bucket is a linked
list (or other structure). All keys mapping to the same
bucket are stored in that bucket's list. Lookup: hash to
bucket, scan list for key. Time: O(1) average, O(n/m)
where n=entries, m=buckets (= load factor).

**Open addressing:** All entries stored in the array itself.
On collision, probe for the next empty slot. Linear probing:
check i+1, i+2, ... Quadratic probing: i+1², i+2², ...
Double hashing: use a second hash function for step size.

---

### How It Works

**Java HashMap (chaining + tree for long chains):**

```
HashMap internals:
  Bucket array of size 16 (default)
  Each bucket: null | single entry | linked list | TreeNode

  Java 8+ optimization:
  When bucket chain length > 8: convert to TreeNode (Red-Black Tree)
  When chain length < 6: convert back to linked list
  This makes worst case O(log n) per bucket, not O(n)
```

**Visualizing collision:**

```
Key "Alice": hash("Alice") % 16 = 3
Key "Bob":   hash("Bob")   % 16 = 7
Key "Carol": hash("Carol") % 16 = 3  ← COLLISION!

Chaining:
Bucket 3: [Alice → Carol]  (linked list)
Bucket 7: [Bob]
```

**Load factor and resize:**

```java
// Java HashMap resizes when: size > capacity * loadFactor
// Default loadFactor = 0.75
// Default capacity = 16
// Resize threshold = 16 * 0.75 = 12 entries

// Over-capacity → O(n) resize → copy all entries
// Amortized O(1) insert despite occasional O(n) resize

// Pre-size if you know the count:
Map<String, Integer> map = new HashMap<>(1024, 0.75f);
// Prevents resize for up to 768 entries
```

**Open addressing example (linear probing):**

```
Capacity=7, insert keys hashing to [3, 3, 3]:
  key1 → slot 3 (empty, insert)
  key2 → slot 3 (occupied), try slot 4 (empty, insert)
  key3 → slot 3 (occupied), try slot 4 (occupied), try slot 5

Lookup key2: hash→3, check slot 3 (key1, not key2), check slot 4 (key2, found)
Delete: must mark as "deleted" (tombstone), not empty
        otherwise lookup for key3 would stop at slot 4
```

---

### Comparison Table

| Technique | Cache | Memory | Delete | Java use |
|-----------|-------|--------|--------|---------|
| Chaining | Poor (linked list) | Higher (pointers) | Easy | HashMap |
| Linear probing | Excellent | Lower | Needs tombstone | Not in Java stdlib |
| Double hashing | Good | Lower | Needs tombstone | Not in Java stdlib |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Hash collisions mean the map is broken" | Collisions are normal and expected; every production hash map handles them |
| "Java HashMap is O(1) for all operations" | O(1) average with good hash distribution; O(log n) worst case per bucket (Java 8+ via TreeNode) |
| "Deleting in chaining is simple" | Removing from chained list is O(1) if you have the node; finding it is O(chain length) |

---

### Failure Modes & Diagnosis

**Failure: All keys land in one bucket (hash flood attack)**
- Cause: Attacker crafts keys with same hash code;
  all go to one bucket → O(n) operations
- Java fix: String `hashCode()` randomized in Java 7+ for
  HashMap; Java 8+ converts long chains to Red-Black Trees
  (O(log n) worst case)
- Security note: This is a real attack vector (CVE in many
  web frameworks); Java's response was the treeification

---

### Quick Reference Card

| Concept | One-line |
|---------|---------|
| Chaining | List at each bucket |
| Open addressing | Probe array for next empty slot |
| Load factor | entries / buckets; >0.75 triggers resize |
| Java 8+ bucket | Linked list if <=8, Red-Black Tree if >8 |

---

### Mastery Checklist

- [ ] Can explain both chaining and open addressing
- [ ] Knows Java 8+ HashMap treeification threshold (8)
      and why it was added (hash flood attack defense)
- [ ] Understands load factor and when to pre-size HashMap

---

### Interview Deep-Dive

**Q1 (Hard):** What changed in Java 8 HashMap to address
the hash flood attack, and why?

> Java 8 added treeification: when a bucket's chain exceeds
> 8 entries, it converts from a LinkedList to a TreeMap
> (Red-Black Tree). This makes per-bucket operations
> O(log n) in the worst case instead of O(n). This directly
> addresses hash flood attacks where an adversary crafts
> keys with identical hash codes to force all entries into
> one bucket, turning O(1) operations into O(n). Pre-Java 8,
> this was a documented attack vector (e.g., Tomcat, PHP
> web applications). Java 7 added hash randomization for
> String keys; Java 8 added treeification as a defense
> in depth.
