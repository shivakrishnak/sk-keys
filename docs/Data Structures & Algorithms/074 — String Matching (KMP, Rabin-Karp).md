---
layout: default
title: "String Matching (KMP, Rabin-Karp)"
parent: "Data Structures & Algorithms"
nav_order: 74
permalink: /dsa/string-matching/
number: "0074"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Array, String, Hashing Techniques, Time Complexity / Big-O
used_by: Suffix Array, Full-Text Search, Intrusion Detection Systems
related: Trie, Suffix Array, Aho-Corasick
tags:
  - algorithm
  - advanced
  - deep-dive
  - pattern
  - datastructure
---

# 074 — String Matching (KMP, Rabin-Karp)

⚡ TL;DR — KMP and Rabin-Karp find a pattern in text in O(N+M) by never re-examining characters already known to be mismatched.

| #0074 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Array, String, Hashing Techniques, Time Complexity / Big-O | |
| **Used by:** | Suffix Array, Full-Text Search, Intrusion Detection Systems | |
| **Related:** | Trie, Suffix Array, Aho-Corasick | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Find pattern "ABCABD" in text "ABCABCABCABD" (length N=12). The naïve algorithm tries every starting position: align pattern at text[0], compare 6 characters — mismatch at position 5. Shift by 1, align at text[1], compare again from scratch. For text of length N and pattern of length M, worst case: N × M comparisons = O(N×M).

THE BREAKING POINT:
For a virus scanner checking a 1 GB log file for a malicious 100-byte signature, O(N×M) = 10⁹ × 100 = 10¹¹ comparisons — over 100 seconds on modern hardware. For intrusion detection on 10 Gbps network traffic, the system falls behind in milliseconds.

THE INVENTION MOMENT:
When the naïve algorithm encounters a mismatch after matching k characters of the pattern, it discards all information about those k matched characters. But that matched prefix tells you exactly how far you can shift the pattern forward without missing a match — because the longest proper prefix of the matched portion that is also a suffix determines the next valid alignment. This is the KMP insight. Rabin-Karp uses a different insight: hash the pattern, then slide a rolling hash over the text — full comparison only on hash matches. Both achieve O(N+M). This is exactly why **String Matching algorithms** were created.

---

### 📘 Textbook Definition

**String Matching** is the problem of finding all occurrences of a pattern string P (length M) within a text string T (length N). **Knuth-Morris-Pratt (KMP)** preprocesses the pattern into a **failure function** (or partial match table) `lps[]` that encodes, for each prefix of P, the length of its longest proper prefix which is also a suffix. This allows the pattern to skip positions on mismatch without re-examining text characters, achieving O(N+M). **Rabin-Karp** uses polynomial rolling hashing to compute window hashes in O(1) per slide, reducing comparisons to hash mismatches; it runs O(N+M) average but O(N×M) worst case (many hash collisions). Both algorithms are optimal for single-pattern matching in the RAM model.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pre-process the pattern to avoid re-reading text you've already matched when a mismatch occurs.

**One analogy:**
> Searching for "ABAB" in a book. When you match "ABA" then fail on the 4th, naïve search goes back to the start: "okay, let's try starting one character later." KMP says: "I already know the current text position ends with 'AB' — which is the first two characters of my pattern — so I can restart my pattern comparison from position 2, not 0." You don't re-read what you already matched.

**One insight:**
KMP's `lps` (longest proper prefix/suffix) array is the key. `lps[i]` tells you: "after a mismatch at pattern position i+1, you can safely jump the pattern to position `lps[i]` and resume — the text pointer never moves backward." Building `lps` takes O(M) and the search takes O(N) — one forward pass of the text, total O(N+M).

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The text pointer `i` never moves backward in KMP — it only ever advances.
2. `lps[k]` = length of the longest proper prefix of `pattern[0..k]` that is also a suffix of `pattern[0..k]`. This is precomputed in O(M).
3. On mismatch at `(text[i], pattern[j])`, instead of shifting by 1, shift the pattern by `j - lps[j-1]` positions — equivalent to setting `j = lps[j-1]`. Total pattern shifts across the entire search ≤ N.

DERIVED DESIGN:
The KMP failure function encodes overlapping structure in the pattern. For "ABCABD": `lps = [0,0,0,1,2,0]`. After matching "ABCAB" then failing on "D", `j = lps[4] = 2`, meaning restart comparison at pattern[2] ("C") — the text has already matched the "AB" prefix of "AB C ABD" for free.

