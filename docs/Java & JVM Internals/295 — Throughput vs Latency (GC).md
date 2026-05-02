---
layout: default
title: "Throughput vs Latency (GC)"
parent: "Java & JVM Internals"
nav_order: 295
permalink: /java/throughput-vs-latency-gc/
number: "0295"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - GC Pause
  - Parallel GC
  - G1GC
  - ZGC
  - GC Tuning
used_by:
  - GC Tuning
  - JIT Compiler
related:
  - GC Tuning
  - GC Pause
  - Serial GC
  - Parallel GC
  - G1GC
  - ZGC
tags:
  - jvm
  - garbage-collection
  - throughput
  - latency
  - java-internals
---

# 0295 — Throughput vs Latency (GC)

## 1. TL;DR
> In JVM garbage collection, **throughput** measures the percentage of time the application runs (vs. doing GC), while **latency** measures the length of individual GC pause events. These goals are in **fundamental tension**: collectors that maximize throughput (by batching GC work) tend to have longer individual pauses, while collectors that minimize pause duration sacrifice throughput by doing more frequent, smaller, or concurrent GC work with overhead.

---

## 2. Visual: How It Fits In

```
GC Trade-off Triangle:

           Throughput
              /\
             /  \
            /    \
           /      \
          /__________\
      Latency     Footprint

You can optimize any two, but the third suffers.

Timeline Illustration:

High Throughput (Parallel GC):
App: ████████████████████│pause│████████████████████│long pause│████
     ←── 95% app time ──►  5%   ←── lots of work ──►  long STW

Low Latency (ZGC):
App: ████████│p│████████████████│p│████████████████│p│██████████████
              ▲                   ▲                  ▲
            < 1ms              < 1ms               < 1ms
     App runs 85-90% with tiny pauses but slightly fewer cycles done

Legend: p = sub-millisecond pause; pause = longer STW pause
```

---

## 3. Core Concept

---

### Throughput definition

**GC Throughput = (Application Time) / (Total Time)**

```
Total Time = Application Time + GC Time

Examples:
- Parallel GC on batch job: 95% app, 5% GC → throughput = 95%
- G1GC on API: 90% app, 10% GC → throughput = 90%
- ZGC on latency-critical: 83% app, 17% GC → throughput = 83%
```

---

### Latency definition

**GC Latency = Max (or P99/P999) individual pause duration**

Not average! Tail latency is what matters for SLAs.

---

### The tension

- **To maximize throughput:** Minimize GC overhead (time spent in GC). Batch GC work, do it less frequently, do it all-at-once STW. Parallel GC wins here.
- **To minimize latency:** Break GC into tiny pieces, do them concurrently with app threads (adding overhead), never do long STW. ZGC wins here.
- **Load barriers (ZGC/Shenandoah):** Shift cost from STW pause to per-access overhead on app threads. Lower max pause, but lower throughput.

---

## 4. Why It Matters

The fundamental question in GC selection is: what does your application need?

| Application Type | Primary Goal | Best Collector |
|-----------------|--------------|----------------|
| Batch ETL (nightly) | Max throughput | Parallel GC |
| REST API (< 200ms SLA) | Balanced | G1GC |
| Trading system (< 1ms) | Min latency | ZGC |
| Interactive gaming | Min latency | ZGC/Shenandoah |
| Memory-constrained service | Min footprint | Serial GC |

Choosing the wrong collector creates structural problems no amount of tuning can fix.

---

## 5. Key Properties / Behavior Table

| Collector | Throughput | P99 Latency | Footprint |
|-----------|-----------|-------------|-----------|
| Serial GC | Moderate | Very poor (seconds) | Lowest |
| Parallel GC | **Best** | Poor (100ms-seconds) | Low |
| CMS | Good | Good (50-200ms) | Moderate |
| G1GC | Good | **Good** (50-200ms) | Moderate |
| ZGC | Good | **Best** (< 1ms) | Higher |
| Shenandoah | Good | **Best** (< 1ms) | Higher (Brooks ptrs) |

---

## 6. Real-World Analogy

> Consider two restaurant models:
> - **High throughput restaurant (Parallel GC):** Processes maximum customers per day by doing a complete deep-clean every night (STW) when closed. During the 2-hour cleaning window, no customers served — but maximum table turnover during open hours.
> - **Low latency restaurant (ZGC):** Stay open 24/7. Cleaning crew works continuously between tables (concurrent GC). Customers occasionally experience 1 second of minor delay as a waiter restacks dishes nearby (< 1ms pause). Fewer total covers served per day, but no 2-hour closure exists.

