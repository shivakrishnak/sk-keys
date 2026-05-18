---
id: OSY-060
title: False Sharing Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-059, OSY-023
used_by: OSY-094
related: OSY-059, OSY-062, OSY-094
tags:
  - false-sharing
  - anti-pattern
  - cache-line
  - contended-counter
  - Contended
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/osy/false-sharing/
---

## TL;DR

False sharing: two threads write to different variables
that happen to sit in the same 64-byte cache line. Every
write by one thread invalidates the other thread's cached
copy, causing continuous cache-line bouncing across cores.
Symptoms: poor scalability under contention despite no
logical sharing. Fix: pad fields to align each to its own
64-byte cache line using `@Contended`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-060 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | false sharing, @Contended, cache line, MESI protocol |
| **Prerequisites** | OSY-059, OSY-023 |

---

### MESI Cache Coherence Protocol

```
Each cache line is in one of four states:
  M (Modified):  Line is dirty; only this core has it; must write back
  E (Exclusive): Line is clean; only this core has it; no other copies
  S (Shared):    Line is clean; multiple cores may have copies
  I (Invalid):   Line is stale; must fetch from another cache or RAM

State transitions under false sharing:
  
  Initial: Thread A and B read counter_a and counter_b
    Core 0 cache line: [counter_a | counter_b]  State: Shared (S)
    Core 1 cache line: [counter_a | counter_b]  State: Shared (S)
    
  Thread A (Core 0) writes counter_a:
    Core 0: Broadcasts "I'm modifying this line!" (RFO: Request for Ownership)
    Core 1: Line state -> Invalid (I)
    Core 0: Line state -> Modified (M)
    
  Thread B (Core 1) reads counter_b (different field!):
    Core 1: Line is Invalid -> must fetch from Core 0
    Core 0: Flush Modified line to L3 / RAM
    Core 1: Load line from L3 -> Shared (S)
    Core 0: Line state -> Shared (S)
    
  Thread A writes counter_a AGAIN:
    Same RFO round-trip: Core 1 invalidated again
    
  This ping-pong continues at RAM latency per operation!
  Expected: lock-free counters operating at L1 speed (4 cycles)
  Actual: cache-line bouncing at L3/RAM speed (40-200 cycles)
  Overhead: 10-50x performance penalty
```

---

### Demonstrating False Sharing

```java
// BAD: two counters share a cache line
public class FalseSharing {
    // Both fields in same object -> same cache line (likely)
    private volatile long counter0 = 0;  // bytes 12-19
    private volatile long counter1 = 0;  // bytes 20-27
    // Both fit in one 64-byte cache line -> FALSE SHARING!
    
    public void runContended() throws InterruptedException {
        Thread t0 = new Thread(() -> {
            for (int i = 0; i < 500_000_000; i++) counter0++;
        });
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 500_000_000; i++) counter1++;
        });
        long start = System.nanoTime();
        t0.start(); t1.start();
        t0.join(); t1.join();
        System.out.println("Time: " + (System.nanoTime() - start)/1e9 + "s");
    }
    // Typical result: ~12 seconds (even though no logical contention!)
    // Single-threaded equivalent: ~0.5 seconds each
    // 12x performance degradation from false sharing
}

// GOOD: pad to separate cache lines
public class NoPaddingIssue {
    // @Contended: JVM pads to isolate field in its own cache line
    @jdk.internal.vm.annotation.Contended
    private volatile long counter0 = 0;
    
    @jdk.internal.vm.annotation.Contended
    private volatile long counter1 = 0;
    
    // Run with: -XX:-RestrictContended
    // Result: ~0.5 seconds per thread (no false sharing)
}

// GOOD: manual padding (if @Contended not available)
public class ManualPadding {
    // 8 bytes counter + 56 bytes padding = 64 byte cache line
    private volatile long counter0;
    private long p1, p2, p3, p4, p5, p6, p7;  // 56 bytes padding
    
    // Next cache line starts here:
    private volatile long counter1;
    private long q1, q2, q3, q4, q5, q6, q7;  // 56 bytes padding
}
```

