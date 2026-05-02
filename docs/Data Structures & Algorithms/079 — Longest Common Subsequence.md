---
layout: default
title: "Longest Common Subsequence"
parent: "Data Structures & Algorithms"
nav_order: 79
permalink: /dsa/longest-common-subsequence/
number: "0079"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Dynamic Programming, Memoization, Tabulation (Bottom-Up DP)
used_by: Diff Tools (git diff), Bioinformatics, Plagiarism Detection
related: Longest Increasing Subsequence, Edit Distance, Dynamic Programming
tags:
  - algorithm
  - advanced
  - deep-dive
  - datastructure
  - pattern
---

# 079 — Longest Common Subsequence

⚡ TL;DR — LCS finds the longest sequence of elements that appear in the same relative order in both strings, powering diff tools, DNA comparison, and plagiarism detection.

| #0079 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Dynamic Programming, Memoization, Tabulation (Bottom-Up DP) | |
| **Used by:** | Diff Tools (git diff), Bioinformatics, Plagiarism Detection | |
| **Related:** | Longest Increasing Subsequence, Edit Distance, Dynamic Programming | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
`git diff` shows exactly which lines changed between two file versions. Given file version A (1,000 lines) and version B (1,000 lines), how do you determine which lines were unchanged (common) and which were added or deleted? The naive approach compares every line of A against every line of B: 1,000 × 1,000 = 1 million comparisons, producing an unmanageable list of "differences."

THE BREAKING POINT:
Without the LCS backbone, diff output has no structure — it can't distinguish whether two similar lines come from the same original, making diffs noisy and unintuitive. DNA sequence alignment for a 3 billion base-pair genome against a 3 billion base-pair reference genome needs to find the most similar regions — O(N²) brute force is 9 × 10^18 operations, infeasible.

THE INVENTION MOMENT:
The longest common subsequence defines the "unchanging core" of two sequences — every element in the LCS represents a stable alignment point. The remaining elements are additions or deletions. Computing LCS with dynamic programming reduces O(2^N) recursive enumeration to O(N×M) tabulation by identifying overlapping subproblems: `LCS(i,j)` depends only on `LCS(i-1,j)`, `LCS(i,j-1)`, and `LCS(i-1,j-1)`. This is exactly why **Longest Common Subsequence** was created.

### 📘 Textbook Definition

A **subsequence** of a string is any subset of its characters in their original relative order (not necessarily contiguous). The **Longest Common Subsequence (LCS)** of two strings X (length M) and Y (length N) is the longest string that is a subsequence of both X and Y. The LCS is computed by dynamic programming: `dp[i][j]` = length of LCS of `X[1..i]` and `Y[1..j]`. Recurrence: if `X[i] == Y[j]`, `dp[i][j] = dp[i-1][j-1] + 1`; else `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`. Time: O(M×N). Space: O(M×N) for full table, O(min(M,N)) for length only.

### ⏱️ Understand It in 30 Seconds

**One line:**
Find the longest string you can form by crossing out characters in two strings while keeping the remaining characters in order.

**One analogy:**
> Comparing two shopping lists: "milk, eggs, flour, sugar" and "bread, milk, butter, eggs." The longest common subsequence is "milk, eggs" — these items appear in both lists and in the same relative order. You can't include "flour" because it doesn't appear in the second list, and you can't reverse the order.

**One insight:**
LCS is NOT the longest common substring (which must be contiguous). "ABCBDAB" and "BDCAB" have LCS "BCAB" (length 4) — but no common substring longer than 2 exists. The subsequence can "skip" characters; the substring cannot. This distinction is crucial: git diff uses LCS thinking (non-contiguous), while DNA restriction fragment analysis uses substring thinking.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The LCS of an empty string with any string is empty: `LCS("", X) = ""` (base case).
2. If `X[i] == Y[j]`, the last character of both matches; the LCS must include it: `LCS(X[1..i], Y[1..j]) = LCS(X[1..i-1], Y[1..j-1]) + X[i]`.
3. If `X[i] ≠ Y[j]`, one (or both) of the last characters is NOT in the LCS; try both options: `max(LCS(X[1..i-1], Y[1..j]), LCS(X[1..i], Y[1..j-1]))`.

DERIVED DESIGN:
These three cases define a complete recurrence. The subproblem structure is: `dp[i][j]` depends only on `dp[i-1][j-1]`, `dp[i-1][j]`, `dp[i][j-1]`. Filling the table row by row (bottom-up DP) gives O(M×N) with no redundant computation. Backtracking through the table recovers the actual LCS string.

