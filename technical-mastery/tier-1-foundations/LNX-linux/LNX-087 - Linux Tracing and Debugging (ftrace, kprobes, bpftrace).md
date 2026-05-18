---
id: LNX-087
title: "Linux Tracing and Debugging (ftrace, kprobes, bpftrace)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-073, LNX-082
used_by: LNX-093, LNX-104
related: LNX-073, LNX-082, LNX-088, LNX-093
tags: [ftrace, kprobes, uprobes, tracepoints, bpftrace, perf, trace-cmd, function-tracer, flame-graph, kernel-debugging, dynamic-tracing, static-tracing, perf-record, perf-report, uprobe, eBPF-tracing, brendan-gregg]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 87
permalink: /technical-mastery/lnx/linux-tracing-debugging/
---

## TL;DR

Linux tracing stack: **ftrace** (kernel function tracing via
`/sys/kernel/debug/tracing/`, `trace-cmd record/report`), **kprobes**
(dynamic breakpoints at any kernel instruction), **uprobes** (breakpoints
in user-space binaries), **tracepoints** (static probe points baked into
kernel source), **perf** (`perf record -ag`, `perf report`, `perf top`,
`perf stat` - CPU PMU counters), and **bpftrace** (high-level eBPF tracing
language with DTrace-like one-liners). Key use: `bpftrace -e
'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm,
str(args->filename)); }'` traces all `open()` calls with process name and
filename. For CPU flame graphs: `perf record -ag -- sleep 30 && perf
script | flamegraph.pl > flame.svg`. Tracing is the difference between
guessing and knowing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-087 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | ftrace, kprobes, tracepoints, bpftrace, perf, flame graphs, dynamic tracing, kernel debugging |
| **Prerequisites** | LNX-073 (eBPF), LNX-082 (system call interface) |

---

### The Problem This Solves

**Problem 1**: A Java application has intermittent 200ms latency spikes every
few minutes. All application metrics look normal during the spike - no GC pause,
no database slow query. The culprit is suspected to be a kernel-level operation.
Without tracing: add more logs, redeploy, wait for the spike. With bpftrace:
`bpftrace -e 'kprobe:schedule_timeout { @[comm, kstack] = hist(arg0); }'`
traces all processes sleeping via schedule_timeout - immediately reveals a JVM
thread sleeping in an I/O path for 200ms every few minutes.

**Problem 2**: A C++ service is crashing with a SIGSEGV in production. The
core dump points to a third-party library with no debug symbols. With uprobes
and bpftrace: attach a probe to the specific function in the library binary,
capture function arguments and return values, see exactly what inputs trigger
the crash - without modifying the binary or adding compile-time instrumentation.

---

### Textbook Definition

**Linux tracing mechanisms (bottom to top):**

| Mechanism | Type | Level | Tool | Cost |
|-----------|------|-------|------|------|
| PMU counters | Hardware | CPU | `perf stat` | Zero overhead when counting |
| Tracepoints | Static kernel | Kernel | `perf trace`, `bpftrace` | Near-zero (when disabled) |
| kprobes | Dynamic kernel | Kernel | `perf probe`, `bpftrace` | ~150ns per probe hit |
| uprobes | Dynamic user | Userspace | `perf probe`, `bpftrace` | ~150ns per probe hit |
| ftrace | Function tracer | Kernel | `trace-cmd`, `/sys/kernel/debug/tracing` | High (traces all calls) |
| eBPF | Programmable | Both | `bpftrace`, `bcc` | Configurable |

**Key tools:**
- **ftrace**: kernel function tracer. Uses compiler-inserted NOPs (converted to calls when enabled). `function_graph` tracer shows call tree with timing.
- **kprobes**: breakpoint inserted at any kernel instruction. Pre-handler (before), post-handler (after), fault handler.
- **uprobes**: same as kprobes but for userspace binaries. Can probe any instruction in any process.
- **tracepoints**: `TRACE_EVENT()` macros in kernel source. Stable ABI (unlike kprobes). Preferred when available.
- **perf**: multi-purpose tool: CPU PMU counters, tracepoints, kprobes, profiling, flame graphs.
- **bpftrace**: high-level language (DTrace-like) for writing eBPF tracing programs. One-liners to full scripts.

---

### Understand It in 30 Seconds

