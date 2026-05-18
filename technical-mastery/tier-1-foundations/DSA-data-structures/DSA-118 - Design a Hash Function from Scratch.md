---
id: DSA-118
title: Design a Hash Function from Scratch
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-012, DSA-013, DSA-014
used_by: DSA-122
related: DSA-012, DSA-083, DSA-084
tags:
  - design
  - hash-function
  - hands-on
  - from-scratch
  - implementation
  - interview
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 118
permalink: /technical-mastery/dsa/hash-function-design/
---

## TL;DR

Designing a hash function requires understanding avalanche
effect, uniform distribution, collision resistance, and
performance trade-offs. From polynomial rolling hash to
MurmurHash3 - knowing the construction reveals why hash
tables work and where they fail.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-118 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | hash function, design, implementation, avalanche |
| **Prerequisites** | DSA-012, DSA-013, DSA-014 |

---

### Requirements for a Good Hash Function

```
1. Deterministic: hash(x) always returns same value
2. Uniform distribution: output spread evenly over [0, 2^N)
3. Avalanche effect: change 1 bit in input -> ~50% output bits flip
4. Fast: O(k) for k-byte input (single pass, no O(k^2) ops)
5. Low collision rate: minimize Pr[hash(a) = hash(b)] for a != b

For non-cryptographic hash tables:
  - Properties 1, 2, 3, 4 are mandatory
  - Property 5 is best-effort (birthday paradox sets floor)
  
For cryptographic hash (SHA-256):
  - All 5 properties + preimage resistance + collision resistance
  - NEVER roll your own cryptographic hash
```

---

### Step-by-Step: Build a String Hash Function

```java
// STEP 1: NAIVE (BAD) - sum of bytes
// Problem: "abc" == "bca" == "cab" (order-independent)
//          anagrams collide
int badHash(String s, int tableSize) {
    int sum = 0;
    for (char c : s.toCharArray()) sum += c;
    return sum % tableSize;
}
// "stop" and "pots" hash to same value. CATASTROPHIC.

// STEP 2: POLYNOMIAL ROLLING HASH (GOOD)
// Position matters: multiply each char by prime^position
int polynomialHash(String s, int tableSize) {
    final int PRIME = 31; // small prime, coprime to tableSize
    long hash = 0;
    long power = 1;
    for (int i = 0; i < s.length(); i++) {
        // Use 'a'=1...'z'=26 (not 'a'=97) to distinguish
        // empty prefix. Otherwise "" and chars starting
        // with null byte would collide.
        hash = (hash + (s.charAt(i) - 'a' + 1) * power)
               % tableSize;
        power = (power * PRIME) % tableSize;
    }
    return (int) hash;
}
// "stop" != "pots": position-sensitive. 
// But: still weak to adversarial inputs targeting collisions.
// Use for competitive programming, not production hash tables.

// STEP 3: FNV-1a (Better - used in real systems)
// FNV = Fowler-Noll-Vo hash. Simple, good distribution.
long fnv1a(byte[] data) {
    long hash = 0xcbf29ce484222325L; // FNV offset basis
    final long FNV_PRIME = 0x00000100000001B3L; // FNV prime
    for (byte b : data) {
        hash ^= (b & 0xFF);        // XOR with byte
        hash *= FNV_PRIME;         // multiply by FNV prime
    }
    return hash;
}
// XOR then multiply ensures avalanche effect.
// Used in: Go's default hash, some JVM symbol tables.

// STEP 4: WHAT JAVA ACTUALLY DOES
// Java String.hashCode() is polynomial with base 31:
// hash = s[0]*31^(n-1) + s[1]*31^(n-2) + ... + s[n-1]
// Equivalent to Horner's method:
// hash = (...((s[0]*31 + s[1])*31 + s[2])...)*31 + s[n-1]
// Problem: Java hashCode is DETERMINISTIC across JVMs
//   Attackers can craft strings with same hashCode to
//   cause HashMap O(n) degradation (HashDoS attack!)
//   Fix: randomized seed (SECURITY LESSON BELOW)
```

---

### Avalanche Effect - Why It Matters

```
BAD: sum-of-bytes hash
  hash("abc") = 97+98+99 = 294
  hash("abd") = 97+98+100 = 295
  Difference: 1 out of 32 bits changed (no avalanche)
  Adjacent keys cluster in same buckets -> O(n) lookup!

GOOD: Polynomial hash or MurmurHash3
  hash("abc") = 0x7B5EE20D (example)
  hash("abd") = 0x3A8FC192 (example)  
  ~50% bits flipped for 1 character change (good avalanche)
  Adjacent keys scattered -> O(1) expected lookup

MurmurHash3 avalanche test:
  Every input bit flips every output bit with probability ~0.5
  This is the "strict avalanche criterion" (SAC)
  SAC is necessary for uniform distribution under any input
```

---

### Security: HashDoS Attack

