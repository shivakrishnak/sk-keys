---
layout: default
title: "Amortized Analysis"
parent: "Data Structures & Algorithms"
nav_order: 50
permalink: /dsa/amortized-analysis/
number: "0050"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Time Complexity / Big-O, Space Complexity
used_by: ArrayList, HashMap, Stack, Dynamic Array
related: Time Complexity / Big-O, Potential Method, Aggregate Analysis
tags:
  - algorithm
  - advanced
  - deep-dive
  - mental-model
---

# 050 — Amortized Analysis

⚡ TL;DR — Amortized analysis proves that a sequence of operations is cheap on average even when individual operations can be expensive, by spreading the cost of rare expensive operations across many cheap ones.

| #050 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Time Complexity / Big-O, Space Complexity | |
| **Used by:** | ArrayList, HashMap, Stack, Dynamic Array | |
| **Related:** | Time Complexity / Big-O, Potential Method, Aggregate Analysis | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are told that `ArrayList.add()` can take O(N) time (when the internal array resizes). Without amortized analysis, you might conclude that adding N elements takes O(N²) total time. You avoid `ArrayList` in performance-critical code and implement a complex linked structure instead — sacrificing cache performance for an imaginary guarantee.

**THE BREAKING POINT:**
Worst-case analysis applied naively to every operation overstates total cost for data structures with occasional expensive operations. A data structure where 99.9% of operations are O(1) and 0.1% are O(N) is NOT O(N) per operation on average — it's O(1) amortized. Without the right analysis tool, you cannot prove this.

**THE INVENTION MOMENT:**
Analyse a *sequence* of N operations, not each operation in isolation. If the total cost of N operations is O(N×f(N)), then the amortized cost per operation is O(f(N)) — regardless of how individual costs fluctuate. "Rare expensive operations pay for themselves by enabling many cheap ones." This is exactly why Amortized Analysis was created.

---

### 📘 Textbook Definition

**Amortized analysis** is a method for determining the average cost of a single operation in the *worst case* over a sequence of operations. Unlike average-case analysis (which assumes probability distributions), amortized analysis is a worst-case guarantee on the average: no matter what sequence of N operations is performed, the total cost is bounded by N × amortized_cost. Three methods: **aggregate analysis** (total cost / N), **accounting method** (each operation charged a virtual cost covering future expensive ops), and **potential method** (define a potential function Φ that tracks "stored energy" in the data structure).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spread the cost of rare expensive operations across the many cheap ones they enable.

**One analogy:**
> A bus that makes 10 local stops before an express run covers 100 km. Each local stop takes 1 minute; the express run takes 10 minutes for everyone to reach their destination faster. Average per stop: (10 × 1 + 10) / 10 = 2 minutes. Neither "worst case = 10 minutes" nor "best case = 1 minute" accurately captures the per-stop cost.

**One insight:**
Amortized analysis is NOT average-case analysis. It does not assume random or typical inputs. It is a *worst-case guarantee on the total cost over any sequence of N operations*. The guarantee holds even on adversarial inputs — the data structure "saves up credit" from cheap ops to pay for expensive ones.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Total cost of N operations = sum of individual operation costs; amortized cost = total / N.
2. Amortized cost is a guaranteed bound on the per-operation average — not a hope or a typical case.
3. The "credit" argument: if cheap ops pay k extra units into a "bank," and expensive ops cost at most k times the typical cheap op, the bank always covers the expensive ops.

**DERIVED DESIGN:**
**Aggregate analysis** — the simplest method:
Total cost of all N operations. Divide by N. Example: dynamic array with doubling.

**ArrayList.add() amortized analysis:**
- At capacity 1, 2, 4, 8, 16, ..., 2^k: resize costs 1, 2, 4, 8, ..., 2^k.
- Total resize cost for N additions: 1 + 2 + 4 + ... + N ≈ 2N (geometric series).
- Plus N non-resize operations at O(1) each: N.
- Total: 3N. Average: 3 = O(1) amortized.

**Accounting method** — charge more than actual cost, bank the surplus:
Each `add` is charged 3 units: 1 for the write, 1 credit "saved" for future copy, 1 credit for copying a previously written element. On resize, credits from cheap ops pay for copying all previous elements. No debt ever accumulated.

**Potential method** — define Φ = 2 × (size − capacity/2) for dynamic array:
On non-resize adds: actual cost 1, Φ increases by 2, amortized cost = 1 + 2 = 3 = O(1).
On resize (size = capacity): actual cost N+1, Φ decreases by N+2 (capacity doubles, Φ drops from N to -(N+2) → delta = -(N+2)), amortized = (N+1) - (N+2) = -1 ≤ 3 = O(1).