```bash
# === bpftrace one-liners ===

# Trace all open() system calls (filename + process):
bpftrace -e 'tracepoint:syscalls:sys_enter_openat {
    printf("%s %s\n", comm, str(args->filename));
}'
# Output: nginx /etc/nginx/nginx.conf
#         sshd /proc/self/loginuid

# Count syscalls by process name:
bpftrace -e 'tracepoint:raw_syscalls:sys_enter {
    @[comm] = count();
}'
# Ctrl-C to exit, output:
# @[kworker/0:2]: 1234
# @[nginx]: 5678
# @[java]: 23456  <- java doing many syscalls!

# Histogram of read() latency in microseconds:
bpftrace -e 'tracepoint:syscalls:sys_enter_read {
    @start[tid] = nsecs;
}
tracepoint:syscalls:sys_exit_read /@start[tid]/ {
    @us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'
# @us:
# [0]     1234 |@@@@@@@@@@@@
# [1]     4567 |@@@@@@@@@@@@@@@@@@@@
# [2, 4)   234 |@@
# [8, 16)   12 |   <- most reads < 16us

# Trace all forks (new processes):
bpftrace -e 'tracepoint:sched:sched_process_fork {
    printf("FORK: parent=%s(%d) child=%d\n",
           comm, pid, args->child_pid);
}'

# Stack trace for kernel allocations > 1MB:
bpftrace -e 'kprobe:__kmalloc /arg0 > 1048576/ {
    printf("Large alloc: %d bytes by %s\n", arg0, comm);
    print(kstack);
}'

# === ftrace basics ===

# Mount debugfs if not mounted:
mount -t debugfs none /sys/kernel/debug

# Enable function_graph tracer:
cd /sys/kernel/debug/tracing
echo function_graph > current_tracer

# Trace only a specific function and its callees:
echo do_sys_openat2 > set_graph_function
echo 1 > tracing_on

# Read trace (live):
cat trace_pipe | head -50
# 0) + 15.678 us   |  do_sys_openat2() {
# 0) + 2.123 us    |    getname_flags() {
# ...

# Stop and clear:
echo 0 > tracing_on
echo > trace   # clear trace buffer

# === trace-cmd (higher-level ftrace interface) ===

# Record 5 seconds of scheduler events:
trace-cmd record -e sched:sched_switch -e sched:sched_wakeup \
    sleep 5
# Creates trace.dat

# Report trace:
trace-cmd report trace.dat | head -20

# Record function graph for a command:
trace-cmd record -p function_graph -g do_sys_openat2 ls /tmp
trace-cmd report

# === perf basics ===

# CPU-wide profile for 10 seconds (all CPUs):
perf record -ag -- sleep 10
# -a: all CPUs, -g: call graph (stack traces)
# Creates perf.data

# View report:
perf report
# Or text report:
perf report --stdio | head -30

# Flame graph with perf:
perf record -ag -F 99 -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# CPU event counters:
perf stat -e cycles,instructions,cache-misses,cache-references \
    -- stress --cpu 1 --timeout 10
# Performance counter stats for 'stress --cpu 1 --timeout 10':
# 10,234,567,890  cycles
#  8,123,456,789  instructions     # insn per cycle: 0.79
#      1,234,567  cache-misses     # 5.23% of all cache refs

# Count specific events:
perf stat -e syscalls:sys_enter_read,syscalls:sys_enter_write \
    -- java -jar app.jar &
# Counts all read/write syscalls during app run

# List available events:
perf list tracepoint 2>&1 | grep syscalls | head -20
perf list kprobes
perf list hardware

# === kprobes with perf probe ===

# Add a kprobe on a kernel function:
perf probe --add 'do_sys_openat2 filename:string'
# Added new event: probe:do_sys_openat2 (on do_sys_openat2 with filename)

# Use in perf stat:
perf stat -e probe:do_sys_openat2 -- sleep 10

# Remove probe:
perf probe --del probe:do_sys_openat2

# === uprobe with bpftrace ===

# Trace a specific function in a binary (no source required):
bpftrace -e 'uprobe:/usr/bin/nginx:ngx_http_request_handler {
    printf("nginx request handler called by pid %d\n", pid);
}'

# Trace Java method via USDT (if JVM has tracepoints):
bpftrace -e 'usdt:/usr/lib/jvm/.../server/libjvm.so:
    hotspot:method__entry {
    printf("%s.%s\n", str(arg1), str(arg3));
}'
```

---

### First Principles

