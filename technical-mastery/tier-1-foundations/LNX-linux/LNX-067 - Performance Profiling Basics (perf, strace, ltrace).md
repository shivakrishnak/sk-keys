---
id: LNX-067
title: "Performance Profiling Basics (perf, strace, ltrace)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-006, LNX-011
used_by: LNX-087, LNX-095
related: LNX-011, LNX-093, LNX-087
tags: [perf, strace, ltrace, profiling, performance, flame-graph, CPU-counters, system-calls, PMU]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/lnx/performance-profiling-basics/
---

## TL;DR

Linux performance profiling toolkit: **strace** (which syscalls, with args,
how long), **ltrace** (which library calls), **perf stat** (CPU hardware
counters: instructions, cache-misses, branch-misses), **perf record + report**
(sampling profiler: flame graphs). strace: `strace -p PID` or `strace -c cmd`
for syscall summary. perf: `perf stat cmd` (one-shot), `perf record -g cmd`
+ `perf report` (profile). `perf top` for live CPU hotspots. `strace` has
~10-100x overhead; `perf` has ~1-5%. Use strace for "what is this process
DOING?", perf for "WHERE is CPU time going?".

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-067 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | perf, strace, ltrace, profiling, flame graph, CPU counters, syscall tracing, PMU |
| **Prerequisites** | LNX-006 (Processes), LNX-011 (System Monitoring) |

---

### The Problem This Solves

**Problem 1**: An application is "slow" but you don't know why. Is it
CPU-bound? I/O-bound? Making too many syscalls? `strace -c cmd` in 5 seconds
reveals: 90% of time is in `read()` syscalls on a single file - the app
is making millions of tiny read() calls instead of buffered reads. Fix:
increase read buffer size. Diagnosis took 5 minutes, fix is one parameter.

**Problem 2**: A Java service is consuming 100% CPU but thread dumps show
no obviously hot threads. `perf top -p PID` shows the CPU is inside the
JVM's JIT-compiled code for a specific method. `perf record -g -p PID` +
`perf report` shows a flame graph where `HashMap.get()` appears at 60%
of CPU time - an O(n) operation in a hot loop due to hashCode() collisions.
This is invisible to application profilers (which look at Java stack frames,
not JIT assembly).

---

### Textbook Definition

**strace**: System call tracer. Uses the `ptrace()` syscall to intercept
every system call a process makes. Shows: syscall name, arguments, return
value, and time taken. Overhead: significant (~10-100x slowdown due to
ptrace interrupting execution for every syscall). Use: debugging (what is
this program doing?), not production profiling.

**ltrace**: Library call tracer. Similar to strace but traces dynamic
library function calls (`printf`, `malloc`, etc.) rather than syscalls.
Uses LD_PRELOAD or breakpoints at library entry points.

**perf**: Linux Performance Events subsystem. Uses hardware performance
counters (PMU - Performance Monitoring Unit) in the CPU to count events
(instructions, cache misses, branch mispredictions) with near-zero overhead.
Can also do statistical sampling (perf record): periodically interrupts
the process and records the instruction pointer -> builds a histogram of
"where was the CPU?" -> flame graph.

**Flame graph**: Visualization of profiling data. X-axis = relative time
spent. Y-axis = call stack depth. Width of each bar = time spent in that
function (including callees). Invented by Brendan Gregg. Identifies hot
paths ("flames") visually in seconds.

---

### Understand It in 30 Seconds

