---
id: LNX-073
title: "eBPF - Extended Berkeley Packet Filter"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-022, LNX-071
used_by: LNX-087, LNX-101
related: LNX-087, LNX-073, LNX-085, LNX-091
tags: [ebpf, bpf, xdp, kprobe, tracepoint, tc, cilium, bpftrace, libbpf, perf, observability, networking, security]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/lnx/ebpf/
---

## TL;DR

**eBPF** (extended Berkeley Packet Filter) is a kernel virtual machine that
lets you run sandboxed programs IN the kernel without modifying kernel source
or loading kernel modules. Programs attach to **hooks**: kprobes (any kernel
function), tracepoints (stable trace events), XDP (network driver receive
path), tc (traffic control), socket, LSM hooks. Programs communicate with
userspace via **maps** (shared data structures: hash, array, ring buffer).
The verifier ensures programs are safe (terminates, no invalid memory).
Use cases: observability (bpftrace, BCC tools: `execsnoop`, `tcpretrans`),
networking (Cilium, XDP packet processing), security (Falco, seccomp
extension). Entry point: `bpftool`, `bpftrace`, BCC toolkit.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-073 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | eBPF, BPF, kprobe, tracepoint, XDP, tc, bpftrace, BCC, Cilium, observability, networking |
| **Prerequisites** | LNX-022 (Process management), LNX-071 (Namespaces) |

---

### The Problem This Solves

**Problem 1**: You need to trace every `open()` syscall on a production
server to detect which processes are accessing sensitive files, but installing
strace on every process is impractical (strace has 100x overhead per process).
eBPF kprobe on `do_sys_open` runs in the kernel, captures the filename and
PID for every open() syscall with <1% overhead. The single eBPF program
instruments ALL processes without modifying them.

**Problem 2**: A microservices platform needs per-service network metrics
(bytes, packets, connections) without adding a sidecar proxy to every pod.
eBPF programs attached to the network stack via `tc` or XDP can label packets
with source/destination pod metadata and count them in BPF maps, then expose
those maps to a monitoring agent - zero changes to application pods, kernel-level
precision, sub-millisecond overhead.

---

### Textbook Definition

**eBPF**: An in-kernel virtual machine with a RISC instruction set (64-bit
registers, ~100 instructions), introduced in Linux 3.18 (2014), significantly
extended through 5.x kernels. Programs are loaded via `bpf(2)` syscall,
verified for safety by the kernel verifier, JIT-compiled to native machine
code, and attached to kernel hooks.

**Components:**
- **Programs**: C code compiled to BPF bytecode (with LLVM/clang), loaded into kernel
- **Maps**: Key-value stores shared between BPF programs and userspace
- **Helpers**: Kernel functions BPF programs can call (`bpf_probe_read`, `bpf_perf_event_output`)
- **Verifier**: Ensures programs are safe: terminate (no loops without bounds before 5.3), no invalid memory access, no unsafe operations
- **JIT Compiler**: Translates BPF bytecode to native code (x86, ARM, etc.)

**Attachment points (hooks):**
- `kprobe`/`kretprobe`: any kernel function entry/exit
- `tracepoint`: stable predefined trace events (syscalls, scheduler, etc.)
- `perf_event`: hardware/software performance counters
- `XDP` (eXpress Data Path): network driver receive queue (earliest possible)
- `tc` (traffic control): ingress/egress network path
- `socket filter`, `sk_lookup`, `cgroup/sock`
- `LSM`: Linux Security Module hooks (kernel 5.7)
- `fentry`/`fexit`: faster alternatives to kprobes (kernel 5.5+)

---

### Understand It in 30 Seconds