**How different tracing mechanisms work:**
```
Tracepoints (static probes):
  Kernel code has TRACE_EVENT() macros:
  
  // In kernel source (fs/open.c):
  TRACE_EVENT(sys_enter_openat,
      TP_PROTO(struct pt_regs *regs, long id),
      TP_ARGS(regs, id),
      ...
  );
  
  Compile-time:
    Tracepoint is a NOP instruction by default (zero cost)
    When enabled: NOP replaced with CALL to probe handler
  
  Runtime enable:
    echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_enter_openat/enable
    Or: bpftrace attaches eBPF program to tracepoint
  
  Advantage: STABLE ABI (kernel developers maintain interface)
  Disadvantage: limited to where kernel developers added them

kprobes (dynamic probes):
  Insert a breakpoint (int3 / trap instruction) at ANY kernel address:
  
  1. User registers kprobe at address X
  2. Kernel saves original instruction at X
  3. Kernel writes int3 (breakpoint) at address X
  4. When CPU reaches X: int3 fires -> trap handler
  5. Trap handler calls kprobe pre_handler
  6. Restores original instruction + single-steps it
  7. Calls kprobe post_handler
  8. Returns to execution
  
  Modern optimization (jump probe, kprobes+ftrace):
    Uses ftrace mcount infrastructure: replaces NOP with JMP
    No int3 overhead (~5-10ns vs ~200ns for int3)
  
  Advantage: can probe ANY kernel function (public or private)
  Disadvantage: no stable ABI (function names can change between versions)
  
uprobes:
  Same mechanism as kprobes but in user-space process memory:
  1. Register uprobe for pid X, file Y, offset Z
  2. Kernel writes int3 at that virtual address in the process
  3. When that process's instruction pointer reaches offset Z:
     int3 fires -> trap -> uprobe handler
  
  Key feature: works on running binaries WITHOUT symbols
  (use with offset from binary, or function name if symbols available)
  
  Overhead: ~150ns per probe hit (int3 + context switch)
  High-call-rate functions: can add significant overhead

ftrace (function tracer):
  Kernel compiled with -pg flag: every function has a NOP or CALL mcount at
  the start. When enabled: NOPs converted to CALL ftrace_caller.
  
  ftrace_caller logs: function name, caller, timestamp
  function_graph_tracer: also logs return time -> shows call graph with duration
  
  Overhead: high if tracing many functions (every function call intercepted)
  Use case: understand call graph of specific kernel path
  trace-cmd: userspace wrapper for ftrace

perf (performance events):
  Two modes:
  
  1. Counting mode (perf stat):
    Hardware PMU (Performance Monitoring Unit) counters
    Counts events: CPU cycles, instructions, cache misses
    Cost: zero overhead (hardware counters, no software trap)
    Measure: perf stat program / sleep 10
  
  2. Sampling mode (perf record):
    Configure PMU to interrupt every N events (e.g., every 10000 cycles)
    At interrupt: capture instruction pointer + call stack
    Produces statistical profile (not exact execution trace)
    Cost: configurable (higher sampling rate = more overhead, more accuracy)
    -F 99: 99 samples per second per CPU (1% overhead)
    -F 9999: 9999 samples per second (10% overhead, more accurate)

bpftrace:
  High-level language that compiles to eBPF:
  - Probes: kprobe:, uprobe:, tracepoint:, usdt:, interval:, profile:, hardware:
  - Actions: printf, @maps, hist, count, sum, min, max
  - Predicates: /condition/ to filter
  
  Compilation path:
    bpftrace script -> clang/LLVM -> eBPF bytecode
    -> kernel BPF verifier -> JIT to native code
    -> attached to probe point
  
  Overhead: only the eBPF program overhead (per probe hit)
  Typical: 50-200ns per probe hit (vs 150-200ns for kprobe/uprobe directly)
  Very similar to raw kprobe cost after JIT compilation
```

---

### Thought Experiment

Diagnosing a production latency spike using bpftrace:

