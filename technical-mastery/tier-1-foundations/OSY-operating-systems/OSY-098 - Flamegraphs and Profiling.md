---
id: OSY-098
title: Flamegraphs and Profiling
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-020, OSY-065, OSY-094, OSY-097
used_by: []
related: OSY-097, OSY-099, OSY-116
tags:
  - flamegraph
  - profiling
  - perf
  - async-profiler
  - JFR
  - CPU-usage
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 98
permalink: /technical-mastery/osy/flamegraphs-profiling/
---

## TL;DR

A flamegraph visualizes CPU profiling data as a stacked
chart: x-axis = total time spent (width = proportion of CPU),
y-axis = call stack depth. The widest blocks at the top
of a stack are the hottest functions. Flamegraphs are the
most efficient way to identify CPU bottlenecks in production
systems. For JVMs: async-profiler provides accurate flamegraphs
without safepoint bias.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-098 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | flamegraph, perf, async-profiler, CPU profiling, JFR |
| **Prerequisites** | OSY-020, OSY-065, OSY-094, OSY-097 |

---

### Reading a Flamegraph

```
ASCII representation of a flamegraph:
  
  main                                         [100%]
  ├── processRequest                            [75%]
  │   ├── parseJson                             [30%]
  │   │   └── JsonReader.read                  [28%]
  │   ├── queryDatabase                         [25%]
  │   │   ├── PreparedStatement.execute        [20%]
  │   │   └── ResultSet.next                    [5%]
  │   └── serializeResponse                    [20%]
  │       └── ObjectMapper.writeValue          [18%]
  └── garbageCollection                         [25%]
      └── G1CollectedHeap::do_collection       [25%]
  
  Reading rules:
    Width = % of time spent in this function + callees
    Top of stack = hot leaf (where CPU actually spends time)
    Tall towers = deep call stacks (not necessarily slow)
    Wide plateaus = hot paths (this is where to optimize)
    
  What to look for:
    Widest blocks at top: "hot spots" - functions consuming CPU
    Unexpected wide blocks: "why is parseJson 30% of CPU?"
    GC blocks: "25% GC = excessive allocation or wrong heap size"
```

---

### Generating Flamegraphs

```bash
# Method 1: perf + FlameGraph (Brendan Gregg's tool)
# Best for: native code, system-wide profiling

# Record:
perf record -F 99 -g -p $PID -- sleep 30
# -F 99: 99Hz sampling (not 100Hz: avoids resonance)
# -g: record call stacks
# -p $PID: specific process
# -- sleep 30: record for 30 seconds

# Generate flamegraph:
perf script | stackcollapse-perf.pl | flamegraph.pl > cpu.svg
# Download FlameGraph tools: github.com/brendangregg/FlameGraph

# View: open cpu.svg in browser
# Interactive: click to zoom, search for specific functions

# Method 2: async-profiler (for JVM - BEST for Java)
# Avoids safepoint bias (regular JVMTI profilers only sample at safepoints)
# Downloads: github.com/async-profiler/async-profiler

# CPU flamegraph for Java process:
./profiler.sh -d 30 -f cpu-flame.html $PID
# Or: profiler.sh start -e cpu -f cpu-flame.html $PID
#     profiler.sh stop $PID

# Allocation flamegraph (where is memory being allocated?):
./profiler.sh -d 30 -e alloc -f alloc-flame.html $PID

# Wall clock flamegraph (includes I/O wait):
./profiler.sh -d 30 -e wall -f wall-flame.html $PID
# Shows: what threads are doing including blocking time
# Reveals: time spent waiting for I/O, locks, sleep

# Lock contention flamegraph:
./profiler.sh -d 30 -e lock -f lock-flame.html $PID

# Method 3: JFR (Java Flight Recorder)
# Built into JDK (JDK 8u262+, JDK 11+)
jcmd $PID JFR.start duration=60s filename=flight.jfr
# Analyze: JDK Mission Control (JMC)
# or: GitHub profiler view
```

---

### Safepoint Bias - Critical for JVM Profiling

