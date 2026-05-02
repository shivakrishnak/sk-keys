---
layout: default
title: "Radix Sort"
parent: "Data Structures & Algorithms"
nav_order: 68
permalink: /dsa/radix-sort/
number: "0068"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Counting Sort, Arrays, Time Complexity / Big-O
used_by: Integer Sorting, IP Address Sorting, Suffix Array Construction
related: Counting Sort, Bucket Sort, Mergesort
tags:
  - algorithm
  - advanced
  - deep-dive
  - pattern
  - performance
---

# 068 — Radix Sort

⚡ TL;DR — Radix Sort sorts integers digit-by-digit using a stable sub-sort, breaking the O(N log N) comparison-sort barrier to achieve O(N × d) where d is the number of digits.

| #068 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Counting Sort, Arrays, Time Complexity / Big-O | |
| **Used by:** | Integer Sorting, IP Address Sorting, Suffix Array Construction | |
| **Related:** | Counting Sort, Bucket Sort, Mergesort | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to sort 10 million IP addresses (32-bit integers). The comparison-based lower bound says any algorithm must make at least N log₂ N ≈ 230 million comparisons. For a constraint like integers in [0, 2^32), can you beat this bound?

**THE BREAKING POINT:**
The O(N log N) lower bound applies **only to comparison-based algorithms** — algorithms whose only operation is comparing pairs of elements. If elements have structure (they are integers with individual digits), you can exploit that structure to sort without comparisons.

**THE INVENTION MOMENT:**
Sort by the least significant digit first, then by the next digit, and so on — using a stable sort for each digit. "Stable" means elements with the same digit preserve their order from the previous pass. After sorting by all D digits, the entire array is sorted. Each pass is O(N + radix) counting sort. Total: O(D × (N + radix)) = O(D × N) for fixed radix. For 32-bit integers with radix=256: D=4 passes. For N=10^7, that's 40 million operations — beating comparison sort's 230 million. This is exactly why **Radix Sort** was created.

---

### 📘 Textbook Definition

**Radix Sort** is a non-comparative integer sorting algorithm that sorts by processing individual digits from least significant to most significant (LSD radix sort) or most significant to least significant (MSD radix sort). Each pass uses a stable sub-sort (typically counting sort) on one digit position. For N elements with maximum value M and radix r, time complexity is O(D × (N + r)) where D = log_r(M). For fixed-width integers, this is O(N). Space complexity: O(N + r).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sort numbers by their last digit, then second-to-last, then so on — using a stable sort each time.

**One analogy:**
> Imagine sorting library cards in alphabetical order. A librarian sorts the entire stack by last letter, then re-sorts by second-to-last letter (preserving last-letter order among ties), and so on to the first letter. Each round takes linear time. After 26 rounds (for 26 letter words), the stack is fully alphabetised. This is faster than comparing card-by-card because each round is a simple counting exercise, not a comparison tournament.

**One insight:**
Radix sort can only beat comparison sort when the key size is bounded. If numbers can be arbitrarily large (log N bits), then D = O(log N) and Radix Sort becomes O(N log N) — same as comparison sort. The speedup only materialises when the key size (number of digits D) is sub-logarithmic in N. For 32-bit integers sorted by 4 bytes (D=4), N must be > 2^(4×8) = 4 billion before D starts growing — for practical N, D is constant.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each pass processes one digit position using a **stable** sub-sort. Stability is non-negotiable — it preserves the partial ordering from previous passes.
2. After processing digit position `k` (LSD order), all elements are ordered correctly by their suffixes (least significant k digits).
3. After all D passes, all D digits are processed — full ordering is correct.

**DERIVED DESIGN:**
**Why LSD (least significant first)?**
LSD works because after each pass, the partial order from previous passes is preserved (stable sub-sort). When two numbers agree on digits 1..k, their relative order from previous round is maintained — so the overall sort is correct after all D rounds.

