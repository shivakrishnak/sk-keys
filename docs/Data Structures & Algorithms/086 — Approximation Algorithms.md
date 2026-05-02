---
layout: default
title: "Approximation Algorithms"
parent: "Data Structures & Algorithms"
nav_order: 86
permalink: /dsa/approximation-algorithms/
number: "0086"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: NP-Complete Problems, Greedy Algorithm, P vs NP
used_by: TSP Approximation, Scheduling Problems, Network Design
related: Greedy Algorithm, Randomized Algorithms, NP-Complete Problems
tags:
  - algorithm
  - advanced
  - deep-dive
  - performance
  - pattern
---

# 086 — Approximation Algorithms

⚡ TL;DR — Approximation algorithms efficiently find solutions that are provably within a guaranteed factor of optimal for NP-hard problems, making intractable problems tractable in practice.

| #0086 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | NP-Complete Problems, Greedy Algorithm, P vs NP | |
| **Used by:** | TSP Approximation, Scheduling Problems, Network Design | |
| **Related:** | Greedy Algorithm, Randomized Algorithms, NP-Complete Problems | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A delivery company needs to plan routes for 1,000 trucks visiting 50,000 locations. TSP (Travelling Salesman Problem) on 50,000 cities is NP-hard — no polynomial algorithm is known. Exact solution: decades of computation. Alternative: use heuristics (nearest-neighbour greedy) that produce routes, but nobody knows how far from optimal: maybe 2× too long, maybe 10× — no guarantee.

**THE BREAKING POINT:**
Heuristics without provable guarantees are engineering guesswork. A company running 20% suboptimal routes wastes millions of dollars monthly — but without a guarantee, they don't even know how much is being wasted. The lack of a performance guarantee prevents rational resource planning.

**THE INVENTION MOMENT:**
For metric TSP (triangle inequality holds), the Christofides algorithm (1976) always produces a tour within 1.5× the optimal length, in polynomial time — a **3/2-approximation ratio**. For Vertex Cover, a simple greedy gives a 2-approximation. These algorithms are polynomial AND come with a mathematical proof of their worst-case quality. This is exactly why **Approximation Algorithms** were created.

---

### 📘 Textbook Definition

An **approximation algorithm** is a polynomial-time algorithm for an NP-hard optimisation problem that produces a solution S whose value is within a proven factor α of the optimal solution OPT. For minimisation: S ≤ α × OPT. For maximisation: S ≥ (1/α) × OPT. The **approximation ratio** α ≥ 1 characterises quality: α=1 is exact, α=2 is a 2-approximation. A **PTAS** (Polynomial-Time Approximation Scheme) provides a (1+ε)-approximation for any ε > 0 in time O(f(1/ε) × N^c). An **FPTAS** (Fully Polynomial-Time Approximation Scheme) runs in O((N/ε)^c) — polynomial in both N and 1/ε.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Trade optimal for provably-near-optimal: get within a guaranteed ratio of the best possible answer in polynomial time.

**One analogy:**
> Buying groceries on a budget. You can't search every store for the absolute cheapest receipt (NP-hard: combinatorial item-store assignment). But you can use a simple rule: "buy each item at the nearest store, and pay at most 2× the absolute minimum if the triangle inequality holds." You don't get the minimum price, but you have a receipt that's at most 2× what the best shopper would pay — and you're done in minutes, not years.

**One insight:**
The approximation ratio separates approximation algorithms from heuristics: a heuristic might produce a good solution without a bound on how bad it could be. An approximation algorithm comes with a mathematical proof: "On any input, this algorithm's output is at most α× optimal." This proof is what makes approximation algorithms scientifically rigorous and economically plannable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The algorithm is polynomial time — O(N^k) for some constant k.
2. The approximation ratio α is **proven** for all inputs, not just typical ones.
3. Lower bounds (inapproximability): for some NP-hard problems, achieving better than a specific ratio would imply P=NP. This defines the "approximability frontier."

**DERIVED DESIGN:**
**Greedy 2-approximation for Vertex Cover:**
1. While there are uncovered edges: pick any edge (u,v), add BOTH u and v to the cover.
2. This covers every selected edge. Total cover ≤ 2 × optimal.