```bash
# === Quick eBPF tools (requires BCC/bpftrace installed) ===

# Install BCC tools (Ubuntu):
# apt install bpfcc-tools linux-headers-$(uname -r)
# or: apt install bpftrace

# === bpftrace: one-liners for instant tracing ===

# Trace all file opens with filename:
bpftrace -e 'tracepoint:syscalls:sys_enter_openat {
    printf("%s opened %s\n", comm, str(args->filename));
}'

# Count syscalls per process:
bpftrace -e 'tracepoint:raw_syscalls:sys_enter {
    @[comm] = count();
}'
# Ctrl-C to dump:
# @[nginx]: 12345
# @[mysqld]: 8901

# Trace TCP connections with latency:
bpftrace -e 'kretprobe:tcp_v4_connect /retval == 0/ {
    printf("%-6d %-12s\n", pid, comm);
}'

# Profile CPU usage (flame graph data):
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }' \
    -o /tmp/profile.bt

# === BCC tools (pre-written eBPF programs) ===

# execsnoop: trace every process exec:
execsnoop-bpfcc
# PCOMM   PID   PPID RET ARGS
# bash    1234  1200   0 /bin/ls -la

# opensnoop: trace file opens:
opensnoop-bpfcc -p 1234   # filter by PID

# tcpconnect: trace outbound TCP connections:
tcpconnect-bpfcc
# PID    COMM  SADDR           SPORT DADDR           DPORT
# 1234   curl  10.0.0.1        54321 93.184.216.34   80

# tcpretrans: trace TCP retransmits (network health indicator):
tcpretrans-bpfcc
# TIME     PID   IP LADDR:LPORT  T> RADDR:RPORT
# 12:00:01 0      4 10.0.0.1:80  R> 10.0.0.2:54321

# runqlat: CPU run queue latency histogram:
runqlat-bpfcc 10 1   # 10 seconds, 1 interval
# usecs   : count     distribution
# 0->1    : 1234      |**|
# 2->3    : 5678      |**********|
# High values: CPU contention or scheduling issues

# biolatency: block I/O latency histogram:
biolatency-bpfcc 10 1

# === bpftool: inspect and manage BPF programs ===
# List loaded BPF programs:
bpftool prog list
# ID  TYPE           TAG             NAME
# 42  kprobe         aaabbbccc       trace_open
# 99  xdp            dddeeefff       xdp_lb

# Show BPF maps:
bpftool map list
bpftool map dump id 5   # dump contents of map ID 5

# Show what's attached to network interface:
bpftool net list dev eth0
```

---

### First Principles

**How eBPF programs execute:**
```
User space writes eBPF program (C code):
  SEC("kprobe/sys_open")
  int trace_open(struct pt_regs *ctx) {
      char filename[256];
      bpf_probe_read_user_str(filename, sizeof(filename),
          (void *)PT_REGS_PARM1(ctx));
      bpf_trace_printk("open: %s\n", sizeof("open: %s\n"), filename);
      return 0;
  }

Compilation with LLVM/clang -> BPF bytecode (ELF object file)
                                      |
                                      v
bpf(BPF_PROG_LOAD) syscall -> Kernel Verifier
                                      |
              Verifier checks:        |
              1. All paths terminate  |
              2. No invalid memory    |
              3. Return type correct  |
              4. Helper functions OK  |
                                      v
                            JIT Compiler (x86/ARM)
                                      |
                                      v
                            Native machine code in kernel memory
                                      |
                         Attach to hook (kprobe on sys_open)
                                      |
Every time sys_open() is called:
  -> CPU executes eBPF JIT code directly (no interpreter overhead)
  -> Program reads/writes BPF maps
  -> Can output to perf ring buffer (userspace reads)
  -> Executes in ~microseconds

BPF Maps (kernel<->userspace data sharing):
  BPF_MAP_TYPE_HASH: key-value hash map
    Use: per-connection tracking, per-process stats
  BPF_MAP_TYPE_ARRAY: fixed-size indexed array
    Use: global counters, per-CPU stats
  BPF_MAP_TYPE_RINGBUF: circular buffer (kernel 5.8)
    Use: event streaming to userspace (replaces perf_event_array)
  BPF_MAP_TYPE_PERCPU_ARRAY: per-CPU arrays
    Use: high-frequency counters (no lock contention)
  BPF_MAP_TYPE_PROG_ARRAY: array of BPF programs
    Use: tail calls (program-to-program jumps for complex pipelines)
```