**MSD (most significant first) vs LSD:**
MSD requires recursive sub-sorting: sort by most significant digit, then independently sort each group by next digit. This is more complex but enables early termination (once a group has size 1, it's sorted). MSD is natural for variable-length strings; LSD requires padding to equal length.

**Counting Sort as the sub-sort:**
For radix r (e.g., 256 for bytes), counting sort counts occurrences of each digit value (0..r-1), computes prefix sums to get output positions, then writes elements to output array in order. This is O(N + r) per pass and — crucially — stable.

**THE TRADE-OFFS:**
**Gain:** O(N × D) total, beating O(N log N) comparison sort when D is small.
**Cost:** Only applicable to integers or fixed-structure keys; O(N + r) extra space; not in-place; radix choice affects performance (large radix = fewer passes but more memory).

---

### 🧪 Thought Experiment

**SETUP:**
Sort [170, 45, 75, 90, 802, 24, 2, 66] by decimal digit (radix=10).

PASS 1 (ones digit): Group by last digit.
0: [170, 90], 2: [802, 2], 4: [24], 5: [45, 75], 6: [66].
Output: [170, 90, 802, 2, 24, 45, 75, 66].

PASS 2 (tens digit):
0: [802, 2], 1: [170], 2: [24], 4: [45], 6: [66], 7: [75], 9: [90].
Output: [802, 2, 170, 24, 45, 66, 75, 90].
Note: 802 has tens digit 0, 2 has tens digit 0 → stable, 802 stays before 2 from previous pass.

PASS 3 (hundreds digit):
0: [2, 24, 45, 66, 75, 90], 1: [170], 8: [802].
Output: [2, 24, 45, 66, 75, 90, 170, 802]. Sorted! ✓

**THE INSIGHT:**
After pass 2, [802, 2] appear before [170] — correct because both have smaller tens digit than 1. Pass 3 finalises by hundreds — 2, 24, 45 etc. all start with 0 (implicit) so they stay before 170. The stability of each pass preserves the previous pass's ordering — this is the key invariant that makes the whole algorithm correct.

---

### 🧠 Mental Model / Analogy

> Radix Sort is like sorting a stack of envelopes by ZIP code. First, sort by last digit of ZIP (0-9). Then re-sort by fourth digit, then third, second, first — keeping the sub-sorted order within each digit group (stable). After 5 rounds for 5-digit ZIPs, all envelopes are in order. Each round is just grouping into 10 buckets and collecting — no head-to-head comparisons needed.

- "Last digit of ZIP" → least significant digit (LSD sort)
- "10 buckets per round" → radix = 10 counting sort
- "Keeping sub-sorted order within digit group" → stability requirement
- "5 rounds for 5-digit ZIP" → D passes for D-digit numbers

Where this analogy breaks down: ZIP codes always have exactly 5 digits. For variable-length strings (words of different lengths), MSD radix sort is more natural — LSD requires padding shorter strings which wastes work.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Radix Sort sorts numbers by looking at one digit at a time, from rightmost to leftmost. Each time, it sorts by just that one digit, keeping the order from previous rounds intact. After processing all digits, the whole list is sorted — without ever directly comparing two complete numbers.

**Level 2 — How to use it (junior developer):**
Choose radix r (typically 256 for bytes or 10 for decimal). For each digit position from 0 to D-1: (1) Extract the digit value at position p: `(arr[i] >> (8*p)) & 0xFF` for radix 256. (2) Counting sort on this digit. Counting sort must be implemented stably — iterate input right-to-left when building output using prefix sums.

**Level 3 — How it works (mid-level engineer):**
Optimal radix choice: r = N^(1/D) minimises total time D × (N + r). For 32-bit integers and N=10^6: r=2^8=256 gives D=4 passes, each O(N+256)≈O(N). r=2^16 gives D=2 passes, each O(N+65536). Which is faster depends on N vs the constant factor. Empirically, r=256 (byte-level) is optimal for most sizes because it balances pass count and counting-sort overhead. MSD radix sort can be implemented in-place but requires careful bookkeeping of group boundaries (American Flag Sort).

**Level 4 — Why it was designed this way (senior/staff):**
The information-theoretic lower bound of O(N log N) for comparison sort is escaped by Radix Sort because Radix Sort does not sort via comparisons — it partitions into buckets. This is analogous to Counting Sort's O(N + k) for keys in [0,k). Radix Sort extends Counting Sort to larger ranges by processing D "digits" in base r. The relationship between D, N, and r determines when Radix Sort beats comparison sort: D × (N + r) < N log N → roughly D < log₂ N / (1 + r/N). For fixed-domain integers, this always holds at sufficient N. Radix Sort is used in suffix array construction (DC3/Skew algorithm uses radix sort on triplets to build suffix arrays in O(N)), in high-frequency trading (sort order books by price in O(N) instead of O(N log N)), and in GPU sorting (highly parallelisable per-digit counting).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ LSD Radix Sort (radix = 256, 32-bit ints)  │
│                                            │
│  for pass = 0 to 3: (4 byte positions)     │
│    digit(x) = (x >> (8*pass)) & 0xFF       │
│                                            │
│    // Counting sort on this digit:         │
│    count[0..255] = 0                       │
│    for each x in arr: count[digit(x)]++    │
│    // Prefix sum for output positions:     │
│    for i in 1..255: count[i]+=count[i-1]  │
│    // Build output (right-to-left: STABLE)│
│    for j = n-1 downto 0:                  │
│      d = digit(arr[j])                    │
│      output[--count[d]] = arr[j]          │
│    arr = output                            │
└────────────────────────────────────────────┘
```

**Why iterate right-to-left for stability:**
If we process elements left-to-right when writing to output, later elements with the same digit overwrite earlier positions — losing stability. Right-to-left processing with prefix sums ensures earlier input elements go to earlier output positions within the same digit group.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Array of N integers in [0, 2^32)
→ Choose radix r=256, passes D=4
→ [RADIX SORT ← YOU ARE HERE]
  → Pass 1: stable sort by byte 0 (ones)
  → Pass 2: stable sort by byte 1 (tens)
  → Pass 3: stable sort by byte 2 (hundreds)
  → Pass 4: stable sort by byte 3 (thousands)
→ Sorted array in O(4*N) = O(N) time
```

**FAILURE PATH:**
```
Negative integers present
→ Two's complement representation: negative
  numbers have MSB=1, positive MSB=0
→ Treating as unsigned: all negatives sort
  AFTER all positives (wrong!)
→ Fix: offset all values by min to make non-neg,
  or sort unsigned then separate sign groups
```

**WHAT CHANGES AT SCALE:**
For N=10⁹ (1 billion integers, ~4 GB), Radix Sort with r=256 needs D=4 auxiliary arrays of 4 GB each — 16 GB total. Impractical. Solution: stream-process in chunks fitting in L3 cache (say 4M integers); radix-sort each chunk; then merge the sorted chunks using K-way merge. This is essentially parallel external radix sort used in Hadoop sort benchmark winners.

---

### 💻 Code Example

**Example 1 — LSD Radix Sort for non-negative integers:**
```java
void radixSort(int[] arr) {
    int max = Arrays.stream(arr).max()
                    .getAsInt();
    // Process each byte position
    for (int shift = 0; (max >> shift) > 0 ||
                        shift == 0; shift += 8) {
        countingSort(arr, shift);
    }
}

void countingSort(int[] arr, int shift) {
    int n = arr.length;
    int[] output = new int[n];
    int[] count = new int[256]; // byte radix

    // Count occurrences of each byte value
    for (int x : arr)
        count[(x >> shift) & 0xFF]++;

    // Prefix sum → output positions
    for (int i = 1; i < 256; i++)
        count[i] += count[i-1];

    // Build output right-to-left (STABLE!)
    for (int j = n-1; j >= 0; j--) {
        int d = (arr[j] >> shift) & 0xFF;
        output[--count[d]] = arr[j];
    }

    // Copy back
    System.arraycopy(output, 0, arr, 0, n);
}
```

**Example 2 — Radix Sort for negative integers:**
```java
void radixSortWithNegatives(int[] arr) {
    // Separate positives and negatives
    List<Integer> neg = new ArrayList<>();
    List<Integer> pos = new ArrayList<>();
    for (int x : arr) {
        if (x < 0) neg.add(-x); // flip sign
        else pos.add(x);
    }

    // Sort each group (non-negative)
    int[] posArr = pos.stream()
                      .mapToInt(i->i).toArray();
    int[] negArr = neg.stream()
                      .mapToInt(i->i).toArray();
    radixSort(posArr);
    radixSort(negArr);

    // Rebuild: negatives in reverse, then positives
    int k = 0;
    for (int i=negArr.length-1; i>=0; i--)
        arr[k++] = -negArr[i];
    for (int x : posArr)
        arr[k++] = x;
}
```

**Example 3 — Radix Sort for strings (MSD):**
```java
// MSD radix sort for fixed-width strings
void msdRadixSort(String[] arr,
                  int lo, int hi, int d) {
    if (hi <= lo) return;
    int[] count = new int[256 + 2]; // extra for end

    // Count
    for (int i = lo; i <= hi; i++) {
        int c = d < arr[i].length()
                ? arr[i].charAt(d) : -1;
        count[c + 2]++;
    }
    // Cumulate
    for (int r = 0; r < 257; r++)
        count[r+1] += count[r];
    // Distribute
    String[] aux = new String[hi-lo+1];
    for (int i = lo; i <= hi; i++) {
        int c = d < arr[i].length()
                ? arr[i].charAt(d) : -1;
        aux[count[c+1]++] = arr[i];
    }
    // Copy back
    for (int i = lo; i <= hi; i++)
        arr[i] = aux[i-lo];

    // Recurse on each character group
    for (int r = 0; r < 256; r++) {
        msdRadixSort(arr,
            lo+count[r], lo+count[r+1]-1, d+1);
    }
}
```

---

### ⚖️ Comparison Table

| Algorithm | Time | Comparisons | Space | In-Place | Best For |
|---|---|---|---|---|---|
| **Radix Sort (LSD)** | O(D × N) | None | O(N + r) | No | Fixed-width integers, large N |
| Counting Sort | O(N + k) | None | O(k) | No | Small ranges [0,k) |
| Bucket Sort | O(N) avg | Yes (insertion sort) | O(N + k) | No | Uniformly distributed floats |
| Mergesort | O(N log N) | Yes | O(N) | No | General, stable, objects |
| Quicksort | O(N log N) avg | Yes | O(log N) | Yes | In-place, primitives |

How to choose: Use Radix Sort for large arrays of fixed-width integers where the digit count D is small relative to log N. Use Counting Sort for small integer ranges. Use comparison-based sorts for general comparable objects.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Radix Sort always beats O(N log N) sorts | Only when D (digit count) < log₂ N. For arbitrarily large integers (D = log N bits), Radix Sort becomes O(N log N) — same as comparison sort |
| Radix Sort is always faster than Quicksort | Radix Sort has larger constant factors (two array passes per digit) and worse cache behavior than Quicksort for moderate N. Quicksort often beats Radix Sort for N < 10^6 with 32-bit integers |
| Stability of the sub-sort is optional | Stability in each counting-sort pass is MANDATORY for correctness. Without stability, earlier passes' ordering is destroyed by later passes |
| LSD and MSD Radix Sort produce identical results | Both produce the same sorted output. LSD processes all elements per pass; MSD recursively divides into groups. LSD is simpler for fixed-width integers; MSD is better for variable-length strings |
| Radix Sort works for arbitrary data types | Radix Sort requires **digit extractability** — a way to decompose keys into a fixed number of sub-keys (digits). Floating-point numbers, strings with variable lengths, and custom objects need special handling |

---

### 🚨 Failure Modes & Diagnosis

**1. Left-to-right instead of right-to-left output phase breaks stability**

**Symptom:** Sort produces wrong results; elements with same digit are in wrong relative order.

**Root Cause:** Iterating input left-to-right when writing to output causes later elements to land in earlier positions (stealing slots from earlier elements), violating stability.

**Diagnostic:**
```java
// Test stability: [12, 22, 32] sorted by ones digit
// All have digit 2; order must be preserved
int[] arr = {12, 22, 32};
radixSort(arr);
assert arr[0]==12 && arr[1]==22 && arr[2]==32
    : "Stability violated!";
```

**Fix:** Iterate input **right-to-left** when writing to output array. This ensures earlier input elements take earlier available slots for their digit group.

**Prevention:** Comment this direction requirement explicitly: "// Right-to-left for stability."

---

**2. Handling negative integers as unsigned — wrong sort order**

**Symptom:** Negative integers sort after all positive integers (e.g., -1 sorts after 1000000).

**Root Cause:** Two's complement negative integers have MSB=1. When treated as unsigned 32-bit: -1 = 0xFFFFFFFF = 4,294,967,295 — larger than any positive.

**Diagnostic:**
```java
int[] arr = {5, -3, 2, -1, 0};
radixSort(arr);
// Wrong: [5, 2, 0, -3, -1]
// Correct: [-3, -1, 0, 2, 5]
```

**Fix:** Handle negatives separately (sort absolute values, reverse, prefix to positive result) or offset all values to make non-negative.

**Prevention:** Document clearly whether the sort supports negative integers. Add input validation.

---

**3. Radix too large causing memory exhaustion**

**Symptom:** `OutOfMemoryError` during Radix Sort.

**Root Cause:** Choosing r=2^16 (65536) creates a count array of 65536 entries — fine. But if this is called in inner loops or with many threads, multiplication of N × r auxiliary arrays exhausts heap.

**Diagnostic:**
```bash
java -verbose:gc -Xmx512m RadixSort
# Look for: "GC overhead limit exceeded"
# Profile with: jcmd <pid> VM.native_memory
```

**Fix:** Use r=256 (byte-level radix) as the default. Only increase radix if profiling shows pass count is the bottleneck and memory is available.

**Prevention:** Benchmark D×(N+r) vs (N+r)×D for different r values before choosing. Default to r=256.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Counting Sort` — the stable sub-sort used within each Radix Sort pass; understanding counting sort is essential.
- `Arrays` — Radix Sort requires auxiliary array allocation and copying; understand array operations.
- `Time Complexity / Big-O` — understanding why Radix Sort breaks the comparison-sort barrier requires understanding the lower bound proof.

**Builds On This (learn these next):**
- `Suffix Array Construction` — the DC3/Skew algorithm uses radix sort on character triplets to build suffix arrays in O(N).
- `External Sort` — radix sort chunks processed and streamed from/to disk in large-scale sort scenarios.
- `GPU Sorting` — radix sort parallelises trivially (each counting sort pass is independent per element); used in GPU CUDA sort libraries.

**Alternatives / Comparisons:**
- `Counting Sort` — O(N+k) for keys in [0,k); radix sort is counting sort extended to larger ranges via digit decomposition.
- `Bucket Sort` — partitions into uniformly-distributed buckets; requires uniform distribution; Radix Sort makes no distribution assumptions.
- `Mergesort` — general, works on any comparable type; O(N log N); stable; use when Radix Sort is inapplicable.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Non-comparative integer sort: process     │
│              │ digit-by-digit with stable counting sort  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Break O(N log N) comparison-sort barrier  │
│ SOLVES       │ for fixed-domain integers                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stability is mandatory in sub-sort;       │
│              │ D×N beats NlogN only when D << logN       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Large N, fixed-width integers, small D    │
│              │ (IP sorting, suffix arrays, histograms)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Variable-length keys; floating-point;     │
│              │ small N (Quicksort constant factor wins)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N×D) sub-linear vs O(N log N) but       │
│              │ requires integer-decompositional keys     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sort by last digit first, then next —    │
│              │  never compare full numbers"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Counting Sort → Suffix Array → GPU Sort   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The comparison-sort lower bound of Ω(N log N) is proven by the decision tree argument: any comparison sort corresponds to a binary decision tree with at least N! leaves (one per permutation). The tree height ≥ log₂(N!) = Ω(N log N). Radix Sort "escapes" this lower bound. Explain precisely at which step the decision tree argument breaks down for Radix Sort. What opertion does Radix Sort use instead of comparisons, and why is the decision tree model inapplicable?

**Q2.** The optimal radix r for sorting N integers each with W bits should minimise D × (N + r) where D = W/log₂(r). Setting the derivative to zero gives r = N (base-N sort with W/log(N) passes). But using r=N means allocating a counting array of size N per pass — potentially enormous. For W=32 bits and varying N from 10^4 to 10^9, calculate the optimal r and total operation count for each N. At what N does base-N sort (r=N, D=1 pass) become better than byte-level sort (r=256, D=4 passes), and what is the hidden practical factor that prevents base-N sort from being used in practice?

