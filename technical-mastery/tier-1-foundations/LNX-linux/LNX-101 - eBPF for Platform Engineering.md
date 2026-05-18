---
id: LNX-101
title: "eBPF for Platform Engineering"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-035, LNX-057, LNX-064
used_by: LNX-104, LNX-105
related: LNX-035, LNX-064, LNX-104, LNX-105
tags: [ebpf, platform-engineering, bpf, xdp, tc-ebpf, kprobe, uprobe, tracepoint, bpf-map, bpftool, libbpf, cilium, falco, tetragon, pixie, bcc-tools, bpftrace, network-policy, observability-ebpf, security-ebpf, performance-ebpf, co-re, btf, verifier]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 101
permalink: /technical-mastery/lnx/ebpf-platform-engineering/
---

## TL;DR

**eBPF** (extended Berkeley Packet Filter) is a Linux kernel technology that
lets user-space programs run sandboxed code inside the kernel without modifying
kernel source or loading kernel modules. The kernel's **verifier** ensures safety
(no loops that run forever, no out-of-bounds memory access). eBPF programs attach
to: **kprobes** (any kernel function entry/exit), **uprobes** (user-space function
entry/exit), **tracepoints** (stable kernel trace events), **XDP** (network
driver level, fastest packet processing), **TC** (traffic control layer).
Platform use cases: (1) **Observability**: Cilium Hubble, Pixie, Tetragon -
trace every syscall/network call with zero instrumentation; (2) **Security**:
Falco, Tetragon - detect container escapes, unexpected syscalls, privilege
escalation in real time; (3) **Networking**: Cilium - replace kube-proxy with
eBPF, enforce NetworkPolicy at kernel level; (4) **Performance**: profile CPU
flame graphs, trace kernel latency without sampling overhead.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-101 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | eBPF, platform engineering, XDP, kprobe, Cilium, Falco, Tetragon, observability, security monitoring |
| **Prerequisites** | LNX-035 (processes), LNX-057 (security), LNX-064 (tracing) |

---

### The Problem This Solves

**Problem 1**: An organization runs 500 Kubernetes pods across 20 nodes. Debugging
a latency issue requires understanding: which service calls which, with what
latency, at what time. Traditional approach: add distributed tracing code to all
services (requires application changes, redeployments, developer coordination).
With eBPF (Pixie/Cilium Hubble): attach uprobes to Go/Java/Python binaries
and trace HTTP calls, database queries, and gRPC calls across ALL services
without ANY application code change. Deployed as a DaemonSet: instant full-mesh
observability in 15 minutes.

**Problem 2**: Kubernetes cluster security. Traditional security scanning:
check container images for known CVEs (static analysis). Misses: runtime
attacks (attacker exploits unknown CVE, executes shell commands from within
container). With eBPF (Falco/Tetragon): trace every `execve()` syscall from
every container. Policy: "nginx container should NEVER execute bash." If
attacker runs bash via a shell injection: immediate alert with container ID,
namespace, user, command, parent process chain.

---

### Textbook Definition

**eBPF (extended Berkeley Packet Filter)**: A kernel subsystem introduced in
Linux 3.18 (2014) that provides a sandboxed, safe execution environment for
user-supplied programs inside the Linux kernel. Programs are written in
restricted C, compiled to BPF bytecode, verified for safety, JIT-compiled
to native machine code, and attached to kernel hooks.

**eBPF subsystem components:**

| Component | Role |
|-----------|------|
| Verifier | Safety check: no infinite loops, bounded memory access |
| JIT compiler | Compiles BPF bytecode to native x86_64/arm64 |
| BPF maps | Shared data structures between kernel program and user-space |
| Helper functions | Kernel APIs available to BPF programs |
| Attachment points | kprobe, uprobe, tracepoint, XDP, TC, cgroup |

---

### Understand It in 30 Seconds

