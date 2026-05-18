---
id: DSA-083
title: Bloom Filter
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-014, DSA-023
used_by: DSA-077, DSA-105
related: DSA-084, DSA-085, DSA-014
tags:
  - data-structures
  - bloom-filter
  - probabilistic
  - false-positive
  - membership-check
  - space-efficient
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/dsa/bloom-filter/
---

## TL;DR

A Bloom Filter answers "is X in the set?" with zero false
negatives and configurable false positive rate, using a
fraction of the space of a hash set - the data structure
behind database query optimizers and distributed caches.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-083 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, bloom-filter, probabilistic |
| **Prerequisites** | DSA-014, DSA-023 |

---

### The Problem This Solves

"Has user X ever registered?" Checking a database table
of 1 billion users: disk I/O, 10-100ms. A HashSet in RAM:
1B * 8 bytes = 8GB just for user IDs. A Bloom filter with
1% false positive rate: ~1.2 bytes per element × 1B = 1.2GB.
1/7th the space with ~1ms answer time, and GUARANTEED no
false negatives (no new registrations missed).

---

### Textbook Definition

A Bloom Filter is a probabilistic space-efficient data
structure that tests set membership. Uses a bit array of
size m and k independent hash functions. Insert: set k
bits corresponding to k hash values. Query: check if all
k bits are set. False negatives: impossible. False positives:
possible with probability ~(1-e^(-kn/m))^k where n = items.
Cannot delete elements (standard Bloom filter).

---

### How It Works

**Implementation:**

```java
class BloomFilter {
    private final BitSet bits;
    private final int size;
    private final int numHashFunctions;

    BloomFilter(int expectedItems, double falsePositiveRate) {
        // Optimal bit array size: m = -n*ln(p) / (ln2)^2
        this.size = (int) (-expectedItems
            * Math.log(falsePositiveRate)
            / (Math.log(2) * Math.log(2)));
        // Optimal hash functions: k = (m/n) * ln2
        this.numHashFunctions = (int) Math.max(1,
            Math.round((double) size / expectedItems * Math.log(2)));
        this.bits = new BitSet(size);
    }

    // Multiple hash functions via double hashing trick
    private int[] getHashPositions(String item) {
        int hash1 = item.hashCode();
        int hash2 = item.hashCode() ^ (item.hashCode() >>> 16);
        int[] positions = new int[numHashFunctions];
        for (int i = 0; i < numHashFunctions; i++) {
            positions[i] = Math.abs((hash1 + i * hash2) % size);
        }
        return positions;
    }

    void add(String item) {
        for (int pos : getHashPositions(item)) bits.set(pos);
    }

    boolean mightContain(String item) {
        for (int pos : getHashPositions(item)) {
            if (!bits.get(pos)) return false; // DEFINITE NO
        }
        return true; // PROBABLE YES (may be false positive)
    }
}

// Usage with guaranteed semantics:
BloomFilter bf = new BloomFilter(1_000_000, 0.01); // 1% FP rate
bf.add("user123");
bf.mightContain("user123"); // true (definitely in set)
bf.mightContain("user456"); // false = definitely not in set
                             // true = probably in set (1% chance false)
```

**Production usage - database query optimization:**

```
PostgreSQL uses Bloom filters to avoid disk reads:
  Query: WHERE id IN (1, 5, 7, 99, 200, ...)
  
  Without Bloom filter: check index for each ID
  With Bloom filter on index pages:
    - Check Bloom filter first (in memory, nanoseconds)
    - If "definitely not in page": skip disk read
    - If "maybe in page": do disk read
    
  Result: 80-90% of disk reads eliminated for selective queries
  
  Enable in PostgreSQL:
  CREATE INDEX USING bloom ON table(column);
```

---

### Comparison Table

| Property | HashSet | Bloom Filter |
|---------|---------|-------------|
| False negatives | No | No |
| False positives | No | Yes (configurable rate) |
| Space | O(n) | O(n * constant, 8-12 bits/item) |
| Delete | Yes | No (standard) |
| Membership check | O(1) exact | O(k) approx |
| 1M items at 1% FP | ~8MB | ~1.2MB |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Bloom filter can give false negatives" | Never. If an item was added, it will always return true. Only false positives are possible |
| "Bloom filter with too many items becomes useless" | It becomes a "definitely contains everything" filter (all bits set = all queries return true = 100% FP rate, 0% useful) |

---

### Failure Modes & Diagnosis

**Failure: False positive rate much higher than configured**
- Cause: More items inserted than expectedItems parameter
  causes bit array saturation
- Diagnosis: Track item count; `FP_rate ≈ (1 - e^(-k*n/m))^k`
- Fix: Size the filter generously (2x expected); or use
  a growing Bloom filter (scalable Bloom filter)

---

### Quick Reference Card

| Property | Bloom Filter |
|---------|-------------|
| False negatives | Impossible |
| False positives | Yes (tunable) |
| Space | ~10 bits/item for 1% FP |
| Add | O(k) |
| Contains | O(k) |
| Delete | Not supported |
| Real usage | PostgreSQL index, Redis, Cassandra |

---

### The Surprising Truth

Google's Bigtable uses Bloom filters to skip SSTables
that don't contain a queried key. Without Bloom filters,
a Bigtable read would check ALL SSTables on disk for the
key (one disk I/O each). With Bloom filters (one per
SSTable, in memory), 90-99% of unnecessary disk reads are
eliminated. The entire performance of Bigtable's read
path depends on Bloom filter accuracy. This same pattern
is used in Apache Cassandra, RocksDB, and LevelDB.

---

### Mastery Checklist

- [ ] Can explain the false-negative impossibility proof
- [ ] Knows the production use cases (DB, cache, streaming)
- [ ] Can calculate approximate size for a given FP rate

---

### Interview Deep-Dive

**Q1 (Hard):** You're building a URL shortener. How would
you use a Bloom filter to improve performance?

> Use case: check if a generated short URL already exists
> before inserting into the database.
> Without Bloom filter: DB query per generated URL (10ms).
> With Bloom filter: check Bloom filter in memory first.
> - "Definitely not in DB" → insert directly (no DB check)
> - "Maybe in DB" → check DB to resolve the 1% false positive
> 
> For 100M short URLs at 1% FP rate: ~120MB Bloom filter
> in RAM, 99% of insert attempts skip the DB read entirely.
> Trade-off: 1% of inserts still query DB (false positive),
> but no incorrect "not found" results.
> Similar pattern: Google Chrome's Safe Browsing uses
> Bloom filters to check URLs against malware lists without
> hitting a server for every URL visited.
