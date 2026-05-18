---
id: LNX-095
title: "Linux CPU Performance (mpstat, perf stat, flame graphs)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-062, LNX-093
used_by: LNX-093, LNX-096
related: LNX-062, LNX-093, LNX-094
tags: [cpu-performance, mpstat, perf-stat, flame-graph, ipc, cache-miss, cpu-steal, cpu-wait, cpu-frequency, numa-cpu, cpu-governor, cpupower, context-switch, cpu-hotspot, perf-top, perf-record, stackcollapse, flamegraph-pl, cpu-profiling, hardware-counter, performance-counter, pmu]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 95
permalink: /technical-mastery/lnx/linux-cpu-performance/
---

## TL;DR

CPU performance investigation flow: (1) **Is CPU saturated?** - load average
vs nproc, vmstat r column, mpstat %idle; (2) **Which process?** - pidstat -u
or top; (3) **Which code?** - perf top (live) or perf record + flame graph
(batch analysis); (4) **CPU efficiency?** - perf stat IPC (instructions per
cycle, < 0.5 = memory-bound), cache miss rate. Key gotchas: CPU steal time
(st in top/mpstat > 5% in cloud VMs = hypervisor stealing CPU), CPU wait
(%wa = blocked on I/O, not a CPU bottleneck), unbalanced CPUs (single core
pegged while others idle = single-threaded hotspot). Flame graphs: wide
plateaus at the top of the graph = code consuming the most CPU. `perf record
-ag -F 99 sleep 30` + `flamegraph.pl` = the universal CPU profiling workflow
that works for any language or runtime.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-095 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | CPU performance, mpstat, perf, flame graphs, IPC, cache miss, CPU steal, profiling |
| **Prerequisites** | LNX-062 (CPU fundamentals), LNX-093 (performance troubleshooting) |

---

### The Problem This Solves

**Problem 1**: Application uses "too much CPU" but the team doesn't know
where. Adding more CPUs (vertical scaling) helps but doesn't solve the root
cause. The expensive cloud bill grows. Without profiling: engineers guess
which function is slow and optimize randomly. With perf + flame graph: in
10 minutes, the exact function consuming 40% of CPU is identified. The fix
takes 2 hours; CPU consumption drops 35%. Cloud bill reduces by $8K/month.

**Problem 2**: A cloud VM's application has unpredictable latency spikes
every few minutes, despite CPU seeming "only 60% utilized". Dashboard shows
60% - but the 60% includes steal time. With mpstat: `%steal` = 15%. The
hypervisor is taking CPU away from the VM 15% of the time. Those steals cause
the latency spikes. Solution: move to dedicated instances (no overcommitted
CPU neighbors), or reserve capacity.

---

### Textbook Definition

**CPU Utilization vs. Saturation:**

| Metric | Meaning | Tool |
|--------|---------|------|
| `%user` + `%system` | % CPU time executing code | mpstat, top |
| `%iowait` | % time CPU idle, waiting for I/O | mpstat |
| `%steal` | % time hypervisor took this CPU | mpstat, top |
| `%nice` | % time running nice'd (low priority) processes | mpstat |
| Load average | Avg runnable + uninterruptible sleep tasks | uptime |
| Run queue | Count of processes waiting for CPU right now | vmstat r |

**CPU performance hierarchy:**
```
fastest: register operations (0 cycles)
       | L1 cache hit (4 cycles, 0.5ns)
       | L2 cache hit (12 cycles, 3ns)
       | L3 cache hit (40 cycles, 10ns)
       | RAM access (200 cycles, 50ns)
       | disk SSD random read (100,000+ cycles)
slowest
```

---

### Understand It in 30 Seconds