```bash
# === strace: trace syscalls ===

# Trace a running process:
strace -p 12345
# Output: read(3, "", 4096) = 0 (repeated thousands of times - too small reads!)

# Run a command and trace it:
strace ls /tmp 2>&1 | head -30
# execve, open, stat, getdents, etc.

# Summary: count syscalls and time spent in each:
strace -c ls /tmp 2>&1
# % time     seconds  usecs/call     calls    errors syscall
# -------  ----------  ----------  --------  ------- ------
#  35.42   0.000148         10        14           7 newfstatat
#  29.90   0.000125         15         8           1 openat
#  19.71   0.000082         27         3             getdents64
# Key: if one syscall dominates %, it's worth investigating

# Filter: only trace network syscalls:
strace -e trace=network curl https://example.com 2>&1
# connect, sendto, recvfrom, etc.

# Filter: only trace file I/O:
strace -e trace=file ls /tmp 2>&1

# Follow children (important for forking servers):
strace -f -p 12345

# Show timing for each syscall (timestamp):
strace -T ls /tmp 2>&1
# <time> at end of each line

# === ltrace: trace library calls ===
ltrace ls /tmp 2>&1 | head -20
# malloc(272) = 0x...
# setlocale(LC_ALL, "") = ...
# Shows which library functions are called

# === perf stat: hardware performance counters ===

# One-shot performance stats:
perf stat ls /tmp
# Output:
# 1,234,567  instructions          #  2.34 insns per cycle
#   567,890  cache-references
#    12,345  cache-misses          #  2.18% of all cache refs
# 45,678     branch-misses         #  1.56% of all branches
# 0.003 seconds time elapsed

# High cache-miss %: memory access pattern problem
# Low IPC (instructions per cycle): stalled pipeline
# High branch-misses: unpredictable conditional branches

# Stat a running process:
perf stat -p 12345 sleep 5   # sample for 5 seconds

# === perf record + report: sampling profiler ===

# Profile a command (-g = callgraph/stack traces):
perf record -g ./myapp
# records to perf.data

# Interactive report (shows call hierarchy, hottest functions):
perf report
# Press / to search, use arrow keys to navigate call tree

# Profile a running process for 10 seconds:
perf record -g -p 12345 sleep 10

# Text-mode report (for scripting/CI):
perf report --stdio 2>/dev/null | head -30

# === perf top: live CPU profiling ===
perf top          # system-wide live profiling
perf top -p PID   # for specific process only
# Shows: function name, % CPU time, module
# Updates every ~2 seconds
# Great for: "what is this server doing right now?"

# === Generating flame graphs ===
# Install flamegraph tools:
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph

# Capture perf data:
perf record -F 99 -g -p $PID sleep 30   # 99 samples/sec, 30 seconds

# Convert to flame graph:
perf script | ./stackcollapse-perf.pl | ./flamegraph.pl > flame.svg
# Open flame.svg in browser: hover over bars to see stack, click to zoom
```

---

### First Principles

**How strace works (ptrace mechanism):**
```
Process A (target):
  Running normally...
  
strace starts:
  Calls ptrace(PTRACE_ATTACH, pid_of_A)
  Sends SIGSTOP to A -> A pauses
  
For each system call A makes:
  When A calls read():
    Kernel: is ptrace watching? YES
    Kernel: STOP A, notify strace
    strace: ptrace(PTRACE_GETREGS) -> read syscall number + args
    strace: prints: read(fd=3, buf=..., count=4096)
    strace: ptrace(PTRACE_SYSCALL) -> resume A
    A: executes read() in kernel
    Kernel: STOP A (syscall exit point), notify strace
    strace: ptrace(PTRACE_GETREGS) -> read return value
    strace: prints: = 1024 <0.000123>
    strace: ptrace(PTRACE_SYSCALL) -> resume A

Cost: TWO ptrace interruptions per syscall
  + 2 context switches per syscall (kernel-strace-kernel-A)
  = 10-100x slowdown for syscall-heavy programs
  
Safe to use in production? Generally NO for continuous tracing.
  Attaching briefly for diagnosis: acceptable.
  -c (count mode) has same overhead per syscall.
```