**THE TRADE-OFFS:**
**Gain:** True per-operation cost guarantees, enables O(1) amortized structures.
**Cost:** Analysis is more complex; worst-case single operation may still be O(N) — latency sensitive code must account for this.

---

### 🧪 Thought Experiment

**SETUP:**
Push N=8 elements onto a dynamic array starting with capacity 1.

Sequence of push operations (capacity, cost):
```
push(1): cap=1, cost=1 (no resize)
push(2): cap=2, write 1st elem to new array (cost=2: 1 copy+1 write)
push(3): resize to 4 (cost=3: 2 copies+1 write), cap=4
push(4): cap=4, cost=1
push(5): resize to 8 (cost=5: 4 copies+1 write), cap=8
push(6): cap=8, cost=1
push(7): cap=8, cost=1
push(8): cap=8, cost=1
```

Total cost: 1+2+3+1+5+1+1+1 = 15.
Average per push: 15/8 ≈ 1.875 = O(1).
Worst single push: 5 = O(N). But amortized: O(1).

**THE INSIGHT:**
The O(N) resize is affordable because it doubles capacity, enabling N/2 O(1) subsequent pushes that "repay" the resize cost. You never resize twice in a row — after each O(N) event, the next N/2 operations are free (relative to resize cost), making the average constant.

---

### 🧠 Mental Model / Analogy

> Amortized analysis is like a gym with an annual membership. Most months you pay $0 per visit because the monthly fee averages your visits. The one month you sign up (O(N) "cost" of setup) is balanced by 11 months of cheap workouts. Average cost per visit is low even though the first month was expensive.

- "Monthly fee spread over visits" → amortized cost per operation
- "Annual membership sign-up" → expensive resize operation
- "Cheap monthly workouts" → O(1) pushes between resizes
- "Average cost per visit" → amortized O(1) per add

Where this analogy breaks down: Gym membership has fixed cost; dynamic array resize cost is proportional to N. The key is that resize happens less often as N grows (only at powers of 2), not at a fixed schedule.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Sometimes doing one thing requires a big upfront cost, but then the next 100 things are cheap. Amortized analysis calculates the "price per thing" averaged over many operations.

**Level 2 — How to use it (junior developer):**
Trust `ArrayList.add()`, `HashMap.put()`, and `Stack.push()` as O(1) amortized — don't avoid them due to fear of the rare O(N) resize. Understand the cost is spread out, not eliminated. In real-time systems (game engines, finance), care about worst-case per-operation latency; in throughput-oriented systems, amortized is the right metric.

**Level 3 — How it works (mid-level engineer):**
Aggregate analysis: total work / N. For push on doubly-growing array: total work = sum of geometric series = O(N), so amortized O(1) per push. For `multipop(k)` on stack: each element can be pushed/popped only once — total push+pop work ≤ 2N for N elements → O(1) amortized per operation. Accounting method: assign 2 credits per push (1 for push cost, 1 banked for future pop); pop consumes 1 banked credit; any pop of k items costs k ≤ total banked credits.

**Level 4 — Why it was designed this way (senior/staff):**
The potential method is the most powerful: Φ(state) maps the data structure state to a "stored energy" value. Amortized cost = actual cost + ΔΦ. This allows proving O(1) amortized for complex structures like splay trees, Fibonacci heaps (amortized O(1) insert and O(log N) extract-min), and skewed heaps. Splay trees achieve O(log N) amortized access using a "working set" argument: recently accessed nodes are moved to root, reducing access cost for temporally-local workloads. The "cash flow" framing of amortized analysis is formally equivalent to Lyapunov function analysis in control systems theory — a cross-domain connection rarely made explicit but illuminating.

---

### ⚙️ How It Works (Mechanism)

**Aggregate analysis for multipop stack:**
```
Operations: N total (push and multipop mixed in any order)

Key observation: each element can be pushed at most once
and popped at most once → total push+pop work ≤ 2N

Even if one multipop(all) costs O(N):
Total work for N operations ≤ 2N → amortized O(1) each
```

**Accounting method for dynamic array:**
```
Charge each push: 3 "tokens" (virtual units)
  - 1 token: pay actual push cost
  - 2 tokens: deposit into bank

On resize (doubling): each element being copied
already has 1 token in bank → copies paid for

Bank balance never goes negative → proof complete
Each push's amortized cost = 3 tokens = O(1)
```