```bash
# Problem: Java app has 100ms latency spikes every 5 minutes.
# GC logs show no GC pause during spike.
# Database metrics show no slow queries.
# Suspicion: OS-level issue.

# Step 1: Rule out scheduler issues (CPU saturation, blocking):
# Check if threads are runnable but not scheduled:
bpftrace -e '
tracepoint:sched:sched_stat_wait /comm == "java"/ {
    @[tid] = hist(args->delay / 1000000);  // ms histogram
}
interval:s:30 { print(@); clear(@); }
'
# If output shows waits > 50ms: scheduler runqueue full (CPU saturation)

# Step 2: Check disk I/O blocking:
bpftrace -e '
tracepoint:block:block_rq_issue { @start[args->sector] = nsecs; }
tracepoint:block:block_rq_complete
/@start[args->sector]/ {
    @ms = hist((nsecs - @start[args->sector]) / 1000000);
    delete(@start[args->sector]);
}
interval:s:30 { print(@); clear(@); }
'
# If shows I/O operations taking 100ms: dirty page flush storm!

# Step 3: Find which kernel path is causing the sleep:
bpftrace -e '
kprobe:schedule_timeout /comm == "java"/ {
    @[kstack] = hist(arg0 * 1000000 / HZ);  // ms
}
interval:s:30 { print(@); clear(@); }
'
# kstack shows kernel call stack when java thread calls schedule_timeout
# Look for stacks with 100ms timeout

# Step 4: Trace lock contention:
bpftrace -e '
tracepoint:lock:contention_begin /comm == "java"/ {
    @start[tid] = nsecs;
}
tracepoint:lock:contention_end /comm == "java" && @start[tid]/ {
    @ms = hist((nsecs - @start[tid]) / 1000000);
    delete(@start[tid]);
}
interval:s:30 { print(@); clear(@); }
'

# Step 5: Check page fault handling time:
bpftrace -e '
kprobe:handle_mm_fault /comm == "java"/ {
    @start[tid] = nsecs;
}
kretprobe:handle_mm_fault /comm == "java" && @start[tid]/ {
    @ms = hist((nsecs - @start[tid]) / 1000000);
    delete(@start[tid]);
}
'
# A 100ms histogram entry here = major page fault (page swapped out!)
# Fix: vm.swappiness=1, ensure JVM heap is in RAM
```

---

### Mental Model / Analogy

```
Linux tracing stack = different levels of surveillance cameras

Tracepoints = official security cameras at reception:
  Built into the building when it was constructed
  Always there, zero cost when recording is off (power-saving mode)
  Turn on: flip switch (/sys/kernel/debug/tracing/events/.../enable)
  Limitation: cameras only where builders put them
  Examples: syscall entry/exit, scheduler events, network events

kprobes = portable CCTV cameras you can place anywhere:
  Bring your own camera, attach to any wall in the building (any kernel address)
  No construction required (dynamic installation)
  Cost: small (~150ns) even when recording
  Risk: camera angle might change if building is renovated (kernel version upgrade)
  No stable ABI - function names can change

uprobes = cameras outside the building (in userspace):
  Watch what specific people (processes) do in their own rooms
  Can attach without modifying the room (no source code change)
  Point camera at apartment 404, offset 0x1234 (binary offset)
  Works even for rooms with no building plan (no debug symbols)

ftrace = total surveillance (all corridors at once):
  Every person's movement logged (every kernel function call)
  Very high cost (can't run long on busy system)
  function_graph: shows who went where, how long they spent
  Best for: understanding a specific code path in detail
  Use: trace-cmd record -g specific_function (just that room's cameras)

perf = statistical sampling surveillance:
  Instead of recording everything: take a snapshot every 10ms
  "Where is everyone at this moment?" -> aggregate snapshots
  Low cost (1% overhead at 99 samples/sec)
  Statistical: can miss short events, but shows hotspots
  perf record -ag -F 99: sample 99 times/sec, all CPUs, all call stacks

bpftrace = programmable surveillance with AI analysis:
  Write: "When SOMEONE goes to room X, log their name and time"
  Attaches smart camera (eBPF program) to any probe point
  Real-time analysis + filtering (no raw data flood)
  Output: structured data (histograms, counts, timing)
  One-liner = one smart camera with specific detection rule

Flame graph = heat map of the building:
  Width = time spent (wider = hotter)
  Position = call stack (bottom = where they came from)
  See at a glance: which rooms (functions) consume most time
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept of Linux tracing. `perf top` (real-time CPU hotspot). `strace -p PID`
(system call trace). `ltrace` (library call trace). `strace -c` (syscall
summary with counts and times). `/sys/kernel/debug/tracing/` directory structure.

**Level 2:**
`perf record -ag sleep 30` and `perf report`. Flame graph generation.
`bpftrace` one-liners for syscall tracing. Tracepoints: list with
`perf list tracepoint`. `trace-cmd record/report`. ftrace `function_graph`
tracer basics. `perf stat` for CPU counters.

**Level 3:**
kprobe vs tracepoint: when to use each (stability vs availability).
bpftrace scripts: maps, histograms, predicates, aggregations. `perf probe`
to add kprobes. uprobe for userspace tracing. `perf annotate` for
assembly-level hotspot analysis. bpftrace built-in variables: `comm`, `pid`,
`tid`, `kstack`, `ustack`, `nsecs`. BCC (BPF Compiler Collection) tools:
`execsnoop`, `opensnoop`, `tcpconnect`, `runqlat`.

**Level 4:**
BCC Python bindings for custom tools. bpftrace language deep-dive: probe
types, built-in functions, map types. `perf probe` with DWARF debug info for
source-level kprobes (`--add do_sys_openat2 filename:string`). USDT (User
Statically Defined Tracing) for application-defined probe points. SystemTap
(older, still used in RHEL). `drgn`: Python-based kernel debugger (reads
kernel memory). `crash`: kernel core dump analysis. Latency histogram
interpretation: p50/p99/p999 from hist data.

**Level 5:**
eBPF tail calls in tracing: chain multiple BPF programs. bpftrace + fentry/fexit
(new probe types replacing kprobe for JIT-compiled functions). `libbpf`-based
tracing tools (low-level C eBPF programs). Kernel live patching and how it
interacts with tracing. `perf inject --jit`: inject JVM JIT profiles into
perf.data for Java flame graphs. NVIDIA NSight for GPU kernel tracing (same
concept at GPU level). `perf c2c`: cache-to-cache coherency tracing for NUMA
performance. Continuous profiling in production: Parca, Pyroscope, pixie
(use eBPF for always-on sampling).

---

### Code Example

**BAD - using strace in production:**
```bash
# BAD: strace on production process
strace -p 12345
# strace intercepts EVERY system call with ptrace()
# ptrace overhead: 2-10x slowdown!
# In production: your 1Gbps service drops to 100Mbps
# Users experience: service degradation, timeouts
# strace is for development/debugging only
# Never attach strace to a production process under load