**Rabin-Karp rolling hash:**
Hash a window of length M: `H(s[i..i+M-1]) = (s[i]·b^(M-1) + s[i+1]·b^(M-2) + ... + s[i+M-1]) mod p`. Sliding one position: remove the contribution of `s[i]` and add `s[i+M]`. This is O(1) per slide using modular arithmetic. Only when `H(window) == H(pattern)` do we perform a full O(M) character comparison to confirm (avoiding hash collision false positives).

THE TRADE-OFFS:
KMP: guaranteed O(N+M), O(M) preprocessing, no false positives, text pointer never retreats. Cost: moderate implementation complexity; the `lps` table logic is non-obvious.
Rabin-Karp: O(N+M) expected, O(N×M) worst case (many collisions), but trivially extends to multiple patterns (check against a hash set). Naturally handles 2D pattern matching.
Both: O(M) extra space for the failure function / pattern hash.

---

### 🧪 Thought Experiment

SETUP:
Text `T = "AAAAAB"`, Pattern `P = "AAAB"` (N=6, M=4).

WHAT HAPPENS WITH NAÏVE:
- Align at T[0]: compare 'A','A','A','B' vs P[0..3]. T[3]='A' ≠ P[3]='B'. Mismatch at 3. Shift 1.
- Align at T[1]: compare T[1..4]='AAAB' vs P. T[4]='A' ≠ P[3]='B'. Shift 1.
- Align at T[2]: T[2..5]='AAAB' vs P. T[5]='B'=P[3]. Match! But cost: 3+3+4=10 comparisons.

WHAT HAPPENS WITH KMP:
- `lps` for "AAAB": at 'A','A','A','B': lps=[0,1,2,0].
- i=0,j=0: T[0]='A'=P[0] → j=1.
- i=1,j=1: T[1]='A'=P[1] → j=2.
- i=2,j=2: T[2]='A'=P[2] → j=3.
- i=3,j=3: T[3]='A'≠P[3]='B'. Mismatch. j = lps[2] = 2. i stays at 3.
- i=3,j=2: T[3]='A'=P[2] → j=3.
- i=4,j=3: T[4]='A'≠P[3]='B'. j = lps[2] = 2. i stays at 4.
- i=4,j=2: T[4]='A'=P[2] → j=3.
- i=5,j=3: T[5]='B'=P[3] → j=4. j==M → MATCH at i-M+1=2. Total: 8 comparisons.

THE INSIGHT:
KMP's text pointer `i` only ever moved forward — never back. Even in the worst case of "AAAA...AB"-style inputs that cost O(N×M) naïvely, KMP stays O(N+M) because the lps table encodes the "already matched" prefix length, preventing re-examination.

---

### 🧠 Mental Model / Analogy

> KMP is a detective reviewing evidence. When you fail to match a suspect's alibi at step 7, you don't throw away everything you verified in steps 1–6. Instead, you look at your notes: "I confirmed steps 1–4 already match the beginning of the alibi. So when I resume, start from step 4, not step 1." The `lps` array is your notes.

"Detective's notes" → `lps` failure function
"Current suspect position (already matched)" → current `j` value
"Failed at step j+1" → mismatch at `pattern[j]` vs `text[i]`
"Resume from lps[j-1]" → `j = lps[j-1]`
"Text pointer i never retreats" → never re-examine confirmed text

Where this analogy breaks down: The analogy suggests going backward in the investigation; KMP never re-examines text characters — only the pattern pointer retreats. The text pointer is strictly monotone.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
String Matching algorithms find where a short word (pattern) appears inside a long text. The smart version avoids re-reading text it already checked by remembering which part of the pattern it had already matched before a mismatch — like not re-reading a paragraph you already understood just because the next sentence didn't fit.

**Level 2 — How to use it (junior developer):**
For most production use cases, use the language standard library: Java `String.indexOf()` (uses naive but tuned for JIT), Python `in` operator, `str.find`. Use KMP explicitly when you need guaranteed O(N+M) or when the naïve approach proves to be a bottleneck in profiling. For multiple patterns simultaneously, use Aho-Corasick (generalization of KMP).

**Level 3 — How it works (mid-level engineer):**
KMP builds the `lps` table in O(M) using the invariant that `lps[i]` is computed from `lps[i-1]`. If `pattern[i] == pattern[lps[i-1]]`, then `lps[i] = lps[i-1] + 1`. Otherwise, use `lps[lps[i-1]-1]` to try shorter prefix-suffixes — the same logic as the search phase. Rabin-Karp uses a rolling polynomial hash modulo a large prime; collision probability per window is ~M/p (use large p to keep this tiny). The slide is `H_new = (H_old × b - s[i] × b^M + s[i+M]) mod p`.