```bash
# === bpftrace: high-level eBPF scripting ===
# Install: yum install -y bpftrace (kernel 4.9+)

# Trace all execve() calls system-wide (which programs are running):
bpftrace -e 'tracepoint:syscalls:sys_enter_execve {
    printf("%s -> %s\n", comm, str(args->filename));
}'
# bash -> /usr/bin/ls
# nginx -> /usr/bin/openssl
# sshd -> /usr/bin/bash   <- ALERT: sshd should not spawn bash!

# Trace all open() calls for a specific process:
bpftrace -e 'tracepoint:syscalls:sys_enter_openat
    /comm == "nginx"/ {
    printf("%s opened: %s\n", comm, str(args->filename));
}'

# Latency histogram for all read() syscalls:
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @start[tid] = nsecs; }
tracepoint:syscalls:sys_exit_read /@start[tid]/ {
    @latency = hist(nsecs - @start[tid]);
    delete(@start[tid]);
}'
# @latency: [1K, 2K)    142 |...
#            [2K, 4K)    456 |...
#            [4K, 8K)     89 |...

# === bcc-tools: pre-built eBPF tools ===
# Install: yum install -y bcc-tools

# opensnoop: trace all file opens system-wide:
/usr/share/bcc/tools/opensnoop
# PID   COMM          FD   ERR PATH
# 1234  nginx          3   0  /etc/nginx/nginx.conf
# 5678  mysqld         8   0  /var/lib/mysql/ib_logfile0

# execsnoop: trace all new process executions:
/usr/share/bcc/tools/execsnoop
# COMM            PID   PPID  RET ARGS
# bash           9876   1234    0 /bin/bash -c "id"

# tcpconnect: trace all TCP connections:
/usr/share/bcc/tools/tcpconnect
# PID   COMM         IP  SADDR          DADDR        DPORT
# 1234  curl          4  10.0.0.5       93.184.216.34  80

# funclatency: function call latency:
/usr/share/bcc/tools/funclatency 'sys_read'
# avg = 2456 nsec, total: 24560 nsec, count: 10

# profile: CPU flame graph data (sample stack traces):
/usr/share/bcc/tools/profile -F 99 30 > /tmp/stacks.txt
# Then: FlameGraph/stackcollapse-bpf.pl /tmp/stacks.txt | \
#       FlameGraph/flamegraph.pl > /tmp/cpu.svg

# === Cilium: Kubernetes eBPF networking ===
# Replaces kube-proxy, iptables for pod networking
# Enforces NetworkPolicy at kernel level (not userspace)

# Check Cilium status:
cilium status
# KVStore:          Ok
# Kubernetes:       Ok
# Cilium:           Ok   1 local node(s)

# Hubble: eBPF-based network observability
hubble observe --namespace production
# May 16 14:22:00.123  FORWARDED  frontend/pod-abc -> backend/pod-xyz:8080 (HTTP GET /api/users)
# May 16 14:22:00.345  DROPPED    backend/pod-xyz -> db/pod-001:5432 (POLICY VIOLATION)
# ^ NetworkPolicy denied: backend should not access db directly

# L7 HTTP observability (no app changes needed):
hubble observe --namespace production --protocol http
# All HTTP requests with method, URL, status code, latency

# === Tetragon: eBPF-based security enforcement ===
# Real-time detection and ENFORCEMENT (not just alerting)

# Tetragon TracingPolicy: detect bash execution in any container:
kubectl apply -f - << 'EOF'
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: "detect-shell-in-container"
spec:
  kprobes:
  - call: "security_bprm_check"
    syscall: false
    args:
    - index: 0
      type: "linux_binprm"
    selectors:
    - matchBinaries:
      - operator: "In"
        values:
        - "/bin/bash"
        - "/bin/sh"
      matchActions:
      - action: Sigkill  # KILL the process (not just alert!)
EOF
# Effect: bash executed inside any container is immediately killed
# Alert sent to centralized security monitoring
```

---

### First Principles