Proof: Each pair (u,v) selected is in the optimal cover (at least one of u,v). Each pair adds 2 vertices to our solution. Optimal adds at least 1. So our solution ≤ 2 × optimal. Simple. Elegant. Proven.

**Christofides 3/2-approximation for metric TSP:**
1. Compute MST T. Cost(T) ≤ OPT (MST is a lower bound on tour cost in metric spaces).
2. Find minimum-weight perfect matching M on odd-degree vertices of T.
3. Combine T + M to get Eulerian graph. Find Euler tour.
4. Shortcut repeated vertices (valid by triangle inequality).
5. Tour cost ≤ Cost(T) + Cost(M) ≤ OPT + OPT/2 = 3/2 × OPT.

**THE TRADE-OFFS:**
**Gain:** Provable quality bound; polynomial time; plannable resource allocation.
**Cost:** Not optimal — α× OPT with α > 1. For some problems, improving the ratio below a threshold requires P=NP (inapproximability hardness). FPTAS adds space/time overhead proportional to 1/ε.

---

### 🧪 Thought Experiment

**SETUP:**
Vertex Cover: Graph with edges (1,2), (2,3), (3,4), (4,5). Minimum cover requires vertices {2,4} (covers all edges). Find a 2-approximation.

**WHAT HAPPENS WITH BRUTE FORCE:**
2^5 = 32 subsets. Check each for cover. Find {2,4}. Minimum = 2. O(2^N) for general N.

**WHAT HAPPENS WITH GREEDY 2-APPROXIMATION:**
- Pick edge (1,2): add vertices 1 AND 2 to cover. Mark edges (1,2) covered.
- Remaining: (2,3)(3,4)(4,5). Pick edge (3,4): add 3 AND 4. Mark (3,4),(2,3),(4,5) covered.
- All edges covered. Cover = {1, 2, 3, 4}. Size = 4.
- Optimal = 2. Our result = 4 = 2 × optimal. Exactly 2×.

**THE INSIGHT:**
The greedy 2-approximation produced a cover of size 4 (2× the optimal 2). This is the worst case — the ratio is tight. But the algorithm ran in O(E) — milliseconds for 10M edges. The optimal algorithm might take 10^6 years. Paying 2× is a rational trade for polynomial time.

---

### 🧠 Mental Model / Analogy

> Approximation algorithms are "good enough" engineers: when asked for the best design, they don't spend 10 years doing exhaustive search. Instead, they apply a principled heuristic and can guarantee: "This design costs at most 1.5× the minimum possible. That's the proof." The client might want perfection, but they get a mathematically bounded near-perfection in budget time.

- "Best design" → optimal solution OPT
- "Good enough design" → approximation algorithm output SOL
- "Costs at most 1.5×" → approximation ratio α=1.5
- "Principled heuristic" → polynomial algorithm with proven bound
- "Budget time" → polynomial runtime

Where this analogy breaks down: Some approximation ratios are tight (cannot be improved without P=NP). In the analogy, clients might want better designs — in inapproximability theory, "better" is simply unavailable in polynomial time.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Approximation algorithms find answers that are close to the best possible when finding "the best" is too hard. The key difference from guessing: they come with a proof of how close they are. "We found an answer that's at most twice as expensive as the cheapest possible answer — and we can prove this."

**Level 2 — How to use it (junior developer):**
Identify the problem as NP-hard; look up known approximation algorithms (e.g., Set Cover: O(log N) approximation; Vertex Cover: 2-approximation; Metric TSP: 3/2 approximation). Implement the algorithm; the approximation ratio is a mathematical guarantee that requires no empirical validation. Distinguish approximation ratio from "how bad it is in practice" — the ratio is worst case; typical cases are often much better.

**Level 3 — How it works (mid-level engineer):**
Two main proof techniques: (1) **Lower bound comparison:** compute a polynomial-time lower bound LB ≤ OPT, then show algorithm produces solution ≤ α × LB, hence ≤ α × OPT. (2) **Primal-dual LP relaxation:** solve the LP relaxation of the IP; round the fractional solution; show rounding introduces at most α× overhead. Set Cover: greedy achieves O(ln N) approximation ratio; LP-rounding achieves the same ratio and matches the inapproximability lower bound (O(ln N) is optimal unless P=NP).