Choose based on: is it worse to close for 2 hours, or serve slightly fewer customers?

---

## 7. How It Works — Step by Step

```
Throughput optimization path (Parallel GC):
1. Allow garbage to accumulate (delay collection)
2. When heap near full, pause ALL threads
3. Use ALL CPU cores to collect as fast as possible
4. Resume — maximum work done per STW investment
Result: long pauses, maximum app CPU time between pauses

Latency optimization path (ZGC):
1. Begin marking as soon as cycle starts (never wait)
2. Spread GC work across concurrent threads running alongside app
3. Use load barriers to "tax" each reference access slightly
4. STW phases are < 1ms (only root scanning)
Result: continuous small overhead, no long pauses

Trade-off quantified:
- ZGC vs Parallel GC on a throughput benchmark:
  Parallel GC: 1,000,000 ops/second (baseline)
  ZGC:         850,000 ops/second (15% overhead)
  
- ZGC vs Parallel GC on latency:
  Parallel GC: P99 = 400ms, P999 = 2000ms
  ZGC:         P99 = 0.5ms, P999 = 1ms
```

---

## 8. Under the Hood (Deep Dive)

---

### GCTimeRatio (Parallel GC throughput knob)

```bash
# GCC Throughput goal:
-XX:GCTimeRatio=N
# GC should use no more than 1/(1+N) of total time
# Default: N=99 means GC≤1% of time
# Setting N=19 allows GC to use up to 5% of time

# JVM auto-adjusts heap size to meet this goal
# If GC overhead > threshold: grow heap
# If GC overhead < threshold: may shrink heap
```

---

### MaxGCPauseMillis (G1GC latency knob)

```bash
# G1 latency goal:
-XX:MaxGCPauseMillis=200  # Default 200ms
# G1 limits Collection Set size to fit within this goal
# Best-effort: not a hard guarantee

# G1 throughput impact:
# Lower MaxGCPauseMillis → smaller CSet → more frequent collections → lower throughput
# Higher MaxGCPauseMillis → larger CSet → less frequent collections → higher throughput
# Trade-off visible in GC overhead %
```

---

### Real benchmark comparison

```
Benchmark: Spring Boot REST API under load
Heap: 4 GB, Java 21, heavy request traffic

Collector         | Throughput     | P50 Pause | P99 Pause | P999 Pause
────────────────────────────────────────────────────────────────────────
Parallel GC       | 95,000 req/s   | 0.5ms     | 450ms     | 3,200ms
G1GC (default)   | 88,000 req/s   | 2ms       | 120ms     | 890ms
G1GC (tuned)     | 86,000 req/s   | 2ms       | 80ms      | 450ms
ZGC (Java 21)    | 80,000 req/s   | 1ms       | 1.5ms     | 3ms
ZGC Generational | 84,000 req/s   | 1ms       | 1.2ms     | 2.5ms

Takeaway: ZGC P999 is 1000× better than Parallel GC P999
         at the cost of ~15% throughput reduction.
```

---

## 9. Comparison Table

| Scenario | Primary Metric | Winner |
|----------|---------------|--------|
| Nightly ETL batch | Total job runtime | Parallel GC |
| REST API (SLA: P99 < 200ms) | P99 latency | G1GC |
| Financial trading (SLA: P99 < 1ms) | P999 latency | ZGC |
| Mobile game backend | Max pause | ZGC/Shenandoah |
| Memory-constrained CLI tool | Footprint | Serial GC |

---

## 10. When to Use / Avoid

| Decision | Guidance |
|----------|----------|
| Throughput-first | Parallel GC; accept long pauses |
| Need both (balanced) | G1GC is the pragmatic default |
| Latency-first | ZGC (Oracle + OpenJDK) or Shenandoah (OpenJDK) |
| Can't afford throughput loss | Profile ZGC overhead before committing |

---

## 11. Common Pitfalls & Mistakes

```
❌ Optimizing for throughput when system has latency SLAs
   → 95% throughput means nothing if P999 pauses cause SLA breaches

❌ Assuming ZGC is always "better" 
   → For pure batch workloads, Parallel GC may complete 15% faster

❌ Using average pause instead of P99/P999 to compare collectors
   → Average masks outliers; use histograms

❌ Not accounting for heap overhead in throughput comparison
   → ZGC may need 2x heap for same workload (concurrent relocation uses more memory)
```

---

## 12. Code / Config Examples

