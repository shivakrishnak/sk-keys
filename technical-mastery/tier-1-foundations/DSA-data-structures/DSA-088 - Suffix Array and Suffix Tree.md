---
id: DSA-088
title: Suffix Array and Suffix Tree
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-056, DSA-017
used_by: DSA-077
related: DSA-056, DSA-089
tags:
  - data-structures
  - suffix-array
  - suffix-tree
  - string-processing
  - pattern-matching
  - o-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 88
permalink: /technical-mastery/dsa/suffix-array/
---

## TL;DR

Suffix Array is a sorted array of all suffixes of a string,
enabling O(m log n) pattern search and O(n) Longest Common
Substring - the index behind grep, text editors, and
genome sequencing tools.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-088 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, suffix-array, string-indexing |
| **Prerequisites** | DSA-056, DSA-017 |

---

### The Problem This Solves

"Find all occurrences of pattern P in text T." Brute force:
O(n*m). KMP/Boyer-Moore: O(n+m) but for ONE pattern.
For multiple queries against a fixed text (search engine
index): build a suffix array in O(n log n), then answer
each query in O(m log n). Genome databases with 3 billion
base pairs use suffix arrays to search for genes in seconds.

---

### Textbook Definition

A Suffix Array SA for string s of length n is an array of
indices [0..n-1] sorted such that s[SA[i]..n] < s[SA[i+1]..n]
(all suffixes in lexicographic order). Built in O(n log n)
(sort-based) or O(n) (DC3/SA-IS algorithms).

Pattern search: binary search for P in the sorted suffix
array in O(m log n) where m = pattern length.

Suffix Tree: the trie of all suffixes, compacted. O(n) build,
O(m) search, but O(n) space with high constants.

---

### How It Works

**Suffix Array construction (simple O(n log^2 n)):**

```java
int[] buildSuffixArray(String s) {
    int n = s.length();
    Integer[] sa = new Integer[n];
    for (int i = 0; i < n; i++) sa[i] = i;

    // Sort by suffix starting at each index
    Arrays.sort(sa, (a, b) -> s.substring(a).compareTo(s.substring(b)));
    // O(n log n * n) due to substring comparison
    // For O(n log^2 n): use rank arrays

    int[] result = new int[n];
    for (int i = 0; i < n; i++) result[i] = sa[i];
    return result;
}
```

**Example - "banana":**

```
All suffixes of "banana":
  SA index  Suffix
  5         a
  3         ana
  1         anana
  0         banana
  4         na
  2         nana

Suffix Array: [5, 3, 1, 0, 4, 2]
(indices sorted by their corresponding suffix lexicographically)

Search for "ana":
  Binary search in SA for range where suffix starts with "ana"
  Found at SA[1]=3 ("ana") and SA[2]=1 ("anana")
  Pattern "ana" occurs at positions 1 and 3
```

**LCP Array (Longest Common Prefix):**

```
LCP[i] = length of longest common prefix between
         s[SA[i-1]..] and s[SA[i]..]
"banana" LCP = [0, 1, 3, 0, 0, 2]

Applications:
- Longest repeated substring: max(LCP)
- Number of distinct substrings: n*(n+1)/2 - sum(LCP)
```

**Pattern search with binary search:**

```java
int[] searchPattern(String text, String pattern, int[] sa) {
    // Binary search for leftmost occurrence
    int lo = 0, hi = sa.length - 1;
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        String suffix = text.substring(sa[mid]);
        if (suffix.compareTo(pattern) < 0 ||
            (suffix.length() >= pattern.length() &&
             suffix.substring(0, pattern.length()).equals(pattern)))
            lo = mid + 1;
        else
            hi = mid;
    }
    // [lo, hi] range contains all pattern occurrences
    return new int[]{lo, hi}; // O(m log n) with proper impl
}
```

---

### Comparison Table

| Structure | Build | Search | Space | Use Case |
|-----------|-------|--------|-------|---------|
| Suffix Array | O(n log n) | O(m log n) | O(n) | Multiple pattern searches |
| Suffix Tree | O(n) | O(m) | O(n) but large constant | Optimal but complex |
| KMP | O(n+m) | O(n+m) | O(m) | Single pattern |
| Boyer-Moore | O(n+m) | O(n/m) best | O(m) | Practical single pattern |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Suffix tree is just a trie of all suffixes" | Suffix tree is a COMPRESSED trie (Patricia tree) - edges represent substrings, not single characters; without compression it's O(n^2) space |
| "Suffix array is only for academic problems" | UNIX grep, bioinformatics tools (BWA, Bowtie for DNA alignment), database text search (PostgreSQL's pg_trgm) all use suffix arrays |

---

### Failure Modes & Diagnosis

**Failure: O(n^2) build time with naive suffix sort**
- Cause: Substring comparison in sort comparator is O(n),
  making sort O(n^2 log n)
- Fix: Use rank-based O(n log^2 n) SA construction or
  linear-time SA-IS algorithm for large texts

---

### Quick Reference Card

| Property | Suffix Array |
|---------|-------------|
| Build | O(n log n) practical; O(n) SA-IS |
| Pattern search | O(m log n) with binary search |
| Space | O(n) integers |
| LCP computation | O(n) with Kasai's algorithm |
| Best for | Pre-indexing fixed text, multiple queries |

---

### The Surprising Truth

Human genome sequencing relies on suffix arrays. The BWA
(Burrows-Wheeler Aligner) tool, used by hospitals worldwide
to analyze patient DNA, builds a suffix array (via BWT
transform) of the 3-billion-character human reference genome.
A patient's sequenced reads are then searched against this
index in seconds. Without suffix arrays, genome alignment
would take weeks instead of hours. The algorithm that
made personalized medicine and rapid COVID-19 variant
identification possible is a sorted array of string suffixes.

---

### Mastery Checklist

- [ ] Can construct a suffix array for a short string by hand
- [ ] Understands binary search on suffix array for pattern search
- [ ] Knows the genomics application

---

### Interview Deep-Dive

**Q1 (Hard):** Find the longest repeated substring in a
string of length n efficiently.

> Build suffix array: O(n log n).
> Build LCP array (Kasai's algorithm): O(n).
> Longest repeated substring = max(LCP[i]) for all i.
> The substring is s[SA[i]..SA[i]+LCP[i]].
> 
> Example: "banana"
> LCP array = [0, 1, 3, 0, 0, 2]
> Max = 3 at index 2, SA[2]=1: "banana"[1..4] = "ana"
> Longest repeated substring = "ana" (appears at index 1 and 3)
> 
> Total time: O(n log n) for SA + O(n) for LCP = O(n log n).
> Space: O(n).
> Brute force: O(n^2) with set of all substrings.