---

### Real-World False Sharing Locations

```java
// JDK internal example: LongAdder uses padding
// java.util.concurrent.atomic.Striped64 (parent of LongAdder)
// Each cell is padded to avoid false sharing between cells:
// @Contended static final class Cell {
//     volatile long value;
// }
// This is WHY LongAdder outperforms AtomicLong under contention!

// AtomicLong: one volatile long, all threads on same cache line
AtomicLong counter = new AtomicLong(0);
// Under high contention: all threads fight over same cache line
// = true sharing (expected), but still limited by cache-line coherence

// LongAdder: many cells, each on its own cache line
LongAdder counter = new LongAdder();
counter.increment();  // thread goes to its own cell (no sharing!)
long total = counter.sum();  // sums all cells

// Performance:
// AtomicLong under 16 threads: ~200ns/increment (L3 round-trips)
// LongAdder under 16 threads: ~10ns/increment (local cell write)
// LongAdder: 20x better throughput for write-heavy counters

// False sharing in Spring/JVM caches:
// HashMap internal table array: resize() can cause false sharing
// ConcurrentHashMap: segment design minimizes it
// Thread-local pools: designed to avoid cross-thread sharing
```

---

### Diagnosing False Sharing

```bash
# Method 1: perf c2c (cache-to-cache) - best tool
perf c2c record java -jar app.jar &
sleep 30
kill %1
perf c2c report --stdio 2>&1 | head -50
# Look for: "True sharing" vs "False sharing" columns
# False sharing lines with high "HITM %" = your culprit

# Method 2: perf stat with cache invalidation events
perf stat -e machine_clears.memory_ordering \
          -e machine_clears.cycle_activity.stalls_l2_miss \
          java -jar app.jar
# High machine_clears.memory_ordering = cache coherence issues

# Method 3: Intel VTune (if available)
# "Memory Access Analysis" -> identify cache line contention

# Method 4: JMH benchmark with padded vs unpadded
# Create two versions (padded and unpadded)
# If padded is significantly faster: false sharing confirmed

# Quick check: add padding and re-run benchmark
# If performance improves 3x+: false sharing was the issue
```

---

### False Sharing in Practice: Counters

```java
// Pattern: per-thread counters without false sharing
public class PerThreadCounters {
    // LongAdder handles false sharing internally:
    private final LongAdder requestCount = new LongAdder();
    private final LongAdder errorCount = new LongAdder();
    
    // Each LongAdder has cells padded with @Contended
    // Each thread uses its own cell (thread-striped)
    
    public void recordRequest() {
        requestCount.increment();
    }
    
    public void recordError() {
        errorCount.increment();
    }
    
    public Metrics getSnapshot() {
        return new Metrics(requestCount.sum(), errorCount.sum());
        // sum() is eventually consistent (acceptable for metrics)
    }
}

// Pattern: Akka/Netty often uses manual cache line alignment
// for hot path state variables in the event loop
// Netty's SingleThreadEventExecutor has padding around
// its task queue state variables to avoid false sharing
// between the I/O thread and submission threads
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Volatile eliminates false sharing overhead" | Volatile ensures visibility (consistent reads) but makes false sharing WORSE: every volatile write requires immediate cache-line invalidation broadcast to all other cores. Volatile + false sharing = maximum cache coherence traffic |
| "False sharing only affects arrays of primitives" | False sharing affects ANY two fields that land in the same 64-byte cache line, including: object fields written by different threads, HashMap entries, queue head and tail pointers (classic case), and thread-local state in a shared array |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Cache line size | 64 bytes (8 longs) |
| MESI invalid | Write triggers invalidation on other cores |
| @Contended | JVM pads field to its own cache line |
| Flag to enable | `-XX:-RestrictContended` for user code |
| LongAdder vs AtomicLong | LongAdder: cells padded; 20x faster under high contention |
| perf c2c | Best tool for diagnosing false sharing |
| Manual padding | 7 long padding fields after each hot field |