```bash
# Throughput-optimized (batch workload)
java -XX:+UseParallelGC \
     -XX:GCTimeRatio=99 \    # GC < 1% of time
     -Xms8g -Xmx8g \
     -jar batch-job.jar

# Balanced (general API)
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=150 \
     -Xms4g -Xmx4g \
     -jar api-service.jar

# Latency-optimized (critical API, Java 21)
java -XX:+UseZGC \
     -XX:+ZGenerational \    # Better throughput in Java 21
     -Xms8g -Xmx8g \
     -jar trading-service.jar
```

---

## 13. Interview Q&A

**Q: Explain the throughput vs latency tradeoff in GC.**
> Throughput is the fraction of time the app runs (vs. GC). Latency is the max individual pause duration. Collectors that maximize throughput (Parallel GC) batch GC work, causing long but infrequent STW pauses. Collectors that minimize latency (ZGC) do work concurrently with the app, incurring constant small overhead (load barriers) that reduces throughput by ~10-15% but eliminates long pauses. You choose based on your SLA: throughput matters for batch jobs, latency matters for user-facing services.

**Q: Which GC collector would you choose for a high-frequency trading system?**
> ZGC (or Shenandoah). Financial trading has sub-millisecond latency requirements where even a single 100ms G1GC pause could have significant financial impact. ZGC's sub-1ms pauses regardless of heap size are the only GC choice for this use case. Use Java 21 with GenerationalZGC for best throughput/latency balance.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| GC Throughput formula | App Time / Total Time (× 100%) |
| Which GC maximizes throughput? | Parallel GC |
| Which GC minimizes latency? | ZGC or Shenandoah |
| What is the cost of low-latency GC? | ~10-15% throughput reduction (load barrier overhead) |
| Flag for G1 pause target | `-XX:MaxGCPauseMillis=N` |

---

## 15. Quick Quiz

**Question 1:** A batch processing service completes in 4 hours with Parallel GC and 4.7 hours with ZGC. What is the likely explanation?

- A) ZGC has a bug
- B) ✅ ZGC's load barrier overhead reduces throughput ~15-18% for CPU-intensive workloads
- C) ZGC uses too much memory
- D) The service has memory leaks with ZGC

**Question 2:** For a REST API with SLA: "P99 response time < 100ms", which GC choice is MOST appropriate?

- A) Parallel GC (highest throughput)
- B) Serial GC (lowest footprint)
- C) ✅ G1GC with `-XX:MaxGCPauseMillis=50` (balanced: targets < 100ms pauses)
- D) No GC, use off-heap memory only

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Using throughput metrics to evaluate latency-sensitive services
   Problem:  95th percentile throughput is fine but P999 pauses kill SLAs
   Fix:      Always measure P99, P999 pause distribution alongside throughput

🚫 Anti-Pattern: Running batch and latency workloads on same GC settings
   Problem:  Batch ETL and API serving have opposite GC needs
   Fix:      Different services should have GC settings appropriate to their SLA
```

---

## 17. Related Concepts Map

```
Throughput vs Latency (GC)
├── throughput → ────► Parallel GC [#287]
│                  ──► GCTimeRatio flag
├── latency → ──────► ZGC [#290]
│                  ──► Shenandoah GC [#291]
│                  ──► G1GC [#289] (balanced)
├── measured via ────► GC Pause [#294]
│                  ──► GC Logs [#293]
└── tuned via ───────► GC Tuning [#292]
```

---

## 18. Further Reading

- [Oracle GC Tuning: Goals](https://docs.oracle.com/en/java/javase/21/gctuning/factors-affecting-garbage-collection-performance.html)
- [ZGC Throughput Analysis — OpenJDK](https://openjdk.org/jeps/439)
- [Latency vs Throughput — Martin Thompson (HPC)](https://mechanical-sympathy.blogspot.com/)

---

## 19. Human Summary

Throughput vs latency is the central GC design debate, and it applies to every collection every time. The fundamental insight is that you cannot have both: doing GC work concurrently (low latency) costs CPU cycles that would otherwise go to the application (lower throughput). Parallel GC says "do all GC work in one big STW burst" — maximum throughput, terrible tail latency. ZGC says "spread GC work as continuous background overhead" — excellent tail latency, slightly lower throughput.

For most real-world apps: G1GC is the right pragmatic balance. For latency-critical services running Java 15+: ZGC with GenerationalZGC (Java 21+) closes the throughput gap while preserving sub-ms pauses.

---

## 20. Tags

`jvm` `garbage-collection` `throughput` `latency` `java-internals` `performance` `tradeoff`