```bash
# === mpstat: per-CPU breakdown ===

# All CPUs, 1-second interval, 5 samples:
mpstat -P ALL 1 5
# CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %idle
# all    45.3    0.0     8.2    2.5      0.1     0.3    0.0    43.6
#   0    92.5    0.0    7.5    0.0      0.0     0.0    0.0     0.0
#   1     3.2    0.0    1.0    0.5      0.0     0.0    0.0    95.3
#   2     4.1    0.0    1.5    0.0      0.0     0.0    0.0    94.4
#   3     3.1    0.0    2.0    0.0      0.0     0.0    0.0    94.9
#
# ANALYSIS:
# CPU 0: 100% busy - single-threaded hotspot on core 0!
# CPUs 1-3: nearly idle - process isn't using multiple cores
# %iowait: blocked waiting for I/O (not a CPU bottleneck)
# %steal: hypervisor stealing CPU (0.0 here - good)

# Identify the single-threaded process:
pidstat 1 1
# PID    %usr  %system  %wait   %CPU  Command
# 9876   88.2    5.8     0.0    94.0  myapp
# PID 9876 using 94% of one CPU (maxing out CPU 0)

# === perf stat: CPU efficiency metrics ===
# Profile the process for 30 seconds:
perf stat -p 9876 sleep 30
# Performance counter stats for process '9876':
#     29,876,543,210 cycles              # 0.995 GHz
#     11,456,789,012 instructions        # 0.38 insn per cycle
#      3,456,789,012 cache-references
#        567,890,123 cache-misses        # 16.43% of all cache refs
#         12,345,678 context-switches
#
# IPC = 0.38: POOR! (< 0.5 = memory-bound application)
# cache-miss rate 16.43%: high! (< 1% is good, > 5% = concern)
# Conclusion: application is memory-bound (waiting on RAM)
# Fix: improve data locality, use cache-friendly data structures

# Compare to well-optimized code:
# instructions per cycle: 2.5+ (IPC > 2 = compute-bound, well-optimized)
# cache-miss rate: < 0.5%

# Interesting hardware counters:
perf stat -e cycles,instructions,cache-misses,cache-references,\
branch-misses,branch-instructions,cpu-clock -p 9876 sleep 10
# branch-misses / branch-instructions = branch misprediction rate
# High (>3%): branch predictor struggling (unpredictable code paths)

# === perf top: live CPU hotspot ===
perf top
# Samples: 34K of event 'cycles', 4000 Hz, lost: 0/0 drop: 0/0
# Overhead  Shared Object     Symbol
#    78.2%  myapp             [.] processRecord
#     5.3%  libc.so.6         [.] strcmp
#     3.2%  [kernel]          [k] copy_user_generic_unrolled
#
# processRecord consuming 78%! That's the hotspot.
# Drilldown: press 'a' on processRecord to see annotated assembly

# === perf record + flame graph: batch profiling ===

# Record for 30 seconds (all CPUs, call graphs, 99Hz):
perf record -ag -F 99 -p 9876 -- sleep 30
# ^ -a: all CPUs, -g: call graph (stack traces), -F 99: 99 Hz sample rate

# For Java (JVM JIT-compiled code): use async-profiler instead:
# ./profiler.sh -d 30 -f flamegraph.html 9876

# Generate flame graph:
perf script | stackcollapse-perf.pl | flamegraph.pl > cpu.svg

# View: open cpu.svg in browser
# Wide plateaus at TOP = hot code (most CPU time spent here)
# Tall narrow spikes = deep call stacks (common, not necessarily hot)

# Quick check: what functions are hot?
perf report --stdio --no-children -i perf.data | head -30

# === CPU steal time: cloud-specific issue ===
# Check steal time in top:
top
# %Cpu(s): 45.3 us, 8.2 sy, 0.0 ni, 44.0 id,  2.5 wa, 0.0 hi, 0.0 si, 0.0 st
#                                                                             ^^ steal!

# For sustained steal monitoring:
mpstat -P ALL 5 | awk '{print $1, "CPU:", $2, "steal:", $9}'

# If steal > 5%: hypervisor is overcommitting CPU on this host
# Fix options:
# 1. Move to Reserved/Dedicated instances (no CPU sharing)
# 2. Move workload to a less-loaded host
# 3. Contact cloud provider to move VM to less-loaded physical host

# === CPU frequency and scaling ===
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
# 1800000  (1.8 GHz - throttled from max 3.5 GHz!)

cpupower frequency-info
# current CPU frequency: 1.80 GHz
# CPU throttling detected! cpuinfo_cur_freq < base frequency
# Cause: thermal throttling (CPU too hot) or power management

# Check thermal throttling:
cat /sys/class/thermal/thermal_zone*/temp
# 89000 (89 degrees C! dangerously hot, near throttle threshold)

# CPU governor:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# powersave  <- use 'performance' for latency-sensitive workloads
# Set all CPUs to performance governor:
cpupower frequency-set -g performance
```

---

### First Principles

