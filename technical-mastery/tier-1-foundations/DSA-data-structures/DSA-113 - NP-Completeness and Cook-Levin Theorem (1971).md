---
id: DSA-113
title: NP-Completeness and Cook-Levin Theorem (1971)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-068, DSA-111
used_by: DSA-122
related: DSA-111, DSA-117
tags:
  - theory
  - np-completeness
  - cook-levin
  - p-vs-np
  - computational-complexity
  - foundations
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 113
permalink: /technical-mastery/dsa/np-completeness/
---

## TL;DR

Cook and Levin proved SAT is NP-Complete (1971): if
any NP-Complete problem has a polynomial-time solution,
ALL NP problems do (P=NP). No NP-Complete problem has
a known polynomial algorithm - explaining why scheduling,
routing, and packing problems are "hard in practice."

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-113 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | NP-completeness, P vs NP, computational complexity |
| **Prerequisites** | DSA-068, DSA-111 |

---

### P vs NP - The Definition

```
P (Polynomial time):
  Problems solvable in O(n^k) time for some k.
  Examples: sorting O(n log n), shortest path O(V+E log V)

NP (Non-deterministic Polynomial):
  Problems where a proposed solution can be VERIFIED
  in polynomial time.
  Example: "Is this a valid Hamiltonian path?" - O(n) to verify
  But finding the path: unknown if polynomial exists

NP-Complete:
  A problem X is NP-Complete if:
  1. X is in NP (solutions verifiable in poly time)
  2. Every NP problem reduces to X in poly time
     (X is NP-hard: as hard as anything in NP)

P = NP question: millennium prize problem ($1M).
  If P = NP: all NP problems (SAT, scheduling, protein
    folding, graph coloring) become efficiently solvable.
  If P ≠ NP (expected): NP-Complete problems have no
    efficient algorithm (exponential lower bound).
```

---

### NP-Complete Problems in Practice

```
Scheduling problems:
  Job-shop scheduling (N jobs, M machines): NP-Complete
  Practical solution: heuristics (genetic algorithms,
    simulated annealing), approximation algorithms

Graph problems:
  Traveling Salesman Problem (TSP): NP-Complete
  Practical solution: Christofides algorithm (1.5x optimal),
    dynamic programming for small n (O(2^n * n^2))

Network optimization:
  Maximum flow: P (O(VE^2) with Edmonds-Karp)
  Minimum vertex cover: NP-Complete
  Minimum edge cover: P

Constraint satisfaction:
  Boolean SAT (3-SAT): NP-Complete (Cook 1971)
  2-SAT: P (O(n+m) via Kosaraju's SCC algorithm)
  Horn-SAT: P (O(n+m))

Packing problems:
  Bin packing: NP-Complete (logistics optimization)
  Knapsack problem: NP-Complete (pseudo-polynomial O(nW))

The engineering takeaway:
  If your problem is NP-Complete:
    Use approximation algorithms (bounded suboptimality)
    Use heuristics (genetic algorithm, simulated annealing)
    Use dynamic programming for small inputs (exact)
    Use special-case structure (e.g., planar graphs often tractable)
    DO NOT wait for a polynomial algorithm
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "NP means exponential time" | NP means "verifiable in polynomial time." It's unknown whether NP problems require exponential time to SOLVE. If P=NP, they don't |
| "NP-Complete problems can't be solved efficiently in practice" | For specific input distributions and sizes, heuristics and approximation algorithms work excellently. TSP routes for 100-city logistics problems are solved to near-optimality in seconds |

---

### Mastery Checklist

- [ ] Can explain P, NP, and NP-Complete in one paragraph each
- [ ] Recognizes NP-Complete patterns when designing algorithms
- [ ] Knows which algorithms to apply when a problem is NP-Complete

---

### The Surprising Truth

Quantum computers (if fault-tolerant) solve only BQP
problems efficiently - a class that MIGHT intersect with
NP but is not believed to contain all of NP. Shor's
algorithm (quantum factoring) is in BQP but may not
be in P. NP-Complete problems are believed to not be
efficiently solvable by quantum computers either.
"Quantum supremacy" headlines are often misleading:
quantum computers offer speedups for specific problems
(optimization, simulation) but are not expected to
solve NP-Complete problems in polynomial time.
