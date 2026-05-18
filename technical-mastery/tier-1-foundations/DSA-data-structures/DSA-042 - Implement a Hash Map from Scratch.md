---
id: DSA-042
title: Implement a Hash Map from Scratch
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-014, DSA-033
used_by: DSA-086
related: DSA-014, DSA-033, DSA-045
tags:
  - data-structures
  - hash-map
  - implementation
  - chaining
  - load-factor
  - resize
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/dsa/implement-hash-map-from-scratch/
---

## TL;DR

Building a HashMap from scratch requires: a hash function
mapping keys to buckets, chaining to handle collisions,
and dynamic resizing when load factor exceeds 0.75 - the
same mechanics as Java's HashMap.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-042 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, hash-map, implementation |
| **Prerequisites** | DSA-014, DSA-033 |

---

### The Problem This Solves

Using HashMap is a skill. Understanding how it works inside
- hash function, bucket array, chaining, load factor, resize
- lets you diagnose performance problems, understand Java 8
treeification, and pass system-design interviews that probe
data structure internals.

---

### How It Works

**Minimal HashMap implementation:**

```java
class SimpleHashMap<K, V> {
    private static final int INITIAL_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;

    private Object[] buckets;   // each bucket: linked list
    private int size = 0;
    private int capacity;

    // Entry node for chaining
    private static class Entry<K, V> {
        K key; V value; Entry<K, V> next;
        Entry(K key, V value) { this.key = key; this.value = value; }
    }

    SimpleHashMap() {
        capacity = INITIAL_CAPACITY;
        buckets = new Object[capacity];
    }

    // Hash to bucket index
    private int bucketIndex(K key) {
        int hash = key == null ? 0 : key.hashCode();
        // spread high bits (like Java's HashMap.hash())
        hash = hash ^ (hash >>> 16);
        return Math.abs(hash % capacity);
    }

    @SuppressWarnings("unchecked")
    void put(K key, V value) {
        if ((float) size / capacity >= LOAD_FACTOR) resize();

        int idx = bucketIndex(key);
        Entry<K, V> head = (Entry<K, V>) buckets[idx];

        // Update if key exists
        for (Entry<K, V> e = head; e != null; e = e.next) {
            if (e.key.equals(key)) { e.value = value; return; }
        }
        // Insert at head of chain
        Entry<K, V> entry = new Entry<>(key, value);
        entry.next = head;
        buckets[idx] = entry;
        size++;
    }

    @SuppressWarnings("unchecked")
    V get(K key) {
        int idx = bucketIndex(key);
        for (Entry<K, V> e = (Entry<K, V>) buckets[idx];
             e != null; e = e.next) {
            if (e.key.equals(key)) return e.value;
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private void resize() {
        Object[] old = buckets;
        capacity *= 2;
        buckets = new Object[capacity];
        size = 0;
        for (Object b : old) {
            for (Entry<K, V> e = (Entry<K, V>) b;
                 e != null; e = e.next) {
                put(e.key, e.value);  // re-hash all entries
            }
        }
    }
}
```

**Key design decisions:**

| Decision | Why |
|---------|-----|
| Load factor 0.75 | Balance: 0.5 = too much resize, 1.0 = too many collisions |
| Capacity power of 2 | `hash & (capacity-1)` faster than `hash % capacity` |
| Hash spreading `h ^ (h>>>16)` | Prevents collisions in low bits from poor hashCode |
| Resize doubles capacity | Amortized O(1) insert (geometric growth) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "HashMap always uses % for bucket index" | Java uses `hash & (capacity-1)` (capacity is always power of 2) which is faster than modulo |
| "Resizing is O(1)" | A single resize is O(n) but amortized over n inserts it is O(1) per insert |

---

### Quick Reference Card

| Component | Purpose |
|-----------|---------|
| Hash function | Key → bucket index |
| Bucket array | Stores chain heads |
| Chaining | Handles collisions |
| Load factor | Triggers resize |
| Resize | Doubles capacity, re-hashes |

---

### Mastery Checklist

- [ ] Can implement put/get with chaining from memory
- [ ] Can explain load factor, resize trigger, and
      amortized O(1) insert
- [ ] Understands Java HashMap's hash spreading trick
      and why capacity is always a power of 2

---

### Interview Deep-Dive

**Q1 (Hard):** Why is Java HashMap's capacity always
a power of 2, and what optimization does this enable?

> When capacity is a power of 2, `hash % capacity` equals
> `hash & (capacity - 1)` because capacity - 1 is all 1s
> in binary. Bitwise AND is significantly faster than
> modulo division. For example, capacity=16:
> capacity-1 = 15 = 0b00001111. Any hash & 0b00001111
> keeps only the last 4 bits = same as hash % 16.
> This is why HashMap grows from 16 to 32 to 64 (doubles)
> rather than 16 to 32 to 48 (adding 16). Java also
> applies hash spreading (`h ^ h>>>16`) to distribute
> high-bit information to low bits, preventing clustered
> collisions when many keys share the same low-bit pattern.