```
CPU performance fundamentals:

Modern CPU execution pipeline:
  Fetch -> Decode -> Issue -> Execute -> Writeback
  
  Instructions Per Cycle (IPC):
    Ideal: 4+ instructions per cycle (superscalar, out-of-order)
    Compute-bound code: 2-4 IPC (ALU operations, registers)
    Memory-bound code: 0.1-0.5 IPC (waiting for memory loads)
    
    Why IPC matters: clock speed (GHz) * IPC = real throughput
    3.5 GHz * IPC 2.5 = 8.75 GIPS (billions of instructions/second)
    3.5 GHz * IPC 0.3 = 1.05 GIPS (same clock, 8x slower throughput)
    
    Poor IPC causes: cache misses (CPU stalls waiting for memory),
    branch mispredictions (pipeline flushed), data dependencies
    (instruction B needs A's result, must wait)

Cache hierarchy and performance:
  L1 cache: 32-64KB, ~4 cycles, per-core
  L2 cache: 256KB-1MB, ~12 cycles, per-core
  L3 cache: 6-32MB, ~40 cycles, shared across cores
  RAM: 16-256GB, ~200 cycles, shared
  
  Cache line: 64 bytes - minimum unit of cache transfer
  
  Cache-friendly code:
    Access data sequentially (array[0], [1], [2]...)
    Prefetcher loads next cache lines automatically
    Each cache line used fully (spatial locality)
    
  Cache-unfriendly code (pointer chasing):
    linked_list->next->next->next->data
    Each pointer dereference: random memory location
    Cache miss ~200 cycles: 1000 pointer chases = 200,000 cycles
    vs array access: cache hit ~4 cycles

CPU saturation mechanics:
  Run queue = list of processes waiting to be scheduled
  nproc CPUs can run nproc processes simultaneously
  
  If runnable > nproc: SATURATION
    Each runnable process waits for CPU turn
    Scheduling interval (Linux default: 1ms-20ms per-task quantum)
    With 10 runnable processes on 4 CPUs: each waits 2.5x
    Latency multiplier: 2.5x for any operation requiring CPU
    
  load average: exponentially weighted moving average of
    (runnable processes + uninterruptible sleep processes)
    1-min, 5-min, 15-min windows
    
  load / nproc:
    < 0.7: underloaded (healthy)
    0.7-1.0: lightly loaded
    1.0: fully loaded (each CPU has work, no queue)
    > 1.0: overloaded (processes waiting for CPU)
    > 2.0: significantly overloaded

CPU steal time in virtualization:
  Type 1 hypervisor (KVM, VMware ESXi): runs directly on hardware
  VMs share physical CPUs via scheduler in hypervisor
  
  When hypervisor needs to run another VM (or hypervisor tasks):
    Stops current VM's virtual CPU
    VM "loses" CPU time
    This appears as %steal in mpstat
    
  Effect on application:
    vm.scheduler.timer fires -> VM wants CPU
    Hypervisor is busy -> VM waits
    VM gets CPU back -> sees elapsed wall clock time
    Application: timer fired "later than expected"
    jitter, unpredictable latency, missed deadlines
    
  Mitigation:
    Reserved instances: hypervisor reserves capacity for this VM
    Dedicated hosts: no sharing at all
    Cloud-native metrics: some clouds provide hypervisor-level metrics
    
  Detection:
    %steal > 1%: light contention, may be acceptable
    %steal > 5%: moderate contention, monitor closely
    %steal > 10%: significant contention, action needed

perf subsystem and sampling:
  Hardware PMU (Performance Monitoring Unit): per-core counters
  perf_event_open() syscall: configure PMU events
  
  Sampling (perf record -F 99):
    PMU interrupts 99 times per second (99 Hz avoids aliasing)
    At each interrupt: capture current instruction pointer
    With -g (call graphs): capture entire call stack
    After 30 seconds: ~3000 samples per CPU
    
  Stack capture methods (with -g):
    frame pointer: fast, requires -fno-omit-frame-pointer compile flag
    DWARF: accurate but slow, requires debug info
    LBR (Last Branch Record): hardware-assisted, limited depth
    ORC (kernel): optimized for kernel code
  
  Flame graph rendering:
    stackcollapse-perf.pl: normalizes perf script output
    flamegraph.pl: renders SVG with colors, widths
    Width = % of total samples = % CPU time
    Color: random (doesn't mean anything in default flamegraph)
```

---

### Thought Experiment

Profiling a Go web service with high CPU:

