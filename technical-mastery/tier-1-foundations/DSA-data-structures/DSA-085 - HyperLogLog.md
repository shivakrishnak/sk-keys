---
id: DSA-085
title: HyperLogLog
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-083, DSA-084
used_by: DSA-105
related: DSA-083, DSA-084
tags:
  - data-structures
  - hyperloglog
  - cardinality-estimation
  - probabilistic
  - streaming
  - redis
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 85
permalink: /technical-mastery/dsa/hyperloglog/
---

## TL;DR

HyperLogLog estimates the count of distinct values (cardinality)
in a stream with ~1.5KB of memory and ~2% error, regardless
of whether there are 1,000 or 1 billion distinct values -
the algorithm behind Redis PFCOUNT and Google Analytics.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-085 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, HyperLogLog, cardinality |
| **Prerequisites** | DSA-083, DSA-084 |

---

### The Problem This Solves

"How many distinct users visited our site today?"
Exact answer: store all user IDs in a set. For 100M
daily users: 100M * 8 bytes = 800MB just for today.
HyperLogLog: 1.5KB for any cardinality, ~2% error.
A 400,000x reduction in memory with acceptably small error.

---

### Textbook Definition

HyperLogLog estimates set cardinality using the following
observation: if we hash elements uniformly, the maximum
number of leading zeros in any hash value follows a
statistical pattern related to cardinality. More leading
zeros → larger set. HLL uses m buckets (m = 2^b bits for
precision b) each tracking the maximum leading zeros seen.
Combines buckets using harmonic mean to estimate total
distinct count. Error: 1.04/sqrt(m).

---

### The Intuition

```
Flip a fair coin repeatedly until you see Heads.
The expected number of flips before first Heads = 1.

If longest run of Tails before Heads you've seen is k,
you've probably flipped about 2^k coins total.

Example: k=0 (immediate heads): ~1 flip
         k=3 (TTTh): ~8 flips
         k=10 (10 tails then head): ~1024 flips

HyperLogLog applies this idea to hash values:
- Hash elements to get a "random" bit string
- Track the maximum number of leading zeros
- Estimate: 2^(max_leading_zeros) ≈ distinct elements
```

**Implementation (simplified):**

```java
class HyperLogLog {
    private final int m;         // number of registers (2^b)
    private final byte[] regs;   // max leading zeros per bucket
    private final int b;         // precision bits

    HyperLogLog(int b) {
        this.b = b;
        this.m = 1 << b;         // 2^b registers
        this.regs = new byte[m];
        // Standard error: 1.04 / sqrt(m)
        // b=10: m=1024, error ≈ 3.25%
        // b=14: m=16384, error ≈ 0.81% (Redis default)
    }

    void add(String item) {
        long hash = murmurhash64(item);
        int register = (int)(hash >>> (64 - b)); // first b bits
        int w = Long.numberOfLeadingZeros(
                  (hash << b) | ((1L << b) - 1)) + 1;
        regs[register] = (byte) Math.max(regs[register], w);
    }

    long count() {
        double alpha = 0.7213 / (1 + 1.079 / m);
        double z = 0;
        for (byte r : regs) z += Math.pow(2, -r);
        long estimate = (long)(alpha * m * m / z);
        // Apply small/large range corrections here
        return estimate;
    }

    // HyperLogLog can be MERGED: union of two HLLs
    HyperLogLog merge(HyperLogLog other) {
        HyperLogLog result = new HyperLogLog(this.b);
        for (int i = 0; i < m; i++)
            result.regs[i] = (byte) Math.max(regs[i], other.regs[i]);
        return result;
    }
}
```

**Redis PFCOUNT:**

```bash
# Redis HyperLogLog uses 12KB (2^14 registers)
# Error ~0.81%

# Count distinct visitors
PFADD page_views:2024-01-15 "user1" "user2" "user3" "user1"
PFCOUNT page_views:2024-01-15  # returns ~3

# Merge multiple day HLLs into weekly count
PFMERGE weekly_visitors page_views:2024-01-15 page_views:2024-01-16
PFCOUNT weekly_visitors  # approximate distinct users in 2 days
```

---

### Comparison Table

| Property | HashSet | HyperLogLog |
|---------|---------|------------|
| Exact count | Yes | No (±2% error) |
| Memory | O(n) | O(log log n) ≈ 1.5KB |
| Add | O(1) | O(1) |
| Count | O(1) | O(m) |
| Merge | O(n) | O(m) |
| Delete | Yes | No |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "HyperLogLog's 1.5KB is for small sets only" | 1.5KB regardless of set size; same memory for 1K or 1B distinct items |
| "HyperLogLog error grows with set size" | Error is a fixed percentage (~2%); not absolute. ±2% of 1B is ±20M, but it's still the same 2% |

---

### Quick Reference Card

| Property | HyperLogLog |
|---------|------------|
| Typical error | ~2% (0.81% at max precision) |
| Memory | ~1.5KB (12KB for max precision) |
| Add | O(1) |
| Count | O(m) |
| Merge | O(m) - take cell-wise max |
| Redis command | PFADD, PFCOUNT, PFMERGE |

---

### The Surprising Truth

Google Analytics uses HyperLogLog for their unique visitor
counts across billions of websites. The "1.2 billion unique
visitors" on major websites is an HLL estimate, not an
exact count. Flajolet et al. published the HyperLogLog
algorithm in 2007. The "Hyper" prefix distinguishes it
from the earlier LogLog algorithm (2003). The key improvement
was using harmonic mean instead of geometric mean for
combining buckets, dramatically reducing variance.

---

### Mastery Checklist

- [ ] Can explain the leading-zeros intuition
- [ ] Knows Redis PFADD/PFCOUNT use HyperLogLog
- [ ] Understands HLL merge = cell-wise max

---

### Interview Deep-Dive

**Q1 (Hard):** Count distinct users across all 50 servers
in your cluster for a given day. Memory per server is
limited to 1MB.

> On each server: use HyperLogLog with b=14 (12KB, 0.81%
> error) to track distinct user IDs seen on that server.
> Add each request's user ID: PFADD daily_hll user_id.
> 
> At end of day (or periodically), send each server's
> 12KB HLL state to an aggregator.
> Aggregator merges all 50 HLLs: cell-wise maximum
> across all 50 * 16384 registers. O(50 * 16384) = O(1M)
> operations to merge.
> 
> Result: approximately accurate global distinct user count.
> Total aggregation data: 50 * 12KB = 600KB (fits in 1MB).
> If you had used HashSets: 50M unique users * 8 bytes =
> 400MB per server × 50 servers = 20GB to transmit.
> HyperLogLog makes this 33,000x more efficient.