```java
// VULNERABILITY: Java HashMap before Java 8 + JEP 180
// An attacker can find strings with identical hashCode:
// "Aa" and "BB" have same hashCode in Java!
// "Aa".hashCode() == "BB".hashCode() == 2112

// Exploit: POST request with 65536 parameters all
// mapping to same HashMap bucket -> O(n^2) processing
// This took down PHP, Ruby, Python, Java servers in 2011.

// FIX 1: Java 8 TREE_BIN - HashMap converts chain
// to Red-Black Tree when bucket has 8+ entries.
// Degrades gracefully to O(log n) per bucket.

// FIX 2: Randomized hash seed (added to many languages)
// Python: random hash seed per process startup (since 3.3)
// Ruby: hash randomization enabled by default
// Java: Strings use hashCode() but HashMaps in Java 8+
//       have tree binning as second defense.

// FIX 3: Use SipHash for untrusted input
// SipHash-2-4: keyed hash (secret key per process)
// Can't precompute collisions without knowing key
// Used by Python 3.4+, Rust HashMap, Ruby 2.4+
```

---

### MurmurHash3 - Production Non-Crypto Hash

```java
// Used in: Cassandra, Guava, Kafka, Elasticsearch
// Key features: fast (4 bytes per cycle), good distribution,
//               NOT secure (no secret key, reversible)

// Core idea: mix 4 bytes at a time with bit rotations and XOR
int murmurHash3(byte[] data, int seed) {
    final int c1 = 0xcc9e2d51;
    final int c2 = 0x1b873593;
    int h1 = seed;
    int i = 0;
    // Process 4 bytes at a time
    while (i + 4 <= data.length) {
        int k1 = (data[i] & 0xFF)
               | ((data[i+1] & 0xFF) << 8)
               | ((data[i+2] & 0xFF) << 16)
               | ((data[i+3] & 0xFF) << 24);
        k1 *= c1;
        k1 = Integer.rotateLeft(k1, 15); // rotate
        k1 *= c2;
        h1 ^= k1;
        h1 = Integer.rotateLeft(h1, 13);
        h1 = h1 * 5 + 0xe6546b64;
        i += 4;
    }
    // Final mix (finalization): fmix32
    h1 ^= data.length;
    h1 ^= (h1 >>> 16);
    h1 *= 0x85ebca6b;
    h1 ^= (h1 >>> 13);
    h1 *= 0xc2b2ae35;
    h1 ^= (h1 >>> 16);
    return h1;
}
// Rotation + XOR + multiply with magic constants achieves
// the avalanche effect. Constants are NOT magic - they were
// found by search to maximize the SAC property.
```

---

### When to Choose Which Hash Function

| Scenario | Hash Function | Why |
|----------|---------------|-----|
| Java HashMap key | Java hashCode() | Default, tree binning protection |
| Untrusted web input | SipHash | Keyed, prevents HashDoS |
| Distributed system partition | MurmurHash3 | Fast, good distribution |
| Cryptographic digest | SHA-256 | Collision resistant |
| Rolling hash on string | Polynomial hash (base 31) | Simple, fast, Rabin-Karp |
| Bloom filter hash | MurmurHash3 x k | Multiple independent hashes |
| Checksum | CRC32 | Error detection, not security |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java's hashCode is secure enough for hash tables" | Java hashCode is deterministic and attackers can craft collision inputs. Java 8+ HashMap has tree binning as mitigation, but for high-security use SipHash |
| "A faster hash function means faster HashMap" | The hash function is typically <5% of HashMap time. Load factor, collision resolution strategy, and JVM JIT optimization of the hash function body matter more |
| "You should never write your own hash function" | For general use: correct. But understanding hash construction is essential for debugging collisions, choosing the right hash for Bloom filters, and reasoning about distributed partition strategies |

---

### Failure Mode: Birthday Paradox Collisions

```
With n elements and m buckets:
  Expected collisions ≈ n^2 / (2m)
  For n=70, m=365: E[collisions] ≈ 70^2/730 ≈ 6.7
  (This is why 23 people suffices for 50% birthday collision)

For HashMap with load factor 0.75:
  n = 0.75m elements in m buckets
  E[collisions] ≈ (0.75m)^2 / (2m) = 0.28m per BUCKET expected
  Wait - that's wrong. Per bucket: Poisson with lambda=0.75
  Pr[bucket has k elements] = e^(-0.75) * 0.75^k / k!
  Pr[0 elements] ≈ 0.47, Pr[1] ≈ 0.35, Pr[2] ≈ 0.13,
  Pr[3] ≈ 0.033, Pr[>=8] ≈ 0.0000062 (Java tree threshold)
  
Implication: Even with perfect hash function, birthday
  paradox means some collisions are inevitable. 
  Java's TREEIFY_THRESHOLD=8 is set based on this Poisson
  distribution: P(>=8 elements in bucket) < 1 in 1M buckets.
  (See Java HashMap source comment in java.util.HashMap)
```

---

### Mastery Checklist

- [ ] Can explain why sum-of-bytes fails (anagram collision)
- [ ] Knows Java hashCode is deterministic and the HashDoS attack
- [ ] Can choose correct hash function for a given scenario
- [ ] Understands avalanche effect and why it matters for distribution
- [ ] Knows why Java HashMap uses tree binning at bucket size 8

---

### The Surprising Truth

The constant 31 in Java's String.hashCode() was chosen by
Joshua Bloch for Effective Java (2001) because 31 is a
Mersenne prime and multiplication by 31 can be optimized
to a left shift and subtraction: `31 * i == (i << 5) - i`.
This was significant on hardware without fast integer
multiply (1990s JVMs). Modern hardware has 1-cycle multiply,
making the optimization moot - but 31 persists for backward
compatibility, since Java's hashCode specification is part
of the documented contract and changing it would break
serialized data structures. A 20-year-old hardware
optimization is now frozen into the Java spec forever.
