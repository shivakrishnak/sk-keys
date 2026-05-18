---
id: ATZ-039
title: "Policy Evaluation Algorithms and Performance"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-026, ATZ-029, ATZ-036, ATZ-037
used_by: ATZ-046, ATZ-050, ATZ-059
related: ATZ-032, ATZ-037, ATZ-046
tags:
  - security
  - authorization
  - policy-evaluation
  - performance
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/authorization/policy-evaluation-algorithms-and-performance/
---

⚡ **TL;DR** - Authorization policy evaluation must be fast - it sits
in the critical path of every request. OPA evaluates Rego policies
in microseconds (compiled to an AST). SpiceDB and OpenFGA do graph
traversal (BFS/DFS) which is O(nodes + edges) per query. XACML
(XML-based) is notoriously slow due to XML parsing overhead.
The performance levers are: evaluation complexity (how many
conditions, how deep the graph), caching (reduce re-evaluation
of stable decisions), and data locality (avoid network calls
during evaluation).

---

### 📊 Entry Metadata

| #039 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-029 Rego, ATZ-036 ReBAC, ATZ-037 Zanzibar | |
| **Used by:** | ATZ-046, ATZ-050, ATZ-059 | |
| **Related:** | ATZ-032 Caching, ATZ-037 Zanzibar, ATZ-046 Perf at Scale | |

---

### 📘 Textbook Definition

Policy evaluation performance is determined by the algorithm
used by the policy engine to resolve an authorization query.
PBAC/ABAC systems (OPA, Cedar) compile policies to efficient
data structures (AST, compiled Wasm) and evaluate conditions
in microseconds. ReBAC systems (SpiceDB, OpenFGA) resolve
authorization via graph traversal, where performance depends
on relationship graph depth and fan-out. XACML evaluators
parse XML documents per request, making them orders of
magnitude slower. Performance optimization techniques include:
partial evaluation (pre-compile policy with known data),
query planning (optimize traversal order), caching (memoize
stable decisions), and data bundling (co-locate policy data).

---

### ⚙️ How It Works (Mechanism)

**Evaluation complexity models:**

```
┌────────────────────────────────────────────────────────┐
│       Policy Evaluation Complexity                     │
├──────────────────────┬─────────────────────────────────┤
│  System              │ Complexity/Latency              │
├──────────────────────┼─────────────────────────────────┤
│  OPA (local)         │ O(policy depth), <0.1ms         │
│  OPA (remote)        │ O(policy depth), 1-5ms          │
│  Cedar (local lib)   │ O(policy count), <0.1ms         │
│  SpiceDB check       │ O(V+E graph), 2-10ms            │
│  OpenFGA check       │ O(V+E graph), 2-10ms            │
│  XACML (typical)     │ O(policy*XML), 10-100ms         │
│  DB row-level sec    │ O(query complexity), 1-10ms     │
├──────────────────────┴─────────────────────────────────┤
│                                                        │
│  OPA OPTIMIZATION:                                     │
│  Partial eval: pre-compile Rego with known data        │
│    Policy with user.department baked in               │
│    -> evaluate only resource conditions per request   │
│  Bundle: ship policy + data together                   │
│    -> no PIP calls during evaluation                  │
│                                                        │
│  SPICEDB/OPENFGA OPTIMIZATION:                         │
│  Limit graph depth in schema (max 3 hops)              │
│  Cache frequent check results                          │
│  Use batch check API (multiple checks in one RPC)      │
│  Choose consistency level: minimize_latency vs full    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA partial evaluation for performance**

```bash
# Pre-compile Rego policy with static data
# Result: a "partial" policy with data already bound
# Evaluation is much faster at request time

opa partial -d policy.rego -d user_roles.json \
  --partial "data.authz.allow" \
  -f pretty

# Output: a simplified policy with role data inlined
# No data lookup needed during request evaluation

# Alternatively: use OPA's decision cache
# OPA caches the compilation output; evaluation is
# in-memory AST evaluation (sub-millisecond)
```

**Example - SpiceDB batch check for list filtering**

```java
// BAD: N+1 authorization check pattern
// For 100 documents: 100 separate check RPCs
public List<Document> getReadableDocuments(
        String userId, List<String> docIds) {
    return docIds.stream()
        .filter(docId ->
            authzService.canRead(userId, docId)) // N calls
        .map(docRepo::findById)
        .collect(Collectors.toList());
}

// GOOD: batch check - all in one RPC
public List<Document> getReadableDocuments(
        String userId, List<String> docIds) {
    // SpiceDB/OpenFGA batch check
    Map<String, Boolean> decisions =
        authzService.batchCheck(userId, "read",
            "document", docIds);
    return docIds.stream()
        .filter(id -> decisions.getOrDefault(id, false))
        .map(docRepo::findById)
        .collect(Collectors.toList());
}
```

---

*Authorization category: ATZ | Entry: ATZ-039 | v5.0*