```
Why eBPF is fundamentally different from previous tracing approaches:

Traditional kernel instrumentation:
  1. kernel modules: arbitrary code in kernel
     Pros: full access, anything possible
     Cons: no safety guarantee, kernel panic risk,
           must match kernel version, code review intense
  
  2. ptrace (strace): attach from user-space
     Pros: safe, no kernel code
     Cons: per-process only, massive overhead (50-100% slowdown),
           each syscall: stop process, context switch to tracer,
           context switch back - ptrace is unusable in production
  
  3. LD_PRELOAD hooks: intercept library calls
     Pros: user-space, safe
     Cons: only library calls, not kernel, attackers bypass it,
           must be injected into each process
  
  4. Network packet capture (tcpdump/pcap):
     Pros: captures all traffic
     Cons: user-space copy of packets (expensive),
           only network, not system calls or user-space functions

eBPF innovation: SAFE kernel execution with MINIMAL overhead

Safety: kernel verifier before ANY eBPF program runs:
  Checks: 1. No unbounded loops (guaranteed termination)
           2. No out-of-bounds memory access (no buffer overflow)
           3. No null pointer dereference
           4. No uninitialized memory reads
           5. Type safety for all operations
  
  If verification fails: program rejected, never runs
  Kernel cannot crash due to eBPF program (guaranteed)
  
Performance: JIT compilation to native code
  BPF bytecode -> x86_64 machine code via JIT
  Executes in kernel context = ZERO syscall overhead
  XDP programs run BEFORE memory allocation: <1 microsecond per packet
  kprobe overhead: ~100-200 nanoseconds (not 50% like ptrace)
  
Programmability:
  BPF maps: key-value stores shared between kernel program and user-space
  Histogram map: kernel counts events, user-space reads summary
  (not raw events - prevents event storm from high-frequency operations)
  Ringbuf: high-performance ring buffer for event streaming

Attachment points (where eBPF programs can attach):
  kprobe/kretprobe:
    Any kernel function entry/exit
    Dynamic: no kernel recompile needed
    Example: attach to tcp_connect() to trace all TCP connections
    Limitation: unstable API (function names may change between kernel versions)
  
  tracepoints:
    Stable, versioned trace events in kernel
    Defined by kernel developers as official API
    Example: syscalls:sys_enter_read (read syscall entry)
    More stable than kprobes between kernel versions
  
  BTF/CO-RE (Compile Once Run Everywhere):
    BTF (BPF Type Format): kernel embeds its own type information
    CO-RE: eBPF program uses BTF to adapt to different kernel versions
    Result: compile eBPF program once, run on kernel 5.4, 5.15, 6.1 etc.
    Before CO-RE: must compile for specific kernel (huge limitation)
  
  XDP (eXpress Data Path):
    Runs at network driver level, BEFORE kernel network stack
    Can: DROP, PASS, REDIRECT, TX packets
    Performance: 10-25 million packets per second on commodity hardware
    Use case: DDoS mitigation (drop spoofed SYN flood before kernel processes)
  
  TC (Traffic Control):
    Runs in traffic control layer (after XDP, before/after routing)
    Can: modify packets, redirect, drop
    Cilium uses TC for pod-to-pod packet routing

Platform engineering use cases:
  Observability without instrumentation:
    Pixie: traces Go/Python/Java functions with uprobes
    Zero application changes, zero restarts
    Traces: HTTP/gRPC calls, database queries, function latency
    
  Network security:
    Cilium Hubble: every network flow logged with L7 context
    No sidecar proxy needed (saves ~30% overhead vs service mesh)
    NetworkPolicy enforced in kernel (not via iptables rules)
    
  Security monitoring:
    Falco: rule-based detection on syscall tracepoints
    Tetragon: detection + enforcement (SIGKILL malicious processes)
    Can enforce: "nginx never executes /bin/bash"
    Response time: microseconds (kernel-level, not agent polling)
```

---

### Thought Experiment

Production eBPF observability deployment:

```bash
# Problem: 200 microservices, intermittent latency spikes in payment service
# No distributed tracing in place, adding OpenTelemetry requires 200 PRs

# Solution: Deploy Pixie (eBPF-based APM, zero instrumentation)
kubectl apply -f https://raw.githubusercontent.com/pixie-labs/pixie/main/k8s/operator/crd/...

# Pixie DaemonSet deploys an eBPF probe on every node
# No sidecar, no application changes, no restart needed

# After 5 minutes: query with Pixie's SQL-like PxL language:
# "Show me all HTTP requests to payment-service with p99 > 100ms"
# px.display(px.DataFrame('http_events')
#   .filter('service' == 'payment-service')
#   .filter('latency' > 100 * 1e6)  # 100ms in nanoseconds
#   .groupby(['path', 'status_code'])
#   .agg(p99=('latency', px.p99), count=('latency', px.count))
# )
#
# Results:
# path                    status  p99         count
# /api/v1/charge           200   450ms        1234
# /api/v1/validate         200   23ms         5678
# /api/v1/refund           500   1200ms!      89  <- Problem!

# Drill down: what is /api/v1/refund doing during slow requests?
# eBPF traces: database queries made during this HTTP request:
# SELECT * FROM transactions WHERE...  -> 1150ms (query timeout!)
# Connection to db-replica-2 failed, retry to db-primary -> added 900ms

# Found: db-replica-2 is lagging, payment-service not handling replica lag
# Fixed in application code: 1200ms -> 45ms, no instrumentation deployed

# eBPF security event in parallel (Tetragon):
# 14:22:45 SIGKILL payment/pod-abc: exec(/bin/sh) by uid=33
# ^ someone tried to run shell in payment container!
# Tetragon killed it AND generated alert with full process tree
# Without eBPF: this would have been invisible or detected only post-facto
```