# BAD: ftrace on all functions in production
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
# This traces EVERY function call in the kernel
# Overhead: 10-50% CPU increase
# On a busy production server: dangerous!

# GOOD: use bpftrace with filtering (safe for production):
# Low overhead - eBPF JIT, only fires on matching events:
bpftrace -e '
tracepoint:syscalls:sys_enter_openat
/comm == "nginx"/ {
    @files[str(args->filename)] = count();
}
interval:s:60 { print(@files); clear(@files); }
'
# Only fires for openat syscalls from nginx process
# Typical overhead: < 1% CPU

# GOOD: ftrace targeted to specific function (not all):
trace-cmd record -p function_graph -g do_sys_openat2 \
    -O nofuncgraph-irqs -- sleep 5
# Only traces do_sys_openat2 and callees
# Much lower overhead than full function tracer
```

**GOOD - production-safe bpftrace tracing:**
```bash
# Identify slow disk I/O in production:
cat > io_latency.bt << 'EOF'
#!/usr/bin/env bpftrace

// Track block I/O latency (milliseconds)
tracepoint:block:block_rq_issue {
    @start[args->dev, args->sector] = nsecs;
}

tracepoint:block:block_rq_complete
/@start[args->dev, args->sector]/ {
    $lat_ms = (nsecs - @start[args->dev, args->sector]) / 1000000;
    if ($lat_ms > 10) {  // only log I/O > 10ms
        printf("Slow I/O: dev=%d sector=%d lat=%dms\n",
               args->dev, args->sector, $lat_ms);
    }
    @lat_ms = hist($lat_ms);
    delete(@start[args->dev, args->sector]);
}

interval:s:30 {
    printf("\n=== I/O Latency Histogram (ms) ===\n");
    print(@lat_ms);
    clear(@lat_ms);
}

END {
    clear(@start);
}
EOF

chmod +x io_latency.bt
./io_latency.bt

# Flame graph from perf for CPU hotspot:
perf record -ag -F 99 -- sleep 30  # 30s, 99 samples/sec, all CPUs

# Generate flame graph:
git clone --depth 1 https://github.com/brendangregg/FlameGraph
perf script | FlameGraph/stackcollapse-perf.pl | \
    FlameGraph/flamegraph.pl > /tmp/cpu-flame.svg

