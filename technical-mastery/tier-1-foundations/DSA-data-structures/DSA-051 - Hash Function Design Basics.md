---
id: DSA-051
title: Hash Function Design Basics
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-014, DSA-033
used_by: DSA-083, DSA-086
related: DSA-033, DSA-042, DSA-083
tags:
  - algorithms
  - hashing
  - hash-function
  - distribution
  - security
  - collision
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/dsa/hash-function-design-basics/
---

## TL;DR

A hash function maps any input to a fixed-size output -
good hash functions are deterministic, fast, and distribute
outputs uniformly; bad ones cause O(n) HashMap performance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-051 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, hashing, hash-function, distribution |
| **Prerequisites** | DSA-014, DSA-033 |

---

### The Problem This Solves

HashMap performance depends entirely on the quality of
`hashCode()`. A good hash function distributes keys
uniformly across buckets. A bad one clusters keys in
a few buckets, causing O(n) operations instead of O(1).

---

### Properties of a Good Hash Function

| Property | Meaning |
|---------|---------|
| Deterministic | Same input always produces same hash |
| Uniform distribution | All outputs equally likely |
| Fast | O(1) computation |
| Avalanche effect | Small input change → very different hash |
| Non-reversible (cryptographic) | Cannot recover input from hash |

---

### How It Works

**Java String hashCode() implementation:**

```java
// Java's String hashCode:
// h = 31 * h + char[i] for each character
// Why 31? Prime number, compiles to (h << 5) - h (fast)
// "abc" = 31*(31*'a' + 'b') + 'c'
//       = 31*(31*97 + 98) + 99
//       = 96354

public int hashCode(String s) {
    int h = 0;
    for (char c : s.toCharArray()) {
        h = 31 * h + c;
    }
    return h;
}
```

**Custom hashCode() for user objects:**

```java
// BAD: always returns same value → O(n) HashMap
@Override
public int hashCode() {
    return 42;  // CATASTROPHIC: all keys in one bucket!
}

// BAD: uses mutable field → breaks HashMap after mutation
@Override
public int hashCode() {
    return Objects.hash(name, mutableField); // BAD
}

// GOOD: uses immutable identifying fields
// Must be consistent with equals()
@Override
public int hashCode() {
    return Objects.hash(id, email); // immutable, identifying
}
// Contract: if a.equals(b), then a.hashCode() == b.hashCode()
// (reverse not required - collisions are normal)
```

**Why prime numbers in hash functions?**

```
Multiplying by a prime (31, 37, 127) distributes bits
across more output positions. Non-prime multipliers
create more structure in the low bits.

31 is especially chosen: 31 * h = (h << 5) - h
CPU can compute this with a shift and subtract (faster
than general multiplication on older CPUs).
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Hash functions for HashMap should be cryptographic" | Cryptographic hashes (SHA-256) are 10,000x slower than HashMap needs; use fast non-crypto hashes |
| "Same hashCode means equal objects" | Same hashCode may be a collision; always verify with equals() |
| "hashCode needs to be unique per object" | Uniqueness impossible (infinite inputs, finite int outputs); only equality requirement is `equals → same hash` |

---

### Failure Modes & Diagnosis

**Failure: HashMap all keys in one bucket**
- Cause: `hashCode()` returns constant or very limited values
- Diagnosis: Map with 10,000 entries has O(n) get time;
  add debugging to print bucket distribution
- Security note: Attackers can craft keys with identical
  hashCodes to degrade HashMap to O(n) - Java 8+ mitigates
  with treeification

---

### Quick Reference Card

| Requirement | Standard | Violation |
|------------|---------|---------|
| Consistency | `equals(b)` ⟹ `same hashCode` | Silent bugs |
| Immutability | Hash only immutable fields | Break if mutated |
| Speed | O(1) | Slow all HashMap ops |
| Distribution | Uniform | O(n) worst case |

---

### Mastery Checklist

- [ ] Knows the hashCode-equals contract
- [ ] Knows to only hash immutable fields in custom objects
- [ ] Understands why constant hashCode is catastrophic

---

### Interview Deep-Dive

**Q1 (Medium):** You have a `Person` class with name and
ssn. You want to use Person as a HashMap key. What fields
do you include in hashCode() and what is the contract?

> Use immutable identifying fields. SSN is the unique
> identifier (immutable), name might not be unique.
> `hashCode()` = `Objects.hash(ssn)`. The contract:
> if `a.equals(b)` is true, `a.hashCode() == b.hashCode()`
> MUST hold. So `equals()` must also use SSN only.
> Never use mutable fields (name could change after the
> Person is inserted in the map, breaking lookup).
> Java's `Objects.hash()` handles null safety and combines
> multiple fields using prime multiplication correctly.
