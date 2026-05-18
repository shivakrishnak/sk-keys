---
id: DSA-070
title: Amortized Analysis
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-023
used_by: DSA-077
related: DSA-023, DSA-012, DSA-004
tags:
  - algorithms
  - amortized-analysis
  - big-o
  - aggregate-method
  - accounting-method
  - potential-method
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/dsa/amortized-analysis/
---

## TL;DR

Amortized analysis computes the average cost per operation
over a sequence of operations - revealing that O(n) array
resizes cost O(1) amortized, making ArrayList append truly
O(1) despite occasional expensive resizes.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-070 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, amortized-analysis, O(1) amortized |
| **Prerequisites** | DSA-023 |

---

### The Problem This Solves

ArrayList.add() copies all elements when resizing - that's
O(n) for that single call. Yet we say ArrayList.add() is
O(1) amortized. How? Amortized analysis proves that even
though some operations are expensive, the average cost
over all operations is constant. Without amortized
analysis, we'd dramatically overestimate ArrayList's
practical cost.

---

### Textbook Definition

Amortized analysis determines the average time per operation
over a worst-case sequence of operations. Three methods:
1. Aggregate method: sum total cost of n operations,
   divide by n
2. Accounting method (banker's method): assign amortized
   cost per operation; excess paid to a "bank" for future
3. Potential method: define a potential function phi that
   measures "stored work"; amortized_cost = actual + delta_phi

All three give the same final answer; choose the one most
natural for the problem.

---

### How It Works

**ArrayList resize - aggregate method:**

```
Start with capacity 1. Double when full.
Operations: add(1), add(2), add(3), add(4), add(5)...

Copies during resizes:
  capacity 1→2: copy 1 element
  capacity 2→4: copy 2 elements
  capacity 4→8: copy 4 elements
  capacity 8→16: copy 8 elements
  ...
  
Total copies for n insertions:
  1 + 2 + 4 + 8 + ... + n/2 = n - 1 < n

Total work for n insertions: n (each add) + (n-1) (copies)
                            = 2n - 1 = O(n)
Average cost per add = O(n) / n = O(1)
→ ArrayList.add() is O(1) amortized.
```

**Why BAD: using O(n) per add as the cost:**

```java
// BAD reasoning: ArrayList add is O(n) → n operations cost O(n^2)
for (int i = 0; i < n; i++) {
    list.add(element); // NOT O(n^2) total, it's O(n) total!
}
// This is a common overestimate. Correct: O(n) total.

// GOOD reasoning: use amortized analysis
// Total cost = O(n). Average per add = O(1) amortized.
```

**Stack push/pop - accounting method:**

```
Multi-pop: pop k elements in one call (expensive single op).
Amortized analysis:
- Each push: assign cost 2 (1 for push, 1 saved for future pop)
- Each pop: use the 1 credit saved from push (actual cost 1)
- No operation costs more than its amortized cost
Total amortized cost for n push/pop operations = O(n)
Each operation: O(1) amortized
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Amortized O(1) means every operation is O(1)" | Some operations are O(n); amortized O(1) means the AVERAGE over all operations is O(1) |
| "Amortized analysis is the same as average case" | Average case considers random inputs. Amortized is worst-case total divided by n - works for any input sequence |

---

### Failure Modes & Diagnosis

**Failure: Performance regression with ArrayList when
wrapping in synchronized block per operation**
- Cause: If each add is called under a different lock/release,
  the amortized benefit disappears because each synchronized
  block may see a resize as an outlier latency spike
- Fix: Use bulk operations (addAll) or preallocate with
  ArrayList(expectedSize) to avoid resizes entirely

---

### Quick Reference Card

| Data Structure | Operation | Amortized Cost | Worst Single |
|---------------|-----------|---------------|-------------|
| ArrayList | add | O(1) | O(n) |
| Stack | push/pop/multipop | O(1) | O(n) |
| Union-Find | find/union | O(alpha(n)) | O(log n) |
| HashMap | put | O(1) | O(n) |

---

### The Surprising Truth

Java's HashMap resize is amortized O(1) for put, but the
SINGLE resize operation that triggers re-hashing all entries
is O(n). In latency-sensitive systems (trading platforms,
game engines), this O(n) spike at unexpected times causes
GC-like pauses. The fix: HashMap(initialCapacity, loadFactor)
to pre-size appropriately. LinkedIn discovered this caused
millisecond latency spikes in their feed ranking system -
they now pre-size all hot-path HashMaps.

---

### Mastery Checklist

- [ ] Can prove ArrayList.add() is O(1) amortized via
      aggregate method
- [ ] Understands the difference between amortized vs
      average-case analysis
- [ ] Knows practical implication: preallocate collections

---

### Interview Deep-Dive

**Q1 (Hard):** A stack supports push, pop, and multi-pop(k)
which pops min(k, size) elements. What is the amortized
cost per operation?

> Aggregate method: in n operations, each element can be
> pushed at most once and popped at most once. Total cost
> of all push operations: at most n. Total cost of all
> pop/multi-pop operations: at most n (can't pop more
> than were pushed). Total: 2n = O(n) for n operations.
> Amortized cost per operation = O(n)/n = O(1).
> Accounting method: charge 2 for each push (1 to push,
> 1 saved). Each pop uses the saved credit. Multi-pop(k)
> uses k credits from previous pushes. Amortized: O(1).