**XDP (eXpress Data Path) - packet processing:**
```
Normal network receive path:
  NIC -> DMA to kernel memory
      -> Driver IRQ -> softirq -> protocol stack
      -> socket buffer -> copy to userspace
      -> Application reads (socket.read)
  Total: ~10-20 microseconds

XDP path (eBPF at driver level):
  NIC -> DMA to kernel memory
      -> Driver calls eBPF XDP program
      -> Returns: XDP_DROP (discard), XDP_PASS (continue normal),
                  XDP_TX (retransmit), XDP_REDIRECT (redirect to other NIC/CPU)
  Decision in ~1 microsecond (before ANY kernel stack processing!)

Why this matters:
  DDoS mitigation: drop malicious packets at line rate (100M+ pps)
    without kernel stack overhead
  Load balancing: redirect packets to backend servers
    (Cilium, Katran use this)
  Packet filtering: faster than iptables (which operates at netfilter
    = AFTER the full stack runs)
  
Performance comparison (packets/sec, single core):
  iptables: ~1M pps
  tc eBPF:  ~3M pps
  XDP generic: ~5M pps (software XDP)
  XDP native: ~20M pps (driver-level XDP)
  XDP offload: line rate (FPGA/SmartNIC XDP)
```

---

### Thought Experiment

Building a simple connection tracker with eBPF:

```c
// trace_tcp_connect.bpf.c - track TCP connections
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/tcp.h>

// Map: store active connections (key=PID, value=stats)
struct conn_stats {
    __u64 total_connections;
    __u64 total_bytes;
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, __u32);           // PID
    __type(value, struct conn_stats);
    __uint(max_entries, 10240);
} conn_map SEC(".maps");

// Attach to TCP connect (kprobe on kernel function):
SEC("kprobe/tcp_v4_connect")
int trace_connect(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    struct conn_stats *stats = bpf_map_lookup_elem(&conn_map, &pid);
    if (!stats) {
        struct conn_stats new_stats = {.total_connections = 1};
        bpf_map_update_elem(&conn_map, &pid, &new_stats, BPF_ANY);
    } else {
        stats->total_connections++;
    }
    return 0;
}

char LICENSE[] SEC("license") = "GPL";

// Userspace reader (Python BCC or libbpf) reads conn_map
// periodically and exports metrics
```

```bash
# bpftrace equivalent (one-liner for quick testing):
bpftrace -e '
kprobe:tcp_v4_connect {
    @connections[comm, pid] = count();
}

interval:s:10 {
    print(@connections);
    clear(@connections);
}
'
```

---

### Mental Model / Analogy

```
eBPF = a supervised plugin system for the kernel

Traditional kernel modification:
  "I need to monitor all file opens"
  -> Write kernel module
  -> One bug = kernel panic (crash the entire system)
  -> Requires kernel recompile or module signing
  -> Complex to maintain, version-specific

eBPF plugin system:
  "I need to monitor all file opens"
  -> Write eBPF program (C)
  -> Submit to kernel's security scanner (verifier)
  -> Verifier guarantees: won't crash, won't loop forever
  -> JIT-compiled to fast native code
  -> Runs inside kernel at hook point
  -> Zero risk to kernel stability (sandbox)
  -> Load/unload without reboot

Analogy: JavaScript in a browser sandbox
  JavaScript runs IN the browser engine:
    - Can manipulate DOM (has access to browser internals)
    - Can't crash the browser (sandboxed, memory-safe)
    - Can't access your filesystem arbitrarily (limited helpers)
  
  eBPF runs IN the kernel:
    - Can read/write kernel memory (within verifier rules)
    - Can't crash the kernel (verifier ensures safety)
    - Can't call arbitrary kernel functions (only approved helpers)

BPF Maps = shared whiteboards:
  eBPF program (kernel side) writes:
    "PID 1234 made 50 TCP connections"
  Userspace program reads the whiteboard:
    Exports to Prometheus / Datadog / your dashboard
  
  Programs don't need to communicate via disk or sockets:
  direct kernel-to-userspace memory sharing

Hooks = event listeners:
  kprobe/tracepoint = addEventListener('sys_open', callback)
  XDP = middleware that runs before the browser (kernel) even processes the request
```

---

### Gradual Depth - Five Levels

**Level 1:**
What eBPF is: safe in-kernel programs. Use cases: observability, networking,
security. Tools: `bpftrace` one-liners, BCC tools (`execsnoop`, `opensnoop`,
`tcpconnect`, `runqlat`). eBPF program types: kprobe, tracepoint. `bpftool prog list`.

**Level 2:**
BPF maps: hash, array, ring buffer. Attachment points: kprobe, tracepoint, XDP, tc.
JIT compilation. The verifier (safety guarantees). libbpf vs BCC (C vs Python API).
`bpftrace` scripting language. CO-RE (Compile Once, Run Everywhere) with BTF.