# View: open in browser
# Hot functions: widest tower segments
# Tall stacks: deep call paths
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "strace is safe to use on production processes" | `strace` uses `ptrace(2)` which intercepts every system call with a context switch to the tracing process. Overhead is 2-10x per traced system call. For a service making 100,000 syscalls/second: `strace -p PID` effectively serializes execution with debugging overhead, potentially reducing throughput by 90%. `strace -c` (count mode) is somewhat safer (summarizes at end), but still adds ptrace overhead per syscall. The production-safe alternative: `bpftrace -e 'tracepoint:raw_syscalls:sys_enter /pid == target_pid/ { @[args->id] = count(); }'` - uses eBPF with near-zero overhead, same information. Rule: strace is for development. bpftrace/perf is for production. |
| "perf record captures exact execution trace" | `perf record` in default mode uses statistical SAMPLING: it interrupts the CPU every N events (e.g., every 10,000 clock cycles) and records the current stack. With `-F 99` (99 samples/second): you get a statistical approximation of where CPU time is spent. Short-lived functions (< 1ms) may not appear in the profile. The flame graph shows WHERE the program STATISTICALLY spends time - not a complete trace of every function call. For exact function call tracing (every call, with timestamps): use bpftrace kprobes/tracepoints or ftrace function_graph. These have higher overhead but provide complete traces. |
| "kprobes break when the kernel is updated" | kprobes attach to kernel functions BY NAME (or address). If a kernel update renames, inlines, or removes a function: the kprobe fails to attach. This is by design - kprobes have no stable ABI. Tracepoints, in contrast, are maintained as stable interfaces (the kernel developers commit to preserving them across versions). For production tooling that needs to work across kernel updates: prefer tracepoints where available. Use kprobes only when no tracepoint exists for the kernel behavior you need to observe. bpftrace provides both: `tracepoint:syscalls:sys_enter_openat` (stable) vs `kprobe:do_sys_openat2` (may break on kernel update). Check available tracepoints: `perf list tracepoint`. |
| "Flame graphs show slow code" | Flame graphs show where CPU TIME is spent - not which code is slow in wall-clock terms. A wide block in a flame graph means that code runs frequently (or for long durations). Two interpretations: (1) The code IS slow (latency issue) OR (2) The code is fast but called millions of times (throughput issue). A 100ns function called 1 billion times shows as "hot" in the flame graph. The fix might be reducing call frequency, not optimizing the function. Also: off-CPU flame graphs (where threads are BLOCKED waiting for I/O, locks, etc.) require a different tool (`bpftrace` with `sched:sched_switch` tracepoint). CPU flame graphs miss all the time a thread spends blocked. For latency issues: use off-CPU analysis. For CPU saturation: use on-CPU flame graphs. |

---

### Failure Modes & Diagnosis

**Tracing tool issues and diagnosis:**
```bash
# === bpftrace permission errors ===
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { ... }'
# Error: Could not attach to tracepoint ... (Permission denied)

# Solution 1: run as root:
sudo bpftrace -e '...'

# Solution 2: grant CAP_BPF + CAP_PERFMON:
# (kernel 5.8+ split CAP_SYS_ADMIN into finer-grained caps)
sudo setcap cap_bpf,cap_perfmon+ep /usr/bin/bpftrace

# === kprobe fails to attach ===
bpftrace -e 'kprobe:tcp_sendmsg_locked { ... }'
# ERROR: Could not attach probe: tcp_sendmsg_locked
# Reason: function inlined by compiler, no symbol

# Fix: find the actual function name:
grep -r "tcp_sendmsg" /proc/kallsyms | head -5
# (check available symbols)
# Try the non-inlined version or use a tracepoint instead:
bpftrace -e 'tracepoint:net:net_dev_xmit { ... }'

# === perf record missing stacks ===
perf report
# [ If no call graph information ]
# Reason: application compiled without frame pointers

# Fix option 1: compile with frame pointers:
# gcc -fno-omit-frame-pointer -g ...
# java: -XX:+PreserveFramePointer

# Fix option 2: use DWARF unwinding:
perf record --call-graph dwarf -- sleep 10
# (requires debug symbols, higher overhead)

# Fix option 3: use LBR (Last Branch Record, Intel only):
perf record --call-graph lbr -- sleep 10
# Zero overhead, limited depth (32 frames)

# === bpftrace script memory issues ===
bpftrace script.bt
# WARNING: Failed to print all values
# Map too large (over memory limit)
# Reduce map size:
# @[tid, comm, kstack] -> @[kstack]  (fewer keys)
# Or increase map memory:
BPFTRACE_MAP_KEYS_MAX=65536 bpftrace script.bt

# === ftrace: trace buffer overflow ===
cat /sys/kernel/debug/tracing/trace | grep overrun
# [overrun in ftrace ring buffer]
# Increase buffer size:
echo 4096 > /sys/kernel/debug/tracing/buffer_size_kb
# Or use trace-cmd --buffer-size 4096
```

---

### Related Keywords

**Foundational:**
LNX-073 (eBPF), LNX-082 (System call interface)

**Builds on this:**
LNX-093 (Performance troubleshooting USE method), LNX-104 (Linux observability platform design)

**Related:**
LNX-088 (Disk performance tools), LNX-093 (Performance troubleshooting)

---

### Quick Reference Card

