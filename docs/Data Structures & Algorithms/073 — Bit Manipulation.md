---
layout: default
title: "Bit Manipulation"
parent: "Data Structures & Algorithms"
nav_order: 73
permalink: /dsa/bit-manipulation/
number: "0073"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Binary Numbers, Integer Representation, Time Complexity / Big-O
used_by: Bloom Filter, Hashing Techniques, Dynamic Programming
related: Bitwise Operators, Integer Overflow, Space-Time Trade-off
tags:
  - algorithm
  - advanced
  - deep-dive
  - performance
  - datastructure
---

# 073 — Bit Manipulation

⚡ TL;DR — Bit Manipulation uses CPU bitwise operations directly on integers to solve problems in O(1) with no extra memory, replacing expensive loops and conditionals.

| #0073 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Binary Numbers, Integer Representation, Time Complexity / Big-O | |
| **Used by:** | Bloom Filter, Hashing Techniques, Dynamic Programming | |
| **Related:** | Bitwise Operators, Integer Overflow, Space-Time Trade-off | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Count the number of 1-bits in a 32-bit integer. The naive loop tests each bit: `for i in 0..31: count += (n >> i) & 1`. That's 32 iterations per call. A graphics engine invoking this 10 million times per frame burns 320 million iterations per frame at 60 FPS — 19 billion loop iterations per second just for this one operation.

**THE BREAKING POINT:**
Many algorithms with loop-based solutions can be replaced by constant-time bitwise idioms because CPUs execute AND, OR, XOR, SHIFT natively in a single clock cycle — often faster than a branch. Operations on 64-bit integers process 64 elements simultaneously. When the data fits in bits, the "loop over bits" is the wrong level of abstraction.

**THE INVENTION MOMENT:**
CPUs operate on integers natively at the bit level. By treating an integer as a set of 64 Boolean flags, you perform 64 logical operations in one CPU instruction. Finding the lowest set bit (`n & -n`), clearing the lowest bit (`n & (n-1)`), checking power-of-two (`n & (n-1) == 0`) — all become single expressions. This is exactly why **Bit Manipulation** is a fundamental technique.

---

### 📘 Textbook Definition

**Bit Manipulation** is the use of bitwise operators (AND `&`, OR `|`, XOR `^`, NOT `~`, left shift `<<`, right shift `>>`, unsigned right shift `>>>`) to operate directly on the binary representation of integers. Because CPUs execute these operations in O(1) on their native word size (32 or 64 bits), bit manipulation replaces loops over individual flags with single-instruction alternatives. Common applications include set operations using integer bitmasks, power-of-two checks, population count, lowest/highest bit extraction, and XOR-based identity/cancellation tricks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use single CPU instructions on integer binary patterns instead of loops over individual bits.

**One analogy:**
> A light switch panel with 32 switches. Flipping switch 5 by hand takes time proportional to finding it. With bit manipulation, you simultaneously set all even switches ON and odd switches OFF in one operation — like a control board with one flip affecting all even-numbered circuits at once.

**One insight:**
The most non-obvious bit trick is `n & (n-1)` — it clears the lowest set bit of `n` in O(1). This is the foundation of **Brian Kernighan's algorithm** for counting bits: instead of looping 32 times, loop only as many times as there are 1-bits. For sparse integers (few 1-bits), this is dramatically faster.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Integers are stored as binary patterns; the CPU can AND, OR, XOR, SHIFT any two 64-bit integers in a single clock cycle.
2. `n & (n-1)` always clears the lowest set bit of `n` — proof: the lowest set bit of `n` is at position `k`; `n-1` flips all bits from 0 to k, and ANDing clears bit k and everything below.
3. `n & (-n)` isolates the lowest set bit of `n` — proof: `-n` in two's complement equals `~n + 1`, so the lowest set bit of `n` survives and all others are cleared.

