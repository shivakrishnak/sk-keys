---
layout: default
title: "Bloom Filter"
parent: "Data Structures & Algorithms"
nav_order: 44
permalink: /dsa/bloom-filter/
number: "0044"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Hashing Techniques, Bit Manipulation
used_by: Caching, Database Query Optimisation, Networking
related: HashMap, Count-Min Sketch, Cuckoo Filter
tags:
  - datastructure
  - advanced
  - algorithm
  - deep-dive
  - distributed
  - performance
---

# 044 — Bloom Filter

⚡ TL;DR — A Bloom Filter uses multiple hash functions and a bit array to answer "is X in the set?" in O(1) with zero false negatives but some tunable false positives, using a fraction of a HashMap's memory.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #044         │ Category: Data Structures & Algorithms │ Difficulty: ★★★        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Hashing Techniques, Bit Manipulation   │                        │
│ Used by:     │ Caching, Database Optimisation, CDN    │                        │
│ Related:     │ HashMap, Count-Min Sketch, Cuckoo Filter│                       │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A database with 1 billion row IDs must quickly answer "does row X exist before performing an expensive disk read?" Storing all 1 billion IDs in a HashSet requires ~8 GB (8 bytes per 64-bit ID). This exceeds the available in-memory budget for many systems. The alternative — always doing the disk read — burns I/O bandwidth on rows that don't exist ("unnecessary negative lookups"), which can represent 50–90% of all disk reads in sparse databases.

THE BREAKING POINT:
You need membership testing for billions of items with limited memory. HashSets are exact but memory-intensive. Any solution that trades perfect accuracy for a 10× or 100× memory reduction — with **no false negatives** and a tunable false-positive rate — would save enormous I/O and memory costs.

THE INVENTION MOMENT:
Use a bit array (not byte array). Hash each element to k positions and set those bits. A query checks if all k bits are set. If any bit is 0 → definitely not in set. If all bits are 1 → probably in set (might be a false positive from other elements setting the same bits). This structure uses ~10 bits per element vs ~64 bits for a 64-bit pointer. This is exactly why the Bloom Filter was created.

### 📘 Textbook Definition

A **Bloom Filter** is a space-efficient probabilistic data structure that supports membership testing with one-sided errors. It consists of a bit array of m bits (initially all 0) and k independent hash functions. To **add** element x: compute k hash values and set the corresponding bits. To **query** x: check if all k bits are set — if any is 0, x is definitely absent; if all are 1, x is probably present (false positive possible). **False negatives are impossible**; false positives occur with probability ≈ (1 - e^(-kn/m))^k for n elements.

### ⏱️ Understand It in 30 Seconds

**One line:**
A bit array where hashed elements set bits — any missing bit means definitely absent, all bits set means probably present.

**One analogy:**
> Think of a checklist with 1,000 checkboxes. Each person who enters the building must check 3 random boxes (hash functions). To verify "was Alice here?", check Alice's 3 boxes. If any is unchecked, she wasn't. If all 3 are checked, she probably was — but maybe three other people checked those same boxes coincidentally.

