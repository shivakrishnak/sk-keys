---
layout: default
title: "Serial GC"
parent: "Java & JVM Internals"
nav_order: 286
permalink: /java/serial-gc/
number: "0286"
category: Java & JVM Internals
difficulty: ★★☆
depends_on:
  - Young Generation
  - Old Generation
  - Minor GC
  - Full GC
  - Stop-The-World (STW)
used_by:
  - GC Tuning
  - Parallel GC
  - GC Logs
related:
  - Parallel GC
  - G1GC
  - CMS (Concurrent Mark Sweep)
  - GC Tuning
  - Throughput vs Latency (GC)
tags:
  - jvm
  - garbage-collection
  - memory-management
  - java-internals
  - performance
---

# 0286 — Serial GC

## 1. TL;DR
> **Serial GC** is the simplest JVM garbage collector — it uses a **single thread** for all GC work and **freezes all application threads** (STW) during every collection. Designed for single-CPU environments and small heaps, it is the only collector that is truly sequential with no parallelism. On modern multi-core hardware with large heaps, it is generally not suitable for production use.

---

## 2. Visual: How It Fits In

```
Serial GC — Single-threaded, Stop-The-World

Young Generation Collection:
App Threads: ──────────────┤ PAUSED ├──────────────────────
GC Thread 1: ──────────────┤  Mark  │ Copy │ Reclaim ├─────
                                    (single thread does everything)

Old Generation Collection (Mark-Sweep-Compact):
App Threads: ──────────────┤       PAUSED (longer)        ├──
GC Thread 1: ──────────────┤  Mark  │  Sweep  │  Compact  ├──

No parallel GC threads — one thread does 100% of the work
```

---

## 3. Core Concept

Serial GC uses:
- **Young Gen:** Mark-Copy — live objects copied to Survivor/Old, Eden reclaimed
- **Old Gen:** Mark-Sweep-Compact — marks live, sweeps dead, compacts remaining

It is **fully Stop-The-World**: not a single GC phase runs concurrently with application threads. Every collection, whether Minor or Full, freezes the entire JVM.

---

### Enable with:

```bash
-XX:+UseSerialGC
```

---

### When Serial GC is chosen automatically:

- Java 7 and earlier on single-CPU machines
- Very small heap environments
- Some embedded/CLI tool contexts

---

## 4. Why It Matters

Serial GC establishes the **baseline understanding** of how GC works before studying more complex algorithms. It is also the **fallback** used during Full GC in G1GC when G1 cannot handle evacuation — G1 degrades to a serial single-threaded full collection in worst cases. Understanding Serial GC helps explain why all other collectors were built to improve upon it.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| GC threads | 1 (single thread) |
| Application threads during GC | Suspended (STW) |
| Young Gen algorithm | Mark-Copy (Copying Collector) |
| Old Gen algorithm | Mark-Sweep-Compact |
| Heap layout | Young (Eden + 2 Survivors) + Old + Metaspace |
| JVM flag | `-XX:+UseSerialGC` |
| Best for | Single-core, small heap (< 100MB), containers with 1 vCPU |
| Typical pause | Proportional to heap size; can be seconds on large heaps |
| Footprint | Lowest of all collectors (minimal metadata) |
| Java version | Available since Java 1.0; still present in Java 21+ |

---

## 6. Real-World Analogy

> A one-person office cleaning crew. When it's time to clean (GC), everyone in the office must leave (STW). The single cleaner vacuums, mops, and reorganizes everything from the break room (Young Gen) to the archive room (Old Gen), all by themselves. It's thorough and predictable, but the office is completely unusable while cleaning happens. A larger office building would hire multiple cleaners (Parallel GC) or cleaners who work during business hours (concurrent GC).

---

## 7. How It Works — Step by Step

```
Minor GC (Young Generation):
1. STW begins — all application threads paused
2. Single GC thread starts
3. Mark phase: trace from GC Roots into Eden + Survivor spaces
4. Copy phase: live objects copied to next Survivor space (or promoted to Old)
5. Eden + old Survivor space reclaimed entirely
6. STW ends — application threads resume

Full GC (Old Generation + Young):
1. STW begins — all application threads paused
2. Single GC thread starts
3. Mark phase: traverse entire heap from GC Roots, mark all live objects
4. Sweep phase: identify and reclaim unreachable objects
5. Compact phase: slide live objects down to eliminate fragmentation
6. Young Gen also collected
7. Metaspace collected (dead classes/classloaders)
8. STW ends — application threads resume
```