```bash
# Service: 20 instances of a Go HTTP server
# Problem: CPU 85% across all instances under 10K RPS
# Expected: should handle 50K RPS at this CPU level

# Step 1: Confirm CPU is the bottleneck
mpstat -P ALL 1 3
# All CPUs: 85% usr, 5% sys, 0% steal, 0% iowait
# Confirmed: CPU saturated, no other bottleneck

# Step 2: Identify which function
# Option A: perf top (live, 30 seconds):
perf top -p $(pgrep myservice)
# Overhead   Symbol
#  45.2%  [.] encoding/json.Marshal
#  23.1%  [.] runtime.mallocgc
#  10.3%  [.] compress/gzip.(*Writer).Write
#   5.4%  [.] net/http.(*Transport).roundTrip
#
# JSON marshaling uses 45%! That's the hotspot.

# Option B: Go's built-in pprof (better for Go):
# Import "net/http/pprof" in main.go (debug endpoint)
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
go tool pprof -http=:8080 cpu.prof
# Visual flame graph in browser, Go-specific (resolves goroutines)

# Step 3: perf stat for efficiency
perf stat -p $(pgrep myservice) sleep 10
# IPC: 1.2 (acceptable for Go GC overhead)
# cache-miss: 4.5% (moderate - JSON parsing has poor locality)

# Diagnosis: JSON marshaling is the bottleneck
# Options:
# 1. Use faster JSON library (sonic, easyjson, encoding/json/v2)
# 2. Use binary serialization (protobuf, msgpack) - 5-10x faster
# 3. Cache pre-marshaled responses where data is stable
# 4. Reduce JSON payload size (return only needed fields)

# Result: switching to sonic JSON library: 
# CPU drops from 85% to 50% at same RPS
# Or: handle 70% more traffic at same CPU level
```

---

### Mental Model / Analogy

```
CPU = office workers at desks

nproc = number of desks (4 CPUs = 4 workers working simultaneously)
runnable queue = stack of tasks on each worker's in-tray
load average = average depth of in-tray over time
load 1.0 on 4 CPUs = each worker has exactly 1 task at a time

%usr = time workers spend actually doing client work
%sys = time workers spend filing paperwork (kernel work)
%iowait = workers sitting idle, waiting for printer/fax (I/O device)
           (doesn't use CPU, but CPU can't be used for other tasks)
           Misleading: workers appear "busy" (at desk) but not working

%steal = manager randomly interrupts workers to do a different
         company's work (hypervisor VM timeslicing)
         "I need your desk for 15 minutes" -> your work stalls

IPC (Instructions Per Cycle) = worker's actual output per hour
  IPC 3.0 = skilled fast worker (4 tasks per hour)
  IPC 0.3 = worker constantly waiting for information from storage room
            (cache misses = worker stalled waiting for files)

Cache hit/miss:
  L1 cache = sticky notes on desk (immediate, microseconds)
  L2 cache = drawer under desk (seconds to retrieve)
  L3 cache = filing cabinet nearby (minute to retrieve)
  RAM = office storage room down the hall (several minutes)
  
  Cache-friendly code = worker needs files in order,
    all in the same folder (sequential access)
    = grabs whole folder, uses all files quickly
  
  Cache-unfriendly code (pointer chasing) = worker needs:
    file A says "go to folder B"
    folder B says "find box C"
    box C says "open drawer D"
    = each step requires a trip to storage room (RAM)
    = 1000 trips instead of 1 trip with the whole folder

Flame graph = heat map of where workers spend their time:
  Wide plateau = lots of time spent here (hot code path)
  Tall narrow spike = deep call chain (many functions but quick)
  The TOP of each stack = where CPU time is consumed
  The BOTTOM = which higher-level operation invoked the hot code
  
  Reading a flame graph:
    Look for the widest blocks at the TOP
    "processRequest (45% wide) -> parseJSON (45% wide)"
    = parseJSON is called by processRequest, consuming 45% of CPU
```

---

### Gradual Depth - Five Levels

**Level 1:**
CPU utilization from `top` (%Cpu(s): us, sy, id, wa). Load average meaning
vs CPU count. What %iowait means (CPU idle but process blocked on I/O).
`mpstat -P ALL` for per-CPU breakdown. Identifying a single-threaded hotspot
(one CPU at 100%, others idle).

**Level 2:**
`perf top` for live CPU hotspot identification. `pidstat 1` for per-process
CPU. `perf stat` basic output: cycles, instructions, IPC. Understanding
%steal in cloud VMs. CPU governor: powersave vs performance. Context switch
rate: `vmstat` cs column.

**Level 3:**
`perf record -ag -F 99` and flame graph generation. IPC interpretation:
compute-bound (> 2) vs memory-bound (< 0.5). Cache miss rate analysis.
branch misprediction rate. NUMA CPU effects: `numactl`, `taskset` for
process pinning. `cpupower` for frequency info. Thermal throttling detection.