**Level 3:**
XDP return codes (DROP, PASS, TX, REDIRECT). eBPF tail calls (program chaining).
Per-CPU maps for lock-free counters. Perf ring buffer vs ring buffer map.
eBPF programs for networking: `tc` classifier/action. Cilium architecture (eBPF
replaces iptables/kube-proxy). fentry/fexit vs kprobes (performance difference).

**Level 4:**
eBPF LSM programs (KRSI - kernel runtime security instrumentation). eBPF for
HTTP/L7 observability (probing userspace SSL via uprobe). `bpf_perf_event_output`
vs `bpf_ringbuf_output`. BTF (BPF Type Format) for portability. eBPF programs
in XDP for DDoS mitigation. Memory access patterns in eBPF (verifier restrictions).
Tail call limits (maximum chain depth). eBPF program pinning (persist beyond
process lifetime).

**Level 5:**
eBPF verifier internals: DAG analysis, register state tracking, complexity
limits. JIT compiler output analysis (`bpftool prog dump jited`). eBPF loop
support (kernel 5.3 bounded loops). eBPF for networking: full socket splicing,
sk_buff modification. Cilium L7 policy enforcement via eBPF. Real-time scheduling
with eBPF sched_ext (kernel 6.6+). eBPF for GPU scheduling research. Security
considerations: eBPF as attack vector (unprivileged eBPF exploit surface).

---

### Code Example

**BAD - naive approaches vs eBPF:**
```bash
# BAD: Use strace to monitor all file opens system-wide
strace -e openat -f -p 1 2>&1   # attach to init and all children
# Problems:
# 1. ptrace mechanism: every syscall causes context switch to strace
# 2. Overhead: 100x-1000x slowdown for traced processes
# 3. ptrace is exclusive: only one tracer per process
# 4. Can't easily aggregate data across all processes

# BAD: Use auditd for network connection logging
# /etc/audit/rules.d/network.rules:
# -a always,exit -F arch=b64 -S connect -k network_connect
# Problems:
# 1. Every connect() syscall logs to audit.log (high volume)
# 2. Post-processing needed to extract useful data
# 3. No aggregation or filtering at capture time
# 4. High overhead for busy services

# GOOD: bpftrace one-liners (low overhead, in-kernel aggregation):
# Count TCP connections by command, in-kernel aggregation:
bpftrace -e '
kprobe:tcp_v4_connect {
    @[comm] = count();
}
END { print(@); }
' &

# ONLY reports totals (not every event) = minimal overhead
# Runs for 30 seconds then exit:
sleep 30; kill %1

# GOOD: BCC execsnoop for process execution audit:
execsnoop-bpfcc -T -l 10
# -T timestamp, -l 10 duration
# Very low overhead: only fires on exec() (rare event)
# vs strace: fires on EVERY syscall (very frequent)
```

**GOOD - bpftrace for common production scenarios:**
```bash
# Scenario 1: Find slow disk reads (I/O latency investigation)
bpftrace -e '
tracepoint:block:block_rq_issue {
    @start[args->sector] = nsecs;
}
tracepoint:block:block_rq_complete {
    if (@start[args->sector]) {
        @usecs = hist((nsecs - @start[args->sector]) / 1000);
        delete(@start[args->sector]);
    }
}
END { print(@usecs); }
'
# Shows histogram of disk read latencies

# Scenario 2: Find processes making network connections to unexpected hosts
bpftrace -e '
kprobe:tcp_v4_connect {
    $sk = (struct sock *)arg0;
    $daddr = ntop(AF_INET, $sk->__sk_common.skc_daddr);
    printf("%-12s %-6d -> %s\n", comm, pid, $daddr);
}
' | grep -v "10\.\|127\.\|172\."   # filter private IPs

# Scenario 3: CPU flame graph data collection
bpftrace -e '
profile:hz:49 {
    @[kstack(6), ustack(6), comm] = count();
}
' -o /tmp/profile.txt 30

# Convert to flame graph (using FlameGraph scripts):
# stackcollapse-bpftrace.pl /tmp/profile.txt > /tmp/folded.txt
# flamegraph.pl /tmp/folded.txt > /tmp/flamegraph.svg
```

---

### Comparison Table