---

### Mental Model / Analogy

```
eBPF = flight data recorder built into the OS

Traditional monitoring = asking pilots for reports:
  Pilots (applications) report what they want
  Add logging code to applications
  Miss events outside application (kernel, syscalls)
  Post-deployment changes (code change, redeploy, restart)
  
eBPF monitoring = black box flight recorder:
  Records EVERYTHING regardless of what pilots do
  No changes to aircraft (applications) needed
  Continuous recording of all events
  Works for any aircraft type (any programming language)
  
BPF verifier = FAA certification for black box software:
  "This code cannot crash the aircraft (kernel)"
  Cannot run until certified safe
  Certification happens at program load time
  
kprobes = sensors on specific aircraft components:
  "Attach sensor to fuel gauge function"
  Reads exactly what the function is processing
  Works on any engine (any kernel function)
  
XDP = air traffic control radar (BEFORE landing):
  Sees packets before they enter the aircraft
  Can redirect, drop, or allow at maximum speed
  
BPF maps = shared flight log between recorder and ground:
  Recorder (kernel program) writes events
  Ground team (user-space) reads summary
  Not raw data (too much volume): histograms, counts, samples
  
Cilium = eBPF-powered air traffic control:
  Knows the identity of every pod (not just IP address)
  Enforces rules at kernel level: "pod A cannot talk to pod B"
  No iptables rules (obsolete for container world)
  
CO-RE = one recorder model for all aircraft:
  Traditional eBPF: compile for each aircraft model (kernel version)
  CO-RE: recorder adapts to any aircraft using its own specs (BTF)
  One binary, runs on kernel 4.19, 5.4, 5.15, 6.1 etc.
```

---

### Gradual Depth - Five Levels

**Level 1:**
What eBPF is: programs that run in the kernel safely. The verifier ensures
safety. `bpftrace` for one-liner tracing. Pre-built tools: `opensnoop`,
`execsnoop` from bcc-tools. Use case: see what files are being opened, what
processes are running, what network connections are made.

**Level 2:**
Attachment points: kprobe, tracepoint, XDP, TC. BPF maps: how data is shared
between kernel program and user-space. `bpftool` for inspecting loaded eBPF
programs. Cilium as eBPF-based Kubernetes networking. Falco for rule-based
security detection. `bpftrace` scripts for custom tracing.

**Level 3:**
CO-RE (Compile Once Run Everywhere) and BTF (BPF Type Format). Writing eBPF
programs with libbpf in C. XDP programs for high-performance packet processing.
Tetragon for security enforcement (not just detection). Pixie for zero-instrumentation
APM. eBPF ringbuf for high-volume event streaming. Verifier limitations: what
eBPF cannot do (complex loops, unbounded data access).

**Level 4:**
eBPF program types in detail: SCHED_CLS, XDP, KPROBE, UPROBE, TRACEPOINT,
CGROUP_SKB. BPF map types: BPF_MAP_TYPE_HASH, ARRAY, PERCPU_ARRAY (for
performance), RINGBUF. Writing custom Cilium network policies using eBPF.
Debugging eBPF programs: `bpftool prog` show, `bpftool map` dump. eBPF
overhead measurement with perf. Security boundaries: what eBPF programs
can and cannot do (no arbitrary memory write, no sleeping).

**Level 5:**
Kernel eBPF internals: struct bpf_prog, JIT compilation for different
architectures (x86_64, arm64, s390). BPF Type Format (BTF) encoding and
how CO-RE relocations work at binary level. eBPF verifier internals: abstract
interpretation, register state tracking, pointer arithmetic analysis. eBPF
and Linux Security Modules (BPF LSM): using eBPF to implement security
policies that hook into LSM framework. Performance overhead analysis: eBPF
at high event rates (1M events/sec), ring buffer sizing, per-CPU maps for
lock-free counters. eBPF in the Linux kernel roadmap: sleepable eBPF, BPF
exceptions, eBPF token for delegation.