**Level 4:**
Off-CPU flame graphs: `offcputime-bpfcc` for time spent blocked (scheduler,
I/O, lock). `perf c2c` for cache-line contention (false sharing between
threads). `runqlat-bpfcc`: scheduler latency histogram. `perf sched`: detailed
scheduler analysis. Hardware performance counter deep dive: PMU events,
`perf list` for available counters. CPU frequency scaling effects: perf stat
shows actual vs base frequency.

**Level 5:**
CPU microarchitecture analysis: TMAM (Top-Down Microarchitecture Analysis
Method) using `perf stat --topdown` - identifies if bottleneck is Front End
(instruction fetch), Back End (execution units), Memory Bound, or Core Bound.
TLB miss analysis: `perf stat -e dTLB-load-misses,iTLB-load-misses`. CPU
prefetcher: `__builtin_prefetch()`, `_mm_prefetch()` for manual prefetch
hints. SIMD vectorization profiling: `perf stat -e fp_arith_inst_retired.256b_packed_double`.
Linux CFS (Completely Fair Scheduler) internals: cfs_rq, vruntime, sched_latency_ns.
Realtime scheduling: `SCHED_FIFO`, `SCHED_RR` priority vs CFS fairness.

---

### Code Example

**BAD - CPU hotspot from cache-unfriendly access pattern:**
```c
// BAD: linked list traversal (cache-unfriendly pointer chasing)
struct Node {
    int value;
    struct Node* next;   // pointer to anywhere in heap!
};

int sum_list(struct Node* head) {
    int sum = 0;
    // Each iteration: random memory access (cache miss)
    // 1000 nodes = 1000 cache misses = ~200,000 cycles
    while (head != NULL) {
        sum += head->value;       // cache miss: random location
        head = head->next;        // cache miss: another random location
    }
    return sum;
}
// perf stat: IPC 0.1 (terrible), cache-miss-rate 40%+
// 1M node list traversal: ~100ms on modern hardware
```

```c
// GOOD: array-based (cache-friendly sequential access)
int sum_array(int* arr, int n) {
    int sum = 0;
    // Each cache line (64 bytes) holds 16 ints
    // Sequential access: prefetcher loads next cache line automatically
    // 1000 ints = 63 cache misses (1 per cache line) = ~2500 cycles
    for (int i = 0; i < n; i++) {
        sum += arr[i];           // likely cache hit: sequential
    }
    return sum;
}
// perf stat: IPC 3.0 (excellent), cache-miss-rate < 0.1%
// 1M element array traversal: ~1ms on modern hardware
// 100x faster than linked list for same operation!

// When linked list is unavoidable: slab allocator for locality
// All nodes allocated from same memory pool = better locality
```

