---
id: OSY-097
title: eBPF Observability
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-087, OSY-089
used_by: []
related: OSY-096, OSY-098, OSY-095
tags:
  - eBPF
  - observability
  - tracing
  - kernel
  - BPFTrace
  - Cilium
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 97
permalink: /technical-mastery/osy/ebpf-observability/
---

## TL;DR

eBPF (extended Berkeley Packet Filter) allows safe, sandboxed
programs to run inside the Linux kernel. Used for observability
(trace any syscall, function, or network packet with zero
application changes), networking (XDP, Cilium CNI), and
security (Falco, Tetragon). The "programmable kernel" - the
biggest change to Linux architecture since loadable modules.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-097 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | eBPF, BPFTrace, XDP, Cilium, Falco, kernel tracing |
| **Prerequisites** | OSY-009, OSY-087, OSY-089 |

---

### What Is eBPF?

```
eBPF = extended Berkeley Packet Filter (originally for packet filtering)
Modern meaning: general-purpose, safe kernel programmability framework

Traditional kernel extension (module):
  Write kernel module in C -> compile -> insmod -> runs in kernel
  Risk: bug in module = kernel panic; full kernel privileges
  
eBPF program:
  Write eBPF program (C subset) -> compile to eBPF bytecode
  Load: sys_bpf() syscall -> eBPF VERIFIER checks program
    Verifier ensures:
      - No infinite loops (bounded execution)
      - No invalid memory accesses (checked pointer bounds)
      - No kernel address disclosure
      - Terminates in bounded time
  If verification passes: JIT-compiled and loaded into kernel
  If verification fails: rejected (kernel prints reason)
  
Safety guarantee:
  eBPF program CANNOT panic the kernel
  Worst case: returns error code; eBPF program disabled
  
Comparison:
  Kernel module: full privileges, no safety, can panic
  eBPF: sandboxed, verified, cannot panic kernel
```

---

### eBPF Hook Points

```
eBPF can attach to many kernel events:

  1. kprobes: dynamic tracing of any kernel function
     Example: trace kmalloc(), sys_read(), tcp_sendmsg()
     Dynamic: no kernel recompile; attach at runtime
     
  2. kretprobes: trace function RETURN values
     Example: trace return value of sys_read() (bytes read)
     
  3. tracepoints: static kernel instrumentation points
     Example: sched_switch (every context switch)
                net_dev_xmit (every packet sent)
                block_rq_complete (every I/O completion)
     More stable than kprobes (survive kernel updates)
     
  4. uprobes: trace user-space function calls
     Example: trace Java method calls (with debug symbols)
     
  5. USDT (User Statically Defined Tracing):
     Application-defined trace points (like DTrace)
     
  6. XDP (eXpress Data Path):
     Attaches to NIC driver level (before kernel network stack)
     Action per packet: pass, drop, redirect, modify
     Used by: Cilium (Kubernetes CNI), Cloudflare DDoS protection
     
  7. TC (Traffic Control):
     Attaches to Linux qdisc (traffic scheduler)
     Both ingress and egress
     
  8. Socket filters:
     Per-socket packet filtering (original BPF purpose)
     
  9. LSM (Linux Security Module) hooks:
     Security enforcement at kernel enforcement points
     Used by: Tetragon (Cilium security)
```

---

### BPFTrace: Easy eBPF from Command Line

```bash
# bpftrace: one-liner eBPF programs
# Install: apt install bpftrace (Ubuntu 20.04+)
# Requires: Linux 4.9+ (ideally 5.8+); root

# 1. Trace all open() syscalls (show filename):
bpftrace -e 'tracepoint:syscalls:sys_enter_openat
             { printf("%s %s\n", comm, str(args->filename)); }'

# 2. Count read() calls per process:
bpftrace -e 'kretprobe:sys_read { @[comm] = count(); }'
# After Ctrl+C: shows counts per process name

# 3. Trace block I/O latency (histogram):
bpftrace -e 'kprobe:blk_account_io_start { @start[arg0] = nsecs; }
             kprobe:blk_account_io_done
             /@start[arg0]/
             { @usecs = hist((nsecs - @start[arg0]) / 1000);
               delete(@start[arg0]); }'
# Shows histogram of I/O latency in microseconds

# 4. Trace TCP connections:
bpftrace -e 'kprobe:tcp_connect
             { printf("connect: %s -> %d\n",
                      comm, ((struct sock *)arg0)->sk_dport); }'

# 5. Trace JVM GC (using uprobes, requires debug symbols):
# bpftrace can trace any user-space function
bpftrace -e 'uprobe:/path/to/libjvm.so:G1CollectedHeap::do_collection
             { printf("GC triggered by %s\n", comm); }'

# 6. Count page faults per process:
bpftrace -e 'software:page-fault:1 { @[comm] = count(); }'
```