**Level 4 — Why it was designed this way (senior/staff):**
Inapproximability results define the "approximation frontier." For metric TSP, best known is Christofides (3/2). Recent improvement: Karlin-Klein-Oveis Gharan 2021 achieved (3/2 - 10^-36)-approximation — barely better, but a major theoretical breakthrough. For General TSP (no triangle inequality): inapproximable to any constant ratio unless P=NP (Sahni-Gonzalez reduction). PCP theorem (probabilistically checkable proofs) provides the mathematical foundation for inapproximability: most NP-hard problems have provable lower bounds on approximation ratio that match (or nearly match) what the best polynomial algorithms achieve, creating a full approximation complexity landscape.

---

### ⚙️ How It Works (Mechanism)

**Greedy Vertex Cover (2-approximation):**

```
┌────────────────────────────────────────────────┐
│ Greedy 2-Approx Vertex Cover                   │
│                                                │
│ Graph: (1,2),(2,3),(3,4),(4,5)                 │
│                                                │
│ Pick edge (1,2): add {1,2} to cover            │
│   Covered edges: {(1,2)} — mark removed       │
│                                                │
│ Remaining edge (3,4): add {3,4} to cover       │
│   Covered edges: {(2,3),(3,4),(4,5)} removed  │
│                                                │
│ No uncovered edges → DONE                      │
│ Cover: {1,2,3,4}, size=4                       │
│                                                │
│ Proof: our pairs {(1,2),(3,4)} are in optimal. │
│ Optimal uses ≥1 vertex per pair → OPT ≥ 2.    │
│ Our solution = 4 ≤ 2 × 2 = 2 × OPT. ✓        │
└────────────────────────────────────────────────┘
```

**Christofides 3/2-Approximation for Metric TSP:**

```
┌────────────────────────────────────────────────┐
│ Christofides Algorithm Steps                   │
│                                                │
│ 1. Compute MST T: cost(T) ≤ OPT               │
│ 2. Find odd-degree vertices O in T            │
│    (|O| is always even)                        │
│ 3. Min weight matching M on vertices in O     │
│    cost(M) ≤ OPT/2 (by TSP path argument)    │
│ 4. Combine T + M → Eulerian graph             │
│ 5. Eulerian circuit → shortcut → Hamiltonian  │
│                                                │
│ Total cost ≤ cost(T) + cost(M)                │
│           ≤ OPT + OPT/2 = 3/2 × OPT          │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
NP-hard optimisation problem (TSP, VC, Set Cover)
→ Determine approximability: is there a PTAS/FPTAS?
→ [APPROXIMATION ALGORITHM ← YOU ARE HERE]
  → Apply algorithm (greedy, LP-rounding, etc.)
  → Output: feasible solution with proven ratio α
→ Present: "Our solution costs at most α × OPT"
→ Decision: is 1.5× or 2× acceptable for the use case?
```

**FAILURE PATH:**
```
Approximation ratio too large for problem requirements
→ α=2 Vertex Cover gives cover twice too large for
  bandwidth-constrained network deployment
→ Fix: Use LP relaxation + randomised rounding for
  expected (1 + ε) ratio at higher compute cost
→ Or: exact solver (branch & bound) for small N
→ Diagnostic: measure actual OPT on small instances;
  compare to approximation quality
```

**WHAT CHANGES AT SCALE:**
For large-scale logistics (Amazon routing 1M packages/day), Christofides 3/2-approx TSP is too slow (O(N³) for matching step). Production systems use LKH (Lin-Kernighan-Helsgott): no proven ratio but empirically finds near-optimal (~1.002× OPT) solutions in sub-quadratic time via local search. For deadline-constrained scheduling: simple greedy (earliest deadline first or shortest processing time) gives provable 2× for pre-emption-free scheduling with machine constraints.

---

### 💻 Code Example

**Example 1 — 2-approximation Vertex Cover:**
```java
Set<Integer> vertexCover(int V, List<int[]> edges) {
    Set<Integer> cover = new HashSet<>();
    boolean[] covered = new boolean[edges.size()];
    for (int i = 0; i < edges.size(); i++) {
        if (covered[i]) continue;
        int u = edges.get(i)[0], v = edges.get(i)[1];
        cover.add(u); cover.add(v); // add BOTH endpoints
        // Mark all edges incident to u or v as covered
        for (int j = i; j < edges.size(); j++) {
            int a = edges.get(j)[0], b = edges.get(j)[1];
            if (a==u || a==v || b==u || b==v)
                covered[j] = true;
        }
    }
    return cover; // |cover| ≤ 2 × OPT (proven)
}
```