**One insight:**
The Bloom filter's power is its asymmetric error model: **no false negatives, some false positives**. This is precisely what you need for cache optimization — if the filter says "definitely not in cache/database," you skip an expensive lookup. You never miss a real hit (no false negative), though you occasionally do a redundant lookup (false positive), which is cheap to verify.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. If x was inserted, all k hash bits MUST be set → query always returns "probably yes" → zero false negatives.
2. If x was NOT inserted, at least one of its k hash bits has probability > 0 of being clear → query might return "probably yes" (false positive) OR "definitely no" (true negative).
3. Elements cannot be deleted (clearing one element's bits might clear bits shared by other elements).

DERIVED DESIGN:
**Optimal k** (number of hash functions): minimise false positive rate. Taking derivatives: `k_optimal = (m/n) × ln(2) ≈ 0.693 × (m/n)`.

**False positive probability**: `p ≈ (1 - e^(-kn/m))^k`. With m=10n (10 bits/element) and k=7: `p ≈ 0.0082` (0.82%). With m=20n, k=14: `p ≈ 0.000063` (0.006%).

**Memory**: 10 bits per element = 1.25 bytes. A HashMap uses 8+ bytes per entry (pointer only) plus key storage. For integer IDs: 10 bits vs 64 bits → 6.4× smaller. For URL strings: 10 bits vs 50+ bytes → 40× smaller.

Can we delete elements? Not from a standard Bloom filter. The Counting Bloom Filter stores counts instead of bits, supporting deletion at 4× the memory cost.

THE TRADE-OFFS:
Gain: 10–100× smaller than HashMap, O(k) = O(1) insert and query, zero false negatives.
Cost: Cannot enumerate members, cannot delete (standard), false positives require tuning, FP rate grows as elements added beyond design capacity.

### 🧪 Thought Experiment

SETUP:
1 billion URLs in a web crawler's "already visited" set. Memory budget: 1.25 GB. HashMap would need ~50 GB for URL strings.

WHAT HAPPENS WITHOUT BLOOM FILTER:
Must use either disk-based storage (100× slower than RAM) or a truncated in-memory set. Re-crawling already seen URLs wastes bandwidth. Missing URLs due to incomplete in-memory set creates an incorrect crawl.

WHAT HAPPENS WITH BLOOM FILTER:
10 bits/URL × 1 billion URLs = 10 billion bits = 1.25 GB. Fits in RAM. False positive rate at 1% means 1% of "new" URLs are wrongly shown as visited — a tiny crawl miss, acceptable for non-critical deduplication. Zero false negatives means a truly already-visited URL is never re-crawled.

THE INSIGHT:
The key question is "which error is more expensive?" In many systems, false negatives (missing a real match) are catastrophic, while false positives (doing one redundant expensive check) are acceptable. Bloom filters are designed for exactly this cost asymmetry.

### 🧠 Mental Model / Analogy

> A Bloom filter is like a passport stamp. When you visit a country, the border officer stamps your passport. To check "have you been to France?", they look at the French stamps ink marks. If no French marks: you've never been. If marks exist: you probably have — but marks can bleed and look similar. The filter is the ink-mark check; your actual passport history is the ground truth.

"Passport page (bits)" → bit array
"Stamp (multiple ink spots)" → k hash positions set to 1
"Looking for French marks" → checking k hash positions
"Ink bleed from another stamp" → false positive

Where this analogy breaks down: Passport stamps are unique per page; hash positions in a Bloom filter are truly shared — multiple elements can set the same bit. There's no way to tell which element set a given bit.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A compact bit array that answers "have I seen this before?" very quickly using very little memory. It's occasionally wrong (says "yes" when the answer is "no") but never says "no" when the answer is "yes."

**Level 2 — How to use it (junior developer):**
Use Guava's `BloomFilter<T>`. `BloomFilter.create(Funnels.stringFunnel(UTF_8), expectedInsertions, falsePositiveProbability)`. Call `put(element)` to add; `mightContain(element)` to query. Never trust "true" as absolute — verify with your data store. Trust "false" absolutely — definitely not present.

**Level 3 — How it works (mid-level engineer):**
Internally: bit array of `m` bits. `put(x)`: for each hash function h₁..hₖ, compute bit index = hᵢ(x) % m, set bit. `mightContain(x)`: for each hᵢ, compute index, check bit — if any is 0, return false; if all are 1, return true. Guava uses a single 128-bit MurmurHash3 and derives k hash values via `hash1 + i * hash2` (Kirsch-Mitzenmacher technique, requires only 2 base hash computations regardless of k).

**Level 4 — Why it was designed this way (senior/staff):**
The Kirsch-Mitzenmacher optimisation (using linear combinations of two hash values to simulate k independent hash functions) is a theoretical result showing no loss of performance vs truly independent hashes, while drastically reducing hash computation. Bloom filters are deployed at scale in: Cassandra (per-SSTable bloom filters to skip disk reads for absent keys), Bitcoin (SPV client transaction monitoring), Chrome Safe Browsing (malicious URL detection), Akamai CDN (one-hit wonder detection to decide whether to cache a response). Facebook's social graph uses them to check if a user has seen a story. The key production concern is: what is the capacity? A filter filled beyond design capacity has a rapidly increasing false positive rate — monitor `n / capacity` ratio.

### ⚙️ How It Works (Mechanism)

**Bit array operations:**
```
Bit array: m=10 bits, k=3 hash functions, initially all 0
[0,0,0,0,0,0,0,0,0,0]

Insert "apple":
  h1("apple") % 10 = 3 → set bit 3
  h2("apple") % 10 = 7 → set bit 7
  h3("apple") % 10 = 1 → set bit 1
[0,1,0,1,0,0,0,1,0,0]

Insert "mango":
  h1("mango") % 10 = 5
  h2("mango") % 10 = 3  ← same as "apple"'s bit 3!
  h3("mango") % 10 = 9
[0,1,0,1,0,1,0,1,0,1]

Query "cherry":
  h1("cherry") % 10 = 2 → bit 2 = 0 → DEFINITELY NOT IN SET
  (return false immediately)

Query "grape":
  h1("grape") % 10 = 1 → bit 1 = 1
  h2("grape") % 10 = 3 → bit 3 = 1
  h3("grape") % 10 = 5 → bit 5 = 1
  All bits set! → PROBABLY IN SET (but "grape" was never inserted!)
  → FALSE POSITIVE
```

**Guava Bloom Filter usage:**
```java
BloomFilter<String> filter = BloomFilter.create(
    Funnels.stringFunnel(Charset.forName("UTF-8")),
    1_000_000,   // expected insertions
    0.01         // 1% false positive probability
);

filter.put("alice@example.com");
filter.put("bob@example.com");

filter.mightContain("alice@example.com"); // true (definitely in)
filter.mightContain("carol@example.com"); // false (definitely NOT in)
filter.mightContain("dave@example.com");  // rare: might be true (FP)
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Request arrives with key K
→ Bloom filter.mightContain(K)?
→ [BLOOM FILTER ← YOU ARE HERE]
→ false → Key definitely absent → skip expensive lookup
→ true  → Key probably present → perform actual lookup
→ Lookup confirms presence or FP
```

FAILURE PATH:
```
More elements than design capacity inserted
→ False positive rate rises rapidly above tuned threshold
→ Every query returns "probably yes"
→ Bloom filter provides no benefit — all lookups proceed
→ Fix: monitor n/capacity ratio; resize or rebuild filter
```

WHAT CHANGES AT SCALE:
At 10 billion elements, with 10 bits/element, you need 12.5 GB per Bloom filter — may exceed single-machine memory. Partition the problem: each shard maintains its own filter for its key range. Distributed Bloom filters across multiple nodes require careful routing. Alternatively, use Count-Min Sketch for approximate frequency counting, or Quotient Filter for deletable membership.

### 💻 Code Example

**Example 1 — Cache pre-check:**
```java
BloomFilter<Long> existsFilter = BloomFilter.create(
    Funnels.longFunnel(),
    10_000_000L, // 10M expected rows
    0.001        // 0.1% FP rate
);
// Load all IDs from DB at startup
allIds.forEach(existsFilter::put);

// On each request:
long requestedId = parseId(request);
if (!existsFilter.mightContain(requestedId)) {
    return Response.notFound(); // skip DB entirely — safe!
}
// Only reach DB for 100% of real IDs
// and 0.1% false positives (will miss in DB, return 404)
Row row = db.findById(requestedId);
return row != null ? Response.ok(row) : Response.notFound();
```

**Example 2 — Custom Bloom filter (no library):**
```java
class BloomFilter {
    private long[] bits;
    private int k; // hash count
    private int m; // bit array size

    BloomFilter(int n, double p) {
        m = (int)(-n * Math.log(p) / (Math.log(2) * Math.log(2)));
        k = (int)(m * 1.0 / n * Math.log(2));
        bits = new long[(m + 63) / 64];
    }

    void add(String s) {
        long h = hash(s);
        for (int i = 0; i < k; i++) {
            int idx = (int)((h + (long)i * (h >>> 32)) % m);
            bits[idx / 64] |= (1L << (idx % 64));
        }
    }

    boolean mightContain(String s) {
        long h = hash(s);
        for (int i = 0; i < k; i++) {
            int idx = (int)((h + (long)i * (h >>> 32)) % m);
            if ((bits[idx / 64] & (1L << (idx % 64))) == 0)
                return false;
        }
        return true;
    }
}
```

### ⚖️ Comparison Table

| Structure | Space | FP | FN | Delete | Best For |
|---|---|---|---|---|---|
| **Bloom Filter** | O(n × bits/elem) | Yes (tunable) | Never | No | Large membership, limited memory |
| HashMap | O(n × entry_size) | Never | Never | Yes | Exact membership |
| HyperLogLog | O(log log n) | N/A (count) | N/A | No | Cardinality estimation |
| Count-Min Sketch | O(ε⁻¹ log δ⁻¹) | Yes | No | No | Frequency estimation |
| Cuckoo Filter | O(n × bits/elem) | Yes (tunable) | Never | Yes | Bloom + deletion support |

How to choose: Use Bloom filter when you need membership testing, can tolerate false positives, and memory is constrained. Use HashMap for exact membership when memory allows. Use Cuckoo filter when deletion is also needed.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bloom filters can have false negatives | False negatives are impossible in standard Bloom filters — if x was inserted, it will always be found |
| You can remove elements from a standard Bloom filter | Standard Bloom filters are append-only; use Counting Bloom Filter or Cuckoo Filter for deletion |
| A filled-to-capacity Bloom filter is still accurate | False positive rate rises rapidly when n > planned capacity; monitor and rebuild before this happens |
| Bloom filter with 0% FP rate is possible | Zero FP rate requires exact set representation — that's a HashSet, not a Bloom filter |
| All hash functions must be truly independent | Kirsch-Mitzenmacher shows two hash functions with linear combinations suffice — fewer hash computations |

### 🚨 Failure Modes & Diagnosis

**1. False positive rate exceeds design threshold**

Symptom: Bloom filter "mightContain" returns true for most queries, including clearly absent items; downstream lookup sees excessive misses.

Root Cause: Number of inserted elements exceeded the design capacity (expectedInsertions parameter). Bits become mostly 1; all k hash positions for any query are likely all 1.

Diagnostic:
```java
// Monitor fill ratio regularly:
System.out.println("Approx inserts: " +
    filter.approximateElementCount());
System.out.println("FP prob: " +
    filter.expectedFpp()); // Guava method
// Alert when > 2× design FP rate
```

Fix: Rebuild filter with larger capacity; or shard the filter by key range.

Prevention: Monitor `approximateElementCount() / expectedInsertions` ratio; alert at 90% capacity.

---

**2. Accepting "true" as definitive (missing false positive handling)**

Symptom: Application returns incorrect data or crashes when Bloom filter returns true but element is absent.

Root Cause: Code treats `mightContain() == true` as a guarantee instead of an indication to verify.

Diagnostic:
```java
// Bug pattern — treating mightContain as definitive:
if (filter.mightContain(key)) {
    return cache.get(key); // can be null on false positive!
}
```

Fix:
```java
if (filter.mightContain(key)) {
    Value v = cache.get(key);
    return v != null ? v : computeOrFetch(key);
}
```

Prevention: Always treat `mightContain()` as a hint, never a guarantee. Document this contract prominently.

---

**3. Serialisation mismatch across restarts**

Symptom: After service restart, Bloom filter behaves as if empty — all previously inserted elements are "not found."

Root Cause: In-memory Bloom filter not persisted to disk on shutdown; rebuilt empty on startup.

Diagnostic:
```bash
# Check logs for "BloomFilter initialized" on startup
# If seen on every restart, filter is ephemeral
```

Fix: Serialise filter state to disk on shutdown; load on startup. Guava: `filter.writeTo(outputStream)` / `BloomFilter.readFrom(inputStream, funnel)`.

Prevention: Treat Bloom filter as a persistent component if it protects against I/O — always persist and restore.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Hashing Techniques` — multiple independent hash functions are the core mechanism.
- `Bit Manipulation` — the bit array and set/check operations require bitwise AND, OR.

**Builds On This (learn these next):**
- `Count-Min Sketch` — extends Bloom filter concept to frequency counting.
- `Consistent Hash Ring` — also uses hashing for scalable distributed membership.

**Alternatives / Comparisons:**
- `HashMap` — exact membership with no false positives; 10–100× more memory per element.
- `Cuckoo Filter` — supports deletion with similar or better FP rates than Bloom filter.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bit array + k hash functions; O(k)=O(1)   │
│              │ membership test with zero false negatives  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Membership testing for billions of items  │
│ SOLVES       │ with GB-scale memory constraint           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "Definitely not" is more useful than       │
│              │ "maybe yes" — skip expensive lookups      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Pre-filtering cache/DB misses; crawl       │
│              │ deduplication; spam/malware URL detection  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ False positives cause critical failures;  │
│              │ deletion is required (use Cuckoo Filter)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ 10-100× less memory vs some false positives│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "10 bits per entry buys you 'definitely   │
│              │  no' for a billion URLs"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hash Ring → Count-Min Sketch   │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Apache Cassandra stores one Bloom filter per SSTable on disk. When a read request arrives for a key, Cassandra checks all SSTable Bloom filters (oldest to newest) before performing any disk reads. As more SSTables accumulate (before compaction), the total false positive rate for a single key lookup increases because you're consulting multiple filters. Derive the combined false positive probability for K filters each with FP rate p, and explain why this makes compaction (reducing SSTable count) a critical correctness and performance operation, not just a storage optimization.

**Q2.** A Content Delivery Network (CDN) uses a Bloom filter to detect "one-hit wonders" — URLs requested only once, which should not be cached. The filter is maintained per time window. For a URL to be cached, it must appear in the filter from the previous time window (meaning it was seen before). Consider: what happens when the Bloom filter's false positive rate is 1%? For a CDN handling 10 billion unique daily requests, how many items would be incorrectly cached due to false positives, and how does this compare to the benefit of avoiding the 0% caching of true one-hit wonders?