---

### Code Example

**BAD - using ptrace-based tracing in production:**
```bash
# BAD: strace on production process for debugging
strace -p 1234  # PID 1234 is production nginx

# Performance impact: 50-100% CPU overhead added to traced process!
# Each syscall: stop process, context switch to strace, report,
# context switch back. For high-traffic nginx: disaster.

# Also BAD: LD_PRELOAD for monitoring
export LD_PRELOAD=/opt/monitor.so
# Bypass: statically linked binaries are unaffected
# Not safe: malicious library can be loaded

# BAD: adding print statements to kernel module for debugging
// kernel module debug logging
printk(KERN_INFO "DEBUG: tcp_connect called from %s\n", current->comm);
// ^ printk at high rate = kernel log flooding, performance degradation
// ^ kernel module: no safety guarantee, crash risk
```

```bash
# GOOD: bpftrace for production-safe tracing

# Trace nginx TCP connections with minimal overhead (<0.01% CPU):
bpftrace -e '
kprobe:tcp_connect {
    printf("%-16s pid=%-6d -> %s:%d\n",
        comm, pid,
        ntop(AF_INET, ((struct sock *)arg0)->__sk_common.skc_daddr),
        ((struct sock *)arg0)->__sk_common.skc_dport
    );
}
' 2>/dev/null

# Latency histogram (kernel-side aggregation: no event storm):
bpftrace -e '
tracepoint:syscalls:sys_enter_read {
    @start[tid] = nsecs;
}
tracepoint:syscalls:sys_exit_read / @start[tid] / {
    @read_latency_ns = hist(nsecs - @start[tid]);
    delete(@start[tid]);
}
interval:s:5 {
    print(@read_latency_ns);
    clear(@read_latency_ns);
}
'
# Output every 5 seconds (not every event):
# @read_latency_ns:
# [1K, 2K)         1234 |**************************|
# [2K, 4K)          456 |**********|
# Zero overhead on application, aggregated in kernel

# GOOD: Tetragon policy for production security (kill, not just alert):
# TracingPolicy applied via kubectl:
# Selects processes that exec /bin/bash from containers
# Action: Sigkill + audit trail
# No application code change needed, sub-millisecond response time
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "eBPF programs can crash the kernel" | The eBPF verifier prevents this by design. Before any eBPF program can run, the kernel analyzes all possible execution paths to verify: (a) no infinite loops (all loops must be bounded), (b) no out-of-bounds memory access, (c) no null pointer dereference, (d) type-safe operations. A program that fails verification is rejected and never runs. The verifier is a formal safety proof. In practice: millions of eBPF programs run in production daily (every Kubernetes node with Cilium is running dozens of eBPF programs). The kernel has not regressed in stability. The risk analogy: "eBPF might crash the kernel" is like "using a type-checked language might corrupt memory." The type system prevents the class of errors; the verifier prevents the crash class of errors. |
| "eBPF is only for networking (it's 'Berkeley Packet Filter')" | The "packet filter" in the name is historical. eBPF was originally BPF (Berkeley Packet Filter), used in `tcpdump` to filter packets in the kernel. Linux extended it (eBPF) into a general-purpose kernel execution environment. Modern eBPF use cases span: performance profiling (CPU flame graphs, function latency), security monitoring and enforcement (syscall auditing, process killing), application observability (HTTP request tracing without sidecars), filesystem operations, scheduler customization (Linux 6.0+), networking (XDP, TC, Cilium). The networking use case is just one of many. In platform engineering today, the most impactful eBPF applications are often in observability (Pixie, Hubble) and security (Falco, Tetragon). |
| "eBPF requires modifying or recompiling the kernel" | No kernel modification or recompilation is required. eBPF programs are compiled to BPF bytecode by user-space tools (clang/LLVM), loaded by user-space programs via the `bpf()` syscall, verified by the kernel, and JIT-compiled to native machine code. The entire process happens at runtime, without touching kernel source code, without rebooting, without kernel modules. The only requirement is a sufficiently recent kernel (4.9+ for basic eBPF, 5.2+ for BTF, 5.8+ for CO-RE, 5.14+ for eBPF ringbuf). This is why eBPF is called "a superpower for Linux" - it lets you extend the kernel's behavior safely, at runtime, without kernel changes. |
| "eBPF observability has high performance overhead" | eBPF overhead is measured in nanoseconds, not the milliseconds of alternatives. Specific comparisons: (a) `strace` (ptrace) adds 50-100% CPU overhead per traced process; eBPF kprobe: ~200 nanoseconds per event. (b) sidecar proxy (Envoy/Istio): 1-3ms added latency per request, ~30% CPU overhead; eBPF networking (Cilium): <1ms added latency, ~5% CPU overhead. (c) Traditional tcpdump (copy packets to user-space): high CPU for high traffic; XDP (in-kernel): 10-25M packets/second with <1 microsecond per packet. For sampling-based profiling: eBPF profile at 99Hz adds <0.1% CPU overhead. The overhead concern is a remnant of pre-eBPF kernel tracing (kprobes without eBPF required kernel recompile and had higher overhead). With JIT-compiled eBPF, the overhead is negligible for production workloads. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: eBPF program rejected by verifier ===
# When loading eBPF program: "Permission denied" or verification error

dmesg | grep -i bpf
# [12345.678] bpf: Permission denied loading program
# [12345.679] bpf: 0: (79) r1 = *(u64 *)(r10 +0)
# [12345.680] bpf: invalid read from stack off 0 size 8

# Common reasons:
# 1. Kernel too old for the eBPF features used:
uname -r
# 4.14.xxx  <- CO-RE requires 5.2+, BTF requires 5.2+

# 2. Capabilities: eBPF requires CAP_BPF (kernel 5.8+) or CAP_SYS_ADMIN:
capsh --print | grep bpf
# Current: = cap_net_admin, cap_net_bind_service
# Missing: cap_bpf  <- need to add CAP_BPF or run as root

# 3. /proc/sys/kernel/unprivileged_bpf_disabled:
cat /proc/sys/kernel/unprivileged_bpf_disabled
# 1  <- unprivileged eBPF disabled (hardened system)
# Fix: run eBPF tools as root, or add CAP_BPF

# === Failure: bpftrace/bcc shows no output ===
# No events shown even though activity is happening

# Debug: check if attachment succeeded:
bpftrace -l 'tracepoint:syscalls:*'  # list available tracepoints
# If no tracepoints listed: kernel BTF not enabled

# Check BTF support:
ls /sys/kernel/btf/vmlinux  # exists = BTF enabled
# No such file = BTF not compiled into kernel
# Solution: upgrade kernel to 5.2+ with CONFIG_DEBUG_INFO_BTF=y

# Verify tracepoint exists:
cat /sys/kernel/debug/tracing/available_events | grep sys_enter_read
# syscalls:sys_enter_read  <- exists, OK

# === Failure: Cilium pods in CrashLoopBackOff ===
kubectl logs -n kube-system -l k8s-app=cilium | tail -20
# level=error msg="BPF filesystem not mounted"
# Fix: ensure BPF filesystem is mounted:
mount | grep bpf
# If not mounted:
mount bpffs /sys/fs/bpf -t bpf
# Add to /etc/fstab:
# none  /sys/fs/bpf  bpf  rw,relatime  0  0

# Cilium needs kernel 4.9+ (minimum), recommended 5.4+:
uname -r  # 4.15: minimum but limited functionality
           # 5.10: most features work
           # 5.15+: full Cilium functionality
```