**GOOD - profiling and optimization workflow:**
```bash
# Profile: find the hotspot
perf record -ag -F 99 -p $SERVICE_PID -- sleep 30
perf report --stdio --no-children 2>/dev/null | \
    awk '/[0-9]+\.[0-9]+%/{print}' | head -20
# Output:
#  45.23%  libssl.so     TLS_method
#  23.45%  libc.so       malloc
#  15.67%  myapp         processRequest

# Annotate TLS_method assembly (see which instruction is hot):
perf annotate --stdio TLS_method | head -30
# TLS_method assembly with per-instruction heat:
# 35.23  sha256_update:   movaps  %xmm0, (%rsi)  <- hot!
# This instruction is 35% of all TLS time

# perf stat for efficiency baseline:
perf stat -e cycles,instructions,cache-misses,\
cache-references -p $SERVICE_PID sleep 10

# If TLS is the hotspot and cache miss rate is high:
# Option 1: TLS session resumption (avoid repeated key exchange)
# Option 2: ECDSA certificates (faster than RSA)
# Option 3: AES-NI hardware acceleration (check: grep aes /proc/cpuinfo)

# After optimization: compare perf stat
# Before: IPC 0.3, cache-miss 15%
# After: IPC 1.8, cache-miss 2%
# Result: 6x improvement in CPU efficiency
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "High %iowait means CPU is the bottleneck" | `%iowait` is time the CPU is IDLE (not executing) while at least one process is blocked on I/O. The CPU is NOT busy - it could run other processes if they were available. High iowait means the DISK (or network) is the bottleneck, not CPU. If load average is low but %iowait is high: your service is I/O bound. The fix is faster storage, better caching, or reducing I/O operations. NOT adding more CPUs. Adding CPUs when %iowait is high = buying more cars when the highway (I/O) is congested - they'll all idle waiting for the bottleneck. |
| "Reducing CPU usage always improves performance" | CPU usage is a RESOURCE, not a bottleneck indicator in isolation. A service using 90% CPU while completing 10,000 requests/second with 5ms latency is performing perfectly. Reducing CPU "optimization" might mean: handling fewer requests, adding caching (trading CPU for memory), or replacing fast in-memory computation with slower I/O. The goal is efficient throughput at acceptable latency, not minimizing CPU usage. CPU becomes a bottleneck only when: (a) all CPUs are saturated AND latency increases, OR (b) CPU saturation causes CPU steal (cloud neighbors) or thermal throttling. |
| "perf top shows the bottleneck function" | `perf top` shows which FUNCTION'S code is executing when the CPU is sampled. A function at 40% in perf top means 40% of CPU time is spent INSIDE that function's instructions. But it doesn't tell you: WHY it's running that long. Cause could be: (a) function is called 1M times (frequency issue), (b) function is called 1 time but takes forever (algorithmic issue), (c) function has poor cache behavior (performance issue). After identifying the hot function with perf top: use perf annotate to see which specific instruction is hot; use call graph (`perf top -g`) to see which code paths call this function. The function is a SYMPTOM; the root cause requires deeper investigation. |
| "Higher CPU clock speed always means better performance" | Modern CPUs frequently throttle clock speed: (a) thermal: if CPU exceeds ~90C, frequency drops to prevent damage; (b) power: sustained workload may trigger power limits reducing frequency; (c) turbo boost: short bursts above base frequency allowed; (d) C-states: sleep states for idle CPUs take time to wake up. A CPU running at base 2.4 GHz consistently may outperform one nominally rated at 3.5 GHz but thermally throttled to 1.8 GHz. Check actual frequency with `cpupower frequency-info` or `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`. For latency-sensitive workloads: disable C-states and use `performance` governor to maintain consistent frequency. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: unexplained CPU spikes ===

# Check: is it periodic? (cron job, GC, connection pool, etc.)
# Record CPU every second for 5 minutes:
sar -u 1 300 > cpu_samples.txt
# Look for periodic spikes at regular intervals

# Identify the culprit during a spike:
watch -n 0.5 'ps aux --sort=-%cpu | head -10'
# or: use pidstat for continuous monitoring
pidstat 1 60 | sort -k8 -rn | head -10

# === Failure: JVM CPU profiling (Java) ===
# Standard perf doesn't work well with JIT-compiled code
# Java JIT: functions compiled at runtime, no ELF symbols
# perf sees: "Lfoo+0x1234" or "Unknown" instead of method names

# Solution: async-profiler (handles JVM correctly)
wget https://github.com/jvm-profiling-tools/.../profiler.sh
./profiler.sh -d 30 -f flamegraph.html $JAVA_PID
# Opens flame graph with real Java method names

# Or: enable perf-map-agent for JVM symbol mapping:
# -agentpath:/path/to/libperf-map-agent.so
# Then perf record + flamegraph works normally

# === Failure: CPU bound but IPC is high ===
# IPC 2.5+ but still CPU saturated at 95%
perf stat -p $PID sleep 10
# instructions: 50,000,000,000 # 2.5 per cycle
# This code IS efficient - problem is workload volume

# Options:
# 1. Horizontal scale: more instances
# 2. Algorithm change: O(n^2) -> O(n log n)
# 3. Hardware upgrade: more cores, faster clock
# 4. Caching: reduce repeated computation

# === Failure: branch misprediction ===
perf stat -e branch-misses,branch-instructions -p $PID sleep 10
# branch-misses: 456,789,012
# branch-instructions: 5,678,901,234
# Misprediction rate: 8.05% (high! > 3% is concerning)

# Common cause: sorting or binary search on unsorted data
# Fix: sort input data before processing (predictable branches)
# Or: use branchless code (ternary operator, SIMD predicate)

# Example: replace unpredictable branch with branchless:
# BAD (unpredictable branch based on data):
# if (arr[i] > threshold) result += arr[i];

# GOOD (branchless, predictable):
# result += arr[i] * (arr[i] > threshold);  // branchless
# Compiler may auto-vectorize with SIMD
```

---

### Related Keywords

**Foundational:**
LNX-062 (CPU fundamentals), LNX-093 (USE method)

**Builds on this:**
LNX-096 (kernel crash analysis)

