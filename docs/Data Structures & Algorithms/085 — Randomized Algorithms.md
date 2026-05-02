---
layout: default
title: "Randomized Algorithms"
parent: "Data Structures & Algorithms"
nav_order: 85
permalink: /dsa/randomized-algorithms/
number: "0085"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Time Complexity / Big-O, Probability Theory, Monte Carlo vs Las Vegas Algorithms
used_by: Hashing Techniques, Approximation Algorithms, Bloom Filter
related: Monte Carlo vs Las Vegas Algorithms, Approximation Algorithms, Greedy Algorithm
tags:
  - algorithm
  - advanced
  - deep-dive
  - performance
  - pattern
---

# 085 — Randomized Algorithms

⚡ TL;DR — Randomized algorithms use random choices during execution to achieve better expected performance, simpler design, or resistance to adversarial inputs compared to deterministic algorithms.

| #0085 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Time Complexity / Big-O, Probability Theory, Monte Carlo vs Las Vegas Algorithms | |
| **Used by:** | Hashing Techniques, Approximation Algorithms, Bloom Filter | |
| **Related:** | Monte Carlo vs Las Vegas Algorithms, Approximation Algorithms, Greedy Algorithm | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
QuickSort is O(N log N) average but O(N²) worst case — triggered by always-sorted or always-reverse-sorted input. An adversary who knows your pivot selection strategy (always pick first element) can craft inputs that degrade every call to O(N²). In production, a sorted request log triggers O(N²) sorting — a DoS vulnerability.

THE BREAKING POINT:
Deterministic algorithms have exploitable worst-case inputs. Any algorithm that always makes the same choice given the same input can be attacked. At N=10^6, O(N²) = 10^12 operations — a 1,000-second sort that should take 0.02 seconds.

THE INVENTION MOMENT:
If the pivot is chosen uniformly at random, no adversary can reliably craft a bad input — each particular input is "bad" with only 1/N probability for any given choice. Randomise the pivot: expected O(N log N) with high probability regardless of input order. No adversary can predict the coin flip. This is exactly why **Randomized Algorithms** are valuable.

### 📘 Textbook Definition

A **randomized algorithm** uses random bits (coin flips, random samples, random permutations) during execution. Its correctness or performance guarantees are probabilistic rather than deterministic. **Las Vegas algorithms** always produce correct output but have random running time (e.g., randomised QuickSort: always sorts correctly, expected O(N log N) runtime). **Monte Carlo algorithms** always terminate in bounded time but may produce incorrect output with bounded probability (e.g., Miller-Rabin primality test: O(k log²N) time, error probability ≤ 1/4^k). Randomized algorithms typically achieve: (1) better expected complexity than deterministic worst case, (2) algorithmic simplicity, (3) resistance to adversarial inputs.

### ⏱️ Understand It in 30 Seconds

**One line:**
Flip coins during the algorithm to prevent adversaries from crafting bad inputs and to break symmetry cheaply.

**One analogy:**
> A fair coin flip in a referee dispute: instead of the referee making a potentially biased decision (exploitable by the home team), a coin flip makes the outcome truly unpredictable. Neither team can game it — the randomness is the fairness guarantee.

**One insight:**
Randomization achieves two fundamentally different goals: (1) **Adversarial resistance** — no deterministic input can always trigger worst-case behaviour if the algorithm's choices are unpredictable. (2) **Symmetry breaking** — when multiple equally valid choices exist, a random choice removes the need for complex tie-breaking logic while maintaining correct expected behaviour.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The probability distribution is over the **algorithm's random choices**, not over the input distribution — the input is chosen by an adversary; the random bits are private.
2. **Las Vegas:** always correct, runtime is a random variable with finite expectation.
3. **Monte Carlo:** runs in bounded deterministic time, output is correct with probability ≥ 1 - δ (δ = error probability, can be made arbitrarily small by repetition).

DERIVED DESIGN:
**Randomized QuickSort analysis:** Choose pivot at random from [0, N-1]. Expected number of comparisons = E[X] = Σᵢ<ⱼ Pr[i and j compared] = Σᵢ<ⱼ 2/(j-i+1) = O(N log N). This is because elements i and j are compared only when one is the first pivot chosen from [i..j]; probability = 2/(j-i+1). This holds for ANY input permutation.