**How perf works (PMU sampling):**
```
CPU has Performance Monitoring Unit (PMU):
  Hardware registers that count CPU events:
    - PERF_COUNT_HW_CPU_CYCLES: clock cycles
    - PERF_COUNT_HW_INSTRUCTIONS: executed instructions
    - PERF_COUNT_HW_CACHE_MISSES: cache miss events
    - PERF_COUNT_HW_BRANCH_MISSES: branch mispredictions
  
perf stat:
  Programs these counters -> run program -> read final counts
  Overhead: near-zero (hardware registers, no process interruption)
  
perf record (sampling profiler):
  Set: "generate hardware interrupt every N cycles" (e.g., every 1000000)
  N cycles pass: CPU interrupt -> kernel interrupt handler
  Handler: record current instruction pointer + call stack
  Resume process: continues executing
  
  Result: histogram of "where was the IP when we sampled?"
  High-frequency functions: appear in many samples = hot code
  Low-frequency: few samples = cold code
  
  Overhead: ~1-5% (only N% of cycles cause an interrupt)
  
Flame graph interpretation:
  Width = % of time (samples) function appears in call stacks
  Height = call stack depth
  "Plateau" (wide flat top) = CPU is spending time HERE
  "Tower" (narrow, tall) = deep call chain but fast
```

---

### Thought Experiment

Diagnosing a slow Java service:

```bash
# Symptom: Java service processing 100 req/s instead of expected 1000 req/s

# Step 1: Is it CPU-bound or I/O-bound?
top -H -p $(pgrep -f myservice.jar) -n1
# If user% high: CPU-bound
# If sys% high: too many syscalls
# If both low: blocked on I/O or locks

# Step 2: If CPU-bound, what's it doing?
perf top -p $(pgrep -f myservice.jar)
# Look for hot functions in [JIT] or specific method names
# "Interpreter" = JVM is interpreting, not JIT-compiled yet (warm-up issue)
# "GC" = garbage collection consuming CPU

# Step 3: Syscall profile (what syscalls is it making?):
strace -c -p $(pgrep -f myservice.jar) -e trace=file,network 2>&1 &
sleep 5
kill %1
# Output shows: are there millions of tiny reads/writes? (buffering issue)
# Network calls: too many small sendto()?

# Step 4: Full flame graph (30-second sample):
perf record -F 99 -g -p $(pgrep -f myservice.jar) sleep 30
perf script > out.perf
# Collapse stack frames:
# cat out.perf | /opt/FlameGraph/stackcollapse-perf.pl > out.folded
# cat out.folded | /opt/FlameGraph/flamegraph.pl > flame.svg

# For Java: JVM needs special handling for JIT symbols:
perf record -F 99 -g -p $JVM_PID sleep 30 -- -XX:+PreserveFramePointer
# The PreserveFramePointer JVM flag enables proper stack unwinding
```

---

### Mental Model / Analogy