**Related:**
LNX-094 (memory pressure), LNX-088 (disk performance)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `mpstat -P ALL 1` | Per-CPU utilization (check steal, wait) |
| `pidstat 1` | Per-process CPU usage |
| `perf top -p PID` | Live CPU hotspot |
| `perf stat -p PID sleep 10` | CPU efficiency (IPC, cache miss) |
| `perf record -ag -F 99 -p PID -- sleep 30` | Record for flame graph |
| `cpupower frequency-info` | CPU frequency and governor |
| `sar -u 1` | CPU utilization over time |

**3 things to remember:**
1. %steal > 5% in a cloud VM = hypervisor taking your CPU - migrate to reserved instances or dedicated hosts
2. IPC (instructions per cycle) from `perf stat`: < 0.5 = memory-bound (fix: data structures), > 2.0 = compute-bound (fix: algorithm or scale out)
3. Flame graph: wide plateaus at the TOP show hotspot functions; perf record -ag -F 99 + flamegraph.pl is universal for any language

---

### Transferable Wisdom

CPU profiling with perf and flame graphs is universal and transferable across
any language: Java (with async-profiler), Python (py-spy), Go (pprof), Rust
(same perf), Node.js (v8-profiler or pprof). The IPC (Instructions Per Cycle)
metric maps to: application throughput efficiency, JVM IPC (JIT quality),
database query execution efficiency (index scan vs full table scan), query
planner quality. Cache miss analysis transfers to: database buffer pool miss
rate (RAM cache vs disk), Redis cache miss rate (Redis vs database), CDN miss
rate (CDN vs origin). The branch misprediction concept maps to: speculative
execution in microservices (pre-fetch data based on likely request type),
database query planner statistics (cardinality estimates for branch choices),
JVM JIT compiler deoptimization (JIT compiles based on observed branches,
deoptimizes if behavior changes). CPU steal time's impact (unpredictable
latency) is conceptually the same as: "noisy neighbor" in shared databases
(one tenant's heavy query degrades others), AWS DynamoDB partition hot keys,
Redis single-threaded command blocking.

---

### The Surprising Truth

The flame graph visualization was invented by Brendan Gregg in 2011 at Sun
Microsystems while investigating a MySQL performance problem. Before flame
graphs: profilers produced tables of function names and percentages. Engineers
had to manually trace call hierarchies. With a 100-function profile output:
nearly impossible to find the root call chain. Flame graphs transformed this
into an immediate visual insight - the hottest code paths are the widest
plateaus. The underlying data was always there (perf stack sampling existed);
the breakthrough was purely the visualization. The name "flame graph" comes
from the orange/red color scheme that looks like fire when stack depth and
heat are combined visually.

The `perf` tool in Linux was originally added in 2009 (Linux 2.6.31) as a
single command that replaced dozens of separate performance counter tools.
It access the same hardware Performance Monitoring Unit (PMU) counters that
Intel's VTune Amplifier uses - but `perf` is free, open-source, and included
in every Linux distribution. Many engineers don't realize that the same hardware
performance analysis capability that enterprise tools sell for thousands of
dollars is already available via `perf` on every Linux system.

---

### Mastery Checklist

- [ ] Can interpret mpstat per-CPU output and identify single-threaded hotspots, steal time, and iowait
- [ ] Can use perf top to identify hot functions in a running process
- [ ] Can generate a flame graph using perf record and explain how to read it
- [ ] Understands IPC from perf stat: what < 0.5 means (memory-bound) vs > 2.0 (compute-bound)
- [ ] Can explain CPU steal time and its impact on VM performance

---

### Think About This

1. A high-frequency trading system requires consistent sub-millisecond response
   times. The engineers notice occasional 5ms latency spikes. Using your
   knowledge of CPU performance metrics: describe four different CPU-related
   causes of these spikes (not disk, not network) and what metrics you would
   check to identify each. For each cause: describe the fix and any trade-offs
   involved.

2. Your team has a Go microservice running on 4-core VMs that peaks at 80% CPU
   at 5K RPS. `perf stat` shows IPC = 0.35 and cache-miss-rate = 22%. A flame
   graph shows: 50% of CPU in JSON marshal/unmarshal, 20% in runtime.mallocgc
   (garbage collection). Design an optimization plan: which of these should
   you tackle first? What is the root cause of the high cache miss rate? What
   specific code changes would address each bottleneck?

3. Explain how a CPU flame graph captures the difference between a function
   that is "hot" because it is called 10 million times (each call is fast) vs
   a function that is "hot" because it is called 100 times but each call takes
   1ms. Given the same flame graph, how would you distinguish between these two
   cases? What additional profiling data would you collect to determine the
   right optimization approach for each?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you diagnose a CPU performance problem in Linux from first principles?
A: CPU DIAGNOSIS SEQUENCE: (1) IS CPU SATURATED? - `uptime` load average vs nproc. `vmstat 1`: r column > nproc = runnable processes waiting for CPU. If not saturated but slow: look elsewhere (memory, disk, network). (2) PER-CPU BREAKDOWN: `mpstat -P ALL 1`. Diagnose: - All CPUs high: distributed workload, normal scaling. - Single CPU at 100%, others idle: single-threaded bottleneck. - %steal > 5%: hypervisor taking CPU from VM (cloud issue). - %iowait high: disk I/O bottleneck, NOT CPU (CPU is idle, waiting for I/O). (3) WHICH PROCESS? `pidstat 1` sorted by %CPU. Alternatively: `top`, sort by CPU, press 'H' to show threads. (4) WHICH FUNCTION? - `perf top -p PID`: live view of hot functions (works for native code). - For JVM: async-profiler `./profiler.sh -d 30 -f out.html PID`. - `ps aux | grep PID` to confirm process is still running. (5) CPU EFFICIENCY ANALYSIS: `perf stat -p PID sleep 10`. Key metrics: IPC (instructions per cycle) - if < 0.5: memory-bound (cache misses causing stalls), fix: data structure locality. If > 2.0: compute-bound, efficient. Cache miss rate: > 5% is concerning. Branch misprediction rate: > 3% is concerning. (6) DEEP PROFILING: `perf record -ag -F 99 -p PID -- sleep 30`. Then: `perf script | stackcollapse-perf.pl | flamegraph.pl > cpu.svg`. Open SVG: wide plateaus at top = hotspot. COMMON FINDINGS IN ORDER OF FREQUENCY: (a) single-threaded bottleneck (scale: parallelize), (b) memory-bound due to cache-unfriendly access (fix: restructure data), (c) CPU steal in cloud VM (fix: reserved instances), (d) serialization/parsing overhead (fix: faster library or binary format), (e) lock contention (fix: reduce critical section or use lock-free).

**Expert:**
Q: Explain CPU steal time and why it causes unpredictable latency in cloud VMs, beyond just "lower throughput."
A: CPU STEAL MECHANICS: In a cloud environment with KVM/Xen/VMware hypervisors: physical CPU cores are shared among multiple VMs. The hypervisor runs a scheduler that gives each VM a time slice (typically 1-50ms). When a VM's time slice expires: hypervisor stops it and schedules another VM. When the stopped VM resumes: it sees wall clock time has advanced without it executing. In `/proc/stat` (read by mpstat): steal time = "time my virtual CPU was ready to run but the hypervisor didn't give it physical CPU." WHY IT CAUSES UNPREDICTABLE LATENCY: Scenario 1 - Timer-based operations: Java application has a timer that fires every 10ms to send a heartbeat. Timer is implemented with clock_gettime() + nanosleep(). If hypervisor steals 8ms during this window: nanosleep(10ms) actually sleeps for 18ms (10ms intent + 8ms steal). Heartbeat arrives late. Downstream sees missed heartbeat -> timeout -> failover. Scenario 2 - Lock acquisition: Thread A holds a mutex, then gets stolen by hypervisor for 20ms. Thread B is spinning waiting for the mutex. Thread B burns CPU cycles spinning on a lock for 20ms - but the VM's steal time isn't visible in the mutex contention metrics. From Thread B's perspective: the lock holder just disappeared. This is called "lock holder preemption" - the critical section took 20ms because the holder was stolen. Scenario 3 - GC pauses: JVM GC needs to stop-the-world. One GC thread gets stolen. GC pause extends by steal duration. Application sees longer-than-configured GC pause. METRICS: mpstat %steal over time. In cloud: use provider-level metrics: AWS: CPUStealTimeDelta in enhanced monitoring. GCP: cpu/steal_time metric. MITIGATIONS: Reserved instances (AWS): hypervisor reserves CPU capacity - no overbooking. CPU pinning (bare metal): dedicated pCPUs mapped to vCPUs (lowest latency). Realtime priority (SCHED_FIFO): within the VM, give the application highest scheduling priority - reduces WITHIN-VM scheduling jitter (doesn't help hypervisor steal). Spread instances across different physical hosts: reduced probability of burst steal from noisy neighbors. IMPLICATION FOR LATENCY SLOs: p99 latency targets need steal time margin: if steal can add 10ms, your p99 SLO must accommodate 10ms jitter even with no code bottlenecks.