**Potential method for dynamic array:**
```
Φ = 2 × size − capacity  (tracks "pressure")

Initial: Φ = 2×0 − 1 = -1 (empty array, cap=1)

Non-resize push:
  actual cost = 1
  ΔΦ = Φ(size+1) - Φ(size) = 2
  amortized = actual + ΔΦ = 1 + 2 = 3 = O(1)

Resize (size = cap = N):
  actual cost = N+1 (N copies + 1 new write)
  before: Φ = 2N − N = N
  after:  Φ = 2(N+1) − 2N = 2
  ΔΦ = 2 - N = -(N-2)
  amortized = (N+1) + (-(N-2)) = 3 = O(1)

In both cases: amortized cost ≤ 3 = O(1)
```

┌──────────────────────────────────────────────┐
│  Dynamic Array: actual vs amortized cost     │
│                                              │
│  Op: 1  2  3  4  5  6  7  8                 │
│  Actual: 1  2  3  1  5  1  1  1 (total=15)  │
│  Amort:  3  3  3  3  3  3  3  3 (total=24)  │
│          ↑ amortized charge ≥ actual         │
│          surplus banked; covers future resize│
└──────────────────────────────────────────────┘

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Sequence of N operations issued
→ Each op: actual cost varies (O(1) or rare O(N))
→ Total cost tracked: T(N)
→ [AMORTIZED ANALYSIS ← YOU ARE HERE]
→ Amortized cost per op = T(N) / N = O(1) proven
→ Structure declared "O(1) amortized" in documentation
```

**FAILURE PATH:**
```
Real-time system requires guaranteed O(1) per operation
→ Amortized O(1) ≠ worst-case O(1)
→ Rare O(N) resize causes latency spike at unlucky moment
→ Fix: constant-size-per-step reallocation (e.g., gap buffers,
        1 element per op copied during "background" phase)
```

**WHAT CHANGES AT SCALE:**
For most server applications, O(1) amortized is sufficient — occasional O(N) operations are invisible in average throughput metrics. For latency-sensitive systems (realtime trading, games, HFT), worst-case latency matters; use structures where worst-case per-operation is guaranteed (not amortized). For distributed systems, amortized analysis applies to batched operations — a distributed hash table doesn't rehash every insertion but periodically, and the cost is amortized across all prior insertions.

---

### 💻 Code Example

**Example 1 — Demonstrating ArrayList doubling:**
```java
// Observe ArrayList resizing behaviour
List<Integer> list = new ArrayList<>(1);
long totalOps = 0;
int prevCapacity = 1;

for (int i = 0; i < 32; i++) {
    list.add(i);
    // capacity accessible via reflection in real code
    // resizes happen at: 1,2,4,8,16,32...
}
// Total adds: 32, total copy work: ~32 (2×16 last resize)
// Amortized: O(1) per add despite one O(N) resize
```

**Example 2 — When amortized O(1) is NOT enough (real-time):**
```java
// BAD for real-time: occasional O(N) resize spike
List<Integer> realTimeBuffer = new ArrayList<>();
while (streaming) {
    realTimeBuffer.add(sensorReading()); // risk: O(N) at resize
}

// GOOD: pre-size to avoid resize
int MAX_READINGS = 100_000;
List<Integer> realTimeBuffer =
    new ArrayList<>(MAX_READINGS); // no resize will occur
while (streaming && realTimeBuffer.size() < MAX_READINGS) {
    realTimeBuffer.add(sensorReading()); // always O(1)
}
```

**Example 3 — Stack with multipop (O(1) amortized):**
```java
Deque<Integer> stack = new ArrayDeque<>();
int totalOps = 0;

// Push N=1000 elements
for (int i = 0; i < 1000; i++) {
    stack.push(i);
    totalOps++; // O(1) each
}