**Space optimisation:**
Since `dp[i][j]` depends only on row i-1 and row i, only two rows (or one row + one saved value) need to be stored: O(min(M,N)) space for length. Recovering the actual LCS requires either storing the full M×N table or rerunning with divide and conquer (Hirschberg's algorithm: O(M×N) time, O(min(M,N)) space).

THE TRADE-OFFS:
Gain: O(M×N) — polynomial for exact LCS. Direct application to diff tools, DNA alignment, plagiarism detection.
Cost: O(M×N) space for full table — for 10,000-line files: 10,000 × 10,000 = 100M entries, ~500 MB. Recovering the actual LCS sequence (not just length) requires backtracking through the whole table. For very long sequences, approximate algorithms (space-efficient Hirschberg, heuristic alignment) are preferred.

### 🧪 Thought Experiment

SETUP:
X = "ABCBDAB", Y = "BDCAB". Find LCS length.

WHAT HAPPENS WITH BRUTE FORCE:
Generate all 2^7 = 128 subsequences of X; for each, check if it's a subsequence of Y. Most subsequences of X are not in Y. Total: 128 subsequences × O(N) check = O(2^M × N) — exponential.

WHAT HAPPENS WITH DP:
Build the 7×5 table. Key entries (i,j) where X[i]==Y[j]:
- X[2]='B'=Y[1]='B': dp[2][1] = dp[1][0]+1 = 1.
- X[3]='C'=Y[3]='C': dp[3][3] = dp[2][2]+1 = 2.
- X[4]='B'=Y[1]: dp[4][1]=1; but dp[4][5]... continue.
- X[6]='A'=Y[4]='A': dp[6][4] = max(dp[5][4], dp[6][3], dp[5][3]+1).
- X[7]='B'=Y[1]: ...

Final answer: dp[7][5] = 4. One LCS: "BCAB". Total operations: 35 table entries = O(M×N). Exponential → polynomial.

THE INSIGHT:
The key structural insight: If we've already solved `LCS(X[1..i], Y[1..j])` for all smaller i,j, then solving for the next (i,j) takes O(1) — lookup and compare. The overlapping subproblem structure (same (i,j) would be recomputed exponentially many times in naive recursion) is eliminated by the table.

### 🧠 Mental Model / Analogy

> LCS is like finding the common "backbone" between two movie scripts. Alice's script has scenes [A, B, C, D, E]; Bob's has [B, D, C, E]. Both scripts have scenes B, D, E in common order — that's the LCS. Scenes can be "skipped" between common points — scenes A and C appear in Alice's but not Bob's or in the wrong relative order.

"Alice's and Bob's scripts" → strings X and Y
"Common scenes in relative order" → common subsequence
"Longest such list of common scenes" → LCS
"Scene reorder" → violates subsequence property (order must be preserved)
"Scene not in one script" → character only in one string

Where this analogy breaks down: The LCS is not necessarily unique — "BCDB" and "BCAB" are both valid LCS of length 4 for the example above. The analogy suggests the common scenes are "the same", but multiple valid LCSs may exist.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
LCS finds the longest set of matching elements that appear in both sequences, keeping their relative order. Think of highlighting the matching items in two lists — LCS gives you the maximum number of highlights where the order matches in both.

**Level 2 — How to use it (junior developer):**
Implement the O(M×N) DP table. Base case: `dp[0][j] = dp[i][0] = 0`. Fill row by row: `if X[i]==Y[j]: dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=max(dp[i-1][j],dp[i][j-1])`. LCS length = `dp[M][N]`. To recover the LCS string: backtrack from `dp[M][N]` to `dp[0][0]`, following the matching choices. Java: no built-in LCS; use the DP implementation directly.

**Level 3 — How it works (mid-level engineer):**
The DP table encodes: "what is the optimal alignment of the first i characters of X with the first j characters of Y?" Space optimisation: only two rows needed for length (current and previous). Hirschberg's divide-and-conquer achieves O(M×N) time with O(min(M,N)) space — solves LCS in the midpoint column, recurses on each half. For diff tools, the Myers diff algorithm (used in git diff) finds the shortest edit script in O((M+N)×D) where D is the number of differences — much faster than full LCS for nearly-identical files.

**Level 4 — Why it was designed this way (senior/staff):**
LCS was first described by Needleman and Wunsch (1970) for sequence alignment in computational biology — the Needleman-Wunsch algorithm is LCS with affine gap penalties. The Smith-Waterman algorithm (1981) extended it to local alignment (longest common substring with scoring). Both are O(M×N) DP. For genomics at scale, BLAST uses heuristic seeding (exact k-mer matches) followed by local extension to avoid full O(M×N) alignment — trades exactness for orders-of-magnitude speed. The four-Russians speedup reduces LCS to O(M×N/log N) using precomputed table blocks. Myers diff (O(D×(M+N))) is optimal for small diff sizes D and is the algorithm behind git diff, `diff`, and most modern diff utilities.

### ⚙️ How It Works (Mechanism)

**DP Table Construction:**

```
┌─────────────────────────────────────────────────┐
│ LCS("ABCB", "BCAB") DP table                    │
│                                                 │
│     ""  B  C  A  B                              │
│ ""  0   0  0  0  0                              │
│ A   0   0  0  1  1                              │
│ B   0   1  1  1  2                              │
│ C   0   1  2  2  2                              │
│ B   0   1  2  2  3  ← LCS length = 3            │
│                                                 │
│ LCS: backtrack from (4,4)                       │
│  dp[4][4]=3: B==B → include 'B', go to (3,3)   │
│  dp[3][3]=2: C==C → include 'C', go to (2,2)   │
│  dp[2][2]=1: B≠C → dp[1][2]=0<dp[2][1]=1 →    │
│               go to (2,1)                       │
│  dp[2][1]=1: B==B → include 'B', go to (1,0)   │
│  dp[1][0]=0: stop. LCS = "BCB" reversed? "BCB" │
└─────────────────────────────────────────────────┘
```

**Space-optimised (O(N) space):**
```java
int lcsLength(String X, String Y) {
    int m = X.length(), n = Y.length();
    int[] prev = new int[n+1], curr = new int[n+1];
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (X.charAt(i-1) == Y.charAt(j-1))
                curr[j] = prev[j-1] + 1;
            else
                curr[j] = Math.max(prev[j], curr[j-1]);
        }
        int[] tmp = prev; prev = curr; curr = tmp;
        Arrays.fill(curr, 0);
    }
    return prev[n];
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Two sequences (strings, file lines, DNA base pairs)
→ Fill M×N DP table bottom-up in O(M×N)
→ [LCS ← YOU ARE HERE]
  → dp[M][N] = LCS length
  → backtrack to recover actual sequence
→ Apply:
  git diff: LCS of lines → unchanged lines → add/delete diff
  DNA alignment: LCS of base pairs → alignment score
  Plagiarism: LCS of sentences → similarity percentage
```

FAILURE PATH:
```
M × N too large for full table (1M lines × 1M lines = 10^12 entries)
→ OutOfMemoryError or infeasible runtime
→ Fix: Hirschberg O(min(M,N)) space for length; Myers O(D(M+N)) for diffs
→ Or: approximate alignment (BLAST seeds) for genomics
→ Diagnostic: estimate M×N × 4 bytes; if > available RAM → switch algorithm
```

WHAT CHANGES AT SCALE:
For a 3 billion base-pair genome alignment (M=N=3×10⁹), O(M×N) DP is 9×10^18 operations — impossible. Production genomics tools (BWA, HISAT2) use:
1. Hash-indexed k-mer seeding: find exact 20-mer matches O(N).
2. Smith-Waterman local alignment only near seeds.
3. Result: O(N × average_alignment_region) — typically linear in N.

### 💻 Code Example

**Example 1 — LCS length (O(M×N) time, O(N) space):**
```java
int lcs(String X, String Y) {
    int m = X.length(), n = Y.length();
    int[] dp = new int[n + 1];
    for (int i = 0; i < m; i++) {
        int prev = 0;
        for (int j = 0; j < n; j++) {
            int temp = dp[j + 1];
            if (X.charAt(i) == Y.charAt(j))
                dp[j + 1] = prev + 1;
            else
                dp[j + 1] = Math.max(dp[j + 1], dp[j]);
            prev = temp;
        }
    }
    return dp[n];
}
```

**Example 2 — Recover actual LCS string:**
```java
String lcsString(String X, String Y) {
    int m = X.length(), n = Y.length();
    int[][] dp = new int[m+1][n+1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            if (X.charAt(i-1) == Y.charAt(j-1))
                dp[i][j] = dp[i-1][j-1] + 1;
            else
                dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
    // Backtrack
    StringBuilder sb = new StringBuilder();
    int i = m, j = n;
    while (i > 0 && j > 0) {
        if (X.charAt(i-1) == Y.charAt(j-1)) {
            sb.append(X.charAt(i-1));
            i--; j--;
        } else if (dp[i-1][j] > dp[i][j-1]) {
            i--;
        } else {
            j--;
        }
    }
    return sb.reverse().toString();
}
```

**Example 3 — Edit distance (LCS extension):**
```java
// EditDistance = M + N - 2 * LCS(X, Y)
// (insertions + deletions = total - 2 * unchanged)
int editDistance(String X, String Y) {
    return X.length() + Y.length() - 2 * lcs(X, Y);
}
```

**Example 4 — Simplified git diff (LCS of lines):**
```java
void simpleDiff(String[] A, String[] B) {
    int m = A.length, n = B.length;
    int[][] dp = new int[m+1][n+1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = A[i-1].equals(B[j-1])
                ? dp[i-1][j-1] + 1
                : Math.max(dp[i-1][j], dp[i][j-1]);
    // Backtrack and emit diff
    int i = m, j = n;
    List<String> diff = new ArrayList<>();
    while (i > 0 || j > 0) {
        if (i > 0 && j > 0 && A[i-1].equals(B[j-1])) {
            diff.add("  " + A[i-1]); i--; j--;
        } else if (j > 0 &&
                   (i==0 || dp[i][j-1]>=dp[i-1][j])) {
            diff.add("+ " + B[j-1]); j--;
        } else {
            diff.add("- " + A[i-1]); i--;
        }
    }
    Collections.reverse(diff);
    diff.forEach(System.out::println);
}
```

### ⚖️ Comparison Table

| Problem | Algorithm | Time | Space | Notes |
|---|---|---|---|---|
| **LCS length** | DP (1D) | O(M×N) | O(N) | Length only, no reconstruction |
| **LCS string** | DP (2D) backtrack | O(M×N) | O(M×N) | Full table needed for backtrack |
| **LCS string (low mem)** | Hirschberg D&C | O(M×N) | O(min(M,N)) | Complex implementation |
| Shortest edit script | Myers diff | O(D(M+N)) | O(M+N) | D=number of diffs; used in git |
| Edit distance | Levenshtein DP | O(M×N) | O(N) | Add/delete/replace cost model |
| Local alignment | Smith-Waterman | O(M×N) | O(M×N) | DNA local similarity with scoring |

How to choose: Use LCS DP directly for correctness and moderate input sizes. Use Myers diff when inputs are nearly identical (small D). Use Hirschberg for large inputs with memory constraints.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LCS is the same as the longest common substring | LCS allows skipping characters (non-contiguous); longest common substring requires contiguity. "ABCDE" and "ACE" have LCS "ACE" (length 3) but longest common substring "A" or "C" or "E" (length 1). |
| LCS is always unique | Multiple valid LCS of the same length often exist. "ABAB" and "BABA" have LCS "BAB" and "ABA" both of length 3. |
| git diff uses the exact LCS algorithm | git diff uses the Myers diff algorithm (O(D×(M+N)) where D = edit distance), which is far more efficient than O(M×N) LCS for nearly-identical files. Both are conceptually LCS-based but Myers is optimised for the diffing use case. |
| Space-optimised LCS reconstructs the actual sequence | The 1D rolling array optimisation only gives the LCS length. Reconstructing the LCS string requires either the full M×N table or Hirschberg's divide-and-conquer. |
| LCS length = edit distance | Edit distance (Levenshtein) allows substitutions; LCS does not. LCS uses only insertions and deletions. Edit distance = M + N - 2×LCS only when substitution cost = insert + delete cost. |

### 🚨 Failure Modes & Diagnosis

**1. Off-by-one in DP table indexing**

Symptom: LCS length is 0 or 1 fewer than expected; backtracking goes out of bounds.

Root Cause: Confusion between 0-indexed strings and 1-indexed DP table. `dp[i][j]` represents `X[0..i-1]` and `Y[0..j-1]`, so string access is `X.charAt(i-1)`.

Diagnostic:
```java
// Test with known LCS: lcs("ABC", "AC") should be 2
assert lcs("ABC", "AC") == 2 : "Off-by-one in LCS";
// Print dp table for small inputs to verify
```

Fix: Use the convention `dp[i][j]` = LCS of `X[0..i-1]` and `Y[0..j-1]`; base case `dp[0][j] = dp[i][0] = 0`.

Prevention: Explicitly comment the index convention; add unit tests for known inputs.

---

**2. Memory overflow for large inputs**

Symptom: `OutOfMemoryError` for files with 100,000+ lines.

Root Cause: Full M×N table: 100,000 × 100,000 × 4 bytes = 40 GB.

Diagnostic:
```java
long estimatedBytes = (long) M * N * 4;
System.out.println("Estimated memory: " +
    estimatedBytes / 1_000_000 + " MB");
// If > available heap: switch algorithm
```

Fix: Use 1D rolling array for length only; or Hirschberg's for actual LCS with O(min(M,N)) space.

Prevention: Estimate M×N before choosing algorithm; set a threshold (e.g., M×N > 10^8 → switch to Myers or Hirschberg).

---

**3. Wrong answer from greedy LCS attempt**

Symptom: Greedy "scan for first match" approach returns shorter LCS than optimal.

Root Cause: Greedy: for each character in X, find its first occurrence in Y after the last matched position. This is locally optimal but globally suboptimal for LCS — unlike sorting-based algorithms where greedy works.

Diagnostic:
```java
// Greedy fails here: X="AB", Y="BA"
// Greedy: match 'A' at Y[1], then 'B' at Y[1] → can't → LCS="A" (length 1)
// DP: dp[2][2]=1 correctly (LCS is "A" or "B") → but verifies
// Greedy works for LCS of sorted sequences, NOT general case
```

Fix: Always use full DP for general LCS; greedy only works for specific cases (longest increasing subsequence with patience sorting).

Prevention: Never use greedy for LCS — the problem has optimal substructure but not the greedy-choice property.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dynamic Programming` — LCS is a canonical DP problem; understanding overlapping subproblems and optimal substructure is essential.
- `Memoization` — Top-down LCS uses memoization to avoid recomputing `lcs(i,j)` multiple times.
- `Tabulation (Bottom-Up DP)` — The standard O(M×N) LCS implementation fills the table bottom-up.

**Builds On This (learn these next):**
- `Edit Distance (Levenshtein)` — LCS extended with substitution costs; `editDist = M + N - 2×LCS` for insert/delete-only.
- `Longest Increasing Subsequence` — Related DP on single sequences; O(N log N) with patience sorting.
- `Myers Diff` — The algorithm behind `git diff`; optimised for sequences with few differences.

**Alternatives / Comparisons:**
- `Longest Common Substring` — Contiguous version of LCS; O(M×N) with sliding window or suffix arrays.
- `Smith-Waterman` — Local sequence alignment with scoring; biological application of LCS ideas.
- `Needleman-Wunsch` — Global sequence alignment with gap penalties; biological LCS with affine scoring.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Longest sequence appearing as a           │
│              │ subsequence in both input strings          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(2^N) brute-force subsequence enumeration│
│ SOLVES       │ → O(M×N) via DP on overlapping subproblems│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ dp[i][j] = dp[i-1][j-1]+1 if chars match;│
│              │ else max(dp[i-1][j], dp[i][j-1])         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diff tools, DNA alignment, plagiarism,    │
│              │ spell correction, revision history        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ M×N > 10^8 (memory); need contiguous      │
│              │ match (use longest common substring)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Optimal O(M×N) time vs O(M×N) space       │
│              │ (use rolling array for length, Hirschberg │
│              │ for string reconstruction)                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Find the shared skeleton of two sequences"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Edit Distance → Myers Diff → Smith-Waterman│
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** The standard LCS algorithm is O(M×N) time and space. The Myers diff algorithm achieves O(D×(M+N)) time where D is the number of edit operations (the edit distance). For a 10,000-line file with only 5 changed lines (D=10), Myers runs in O(10 × 20,000) = 200,000 operations vs LCS's O(100,000,000) — a 500× difference. However, if files are completely different (D = M+N), Myers degrades to O((M+N)²) — worse than LCS. Describe the structural property of "nearly identical" files that allows Myers to exploit D ≪ M+N, and explain why the diagonal DP formulation enables this.

**Q2.** The DNA sequences of two human organisms are 3 billion base pairs, with 99.9% identity. The LCS length is approximately 2.997 billion. The actual areas of difference (SNPs, insertions, deletions) are concentrated in ~1 million locations. A naive O(M×N) alignment requires 9×10^18 operations. BLAST uses a two-phase approach: (1) find exact k-mer matches (seeds), (2) extend locally with Smith-Waterman. How does this heuristic avoid the O(M×N) cost, what is the false-negative risk (missed alignments), and why is a k-mer length of k=11 typically chosen for DNA while k=3 is used for protein sequences?