```
strace = following someone with a clipboard, writing down everything they do:
  "At 10:00: opened the fridge (open call)"
  "At 10:01: looked at the milk (read call)"
  "At 10:02: put it back (close call)"
  Very detailed, but your constant writing slows them down (overhead)
  Good for: debugging (what is this process DOING?)
  Bad for: performance (the observation changes the behavior too much)

perf stat = weighing the person and checking their heart rate:
  "In the last minute: 120,000 steps (instructions), 
   heart rate 140 bpm (cycles), 
   tripped 50 times (cache misses)"
  Near-zero impact (hardware counters, not interrupting behavior)
  Good for: measuring overall efficiency

perf record = taking 99 photographs per second:
  Stop them at random moments and take a photo of exactly where they are
  and what led them to that point (call stack)
  After 30 seconds: 2970 photos
  Develop photos: 60% of photos show them at the coffee machine!
  Conclusion: they spend 60% of their time getting coffee (hot path)
  Overhead: only the time it takes to snap each photo (~1-5%)

Flame graph = the photo album:
  X-axis = time (how many photos were taken here)
  Y-axis = what they're doing (call stack depth)
  Wide bars at top = this is where most time is spent
  Click into bars = see the detail of why they're there (callee breakdown)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`strace -c cmd` for syscall summary. `strace -p PID` for live tracing.
`perf stat cmd` for hardware counters. `perf top` for live CPU hotspots.
`strace` shows what the program IS doing; `perf` shows where CPU time IS SPENT.

**Level 2:**
`perf record -g + perf report` workflow. Flame graph generation with
Brendan Gregg's FlameGraph scripts. strace filters (`-e trace=file`,
`-e trace=network`). `strace -T` for syscall timing. ltrace for library
call tracing. `-f` flag for following forks.

**Level 3:**
`perf` events: `perf list` to see all available events (hardware, software,
tracepoints, probes). `perf stat -e cycles,instructions,cache-misses cmd`.
Custom probes: `perf probe --add 'myfunction'`. `perf trace` (faster strace
alternative using tracepoints). Linux tracepoints vs dynamic probes.
User-space probes via USDT (User Statically Defined Tracepoints).

**Level 4:**
Off-CPU profiling (time spent NOT on CPU: I/O wait, sleep, locks).
`perf record -e block:block_rq_complete` for disk I/O profiling.
`perf sched record + perf sched latency` for scheduling latency.
PMU (Performance Monitoring Unit) internals: per-core vs uncore counters.
PEBS (Precise Event Based Sampling) for precise instruction attribution.
BPF profiling with bpftrace as perf alternative.

**Level 5:**
Microarchitectural profiling: Intel VTune/AMD uProf concepts - pipeline
stalls (frontend vs backend bound), memory latency breakdown (L1/L2/L3/DRAM
hit rates), NUMA effects. `pmu-tools` for Intel TopDown analysis methodology
(Top-level 4-bucket analysis: Retiring, Bad Speculation, Frontend Bound,
Backend Bound). Profiling JVM bytecode: AsyncProfiler for Java (uses
Linux `perf_events` for CPU profiling without safepoint bias that
traditional JVMTI profilers have).

---

### Code Example

**BAD - incorrect profiling approach:**
```bash
# BAD 1: Using strace as a continuous monitoring solution:
strace -p 12345 > /var/log/app-trace.log 2>&1 &
# This adds 10-100x overhead to every syscall the process makes
# Will DESTROY performance of a production service
# Fine for: brief debugging sessions (seconds to minutes)
# Not for: continuous logging

# BAD 2: strace on a multi-threaded program without -f:
strace -p 12345   # single-threaded strace on multi-threaded process
# Only traces the main thread!
# All the work happening in worker threads is INVISIBLE

# GOOD: use -f to follow threads and children:
strace -f -p 12345   # follow all threads and child processes

# BAD 3: perf record without -g (no callgraph):
perf record -p 12345 sleep 30
perf report
# Shows: "func_xyz: 45%" but no information about WHERE func_xyz is called from
# Can't build flame graph without callgraph data

# GOOD: always include -g for callgraph:
perf record -g -F 99 -p 12345 sleep 30
```

**GOOD - systematic profiling approach:**
```bash
#!/bin/bash
# profile-app.sh: systematic Linux performance profiling

PID=${1:?Usage: $0 <PID>}
DURATION=${2:-30}   # seconds to profile
OUTPUT_DIR=$(mktemp -d -t profile-XXXXXX)

echo "=== Profiling PID $PID for ${DURATION}s ==="
echo "Output directory: $OUTPUT_DIR"

# 1. Quick CPU check (no overhead):
echo ""
echo "[1/5] Hardware counters (perf stat)..."
timeout "$DURATION" perf stat -p "$PID" 2>"$OUTPUT_DIR/perf-stat.txt" || true
echo "IPC and cache miss summary:"
grep -E "insns per cycle|cache-misses" "$OUTPUT_DIR/perf-stat.txt"

# 2. Quick syscall summary (elevated overhead for duration):
echo ""
echo "[2/5] Syscall summary (strace -c, ${DURATION}s)..."
timeout "$DURATION" strace -c -p "$PID" 2>"$OUTPUT_DIR/strace-c.txt" || true
echo "Top syscalls by time:"
head -10 "$OUTPUT_DIR/strace-c.txt"

# 3. CPU flame graph:
echo ""
echo "[3/5] CPU flame graph (perf record)..."
perf record -F 99 -g -p "$PID" -o "$OUTPUT_DIR/perf.data" sleep "$DURATION" 2>/dev/null