| Tool | Use Case | Overhead |
|------|----------|---------|
| `bpftrace -e '...'` | Ad-hoc one-liner tracing | Low (eBPF JIT) |
| `perf record -ag -F 99` | CPU profiling + flame graphs | ~1% |
| `perf stat` | CPU counter measurements | Zero |
| `trace-cmd record -p function_graph` | Kernel call graph | Medium-High |
| `strace -p PID` | Syscall tracing (dev only!) | 2-10x slowdown |
| `perf probe --add func:arg` | Add kprobe via perf | Low per-hit |

**3 things to remember:**
1. `strace` is not safe for production (2-10x overhead per syscall via ptrace) - use bpftrace tracepoints instead (< 1% overhead)
2. Flame graph width = time spent there; tall = deep call stack; identify the WIDEST tower at the top as the CPU hotspot
3. For latency spikes: trace scheduler wait time (`tracepoint:sched:sched_stat_wait`) and disk I/O latency (`tracepoint:block:block_rq_complete`) - these catch 90% of "mysterious" latency sources

---

### Transferable Wisdom

The tracing philosophy - observe the system in production without modifying it,
at any level, with minimal overhead - is the same goal as: distributed tracing
(OpenTelemetry, Jaeger), application performance monitoring (APM tools), and
chaos engineering (observe failure modes safely). Flame graphs (invented by
Brendan Gregg) are now universal: used for CPU (Linux perf), memory
allocations (heaptrack), JVM profiling (async-profiler), Node.js (v8-profiler),
Go (pprof web UI). The visualization principle translates across languages.
The kprobe/uprobe model (dynamic instrumentation at any instruction) was
pioneered by DTrace (Solaris, 2003) and inspired Linux's tracing infrastructure.
The design principle: observable behavior should be possible without recompilation.
Production profiling without overhead is now possible with continuous profiling
tools (Parca, Pyroscope, Grafana Beyla) that use eBPF to sample stacks
across all processes with < 1% overhead 24/7 - turning profiling from an
occasional debugging activity to always-on observability. The bpftrace language
(probe:action pattern) maps directly to Prometheus alerting rules (metric{label}:
rule) - both are event-condition-action patterns for observability.

---

### The Surprising Truth

The foundational paper for Linux's tracing infrastructure was written about
DTrace on Solaris in 2004. For years, Linux lacked an equivalent. Brendan Gregg,
who co-invented DTrace at Sun, later joined Netflix where he systematically
built the modern Linux tracing toolkit: he invented flame graphs (2011),
popularized SystemTap and perf tools, and when eBPF became capable (kernel
3.18, 2014+), he co-founded the bpftrace project and wrote most of the BCC
tool library. The bpftrace language syntax is deliberately similar to DTrace's
D language. Gregg's "BPF Performance Tools" book (2019) and "Systems Performance"
(2020) are considered the definitive references. The surprising productivity
insight: armed with bpftrace, a skilled engineer can diagnose any production
kernel-level performance issue in minutes without touching production code.
The entire Linux tracing infrastructure is available on any modern kernel - but
most engineers never discover it. Netflix, Meta, Google, and Cloudflare all
use eBPF-based tracing as first-line production debugging. The tools existed
for years before widespread adoption. In 2024, eBPF-based continuous profiling
(always-on, < 1% overhead) is becoming standard in Kubernetes platforms -
flame graphs as a service, automatically.

---

### Mastery Checklist

- [ ] Can write bpftrace one-liners to trace system calls, latency, and count events
- [ ] Can generate CPU flame graphs using perf record and the FlameGraph toolkit
- [ ] Understands the difference between kprobes (dynamic) and tracepoints (static)
- [ ] Knows why strace is dangerous in production and what to use instead
- [ ] Can use perf stat to measure CPU efficiency (instructions per cycle, cache misses)

---

### Think About This

1. A production service has a p99 latency of 50ms but p999 of 5 seconds. The
   spikes happen ~1 per 1000 requests. Traditional logs and metrics don't
   capture the cause. Design a bpftrace investigation strategy: which probe
   types would you use, what would you measure (scheduler wait time, disk I/O,
   network I/O, memory faults, lock contention?), and how would you correlate
   kernel events with specific requests given you know the process PID but not
   the individual request thread ID?

2. You need to trace a third-party Java library that has a suspected memory
   leak. You have no source code and cannot recompile. The library calls a
   specific native method `com.vendor.NativeLib.processData()` which is compiled
   to `process_data()` in a .so file. Design the uprobes approach: how do you
   find the correct binary offset for the uprobe attachment, what context
   (arguments, return value) would you capture, and how would you correlate
   with Java heap growth over time using combination of uprobe + JVM USDT probes?