| Tool/Approach | Mechanism | Overhead | Use case |
|--------------|-----------|---------|---------|
| strace | ptrace (context switch) | Very high (100x+) | Single process debug |
| auditd | audit subsystem | Medium | Compliance logging |
| bpftrace | eBPF kprobe/tracepoint | Very low (<1%) | Ad-hoc investigation |
| BCC tools | eBPF (compiled) | Very low | Production monitoring |
| Cilium | eBPF (tc/XDP) | Minimal | Kubernetes networking |
| Falco | eBPF + rules engine | Low | Runtime security |
| perf | CPU PMU + kernel sampling | Configurable | CPU profiling |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "eBPF programs can crash the kernel" | The eBPF verifier is specifically designed to prevent this. Before any eBPF program runs, the kernel's verifier performs static analysis: every code path must terminate (bounded loops in 5.3+, previously no loops), no null pointer dereferences (all memory accesses checked), no out-of-bounds array accesses, no stack overflows (limited stack size: 512 bytes). A program that fails verification is rejected with an error message (like a compiler error), not loaded. Verified eBPF programs run in the kernel with the same safety as kernel code, but with static proof of safety. Comparison: kernel modules have NO safety guarantee - one bug = kernel panic. |
| "eBPF requires root access to use" | In older kernels (pre-5.8), most eBPF operations required `CAP_SYS_ADMIN`. Modern systems (kernel 5.8+, using `CAP_BPF` + `CAP_PERFMON`) allow unprivileged users to load certain eBPF program types (particularly socket filters, which were always limited-privileged). However: kprobe/tracepoint/XDP programs still require elevated privileges. Many distributions disable unprivileged eBPF (`/proc/sys/kernel/unprivileged_bpf_disabled=1`) as a security measure. In practice: most production eBPF tools require root or specific capabilities. Container deployment: run eBPF agent with `CAP_BPF` + `CAP_PERFMON` (not full root). |
| "eBPF is only for networking" | eBPF's original application was indeed in networking (Berkeley Packet Filter = socket filtering). But modern eBPF is used for: observability (bpftrace, BCC tools - trace any kernel/user function), profiling (CPU flame graphs, off-CPU analysis), security (Falco runtime security, LSM hooks), storage (io.stat latency histograms), scheduler monitoring (runqlat), and even replacing kernel subsystems (Cilium replaces iptables/kube-proxy, sched_ext replaces the CFS scheduler via eBPF). The networking history is just the origin story. |
| "Writing eBPF programs requires kernel developer expertise" | Modern tooling has abstracted eBPF significantly. Three tiers of accessibility: (1) `bpftrace` one-liners - requires only basic awareness of trace points and map syntax, similar to awk; most engineers can write useful `bpftrace` one-liners in minutes. (2) BCC Python API - moderate Python skills + eBPF C program; BCC handles loading, verifier errors, map reading. (3) Raw libbpf C - requires deep eBPF knowledge, handles portability with CO-RE/BTF. For most operational use cases (production debugging, observability), level 1-2 is sufficient. The BCC project includes 100+ ready-to-use tools that require zero eBPF programming knowledge. |

---

### Failure Modes & Diagnosis

**eBPF troubleshooting:**
```bash
# Error: "Operation not permitted"
bpftrace -e 'kprobe:do_sys_open { printf("%s\n", comm); }'
# Error: Operation not permitted
# Cause 1: Not root, and unprivileged_bpf_disabled=1
# Fix: run as root, or add CAP_BPF + CAP_PERFMON
# Check: cat /proc/sys/kernel/unprivileged_bpf_disabled

# Error: verification failed
bpftrace -e '
kprobe:some_func {
    // Try to read beyond stack limit (512 bytes)
    char buf[1000];   // Error! BPF stack limit
    ...
}
'
# eBPF verification error: too large
# Fix: use a BPF map instead of large stack allocation

# Error: "unknown func bpf_... attempted"
# eBPF helper not available in this kernel version
# Check kernel version: uname -r
# Some helpers require kernel 5.x+

# bpftrace: "No such file or directory" for tracepoints
bpftrace -l 'tracepoint:syscalls:*' | grep openat
# If not found: check kernel tracing is enabled
ls /sys/kernel/debug/tracing/events/syscalls/ | grep openat

# Performance issue: bpftrace consuming too much CPU
# Problem: very frequent kprobe (e.g., on tcp_sendmsg for high-bandwidth)
# Fix: add filtering: /comm == "nginx"/ to reduce events
# Fix: use in-kernel aggregation (@map[key] = count()) instead of printf per event

# Check loaded BPF programs (cleanup after crashes):
bpftool prog list
# If leftover programs from crashed tools:
bpftool prog detach id <ID> ...   # detach specific program
# Or: programs are auto-detached when the loading process dies (unless pinned)
# Check for pinned programs:
ls /sys/fs/bpf/   # pinned programs persist here
```