**Example 2 — Greedy Set Cover (O(log N) approximation):**
```java
List<Integer> greedySetCover(int universe,
    List<Set<Integer>> sets) {
    Set<Integer> uncovered = new HashSet<>();
    for (int i = 0; i < universe; i++) uncovered.add(i);
    List<Integer> chosen = new ArrayList<>();
    while (!uncovered.isEmpty()) {
        // Pick set covering maximum uncovered elements
        int best = -1, bestCount = 0;
        for (int i = 0; i < sets.size(); i++) {
            long count = sets.get(i).stream()
                .filter(uncovered::contains).count();
            if (count > bestCount) {
                bestCount = (int) count; best = i;
            }
        }
        chosen.add(best);
        uncovered.removeAll(sets.get(best));
    }
    return chosen;
    // |chosen| ≤ OPT × H(max_set_size) ≤ OPT × ln(N)+1
}
```

**Example 3 — FPTAS for 0/1 Knapsack ((1+ε)-approx):**
```java
int fptas(int[] w, int[] v, int W, double eps) {
    int n = w.length;
    int vMax = Arrays.stream(v).max().getAsInt();
    // Scale values down by K: trade accuracy for smaller W
    double K = eps * vMax / n;
    int[] vScaled = new int[n];
    for (int i = 0; i < n; i++)
        vScaled[i] = (int)(v[i] / K); // floor scaling
    // Run exact DP on scaled values (much smaller table)
    int scaledTotal = Arrays.stream(vScaled).sum();
    // dp[i] = min weight to achieve exactly value i
    int[] dp = new int[scaledTotal + 1];
    Arrays.fill(dp, Integer.MAX_VALUE); dp[0] = 0;
    for (int i = 0; i < n; i++)
        for (int j = scaledTotal; j >= vScaled[i]; j--)
            if (dp[j - vScaled[i]] != Integer.MAX_VALUE)
                dp[j] = Math.min(dp[j],
                    dp[j - vScaled[i]] + w[i]);
    // Find maximum scaled value with weight ≤ W
    for (int j = scaledTotal; j >= 0; j--)
        if (dp[j] <= W) return j; // actual value ≥ j × K
    return 0;
    // Returns (1-ε)-optimal value, runs in O(N²/ε)
}
```

---

### ⚖️ Comparison Table

| Problem | Best Approx Ratio | Algorithm | Inapprox. Lower Bound |
|---|---|---|---|
| **Metric TSP** | 3/2 | Christofides (1976) | 123/122 (TSP PCP) |
| Vertex Cover | 2 | Greedy | 1.36 (assuming UGC) |
| Set Cover | O(ln N) | Greedy | Ω(ln N) (P≠NP) |
| 0/1 Knapsack | (1+ε) | FPTAS | — (FPTAS exists) |
| General TSP | Inapprox. | — | Any constant |
| Independent Set | O(N^ε) | SDP-based | N^(1-ε) (P≠NP) |

How to choose: FPTAS when problem has pseudo-polynomial DP (Knapsack). PTAS when geometric structure available (Euclidean TSP). Constant-ratio approximation for well-studied problems (Christofides). Logarithmic for Set Cover. Inapproximable beyond constant: design heuristics.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A good heuristic is an approximation algorithm | Only algorithms with a proven worst-case ratio qualify. Nearest-neighbour TSP has no proven constant ratio (counterexamples exist with arbitrarily bad ratios). |
| Approximation algorithms are for when you don't care about quality | Quite the opposite: the ratio is the WORST CASE guarantee. In practice, approximation algorithms often achieve near-optimal results. The ratio is a mathematical floor on quality. |
| PTAS is always better than a constant-ratio approximation | PTAS grows with 1/ε. For Euclidean TSP, a PTAS with ε=0.01 may take longer than Christofides 3/2 on large instances, despite theoretically better ratio. |
| Inapproximability means worst-case is hard, average is easy | Inapproximability applies to worst-case inputs. For many NP-hard problems, average-case instances are easy to solve to near-optimality with local search. |

---

### 🚨 Failure Modes & Diagnosis