**DERIVED DESIGN:**
From these three invariants, most bit tricks follow:
- **Check power of 2:** `n > 0 && (n & (n-1)) == 0` — a power of 2 has exactly one set bit.
- **Count bits (Kernighan):** loop `while (n != 0) { count++; n &= (n-1); }` — O(#setBits).
- **Swap without temp:** `a ^= b; b ^= a; a ^= b` — XOR self-inverse property: `a ^ a = 0`.
- **Toggle bit k:** `n ^= (1 << k)`.
- **Set bit k:** `n |= (1 << k)`.
- **Clear bit k:** `n &= ~(1 << k)`.
- **Check bit k:** `(n >> k) & 1`.

**Bitmask as set:**
An integer can represent a subset of {0,1,...,63}: bit k is set iff element k is in the subset. Union = OR, intersection = AND, difference = `A & ~B`. This enables O(1) set operations and O(2^N) DP over all subsets (bitmask DP).

**THE TRADE-OFFS:**
**Gain:** O(1) per operation vs O(N) loops; no extra memory; exploits CPU native instruction set.
**Cost:** Code readability suffers severely — `n & -n` is opaque without comment. Restricted to fixed-size integers (32 or 64 bits). Bitmask DP explodes at N > 20 (2^20 = 1M states; 2^30 = 1B — impractical).

---

### 🧪 Thought Experiment

**SETUP:**
Given N=20 items, find the minimum cost to visit all items exactly once (Travelling Salesman Problem variant). You need to track "which items have been visited" as state.

**WHAT HAPPENS WITHOUT BIT MANIPULATION:**
Represent visited set as `boolean[] visited`. Copying the array for each DP state costs O(N) per state. With 2^20 × 20 states, each copying O(N) array: 2^20 × 20 × 20 = ~400 million copies.

**WHAT HAPPENS WITH BIT MANIPULATION:**
Represent visited set as a single integer `mask` where bit k = 1 means item k is visited. `dp[mask][last]` = min cost to visit exactly the items in `mask`, ending at `last`. Transitions: `dp[mask | (1<<next)][next]`. Each transition is one OR operation. No array copy. State space: 2^20 × 20 = ~20 million integers. 20× speedup.

**THE INSIGHT:**
An integer is a compressed Boolean array. When N ≤ 20, fitting the entire visited-set into one 32-bit integer reduces memory by 32× and eliminates all per-state allocation. This "bitmask DP" approach makes TSP on 20 cities tractable in milliseconds.

---

### 🧠 Mental Model / Analogy

> Think of a 32-bit integer as a row of 32 light bulbs, each either ON (1) or OFF (0). Bitwise AND with a mask turns off all bulbs not in the mask simultaneously. Bitwise XOR with a mask toggles exactly the masked bulbs. All 32 bulbs update in one CPU clock cycle — not one by one.

- "Light bulb ON" → bit is 1
- "Light bulb OFF" → bit is 0
- "Mask with AND" → turn off specified bulbs (clear bits)
- "Mask with OR" → turn on specified bulbs (set bits)
- "Mask with XOR" → toggle specified bulbs
- "Check bulb k" → `(n >> k) & 1`

Where this analogy breaks down: Physical bulbs are independent; integer bits interact in two's complement arithmetic (e.g., `-n` in two's complement flips all bits and adds 1 — not a simple toggle). This is why `n & -n` (isolate lowest bit) is non-obvious from the light bulb model.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Numbers are stored in computers as sequences of 0s and 1s. Bit Manipulation is a set of tricks to work directly with those 0s and 1s — like operating a control panel where one flip simultaneously changes multiple digits. These tricks can replace many slow loops with a single operation.

**Level 2 — How to use it (junior developer):**
Learn the six core operations: set bit k (`n |= 1<<k`), clear bit k (`n &= ~(1<<k)`), toggle bit k (`n ^= 1<<k`), check bit k (`(n >> k) & 1`), isolate lowest bit (`n & -n`), clear lowest bit (`n & (n-1)`). Use `Integer.bitCount(n)` in Java for population count (maps to `POPCNT` hardware instruction). Represent small sets as integers for combinatorics problems.

**Level 3 — How it works (mid-level engineer):**
XOR has three key properties: self-inverse (`a ^ a = 0`), identity (`a ^ 0 = a`), commutativity. This makes XOR ideal for finding a single number that appears an odd number of times — XOR all numbers; duplicates cancel. For bitmask DP: state is an integer `mask`, iterate from 0 to `(1<<N)-1`, use `mask & (mask-1)` to enumerate all submasks. For cycle detection: Floyd's in-place XOR swap avoids a temporary variable. Hardware POPCNT (available via `Integer.bitCount`) counts set bits in one instruction cycle on x86.

