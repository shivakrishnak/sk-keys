---
id: OSY-078
title: perf stat Performance Counters
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-059, OSY-077
used_by: OSY-094, OSY-098, OSY-099
related: OSY-077, OSY-094, OSY-098
tags:
  - perf
  - PMU
  - performance-counters
  - hardware-events
  - IPC
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 78
permalink: /technical-mastery/osy/perf-stat/
---

## TL;DR

`perf stat` reads CPU hardware performance counters (PMU -
Performance Monitoring Unit) to measure: instructions
executed, cache misses, branch mispredictions, and IPC
(instructions per cycle). IPC < 1.0 usually means memory-
bound. High cache-misses mean poor data locality. The
starting point for hardware-level performance diagnosis.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-078 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | perf stat, PMU, IPC, cache-misses, branch-misses |
| **Prerequisites** | OSY-059, OSY-077 |

---

### perf stat Basics

```bash
# Basic perf stat:
perf stat java -jar app.jar
# Output (example):
#
# Performance counter stats for 'java -jar app.jar':
#
#    60,245,123,456  instructions              #    1.45  insns per cycle
#    41,547,912,345  cycles
#     3,204,567,890  cache-misses              #    4.78% of all cache refs
#    67,089,234,567  cache-references
#       456,789,012  branch-misses             #    1.23% of all branches
#    37,123,456,789  branches
#
#       5.123456789  seconds time elapsed

# Interpreting:
# IPC = 1.45: decent (modern x86: good IPC is 2.0-4.0)
# cache-miss rate = 4.78%: moderate (> 10% is problematic)
# branch-miss rate = 1.23%: good (< 5% is acceptable)

# Attach to running process:
perf stat -p $(pgrep java) -- sleep 30
# Measure for 30 seconds, then print stats

# Specific event list:
perf stat -e cycles,instructions,cache-misses,\
              L1-dcache-loads,L1-dcache-load-misses,\
              LLC-loads,LLC-load-misses,\
              branch-misses,branch-loads \
          -p $(pgrep java) -- sleep 10

# Kernel events only (JVM is user-space; kernel events show kernel overhead):
perf stat -e cycles:k,instructions:k -p $(pgrep java) -- sleep 10
# cycles:k, instructions:k = kernel-mode only
# Compare with user-mode (default): ratio shows kernel overhead
```

---

### IPC Interpretation

```
IPC (Instructions Per Cycle):
  Measures: how much work per clock cycle
  
  Modern x86 pipeline: can execute 3-6 instructions per cycle (OOO exec)
  IPC < 1.0: CPU is stalling, waiting for something
  IPC 1-2:   Moderate; some stalls but reasonable
  IPC > 3:   Excellent; good instruction-level parallelism
  
  IPC diagnosis:
  
  Low IPC (<1.0) + high cache-misses:
    -> Memory bound: CPU waiting for data from RAM
    -> Fix: improve data locality, use cache-friendly structures
    -> Or: use huge pages (fewer TLB misses)
    
  Low IPC (<1.0) + low cache-misses:
    -> Other stalls: dependency chains, branch mispredictions?
    -> Check: branch-misses, cycles stalled on memory
    
  Low IPC (<1.0) + many futex operations:
    -> Lock contention: threads sleeping/waking
    -> CPU doing real work less than it could
    
  High IPC (>3.0):
    -> CPU-bound, computationally efficient
    -> Optimization target: algorithmic improvements
    -> Parallelism: can we use multiple cores?

  Throughput formula:
    effective_work = IPC * frequency * time
    Poor IPC: even fast CPU underperforms
```

---

### perf stat Event Categories

```bash
# List all available hardware events:
perf list hardware
perf list cache
perf list software
perf list tracepoint | head -20  # kernel tracepoints (many!)

# Hardware events (PMU):
# cycles          CPU clock cycles
# instructions    Instructions retired
# cache-references LLC (L3) accesses
# cache-misses    LLC misses -> goes to RAM
# branch-misses   Branch predictor misses
# bus-cycles      CPU-to-memory bus cycles

# Software events (kernel counters):
# task-clock      CPU time used
# context-switches context switch count
# cpu-migrations  thread migrated to another CPU
# page-faults     page fault count (major + minor)

# Cache hierarchy events:
perf stat -e L1-dcache-load-misses,\
              L2-dcache-load-misses,\
              LLC-load-misses \
          java -jar app.jar
# Shows miss rate at each cache level
# L1 miss rate -> most important for hot path code

# TLB events:
perf stat -e dTLB-load-misses,iTLB-load-misses -p $(pgrep java) -- sleep 10
# High dTLB misses: many different pages accessed (bad locality or huge page need)
# iTLB misses: JIT code cache too large or scattered

# NUMA events:
perf stat -e node-loads,node-load-misses -p $(pgrep java) -- sleep 10
# node-load-misses: remote NUMA memory accesses (bad = 2x latency)
```

---

### perf stat for Java JVM

```bash
# Java JVM note: JVM has its own profiling (JFR, JMH)
# perf stat works for: CPU/hardware behavior; doesn't know Java methods

# Step 1: Get hardware overview of JVM
perf stat -e cycles,instructions,cache-misses,branch-misses \
          -p $(pgrep java) -- sleep 30
# Determine: is it CPU-bound, memory-bound, or branch-bound?

# Step 2: If memory-bound (low IPC + high cache-misses):
perf stat -e L1-dcache-load-misses,LLC-load-misses \
          -p $(pgrep java) -- sleep 30
# How bad are the misses?

# Step 3: If high LLC-misses: use perf record + report to find HOT CODE
perf record -e LLC-load-misses -g -p $(pgrep java) -- sleep 30
perf report
# Shows: which Java methods (via JVM JIT symbols) are causing LLC misses
# Requires: -XX:+PreserveFramePointer (JVM flag for perf compatibility)
# And:      perf-map-agent (for JVM JIT symbol resolution)

# perf-map-agent: generates /tmp/perf-PID.map with JIT symbol addresses
# download: https://github.com/jvm-profiling-tools/perf-map-agent
java -agentpath:/path/to/libperfmap.so \
     -XX:+PreserveFramePointer \
     -jar app.jar &
PID=$!
perf record -F 99 -g -p $PID -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
# Flamegraph shows: CPU time by Java method name (JIT-resolved)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "perf stat overhead is the same as strace" | perf stat uses CPU hardware counters (PMU) which are read with near-zero overhead. The counters run independently in hardware; perf just reads registers. Overhead: < 1% for most workloads. Unlike strace, perf stat is safe for sustained production use on specific metrics |
| "High IPC means the application is performing well" | High IPC means the CPU is executing instructions efficiently. But the instructions might be wrong ones (hot loop doing useless work, spinning in a busy-wait, or repeatedly computing the same thing). IPC is a CPU efficiency metric, not an application correctness or algorithmic efficiency metric |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| IPC < 1.0 | CPU stalling; likely memory-bound (check cache-misses) |
| IPC > 3.0 | CPU-bound; good instruction-level parallelism |
| Cache-miss rate > 10% | Poor data locality; consider cache-friendly structures |
| Branch-miss rate > 5% | Branch predictor struggling; reduce conditional code |
| perf stat overhead | < 1% (hardware counters); safe for production |
| Java + perf | Need `-XX:+PreserveFramePointer` + perf-map-agent for JIT symbols |