---

### Related Keywords

**Foundational:**
LNX-022 (Process management), LNX-071 (Namespaces)

**Builds on this:**
LNX-087 (Linux tracing), LNX-101 (eBPF for platform engineering), LNX-085 (XDP networking)

**Related:**
LNX-091 (tc/qdisc networking), LNX-079 (LSM/SELinux)

---

### Quick Reference Card

| Tool | Command | Purpose |
|------|---------|---------|
| `bpftrace` | `bpftrace -e 'kprobe:func { printf... }'` | Ad-hoc tracing |
| `execsnoop-bpfcc` | `execsnoop-bpfcc` | Trace all exec() calls |
| `opensnoop-bpfcc` | `opensnoop-bpfcc -p PID` | Trace file opens |
| `tcpconnect-bpfcc` | `tcpconnect-bpfcc` | Trace TCP connects |
| `runqlat-bpfcc` | `runqlat-bpfcc 10 1` | CPU scheduler latency |
| `biolatency-bpfcc` | `biolatency-bpfcc` | Disk I/O latency |
| `bpftool` | `bpftool prog list` | List loaded programs |

**3 things to remember:**
1. eBPF = sandboxed kernel programs verified for safety - can't crash the kernel, unlike kernel modules
2. Verifier + JIT: verified for safety, compiled for speed - runs as fast as kernel code
3. BPF Maps = kernel<->userspace shared memory; write counters/events in kernel, read from userspace for export

---

### Transferable Wisdom

eBPF design principles transfer to: Chrome's V8 engine (sandboxed JS execution
in browser) - same "safe runtime in a privileged context" model. WebAssembly
(WASM) - sandboxed, JIT-compiled, verified bytecode running in browser or server.
The BPF verifier's approach (static analysis, bounded execution, no unsafe memory)
is the core of security sandboxing in general - Kubernetes admission webhooks,
OPA (Open Policy Agent), and AWS Lambda execution models all share the principle
of "run untrusted code with a safety envelope." eBPF in production means:
Cilium (Kubernetes networking without iptables, eBPF-based service mesh),
Falco (runtime security), Meta's Katran (load balancing), Cloudflare's
packet processing - these are production systems processing millions of packets/sec
with eBPF. For platform engineers: understanding eBPF means you can attach
custom instrumentation to ANY Linux function without code changes to the
instrumented software - the ultimate zero-instrumentation observability.

---

### The Surprising Truth

eBPF is actually a radical departure from the traditional Linux kernel extension
model. The Linux kernel historically grew by adding subsystems and accepting
patches into the mainline. Kernel modules allowed out-of-tree extensions but
with zero safety guarantees. Alexei Starovoitov's 2014 eBPF extension was
explicitly designed with the insight that the kernel didn't need to know
everything upfront - it needed a SAFE extension mechanism. The result: eBPF
has enabled more innovation in the Linux networking and observability space
in 5 years than the prior 20 years of kernel development. The kernel community
joke: "eBPF is an escape hatch from having to upstream changes to the kernel."
Google, Meta, Cloudflare, and other hyperscalers use eBPF to implement custom
packet processing, schedulers, and security policies that would never get
accepted into mainline Linux (too specific, too experimental). Cilium replaced
the entire iptables-based kube-proxy in Kubernetes with eBPF - a fundamental
networking component rewritten in eBPF without a single line of kernel source
change. This is the design pattern: "program the kernel from userspace."

---

### Mastery Checklist

- [ ] Can write basic bpftrace one-liners for tracing file opens, syscalls, and TCP connections
- [ ] Understands eBPF program types: kprobe, tracepoint, XDP, tc
- [ ] Knows what BPF maps are and why they're used for kernel-userspace communication
- [ ] Can use BCC tools (execsnoop, tcpconnect, runqlat) for production debugging
- [ ] Understands the verifier's role (safety) and JIT's role (performance)

---

### Think About This