**Random hash function (universal hashing):** Choose a random hash function from a universal family. For any two distinct keys x ≠ y: Pr[h(x) = h(y)] ≤ 1/m (m = table size). No adversary can craft keys that all collide, since they don't know which hash function was chosen.

THE TRADE-OFFS:
Gain: Expected O(N log N) QuickSort regardless of input; O(1) expected hash table operations without adversarial vulnerability; algorithmic simplicity.
Cost: Non-deterministic behaviour — debugging harder; tests may pass/fail non-reproducibly; security-critical systems need cryptographically secure RNG (slower than PRNG); error probability in Monte Carlo (must be handled).

### 🧪 Thought Experiment

SETUP:
Sort N=1,000,000 integers with deterministic QuickSort (always pivot at first element) vs randomised QuickSort on adversarial input: the sorted array [1, 2, 3, ..., 1,000,000].

WHAT HAPPENS WITH DETERMINISTIC QUICKSORT:
Pivot = 1 (first element). Partition: left=[], right=[2,...,1M]. Cost: N comparisons. Recurse on [2,...,1M]. Pivot = 2. Cost: N-1 comparisons. Total: N + (N-1) + ... + 1 = N(N+1)/2 ≈ 500 billion comparisons at N=1M. ~500 seconds on modern hardware.

WHAT HAPPENS WITH RANDOMIZED QUICKSORT:
Pivot chosen uniformly at random. For [1,...,N], a random pivot has a 50% chance of landing in the "good middle" (between N/4 and 3N/4). Expected depth: O(log N). Expected total comparisons: O(N log N) = ~20M. ~0.02 seconds.

THE INSIGHT:
The adversarial input [1,...,1M] perfectly exploits deterministic pivot selection. Randomised selection makes no input consistently bad. The adversary would need to predict the random bits — impossible if the RNG is unpredictable.

### 🧠 Mental Model / Analogy

> A randomized algorithm is like a taxi driver who chooses a random route each day. An adversary (traffic jam orchestrator) can't reliably make them late — they don't know which route was chosen. The deterministic driver (always takes Route 1) is perfectly predictable and always gets stuck if the adversary chooses to block Route 1.

"Random route" → random algorithm choice (pivot, hash function)
"Adversarial traffic jam" → adversarial input designed for worst case
"Unpredictability" → protection against adversarial input
"Some routes still slow" → bad random choices still occur (with low probability)
"Expected travel time" → expected algorithm runtime

Where this analogy breaks down: A taxi driver remembers past routes (no memory); a randomized algorithm makes fresh random choices each time. Also, the driver's RNG (which route to choose) must be truly random, not just "varied" — a pseudorandom but predictable sequence still allows adversarial exploitation.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Randomized algorithms flip coins during their execution to make unpredictable choices. This prevents anyone from designing inputs that always make the algorithm slow, and often makes the algorithm simpler. The price: the algorithm might occasionally be slower than expected, but on average it's fast.

**Level 2 — How to use it (junior developer):**
Use `Collections.shuffle(list)` before QuickSort to randomise pivot selection. Use `Math.random()` or `ThreadLocalRandom` for randomised choices. Use Miller-Rabin primality test (Java `BigInteger.isProbablePrime(certainty)`) for fast near-certain primality testing. For hash maps, Java uses a randomised seed per JVM start (added Java 8) to resist HashDoS attacks.