**Level 4 — Why it was designed this way (senior/staff):**
KMP was independently published by Knuth, Morris, and Pratt in 1977. Its `lps` function is equivalent to the **border function** in stringology — the pattern's self-overlapping structure. This generalises: Aho-Corasick builds a trie of all patterns and computes failure links (equivalent to `lps` across the trie), enabling simultaneous O(N + total pattern length) matching for thousands of patterns — used in intrusion detection systems (Snort), virus scanners (ClamAV), and DNA sequence analysis. The lower bound for single-pattern matching is Ω(N/M) — KMP achieves O(N) which is optimal for M ≥ 1. For very short patterns (M ≤ 4), CPU SIMD instructions (SSE4.2 `pcmpistri`) outperform KMP due to instruction-level parallelism.

---

### ⚙️ How It Works (Mechanism)

**KMP Phase 1: Build LPS Table**

```
┌────────────────────────────────────────────────┐
│ LPS for pattern "ABCABD"                       │
│                                                │
│ i=0: P[0]='A'  → lps[0]=0  (basis case)       │
│ i=1: P[1]='B'  ≠ P[0]='A' → lps[1]=0         │
│ i=2: P[2]='C'  ≠ P[0]='A' → lps[2]=0         │
│ i=3: P[3]='A'  = P[0]='A' → lps[3]=1         │
│ i=4: P[4]='B'  = P[1]='B' → lps[4]=2         │
│ i=5: P[5]='D'  ≠ P[2]='C' → try lps[1]=0     │
│       P[5]='D' ≠ P[0]='A' → lps[5]=0         │
│                                                │
│ lps = [0, 0, 0, 1, 2, 0]                      │
└────────────────────────────────────────────────┘
```

**KMP Phase 2: Search**

```
┌────────────────────────────────────────────────┐
│ Text:    ABCABCABCABD                          │
│ Pattern: ABCABD                                │
│                                                │
│ i=0..4: match A,B,C,A,B → j=5                 │
│ i=5: text='C' ≠ pattern[5]='D'                │
│       j = lps[4] = 2  ← don't restart at 0!   │
│ i=5: text='C' = pattern[2]='C' → j=3          │
│ i=6..8: match A,B,C → continues               │
│ i=9..10: match A,B → j=5                      │
│ i=11: text='D'=pattern[5]='D' → j=6==M        │
│       MATCH at position 11-6+1 = 6            │
└────────────────────────────────────────────────┘
```

**Rabin-Karp Rolling Hash:**

```
┌────────────────────────────────────────────────┐
│ Rabin-Karp: slide window of size M             │
│                                                │
│ Pattern hash: H(P) computed once → O(M)        │
│ First window hash: H(T[0..M-1]) → O(M)         │
│                                                │
│ Slide to next window:                          │
│   H_new = (H_old * b                          │
│            - T[i] * b^M                       │
│            + T[i+M]) mod p                    │
│   → O(1) per slide                            │
│                                                │
│ On hash match: full compare O(M)               │
│ If true match → record; always continue        │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Long text T (e.g., log file, genome, network packet)
→ Short pattern P (e.g., error signature, gene, malware)
→ [STRING MATCHING ← YOU ARE HERE]
  KMP: Preprocess P → lps[] in O(M)
       Scan T with text pointer advancing only → O(N)
  Rabin-Karp: Hash P;
       Roll hash across T, full compare on match
→ Return all match positions in O(N+M)
→ Downstream: alert, replace, extract
```

FAILURE PATH:
```
Hash collision in Rabin-Karp
→ Full O(M) character compare triggered for false positive
→ Many collisions → degrades to O(N*M)
→ Fix: use double hashing (two independent hash functions)
→ Or: switch to KMP for guaranteed O(N+M)
```

WHAT CHANGES AT SCALE:
In production search engines (Elasticsearch), full-text search is NOT done with KMP/Rabin-Karp per query. Text is preprocessed into an inverted index: each word → [list of document IDs + positions]. At query time, lookup is O(1) per term, O(K log D) to intersect K result lists of D documents. KMP is used at index-build time for tokenization and at the data-structure level for wildcard queries. For DNA databases (~3 billion base pairs), suffix arrays and BWT (FM-index) enable O(M log N) search with sublinear space.

---

### 💻 Code Example

**Example 1 — KMP build LPS:**
```java
int[] buildLPS(String pattern) {
    int m = pattern.length();
    int[] lps = new int[m];
    int len = 0, i = 1;
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
```

