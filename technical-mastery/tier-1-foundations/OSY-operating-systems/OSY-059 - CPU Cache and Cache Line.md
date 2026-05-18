---
id: OSY-059
title: CPU Cache and Cache Line
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-011, OSY-054
used_by: OSY-060, OSY-094, OSY-099
related: OSY-058, OSY-060, OSY-094
tags:
  - CPU-cache
  - cache-line
  - L1-L2-L3
  - cache-hierarchy
  - hardware
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/osy/cpu-cache-cache-line/
---

## TL;DR

CPU cache is SRAM between the CPU and main RAM. Cache line
is the unit of transfer (64 bytes on x86). L1: 4 cycles,
L2: 12 cycles, L3: 40 cycles, RAM: 200+ cycles. Programs
that access data sequentially (cache-friendly) run 10-100x
faster than programs with random access. False sharing
occurs when two threads write to different fields that share
the same 64-byte cache line.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-059 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | L1 L2 L3 cache, cache line, false sharing, hardware prefetch |
| **Prerequisites** | OSY-011, OSY-054 |

---

### Cache Hierarchy and Latency Numbers

```
CPU Core 0                         CPU Core 1
  |                                  |
  L1-I cache (32KB, ~4 cycles)       L1-I cache
  L1-D cache (32KB, ~4 cycles)       L1-D cache
  L2 unified  (256KB, ~12 cycles)    L2 unified
  |                                  |
  L3 unified (shared, 8-32MB, ~40 cycles)
  |
  RAM (64GB, ~200-300 cycles = 70-100ns)
  |
  NVMe SSD (~100,000 cycles = 30-60 microseconds)
  |
  HDD (~10,000,000 cycles = 5-10 milliseconds)

Latency in human scale (CPU cycle = 1 second):
  L1 cache hit:    4 seconds
  L2 cache hit:   12 seconds
  L3 cache hit:   40 seconds
  RAM:           200 seconds (3+ minutes)
  NVMe SSD:     100,000 seconds (28 hours)
  HDD:       10,000,000 seconds (4 months)

Cache size vs working set:
  L1: 32KB   -> ~8000 longs or ~4000 object references
  L2: 256KB  -> ~64000 longs
  L3: 8MB    -> ~2M longs (typical hot path data)
  RAM: 64GB  -> everything else

Cache line: 64 bytes (x86-64)
  = 8 longs, 16 ints, 64 bytes, or one Java object header+1 field
  When CPU loads one byte: entire 64-byte line loaded from memory
```

---

### Sequential vs Random Access

```java
// BAD: random access - cache unfriendly
public class RandomAccess {
    public static long sum(int[] data, int[] indices) {
        long total = 0;
        for (int i : indices) {
            total += data[i]; // random jump: likely cache miss
        }
        return total;
    }
}
// Each data[i] likely in different cache line
// Most accesses: L3 miss -> RAM fetch (200 cycles each)
// 1 million elements * 200 cycles = 200M cycles wasted

// GOOD: sequential access - cache friendly
public class SequentialAccess {
    public static long sum(int[] data) {
        long total = 0;
        for (int val : data) {
            total += val; // sequential: hardware prefetch works!
        }
        return total;
    }
}
// CPU hardware prefetcher detects sequential pattern
// Pre-fetches next cache lines before they're needed
// Most accesses: L1 hit (4 cycles each)
// 50x+ faster than random access

// Benchmark comparison (JMH):
// Sequential: ~5 ns per element (L1/L2 hits)
// Random:     ~200 ns per element (L3/RAM misses)
// Ratio: 40x difference in throughput
```

---

### Cache Lines and Data Structure Layout

```java
// GOOD: struct-of-arrays (SoA) - cache friendly
// All x values together, all y values together
class Points {
    float[] x = new float[N];  // all x's in contiguous cache lines
    float[] y = new float[N];  // all y's in contiguous cache lines
    
    float sumX() {
        float sum = 0;
        for (int i = 0; i < N; i++) {
            sum += x[i];  // loads 16 floats per cache line
        }
        return sum;       // perfect sequential access
    }
}

// BAD: array-of-structs (AoS) - cache unfriendly for partial use
class PointAoS {
    float x, y, z, w;  // 16 bytes per point
}
PointAoS[] points = new PointAoS[N];

float sumX() {
    float sum = 0;
    for (PointAoS p : points) {
        sum += p.x;  // Need only x, but loads entire object + y/z/w
        // Each object might be in different cache line
        // (JVM object layout: header 12-16 bytes + fields)
    }
    return sum;
}
// AoS: 25% cache utilization (only x used from 16-byte struct)
// SoA: 100% cache utilization (only x[] accessed)
```