**Level 3 — How it works (mid-level engineer):**
**Randomized QuickSort probability analysis:** Expected comparisons = 2N ln N. For N=10^6: 2 × 10^6 × 13.8 ≈ 27.6M comparisons. Probability of taking > 4N ln N comparisons: ≤ 1/N (by Markov's inequality). So for N=10^6, probability of runtime > 4× expected is ≤ 10^-6. Practically guaranteed O(N log N). **Karger's min-cut algorithm:** Randomly contracts edges; probability of finding minimum cut = Ω(1/N²); repeating O(N² log N) times gives high-probability correct result.

**Level 4 — Why it was designed this way (senior/staff):**
The power of randomization in algorithms is formalised by the probabilistic method (Erdős): if a random object has a positive probability of satisfying a property, then an object satisfying the property must exist. This is a non-constructive proof technique of enormous reach. Derandomization — removing randomness from randomized algorithms using pseudorandom generators — is a central goal of complexity theory. If P = BPP (derandomization is generally possible), every randomized poly-time algorithm has a deterministic poly-time equivalent. Most researchers believe P = BPP, making randomization a "convenience" rather than fundamental power.

### ⚙️ How It Works (Mechanism)

**Randomized QuickSort:**

```
┌────────────────────────────────────────────────┐
│ Randomized QuickSort                           │
│                                                │
│ randomPartition(arr, low, high):               │
│   rand = random integer in [low, high]         │
│   swap arr[rand] with arr[high]  ← random pivot│
│   return deterministicPartition(arr,low,high)  │
│                                                │
│ Expected comparisons bound:                    │
│   For any pair (i,j) with i<j:                 │
│   Pr[i and j compared] = 2 / (rank(j)-rank(i)+1)│
│   Summing over all pairs: O(N log N)            │
│   Holds for ANY fixed input permutation        │
└────────────────────────────────────────────────┘
```

**Miller-Rabin Primality (Monte Carlo):**

```
┌────────────────────────────────────────────────┐
│ Miller-Rabin: O(k × log²N) time                │
│                                                │
│ Input: N (candidate), k (rounds)               │
│ For each round:                                │
│   Pick random a ∈ [2, N-2]                     │
│   Check Fermat-like witness condition          │
│   If "composite witness" found → COMPOSITE (certain)│
│   If no witness found → "probably prime"       │
│                                                │
│ After k rounds, error ≤ (1/4)^k               │
│ k=40 rounds: error ≤ 10^-24 (negligible)       │
│ Used in: Java BigInteger.isProbablePrime(80)   │
│   (80 = certainty = 40 × 2 rounds)             │
└────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Algorithm with deterministic worst-case weakness
→ Identify adversarially exploitable decision point
→ [RANDOMIZE ← YOU ARE HERE]
  → Replace deterministic choice with random choice
  → Analyse expected time (Las Vegas) or error (Monte Carlo)
→ Verify: expected complexity ≤ deterministic average
→ Verify: error probability controllable (Monte Carlo only)
→ Deploy with CSPRNG for security-critical uses
```

FAILURE PATH:
```
Predictable PRNG in security context
→ Adversary seeds same PRNG → predicts random choices
→ Hash table DoS attack still possible
→ Fix: use SecureRandom / OS entropy (/dev/urandom) for crypto uses
→ ThreadLocalRandom for non-security performance uses
→ Diagnostic: audit PRNG usage in security-critical paths
```

WHAT CHANGES AT SCALE:
At 100M requests/second, Java HashMap with per-JVM random seed resists HashDoS. But ConcurrentHashMap in high-concurrency workloads benefits from additional randomization in key distribution. For distributed systems, Consistent Hashing uses random virtual nodes to achieve uniform load balance — the randomness absorbs hotspot patterns. In machine learning, Stochastic Gradient Descent (SGD) randomly samples mini-batches — the randomness escapes local optima and accelerates convergence over full-batch gradient descent.

### 💻 Code Example

**Example 1 — Randomized QuickSort:**
```java
void randomQuickSort(int[] arr, int low, int high) {
    if (low < high) {
        int pivot = randomPartition(arr, low, high);
        randomQuickSort(arr, low, pivot - 1);
        randomQuickSort(arr, pivot + 1, high);
    }
}
int randomPartition(int[] arr, int low, int high) {
    // Random pivot selection: adversarial-resistant
    int r = low + ThreadLocalRandom.current()
        .nextInt(high - low + 1);
    int tmp = arr[r]; arr[r] = arr[high]; arr[high] = tmp;
    return deterministicPartition(arr, low, high);
}
```

**Example 2 — Las Vegas: Randomized SELECT (k-th smallest):**
```java
// Expected O(N), worst case O(N²) — Las Vegas
int randomSelect(int[] arr, int low, int high, int k) {
    if (low == high) return arr[low];
    int pivot = randomPartition(arr, low, high);
    int rank = pivot - low + 1;
    if (k == rank) return arr[pivot];
    else if (k < rank)
        return randomSelect(arr, low, pivot-1, k);
    else
        return randomSelect(arr, pivot+1, high, k-rank);
}
```

**Example 3 — Monte Carlo: Karger's min-cut (probabilistic):**
```java
// Run many times; take minimum cut found
int kargerMinCut(int[][] adj, int V, int iterations) {
    int minCut = Integer.MAX_VALUE;
    for (int i = 0; i < iterations; i++) {
        // Contract random edges until 2 vertices remain
        int[] parent = new int[V * 2];
        // ... (union-find based contraction) ...
        int cut = countCrossEdges(parent, adj);
        minCut = Math.min(minCut, cut);
    }
    return minCut;
    // Success probability: Ω(1/N²) per trial
    // O(N² log N) iterations → high probability correct
}
```

**Example 4 — Bloom filter (probabilistic membership):**
```java
class BloomFilter {
    private final long[] bits;
    private final int[] seeds; // random hash seeds
    BloomFilter(int capacity, int numHashes) {
        bits = new long[(capacity >> 6) + 1];
        seeds = generateRandomSeeds(numHashes);
    }
    void add(String s) {
        for (int seed : seeds)
            setBit(hash(s, seed) % (bits.length * 64));
    }
    boolean mightContain(String s) {
        for (int seed : seeds)
            if (!getBit(hash(s, seed) % (bits.length * 64)))
                return false; // definitely not present
        return true; // probably present (false positive possible)
    }
}
```

### ⚖️ Comparison Table

| Algorithm Type | Correctness | Runtime | Error | Best For |
|---|---|---|---|---|
| **Deterministic** | Always correct | Guaranteed worst case | None | When worst-case guarantee required |
| **Las Vegas** | Always correct | Expected, not guaranteed | None | Sorting, selection, hashing |
| **Monte Carlo** | Correct with prob. | Guaranteed | Bounded (1/4^k) | Primality, min-cut, approximation |
| **Atlantic City** | Correct with high prob. | Expected | Bounded | Theoretical interest |
| **Pseudo-random Det.** | Always correct | Expected (if no adversary) | None | Non-adversarial environments |

How to choose: Use Las Vegas when correctness must be guaranteed (randomized QuickSort). Use Monte Carlo when a polynomial time bound is more important than perfect correctness and errors are controllable by repetition (Miller-Rabin, HyperLogLog).

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Randomized algorithms are approximations | Las Vegas algorithms are EXACTLY correct — only their runtime is random. Monte Carlo trades error for speed, but the error probability can be reduced to 10^-100 with enough repetitions. |
| rand() is sufficient for randomized algorithms | `rand()` in most languages uses a PRNG with known seed that can be predicted. For adversarial resistance (HashDoS protection), use a CSPRNG or hash map with randomised seed per start. |
| Randomized algorithms are faster than deterministic ones | They achieve better EXPECTED complexity vs WORST-CASE deterministic. Deterministic algorithms with provably optimal worst-case complexity (like HeapSort: O(N log N) worst) can be faster for specific inputs. |
| Monte Carlo results need to be exact after enough repetitions | Monte Carlo output is probabilistically correct; running it more times increases confidence but never provides certainty (unlike Las Vegas). For Boolean decisions: run k times, vote; majority is correct with probability 1 - 2^(-k). |

### 🚨 Failure Modes & Diagnosis

**1. Using weak PRNG in security context**

Symptom: Hash table DoS attack succeeds despite "randomized" hash function; attacker crafts keys that all collide.

Root Cause: Application uses predictable PRNG (seeded with timestamp at startup); attacker replicates seed and predicts hash outputs.

Diagnostic:
```bash
# Test: does the hash map slow dramatically for your key set?
# time java MapBenchmark attack_keys.txt  # should be fast
# time java MapBenchmark normal_keys.txt  # baseline
# If attack_keys >> normal_keys: PRNG is predictable
```

Fix: Use `new SecureRandom()` for security-critical seeds; Java HashMap uses OS entropy since Java 8 for its seed.

Prevention: Use `SecureRandom` for any cryptographic or security-relevant randomness; `ThreadLocalRandom` for performance-only randomness.

---

**2. Underestimating Karger's min-cut repetition requirement**

Symptom: Karger's algorithm returns wrong min-cut (larger than actual minimum); downstream graph partition is suboptimal.

Root Cause: Each trial has only Ω(1/N²) success probability. For N=100, need ~30,000 trials for 99% probability. Too few trials → high failure rate.

Diagnostic:
```java
// Track: how often does running more iterations improve result?
// If cut improves after 10,000 trials: probably need more
System.out.println("Min cut after 1000 trials: " + cut1000);
System.out.println("Min cut after 10000 trials: " + cut10000);
// Should converge; if not, N is too large for Karger's alone
```

Fix: Use Karger-Stein algorithm (O(N² log³ N) total) for better success probability.

Prevention: For N > 50, use Stoer-Wagner deterministic algorithm O(N³) instead.

---

**3. Forgetting to fix random seed for reproducible tests**

Symptom: Test suite passes some runs, fails others; non-deterministic CI failures for randomised algorithm tests.

Root Cause: Algorithm uses `Math.random()` with time-based seed; different runs produce different results, and edge cases trigger bugs only sometimes.

Diagnostic:
```java
// Log the seed used:
long seed = System.currentTimeMillis();
Random rng = new Random(seed);
System.out.println("Test seed: " + seed); // log for reproduction
```

Fix: In tests, fix the seed to a constant; in production, use unpredictable seeding.

Prevention: Parameterise `Random` instance in algorithm; pass seeded `Random` in tests, unseeded in production.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Time Complexity / Big-O` — Expected complexity analysis (E[T(N)]) is essential for Las Vegas algorithms; understanding amortized vs worst-case vs expected is key.
- `Monte Carlo vs Las Vegas Algorithms` — The two primary categories of randomized algorithms; understanding their correctness/speed trade-off is foundational.

**Builds On This (learn these next):**
- `Hashing Techniques` — Universal hashing uses random hash function families for adversarial-resistant O(1) operations; an application of randomized algorithms to data structures.
- `Approximation Algorithms` — Many approximation algorithms use randomisation (random rounding of LP relaxations) to achieve provable guarantees.
- `Bloom Filter` — Probabilistic data structure using multiple random hash functions; a practical Monte Carlo space-time trade-off.

**Alternatives / Comparisons:**
- `Deterministic Algorithms` — Always correct, always bounded; preferred when worst-case guarantees are required and adversarial inputs exist.
- `Greedy Algorithm` — Makes locally optimal choices deterministically; different trade-off: often sub-optimal but always fast and deterministic.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Algorithms using random choices for       │
│              │ expected performance or error resistance   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Deterministic worst cases exploitable by  │
│ SOLVES       │ adversaries; complex symmetry-breaking    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Random choices: adversary can't predict   │
│              │ → no consistent worst-case input exists   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Adversarial input possible; expected       │
│              │ performance matters more than worst case  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Worst-case guarantee required;            │
│              │ security-critical (needs CSPRNG)          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Better expected/ adversarial performance  │
│              │ vs non-determinism, harder debugging      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Unpredictability is a superpower"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Universal Hashing → Bloom Filter → CSPRNG │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Randomized QuickSort achieves expected O(N log N) for ANY fixed input. Now consider an adaptive adversary that can observe the random bits chosen during execution (e.g., through a timing side channel). If the adversary knows the pivot selected at each recursive call, they can now construct a bad input in real-time, sending N elements just as heavy as the current pivot. Does this adaptive adversary break the O(N log N) expected guarantee? What security model does this require, and how does it relate to cryptographically secure pseudorandom number generators vs insecure PRNGs?

**Q2.** HyperLogLog is a Monte Carlo algorithm that estimates the cardinality of a data stream using O(log log N) memory with a relative error of ε = 1.04/√M (M = number of buckets). For a stream of 10 billion unique URLs counted daily by Google Analytics, HyperLogLog uses ~1.5 KB of memory with 1% error. Compare this to an exact count requiring a HashSet (~650 MB for 10B URLs at 8 bytes/hash). This is a 400,000× space savings with 1% error. For what applications is 1% error acceptable, and for what applications would exact count (or error < 0.001%) be required despite the 400,000× memory cost?