**1. Applying constant-ratio algorithm to problem without triangle inequality**

**Symptom:** Christofides applied to general non-metric TSP produces tours far worse than 3/2× optimal — no ratio guarantee holds.

**Root Cause:** Christofides relies on triangle inequality: shortcutting vertices only decreases or maintains tour cost. In general TSP, shortcuts may increase cost arbitrarily.

**Diagnostic:**
```
Verify metric space: for all cities a,b,c:
  dist(a,c) ≤ dist(a,b) + dist(b,c)
If any violation: cannot use Christofides
```

**Fix:** For non-metric TSP, use LKH-3 local search heuristic (no ratio guarantee, empirically very good).

**Prevention:** Check triangle inequality before applying metric-TSP algorithms.

---

**2. FPTAS too slow for large ε^-1**

**Symptom:** FPTAS with ε=0.001 (0.1% error) on Knapsack with N=1000 items runs for hours.

**Root Cause:** FPTAS time O(N²/ε). For N=1000, ε=0.001: 10^6 / 0.001 = 10^9 operations.

**Diagnostic:**
```java
long estimatedOps = (long)(n * n) / eps;
// n=1000, eps=0.001 → 10^9 ops → ~1 second or minutes
System.out.println("Estimated ops: " + estimatedOps);
```

**Fix:** Use ε=0.01 (1% error, 100× faster) or branch-and-bound for near-optimal with pruning.

**Prevention:** Profile FPTAS time for target ε and N before committing to the approach.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `NP-Complete Problems` — Approximation algorithms are designed for NP-hard problems; understanding why exact polynomial algorithms are unlikely explains why approximation is necessary.
- `Greedy Algorithm` — Many approximation algorithms are greedy with a proven worst-case ratio; Set Cover, Vertex Cover, Scheduling.
- `P vs NP` — Inapproximability bounds are conditioned on P≠NP; understanding this connects approximation to the fundamental hardness question.

**Builds On This (learn these next):**
- `TSP Approximation (Christofides)` — The flagship 3/2-approximation for metric TSP.
- `LP Relaxation and Rounding` — Powerful technique: solve LP, round fractional solution to integer with controlled overhead.

**Alternatives / Comparisons:**
- `Heuristics (e.g. LKH, Simulated Annealing)` — No ratio guarantee but often better in practice; unknown worst-case quality.
- `Exact Solvers (Branch & Bound, ILP)` — Optimal but exponential worst case; practical for moderate N.
- `Parameterised Algorithms (FPT)` — Polynomial for fixed parameter k; exponential in k but polynomial in N.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Polynomial-time algorithms with proven    │
│              │ worst-case ratio to optimal for NP-hard  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ NP-hard: no poly exact algorithm;         │
│ SOLVES       │ heuristics: no quality guarantee         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ α-approximation: provably within α× OPT  │
│              │ for ALL inputs, not just typical ones     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ NP-hard problem; polynomial exact unfeasible;│
│              │ provable quality bound needed              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Exact solution required (use branch&bound);│
│              │ ratio too large for application tolerance  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Poly time + proven bound vs optimality;   │
│              │ ratio often matches inapproximability limit│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Provably good enough, always, fast"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Christofides → LP Rounding → PCP Theorem  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The greedy Set Cover algorithm achieves O(ln N) approximation ratio, and this is tight — no polynomial algorithm can do better (unless P=NP, by PCP theorem). Yet for special instances of Set Cover (e.g., when all sets have size ≤ 3: "3-Dimensional Matching"), constant-ratio approximations exist. Explain the structural property of these restricted instances that allows better approximation, and show how the Unique Games Conjecture (if true) would make even the 2-approximation for Vertex Cover optimal — despite VC being a special case of Set Cover.

**Q2.** Christofides algorithm achieves 3/2 for metric TSP and was the best known for 47 years. In 2021, a 3/2 - 10^-36 approximation was published (Karlin-Klein-Oveis Gharan). The improvement is cosmetically tiny but requires entirely new mathematics (strongly Rayleigh measures on spanning trees). Why does the field care about an improvement of ε = 10^-36? What does it demonstrate about the Christofides bound, and what does the new proof technique suggest about whether the true approximation frontier might be close to 1 (optimal) or close to 3/2 (Christofides)?

