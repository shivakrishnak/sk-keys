---
id: DSA-108
title: Fleet-Scale Algorithm Audit
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-106, DSA-107, DSA-076
used_by: DSA-122
related: DSA-106, DSA-107
tags:
  - fleet-scale
  - audit
  - principal-engineer
  - org-wide
  - algorithm-review
  - governance
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 108
permalink: /technical-mastery/dsa/fleet-scale-audit/
---

## TL;DR

A fleet-scale algorithm audit identifies O(n^2) code
paths, custom implementations that should be standard
library, and security-relevant algorithm choices across
an entire organization's codebase - enabling systematic
technical debt reduction.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-108 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | fleet scale, audit, principal engineer, governance |
| **Prerequisites** | DSA-106, DSA-107, DSA-076 |

---

### What a Fleet-Scale Audit Finds

A fleet audit at a 500-engineer company typically finds:
1. 15-30 custom LRU/LFU cache implementations
2. 50-100 instances of List.contains() inside loops (O(n^2))
3. 5-10 HashMap instances with default capacity storing >100K entries
4. 20-50 synchronized(map) patterns causing thundering herd
5. Custom sorting implementations missing edge cases
6. 3-7 Bloom filter implementations with incorrect hash function count

Each category has an estimated remediation ROI.

---

### Audit Phase 1: Automated Code Scanning

**Static analysis rules (SpotBugs + custom rules):**

```java
// Custom SpotBugs rule: detect List.contains() in loops
// Pattern: for-each loop body contains list.contains() call
// This is O(n^2) for List, O(1) for Set

// Detect via AST pattern matching:
// ForEachStatement → body contains MethodCall "contains"
//   on type implementing List (not Set, not Map)

// PMD custom rule in XPath:
// //ForStatement/Statement//PrimaryExpression
//   [PrimaryPrefix/Name[ends-with(@Image, '.contains')]]
//   [ancestor::ForStatement]

// SonarQube custom rule:
// Type check: method called on variable of type List<T>
// Context: inside a loop body (For, While, DoWhile, ForEach)
// Report: "List.contains() in loop is O(n^2). Use Set.contains()"
```

**Grep patterns for manual audit:**

```bash
# Find synchronized map patterns
grep -rn "Collections.synchronizedMap\|Collections.synchronizedList" \
  src/ --include="*.java" | wc -l

# Find HashMap without initial capacity
grep -rn "new HashMap<>()" src/ --include="*.java" \
  | grep -v "// pre-sized" | head -30

# Find custom cache implementations
grep -rn "class.*Cache.*{" src/ --include="*.java"
grep -rn "private.*Map.*cache\|private.*Cache\|evict" \
  src/ --include="*.java" | grep -v "import" | head -20

# Find potential O(n^2) string building
grep -rn '"+=' src/ --include="*.java" | head -20
# Look for patterns like: result += someString inside loop

# Find custom sorting
grep -rn "void.*sort\|implements Comparator" \
  src/ --include="*.java" | grep -v "import\|test\|Test"
```

---

### Audit Phase 2: Profiling at Scale

```bash
# Fleet-wide allocation rate monitoring (JFR + Prometheus)
# Add to all JVM services:
# -XX:StartFlightRecording=duration=60s,filename=/tmp/app.jfr
# OR continuous recording with periodic dump

# Aggregate allocation hotspots across fleet:
# For each pod: dump top-10 allocation classes per 5 minutes
# Aggregate: which class appears most frequently fleet-wide?

# Alert on fleet-wide patterns:
# ALERT HighBoxingAllocationFleetWide
#   IF avg(jfr_allocation_rate{class="java.lang.Integer"})
#      > 10_000_000  # 10M Integer allocations/sec fleet-wide
#   FOR 10m

# Fleet-wide GC pause monitoring:
# Sum of all GC pause time across fleet = "GC tax"
# If 5% of all fleet CPU is GC: algorithm audit warranted
```

---

### Audit Phase 3: Security Review

**Security-relevant algorithm patterns:**

```java
// 1. HashMap with untrusted key input (hash flooding risk)
//    Check: are keys ever derived from user input?
//    Mitigation: Java 7u6+ String hash seeding protects String keys
//                Custom key classes need their own seeding

// 2. Timing-vulnerable equality checks (side-channel attack)
//    BAD: comparing API keys, tokens, or MACs with equals()
if (storedToken.equals(receivedToken)) { ... }
//    This can leak information via timing differences
//    GOOD: MessageDigest.isEqual() (constant-time comparison)
if (MessageDigest.isEqual(
        storedToken.getBytes(),
        receivedToken.getBytes())) { ... }

// 3. Random number generator choice
//    BAD: new Random() for security tokens (predictable seed)
Random rng = new Random(); // PREDICTABLE
String token = Long.toHexString(rng.nextLong());
//    GOOD: SecureRandom for security-sensitive values
SecureRandom rng2 = new SecureRandom();
byte[] token2 = new byte[32];
rng2.nextBytes(token2);

// 4. Unbounded input processing
//    Pattern: processAllRecords(userProvidedList)
//    Risk: DoS via extremely large list
//    Mitigation: validate input size at service boundary
if (items.size() > MAX_BATCH_SIZE) {
    throw new IllegalArgumentException(
        "Batch size " + items.size() +
        " exceeds maximum " + MAX_BATCH_SIZE
    );
}
```

---

### Audit Prioritization Matrix

| Issue | Performance Impact | Security Risk | Fix Effort | Priority |
|-------|------------------|--------------|-----------|---------|
| O(n^2) in hot path | Critical | Low | Low | P0 |
| synchronizedMap thundering herd | High | Low | Low | P1 |
| HashMap resize at startup | Medium | Low | Very Low | P1 |
| Custom LRU cache (concurrent bug) | Medium | Medium | Medium | P1 |
| equals() for token comparison | Low | Critical | Very Low | P0 |
| new Random() for tokens | Low | Critical | Very Low | P0 |
| Integer boxing in tight loop | Medium | Low | Medium | P2 |
| Custom sort missing edge cases | Low | Low | Low | P2 |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Fleet audits require expensive tooling" | Basic grep patterns + SpotBugs + existing APM (Datadog, New Relic) allocation metrics cover 80% of findings. Expensive tooling is not required |
| "Fixing O(n^2) across the fleet requires large refactors" | The most common fixes (List.contains -> Set.contains, synchronizedMap -> ConcurrentHashMap) are 1-5 line changes with large performance impact |

---

### Mastery Checklist

- [ ] Has designed a custom SpotBugs or SonarQube rule
- [ ] Knows the fleet-wide security patterns to audit for
- [ ] Can build a remediation prioritization from an audit
- [ ] Has presented fleet-scale findings to engineering leadership

---

### The Surprising Truth

Google's "Codebase Health" team conducts regular
fleet-scale algorithm audits across all Google services.
They found that fixing O(n) -> O(1) patterns (by
switching to the right data structure) in 200+ services
saved more than 500 CPU-years annually across their
fleet. The cost of the audit and fixes paid back within
3 months. The most impactful single change across their
audit: replacing `List.contains()` inside loops with
`Set.contains()` - a pattern so common that eliminating
it across Google's codebase freed multiple data center
racks worth of compute.