if [[ -f "$OUTPUT_DIR/perf.data" ]]; then
    perf report -i "$OUTPUT_DIR/perf.data" --stdio \
        2>/dev/null > "$OUTPUT_DIR/perf-report.txt"
    echo "Top CPU functions:"
    grep "^#\|[0-9]\+\.[0-9]\+%" "$OUTPUT_DIR/perf-report.txt" | head -20
fi

echo ""
echo "=== Results saved to $OUTPUT_DIR ==="
echo "View full report: perf report -i $OUTPUT_DIR/perf.data"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "strace shows what the program is doing inside" | strace shows SYSCALLS - the boundary between the program and the kernel. It does NOT show function calls within the program itself, library function calls, or algorithm execution. A program that spends 99% of its time sorting an array in userspace is entirely invisible to strace (no syscalls for sorting). strace is most useful for: understanding I/O patterns, debugging "file not found" errors (seeing the exact path being looked for), diagnosing network connection failures, understanding why a program hangs (what syscall is it blocked on). For internal function profiling: use perf record, gprof, Valgrind's callgrind, or language-specific profilers. |
| "perf record accurately shows JVM/Python/interpreted code hotspots" | perf record works by sampling the native instruction pointer. For JVM: unless you use `-XX:+PreserveFramePointer` (JDK 8u60+), the JIT compiler optimizes away frame pointers, making stack unwinding impossible - perf shows `[JIT]` as a monolithic block with no function names. For Python: CPython bytecode is executed in `ceval.c` - all Python code shows as time in the interpreter loop. Solutions: AsyncProfiler for Java (works with JVM's frame pointer optimization). py-spy or Austin for Python (read process memory to get Python stack frames). These tools know how to unwind language-specific stack representations. |
| "strace -c overhead is lower because it just counts" | strace `-c` has the SAME per-syscall overhead as regular strace mode: it still uses `ptrace()` to intercept every syscall at entry and exit. The only difference is it summarizes (counts and times) instead of printing each call. The process is still interrupted twice per syscall, causing similar slowdown. For production CPU profiling with lower overhead, use `perf stat` (hardware counters, near-zero overhead) or `perf trace` which uses kernel tracepoints instead of ptrace. |
| "A function appearing at 50% in perf report takes 50% of execution time" | perf report shows the percentage of SAMPLES where a function appeared anywhere in the call stack (including as a leaf or an ancestor). The actual "self" time (time spent in that function, excluding callees) is shown separately as "self" vs "children" in perf. A function at "50% children" might itself do nothing (pure dispatch/delegation) but calls expensive functions. Focus on the LEAF functions (highest self %) for where CPU is actually executing instructions. The flame graph visualization makes this distinction clear: the WIDTH of the TOP (leaf) portion of each tower = self time. |
| "`ltrace` is more useful than strace because it shows library calls" | strace is generally more useful because: (1) library calls eventually become syscalls - strace shows the authoritative source. (2) ltrace has higher overhead (breakpoints at every library entry). (3) ltrace misses inline library functions (LTO can inline `strlen`, `memcpy`, etc.). (4) strace is more commonly supported and documented. ltrace is useful for: seeing exactly which library function is being called (format strings, malloc sizes), debugging applications that make heavy library calls but few syscalls (e.g., a GUI application using X11 functions). For most backend diagnostics: strace first. |

---

### Failure Modes & Diagnosis

**perf: not enough permissions:**
```bash
# Error: "You may not have permission to collect system-wide stats"
# or: "perf_event_paranoid = 3: No permission"

# Check current setting:
cat /proc/sys/kernel/perf_event_paranoid
# 3 = only root can use perf (most secure default on some distros)
# 2 = kernel profiling for root only, user profiling allowed
# 1 = allow kernel profiling for user
# 0 = allow all profiling
# -1 = no restrictions

# For development (temporary):
sysctl kernel.perf_event_paranoid=1

# For CI/CD (persist):
echo "kernel.perf_event_paranoid=1" >> /etc/sysctl.conf
sysctl -p

# For containers: perf needs privileged mode or:
# docker run --cap-add SYS_ADMIN --security-opt seccomp=unconfined ...
# Or set perf_event_paranoid=0 on host

# Alternative for containers (no kernel access): eBPF-based profilers:
# - bpftrace
# - Parca (continuous profiling)
# - Pyroscope
```

---

### Related Keywords

**Foundational:**
LNX-006 (Process management), LNX-011 (System monitoring)

**Builds on this:**
LNX-087 (Linux Tracing - ftrace, bpftrace), LNX-095 (CPU Performance)

**Related:**
LNX-093 (USE Method), LNX-094 (Memory pressure diagnosis)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `strace -c cmd` | Syscall summary (count + time) |
| `strace -p PID` | Live syscall trace |
| `strace -e trace=file cmd` | Filter: file syscalls only |
| `perf stat cmd` | Hardware counters (IPC, cache) |
| `perf top -p PID` | Live CPU hotspot view |
| `perf record -g -p PID sleep 30` | 30-second CPU profile |
| `perf report` | Analyze perf.data interactively |
| `ltrace cmd` | Library call tracing |

**3 things to remember:**
1. strace adds 10-100x overhead (ptrace); use briefly for diagnosis, not production monitoring
2. `perf stat`: zero overhead hardware counters; `perf record -g`: ~1-5% overhead sampling profiler
3. Always use `-g` with `perf record` for call graphs; without it, you can't build flame graphs

---

### Transferable Wisdom

Profiling concepts appear in: Java's JFR (Java Flight Recorder) and
async-profiler: same sampling principle as `perf record` but JVM-aware.
Python's cProfile and py-spy: cProfile instruments every function call
(like strace overhead), py-spy samples (like perf record). eBPF-based
profilers (bpftrace, Parca): next-generation, kernel-level profiling with
programmable analysis. Continuous profiling platforms (Pyroscope, Grafana
Phlare): production-always-on sampling at 99Hz with time-series storage.
The flame graph visualization has become ubiquitous: Chrome DevTools,
IntelliJ profiler, Xcode Instruments, AWS X-Ray all use the same visual
format. Understanding the sampling-vs-tracing trade-off (overhead vs
completeness) appears in all observability systems: high-frequency sampling
(expensive but complete) vs low-frequency sampling (cheap but misses rare
events) vs tracing every request (expensive).

---

### The Surprising Truth

Brendan Gregg created the flame graph visualization in 2011 while debugging
a MySQL performance issue at Sun Microsystems. The original perf data
was too dense to understand - thousands of function names and percentages
in text output. He wrote a Perl script to visualize it as stacked colored
bars, and the flame graph was born in a weekend. The "surprising" part: the
flame graph became the de facto standard for performance visualization across
ALL programming languages and environments (Java, Python, Go, Rust, JavaScript,
browsers, mobile apps) not because of a standards body or big company, but
because one engineer shared a Perl script on GitHub. The second surprise:
the most valuable profiling insight for most applications is NOT which function
is hottest, but WHY a function that should be fast is appearing everywhere.
The flame graph makes the difference visible immediately: a function that
appears as a thin tower (narrow but tall) is called rarely but deeply. A
function that appears as a wide plateau (wide but short) is called CONSTANTLY
from everywhere. "Wide plateaus" are the treasure - they represent optimization
opportunities that compound across the entire program.

---

### Mastery Checklist

- [ ] Can use strace to capture a syscall summary with strace -c
- [ ] Can attach strace to a running process and understand the output
- [ ] Can use perf stat to check IPC and cache miss rates
- [ ] Can generate a CPU profile with perf record -g and analyze with perf report
- [ ] Understands the trade-off: strace (high overhead, detailed) vs perf (low overhead, sampling)

---

### Think About This

1. A web service processes 10,000 requests/second on Linux. You suspect
   it's slower than it should be. Describe a systematic investigation plan
   using strace, perf, and /proc that determines: (a) whether it's CPU-bound
   or I/O-bound, (b) if CPU-bound: which functions are hottest, (c) if
   I/O-bound: which files/syscalls are responsible. Include the specific
   commands you would run and what metrics you're looking for.

2. `strace -c ./myprogram` shows that 80% of the time is spent in `read()`
   syscalls, and the program is reading 4KB at a time from a 10GB file.
   Explain: (a) why this is a problem, (b) what the optimal read size
   would be, (c) how to verify the improvement using strace and perf stat,
   and (d) what `perf stat` metrics (instructions per cycle, cache misses)
   would change after optimization.

3. You want to profile a Java application's CPU usage but `perf report`
   shows "60% of CPU time in [JIT]" without any method names. Explain why
   this happens, what JVM flag fixes it, and name an alternative Java-specific
   profiler that doesn't require this flag while still providing accurate
   CPU profiling without safepoint bias.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between strace and perf, and when would you use each?
A: strace and perf solve different performance investigation problems: strace: traces SYSTEM CALLS (the interface between user programs and the kernel). Uses ptrace() to intercept every syscall at entry and exit. Shows: what files are opened, what network connections are made, what memory is allocated at the kernel level. OVERHEAD: 10-100x slowdown because every syscall requires two ptrace interruptions + context switches. USE WHEN: debugging "what is this process DOING?" - files it opens, network calls, why it fails or hangs. "strace -c" for syscall distribution - which calls dominate. Brief diagnostic sessions (seconds to minutes), not continuous profiling. perf: uses hardware performance counters (PMU) and statistical sampling. OVERHEAD: near-zero for `perf stat` (hardware registers), 1-5% for `perf record` (periodic sampling interrupts). TWO MODES: `perf stat` - count hardware events (cache misses, instructions per cycle, branch mispredictions) for overall efficiency measurement. `perf record -g` - statistical sampling profiler: captures call stack at regular intervals to build a histogram of "where is CPU time spent". USE WHEN: CPU profiling (which functions are hot?), performance counters (memory efficiency, CPU stalls), production-safe sampling (~1-5% overhead). Rule of thumb: strace first if the question is "why is this broken or slow in terms of I/O/syscalls?" perf first if the question is "where is CPU time going?" or "is this CPU or memory-bound?" A complete investigation often uses both: strace -c to see syscall distribution, then perf record + flame graph to find hot code paths.

**Expert:**
Q: How would you profile a Java application that's consuming high CPU but you can't find the hot code path with standard profilers?
A: Standard Java profilers (JVisualVM, YourKit, JProfiler) use JVMTI safepoints for sampling - they only sample the call stack at "safepoint" locations, which are places the JVM inserts to allow GC and JVM operations. The problem: the JVM only checks for safepoints at certain points in compiled code (loop back-edges, method returns). If the hot code is a tight inner loop with NO safepoints, the profiler NEVER samples inside that loop. Result: misleading profile - the METHOD calling the hot loop appears at 100%, but the loop itself (which is the real problem) is invisible. Solutions: (1) AsyncProfiler: uses Linux perf_events and hardware breakpoints to sample the native instruction pointer - bypasses the safepoint bias entirely. Works even inside JIT-compiled loops. Usage: `java -agentpath:/path/async-profiler.so=start,event=cpu,file=profile.html MyApp` -> generates flame graph with actual hot code. (2) perf record with frame pointers: `java -XX:+PreserveFramePointer -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints myapp`, then `perf record -g -p $PID sleep 30`. The JVM flag preserves frame pointers in JIT code, enabling Linux perf to unwind the JVM stack. Combined with JVM symbol maps (`perf-map-agent`), this shows Java method names in perf output. (3) JFR (Java Flight Recorder): AsyncGetCallTrace-based (JDK 11+), low overhead, built-in. `jcmd $PID JFR.start duration=30s filename=profile.jfr` then analyze in JMC. The key insight: safepoint-biased profilers systematically MISS the most pathological performance problems (tight loops, JNI code, JIT-compiled code), and async profiling fixes this. This is why `perf stat` showing high `instructions-per-cycle` but application profilers showing "nothing special" is a common diagnostic mismatch.