**Example 2 — KMP search:**
```java
List<Integer> kmpSearch(String text, String pattern) {
    int n = text.length(), m = pattern.length();
    int[] lps = buildLPS(pattern);
    List<Integer> matches = new ArrayList<>();
    int i = 0, j = 0; // text and pattern pointers
    while (i < n) {
        if (text.charAt(i) == pattern.charAt(j)) {
            i++; j++;
        }
        if (j == m) {
            matches.add(i - j); // match found
            j = lps[j - 1];    // look for next match
        } else if (i < n &&
                   text.charAt(i) != pattern.charAt(j)) {
            if (j != 0) j = lps[j - 1]; // shift pattern
            else i++;
        }
    }
    return matches;
}
```

**Example 3 — Rabin-Karp:**
```java
List<Integer> rabinKarp(String text, String pattern) {
    int n = text.length(), m = pattern.length();
    final long BASE = 31, MOD = 1_000_000_007L;
    long pw = 1;
    for (int i = 0; i < m - 1; i++) pw = pw * BASE % MOD;
    // Compute pattern hash and first window hash
    long ph = 0, wh = 0;
    for (int i = 0; i < m; i++) {
        ph = (ph * BASE + pattern.charAt(i)) % MOD;
        wh = (wh * BASE + text.charAt(i)) % MOD;
    }
    List<Integer> matches = new ArrayList<>();
    for (int i = 0; i <= n - m; i++) {
        if (wh == ph) { // hash match: verify
            if (text.substring(i, i + m).equals(pattern))
                matches.add(i);
        }
        if (i < n - m) // slide window
            wh = (wh - text.charAt(i) * pw % MOD
                  + MOD) % MOD;
            wh = (wh * BASE + text.charAt(i + m)) % MOD;
    }
    return matches;
}
```

**Example 4 — Java built-in (production use):**
```java
// Java String.indexOf() — fine for most production use
int idx = text.indexOf(pattern); // first occurrence
// Find all occurrences:
int pos = 0;
while ((pos = text.indexOf(pattern, pos)) != -1) {
    System.out.println("Found at: " + pos);
    pos += pattern.length(); // or pos++ to find overlapping
}
```

---

### ⚖️ Comparison Table

| Algorithm | Preprocessing | Search | Worst Case | Multiple Patterns |
|---|---|---|---|---|
| **KMP** | O(M) | O(N) | O(N+M) | No (use Aho-Corasick) |
| **Rabin-Karp** | O(M) | O(N) avg | O(N×M) | Yes (hash set) |
| Naïve | O(1) | O(N×M) | O(N×M) | No |
| Boyer-Moore | O(M+Σ) | O(N/M) best | O(N×M) | No |
| Aho-Corasick | O(Σ×total M) | O(N+matches) | O(N+matches) | Yes |

How to choose: Use KMP for guaranteed O(N+M) single-pattern matching. Use Rabin-Karp when matching against a set of patterns (use a hash set of pattern hashes). Use Boyer-Moore in practice for long patterns (best-case O(N/M)). Use Aho-Corasick for simultaneous multi-pattern matching.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| KMP is always faster than the naïve algorithm | For typical short patterns on random text (e.g., searching web content), Boyer-Moore is often 3–10× faster because it skips characters from the right. KMP's O(N+M) is worst-case optimal; Boyer-Moore's average case is far better. |
| Rabin-Karp is always O(N+M) | Its average case is O(N+M) but worst case is O(N×M) when many hash collisions occur (e.g., all-same character text and pattern). Use double hashing to reduce collision probability. |
| Java `String.indexOf()` is O(N×M) | Modern JVMs (HotSpot) often optimise `indexOf` to use Boyer-Moore-Horspool or SIMD instructions at the JIT level, making it faster than hand-coded KMP for typical inputs. |
| The LPS (failure function) is about failure | `lps[i]` represents the *success* information — it encodes how much of the pattern you've already matched that you don't need to re-check. "Failure" means the algorithm's response to a character mismatch was designed correctly. |
| String matching is trivially solved by regex | Regex matching is not O(N+M) in general — it can be exponential for backtracking-based engines (Java `Pattern`, Python `re`) on adversarial inputs. Guaranteed O(N+M) requires finite automaton or Thompson NFA evaluation. |

---

### 🚨 Failure Modes & Diagnosis

**1. Off-by-one in LPS table construction**

Symptom: KMP returns wrong match positions or misses matches.