---

### Hardware Prefetcher

```
CPU hardware prefetcher:
  Detects memory access patterns and pre-loads cache lines
  
  Patterns it detects:
    Sequential (stride 1): a[0], a[1], a[2], ... -> PERFECT
    Stride pattern: a[0], a[8], a[16], ...       -> DETECTED
    Random: a[5], a[273], a[1], a[99], ...       -> FAILS
    
  Prefetch distance:
    Typically 8-32 cache lines ahead
    Reads ahead before data is needed -> hides RAM latency
    
  When prefetcher helps most:
    Large arrays, sequential iteration
    Sorted data structures (binary tree traversal is poor)
    
  When prefetcher fails:
    Pointer chasing: node.next.next.next (each pointer to unknown addr)
    Hash tables with poor hash functions (scattered memory)
    Trees with scattered node allocation

Java LinkedList vs ArrayList:
  ArrayList: contiguous memory -> hardware prefetcher works
  LinkedList: pointer chasing (node.next = anywhere in heap)
    -> hardware prefetcher cannot help
    -> LinkedList iteration: 5-10x slower than ArrayList
    -> This is why ArrayList is preferred for iteration
```

---

### Diagnosing Cache Miss Behavior

```bash
# Count cache misses with perf:
perf stat -e cache-references,cache-misses,L1-dcache-loads \
          -e L1-dcache-load-misses,LLC-loads,LLC-load-misses \
          java -jar app.jar 2>&1

# Example output:
#   100,000,000  L1-dcache-loads
#     5,000,000  L1-dcache-load-misses    (5% L1 miss rate)
#    10,000,000  LLC-loads
#     2,000,000  LLC-load-misses          (20% LLC miss rate = problem!)
# 
# LLC = Last Level Cache = L3
# LLC miss rate > 10%: significant time spent waiting for RAM

# Find hot cache misses (which code is missing most):
perf record -e cache-misses java -jar app.jar
perf report  # shows flame graph colored by cache misses

# Identify memory access pattern issues:
perf stat -e dTLB-loads,dTLB-load-misses \
          -e node-loads,node-load-misses java -jar app.jar
# node-load-misses: NUMA remote access misses
# dTLB-load-misses: page table cache misses
```

---

### Cache-Friendly Data Access Patterns

```
Matrix multiplication: cache-friendly vs unfriendly

N x N matrix stored in row-major order:
  A[row][col] = A[row * N + col]  (contiguous row storage)
  
BAD: column-major iteration (cache-unfriendly)
  for(int j = 0; j < N; j++)       // column outer
    for(int i = 0; i < N; i++)     // row inner
      C[i][j] += A[i][k] * B[k][j];
  // B[k][j]: j varies in inner loop -> jumps N*4 bytes each access
  // For N=1000: jumps 4KB per access = different cache line each time

GOOD: loop tiling (cache-friendly)
  int BLOCK = 32;  // fits in L1 cache (32 * 32 * 4 = 4KB)
  for(int ii = 0; ii < N; ii += BLOCK)
    for(int jj = 0; jj < N; jj += BLOCK)
      for(int kk = 0; kk < N; kk += BLOCK)
        for(int i = ii; i < min(ii+BLOCK, N); i++)
          for(int j = jj; j < min(jj+BLOCK, N); j++)
            for(int k = kk; k < min(kk+BLOCK, N); k++)
              C[i][j] += A[i][k] * B[k][j];
  // Each 32x32 block fits in L1 cache
  // 10-20x performance improvement on large matrices
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java object field access is always fast" | JVM object layout: header (12-16 bytes) + fields. If two frequently-accessed fields are in different cache lines (or an object reference graph has poor locality), every field access may be a cache miss. The JVM does NOT guarantee cache-friendly object layout |
| "A larger L3 cache always improves performance proportionally" | L3 is shared between cores. Under high thread count, L3 contention can cause threads to evict each other's data. Doubling L3 size helps only if the working set was just slightly over the previous limit. If your working set is 10x larger than L3, a bigger L3 won't help |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Cache line size | 64 bytes on x86-64 |
| L1 hit | ~4 cycles |
| L3 hit | ~40 cycles |
| RAM access | ~200+ cycles |
| Sequential vs random | Sequential: 40x faster (hardware prefetch) |
| ArrayList vs LinkedList | ArrayList wins iteration (cache locality) |
| perf cache misses | `perf stat -e LLC-load-misses java ...` |