---

## 8. Under the Hood (Deep Dive)

---

### Memory layout

```
Serial GC heap layout:
┌─────────────────────────────────────────────────────────┐
│  Young Generation (-XX:NewRatio controls split)         │
│  ┌──────────────────────┬────────────┬────────────────┐ │
│  │       Eden           │ Survivor 0  │ Survivor 1     │ │
│  │   (new objects)      │ (from)      │ (to)           │ │
│  └──────────────────────┴────────────┴────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Old Generation                                         │
│  (objects surviving multiple Minor GCs)                 │
└─────────────────────────────────────────────────────────┘
Metaspace: separate native memory (not in heap)
```

---

### Copying collector (Young Gen)

```
Before Minor GC:
Eden: [A][B][C][D][E] (A, C, E = live; B, D = dead)
S0:   [F][G]          (both live)
S1:   []              (empty — "to" space)

After Minor GC (objects copied to S1 or promoted):
Eden: [] (cleared)
S0:   [] (cleared)
S1:   [A][C][E][F][G] (live objects copied)
Old:  []  (if any objects old enough, promoted here)
```

---

### Mark-Sweep-Compact (Old Gen)

```
Step 1: Mark
  Walk all GC roots → mark reachable objects

Step 2: Sweep
  Scan heap; objects not marked = dead → free them

Step 3: Compact
  Slide all live objects to one end of Old Gen
  Update all references to reflect new positions
  
Result: No fragmentation, but expensive for large heaps
```

---

### Tuning Serial GC

```bash
-XX:+UseSerialGC              # Enable Serial GC
-Xms64m -Xmx64m              # Fixed heap for predictability
-XX:NewRatio=2                # Old:Young ratio = 2:1
-XX:SurvivorRatio=8           # Eden:Survivor ratio = 8:1
-XX:MaxTenuringThreshold=15   # Promotions after 15 Minor GCs
```

---

## 9. Comparison Table

| Feature | Serial GC | Parallel GC | G1GC | ZGC |
|---------|-----------|-------------|------|-----|
| GC threads | 1 | N (parallel) | N (parallel+concurrent) | N (concurrent) |
| STW pauses | All phases | All phases | Most phases | < 1ms |
| Heap size | < 100MB ideal | Up to ~8GB | Up to 32GB+ | 100MB–16TB |
| Throughput | Moderate | High | High | Good |
| Latency | Poor | Poor | Good | Excellent |
| Footprint | Minimal | Low | Moderate | Higher |
| Use case | CLI tools, containers, 1 CPU | Batch jobs | General purpose | Latency-critical |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Single-CPU containers (1 vCPU) | Serial GC can be appropriate |
| Small microservices (< 64MB heap) | Serial GC reduces overhead |
| Batch/CLI tools | Serial GC is fine |
| Multi-core production APIs | ❌ Avoid — use G1 or ZGC |
| Heap > 1 GB | ❌ Avoid — pauses too long |

---

## 11. Common Pitfalls & Mistakes

```
❌ Running Serial GC on multi-core servers with large heap
   → Wastes cores; pauses grow with heap size

❌ Mistaking SerialGC fallback in G1 for a configuration choice
   → When G1 does Full GC, it uses serial algorithm as fallback

❌ Not specifying GC at all in containers
   → JVM may choose Serial GC if it detects < 2 CPUs
   → Explicitly set -XX:+UseG1GC (Java 9+ default)

❌ Expecting Serial GC to compact Young Gen
   → Young Gen uses Copying (no compaction); Old Gen uses compaction
```

---

## 12. Code / Config Examples

```bash
# Explicitly enable Serial GC
java -XX:+UseSerialGC -Xms32m -Xmx64m -jar app.jar

# Use-case: small CLI tool with bounded memory
java -XX:+UseSerialGC -Xmx32m -cp tools.jar com.example.BatchTool

# Log Serial GC events
java -XX:+UseSerialGC \
     -Xlog:gc*:file=serial-gc.log:time,uptime \
     -jar app.jar

# Verify active GC at startup
java -XX:+UseSerialGC -XX:+PrintCommandLineFlags -version
```