Root Cause: Incorrect base case handling (`lps[0] = 0` is always correct; mistakes occur at the `else if (len != 0)` branch — not decrementing via `lps[len-1]` instead of `len = 0`.

Diagnostic:
```java
// Print lps and verify manually for simple pattern
// "AAAB" should give [0,1,2,0]
System.out.println(Arrays.toString(buildLPS("AAAB")));
```

Fix: Test `buildLPS` independently with known patterns ("ABCABC" → [0,0,0,1,2,3]).

Prevention: Add unit tests for `buildLPS` before integrating into search.

---

**2. Rabin-Karp negative hash values**

Symptom: Hash comparisons always fail; no matches found despite correct input.

Root Cause: In Java, `(wh - text.charAt(i) * pw % MOD)` can go negative due to modular subtraction.

Diagnostic:
```java
// Print intermediate hash values
System.out.println("window hash: " + wh);
System.out.println("pattern hash: " + ph);
// If wh is negative: modular subtraction bug
```

Fix: Add `+ MOD` before the final `% MOD`: `(wh - x + MOD) % MOD`.

Prevention: Always add `MOD` before `% MOD` when subtraction is involved.

---

**3. Overlapping matches missed**

Symptom: Pattern "ABA" in text "ABABA" found only twice but three overlapping matches exist.

Root Cause: After a match at position `i`, advancing by `m` (pattern length) skips overlapping matches. Should advance by 1 or by `lps[m-1]`.

Diagnostic:
```java
// For "ABA" in "ABABA", expected positions: 0, 2
// If only 0 found: check post-match advancement
```

Fix: After recording a match, set `j = lps[j-1]` (not `j = 0`) to continue finding overlapping matches.

Prevention: Explicitly test with overlapping patterns: "AA" in "AAAA" should return 3 matches.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — Both KMP and Rabin-Karp use arrays for the `lps` table and hash computation.
- `Hashing Techniques` — Rabin-Karp's rolling hash requires understanding polynomial hashing and modular arithmetic.
- `String` — The fundamental data structure; understanding character indexing and string comparison costs is essential.

**Builds On This (learn these next):**
- `Aho-Corasick` — Generalises KMP to simultaneously match thousands of patterns in O(N + total|patterns| + matches); used in antivirus and IDS systems.
- `Suffix Array` — Preprocessing the text (not pattern) for O(M log N) search; memory-efficient for repeated searches against a fixed text.
- `Regular Expressions (finite automaton)` — Thompson NFA evaluation is equivalent to running KMP on a compiled state machine; linear-time guaranteed.

**Alternatives / Comparisons:**
- `Boyer-Moore` — O(N/M) best case on long patterns; superior for natural language text search; more complex implementation.
- `Trie` — Preprocesses patterns for fast lookup; excellent for prefix matching but not infix/substring matching.
- `Suffix Tree` — O(N) build, O(M) search for arbitrary pattern in fixed text; memory-intensive.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ O(N+M) pattern search using preprocessed  │
│              │ failure function (KMP) or rolling hash     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(N×M) naïve search scales catastrophically│
│ SOLVES       │ for large text and long patterns           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ KMP: text pointer never retreats; lps[]   │
│              │ encodes skip distance on mismatch         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Single-pattern search (KMP); multi-pattern │
│              │ search via hash (Rabin-Karp); DNA/logs    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Short patterns (<8 chars): naïve or       │
│              │ Boyer-Moore is faster in practice         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N+M) guaranteed (KMP) / expected (RK)   │
│              │ vs O(M) preprocessing space and complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't re-read what you already matched"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aho-Corasick → Suffix Array → Boyer-Moore │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** KMP guarantees O(N+M) even for worst-case inputs like `T="AAAAAAAAB"` and `P="AAAAB"`. Trace the LPS table for P and show how, when the mismatch occurs after matching "AAAA", the j pointer jumps to lps[3] instead of 0. Count the total text pointer movements — verify they total exactly N. Now consider: what is the maximum number of times the pattern pointer `j` can decrease across the entire search, and how does that bound the total operation count?

**Q2.** Rabin-Karp can effectively search for any of K patterns simultaneously by storing all K pattern hashes in a HashSet and checking each window hash against the set in O(1). For a malware scanner checking 10,000 virus signatures (each 64 bytes) in a 1 GB log file, compare: (a) 10,000 separate KMP passes O(10,000 × N) vs (b) Rabin-Karp with hash set O(N + 10,000×M). What are the constants and hash-collision risks in real-world deployment, and why do production antivirus engines (ClamAV) use Aho-Corasick instead of either?