---

### BCC Tools: Production Ready

```bash
# BCC (BPF Compiler Collection): Python frontends for eBPF
# Install: apt install bpfcc-tools

# execsnoop: trace new process executions
execsnoop-bpfcc

# opensnoop: trace file opens (with PID, process name)
opensnoop-bpfcc -p $PID

# biolatency: block I/O latency histogram
biolatency-bpfcc -D 30    # 30 second histogram

# tcpconnect: trace outbound TCP connections
tcpconnect-bpfcc

# tcpretrans: trace TCP retransmits (network issues)
tcpretrans-bpfcc

# runqlat: CPU run queue latency histogram
# Shows: how long tasks WAIT before getting CPU
runqlat-bpfcc 30          # 30 second sample
# If histogram shows many microseconds of wait:
#   CPU contention; too many threads for CPU count

# profile: CPU profiling (like perf record but eBPF)
profile-bpfcc -F 99 -p $PID 30   # 99Hz sampling for 30s
# Generates flamegraph-ready output

# cachestat: page cache hit ratio
cachestat-bpfcc 1         # 1-second intervals
# Shows: hits, misses, ratio
# Low hit ratio: working set larger than page cache
```

---

### eBPF in Production Systems

```
Cilium (Kubernetes CNI):
  Replaces: iptables-based kube-proxy
  Uses: eBPF TC and XDP hooks for all pod networking
  Result: 10x faster network policy enforcement vs iptables
  Feature: identity-based policy (not IP-based)
  
Falco (Security):
  Monitors: all syscalls via eBPF tracepoints
  Detects: container escapes, privilege escalation, file tampering
  Alert: "Java process in container executed /bin/bash"
  
Pixie (Observability, now CNCF):
  Auto-traces: all HTTP/gRPC/database calls without code changes
  Method: eBPF uprobes on TLS/SSL libraries + protocol parsers
  Shows: service map, latency histograms, per-request traces
  
Prometheus node_exporter + eBPF:
  perf_event_array: collect hardware counters via eBPF
  Expose as Prometheus metrics: CPU cycles, cache misses, TLB misses
  
Cloudflare (DDoS protection):
  XDP programs: drop attack packets before kernel network stack
  Rate: processes millions of packets/second per CPU
  Latency: packet dropped in ~50ns (vs 5000ns in kernel stack)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "eBPF programs can crash the kernel" | The eBPF verifier prevents unsafe programs from loading. A buggy eBPF program is rejected before execution. The worst a loaded program can do is return an error or cause unexpected behavior in its specific hook - not a kernel panic. This is the key advantage over kernel modules. |
| "eBPF requires kernel changes to the traced application" | eBPF can trace ANY kernel function or user-space function without any changes to the application. uprobes attach to binary functions; USDT traces pre-defined markers. You can trace a production JVM, nginx, or PostgreSQL without any modifications or restarts. |
| "eBPF is only for networking" | eBPF started as a packet filter but is now used for: performance profiling, security monitoring, tracing, system call auditing, resource accounting, and more. The BCC/BPFTrace tooling covers CPU, memory, I/O, networking - the entire system. |

---

### Quick Reference Card

| Task | Tool | Command |
|------|------|---------|
| Trace file opens | BCC | `opensnoop-bpfcc` |
| I/O latency histogram | BCC | `biolatency-bpfcc 30` |
| CPU run queue latency | BCC | `runqlat-bpfcc 30` |
| TCP connection trace | BCC | `tcpconnect-bpfcc` |
| Page cache hit ratio | BCC | `cachestat-bpfcc 1` |
| Custom one-liner | BPFTrace | `bpftrace -e 'tracepoint:...'` |
| Kernel function trace | BPFTrace | `kprobe:function_name { ... }` |
| Kubernetes CNI | Cilium | Helm chart deployment |
| Container security | Falco | DaemonSet deployment |