// One multipop of all 1000 — looks O(N)!
while (!stack.isEmpty()) {
    stack.pop();
    totalOps++; // O(1) each pop
}
// Total: 2000 ops for 2000 operations = O(1) amortized
```

---

### ⚖️ Comparison Table

| Analysis Type | What It Measures | Use When |
|---|---|---|
| **Amortized** | Worst case average over any N-op sequence | Structures with rare expensive ops |
| Worst Case | Single operation worst case | Real-time systems requiring latency guarantees |
| Average Case | Expected cost assuming random input | Randomised algorithms (quicksort avg) |
| Best Case | Single operation best case | Rarely useful; too optimistic |

How to choose: For throughput-oriented systems, amortized analysis gives the right metric. For latency-sensitive systems (real-time, HFT), use worst-case despite higher complexity. Average-case analysis is for randomised algorithms.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Amortized = average case | Amortized analysis gives a worst-case guarantee on the average; average-case analysis assumes random inputs |
| Amortized O(1) means every operation is O(1) | Amortized O(1) means N operations total O(N); some individual operations can be O(N) |
| ArrayList is O(N) per add because of resizing | Single worst-case add is O(N); amortized add is O(1) — N adds total O(N) work |
| Doubling strategy is arbitrary | Doubling is optimal: any smaller factor (e.g., +1) gives O(N²) total; any larger factor wastes memory; 2× minimises total cost |

---

### 🚨 Failure Modes & Diagnosis

**1. Latency spike from ArrayList resize in real-time path**

**Symptom:** P99 latency spikes periodically (milliseconds instead of microseconds); GC profiler shows no unusual activity.

**Root Cause:** `ArrayList` resize triggered at an inopportune moment, copying O(N) elements synchronously on the calling thread.

**Diagnostic:**
```bash
# Use Java flight recorder to find allocation in hot path
jcmd <pid> JFR.start duration=60s filename=app.jfr
# Look for ArrayList.grow() in the recording
```

**Fix:** Pre-size the `ArrayList` to expected capacity: `new ArrayList<>(expectedSize)`.

**Prevention:** For real-time paths, profile with JFR or async-profiler; ensure no data structure resize occurs in the critical path.

---

**2. Using amortized analysis as justification for ignoring GC**

**Symptom:** Service has good average throughput but occasional "pause storms" causing client timeouts.

**Root Cause:** High allocation rate (from amortized-O(1) structures creating many short-lived objects) triggers GC, which pauses all threads for O(N) time where N is heap size.

**Diagnostic:**
```bash
java -Xlog:gc* MyApp | grep "Pause Full"
# Full GC pauses should be < 0.5% of runtime
```

**Fix:** Use off-heap structures, primitive collections, or reduce allocation rate. Consider ZGC or Shenandoah for sub-ms pauses.

**Prevention:** Amortized O(1) analysis applies to the algorithm; JVM GC operates at the memory management layer above. Both layers must be analysed.

---

**3. Stack capacity initialisation causing resize in batch processing**

**Symptom:** Batch job processes 10M records but is 3× slower than expected.

**Root Cause:** Default-capacity `ArrayDeque` (capacity 16) resizes dozens of times as 10M elements are pushed.

**Diagnostic:**
```bash
# Add resize counter temporarily:
# Or use -verbose:gc to see allocation pressure
```

**Fix:** `new ArrayDeque<>(10_000_000)` pre-sized to expected usage.

**Prevention:** Whenever you know the maximum size of a collection upfront, always pass it at construction time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Time Complexity / Big-O` — amortized analysis uses the same notation and framework.
- `Space Complexity` — potential functions in amortized analysis often relate to stored state.

**Builds On This (learn these next):**
- `Space-Time Trade-off` — dynamic arrays trade occasional O(N) time for O(1) access.

**Alternatives / Comparisons:**
- `Worst-Case Analysis` — guarantees per-operation cost; required for real-time systems.
- `Average-Case Analysis` — different tool for randomised algorithms; assumes input distributions.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Worst-case guarantee on per-operation     │
│              │ average over N operations                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Naive worst-case analysis overstates cost │
│ SOLVES       │ for data structures with rare bulk ops    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rare expensive operations "pay for" many  │
│              │ cheap ones — credit stored in data struct │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Analysing ArrayList, HashMap resize,      │
│              │ splay trees, Fibonacci heaps, stacks      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Real-time/latency-sensitive systems need  │
│              │ worst-case per-operation guarantees       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correct throughput guarantee vs allows    │
│              │ individual O(N) spikes                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "N cheap ops pay for 1 expensive op —     │
│              │  fair average, occasional spike"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Space-Time Trade-off → Memoization        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `ArrayList` uses a growth factor of 1.5× (not 2×) starting from Java 6 in some implementations, while Python's list uses ~1.125× in some versions. The choice of growth factor directly affects the amortized cost constant. Derive the total copy work for N insertions with growth factor r (r > 1): what is the sum of the geometric series, and what does this imply about the relationship between the growth factor and the amortized constant? At r=1.0001, what is the amortized cost per insertion?

**Q2.** A splay tree performs each access in amortized O(log N) time — individual operations can be O(N) (e.g., accessing the minimum repeatedly). However, a sequence of M operations on a splay tree costs O((N + M) log N) total, where N is the number of nodes. This is the "working set" property. Explain how the potential method would be applied to prove this: what would the potential function Φ represent in terms of the tree structure, and how does the self-adjusting property of splaying create the credit that funds future expensive operations?