1. A production service is experiencing intermittent latency spikes of 50-100ms
   every few seconds. CPU and memory metrics look normal. Using eBPF tools
   (specifically `runqlat` and `biolatency`), design an investigation procedure.
   What would each tool tell you, what hypothesis would each result confirm or
   rule out, and what eBPF program would you write next if the initial tools
   don't reveal the cause?

2. Your Kubernetes cluster uses iptables-based kube-proxy, and you're
   experiencing poor performance with 10,000 Services (each adding iptables
   rules). Explain why Cilium's eBPF-based approach eliminates this O(n) problem,
   tracing through: (a) how iptables processes packets for service routing,
   (b) how eBPF XDP/tc processes the same packet, (c) why BPF maps provide
   O(1) lookups vs iptables' O(n) chain traversal.

3. A security team wants to detect when any process reads `/etc/shadow` (the
   password file) in a production Kubernetes cluster. Design an eBPF-based
   detection system: (a) which hook/attachment point would you use, (b) what
   data would you capture in BPF maps, (c) how would you export the data for
   alerting, and (d) what are the limitations of eBPF-based detection vs
   kernel LSM policies (using eBPF LSM)?

---

### Interview Deep-Dive

**Foundational:**
Q: What is eBPF, and why is it significant for Linux observability?
A: eBPF (extended Berkeley Packet Filter) is a kernel virtual machine that allows running sandboxed programs inside the Linux kernel without modifying kernel source code or loading kernel modules. Significance for observability: BEFORE eBPF: getting kernel-level visibility required: kernel modules (risky, unstable, version-specific), ptrace/strace (prohibitive performance overhead, single-process only), kernel patches (requires upstream acceptance, long cycle), static tracepoints (limited predefined hooks only). WITH eBPF: attach a program to ANY kernel function via kprobe, ANY predefined trace event via tracepoints, or the network stack via XDP/tc. The program runs with near-zero overhead (JIT-compiled to native code), aggregates data IN the kernel (reducing userspace I/O), and is SAFE (verified - can't crash the kernel or loop infinitely). Practical example: tracing all file opens system-wide. strace on all processes: impractical (100x overhead per traced process, need to attach to each). eBPF kprobe on `do_sys_open`: one program, instruments all processes, <1% total overhead, in-kernel filtering. The result: bpftrace one-liners that would have previously required kernel development are now single commands. Production tools like Cilium (networking), Falco (security), and Netflix/Google's performance tools all use eBPF as the foundational mechanism.

**Expert:**
Q: How does the eBPF verifier ensure safety, and what are its key limitations?
A: The eBPF verifier performs static analysis on BPF bytecode before a program is allowed to run. Key checks: (1) CONTROL FLOW ANALYSIS: builds a directed acyclic graph (DAG) of all instructions. Before kernel 5.3: no backward jumps (no loops) - programs must terminate. From 5.3: bounded loops allowed (the verifier tracks maximum iterations to prove termination). All code paths must be verified (no unreachable code after the last instruction). (2) REGISTER STATE TRACKING: each register has associated metadata: whether it's initialized, if it contains a pointer and its type, what the valid range of values is. Operations like pointer arithmetic are checked: `ptr + offset` - the verifier tracks that offset stays within bounds of the pointed-to object. Uninitialized register reads are rejected. (3) MEMORY ACCESS VERIFICATION: pointer types are tracked. Reading from kernel stack: only the local 512-byte stack. Accessing map values: must check that the pointer is non-NULL after `bpf_map_lookup_elem`. Direct packet data access: must check `data + offset < data_end` before accessing. (4) HELPER FUNCTION VERIFICATION: only approved helper functions (`bpf_probe_read`, `bpf_map_lookup_elem`, etc.) can be called. Each helper has a defined type signature that the verifier enforces. KEY LIMITATIONS: Complexity limit: the verifier has a maximum instruction count it will analyze (by default 1M instructions as of 5.2). Programs that branch extensively can hit this limit even if they're logically simple. Stack size: 512 bytes maximum (no large local arrays). No dynamic memory allocation: can only use pre-allocated BPF maps. Portability: kprobe programs attach to internal kernel functions whose signatures change between kernel versions (BTF/CO-RE addresses this for tracepoints and fentry/fexit). Debugging verification failures: the error messages from the verifier can be cryptic; `bpftool prog load --debug` dumps verifier log. For production use: prefer tracepoints (stable) over kprobes (unstable function signatures) when possible.
