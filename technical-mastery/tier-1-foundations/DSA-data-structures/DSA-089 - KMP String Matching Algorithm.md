---
id: DSA-089
title: KMP String Matching Algorithm
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-004, DSA-023
used_by: DSA-088
related: DSA-088, DSA-056
tags:
  - algorithms
  - kmp
  - string-matching
  - pattern-matching
  - o-n-m
  - lps
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 89
permalink: /technical-mastery/dsa/kmp-algorithm/
---

## TL;DR

KMP (Knuth-Morris-Pratt) finds all occurrences of pattern P
in text T in O(n+m) using a precomputed "failure function"
that avoids re-examining characters - never backtracking
in the text.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-089 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, KMP, string-matching, LPS-table |
| **Prerequisites** | DSA-004, DSA-023 |

---

### The Problem This Solves

Naive pattern matching: O(n*m). For a 1GB log file with
m=50 pattern, that's 50 billion comparisons. KMP: O(n+m)
= 1 billion comparisons. The key insight: when a mismatch
occurs, the pattern itself tells us where to resume - we
never re-examine text characters.

---

### Textbook Definition

KMP uses a precomputed LPS array (Longest Proper Prefix
which is also Suffix) of length m for the pattern. LPS[i]
= length of longest proper prefix of pattern[0..i] that
is also a suffix. When a mismatch at position j occurs,
resume matching from position LPS[j-1] in the pattern
(not 0). This ensures each character of text is examined
at most twice total.
Build LPS: O(m). Search: O(n). Total: O(n+m).

---

### How It Works

**LPS (failure function) computation:**

```java
// LPS: lps[i] = length of longest proper prefix of pattern[0..i]
// that is also a suffix of pattern[0..i]
int[] buildLPS(String pattern) {
    int m = pattern.length();
    int[] lps = new int[m];
    int len = 0; // length of previous longest prefix-suffix
    int i = 1;
    while (i < m) {
        if (pattern.charAt(i) == pattern.charAt(len)) {
            lps[i++] = ++len;
        } else if (len != 0) {
            len = lps[len - 1]; // try shorter prefix
        } else {
            lps[i++] = 0;
        }
    }
    return lps;
}

// Example: pattern = "ABABCABAB"
// LPS:               [0,0,1,2,0,1,2,3,4]
// LPS[7]=3 means "ABA" is the longest prefix that is also a suffix
```

**KMP search:**

```java
List<Integer> kmpSearch(String text, String pattern) {
    int n = text.length(), m = pattern.length();
    int[] lps = buildLPS(pattern);
    List<Integer> matches = new ArrayList<>();
    int i = 0, j = 0; // i = text index, j = pattern index

    while (i < n) {
        if (text.charAt(i) == pattern.charAt(j)) {
            i++; j++;
            if (j == m) {
                matches.add(i - j); // found at i-j
                j = lps[j - 1]; // continue for next match
            }
        } else if (j > 0) {
            j = lps[j - 1]; // don't advance i; try shorter match
        } else {
            i++; // complete mismatch, advance text
        }
    }
    return matches;
}
```

**The key insight - why it's O(n):**

```
Text:    AABABAB
Pattern: ABABAB

Naive at position 2 after partial match "ABAB":
  Mismatch at position 4! Restart from pattern[0]?
  No! LPS[3] = 2 ("AB" is both prefix and suffix of "ABAB")
  Resume from pattern[2] - we already matched "AB"!

This means i never decreases. Each character examined ≤ 2x.
Total comparisons: O(n + m).
```

---

### Comparison Table

| Algorithm | Preprocessing | Search | Backtrack |
|-----------|-------------|--------|----------|
| Naive | O(1) | O(n*m) worst | Yes |
| KMP | O(m) LPS | O(n) | Never |
| Boyer-Moore | O(m) | O(n/m) best | Yes (pattern-only) |
| Rabin-Karp | O(m) | O(n) avg | Yes if hash match |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "KMP never revisits text characters" | Correct - i only advances, never decreases. j may decrease but text pointer i never backtracks |
| "KMP is always faster than naive" | For short patterns with few partial matches, naive can be faster due to KMP's LPS overhead |

---

### Quick Reference Card

| Property | KMP |
|---------|-----|
| Build LPS | O(m) |
| Search | O(n) |
| Space | O(m) for LPS array |
| Backtracking | Never in text |
| Java built-in | String.indexOf() (uses naive or optimized) |

---

### The Surprising Truth

Java's String.indexOf() does NOT use KMP. It uses a variant
of Boyer-Moore for long patterns but falls back to naive
for short patterns. The JVM JIT often outperforms a naive
implementation for short strings due to CPU vectorization
(SIMD). For production text search against large texts,
use dedicated libraries (Apache Commons Text,
com.google.re2j) rather than implementing KMP manually.

---

### Mastery Checklist

- [ ] Can compute LPS array for a given pattern by hand
- [ ] Implements KMP search from memory
- [ ] Understands why i never decrements (O(n) guarantee)

---

### Interview Deep-Dive

**Q1 (Hard):** Given a string s, find the shortest string
that contains s as a rotation (cyclic pattern).

> Observation: all rotations of s are substrings of s+s.
> To check if t is a rotation of s: check if t is a
> substring of s+s using KMP.
> T = s+s, pattern = t. KMP search in O(2n+m) = O(n).
> This is the classic "rotation check" using KMP.
> Interview insight: transforming a rotation check into
> a substring search is a common "aha" moment; KMP is
> the efficient tool for the substring search step.