**Level 4 — Why it was designed this way (senior/staff):**
Bit manipulation exploits the algebraic structure of the ring Z/2^nZ and the Galois field GF(2). XOR is addition in GF(2); AND is multiplication. LFSR (Linear Feedback Shift Register) pseudo-random generators exploit GF(2) polynomial arithmetic. In cryptography, AES S-boxes are defined over GF(2^8) with operations implementable as bit manipulations for performance. SIMD (AVX-512) extends the concept: 512-bit registers process 8 doubles or 64 bytes simultaneously — the "all bits at once" model extended to entire vectors. Understanding bit manipulation is the prerequisite to understanding SIMD, LFSR, CRC computation, and cryptographic primitives.

---

### ⚙️ How It Works (Mechanism)

**Core Bit Operations Reference:**

```
┌──────────────────────────────────────────────┐
│ Operation        │ Expression    │ Effect     │
├──────────────────┼───────────────┼────────────┤
│ Check bit k      │ (n>>k) & 1    │ 0 or 1     │
│ Set bit k        │ n |= 1<<k     │ bit=1      │
│ Clear bit k      │ n &= ~(1<<k)  │ bit=0      │
│ Toggle bit k     │ n ^= 1<<k     │ flip bit   │
│ Lowest set bit   │ n & -n        │ isolate    │
│ Clear lowest bit │ n & (n-1)     │ remove     │
│ Is power of 2    │ n>0 & n&(n-1)=│ bool check │
│ Count set bits   │ Integer       │ POPCNT     │
│                  │ .bitCount(n)  │            │
└──────────────────────────────────────────────┘
```

**Brian Kernighan's Bit Count (vs naive):**
```
n = 1010 0110  (binary)
Kernighan: loop 4 times (4 set bits)
Naive:     loop 8 times (checks all bits)
For n=255: Kernighan=8 loops, Naive=8 loops
For n=1:   Kernighan=1 loop,  Naive=8 loops
```

**Bitmask DP state transition:**
```
┌──────────────────────────────────────────────┐
│ Bitmask DP: Minimum Vertex Cover example     │
│                                              │
│ N = 4 nodes                                  │
│ mask = 0101 means nodes {0, 2} selected      │
│                                              │
│ Add node 1: mask | (1<<1) = 0111             │
│ Remove node 2: mask & ~(1<<2) = 0001         │
│ Is node 3 in mask: (mask >> 3) & 1 = 0       │
│                                              │
│ Enumerate all subsets of mask:               │
│ for(sub=mask; sub>0; sub=(sub-1)&mask)       │
│   ... process subset 'sub'                  │
└──────────────────────────────────────────────┘
```

**XOR trick — find the single non-duplicate:**
XOR all elements. Duplicates cancel (`x ^ x = 0`). Single element remains (`x ^ 0 = x`). O(N) time, O(1) space.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Problem with Boolean set / flag tracking
→ Identify N ≤ 64 binary flags
→ Encode flags as bits of a single integer
→ [BIT MANIPULATION ← YOU ARE HERE]
  → Replace flag loops with bitwise operations
  → Replace set operations with &, |, ^, ~
  → Replace iteration with bit tricks