```
Problem with traditional JVMTI profilers (YourKit, JProfiler):

JVMTI profiler samples at SAFEPOINTS only:
  Safepoints: JVM can only sample threads at SafePoint locations
  SafePoint locations: method returns, loop back-edges
  But NOT: in the middle of arbitrary code
  
  Consequence: profiler CANNOT sample threads in tight loops
    that don't have safepoint polls.
    Those loops appear to not exist in the profile!
    The hottest CPU code may be INVISIBLE to safepoint-biased profiler.
    
  Example:
    double[] array = new double[1000000];
    for (int i = 0; i < array.length; i++) {
        array[i] = Math.sqrt(i * 1.5);  // HOT LOOP
    }
    // JIT compiles: tight loop with no safepoint polls
    // JVMTI profiler: cannot see this loop at all!
    
async-profiler solution:
  Uses AsyncGetCallTrace (internal JVM API):
    Can interrupt and sample thread at ANY instruction
    Not limited to safepoint locations
    Catches: tight loops, JIT-compiled hot paths
    Accurate: CPU time attributed to actual hot instruction
    
  Additionally: uses perf_events for native + kernel frames
    Shows: full stack from Java -> JNI -> native -> kernel
    Single flamegraph: Java code + GC code + syscall
    
Example: async-profiler reveals what JVMTI misses:
  
  JVMTI says: 60% in requestHandler (safepoint visible)
  async-profiler says:
    30% in Math.sqrt() in tight loop (no safepoint)
    30% in requestHandler
    20% in GC
    20% in other
  Optimization: replace Math.sqrt with integer approximation
    -> 30% CPU reduction invisible to JVMTI profiler!
```

---

### Flamegraph Patterns and Diagnoses

```
Pattern 1: Wide plateau at top of stack
  
  ___________________________________________
  |        MyService.computeHash            |  <- Wide: CPU hot
  |_____________________|___________________|
  |    handleRequest    | processPayment    |
  
  Diagnosis: computeHash() is consuming lots of CPU
  Action: optimize or cache results

Pattern 2: GC taking significant share
  
  _____________________  ___________________
  |   G1 collection   |  | application code |
  |___________________|  |__________________|
  
  If GC > 10-15% of CPU: excessive allocation
  Action: allocation flamegraph to find allocation hot spots
    ./profiler.sh -e alloc: find what's allocating most

Pattern 3: Idle frames visible
  
  In wall-clock flamegraph:
  ___________________________________________
  |          Object.wait / park             |  <- Waiting
  
  Thread waiting: I/O, lock, sleep
  In CPU flamegraph: thread not sampled (not using CPU)
  Use wall-clock mode (-e wall) to see wait time

Pattern 4: Thin, tall spikes
  
  |    |
  |    |
  | x  |
  | x  |
  Deep call stack but narrow: rarely executed deep code
  Usually: not the bottleneck; ignore unless for stack depth concerns

Pattern 5: Lots of small blocks across top
  
  | a | b | c | d | e | f | g | h |...
  Many small hot functions: well-distributed work
  No single hot spot: CPU used efficiently
  Hard to optimize further: consider algorithmic change or scale out
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Profiling always slows the application significantly" | perf sampling at 99Hz adds < 1% overhead (statistical; most samples don't interrupt). async-profiler CPU profiling: 1-5% overhead. JFR: 0.5-2% overhead (designed for production). Avoid: JVMTI instrumentation profiling (can add 50-100% overhead via bytecode injection). |
| "The widest block in a flamegraph is the slowest function" | Width = total time in function AND all its callees. A wide function may be wide because it calls many things, not because it itself is slow. Look at the TOP of wide stacks - the leaf function at the top is where CPU is actually being spent. |
| "Flamegraphs show all threads equally" | By default, perf and async-profiler sample ON-CPU threads only. I/O-waiting threads don't appear (they're not consuming CPU). Use `-e wall` in async-profiler for wall-clock (shows blocking time too). Use `-t` in perf to include all threads. |

---

### Quick Reference Card

| Task | Tool | Command |
|------|------|---------|
| JVM CPU flamegraph | async-profiler | `profiler.sh -d 30 -f out.html PID` |
| JVM allocation flamegraph | async-profiler | `profiler.sh -d 30 -e alloc -f out.html PID` |
| JVM wall-clock flamegraph | async-profiler | `profiler.sh -d 30 -e wall -f out.html PID` |
| JVM lock flamegraph | async-profiler | `profiler.sh -d 30 -e lock -f out.html PID` |
| Native CPU flamegraph | perf + FlameGraph | `perf record -F 99 -g -p PID; perf script \| ...` |
| Avoid safepoint bias | async-profiler | Uses AsyncGetCallTrace internally |
| Production safe? | JFR, async-profiler | < 2% overhead; safe in production |