3. Explain why "wide" in a flame graph does NOT automatically mean "slow code
   that needs optimization". Give three concrete scenarios where a wide flame
   graph block should NOT be optimized: (a) a function that's called correctly
   but frequently, (b) a utility function shared by all code paths, (c) intentional
   blocking/waiting. For each, explain what the correct action is instead of
   optimizing the function itself.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between tracepoints, kprobes, and uprobes in Linux, and when would you choose each?
A: These are three different mechanisms for attaching observation code to running Linux systems, with different trade-offs. TRACEPOINTS: static probe points baked into kernel source code using `TRACE_EVENT()` macros. When disabled: they're a NOP instruction (zero overhead). When enabled: a small stub is called, which invokes any registered handlers (eBPF programs or ftrace). STABLE ABI: the kernel developers maintain these interfaces and don't remove them between versions. Coverage: syscall entry/exit, scheduler events, network events, block I/O, memory allocation. Available: `perf list tracepoint` or `ls /sys/kernel/debug/tracing/events/`. Use when: the kernel behavior you want to observe has a tracepoint (always prefer tracepoints for production tooling because they're stable). KPROBES: dynamically inserted breakpoints at any kernel instruction. You specify a function name or address. The kernel saves the original instruction, writes a breakpoint, and calls your handler when hit. NOT stable: function names can change between kernel versions, functions can be inlined (disappear). Use when: the kernel behavior you need has NO tracepoint and you need to observe internal kernel functions. Example: `kprobe:tcp_sendmsg` to trace TCP send internals. UPROBES: same mechanism as kprobes, but in userspace process memory. Attach to any instruction in any running binary. Works without modifying the binary. No recompilation needed. Can probe any binary: libc, JVM, Nginx, OpenSSL. Use when: you need to trace application behavior without modifying the application - especially third-party or closed-source binaries. Example: `uprobe:/usr/lib/libssl.so:SSL_write` to trace all TLS writes. USDT (User Statically Defined Tracing): static probes in applications (like tracepoints for userspace). Java HotSpot JVM has USDT probes. They're like tracepoints: stable, zero cost when disabled. HOW TO CHOOSE: If tracepoint exists: use it (stable). If kernel-internal only: use kprobe. If userspace binary tracing: use uprobe. If available USDT: prefer over uprobe.

**Expert:**
Q: How do you approach diagnosing a production latency spike that appears in p999 metrics but is invisible to application-level tracing?
A: p999 latency spikes that bypass application observability (no slow DB query, no GC pause, no external API timeout) are typically caused by kernel-level blocking. The diagnosis approach: STEP 1 - Eliminate scheduler issues. Use `bpftrace -e 'tracepoint:sched:sched_stat_wait /comm == "app_name"/ { @[tid] = hist(args->delay); }'`. If threads show scheduler wait > 50ms: CPU is saturated (threads runnable but not scheduled). Fix: reduce CPU load, check for noisy neighbor. STEP 2 - Check disk I/O blocking. Use `bpftrace -e 'tracepoint:block:block_rq_complete { @ms = hist((nsecs - @start[args->dev, args->sector]) / 1000000); }'`. If disk operations show 100ms+: dirty page writeback storm, or failing disk. Corroborate: `cat /proc/meminfo | grep -E "Dirty|Writeback"` during spike. Fix: tune vm.dirty_ratio. STEP 3 - Check memory pressure. Major page faults (pages swapped out and back in): `bpftrace -e 'kprobe:handle_mm_fault /comm == "app"/ { @start[tid] = nsecs; }; kretprobe:handle_mm_fault /comm == "app" && @start[tid]/ { @ms = hist((nsecs - @start[tid]) / 1000000); delete(@start[tid]); }'`. If shows 100ms+ faults: memory being swapped. Fix: vm.swappiness=1, ensure sufficient RAM. STEP 4 - Check lock contention. `perf lock record -a -- sleep 30 && perf lock report`. STEP 5 - If nothing found: off-CPU flame graph. Record scheduler switches and capture stacks of blocked threads: `bpftrace -e 'tracepoint:sched:sched_switch /prev_comm == "app"/ { @[ustack, kstack] = count(); }'`. The combination of blocked thread stacks (kstack) and their position in the code (ustack) reveals exactly where threads spend time blocked. The key insight: regular latency (average) reflects application performance. p999 spikes that bypass application observability are almost always OS-level: scheduler jitter, I/O blocking, memory pressure, or kernel lock contention. bpftrace's ability to probe any kernel event with near-zero overhead makes these diagnoses possible in production without any prior instrumentation.