```
# Sample Serial GC log output:
[0.012s][info][gc] GC(0) Pause Young (Allocation Failure) 24M->8M(64M) 12.345ms
[5.678s][info][gc] GC(1) Pause Young (Allocation Failure) 56M->10M(64M) 15.678ms
[10.234s][info][gc] GC(2) Pause Full (Allocation Failure)  62M->15M(64M) 245.123ms
```

---

## 13. Interview Q&A

**Q: What is Serial GC and when would you use it?**
> Serial GC is JVM's single-threaded, fully Stop-The-World garbage collector using Mark-Copy for Young Gen and Mark-Sweep-Compact for Old Gen. Use it for single-CPU environments, small-heap CLI tools, or container workloads with 1 vCPU where multi-threaded GC overhead isn't justified.

**Q: Why is Serial GC unsuitable for large heap production services?**
> Because all GC work is done by a single thread while application threads are fully suspended. Pause time scales with heap size — a 16 GB heap can result in multi-second STW pauses, which violates any reasonable latency SLA.

**Q: How does G1GC's fallback relate to Serial GC?**
> When G1GC encounters an evacuation failure (cannot move objects), it falls back to a serial, fully STW Full GC using the same algorithm as Serial GC. This is a worst-case scenario for G1 and should be avoided through proper heap sizing.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| How many GC threads does Serial GC use? | 1 (single thread) |
| What algorithm does Serial GC use for Young Gen? | Mark-Copy (Copying Collector) |
| What algorithm for Old Gen? | Mark-Sweep-Compact |
| JVM flag to enable Serial GC | `-XX:+UseSerialGC` |
| When does G1GC use serial collection? | On evacuation failure (Full GC fallback) |

---

## 15. Quick Quiz

**Question 1:** Which heap region does NOT get compacted in Serial GC?

- A) Old Generation
- B) ✅ Young Generation (uses Copying, not Compaction)
- C) Metaspace
- D) Both A and C

**Question 2:** In which scenario is Serial GC the correct choice?

- A) 64-core server, 128 GB heap, e-commerce site
- B) ✅ 1-vCPU container, 64 MB heap, batch import tool
- C) Low-latency trading system, 8 GB heap
- D) Kubernetes pod with 4 CPUs, Spring Boot API

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Default JVM in containerized environment
   Problem:  JVM sees container CPUs incorrectly; may choose Serial GC
   Fix:      Always specify -XX:+UseG1GC explicitly in containers

🚫 Anti-Pattern: Using Serial GC for microservices on Kubernetes
   Problem:  STW pauses fail readiness probes, cause pod restarts
   Fix:      Use G1GC with -XX:MaxGCPauseMillis=100 or ZGC

🚫 Anti-Pattern: Believing Serial GC "fully compacts" the heap every time
   Problem:  Only Old Gen is compacted; Young Gen uses copying
   Fix:      Understand the dual-algorithm nature of Serial GC
```

---

## 17. Related Concepts Map

```
Serial GC
├── uses ────────────► Mark-Copy (Young Gen)
│                  ──► Mark-Sweep-Compact (Old Gen)
├── requires ────────► Stop-The-World (STW) [#285]
├── collects ────────► Young Generation [#278]
│                  ──► Old Generation [#281]
├── compared to ─────► Parallel GC [#287]
│                  ──► G1GC [#289]
│                  ──► CMS [#288]
├── fallback for ────► G1GC Full GC
└── tuned via ───────► GC Tuning [#292]
```

---

## 18. Further Reading

- [Oracle: Serial Collector](https://docs.oracle.com/en/java/javase/21/gctuning/available-collectors.html)
- [JVM GC Tuning Guide — Oracle Java 21](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [Serial GC vs Parallel GC benchmarks](https://plumbr.io/blog/garbage-collection/serial-vs-parallel-vs-cms-vs-g1)

---

## 19. Human Summary

Serial GC is the original JVM garbage collector — the one that taught us what GC fundamentally means. It's simple, predictable, and still useful in constrained environments. But on any modern server with multiple cores and a meaningful heap size, it becomes a liability: one thread doing all the work while everything else stops is exactly the kind of bottleneck you don't want in production.

Understanding Serial GC deeply helps you appreciate why Parallel GC was built (use all cores), why CMS was built (do work concurrently), why G1 was built (predictable pauses), and why ZGC was built (near-zero pauses). Each is an answer to a different limitation of the one before it.

---

## 20. Tags

`jvm` `garbage-collection` `memory-management` `java-internals` `performance` `serial-gc`