---

### Related Keywords

**Foundational:**
LNX-035 (processes), LNX-057 (security), LNX-064 (tracing)

**Builds on this:**
LNX-104 (observability platform), LNX-105 (fleet-scale networking)

**Related:**
LNX-104 (Linux observability platform), LNX-105 (DPDK, SR-IOV networking)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf(...) }'` | Trace all program executions |
| `/usr/share/bcc/tools/opensnoop` | Trace all file opens |
| `/usr/share/bcc/tools/execsnoop` | Trace all new process executions |
| `/usr/share/bcc/tools/tcpconnect` | Trace TCP connections |
| `bpftool prog list` | List loaded eBPF programs |
| `bpftool map list` | List eBPF maps |
| `ls /sys/kernel/btf/vmlinux` | Check BTF support (CO-RE requirement) |
| `cilium status` | Cilium/Hubble cluster status |

**3 things to remember:**
1. eBPF programs run in the kernel with ~200ns overhead (vs strace's 50-100% overhead). The BPF verifier guarantees kernel safety - no crashes. JIT compilation means near-native performance.
2. Three attachment point categories: (a) syscall tracing (tracepoints: stable API), (b) kernel function tracing (kprobes: flexible but unstable names), (c) user-space function tracing (uprobes: requires debug symbols). For production: prefer tracepoints for stability.
3. Platform use cases: Cilium (eBPF networking), Falco/Tetragon (eBPF security), Pixie/Hubble (eBPF observability). All three provide capabilities impossible or very expensive with traditional approaches.

---

### Transferable Wisdom

eBPF's design principles transfer broadly: the verifier-based safety model
is the same as: TypeScript types (compile-time proof of type safety), Rust's
borrow checker (compile-time proof of memory safety), formal methods (proof
of program correctness). The "programmable kernel hook" pattern appears in:
Linux LSM (Linux Security Modules), iptables/nftables rule processing,
Kubernetes admission webhooks (programmable API server hook), AWS Lambda@Edge
(programmable CDN). XDP's "process before memory allocation" optimization
maps to: Kafka's zero-copy design (avoid extra memory copies), io_uring
(batched I/O without syscall overhead per operation), DPDK (bypass kernel
entirely for packet processing). eBPF's CO-RE (Compile Once Run Everywhere)
approach to version compatibility is the same challenge as: Docker images
(package dependencies to run anywhere), Kubernetes operators (reconcile API
changes across Kubernetes versions), JVM (write once run anywhere). The
platform engineering shift from instrumented observability (add code to
apps) to infrastructural observability (kernel-level eBPF) mirrors the
shift from VM-based monitoring to container-native monitoring.

---

### The Surprising Truth

eBPF started as a network packet filter (BPF) in 1992, designed for `tcpdump`.
For 22 years it was just that: a way to filter packets efficiently. In 2014,
Alexei Starovoitov submitted a patch to the Linux kernel that fundamentally
reimagined BPF as a general-purpose virtual machine, renaming it "extended
BPF" (eBPF). The Linux kernel community had refused to merge new kernel
subsystems for years (too much risk, too complex to review). eBPF got merged
because it came with a safety guarantee (the verifier) that no previous
kernel extension mechanism had: mathematical proof that the program cannot
crash the kernel or access memory it shouldn't.

The surprising consequence: eBPF has become the platform that replaced
what would have required dozens of separate kernel subsystems. Network
observability, security monitoring, performance profiling, and container
networking - all of these were being solved with incompatible kernel modules
or userspace approximations before eBPF. Now a single technology, built on
the 1992 packet filter concept, is the foundation of modern Linux platform
engineering.

---

### Mastery Checklist

- [ ] Can write a basic bpftrace one-liner to trace syscalls or function calls
- [ ] Understands the role of the BPF verifier and what it prevents
- [ ] Can explain the three main attachment point categories (kprobe, tracepoint, XDP)
- [ ] Understands the platform engineering use cases: Cilium, Falco, Tetragon, Pixie
- [ ] Knows the prerequisites for CO-RE and why it matters for production deployment

---

### Think About This

1. Design an eBPF-based observability strategy for a Kubernetes cluster running
   200 microservices in multiple programming languages (Go, Java, Python, Node.js).
   Requirements: trace all inter-service HTTP calls, measure database query
   latency, detect security anomalies, with ZERO application code changes.
   Which tools would you use? What are the limitations for each language?
   How would you handle the data volume (millions of events per second)?
   What would the operator deployment look like?

2. A security team wants to enforce: "No production container should ever
   execute bash, sh, or python directly." They debate three approaches:
   (a) eBPF with Tetragon enforcement (kill the process), (b) Kubernetes
   PodSecurityPolicy/OPA admission control (reject pods with wrong security
   context at deploy time), (c) Container image scanning (reject images with
   shell binaries). Analyze what each approach catches and misses. In what
   attack scenario does each approach fail? Is the combination of all three
   equivalent to perfect security?

3. eBPF programs run in kernel context with kernel privileges but are verified
   safe. A security researcher discovers a verifier bypass that allows arbitrary
   kernel memory reads. How does this change your eBPF deployment strategy?
   What defense-in-depth measures exist if the verifier has a bug? How would
   you detect that an eBPF program is being misused on your systems?

---

### Interview Deep-Dive

**Foundational:**
Q: What is eBPF, and what problems does it solve for platform engineers?
A: EBPF DEFINITION: eBPF (extended Berkeley Packet Filter) is a Linux kernel technology that allows running sandboxed programs inside the kernel without kernel source modification or module loading. The kernel's verifier ensures programs are safe (no crashes, no memory violations) before they run. JIT compilation provides near-native performance. WHAT IT SOLVES: (1) OBSERVABILITY WITHOUT INSTRUMENTATION: Before eBPF, getting visibility into all HTTP calls, database queries, and function latencies required adding OpenTelemetry/Jaeger to every application. eBPF tools like Pixie or Cilium Hubble attach uprobes to application binaries and trace all function calls without any application code change. For a 200-service microservices deployment: eBPF gives full distributed tracing in 15 minutes via a DaemonSet, vs 6 months of "add tracing to every service" work. (2) SECURITY WITHOUT SIDECAR: Detecting runtime attacks (shell execution in containers, unexpected file access, privilege escalation) traditionally required sidecar injection into every pod (Istio/Linkerd) adding 1-3ms latency overhead. eBPF tools (Falco, Tetragon) attach to kernel syscall tracepoints: see every execve, every file open, every network connection from every container with <200ns overhead, no sidecar needed. (3) NETWORKING WITHOUT IPTABLES: Kubernetes uses iptables for service load balancing (kube-proxy). At 10,000 pods: iptables has 10,000+ rules, O(n) lookup time, slow to update. Cilium replaces kube-proxy with eBPF maps: O(1) lookup regardless of number of pods. Also enables identity-based NetworkPolicy (not just IP-based). CONCRETE EXAMPLES: `bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s %s\n", comm, str(args->filename)); }'` traces every process execution system-wide with <0.01% CPU overhead. The same information via strace would add 50-100% overhead.

**Expert:**
Q: Explain how Cilium uses eBPF to replace kube-proxy and what the performance advantages are at scale.
A: KUBE-PROXY ARCHITECTURE AND LIMITATIONS: kube-proxy implements Kubernetes Services (ClusterIP, NodePort, LoadBalancer) using iptables rules. For each Service, kube-proxy creates iptables PREROUTING/FORWARD rules for DNAT (destination NAT) to load balance across pod endpoints. Problems at scale: (1) O(n) rule processing: iptables processes rules linearly. At 10,000 pods with 1,000 services: tens of thousands of iptables rules, processed for every packet. As cluster grows: latency increases. (2) State synchronization: kube-proxy polls Kubernetes API, rebuilds iptables ruleset when endpoints change. At 100 endpoint updates/second: constant iptables flush/replace operations, brief networking disruption. (3) Connection tracking table: high-traffic clusters fill the kernel's connection tracking table (nf_conntrack), causing drops. (4) No identity: iptables only knows IPs. Pod IPs change constantly (pod restarts). No semantic network policy beyond IP+port. CILIUM'S EBPF APPROACH: Cilium replaces kube-proxy entirely with eBPF programs. Architecture: (1) BPF maps for service routing: `BPF_MAP_TYPE_HASH` maps service ClusterIP -> list of backend pods. O(1) hash lookup per packet regardless of scale. (2) Service load balancing in eBPF TC hook: eBPF program on the socket layer intercepts connection requests, selects backend via consistent hashing from BPF map, establishes direct kernel socket bypass. (3) Endpoint identity: Cilium assigns each pod an identity (derived from labels). eBPF programs carry identity metadata with packets. Network policies evaluated by identity (not IP). (4) Conntrack replacement: Cilium uses its own BPF-based connection tracking, not kernel nf_conntrack. Larger, faster, lower CPU overhead. PERFORMANCE COMPARISON: kube-proxy at 10,000 endpoints: rule evaluation O(n). Cilium at 10,000 endpoints: O(1) BPF map lookup. Measured: Cilium achieves ~3x higher throughput than kube-proxy at scale, ~60% lower CPU for policy enforcement, 99th-percentile latency improvement of 2-3x. For pod-to-pod communication on the same node: Cilium uses XDP-accelerated path, bypassing most of the kernel network stack. ADDITIONAL CAPABILITIES: Cilium Hubble (observability) uses eBPF TC hooks to record every network flow with L7 context (HTTP method, URL, status code) without any sidecar. This is impossible with iptables-based kube-proxy (no L7 visibility). Cilium Network Policies can specify L7 rules: "Service A can call POST /api/users on Service B, but not GET /admin." Enforced at kernel level.