→ O(1) per operation instead of O(N) loop
→ 64× parallelism on 64-bit integers
```

**FAILURE PATH:**
```
N > 64 → single integer insufficient
→ Overflow / wrong results silently
→ Fix: use BitSet for N > 64 or segment into multiple longs
→ Diagnostic: assert n <= 64 before using long bitmask
```

**WHAT CHANGES AT SCALE:**
At scale, hardware population count (`POPCNT`) and bit-scan instructions (`BSF`, `BSR`) execute in 1 clock cycle with perfect pipelining. Language runtimes expose these: Java `Integer.bitCount` → `POPCNT`, Java `Integer.numberOfTrailingZeros` → `BSF`. In columnar databases, Roaring Bitmaps store billions of integer sets using packed bit arrays with run-length encoding, enabling set intersection/union at billions of integers per second — all built on bit manipulation primitives.

---

### 💻 Code Example

**Example 1 — Core tricks:**
```java
// Check if bit k is set
boolean isBitSet(int n, int k) {
    return ((n >> k) & 1) == 1;
}
// Set bit k
int setBit(int n, int k) { return n | (1 << k); }
// Clear bit k
int clearBit(int n, int k) { return n & ~(1 << k); }
// Toggle bit k
int toggleBit(int n, int k) { return n ^ (1 << k); }
// Count set bits (Brian Kernighan)
int countBits(int n) {
    int count = 0;
    while (n != 0) { n &= (n - 1); count++; }
    return count;
}
// Or: Java built-in (maps to single POPCNT instruction)
int fastCount(int n) { return Integer.bitCount(n); }
```

**Example 2 — XOR find single number:**
```java
// In array [4,1,2,1,2], find the element appearing once
// XOR: 4^1^2^1^2 = 4^(1^1)^(2^2) = 4^0^0 = 4
int singleNumber(int[] nums) {
    int result = 0;
    for (int n : nums) result ^= n;
    return result; // O(N) time, O(1) space
}
```

**Example 3 — Bitmask DP (TSP on N≤20 cities):**
```java
int tsp(int[][] dist, int n) {
    int FULL = (1 << n) - 1;
    // dp[mask][i] = min cost ending at city i,
    //               visiting exactly cities in mask
    int[][] dp = new int[1 << n][n];
    for (int[] row : dp) Arrays.fill(row, Integer.MAX_VALUE/2);
    dp[1][0] = 0; // start at city 0, mask=0001
    for (int mask = 1; mask <= FULL; mask++) {
        for (int u = 0; u < n; u++) {
            if ((mask & (1 << u)) == 0) continue;
            if (dp[mask][u] == Integer.MAX_VALUE/2) continue;
            for (int v = 0; v < n; v++) {
                if ((mask & (1 << v)) != 0) continue;
                int nm = mask | (1 << v);
                dp[nm][v] = Math.min(dp[nm][v],
                    dp[mask][u] + dist[u][v]);
            }
        }
    }
    int ans = Integer.MAX_VALUE;
    for (int u = 1; u < n; u++)
        ans = Math.min(ans, dp[FULL][u] + dist[u][0]);
    return ans;
}
```

**Example 4 — Power of 2 and lowest bit isolation:**
```java
boolean isPowerOfTwo(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
// Isolate lowest set bit: n=0110 → result=0010
int lowestSetBit(int n) { return n & -n; }
// Clear lowest set bit: n=0110 → result=0100
int clearLowestBit(int n) { return n & (n - 1); }
```

---

### ⚖️ Comparison Table

| Approach | Time | Space | Clarity | Best For |
|---|---|---|---|---|
| **Bit Manipulation** | O(1)–O(#bits) | O(1) | Low | N≤64 flags, performance-critical paths |
| Boolean Array | O(N) | O(N) | High | N > 64 flags, readable code |
| HashSet | O(1) avg | O(N) | High | Dynamic sets with arbitrary elements |
| java.util.BitSet | O(1) per op | O(N/64) | Medium | N > 64 binary flags, Java standard |
| Bitmask DP | O(2^N × N) | O(2^N × N) | Low | N ≤ 20 subsets enumeration |

How to choose: Use bit manipulation for N ≤ 64 performance paths. Use `BitSet` for N > 64. Use HashSet when elements are not small integers or when code clarity is paramount.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bit manipulation is only useful in competitive programming | It appears in production: JDK's `HashMap` uses bit masking for bucket index (`hash & (n-1)`); Java `BitSet` for NIO buffers; Redis uses bit fields natively; columnar DBs use bitmaps for WHERE clauses. |
| `n & (n-1)` is the same as `n - 1` | `n-1` subtracts 1 (may change many bits); `n & (n-1)` clears only the lowest set bit. Very different results: for n=8 (1000), n-1=7 (0111), n&(n-1)=0. |
| XOR swap (`a^=b; b^=a; a^=b`) is always better | XOR swap is NOT safe when `a` and `b` are the same variable or alias — it zeroes out the value. Always use a temp variable for aliasing cases. |
| Right shift `>>` and `>>>` are identical | `>>` is arithmetic (preserves sign bit for negatives); `>>>` is logical (always fills with 0). For negative numbers: `(-1) >> 1 = -1`, `(-1) >>> 1 = Integer.MAX_VALUE`. |
| Bit counting loops are always 32 iterations | Brian Kernighan's algorithm loops once per set bit (popcount), not per total bits. For sparse integers this is dramatically faster. |

---

### 🚨 Failure Modes & Diagnosis

**1. Integer overflow in shift operations**

**Symptom:** `1 << 31` gives `-2147483648`; `1 << 32` is `1` (wraps) — both silently wrong.

**Root Cause:** Java `int` is 32 bits. Shifting by ≥ 32 is undefined / wraps in Java. `1 << 31` sets the sign bit → negative.

**Diagnostic:**
```java
System.out.println(1 << 31);  // prints -2147483648
System.out.println(1 << 32);  // prints 1 (wrapped)
System.out.println(1L << 31); // prints 2147483648 ✓
```

**Fix:** Use `1L << k` for shifts ≥ 31 to promote to `long`.

**Prevention:** Always use `long` bitmasks for bit positions ≥ 31.

---

**2. XOR swap on aliased variables**

**Symptom:** Variable becomes zero after supposed swap.

**Root Cause:** `a ^= b; b ^= a; a ^= b` when `a` and `b` are the same variable: `a ^= a` → `a = 0`; all subsequent steps see 0.

**Diagnostic:**
```java
int[] arr = {1, 2, 3};
int i = 1, j = 1; // same index!
arr[i] ^= arr[j];
arr[j] ^= arr[i];
arr[i] ^= arr[j]; // arr[1] = 0 — wrong!
```

**Fix:** Guard with `if (i != j)` before XOR swap, or always use a temporary variable.

**Prevention:** Never use XOR swap in sorting algorithms where `i == j` is possible.

---

**3. Signed vs unsigned right shift confusion**

**Symptom:** Bit operations on negative numbers produce unexpected large positive values.

**Root Cause:** `>>` fills with the sign bit (1 for negatives), `>>>` fills with 0. Using `>>>` on a negative int sign-extends incorrectly.

**Diagnostic:**
```java
int n = -4;
System.out.println(n >> 1);   // -2 (arithmetic)
System.out.println(n >>> 1);  // 2147483646 (logical)
```

**Fix:** Use `>>` for signed arithmetic; `>>>` only when treating the value as unsigned bits (e.g., HashMap hash distribution).

**Prevention:** Default to `>>` unless you explicitly need unsigned shift.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Binary Numbers` — Bit manipulation operates on the binary representation of integers; understanding two's complement is essential to grasping `n & -n`.
- `Integer Representation` — Understanding overflow, sign bits, and two's complement explains why `-n = ~n + 1` and how arithmetic shifts work.

**Builds On This (learn these next):**
- `Bloom Filter` — Uses multiple bit positions as a compact probabilistic set; entire hash-indexed bit array manipulated with bit operations.
- `Bitmask Dynamic Programming` — Uses integer subsets as DP state keys; enables O(2^N × N) solutions to subset enumeration problems.
- `Hashing Techniques` — Hash functions often use XOR and shifts (MurmurHash, FNV) to mix bits uniformly.

**Alternatives / Comparisons:**
- `Boolean Array` — More readable, O(N) space; use when N > 64 or clarity is priority.
- `java.util.BitSet` — Java standard library bit array for arbitrary N; slower per operation than native int due to object overhead.
- `Set<Integer>` — O(1) average operations but O(N) space with high constant; use when elements are non-consecutive.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Direct O(1) operations on integer binary  │
│              │ representations using CPU bitwise ops     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(N) loops over Boolean flags waste CPU;  │
│ SOLVES       │ replace with 1-cycle bitwise instructions │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ n & (n-1) clears lowest bit in O(1);      │
│              │ integer = compressed 64-element bool set  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ N ≤ 64 flags; performance-critical;       │
│              │ bitmask DP over all subsets (N ≤ 20)      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N > 64 (use BitSet); code clarity is      │
│              │ paramount; elements are non-integers      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) constant factor & O(1) space vs      │
│              │ near-zero code readability                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your integer is a tiny parallel computer"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bitmask DP → Bloom Filter → SIMD/AVX      │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The XOR trick finds the single number in `O(N)` time and `O(1)` space. Now the problem changes: exactly two numbers appear an odd number of times. The XOR of all elements gives `a ^ b` (where a and b are the two unique numbers). How do you use `(a^b) & -(a^b)` to split all numbers into two groups and XOR-find each unique number separately? Walk through the algorithm for `[1,2,1,3,2,5]`.

**Q2.** In Bitmask DP for the Travelling Salesman on N=20 cities, the state space is 2^20 × 20 ≈ 20M states. Each state fit in 32 bits. At 20M states × 4 bytes = 80 MB. Now scale to N=30: 2^30 × 30 ≈ 32B states × 4 bytes = 128 GB — infeasible. What algorithmic alternative exists for N=30, and why does bitmask DP's exponential state growth preclude it from scaling beyond N≈24 on modern hardware?

